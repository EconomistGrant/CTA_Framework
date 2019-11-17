import pandas as pd
import numpy as np

IC = pd.read_csv('C:/Users/account/Desktop/BackTest/ICtable_new.csv', index_col = 0)
IH = pd.read_csv('C:/Users/account/Desktop/BackTest/IHtable_new.csv', index_col = 0)

Contract = pd.merge(IC, IH, how = 'inner', on = 'tradedate', suffixes = ('_IC', '_IH'))
Contract.to_csv('C:/Users/account/Desktop/BackTest/contract.csv')