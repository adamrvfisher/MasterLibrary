# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 14:31:49 2017

@author: AmatVictoriaCuramIII
"""
import numpy as np
from pandas_datareader import data
import pandas as pd
ticker = '^GSPC'
s = data.DataReader(ticker, 'yahoo', start='01/01/2006', end='01/01/2050')
s['LogRet'] = np.log(s['Adj Close']/s['Adj Close'].shift(1)) 
s['LogRet'] = s['LogRet'].fillna(0)
s['CLV'] = (((s['Adj Close'] - s['Low']) - (s['High'] - s['Adj Close']))
                    / (s['High'] - s['Low']))
Length = len(s['LogRet'])
Range = range(0,Length-1)
index = s.index
a = 20 #number of days for moving average window
b = 43 #numer of days for moving average window
multiplierA = (2/(a+1))
multiplierB = (2/(b+1))
s['ADI'] = (s['Volume'] * s['CLV']).cumsum()
EMAyesterdayA = s['ADI'][0] #these prices are based off the SMA values
EMAyesterdayB = s['ADI'][0] #these prices are based off the SMA values
smallEMA = [EMAyesterdayA]
for i in Range:
    holder = (s['ADI'][i]*multiplierA) + (EMAyesterdayA *
                                            (1-multiplierA))
    smallEMA.append(holder)
    EMAyesterdayA = holder
smallEMAseries = pd.Series(smallEMA[:], index=s.index)    
largeEMA = [EMAyesterdayB]
for i in Range:
    holder1 = (s['ADI'][i]*multiplierB) + (EMAyesterdayB *
                                            (1-multiplierB))
    largeEMA.append(holder1)
    EMAyesterdayB = holder1
largeEMAseries = pd.Series(largeEMA[:], index=s.index)
s['ADIEMAsmall'] = smallEMAseries
s['ADIEMAlarge'] = largeEMAseries
s['Chaikin'] = s['ADIEMAsmall'] - s['ADIEMAlarge']
s['ZeroLine'] = 0
volumewindow = 21
s['AverageRollingVolume'] = s['Volume'].rolling(center=False,
                                        window=volumewindow).mean()
s['NormChaikin'] = s['Chaikin']/s['AverageRollingVolume']
s[['ADI','ADIEMAsmall','ADIEMAlarge']].plot(grid=True, figsize = (8,3))
kk = s[:volumewindow-1]
s = s[volumewindow-1:]
s['Touch'] = np.where(s['NormChaikin'] < 0, 1,0) #long signal
s['Touch'] = np.where(s['NormChaikin'] > 0, -1, s['Touch']) #short signal
s['Sustain'] = np.where(s['Touch'].shift(1) == 1, 1, 0) # never actually true when optimized
s['Sustain'] = np.where(s['Sustain'].shift(1) == 1, 1, 
                                 s['Sustain']) 
s['Sustain'] = np.where(s['Touch'].shift(1) == -1, -1, 0) #true when previous day touch is -1, and current RSI is > line 37 threshold 
s['Sustain'] = np.where(s['Sustain'].shift(1) == -1, -1,
                                 s['Sustain']) 
s['Sustain'] = np.where(s['NormChaikin'] > 0, 0, s['Sustain']) #if RSI is greater than threshold, sustain is forced to 0
s['Sustain'] = np.where(s['NormChaikin'] < 0, 0, s['Sustain']) #never actually true when optimized
s['Regime'] = s['Touch'] + s['Sustain']
s['Strategy'] = (s['Regime']).shift(1)*s['LogRet']
s['Strategy'] = s['Strategy'].fillna(0)
sharpe = (s['Strategy'].mean()-s['LogRet'].mean())/s['Strategy'].std()
#s[['LogRet','Strategy']].cumsum().apply(np.exp).plot(grid=True,
#                                 figsize=(8,5))
s[['NormChaikin', 'ZeroLine']].plot(grid=True, figsize = (8,3))
s = kk.append(s)
Length = len(s['LogRet'])
Range = range(0,Length)
print(sharpe)
