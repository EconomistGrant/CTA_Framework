import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from datetime import timedelta
from jqdatasdk import *
auth('13097089601', 'LSH19971019')
import os

main = os.path.abspath(os.path.dirname(os.getcwd()))
contract = pd.read_csv('{}/Contract.csv'.format(main), index_col = 0)
contract.tradedate = pd.to_datetime(contract.tradedate)

for x in contract.index:
	contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'].rstrip()
	contract.loc[x, 'instrumentID_IC'] = contract.loc[x, 'instrumentID_IC'] + '.CCFX'
	contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'].rstrip()
	contract.loc[x, 'instrumentID_IH'] = contract.loc[x, 'instrumentID_IH'] + '.CCFX'
###
###前一天最后x分钟基差的变化
###

for x in contract.index:
	if x == 0:
		pass
	else:
		tradedate = contract.loc[x, 'tradedate']
		print(tradedate)
		predate = contract.loc[x - 1, 'tradedate'] + timedelta(hours = 15)
		ICpreclose_f = get_price(contract.loc[x, 'instrumentID_IC'], count = 1, end_date = predate, frequency = 'daily').close[0]
		ICpreclose_i = get_price('000905.XSHG', count = 1, end_date = predate, frequency = 'daily').close[0]
		ICpreclose_b = ICpreclose_i - ICpreclose_f

		ICpremins_f = get_price(contract.loc[x, 'instrumentID_IC'], count = 2, end_date = predate, frequency = '60m').close[0]
		ICpremins_i = get_price('000905.XSHG', count = 2, end_date = predate, frequency = '60m').close[0]
		ICpremins_b = ICpremins_i - ICpremins_f

		dIC_b = ICpreclose_b - ICpremins_b

		IHpreclose_f = get_price(contract.loc[x, 'instrumentID_IH'], count = 1, end_date = predate, frequency = 'daily').close[0]
		IHpreclose_i = get_price('000016.XSHG', count = 1, end_date = predate, frequency = 'daily').close[0]
		IHpreclose_b = IHpreclose_i - IHpreclose_f

		IHpremins_f = get_price(contract.loc[x, 'instrumentID_IH'], count = 2, end_date = predate, frequency = '60m').close[0]
		IHpremins_i = get_price('000016.XSHG', count = 2, end_date = predate, frequency = '60m').close[0]
		IHpremins_b = IHpremins_i - IHpremins_f

		dIH_b = IHpreclose_b - IHpremins_b

		dbasis = dIC_b - dIH_b

		contract.loc[x, 'dbasis_premins'] = dbasis

future = pd.read_csv('{}/JoinQuant/futures.csv'.format(main), index_col = 0)
future = future[['tradedate','ICmIH']]
future['tradedate'] = pd.to_datetime(future['tradedate'])
contract['tradedate'] = pd.to_datetime(future['tradedate'])
Basis = pd.merge(contract, future, how = 'inner', on = 'tradedate')
Basis = Basis.dropna(how = 'any').reset_index(drop = True)

def test_factor (factor = 'dbasis_premins', direction = 1):
	Basis['cum'] = np.ones(len(Basis))
	Basis['ret'] = np.zeros(len(Basis))
	Basis['signal'] = np.zeros(len(Basis))
	for x in range(len(Basis.index)):
		if (Basis.loc[x, factor] * direction) >= 0:
			Basis.loc[x, 'signal'] = 1
		elif (Basis.loc[x, factor] * direction) < -0:
			Basis.loc[x, 'signal'] = -1
	Basis['ret'] = Basis['signal'] * Basis['ICmIH']
	for x in range(len(Basis.index)):
		if x == 0:
			pass
		else:
			Basis.loc[x, 'cum'] = (Basis.loc[x-1, 'cum'] * (Basis.loc[x, 'ret'] +1))
	print(Basis.cum.tail())
	return Basis

dbasis = test_factor()

Basis.to_csv('{}/basis/dbasis_pre60mins_test.csv'.format(main))
'''
dbasis = pd.read_csv('C:/Users/account/Desktop/BackTest/basis/dbasis_pre60mins.csv')
dbasis['tradedate'] = pd.to_datetime(dbasis['tradedate'])

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

from winrate import test
draw(dbasis.cum)
test(dbasis)
print(dbasis.cum.tail)
plt.plot(dbasis.tradedate, dbasis.cum)
plt.xticks(rotation = 45)
plt.grid()
plt.show()

