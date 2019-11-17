#研究前日收盘集合竞价的成交金额，生成第二天的交易信号
#查看目录下的test.csv是生成的信号、交易、收益统计文件
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from jqdatasdk import *
import os
'''
#获取last_money.csv文件
#因为已经获取所以注释掉了
auth('13097089601', 'LSH19971019')

index = pd.read_csv('C:/Users/account/Desktop/BackTest/JoinQuant/ICIHindex.csv', index_col = 0)
index['tradedate'] = pd.to_datetime(index['tradedate'])

for x in index.index:
	tradetime = index.loc[x, 'tradedate'] - timedelta(days = 1) + timedelta(hours = 15)
	print(tradetime)
	ICtemp = get_price('000905.XSHG', count = 2, end_date = tradetime, frequency = '1m')
	ICmoney = ICtemp.money[1]
	ICret = ICtemp.close[1] / ICtemp.close[0] - 1
	index.loc[x, 'ICpre_last_money'] = ICmoney
	index.loc[x, 'ICpre_last_ret'] = ICret

	IHtemp = get_price('000016.XSHG', count = 2, end_date = tradetime, frequency = '1m')
	IHmoney = IHtemp.money[1]
	IHret = IHtemp.close[1] / IHtemp.close[0] - 1
	index.loc[x, 'IHpre_last_money'] = IHmoney
	index.loc[x, 'IHpre_last_ret'] = IHret

index['tradedate'] = pd.to_datetime(index['tradedate'])

index['IClastmean'] = index['ICpre_last_money'].rolling(30).mean().shift(1)
index['IClaststd'] = index['ICpre_last_money'].rolling(30).std().shift(1)
index['IHlastmean'] = index['IHpre_last_money'].rolling(30).mean().shift(1)
index['IHlaststd'] = index['IHpre_last_money'].rolling(30).std().shift(1)

index.to_csv('C:/Users/account/Desktop/BackTest/last_vol/last_money.csv')
'''
main = os.path.abspath(os.path.dirname(os.getcwd()))
print(main)
#也可以读取last_vol文件
index = pd.read_csv('last_money.csv', index_col = 0)
index = index.dropna(how = 'any').reset_index(drop = True)
index['IClast_stdzd'] = (index['ICpre_last_money'] - index['IClastmean']) / index['IClaststd']
index['IHlast_stdzd'] = (index['IHpre_last_money'] - index['IHlastmean']) / index['IHlaststd']
index['dlast_stdzd'] = index['IClast_stdzd'] - index['IHlast_stdzd'] 
index['IHratio'] = index['IHpre_last_money'] / index['IHlastmean']

future = pd.read_csv('{}/JoinQuant/futures.csv'.format(main), index_col = 0)
merge = pd.merge(index, future, how = 'inner', on = 'tradedate', suffixes = ('_i', '_f'))
merge = merge.dropna(how = 'any').reset_index(drop = True)


merge['signal'] = np.zeros(len(merge))
num_of_signals = 0

#IH相对于过去30天的rolling mean翻倍太大则判定为“事件”
#选取倍数为2，3，4结果都不太好
for x in merge.index:
	if merge.loc[x, 'IHratio'] > 3:
		if merge.loc[x, 'ICpre_last_ret'] > merge.loc[x, 'IHpre_last_ret']:
			merge.loc[x, 'signal'] = 1
			num_of_signals += 1
		elif merge.loc[x, 'ICpre_last_ret'] < merge.loc[x, 'IHpre_last_ret']:
			merge.loc[x, 'signal'] = -1
			num_of_signals += 1
	else:
		pass

#标准化成交额 超过阈值 IC IH做差 生成信号
'''
for x in merge.index:
	if abs(merge.loc[x, 'dlast_stdzd']) > 2:
		if merge.loc[x, 'ICpre_last_ret'] > merge.loc[x, 'IHpre_last_ret']:
			merge.loc[x, 'signal'] = 1
			num_of_signals += 1
		elif merge.loc[x, 'ICpre_last_ret'] < merge.loc[x, 'IHpre_last_ret']:
			merge.loc[x, 'signal'] = -1
			num_of_signals += 1
	else:
		pass


#价格变化*标准化交易量 IC IH做差 生成信号
for x in merge.index:
	a = merge.loc[x, 'ICpre_last_ret'] * merge.loc[x, 'ICpre_last_vol'] - merge.loc[x, 'IHpre_last_ret'] * merge.loc[x, 'IHpre_last_vol']
	if a > 0:
		merge.loc[x, 'signal'] = 1
	if a < 0:
		merge.loc[x, 'signal'] = -1

'''

merge['ret'] = merge['signal'] * merge['ICmIH_f']

print(num_of_signals)
merge = merge.loc[merge["signal"]!= 0]
print(merge.columns)
merge = merge[['tradedate', 'ICreturn', 'IHreturn', 'ICmIH_f', 'IHpre_last_money', 'IHlastmean', 'IHratio','ICpre_last_ret', 'IHpre_last_ret', 'signal','ret']]
print(merge)
merge.to_csv('test.csv')

def test_factor(data):
	data['cum'] =  np.ones(len(data))
	data['tradedate'] = pd.to_datetime(data['tradedate'])
	data = data.dropna(how = 'any').reset_index(drop = True)
	#get cumulated value
	temp = data.signal[0]
	cumtemp = 1
	feecumtemp = 1
	for x in data.index:
		if x == 0:
			pass
		else:
			data.loc[x, 'cum'] = (data.ret[x] + 1) * cumtemp
		cumtemp = data.loc[x, 'cum']
	return data

data = test_factor(data = merge)
print(data.cum.tail())
from winrate import test
test(data = data)

plt.plot(data.tradedate, data.cum)
plt.xticks(rotation  = 45)
plt.show()
