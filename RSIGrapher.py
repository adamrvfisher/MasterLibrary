# -*- coding: utf-8 -*-
"""

@author: Adam Reinhold Von Fisher - https://www.linkedin.com/in/adamrvfisher/

"""

#This is a strategy tester
#pandas_datareader is deprecated, use YahooGrabber

#Import modules
from pandas_datareader import data
import numpy as np

#Request data
s = data.DataReader('^GSPC', 'yahoo', start='1/1/2000', end='01/01/2050')

#Calculate log returns
s['LogRet'] = np.log(s['Adj Close']/s['Adj Close'].shift(1)) 
s['LogRet'] = s['LogRet'].fillna(0)
#Variable assignment
close = s['Adj Close']
window = 7    
delta = close.diff()
delta = delta[1:]
up, down = delta.copy(), delta.copy()
up[up < 0] = 0
down[down > 0] = 0
#RSI calculation
AvgGain = up.rolling(window).mean()
AvgLoss = down.abs().rolling(window).mean() 
RS = AvgGain/AvgLoss
RSI = 100 - (100/(1.0+RS))
#Vectorize
s['RSI'] = RSI
s['RSI'] = s['RSI'].fillna(0)
#Directional methodology 
s['Touch'] = np.where(s['RSI'] < 59.430916, 1,0) #long signal
s['Touch'] = np.where(s['RSI'] > 61.387121, -1, s['Touch']) #short signal
s['Sustain'] = np.where(s['Touch'].shift(1) == 1, 1, 0) # never actually true when optimized
s['Sustain'] = np.where(s['Sustain'].shift(1) == 1, 1, 
                                   s['Sustain']) 
s['Sustain'] = np.where(s['Touch'].shift(1) == -1, -1, 0) #true when previous day touch is -1, and current RSI is > line 37 threshold 
s['Sustain'] = np.where(s['Sustain'].shift(1) == -1, -1,
                                 s['Sustain']) 
s['Sustain'] = np.where(s['RSI'] > 63.617771, 0, s['Sustain']) #if RSI is greater than threshold, sustain is forced to 0
s['Sustain'] = np.where(s['RSI'] < 59.511533, 0, s['Sustain']) #never actually true when optimized
#Final regime
s['Regime'] = s['Touch'] + s['Sustain']
#Trim off time series when RSI still being calculated - apply position to returns
s['Strategy'] = (s['Regime'][window:]).shift(1)*s['LogRet'][window:]
s['Strategy'] = s['Strategy'].fillna(0)

#Ones
endgains = 1
endreturns = 1

#Cumulative returns
for g in s['LogRet']:
    slate = endreturns * (1+g)
    endreturns = slate
for q in s['Strategy']:
    otherslate = endgains * (1+q)
    endgains = otherslate
#Performance metric
sharpe = (s['Strategy'].mean()-s['LogRet'].mean())/s['Strategy'].std()
#Graphical display
s[['LogRet','Strategy']].cumsum().apply(np.exp).plot(grid=True,
                                                figsize=(8,5))
#Display results
print(endreturns)
print(endgains)                                                
print(sharpe)
