# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 19:07:37 2017

@author: AmatVictoriaCuramIII
"""
import numpy as np
import random as rand
import pandas as pd
import time as t
from DatabaseGrabber import DatabaseGrabber
from YahooGrabber import YahooGrabber
Empty = []
Dataset = pd.DataFrame()
Portfolio = pd.DataFrame()
Start = t.time()
Counter = 0

#Input

Ticker1 = 'UVXY'
Ticker2 = '^VIX'

#Remote Signal
Ticker3 = '^VIX'
Ticker4 = '^VXV'
#Here we go
Asset1 = YahooGrabber(Ticker1)
Asset2 = YahooGrabber(Ticker2)

#Remote Signal
Asset3 = YahooGrabber(Ticker3)
Asset4 = YahooGrabber(Ticker4)
#Match lengths

#Trimmer
trim = abs(len(Asset1) - len(Asset2))
if len(Asset1) == len(Asset2):
    pass
else:
    if len(Asset1) > len(Asset2):
        Asset1 = Asset1[trim:]
    else:
        Asset2 = Asset2[trim:]


Asset3 = Asset3[-len(Asset2):]
Asset4 = Asset4[-len(Asset2):]

#Asset2 = Asset2[-600:]

#Log Returns

Asset1['LogRet'] = np.log(Asset1['Adj Close']/Asset1['Adj Close'].shift(1))
Asset1['LogRet'] = Asset1['LogRet'].fillna(0)
Asset2['LogRet'] = np.log(Asset2['Adj Close']/Asset2['Adj Close'].shift(1))
Asset2['LogRet'] = Asset2['LogRet'].fillna(0)

#Prepare the remote controller
Asset3['LogRet'] = np.log(Asset3['Adj Close']/Asset3['Adj Close'].shift(1))
Asset3['LogRet'] = Asset3['LogRet'].fillna(0)

Asset3['Meter'] = (Asset3['Close']/Asset4['Close'])

##Retrim Assets
#Asset1 = Asset1[window:]
#Asset2 = Asset2[window:]                             
#Asset3 = Asset3[window:]

#Brute Force Optimization
iterations = range(0, 200000-----------------------------------------)

for i in iterations:
    Counter = Counter + 1
    a = rand.random()
    b = 1 - a
    c = rand.random()
    d = rand.random()
    if c + d > 1: continue
    e = 1.5 - (rand.random()*1)
    f = rand.randint(3,30)
    g = rand.randint(0,30)
    window2 = int(f)
    window3 = int(g)
    Asset3['Signal'] = np.where(Asset3['Meter'].shift(1) > e, 1, 0)
    Asset3['CumulativeRollingSignal'] = Asset3['Signal'].rolling(window = window2).sum()

    Asset1['Position'] = a
    Asset1['SmartPosition'] = np.where(Asset3['CumulativeRollingSignal'] > window3, c, a)                                 
    Asset1['Pass'] = (Asset1['LogRet'] * Asset1['Position'])
    
    Asset2['Position'] = b
    Asset2['SmartPosition'] = np.where(Asset3['CumulativeRollingSignal'] > window3, d, b) 
    Asset2['Pass'] = (Asset2['LogRet'] * Asset2['Position'])
    
    Portfolio['Asset1Pass'] = (Asset1['Pass']) * (-1) #Pass a short position
    Portfolio['Asset2Pass'] = (Asset2['Pass']) #* (-1)


    
    Portfolio['LongShort'] = (Portfolio['Asset1Pass']) + (Portfolio['Asset2Pass'])   
    if Portfolio['LongShort'].std() == 0:    
        continue
    
    Portfolio['Multiplier'] = Portfolio['LongShort'].cumsum().apply(np.exp)
    drawdown =  1 - Portfolio['Multiplier'].div(Portfolio['Multiplier'].cummax())
    MaxDD = max(drawdown)
    if MaxDD > float(.3): 
        continue
    
    dailyreturn = Portfolio['LongShort'].mean()
    if dailyreturn < .002:
        continue
    
    dailyvol = Portfolio['LongShort'].std()
    sharpe =(dailyreturn/dailyvol)
    
    Portfolio['Multiplier'] = Portfolio['LongShort'].cumsum().apply(np.exp)
    drawdown =  1 - Portfolio['Multiplier'].div(Portfolio['Multiplier'].cummax())
    MaxDD = max(drawdown)
    print(Counter)
    Empty.append(a)
    Empty.append(b)
    Empty.append(c)
    Empty.append(d)
    Empty.append(e)
    Empty.append(f)
    Empty.append(g)
    Empty.append(sharpe)
    Empty.append(sharpe/MaxDD)
    Empty.append(dailyreturn/MaxDD)
    Empty.append(MaxDD)
    Emptyseries = pd.Series(Empty)
    Dataset[0] = Emptyseries.values
    Dataset[i] = Emptyseries.values
    Empty[:] = [] 
    
z1 = Dataset.iloc[8]
w1 = np.percentile(z1, 80)
v1 = [] #this variable stores the Nth percentile of top performers
DS1W = pd.DataFrame() #this variable stores your financial advisors for specific dataset
for h in z1:
    if h > w1:
      v1.append(h)
for j in v1:
      r = Dataset.columns[(Dataset == j).iloc[8]]    
      DS1W = pd.concat([DS1W,Dataset[r]], axis = 1)
y = max(z1)
k = Dataset.columns[(Dataset == y).iloc[8]] #this is the column number
kfloat = float(k[0])
End = t.time()
print(End-Start, 'seconds later')
print(Dataset[k])


window = (Dataset[kfloat][4])
window2 = int(Dataset[kfloat][5])
window3 = int(Dataset[kfloat][6])
  
Asset3['Signal'] = np.where(Asset3['Meter'].shift(1) > Dataset[kfloat][4], 1, 0)
Asset3['CumulativeRollingSignal'] = Asset3['Signal'].rolling(window = window2).sum()

Asset1['Position'] = Dataset[kfloat][0]
Asset1['SmartPosition'] = np.where(Asset3['CumulativeRollingSignal'] > window3,
                                     Dataset[kfloat][2], Dataset[kfloat][0])                                 
Asset1['Pass'] = (Asset1['LogRet'] * Asset1['Position'])

Asset2['Position'] = Dataset[kfloat][1]
Asset2['SmartPosition'] = np.where(Asset3['CumulativeRollingSignal'] > window3,
                                     Dataset[kfloat][3], Dataset[kfloat][1]) 
Asset2['Pass'] = (Asset2['LogRet'] * Asset2['Position'])

Portfolio['Asset1Pass'] = Asset1['Pass'] * (-1)
Portfolio['Asset2Pass'] = Asset2['Pass'] #* (-1)
#Portfolio['PriceRelative'] = Asset1['Adj Close'] / Asset2['Adj Close']
#asone['PriceRelative'][-180:].plot(grid = True, figsize = (8,5))
Portfolio['LongShort'] = Portfolio['Asset1Pass'] + Portfolio['Asset2Pass'] 
Portfolio['LongShort'][:].cumsum().apply(np.exp).plot(grid=True, figsize=(8,5))
dailyreturn = Portfolio['LongShort'].mean()
dailyvol = Portfolio['LongShort'].std()
sharpe =(dailyreturn/dailyvol)
Portfolio['Multiplier'] = Portfolio['LongShort'].cumsum().apply(np.exp)
drawdown2 =  1 - Portfolio['Multiplier'].div(Portfolio['Multiplier'].cummax())
#conversionfactor = Portfolio['PriceRelative'][-1]
print(max(drawdown2))
#pd.to_pickle(Portfolio, 'VXX:UVXY')