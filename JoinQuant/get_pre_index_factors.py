import pandas as pd
import numpy as np
from datetime import timedelta
import os
from jqdatasdk import *
auth('13097089601', 'LSH19971019')
#获取指数信号，前一交易日的信号，前一天日末建仓，收益算的是今天的

main = os.path.abspath(os.path.dirname(os.getcwd()))
Contract = pd.read_csv('{}/contract.csv'.format(main), index_col = 0)
Contract['tradedate'] = pd.to_datetime(Contract['tradedate'])

if os.path.exists('pre_factors.csv'):
	factors = pd.read_csv('pre_factors.csv', index_col = 0)
	factors['tradedate'] = pd.to_datetime(factors['tradedate'])
else:
	for x in Contract.index:
		if x == 0:
			pass
		else:
			# tradedate：模拟交易的日子 
			# x-1: 第x个交易日，遵循的信号日
			print(Contract.loc[x,'tradedate'])
			pretradedate = Contract.loc[x - 1,'tradedate'] + timedelta(hours = 15)
			tempIC = get_price('000905.XSHG', count = 1, end_date = pretradedate , frequency = 'daily', fields = ['close', 'pre_close', 'high', 'low'])
			tempIC30 = get_price('000905.XSHG', count = 2, end_date = pretradedate , frequency = '30m').close
			retIC30 = tempIC30[-1] / tempIC30[0] -1

			preretIC = tempIC.close[0] / tempIC.pre_close[0] - 1
			prehighIC = tempIC.high[0] / tempIC.close[0] - 1
			prelowIC = tempIC.low[0] / tempIC.close[0] - 1
			Contract.loc[x, 'preret_IC'] = preretIC		
			Contract.loc[x, 'prehigh_IC'] = prehighIC
			Contract.loc[x, 'prelow_IC'] = prelowIC
			Contract.loc[x, 'pre_30min_IC'] = retIC30

			tempIH = get_price('000016.XSHG', count = 1, end_date = pretradedate , frequency = 'daily', fields = ['close', 'pre_close', 'high', 'low'])
			tempIH30 = get_price('000016.XSHG', count = 2, end_date = pretradedate , frequency = '30m').close
			retIH30 = tempIH30[-1] / tempIH30[0] -1

			preretIH = tempIH.close[0] / tempIH.pre_close[0] - 1
			prehighIH = tempIH.high[0] / tempIH.close[0] - 1
			prelowIH = tempIH.low[0] / tempIH.close[0] - 1
			Contract.loc[x, 'preret_IH'] = preretIH		
			Contract.loc[x, 'prehigh_IH'] = prehighIH
			Contract.loc[x, 'prelow_IH'] = prelowIH
			Contract.loc[x, 'pre_30min_IH'] = retIH30

			Contract.loc[x, 'dpreret'] = preretIC - preretIH
			Contract.loc[x, 'dprehigh'] = prehighIC - prehighIH
			Contract.loc[x, 'dprelow'] = prelowIC - prelowIH
			Contract.loc[x, 'dpre30'] = retIC30 - retIH30

	Contract.to_csv('C:/Users/account/Desktop/BackTest/JoinQuant/pre_factors.csv')
	factors = Contract

future = pd.read_csv('C:/Users/account/Desktop/BackTest/JoinQuant/futures.csv')
future = future[['tradedate','ICmIH']]

future.tradedate = pd.to_datetime(future.tradedate)
merge = pd.merge(future, factors, how = 'inner', on = 'tradedate').dropna(how = 'any').reset_index(drop = True)
merge['signal'] = np.zeros(len(merge))
merge['cum'] = 1
merge['fee_cum'] = 1

def test_factor(data = merge, factor = 'dpreret', direction = 1):
	#get signal
	for x in data.index:
		if (data.loc[x, factor] * direction) > 0:
			data.loc[x, 'signal'] = 1
		elif (data.loc[x, factor] * direction) < 0:
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


#dret, dprehigh, dprelow
t = test_factor(factor = 'dpreret', direction = 1)

print(t[['tradedate','cum']].tail())

def draw (data):
    drawback_list = []
    for i,x in enumerate(data):
        temp = []
        for j,y in enumerate(data):
            if j < i:
                pass
            else:
                temp.append((y-x)/x)
        x_drawback = min(temp)
        drawback_list.append(x_drawback)
    drawback = min(drawback_list)
    print('最大回撤为{}'.format(drawback))
draw(t.cum)
from winrate import test
test(t)
t.to_csv('C:/Users/account/Desktop/BackTest/JoinQuant/dpreret.csv')

import matplotlib.pyplot as plt
plt.plot(t.tradedate, t.cum)
plt.grid()
plt.show()
