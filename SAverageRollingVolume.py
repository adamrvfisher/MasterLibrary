# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 13:31:53 2017

@author: AmatVictoriaCuramIII
"""

#This is a summary statistic + database query tool

def SAverageRollingVolume(s):
    s['AverageRollingVolume'] = s['Volume'].rolling(center=False, 
                                                        window=252).mean()
    return s['AverageRollingVolume'].tail(1)
