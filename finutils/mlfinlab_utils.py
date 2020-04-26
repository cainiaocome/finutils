#!/usr/bin/env python

'''
mlfinlab的一些辅助函数
'''

def copy_rqtick_df(rqtick):
    df = rqtick.df.copy()
    df.set_index('datetime', drop=True, inplace=True)
    df['datetime'] = list(df.index)
    # 删除交易时间以外的数据，ricequant的数据质量并不是特别好
    # 又有重复数据又没有清理这些异常数据，还好意思收费
    df = df[market_open_time_range.include_these(df.datetime)]
    no_touch_df = df

def trades_generator(df, method, plot=False):
    if method=='sample':
        # 只sample一小部分数据，方便research
        tmpdf = RqData.sample_without_time_gap(df, 6000, pd.to_timedelta('1 minutes'))
        df_gen = [(0, tmpdf)]
    elif method=='all':
        group_ids = group_ts_by_gap(df.datetime, pd.to_timedelta('1 minutes'))
        df['group_ids'] = group_ids
        df_gen = df.groupby('group_ids')
    else:
        raise Exception('method should be "sample" or "all"')

    for i,g in df_gen:
        df = g
        # 某些tick没有成交，只有报单修改，这里删除这些数据点，肯定会丢失某些信息
        # 以后再考虑如何处理
        df = df[~(df['volume_in_tick']==0)]          

        df['date'] = df['datetime']
        df['price'] = df['dollar_in_tick']/df['volume_in_tick']/contract.contract_multiplier
        _ = df['price'].fillna(method='ffill', inplace=True)
        df['volume'] = df['volume_in_tick']

        df.set_index('datetime', inplace=True)
        # 作图，看看price和volume
        if plot:
            price_volume_plot(df)
        yield df

