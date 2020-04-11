!pip install --upgrade git+https://github.com/cainiaocome/finutils
try:
    import mlfinlab
except:
    !pip install --upgrade mlfinlab

import os
import sys
import pathlib
import pandas as pd
import sklearn 
import numpy as np
import random
from time import sleep
import statsmodels.api as sm
from sklearn import linear_model
import matplotlib.pyplot as plt
from pprint import pprint
import warnings
import itertools
import mlfinlab
from datetime import datetime, time, timedelta
from concurrent.futures import ProcessPoolExecutor
warnings.filterwarnings('ignore')


from finutils.rq import RqData, RqTick
from finutils.utils import html_df, html_df_near, group_ts_by_gap
from finutils.time_range import TimeRange, MultiTimeRange, get_market_open_and_close_time_range


pd.set_option('display.float_format', lambda x: '%.4f' % x)


# display cell's all output
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


if pathlib.Path('/kaggle/input/').exists():
    data_dir = pathlib.Path('/kaggle/input/rqtick/')
else:
    data_dir = pathlib.Path('./data/')


market_open_and_close_time_range = get_market_open_and_close_time_range()
