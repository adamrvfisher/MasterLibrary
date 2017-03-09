# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:12:37 2017

@author: AmatVictoriaCuramIII
"""

import numpy as np
from pandas_datareader import data
import pandas as pd
s = data.DataReader('^GSPC', 'yahoo', start='9/1/2016', end='01/01/2050')
s['LogReturn'] = np.log(s['Adj Close']/s['Adj Close'].shift(1))
s['LogReturn'] = s['LogReturn'].fillna(0)
Length = len(s['LogReturn'])
Range = range(0,Length)
OBV = []
store = 0
for i in Range:
    if s['LogReturn'][i] > 0:
        store = store + s['Volume'][i]
        OBV.append(store)
    elif s['LogReturn'][i] < 0:
        store = store - s['Volume'][i]
        OBV.append(store)
    elif s['LogReturn'][i] == 0:
        store = store + 0
        OBV.append(store)
OBVSeries = pd.Series(OBV)
OBVSeries.plot(grid=True, figsize = (8,5))