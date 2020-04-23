#!/usr/bin/env python

import pandas as pd
from datetime import datetime, time, timedelta
from collections import Iterable

class TimeRange:
    def __init__(self, start: time, end:time):
        self.start = start
        self.end = end

    def __contains__(self, x:time):
        return x>=self.start and x<=self.end

    def __repr__(self):
        return f'TimeRange {self.start} -> {self.end}'

    @classmethod
    def from_time_and_timedelta(cls, center: time, deviation:timedelta):
        dummy_datetime = datetime(2020,3,15,center.hour, center.minute, center.second, center.microsecond)
        start = (dummy_datetime - deviation).time()
        end = (dummy_datetime + deviation).time()
        return cls(start, end)


class MultiTimeRange:
    def __init__(self, *args):
        self.time_range_list = args

    def __contains__(self, x):
        '''
        magic method __contains__ can only return True/False, or else will be converted by python automatically
        '''
        for time_range in self.time_range_list:
            if x in time_range:
                return True
        return False

    def include_these(self, x):
        def include_this(x):
            if type(x) in [datetime, pd.Timestamp]:
                x = x.time()
            return (x in self)
        if isinstance(x, pd.DatetimeIndex):
            x = list(x)
        if isinstance(x, Iterable):
            return [include_this(i) for i in x]
        return include_this(x)
            
    def __repr__(self):
        s = 'MultiTimeRange:\n'
        for tr in self.time_range_list:
            s += f'- {tr}\n'
        return s

    def add_time_range(self, time_range):
        self.time_range_list.append(time_range)


def get_market_open_and_close_time_range(td=timedelta(minutes=3)):
	return MultiTimeRange(
		# morning
		TimeRange.from_time_and_timedelta(time(9, 0), td),
		TimeRange.from_time_and_timedelta(time(11, 30), td),
		# afternoon
		TimeRange.from_time_and_timedelta(time(13, 30), td),
		TimeRange.from_time_and_timedelta(time(15, 0),td),
		# night trade time range  
		# only for au now
		TimeRange.from_time_and_timedelta(time(21, 0), td),
		TimeRange.from_time_and_timedelta(time(2, 30), td),
	)
