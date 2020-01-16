# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 16:36:25 2017

@author: AmatVictoriaCuramIII
"""

#This is part of a multithreading tool to speed up brute force optimization - may be unfinished.

from numba import jit
@jit

def multithreadADXStratOpt():
    import pandas as pd
    from pandas_datareader import data
    import numpy as np
    import time as t
    import random as rand
    ticker = '^GSPC'
    s = data.DataReader(ticker, 'yahoo', start='01/01/2016', end='01/01/2050')
    iterations = range(0,800)
    counter = 0
    empty = []
    dataset = pd.DataFrame()
    start = t.time()
    s['UpMove'] = s['High'] - s['High'].shift(1)
    s['DownMove'] = s['Low'] - s['Low'].shift(1)
    s['LogRet'] = np.log(s['Adj Close']/s['Adj Close'].shift(1)) 
    s['LogRet'] = s['LogRet'].fillna(0)
    s['Method1'] = s['High'] - s['Low']
    s['Method2'] = abs((s['High'] - s['Adj Close'].shift(1)))
    s['Method3'] = abs((s['Low'] - s['Adj Close'].shift(1)))
    s['Method1'] = s['Method1'].fillna(0)
    s['Method2'] = s['Method2'].fillna(0)
    s['Method3'] = s['Method3'].fillna(0)
    s['TrueRange'] = s[['Method1','Method2','Method3']].max(axis = 1)
    s['PDM'] = (s['High'] - s['High'].shift(1))
    s['MDM'] = (s['Low'].shift(1) - s['Low'])
    s['PDM'] = s['PDM'][s['PDM'] > 0]
    s['MDM'] = s['MDM'][s['MDM'] > 0]
    s['PDM'] = s['PDM'].fillna(0)
    s['MDM'] = s['MDM'].fillna(0)
    for x in iterations:
        counter = counter + 1    
        a = rand.randint(1,30)
        b = 100 - rand.random() * 200
        c = 100 - rand.random() * 200
        d = 100 - rand.random() * 200
        e = 100 - rand.random() * 200
        window = a
        s['AverageTrueRange'] = s['TrueRange'].rolling(window = window,
                                        center=False).sum()
        s['AverageTrueRange'] = ((s['AverageTrueRange'].shift(1)*(window-1
                                     ) + s['TrueRange']) / window)
        s['SmoothPDM'] = s['PDM'].rolling(window = window,
                                        center=False).sum()
        s['SmoothPDM'] = ((s['SmoothPDM'].shift(1)*(window-1
                                     ) + s['PDM']) / window)
        s['SmoothMDM'] = s['MDM'].rolling(window = window,
                                        center=False).sum()
        s['SmoothMDM'] = ((s['SmoothMDM'].shift(1)*(window-1
                                     ) + s['MDM']) / window)
        s['PDI'] = (100*(s['SmoothPDM']/s['AverageTrueRange']))
        s['MDI'] = (100*(s['SmoothMDM']/s['AverageTrueRange']))
        s['DIdiff'] = abs(s['PDI'] - s['MDI'])
        s['DIdivergence'] = s['PDI'] - s['MDI']
        s['DIsum'] = s['PDI'] + s['MDI']
        s['DX'] = (100 * (s['DIdiff']/s['DIsum']))
        s['DX'] = s['DX'].fillna(0)
        s['ADX'] = s['DX'].rolling(window = window, center = False).mean()
        s['ADXmean'] = s['ADX'].mean()
        s['Touch'] = np.where(s['DIdivergence'] < b, 1,0) #long signal
        s['Touch'] = np.where(s['DIdivergence'] > c, -1, s['Touch']) #short signal
        s['Sustain'] = np.where(s['Touch'].shift(1) == 1, 1, 0) # never actually true when optimized
        s['Sustain'] = np.where(s['Sustain'].shift(1) == 1, 1, 
                                         s['Sustain']) 
        s['Sustain'] = np.where(s['Touch'].shift(1) == -1, -1, 0) #true when previous day touch is -1, and current RSI is > line 37 threshold 
        s['Sustain'] = np.where(s['Sustain'].shift(1) == -1, -1,
                                         s['Sustain']) 
        s['Sustain'] = np.where(s['DIdivergence'] > d, 0, s['Sustain']) #if RSI is greater than threshold, sustain is forced to 0
        s['Sustain'] = np.where(s['DIdivergence'] < e, 0, s['Sustain']) #never actually true when optimized
        s['Regime'] = s['Touch'] + s['Sustain']
        s['Strategy'] = (s['Regime']).shift(1)*s['LogRet']
        s['Strategy'] = s['Strategy'].fillna(0)
        if s['Strategy'].std() == 0:    
            continue
        s['sharpe'] = (s['Strategy'].mean()-s['LogRet'].mean())/s['Strategy'].std()
        if s['sharpe'][-1] < 0.01:     
            continue
        if s['LogRet'].cumsum().apply(np.exp)[-1] > s['Strategy'].cumsum(
                                ).apply(np.exp)[-1]:     
            continue                                
        print(counter)
        empty.append(a)
        empty.append(b)
        empty.append(c)
        empty.append(d)
        empty.append(e)
        empty.append(s['sharpe'][-1])
        emptyseries = pd.Series(empty)
        dataset[x] = emptyseries.values
        empty[:] = []      
    z1 = dataset.iloc[5]
    w1 = np.percentile(z1, 80)
    v1 = [] #this variable stores the Nth percentile of top performers
    DS1W = pd.DataFrame() #this variable stores your financial advisors for specific dataset
    for h in z1:
        if h > w1:
          v1.append(h)
    for j in v1:
          r = dataset.columns[(dataset == j).iloc[5]]    
          DS1W = pd.concat([DS1W,dataset[r]], axis = 1)
    y = max(z1)
    k = dataset.columns[(dataset == y).iloc[5]] #this is the column number
    end = t.time()
    print(end-start, 'seconds later')
    return dataset[k]
