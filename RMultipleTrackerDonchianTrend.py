# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:04:55 2018

@author: AmatVictoriaCuramIII
"""
#Developed in Python 3.5

#This is a trading strategy model with graphical display
#It looks like the stop logic and exit logic are correct
#also see DonchianTrendEfficiencyFilterSingleStockSingleFrequency.py

#R Multiple; Trade Tracking
import numpy as np
#import random as rand
import pandas as pd
#import time as t
#from DatabaseGrabber import DatabaseGrabber
from YahooGrabber import YahooGrabber
#import matplotlib.pyplot as plt
import warnings 
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates

#Inputs - OHLC data
Ticker1 = 'GLD'
#Asset1 = YahooGrabber(Ticker1)
Asset1 = Asset
##Tasty OHLC; ***ATTN*** insert path for OHLC data
#Asset1 = pd.read_pickle('C:\\Users\\Tasty\\Desktop\\WorkingDirectory\\GLD')

#Don't display warnings 
warnings.filterwarnings("ignore",category =RuntimeWarning) 
pd.options.mode.chained_assignment = None 
#Declaration/Assignments
#Empty list
Empty = []
#Empty dataframe
Trades = pd.DataFrame()
Equity = 100000
RiskPerTrade = Equity * .005 
#Constraints in percentages
Commission = .01
Slippage = .01

#Time series trimmer for in/out sample data
Asset1 = Asset1[-1500:] #In
#

#Variable windows
donchianwindow = 55
ATRwindow = 20
stopwindow = 13
Counter = 0
#Log Returns
Asset1['Index'] = Asset1.index
Asset1['SubIndex'] = range(0,len(Asset1))
Asset1['IndexToNumber'] = Asset1['Index'].apply(mdates.date2num)
Asset1['LogRet'] = np.log(Asset1['Adj Close']/Asset1['Adj Close'].shift(1))
Asset1['LogRet'] = Asset1['LogRet'].fillna(0)
Asset1['Method1'] = Asset1['High'] - Asset1['Low']
Asset1['Method2'] = abs((Asset1['High'] - Asset1['Close'].shift(1)))
Asset1['Method3'] = abs((Asset1['Low'] - Asset1['Close'].shift(1)))
Asset1['Method1'] = Asset1['Method1'].fillna(0)
Asset1['Method2'] = Asset1['Method2'].fillna(0)
Asset1['Method3'] = Asset1['Method3'].fillna(0)
Asset1['TrueRange'] = Asset1[['Method1','Method2','Method3']].max(axis = 1)
#ATR in points; not %
Asset1['ATR'] = Asset1['TrueRange'].rolling(window = ATRwindow,
                                center=False).mean()

#Market top and bottom calculation
Asset1['RollingMax'] = Asset1['High'].rolling(window=donchianwindow, center=False).max()
Asset1['RollingMin'] = Asset1['Low'].rolling(window=donchianwindow, center=False).min()

#Asset1[['RollingMax','RollingMin','Close']].plot()

#Signal = Price </> min/max
#if price is less than the min go long
#if price is greater than the max go short
Asset1['LongSignal'] = np.where(Asset1['High'] >= Asset1['RollingMax'].shift(1) , 1, 0)
Asset1['ShortSignal'] = np.where(Asset1['Low'] <= Asset1['RollingMin'].shift(1) , 1, 0)
#If double signal days exist, then entry and P/L on those days will not be reflected correctly 
Asset1['DoubleDay'] = np.where(Asset1['LongSignal'] + Asset1['ShortSignal'] == 2, 1, 0)

Asset1['Signal'] = np.where(Asset1['LongSignal'] == 1, 1, 0)
Asset1['Signal'] = np.where(Asset1['ShortSignal'] == 1, -1, Asset1['Signal'])
#if Rolling Min/Max is still being computed, stay out of market
Asset1['Signal'] = np.where(Asset1['RollingMax'] == np.nan, 0, Asset1['Signal'])

#Indexes for segmenting data for trade analysis
SignalDates = list(Asset1['Signal'].loc[(Asset1['Signal'] != 0)].index)

#Trade ATR for signal
Asset1['TradeATR'] = np.where(Asset1['Signal'] != 0, Asset1['ATR'].shift(1), np.nan)
#experimental exits
Asset1['LimitExitPrice'] = np.nan
Asset1['ShortExitPrice'] =  Asset1['High'].rolling(window=stopwindow, center=False).max()
Asset1['LongExitPrice'] =  Asset1['Low'].rolling(window=stopwindow, center=False).min()

#Find the first trade of the signal period, so we can document entry prices
#Declare columns to record entry price and stop for unit one
Asset1['EntryPriceUnitOne'] = np.nan
Asset1['StopPriceUnitOne'] = np.nan

#Be sure to check for double signal days, gaps on first unit entry, and gaps on exits.


#Default stops and entries
#Long entry first unit
Asset1['EntryPriceUnitOne'] = np.where(Asset1['Signal'] == 1, 
                              Asset1['RollingMax'].shift(1) + .01, np.nan)
#Short entry first unit
Asset1['EntryPriceUnitOne'] = np.where(Asset1['Signal'] == -1, 
              Asset1['RollingMin'].shift(1) - .01, Asset1['EntryPriceUnitOne'])


#Long gap entry first unit
#Find all days that gap above entry on open
LongGapEntryIndexList = list(Asset1['EntryPriceUnitOne'].loc[(Asset1['Signal'] == 1) & (
            Asset1['Open'] > Asset1['EntryPriceUnitOne'])].index)
#For all LongGapEntries use open price
for l in LongGapEntryIndexList:
    Asset1.set_value(l, 'EntryPriceUnitOne', Asset1.loc[l]['Open'])
    

#Short gap entry first unit
#Find all days that gap below entry on open 
ShortGapEntryIndexList = list(Asset1['EntryPriceUnitOne'].loc[(Asset1['Signal'] == -1) & (
            Asset1['Open'] < Asset1['EntryPriceUnitOne'])].index)
#For all ShortGapEntries use open price
for s in ShortGapEntryIndexList:
    Asset1.set_value(s, 'EntryPriceUnitOne', Asset1.loc[s]['Open'])


#Fixed long stop first unit
Asset1['StopPriceUnitOne'] = np.where(Asset1['Signal'] == 1, 
                Asset1['EntryPriceUnitOne'] - (Asset1['TradeATR'] * 2), np.nan)
#Fixed short stop first unit
Asset1['StopPriceUnitOne'] = np.where(Asset1['Signal'] == -1, 
              Asset1['EntryPriceUnitOne'] + (Asset1['TradeATR'] * 2), Asset1['StopPriceUnitOne'])
              

#Experimental exits - combine fixed stop with trailing max high/min low
Asset1['HybridLongExitPrice'] = np.where(Asset1['LongExitPrice'] > Asset1['StopPriceUnitOne'], 
                          Asset1['LongExitPrice'], Asset1['StopPriceUnitOne'])
Asset1['HybridLongExitPrice'] = Asset1['HybridLongExitPrice'].ffill()

Asset1['HybridShortExitPrice'] = np.where(Asset1['ShortExitPrice'] < Asset1['StopPriceUnitOne'],
                          Asset1['ShortExitPrice'], Asset1['StopPriceUnitOne'])  
Asset1['HybridShortExitPrice'] = Asset1['HybridShortExitPrice'].ffill()

               
#TradeSubset is a 'copy' of Asset1 starting from the first signal date, we make a trade and trim it, make a trade and trim.    
#The first trade is being set up. Trim 
TradeSubset = Asset1.loc[(Asset1.index >= SignalDates[0])] 

#Every trade is in the while loop. If a position exists
#that is still open at the end of the testing period, it is taken care of outside the while loop
#while Counter < 15:
while sum(abs(TradeSubset['Signal'])) != 0:
    TradeATR = TradeSubset['ATR'][0]
    numshares = (RiskPerTrade)/((TradeATR * 2))
    TradeDirection = TradeSubset['Signal'][0]
    #This column holds the type of exit that was taken
    TradeSubset['Exit'] = 0
    #Short exit, 1 = yes, 0 = no
    TradeSubset['ShortExit'] = 0
    #Long exit, 1 = yes, 0 = no
    TradeSubset['LongExit'] = 0
    #Did the exit gap overnight? or hit after open
    TradeSubset['GapShortExit'] = 0
    #Did the exit gap overnight? or hit after open
    TradeSubset['GapLongExit'] = 0
    #
    #
    if TradeDirection == 1:
    #1 = Long exit being hit starting the day of the signal.
        LongExitIndexList = list(TradeSubset['LongExit'].loc[(TradeSubset['Low'] < TradeSubset['HybridLongExitPrice'])].index)
        for l in LongExitIndexList:
            TradeSubset.set_value(l, 'LongExit', 1)
    #1 = Short exit being hit starting the day of the signal. 
    if TradeDirection == -1:
        ShortExitIndexList = list(TradeSubset['ShortExit'].loc[(TradeSubset['High'] > TradeSubset['HybridShortExitPrice'])].index)
        for s in ShortExitIndexList:
            TradeSubset.set_value(s, 'ShortExit', 1)
    
    #Assess Gaps on days where trade closes
    if TradeDirection == 1:
        GapLongExitIndexList = list(TradeSubset['GapLongExit'].loc[(TradeSubset['LongExit'] == 1) & (
                 TradeSubset['Open'] < TradeSubset['HybridLongExitPrice'])].index)
        for l in GapLongExitIndexList:
            TradeSubset.set_value(l, 'GapLongExit', 1)
                 
    if TradeDirection == -1:             
        GapShortExitIndexList = list(TradeSubset['GapShortExit'].loc[(TradeSubset['ShortExit'] == 1) & (
                TradeSubset['Open'] > TradeSubset['HybridShortExitPrice'])].index)
        for s in GapShortExitIndexList:
            TradeSubset.set_value(s, 'GapShortExit', 1)
    #Types of exit
    TradeSubset['Exit'].loc[(TradeSubset['ShortExit'] == 1)] = 1 #1 indicating short exit
    TradeSubset['Exit'].loc[(TradeSubset['LongExit'] == 1)] = 2 #1 indicating long exit 
    TradeSubset['Exit'].loc[(TradeSubset['GapShortExit'] == 1)] = 3 #1 indicating short exit w/ gap
    TradeSubset['Exit'].loc[(TradeSubset['GapLongExit'] == 1)] = 4 #1 indicating long exit w/ gap
    
    #List comprehension to find exit taken for subset.
    #The next function gives a position on the TradeSubset index
    ExitTaken = TradeSubset['Exit'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    if ExitTaken == 0:
        break
   #The length of the trade
    LengthOfTrade = int(next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0))
    #The SubIndex of the exit date is for continuing looking for rentry in new subset 
    IndexOfEntry = TradeSubset.index[0]
    IndexOfExit = TradeSubset.index[next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    SubIndexOfExit = TradeSubset['SubIndex'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    EntryPriceUnitOne = TradeSubset['EntryPriceUnitOne'][0]
    if TradeDirection == 1:
        StopPriceUnitOne = TradeSubset['HybridLongExitPrice'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    elif TradeDirection == -1:
        StopPriceUnitOne = TradeSubset['HybridShortExitPrice'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    OpenPriceOnGap = TradeSubset['Open'][LengthOfTrade]
    if ExitTaken == 1: # if exiting short trade, exit during market day
        TradePercentReturn = (EntryPriceUnitOne - StopPriceUnitOne)/EntryPriceUnitOne
        TradeDollarReturn = (EntryPriceUnitOne - StopPriceUnitOne) * numshares
    elif ExitTaken == 2: # if exiting long trade, exitduring market day 
        TradePercentReturn = (StopPriceUnitOne - EntryPriceUnitOne)/EntryPriceUnitOne
        TradeDollarReturn = (StopPriceUnitOne - EntryPriceUnitOne) * numshares
    elif ExitTaken == 3: # if exiting short trade with gap 
        TradePercentReturn = (EntryPriceUnitOne - OpenPriceOnGap)/EntryPriceUnitOne
        TradeDollarReturn = (EntryPriceUnitOne - OpenPriceOnGap) * numshares
    elif ExitTaken == 4: # if exiting long trade with gap 
        TradePercentReturn = (OpenPriceOnGap - EntryPriceUnitOne)/EntryPriceUnitOne
        TradeDollarReturn = (OpenPriceOnGap - EntryPriceUnitOne) * numshares
    RMultiple = TradeDollarReturn / RiskPerTrade
    Equity = Equity + TradeDollarReturn
    DollarRiskPerATR = Equity * .005
    #Log Trade details in Trade dataframe
    Empty.append(ExitTaken)
    Empty.append(numshares)
    Empty.append(LengthOfTrade)
    Empty.append(EntryPriceUnitOne)
    Empty.append(StopPriceUnitOne)
    Empty.append(IndexOfEntry)
    Empty.append(IndexOfExit)
    Empty.append(TradeDirection)
    Empty.append(OpenPriceOnGap)
    Empty.append(TradePercentReturn)
    Empty.append(TradeDollarReturn)
    Empty.append(RMultiple)
    Empty.append(SubIndexOfExit)
    Empty.append(TradeATR)
    Emptyseries = pd.Series(Empty)
    Trades[Counter] = Emptyseries.values
    Empty[:] = [] 
    print(Counter) 
    Counter = Counter + 1
    #This trimmer trims the Trade out of the TradeSubset, then trims to the next signal!
    TradeSubset = TradeSubset[(LengthOfTrade + 1):]
    SignalTrim = next((n for n, x in enumerate(TradeSubset['Signal']) if x), 0)
    TradeSubset = TradeSubset[SignalTrim:]
#    
##If there is a trade that is still open
if sum(abs(TradeSubset['Signal'])) != 0:
    ExitTaken = 0
    numshares = (RiskPerTrade)/((TradeATR) * 2)
    LengthOfTrade = len(TradeSubset)
    EntryPriceUnitOne = TradeSubset['EntryPriceUnitOne'][0]
    if TradeDirection == 1:
        StopPriceUnitOne = TradeSubset['HybridLongExitPrice'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    elif TradeDirection == -1:
        StopPriceUnitOne = TradeSubset['HybridShortExitPrice'][next((n for n, x in enumerate(TradeSubset['Exit']) if x), 0)]
    IndexOfEntry = TradeSubset.index[0]
    IndexOfExit = TradeSubset.index[-1]
    SubIndexOfExit = TradeSubset['SubIndex'][-1]
    TradeDirection = TradeSubset['Signal'][0]
    OpenPriceOnGap = np.nan
    if TradeDirection == 1:
        TradePercentReturn = (TradeSubset['Adj Close'][-1] - EntryPriceUnitOne)/EntryPriceUnitOne
        TradeDollarReturn = (TradeSubset['Adj Close'][-1] - EntryPriceUnitOne) * numshares
    elif TradeDirection == -1:
        TradePercentReturn = (EntryPriceUnitOne - TradeSubset['Adj Close'][-1])/EntryPriceUnitOne
        TradeDollarReturn = (EntryPriceUnitOne - TradeSubset['Adj Close'][-1]) * numshares
    RMultiple = TradeDollarReturn / RiskPerTrade
#    Equity = Equity + TradeDollarReturn
#    Log Trade details in Trade dataframe
    Empty.append(ExitTaken)
    Empty.append(numshares)
    Empty.append(LengthOfTrade)
    Empty.append(EntryPriceUnitOne)
    Empty.append(StopPriceUnitOne)
    Empty.append(IndexOfEntry)
    Empty.append(IndexOfExit)
    Empty.append(TradeDirection)
    Empty.append(OpenPriceOnGap)
    Empty.append(TradePercentReturn)
    Empty.append(TradeDollarReturn)
    Empty.append(RMultiple)
    Empty.append(SubIndexOfExit)
    Empty.append(TradeATR)
    Emptyseries = pd.Series(Empty)
    Trades[Counter] = Emptyseries.values
    Empty[:] = [] 
    Counter = Counter + 1
    print(Counter)
    print('The last trade in this time series is still open.')

Trades = Trades.rename(index={0: "ExitTaken", 1: "NumberOfShares", 2: "LengthOfTrade",
    3: "EntryPriceUnitOne", 4: "StopPriceUnitOne", 5: "IndexOfEntry", 6: "IndexOfExit",
    7: "TradeDirection", 8: "OpenPriceOnGap", 9: "TradePercentReturn",
    10: "TradeDollarReturn", 11: "RMultiple", 12:"SubIndexOfExit", 13:"TradeATR"})
Asset1['StrategyReturns'] = 1   

#The next two lines are the only reason keep track of 'SubIndexOfExit'
#I need help indexing properly
for d in Trades:
    Asset1['StrategyReturns'].loc[(Asset1['SubIndex'] == Trades[d]['SubIndexOfExit'])] = 1 + Trades[d]['TradePercentReturn']
    
#System statistics for time series 
NumWinningTrades = len(Asset1['StrategyReturns'][Asset1['StrategyReturns'] > 1])
NumLosingTrades = len(Asset1['StrategyReturns'][Asset1['StrategyReturns'] < 1])
AvgWin = Asset1['StrategyReturns'][Asset1['StrategyReturns'] > 1].mean()
AvgLoss = Asset1['StrategyReturns'][Asset1['StrategyReturns'] < 1].mean()
RewardRisk = AvgWin/AvgLoss
WinRate = NumWinningTrades / (NumWinningTrades + NumLosingTrades)
LossRate = NumLosingTrades / (NumWinningTrades + NumLosingTrades)
Expectancy = (WinRate * RewardRisk) - (LossRate)
RMultiples = pd.DataFrame(data = Trades.loc['RMultiple',:])
Asset1['Multiplier'] = Asset1['StrategyReturns'].cumprod()

#This is supposed to be a graph of the equity curve from trade exits
Asset1['Multiplier'].plot()
print(sum(Asset1['DoubleDay']), ' Double signal days exist')
print('The expectancy of the system is ', Expectancy)
print(RMultiples)
##Need to make histogram
#plt.hist(RMultiples['RMultiple'], normed=True, bins=10
#plt.ylabel('RMultiple')
#plt.show()
AssetCopy = Asset[['Date', 'Open', 'High', 'Low','Close']].copy()
AssetCopy['Date'] = AssetCopy.index
AssetCopy['Date'] = AssetCopy['Date'].apply(mdates.date2num)
fig1, axe = plt.subplots(figsize = (10,5))
candlestick_ohlc(axe, AssetCopy.values, width=.6, colorup='green', colordown='red')
axe.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
#Overlay
axe.plot(AssetCopy['IndexToNumber'], Asset['RollingMax'], color = 'green', label = 'RollingMax')
axe.plot(AssetCopy['IndexToNumber'], Asset['RollingMin'], color = 'red', label = 'RollingMin')
#axe.plot(Asset['IndexToNumber'], Asset['SMA'], color = 'black', label = 'SMA')

#Signal triangles..
axe.scatter(Asset1.loc[Asset1['OriginalTrade'] == 1, 'IndexToNumber'].values, 
            Asset1.loc[Asset1['OriginalTrade'] == 1, 'Adj Close'].values, label='skitscat', color='green', s=75, marker="^")
axe.scatter(Asset1.loc[Asset1['OriginalTrade'] == -1, 'IndexToNumber'].values, 
            Asset1.loc[Asset1['OriginalTrade'] == -1, 'Adj Close'].values, label='skitscat', color='red', s=75, marker="v")
