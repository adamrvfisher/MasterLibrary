# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 12:50:29 2020

@author: AmatVictoriaCuramIII
"""

#Import modules
from time import strftime
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message
import pandas as pd
import numpy as np
#import time
#import math 

#Variable assignment

#RangeID = range(1,33)
#RangeArray = np.array(RangeID)
#UniverseCSVList = pd.read_pickle('F:\\Users\\AmatVictoriaCuram\\FDL\\'+
#                      'DataSources\\NASDAQSource\\UniverseLists\\Universe2018')
#UniverseList =  [s[:-4] for s in UniverseCSVList]
#UniverseList = UniverseList[:35]
#TotalConnections = len(UniverseList)
#NumTiles = math.ceil(TotalConnections/32)
#ConnectionIDs = np.tile(RangeArray, NumTiles)
#ConnectionIDs = ConnectionIDs[:len(UniverseList)]
#for t in (UniverseList):
def nextValidId_handler(msg):
    print(msg)
    inner()

hist = []
ticker = str()


def my_hist_data_handler(msg):
    print(msg)
    if "finished" in msg.date:
        print('disconnecting', con.disconnect())
        df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('Date', 'Open', 'High', 'Low', 'Close'))
        for index, msg in enumerate(hist):
            df.loc[index,'Date':'Close'] = msg.date, msg.open, msg.high, msg.low, msg.close
        #Set index to Date
        df = df.set_index('Date')
        #Format datetime index
        df.index = pd.to_datetime(df.index, unit = 's')
        #Convert float to float64
        for i in df.columns:
            df[i] =  pd.to_numeric(df[i], errors='coerce')
        #Save to pickle
        pd.to_pickle(df, "F:\\Users\\AmatVictoriaCuram\\FDL\\DataSources\\IBSource\\DataName")
        print(df)
    else:
        hist.append(msg)    

def error_handler(msg):
    print(msg)

if __name__ == '__main__':

    con = ibConnection(port=7497,clientId=3)
    con.register(error_handler, message.Error)
    con.register(nextValidId_handler, message.nextValidId)
    con.register(my_hist_data_handler, message.historicalData)
    con.connect()

    print(con.isConnected())

    def inner():

        CntrctObj = Contract()
        CntrctObj.m_secType = "FUT" 
        CntrctObj.m_symbol = "ES"
        globals()[ticker] = CntrctObj.m_symbol         
        CntrctObj.m_currency = "USD"
        CntrctObj.m_exchange = "GLOBEX"
        CntrctObj.m_localSymbol = "ESH0"
        endtime = strftime('%Y%m%d %H:%M:%S')
        print(endtime)
        con.reqHistoricalData(1, CntrctObj, endtime, "1 Y", "1 hour", "MIDPOINT", 1, 2)

    print(con.isConnected())
#time.sleep(.5)
        