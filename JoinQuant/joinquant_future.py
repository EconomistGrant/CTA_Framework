import pandas as pd
import numpy as np
from datetime import timedelta
import os
from jqdatasdk import *
auth('13097089601', 'LSH19971019')
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

main = os.path.abspath(os.path.dirname(os.getcwd()))
#从JoinQuant上抓取指数期货价格数据
contract = pd.read_csv('{}/contract.csv'.format(main), index_col = 0)
contract['tradedate'] = pd.to_datetime(contract['tradedate'])

for x in contract.index:
	if x < 2:
		pass
	if x > 2:
		contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'].rstrip()
		contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'] + '.CCFX'
		contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'].rstrip()
		contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'] + '.CCFX'
		tradedate = contract.tradedate[x]
		tradedate = pd.to_datetime(tradedate)
		print(tradedate)
		pre = contract.tradedate[x - 1]
		pre2 = contract.tradedate[x - 2]
		contract.loc[x, 'ICprice'] = get_price(security = contract.instrumentID_IC[x], count= 1, end_date = tradedate, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'IHprice'] = get_price(security = contract.instrumentID_IH[x], count= 1, end_date = tradedate, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'ICpreclose'] = get_price(security = contract.instrumentID_IC[x], count= 1, end_date = pre, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'IHpreclose'] = get_price(security = contract.instrumentID_IH[x], count= 1, end_date = pre, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'ICpre2close'] = get_price(security = contract.instrumentID_IC[x], count= 1, end_date = pre2, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'IHpre2close'] = get_price(security = contract.instrumentID_IH[x], count= 1, end_date = pre2, fields = ['close'], frequency = 'daily').close[0]
		contract.loc[x, 'ICreturn'] = contract.loc[x, 'ICprice'] / contract.loc[x, 'ICpreclose'] - 1
		contract.loc[x, 'IHreturn'] = contract.loc[x, 'IHprice'] / contract.loc[x, 'IHpreclose'] - 1 
		contract.loc[x, 'ICpreret'] = contract.loc[x, 'ICpreclose'] / contract.loc[x, 'ICpre2close'] - 1
		contract.loc[x, 'IHpreret'] = contract.loc[x, 'IHpreclose'] / contract.loc[x, 'IHpre2close'] - 1

contract['ICmIH'] = contract['ICreturn'] - contract['IHreturn']
contract['dret'] = contract['ICpreret'] - contract['IHpreret']

contract.to_csv('{}/JoinQuant/futures.csv'.format(main))
'''
contract = pd.read_csv('C:/Users/account/Desktop/BackTest/JoinQuant/futures.csv')

def test_factor(data, factor = 'dret', direction = 1):
	#get signal
	data['signal'] = np.zeros(len(data))
	data['cum'] =  np.ones(len(data))
	data['fee'] = np.zeros(len(data))
	data['fee_cum'] = np.ones(len(data))
	data['tradedate'] = pd.to_datetime(data['tradedate'])
	data = data.dropna(how = 'any').reset_index(drop = True)

	for x in data.index:
		if (data.loc[x, factor] * direction) >= 0:
			data.loc[x, 'signal'] = 1
		elif (data.loc[x, factor] * direction) < -0:
			data.loc[x, 'signal'] = -1
		data.loc[x, 'ret'] = data.loc[x, 'signal'] * data.loc[x, 'ICmIH']
	#get cumulated value
	temp = data.signal[0]
	cumtemp = 1
	feecumtemp = 1
	for x in data.index:
		if data.loc[x, 'signal'] == temp:
			data.loc[x, 'fee'] = 0
		else:
			data.loc[x, 'fee'] = 0.0002 *abs(data.loc[x, 'signal'] - temp)
		data.loc[x, 'fee_ret'] = data.loc[x,'ret'] - data.loc[x, 'fee']
		
		if x == 0:
			pass
		else:
			data.loc[x, 'cum'] = (data.ret[x] + 1) * cumtemp
			data.loc[x, 'fee_cum'] = (data.loc[x, 'fee_ret'] +1) * feecumtemp

		cumtemp = data.loc[x, 'cum']
		feecumtemp = data.loc[x, 'fee_cum']
		temp = data.loc[x, 'signal']
	return data

test = test_factor(data = contract, factor = 'dret', direction = 1)
print(test.cum.head())
print(test.cum.tail())
'''