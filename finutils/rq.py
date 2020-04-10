#!/usr/bin/env python

# ricequant的数据解析

'''
这里应该考虑是否需要自己做一个tick和bar数据结构的抽象
或者直接使用vnpy的现成结构，目前认为直接使用最好，第一
能熟悉vnpy的代码结构，二也少了很多工作，vnpy里面肯定
已经有很多对这两个数据结构进行操作的代码

rq tick columns:

datetime,trading_date,
open,last,high,low,prev_settlement,prev_close,
volume,open_interest,total_turnover,limit_up,limit_down,
a1,a2,a3,a4,a5,b1,b2,b3,b4,b5,a1_v,a2_v,a3_v,a4_v,a5_v,b1_v,b2_v,b3_v,b4_v,b5_v,
change_rate
'''

import glob
import pathlib
import pickle
import gzip
import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta


class RqData:
    def __init__(self, path):
        self.path = pathlib.Path(path)

        # now, read csv
        self.df = pd.read_csv(self.path, parse_dates=['datetime'], header=0, compression='gzip')

    @staticmethod
    def sample_without_time_gap(df, ticks, max_time_gap):
        while True:
            s = random.randint(0,len(df)-ticks)
            tmpdf = df.iloc[s:s+ticks]
            tds = tmpdf.datetime.diff()
            if tds.max()>max_time_gap:
                continue
            else:
                return tmpdf

    @staticmethod
    def read_dominant_contracts_and_contracts_information(result_pkl_path):
        p = pathlib.Path(result_pkl_path)
        p_bytes = p.read_bytes()
        sep = b'thisisimpossible'
        x = p_bytes.split(sep)
        x = x[:2]
        for segment in x:
            result = pickle.loads(gzip.decompress(gzip.decompress(segment)))
            _type = result['type']
            if _type == 'dominant_contracts':
                dominant_contracts_df = result[_type]
            elif _type == 'contracts_information':
                contracts_information_df = result[_type]
        return dominant_contracts_df, contracts_information_df


class RqTick(RqData):
    def __init__(self, path):
        super().__init__(path)
        df = self.df

        # spread
        df['spread'] = df['a1'] - df['b1']

        g_l = []
        for trading_date,g in df.groupby('trading_date'):
            g = g.copy()
            g['volume_in_tick'] = g['volume'].diff()
            g['dollar_in_tick'] = g['total_turnover'].diff()
            g.dropna(inplace=True)
            g_l.append(g)
        self.df = pd.concat(g_l)
        drop_columns = 'a2,a3,a4,a5,b2,b3,b4,b5,a2_v,a3_v,a4_v,a5_v,b2_v,b3_v,b4_v,b5_v,change_rate'.split(',')
        self.df.drop(columns=drop_columns, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
    
    def to_vnpy_tick(self):
        raise Exception('not implemented yet')
        from vnpy.trader.constant import Exchange, Interval
        from vnpy.trader.object import TickData, BarData
        from vnpy.trader.utility import BarGenerator

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

