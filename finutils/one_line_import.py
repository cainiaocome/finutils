#!/usr/bin/env python

import os
import shlex
import subprocess

# install finutils
install_cmd = 'pip install --upgrade git+https://github.com/cainiaocome/finutils'
install_cmd = shlex.split(install_cmd)
completedprocess = subprocess.run(install_cmd, check=True)

python_code = '''
from finutils.rq import RqData, RqTick
from finutils.utils import html_df, html_df_near, group_ts_by_gap
from finutils.time_range import TimeRange, MultiTimeRange
'''
exec(python_code, globals(), locals())

print('the following code is executed automatically')
print(python_code)
