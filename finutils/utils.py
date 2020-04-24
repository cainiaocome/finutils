import pathlib
import json
import numpy as np
from datetime import datetime
import pandas as pd


def format_datetime_to_date(dt):
    return dt.strftime('%Y%m%d')


def group_ts_by_gap(ts, gap):
    '''
    ts: time series
    gap: timedelta
    根据gap分割ts, 如果ts两个连续的timestamp的delta > gap, 在这里进行分割
    https://stackoverflow.com/questions/47415306/pandas-splitting-dataframe-into-multiple-dataframe-based-on-threshold-value
    '''
    ts_diff = ts.diff()
    x = (ts_diff>=gap)
    x.iloc[0] = 0
    x = x.cumsum()
    return x


def html_df(df):
    from IPython.display import HTML, display
    display(HTML(df.to_html()))
def html_df_near(df, i):
    html_df(df.iloc[i-10:i+10])


def check_for_stationarity(X, cutoff=0.01):
    # H_0 in adfuller is unit root exists (non-stationary)
    # We must observe significant p-value to convince ourselves that the series is stationary
    from statsmodels.tsa.stattools import adfuller
    pvalue = adfuller(X)[1]
    return pvalue < cutoff, pvalue


def get_df_near_timestamp(df, timestamp, delta=pd.to_timedelta('30 seconds')):
    start = timestamp - delta
    end = timestamp + delta
    return df[(df.index>start)&(df.index<end)]

