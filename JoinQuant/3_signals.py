import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import os

main = os.path.abspath(os.path.dirname(os.getcwd()))
pre = pd.read_csv('{}/JoinQuant/preret+prehigh.csv'.format(main),index_col = 0)
prebasis = pd.read_csv('{}/Basis/dbasis_pre60mins.csv'.format(main),index_col = 0)

pre = pre[['tradedate','ICmIH','signal']]
prebasis = prebasis[['tradedate', 'signal']]

merge = pd.merge(pre, prebasis, how = 'inner', on = 'tradedate', suffixes = ('_x','_y'))

merge['signal'] = np.zeros(len(merge))
for i in merge.index:
	if merge.loc[i,'signal_x'] == merge.loc[i,'signal_y']:
		merge.loc[i, 'signal'] = merge.loc[i, 'signal_x']
	else:
		pass
merge['ret'] = merge['ICmIH'] * merge['signal']


merge['cum'] = 1
merge['fee_cum'] = 1
temp = merge.signal[0]
cumtemp = 1
feecumtemp = 1

for x in merge.index:
	if merge.loc[x, 'signal'] == temp:
		merge.loc[x, 'fee'] = 0
	else:
		merge.loc[x, 'fee'] = 0.0004 * abs(merge.loc[x, 'signal'] - temp)
	merge.loc[x, 'fee_ret'] = merge.loc[x,'ret'] - merge.loc[x, 'fee']
	
	if x == 0:
		pass
	else:
		merge.loc[x, 'cum'] = (merge.ret[x] + 1) * cumtemp
		merge.loc[x, 'fee_cum'] = (merge.loc[x, 'fee_ret'] +1) * feecumtemp
	cumtemp = merge.loc[x, 'cum']
	feecumtemp = merge.loc[x, 'fee_cum']
	temp = merge.loc[x, 'signal']

merge.tradedate = pd.to_datetime(merge.tradedate)
print(merge[['cum','fee_cum']].tail())

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
draw(merge.fee_cum)
from winrate import test
test(merge)

merge.to_csv('{}/JoinQuant/pre_3_signals.csv'.format(main))
plt.plot(merge.tradedate, merge.cum, label = 'no_fee')
plt.plot(merge.tradedate, merge.fee_cum, label = 'after_fee')
plt.xticks(rotation = 45)
plt.grid()
plt.legend(loc="upper left")
plt.show()
