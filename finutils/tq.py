#!/usr/bin/env python

# 天勤
# tqsdk related classes and functions

'''
这里应该考虑是否需要自己做一个tick和bar数据结构的抽象
或者直接使用vnpy的现成结构，目前认为直接使用最好，第一
能熟悉vnpy的代码结构，二也少了很多工作，vnpy里面肯定
已经有很多对这两个数据结构进行操作的代码

tq tick columns:
datetime,last_price,highest,lowest,
bid_price1,bid_volume1,ask_price1,ask_volume1,
volume,amount,open_interest
'''

import glob
import pathlib
import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import TickData, BarData
from vnpy.trader.utility import BarGenerator


class TqData:
    def __init__(self, path):
        self.path = pathlib.Path(path)

        # extract exchange, symbol, start_date, end_date, interval 
        l = self.path.name.split('.')
        self.exchange, self.symbol, self.start_date, self.end_date, self.interval, _ = l
        self.exchange = Exchange(self.exchange)
        # todo: parse dates
        # todo: tq interval and vnpy interval converter
        self.interval = int(self.interval)

        # now, read csv
        self.df = pd.read_csv(self.path, parse_dates=['datetime'], skiprows=[1], header=0)
        # rename some columns
        self.remove_column_prefix()

    def remove_column_prefix(self):
        # remove prefix
        exchange = self.exchange.value
        symbol = self.symbol
        prefix = f'{exchange}.{symbol}.'
        self.df.rename(
            columns = lambda x:x.replace(prefix, ''),
            inplace = True,
        )

    
    def calc_series_diff_like_volume(self, s):
        volume = s.copy()

        volume_diff = volume.diff()
        volume_diff[0] = volume[0]

        volume_in_tick = volume_diff
        negative_index = volume_diff<0
        volume_in_tick[negative_index] = volume[negative_index]
        return volume_in_tick


class TqTick(TqData):
    def __init__(self, path):
        super().__init__(path)
        df =self.df

        # spread
        df['spread'] = df['ask_price1'] - df['bid_price1']

        # 某个tick没有成交，但是有其他变化的时候，last_price为nan，这里用上一个last_price补充
        df.last_price.fillna(method='ffill', inplace=True)

        # 删除ask_price1并且bid_price1为nan的行, 这些行往往是垃圾数据，注意不要删除只要是ask_price1
        # 或者bid_price1为nan的行，可能是因为涨停或者跌停造成的
        # 还有刚刚补了之后还是nan的last_price
        df.dropna(subset=['ask_price1', 'bid_price1'], how='all', inplace=True)
        df.dropna(subset=['last_price'], inplace=True)

        # 重置index
        df.reset_index(drop=True, inplace=True)

        # 计算tick内的volume
        df['volume_in_tick'] = self.calc_series_diff_like_volume(df.volume)
    
    def to_vnpy_tick(self):
        mapper = {
            'bid_price1': 'bid_price_1',
            'bid_volume1': 'bid_volume_1',
            'ask_price1': 'ask_price_1',
            'ask_volume1': 'ask_volume_1',
            'highest': 'high_price',
            'lowest': 'low_price',
        }
        df = self.df.copy()
        # vnpy tick里面没有amount
        # volume_in_tick, spread是自己计算的数据，vnpy tick初始化的时候也不需要
        df.drop(columns=['amount', 'volume_in_tick', 'spread'], inplace=True)
        df.rename(columns=mapper, inplace=True)
        for ix,row in df.iterrows():
            kwargs = dict(row)
            kwargs.update({
                'symbol': self.symbol,
                'exchange': self.exchange,
                'gateway_name': 'tq',
            })
            yield TickData(**(kwargs))

    def to_1m_bar(self):
        '''
        这里用的vnpy的BarGenerator，从tick数据生成1m bar数据
        '''
        bars = []
        def on_bar(bar):
            bars.append(bar)
        bargenerator = BarGenerator(on_bar=on_bar)
        for tick in self.to_vnpy_tick():
            bargenerator.update_tick(tick)
        return bars


