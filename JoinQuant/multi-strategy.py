import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import os

main = os.path.abspath(os.path.dirname(os.getcwd()))
pre = pd.read_csv('{}/JoinQuant/pre_3_signals.csv'.format(main),index_col = 0)
first = pd.read_csv('{}/first_mins/5min-future-future-new.csv'.format(main), index_col = 0)
basis = pd.read_csv('{}/basis/dbasis_pre60mins.csv'.format(main), index_col = 0)

#临时计算basis的手续费后累积净值
basis['fee_cum'] = np.ones(len(basis))
basis['fee'] = np.zeros(len(basis))
signal_temp = 0
for x in basis.index:
	if basis.loc[x, 'signal'] == signal_temp:
		pass
	else:
		basis.loc[x, 'fee'] = 0.0002 * (basis.loc[x, 'signal'] - signal_temp)
	basis.loc[x, 'fee_ret'] = basis.loc[x, 'ret'] - basis.loc[x, 'fee']
	signal_temp = basis.loc[x, 'signal']

feecumtemp = 1

for x in basis.index:
	if x == 0:
		pass
	else:
		basis.loc[x, 'fee_cum'] = (basis.loc[x, 'fee_ret'] +1) * feecumtemp
	feecumtemp = basis.loc[x, 'fee_cum']


merge = pd.merge(basis, first, how = 'inner', on ='tradedate', suffixes = ('_k', '_l'))

#分配比例
#first为当日开盘五分钟趋势跟随，回撤较大但是长期收益较好
#pre为前一天三个因子的综合策略，回撤较小但是长期收益较小
k = 0.7
merge['ret'] = k * merge['ret_k'] + (1-k) * merge['ret_l']
merge['fee_ret'] = k * merge['fee_ret_k'] + (1-k) *merge['fee_ret_l']
merge['cum'] = np.ones(len(merge))
merge['fee_cum'] = np.ones(len(merge))
cumtemp = 1
feecumtemp = 1
for x in merge.index:
	if x == 0:
		pass
	else:
		merge.loc[x, 'cum'] = (merge.ret[x] + 1) * cumtemp
		merge.loc[x, 'fee_cum'] = (merge.fee_ret[x] + 1) * feecumtemp
	cumtemp = merge.loc[x, 'cum']
	feecumtemp = merge.loc[x, 'fee_cum']

print(merge.tail())

from winrate import test

merge['tradedate'] = pd.to_datetime(merge['tradedate'])

test(merge)

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

draw(merge.cum)
draw(merge.fee_cum)
plt.plot(merge.tradedate, merge.cum, label = 'no_fee')
plt.plot(merge.tradedate, merge.fee_cum, label = 'after_fee')
plt.xticks(rotation = 45)
plt.grid()
plt.legend(loc="upper left")
plt.show()