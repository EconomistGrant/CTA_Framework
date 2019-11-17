#这个文件计算的是当日开盘的基差变化，结果不太理想
#修改min的参数值（3，4，5，10，15，20，30），直接运行代码，可以得到结果
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import warnings
import os
warnings.simplefilter(action='ignore', category = FutureWarning)

min = 30
main = os.path.abspath(os.path.dirname(os.getcwd()))

future = pd.read_csv('{}/first_mins/{}min_future-future.csv'.format(main, min), index_col = 0)
index = pd.read_csv('{}/first_mins/{}min_index-future.csv'.format(main, min), index_col = 0)
future = future[['tradedate','ICopen','ICopen2','IHopen','IHopen2','drest']]
index = index[['tradedate','ICopen','ICopen2','IHopen','IHopen2']]
merge = pd.merge(future, index, how = 'inner', on = 'tradedate', suffixes = ('_f','_i'))
merge['tradedate'] = pd.to_datetime(merge['tradedate'])
merge = merge.dropna(how = 'any').reset_index(drop = True)

merge['ICbasis2'] = merge['ICopen2_i'] - merge['ICopen2_f']
merge['ICbasis'] = merge['ICopen_i'] - merge['ICopen_f']
merge['ICdbasis'] = merge['ICbasis2'] - merge['ICbasis']

merge['IHbasis2'] = merge['IHopen2_i'] - merge['IHopen2_f']
merge['IHbasis'] = merge['IHopen_i'] - merge['IHopen_f']
merge['IHdbasis'] = merge['IHbasis2'] - merge['IHbasis']

merge['ddbasis'] = merge['ICdbasis'] - merge['IHdbasis']

for x in merge.index:
	if merge.loc[x, 'ddbasis'] > 0:
		merge.loc[x, 'signal'] = 1
	else:
		merge.loc[x, 'signal'] = -1

merge['ret'] = merge['signal'] * merge['drest']
merge['fee'] = 0.0004
merge['fee_ret'] = merge['ret'] - merge['fee']

merge['cum'] =  np.ones(len(merge))
merge['fee_cum'] = np.ones(len(merge))

cumtemp = 1
feecumtemp = 1
for x in merge.index:
	if x == 0:
		merge['cum'] = 1 + merge.loc[x, 'ret']
	else:
		merge.loc[x, 'cum'] = (merge.loc[x, 'ret'] + 1) * cumtemp
		merge.loc[x, 'fee_cum'] = (merge.loc[x, 'fee_ret'] +1) * feecumtemp

	cumtemp = merge.loc[x, 'cum']
	feecumtemp = merge.loc[x, 'fee_cum']
 

print(merge[['cum','fee_cum']].tail())

from winrate import test
print(min)
test(merge)

merge.to_csv('{}/first_mins/{}min_basis-future.csv'.format(main, min))

plt.plot(merge.tradedate, merge.cum)
plt.xticks(rotation = 45)
plt.show()