class ProductTick:
    '''
    某种品种的所有tq tick数据汇总
    '''
    def __init__(self, datadir, exchange, symbol, start, end):
        self.load_df_l(datadir, exchange, symbol, start, end)
        self.merge_df_l()
        self.clean_after_merge()

    def load_df_l(self, datadir, exchange, symbol, start, end):
        self.df_l = []
        f_l = sorted(glob.glob(f'{datadir}/{exchange}.{symbol}*.0.csv'))
        for f in f_l:
            tqtick = TqTick(f)
            exchange, symbol = tqtick.exchange.value, tqtick.symbol
            df = tqtick.df
            dts = df.datetime
            this_range = pd.date_range(dts.iloc[0].date(), dts.iloc[-1].date())
            print(exchange, symbol, this_range[0], this_range[-1], '    ', end='')

            if dts.iloc[0]<=start and dts.iloc[-1]>=end:
                print('include')
                df = df[(df.datetime>start) & (df.datetime<end)].copy()
                if df.shape[0]==0:
                    continue
                df.rename(columns=lambda x:x if x=='datetime' else f'{symbol}.{x}', inplace=True)
                self.df_l.append(df[['datetime', 
                    f'{symbol}.last_price',
                    f'{symbol}.ask_price1',
                    f'{symbol}.bid_price1',
                    f'{symbol}.spread',
                    f'{symbol}.volume',
                    f'{symbol}.volume_in_tick',
                    f'{symbol}.open_interest',
                ]])
            else:
                print('exclude')
        
    def merge_df_l(self):
        # it is required to specify datetime column name or else error would be raised when merged
        df = pd.DataFrame(columns=['datetime'])
        for dfi in self.df_l:
            df = pd.merge(df, dfi, on='datetime', how='outer')
        self.symbol_l = [x.split('.')[0] for x in df.filter(like='open_interest').columns]
        self.df = df

    def clean_after_merge(self):
        df = self.df
        df.sort_values('datetime', inplace=True)
        df.reset_index(drop=True, inplace=True)
        # 下面这一行会产生一个copy，导致fillna失败
        # https://stackoverflow.com/questions/38134012/pandas-dataframe-fillna-only-some-columns-in-place
        #df.loc[:, [f'{symbol}.volume_in_tick' for symbol in self.symbol_l]].fillna(0, inplace=True)
        df.fillna(
            dict.fromkeys([f'{symbol}.volume_in_tick' for symbol in self.symbol_l], 0),
            inplace=True,
        )
        df.fillna(method='ffill', inplace=True)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

    def iterday(start=None, end=None):
        r = pd.date_range(start, end)
        for day in r:
            s = day.replace(hour=8)
            e = day.replace(hour=16)
            yield df[(df.datetime>=s)&(df.datetime<=e)]
 
    def sort_contracts(self, method='volume', start=None, end=None):
        '''
        # 使用open_interest来选取跨期合约并不好，因为持仓量高并不一定代表
        # 成交活跃，成交不活跃，即使价差存在套利偏差，但是没有成交，也无法
        # 完成，所以最好还是用volume来进行判断

        method: open_interest or volume
        start,end: datetime
        '''
        df = self.df
        if start==None:
            start = df.datetime.iloc[0]
        if end==None:
            end = df.datetime.iloc[-1]
        if method=='open_interest':
            oi = df[(df.datetime>=start) & (df.datetime<=end)].filter(like='open_interest')
            l = oi.mean().sort_values(ascending=False).index
            return [x.split('.')[0] for x in l]
        elif method=='volume':
            volume = df[(df.datetime>=start) & (df.datetime<=end)].filter(like='volume_in_tick')
            l = volume.sum().sort_values(ascending=False).index
            return [x.split('.')[0] for x in l]


class TqBar(TqData):
    def to_vnpy_bar(self):
        df = self.df
        df['open_interest'] = df['close_oi']
        data = []
        for ix, row in df.iterrows():
            bar = BarData(
                symbol=self.symbol,
                exchange=Exchange(self.exchange),
                interval=Interval(self.interval),
                #datetime=row.name.to_pydatetime() - adjustment,
                datetime=row['datetime'],
                open_price=row["open"],
                high_price=row["high"],
                low_price=row["low"],
                close_price=row["close"],
                volume=row["volume"],
                # 这里用的是close_oi而不是open_oi，但是应该用哪一个还需要继续
                # 参考vnpy的代码或者论坛提问
                open_interest=row["close_oi"],
                gateway_name="tq"
            )
            data.append(bar)
        return data
