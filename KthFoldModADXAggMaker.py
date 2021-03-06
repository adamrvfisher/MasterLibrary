# -*- coding: utf-8 -*-
"""

@author: Adam Reinhold Von Fisher - https://www.linkedin.com/in/adamrvfisher/

"""

#pandas_datareader is deprecated, use YahooGrabber
#This is part of a kth fold optimization tool

#Import module
import numpy as np
import pandas as pd
import time as t
from pandas_datareader import data
#Empty data structures
empty = []
openspace = []
openseries = pd.Series()
testsetwinners = pd.DataFrame()
#Define function
def ModADXAggMaker(ticker, testset, firsttime, secondtime):
    #Start timer
    starttime = t.time()    
    #Request data
    s = data.DataReader(ticker, 'yahoo', start=firsttime, end=secondtime)
    #Calculate log returns
    s['LogRet'] = np.log(s['Adj Close']/s['Adj Close'].shift(1)) 
    s['LogRet'] = s['LogRet'].fillna(0)
    #Calculate ATR
    s['UpMove'] = s['High'] - s['High'].shift(1)
    s['DownMove'] = s['Low'] - s['Low'].shift(1)
    s['Method1'] = s['High'] - s['Low']
    s['Method2'] = abs((s['High'] - s['Adj Close'].shift(1)))
    s['Method3'] = abs((s['Low'] - s['Adj Close'].shift(1)))
    s['Method1'] = s['Method1'].fillna(0)
    s['Method2'] = s['Method2'].fillna(0)
    s['Method3'] = s['Method3'].fillna(0)
    s['TrueRange'] = s[['Method1','Method2','Method3']].max(axis = 1)
    #Calculate ADX
    s['PDM'] = (s['High'] - s['High'].shift(1))
    s['MDM'] = (s['Low'].shift(1) - s['Low'])
    s['PDM'] = s['PDM'][s['PDM'] > 0]
    s['MDM'] = s['MDM'][s['MDM'] > 0]
    s['PDM'] = s['PDM'].fillna(0)
    s['MDM'] = s['MDM'].fillna(0)
    #Iteration tracking
    counter = 0
    #Number of params
    size = len(testset.iloc[0])
    #For all params in testset
    for i in testset:    
        #Iteration tracking
        counter = counter + 1  
        ratio = counter/size
        #Load params to variables
        aa = testset.loc[0,i] #numer of days for moving average window
        a = aa.astype(int)
        b = testset[i].iloc[1]
        c = testset[i].iloc[2] 
        d = testset[i].iloc[3]
        window = a
        #ATR calculation
        s['AverageTrueRange'] = s['TrueRange'].rolling(window = window,
                                        center=False).sum()
        s['AverageTrueRange'] = ((s['AverageTrueRange'].shift(1)*(window-1
                                     ) + s['TrueRange']) / window)
        #ADX calculation
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
        s['ADXmean'] = s['ADX'].mean() * b
        #Directional methodology
        s['Touch'] = np.where(s['DIdivergence'] < c, 1,0) #long signal
        s['Touch'] = np.where(s['DIdivergence'] > d, -1, s['Touch']) #short signal
        s['Sustain'] = 0
        s['Sustain'] = np.where(s['ADX'] >  s['ADXmean'], 0, s['Sustain']) #if RSI is greater than threshold, sustain is forced to 0
        s['Sustain'] = np.where(s['ADX'] < s['ADXmean'], (s['Touch']*-1
                              ), s['Sustain']) #never actually true when optimized
        s['Regime'] = s['Touch'] + s['Sustain']
        #Apply position to returns
        s['Strategy'] = (s['Regime']).shift(1)*s['LogRet']
        s['Strategy'] = s['Strategy'].fillna(0)
        #Iteration tracking
        print(ratio)
        #Constraints
        if s['Strategy'].std() == 0:
            continue
        #Performance metrics
        s['sharpe'] = (s['Strategy'].mean()-s['LogRet'].mean(
                                ))/s['Strategy'].std()
        #Constraints
        if s['sharpe'][-1] < .03:
            continue        
        #Add params and metrics to list
        openspace.append(a)
        openspace.append(b)
        openspace.append(c)
        openspace.append(d)
        openspace.append(s['sharpe'][-1])
        #List to Series
        openseries = pd.Series(openspace)
        #Series to dataframe
        testsetwinners[i] = openseries.values
        #Clear list
        openspace[:] = []
    #End timer
    endtime = t.time()
    #Timer stats
    print('That dataset took ', endtime-starttime,' seconds')    
    #Output optimal params
    return testsetwinners
