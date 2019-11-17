import pandas as pd
import numpy as np
from datetime import timedelta
import os
from jqdatasdk import *
auth('13097089601', 'LSH19971019')
import matplotlib.pyplot as plt


main = os.path.abspath(os.path.dirname(os.getcwd()))
contract = pd.read_csv('{}/Contract.csv'.format(main), index_col = 0)
contract['tradedate'] = pd.to_datetime(contract['tradedate'])

for x in contract.index:
	contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'].rstrip()
	contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'] + '.CCFX'
	contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'].rstrip()
	contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'] + '.CCFX'

for x in contract.index:
	tradedate = contract.loc[x, 'tradedate']

	#start和end是计算信号的窗口
	start = tradedate + timedelta(hours = 9) + timedelta(minutes = 30) 
	end = start + timedelta (minutes = 5)
	#temp用来计算信号 close和start用来计算期货收益
	tempIC = get_price(contract.loc[x, 'instrumentID_IC'], count = 1, end_date = end , frequency = '5m',fields = ['open','close'])
	closeIC = get_price(contract.loc[x, 'instrumentID_IC'], count = 1, end_date = tradedate , frequency = 'daily').close[0]	
	startIC = get_price(contract.loc[x, 'instrumentID_IC'], count = 1, end_date = end , frequency = '5m').close[0]

	tempIH = get_price(contract.loc[x, 'instrumentID_IH'], count = 1, end_date = end , frequency = '5m',fields = ['open','close'])
	closeIH = get_price(contract.loc[x, 'instrumentID_IH'], count = 1, end_date = tradedate , frequency = 'daily').close[0]	
	startIH = get_price(contract.loc[x, 'instrumentID_IH'], count = 1, end_date = end , frequency = '5m').close[0]

	contract.loc[x, 'ICopen'] = tempIC.open[0]
	contract.loc[x, 'ICopen2'] = tempIC.close[0]
	contract.loc[x, 'ICopen_ret'] = tempIC.close[0] / tempIC.open[0] - 1

	contract.loc[x, 'ICclose'] = closeIC
	contract.loc[x, 'IC_rest_of_the_day'] = closeIC / startIC - 1

	contract.loc[x, 'IHopen'] = tempIH.open[0]
	contract.loc[x, 'IHopen2'] = tempIH.close[0]
	contract.loc[x, 'IHopen_ret'] = tempIH.close[0] / tempIH.open[0] - 1
	contract.loc[x, 'IHclose'] = closeIH
	contract.loc[x, 'IH_rest_of_the_day'] = closeIH / startIH - 1

	contract.loc[x, 'dopen'] = contract.loc[x, 'ICopen_ret'] - contract.loc[x, 'IHopen_ret']
	if contract.loc[x,'dopen'] > 0:
		contract.loc[x, 'signal'] = 1
	else:
		contract.loc[x, 'signal'] = -1

contract['drest'] = contract['IC_rest_of_the_day'] - contract['IH_rest_of_the_day']
contract['ret'] = contract['signal'] * contract['drest']
contract['fee_ret'] = contract['ret'] - 0.0004
from winrate import test

test(contract)

def get_cum(data, factor = 'dret', direction = 1):
	#get signal
	data['cum'] =  np.ones(len(data))
	data['fee_cum'] = np.ones(len(data))
	data['tradedate'] = pd.to_datetime(data['tradedate'])
	data = data.dropna(how = 'any').reset_index(drop = True)

	temp = data.signal[0]
	cumtemp = 1
	feecumtemp = 1

	for x in data.index:
		if x == 0:
			pass
		else:
			data.loc[x, 'cum'] = (data.ret[x] + 1) * cumtemp
			data.loc[x, 'fee_cum'] = (data.loc[x, 'fee_ret'] +1) * feecumtemp

		cumtemp = data.loc[x, 'cum']
		feecumtemp = data.loc[x, 'fee_cum']
		temp = data.loc[x, 'signal']


	plt.plot(data.tradedate, data.cum)
	plt.xticks(rotation = 45)
	plt.show()
	return data

data = get_cum(contract, 'dopen', 1)
data.to_csv('{}/first_mins/5min-future-future.csv'.format(main))

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
draw(data.cum)
draw(data.fee_cum)

plt.plot(data.tradedate, data.cum, label = 'no_fee')
plt.plot(data.tradedate, data.fee_cum, label = 'after_fee')
plt.xticks(rotation = 45)
plt.grid()
plt.legend(loc="upper left")
plt.show()