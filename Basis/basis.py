import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
'''
future = pd.read_csv('C:/Users/account/Desktop/BackTest/ICIH.csv', index_col = 0)
'''

main = os.path.abspath(os.path.dirname(os.getcwd()))
future = pd.read_csv('{}/JoinQuant/futures.csv'.format(main), index_col = 0)
index = pd.read_csv('{}/JoinQuant/ICIHindex.csv'.format(main), index_col = 0)

future.tradedate = pd.to_datetime(future.tradedate)
index.tradedate = pd.to_datetime(index.tradedate)
Basis = pd.merge(future, index, how = 'inner', on = 'tradedate', suffixes = ('_f','_i'))
print(Basis.columns)
Basis['basis_ic'] = Basis['preclose_IC'] - Basis['ICpreclose']
Basis['basis_ih'] = Basis['preclose_IH'] - Basis['IHpreclose']

Basis['prebasis_ic'] = Basis.basis_ic.shift(1)
Basis['dbasis_ic'] = Basis.prebasis_ic - Basis.basis_ic

Basis['prebasis_ih'] = Basis.basis_ih.shift(1)
Basis['dbasis_ih'] = Basis.prebasis_ih - Basis.basis_ih
Basis['ddbasis'] = Basis.dbasis_ic - Basis.dbasis_ih
Basis['dbasis'] = Basis.basis_ic - Basis.basis_ih

Basis = Basis.dropna(how = 'any').reset_index(drop = True)
Basis = Basis[['instrumentID_IC', 'instrumentID_IH', 'tradedate', 'dbasis_ih', 'dbasis_ic','dbasis','ddbasis','ICmIH_f']]

Basis['signal'] = np.zeros(len(Basis))
Basis['cum'] = np.ones(len(Basis))


def test_factor (factor = 'ddbasis', direction = 1):
	for x in range(len(Basis.index)):
		if (Basis.loc[x, factor] * direction) >= 0:
			Basis.loc[x, 'signal'] = 1
		elif (Basis.loc[x, factor] * direction) < -0:
			Basis.loc[x, 'signal'] = -1
	Basis['ret'] = Basis['signal'] * Basis['ICmIH_f']
	for x in range(len(Basis.index)):
		if x == 0:
			pass
		else:
			Basis.loc[x, 'cum'] = (Basis.loc[x-1, 'cum'] * (Basis.loc[x, 'ret'] +1))
	result = Basis[['tradedate','ICmIH_f',factor, 'signal', 'ret', 'cum']]
	return result

dbasis = test_factor('ddbasis', 1)
from winrate import test
test(dbasis)
print(dbasis.head(5))
print(dbasis.tail(5))

plt.plot(Basis.tradedate, Basis.cum)
plt.xticks(rotation = 45)
plt.show()
