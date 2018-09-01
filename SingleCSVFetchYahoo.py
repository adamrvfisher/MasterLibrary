# -*- coding: utf-8 -*-
"""
Created on Thu May 18 15:55:54 2017

@author: AmatVictoriaCuramIII
"""
import webbrowser as web
import requests
from io import StringIO
import pandas as pd
import time as t
starttime = t.time()
ticker = "CXW"
artificialcrumb = "1.ZWRp1I9ZS"
downloadurl = ("https://query1.finance.yahoo.com/v7/finance/download/" + ticker 
+ "?period1=-631123200&period2=1598374000&interval=1d&events=history&crumb=" + artificialcrumb)
response = requests.post(downloadurl)#, data=CookieDict)
datastr = response.text
formatter = StringIO(datastr)
df = pd.read_csv(formatter, sep = ',')
df = df.set_index('Date')
df.index = pd.to_datetime(df.index, format = "%Y/%m/%d") 
endtime = t.time()
duration = endtime - starttime 

# you may now write to file

df.to_csv(("F:\\Users\\AmatVictoriaCuram\\TemporaryCSV\\"+ ticker + ".csv"))