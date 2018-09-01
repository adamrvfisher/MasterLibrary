# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 19:07:37 2017

@author: AmatVictoriaCuramIII
"""

import numpy as np
from pandas_datareader import data
import random as rand
import pandas as pd
import time as t
from DatabaseGrabber import DatabaseGrabber
empty = []
dataset = pd.DataFrame()
asone = pd.DataFrame()
listoftickers = ['UVXY', 'VXX', '^VIX', 'VXV', 'TLT', '^GSPC']
start = t.time()
counter = 0

#the goal is to make a for loop to get all combinations of tickers and find 
#predictable relationships/trends

UVXY = DatabaseGrabber('UVXY')
VXX = DatabaseGrabber('VXX')

UVXY['LogRet'] = np.log(UVXY['Adj Close']/UVXY['Adj Close'].shift(1))
UVXY['LogRet'] = UVXY['LogRet'].fillna(0)
VXX['LogRet'] = np.log(VXX['Adj Close']/VXX['Adj Close'].shift(1))
VXX['LogRet'] = VXX['LogRet'].fillna(0)

iterations = range(0, 500)
for i in iterations:
    counter = counter + 1
    a = rand.random()
    b = 1 - a
    
    UVXY['Position'] = a
    UVXY['Pass'] = UVXY['LogRet'] * UVXY['Position']
    VXX['Position'] = b
    VXX['Pass'] = VXX['LogRet'] * VXX['Position']
    
    asone['VXXpass'] = VXX['Pass']
    asone['UVXYpass'] = UVXY['Pass']
    asone['PriceRelative'] = VXX['Adj Close'] / UVXY['Adj Close']
    #asone['PriceRelative'][-180:].plot(grid = True, figsize = (8,5))
    asone['LongShort'] = UVXY['Pass'] + (-1 * VXX['Pass']) 
#    asone = asone[:-2]
#    asone['LongShort'][-180:].cumsum().apply(np.exp).plot(grid=True,
#                                     figsize=(8,5))

    dailyreturn = asone['LongShort'].mean()
    dailyvol = asone['LongShort'].std()

    if asone['LongShort'].std() == 0:    
        continue

    sharpe =(dailyreturn/(dailyvol))

    if sharpe < 0.042:     
        continue

    portfoliomultiplier = asone['LongShort'].cumsum().apply(np.exp)
    maxdd = 0
    tempdd = 0 
    highwater = 1
    ranger = range(0,len(portfoliomultiplier))

    for r in ranger:
        currentvalue = portfoliomultiplier[r]
        if highwater == 0:
            currentvalue = highwater
        if currentvalue > highwater:
            highwater = currentvalue
        else:
            tempdd = 1 - (currentvalue/highwater)
        if tempdd > maxdd:
            maxdd = tempdd
            tempdd = 0
    print(counter)    
    empty.append(a)
    empty.append(b)
    empty.append(sharpe)
    empty.append(sharpe/maxdd)
    emptyseries = pd.Series(empty)
    dataset[i] = emptyseries.values
    empty[:] = [] 
z1 = dataset.iloc[3]
w1 = np.percentile(z1, 80)
v1 = [] #this variable stores the Nth percentile of top performers
DS1W = pd.DataFrame() #this variable stores your financial advisors for specific dataset
for h in z1:
    if h > w1:
      v1.append(h)
for j in v1:
      r = dataset.columns[(dataset == j).iloc[3]]    
      DS1W = pd.concat([DS1W,dataset[r]], axis = 1)
y = max(z1)
k = dataset.columns[(dataset == y).iloc[3]] #this is the column number
kfloat = float(k[0])
end = t.time()
print(end-start, 'seconds later')
print(dataset[k])




UVXY['Position'] = (dataset[kfloat][0])/2
UVXY['Pass'] = UVXY['LogRet'] * UVXY['Position']
VXX['Position'] = (dataset[kfloat][1])/2
VXX['Pass'] = VXX['LogRet'] * VXX['Position']

asone['VXXpass'] = VXX['Pass']
asone['UVXYpass'] = UVXY['Pass']
asone['PriceRelative'] = VXX['Adj Close'] / UVXY['Adj Close']
#asone['PriceRelative'][-180:].plot(grid = True, figsize = (8,5))
asone['LongShort'] = UVXY['Pass'] + (-1 * VXX['Pass']) 
asone['LongShort'][:].cumsum().apply(np.exp).plot(grid=True,
                                     figsize=(8,5))

dailyreturn = asone['LongShort'].mean()
dailyvol = asone['LongShort'].std()
sharpe =(dailyreturn)
portfoliomultiplier = asone['LongShort'].cumsum().apply(np.exp)
maxdd = 0
tempdd = 0 
highwater = 1
ranger = range(0,len(portfoliomultiplier))

for r in ranger:
    currentvalue = portfoliomultiplier[r]
    if highwater == 0:
        currentvalue = highwater
    if currentvalue > highwater:
        highwater = currentvalue
    else:
        tempdd = 1 - (currentvalue/highwater)
    if tempdd > maxdd:
        maxdd = tempdd
        tempdd = 0
print('Max drawdown is ' + str(maxdd))