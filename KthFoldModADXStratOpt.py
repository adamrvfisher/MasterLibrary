# -*- coding: utf-8 -*-
"""

@author: Adam Reinhold Von Fisher - https://www.linkedin.com/in/adamrvfisher/

"""

#This is a brute force optimization tool that is part of a kth fold optimization tool

#Import modules
import pandas as pd
from pandas_datareader import data
import numpy as np
import random as rand

#Define function
def DefModADXStratOpt(ranger2, s):
    #Request data
#    s = data.DataReader(ticker, 'yahoo', start=starttime, end=endtime)
    #Assign data structures
    empty = []
    counter = 0
    dataset = pd.DataFrame()
    #For all iterations 
    for r in ranger2: 
        #Random variable generation
        a = rand.randint(1,60)
        b = rand.random() * 2
        c = 100 - rand.random() * 200
        d = 100 - rand.random() * 200
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
        #Apply position to log returns
        s['Strategy'] = (s['Regime']).shift(1)*s['LogRet']
        s['Strategy'] = s['Strategy'].fillna(0)  
        #Constraints
        if s['Strategy'].std() == 0:
            continue
        #Performance metric
        s['sharpe'] = (s['Strategy'].mean()-s['LogRet'].mean(
                                                    ))/s['Strategy'].std()
        #Constraints
        if s['sharpe'][-1] < -.05:        
            continue      
        #Add params and metric to list
        empty.append(a)
        empty.append(b)
        empty.append(c)
        empty.append(d)
        empty.append(s['sharpe'][-1])
        #List to Series
        emptyseries = pd.Series(empty)
        #Series to dataframe
        dataset[r] = emptyseries.values
        #Clear list
        empty[:] = []      
    #Metric of choice
    z1 = dataset.iloc[4]
    #Threshold
    w1 = np.percentile(z1, 95)
    v1 = [] #this variable stores the Nth percentile of top params
    DS1W = pd.DataFrame() #this variable stores your params for specific dataset
    #For all metrics
    for h in z1:
        #If metric greater than threshold
        if h > w1:
          #Add to list
          v1.append(h)
    #For top params
    for j in v1:
          #Find column ID
          r = dataset.columns[(dataset == j).iloc[4]]   
          #Add params to dataframe by column ID 
          DS1W = pd.concat([DS1W,dataset[r]], axis = 1)
    #Output top param sets    
    return DS1W
