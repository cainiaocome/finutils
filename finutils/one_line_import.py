#!/usr/bin/env python

import os
import shlex
import subprocess

# install finutils
install_cmd = 'pip install --upgrade git+https://github.com/cainiaocome/finutils'
install_cmd = shlex.split(install_cmd)
completedprocess = subprocess.run(install_cmd, check=True)

python_code = '''
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


if pathlib.Path('/kaggle/input/').exists():
    data_dir = pathlib.Path('/kaggle/input/rqtick/')
else:
    data_dir = pathlib.Path('./data/')


from finutils.rq import RqData, RqTick
from finutils.utils import html_df, html_df_near, group_ts_by_gap
from finutils.time_range import TimeRange, MultiTimeRange


pd.set_option('display.float_format', lambda x: '%.4f' % x)


from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

'''
exec(python_code, globals(), locals())

print('the following code is executed automatically')
print(python_code)
