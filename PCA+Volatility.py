# -*- coding: utf-8 -*-
"""

@author: Adam Reinhold Von Fisher - https://www.linkedin.com/in/adamrvfisher/

"""

#This is a PCA model for volatility analysis, need to add a trading model behind it.
#PCA draft for ROC to fwd returns PCA

#Import modules
import numpy as np
from sklearn.decomposition import PCA 
import matplotlib.pyplot as plt
from YahooSourceDailyGrabber import YahooSourceDailyGrabber

#Make data structure 
Asset = YahooSourceDailyGrabber('UVXY')
#Sample sizing..
AssetCopy = Asset[['Adj Close', '4wkRateOfChange']][-1000:]
#FWD returns
AssetCopy['12wkFWDRateOfChange'] = (Asset['Adj Close'].shift(-60
                        ) - Asset['Adj Close']) / Asset['Adj Close']  
#Trim undiscovered FWD returns..
AssetCopy = AssetCopy[:-60]
#Calculate sample size
SampleSize = len(AssetCopy)
#Indicators
NwkROC = np.array(AssetCopy['4wkRateOfChange'])
NwkFWDROC = np.array(AssetCopy['12wkFWDRateOfChange'])

ComponentsObject = np.column_stack([NwkROC, NwkFWDROC])
#PCA with scikit-learn 
PCAObject = PCA(n_components = ComponentsObject.shape[1]) 
PCAObject.fit(ComponentsObject) 
print(PCAObject.explained_variance_ratio_)
#Object transformation
PCTransform = PCAObject.transform(ComponentsObject)

#Graphical display params
plt.subplot(121) 
plt.scatter(ComponentsObject[:, 0], ComponentsObject[:, 1]) 
plt.xlabel("4 wk ROC"); plt.ylabel("12 wk FWD ROC")

plt.subplot(122) 
plt.scatter(PCTransform[:, 0], PCTransform[:, 1]) 
plt.xlabel("PC1 (var=%.2f)" % PCAObject.explained_variance_ratio_[0]) 
plt.ylabel("PC2 (var=%.2f)" % PCAObject.explained_variance_ratio_[1]) 
plt.axis('equal') 
plt.tight_layout()
