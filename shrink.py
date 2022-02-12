import pandas as pd
data1 = pd.read_csv('./pickUp.csv').sample(20000)
data1.to_csv('./pickUpSmall.csv')
data2 = pd.read_csv('./dropOff.csv').sample(20000)
data2.to_csv('./dropOffSmall.csv')