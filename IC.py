import pandas as pd
import pymssql
import numpy as np

def query(chSQL, to_dict = True):
    conn = pymssql.connect('192.168.1.153:1433', 'Traders', 'abcd4321', 'FutureTickData')
    cursor = conn.cursor(as_dict=to_dict)
    cursor.execute(chSQL)
    results = cursor.fetchall()
    conn.close()
    return results

#---建一个包含交易日和交易日对应的最近一期的期指合同的表---#
#所有的期指合同
IClist = query("SELECT name FROM sysobjects WHERE xtype='U' AND name LIKE 'IC%'", False)
print(IClist)
#初始化一张1505的表作为总表，之后再合并
ICtable =  pd.DataFrame(query("SELECT DISTINCT tradedate, instrumentID FROM IC1505"))
ICtable['tradedate'] = pd.to_datetime(ICtable['tradedate'])
#每个新期指合同，只更新之前的总表中不包含的日期，这样每个日期对应的表就是最近的期指合同
#这里把最后一条drop掉，就可以被下一期覆盖（即每个合同最后一个交易日，第三个周五，采用的是远期的合同）
for IC in IClist:
	print(IC)
	contract = pd.DataFrame(query("SELECT DISTINCT tradedate, instrumentID FROM {}".format(IC[0])))
	contract['tradedate'] = pd.to_datetime(contract['tradedate'])
	contract = contract.drop(index = len(contract) - 1)
	for x in range(len(contract.index)):
		if contract.iloc[x]['tradedate'] <= ICtable.iloc[-1]['tradedate']:
			pass
		else:
			ICtable = ICtable.append(contract.iloc[x])
			ICtable = ICtable.reset_index(drop = True)
ICtable.to_csv('ICtable_new.csv')
'''
#---建立因子---#
#数据为：ID, 交易日，前一交易日，前一交易日的收盘价，这个交易日的收盘价，（前一交易日产生的）因子
ICtable = pd.read_csv('ICtable.CSV', header = 0, index_col = 0)
ICtable['pretradedate'] = ICtable['tradedate'].shift(1)
ICtable = ICtable.dropna(how = 'any')
ICtable = ICtable.reset_index(drop = True)

#建立MF因子。如果LastPrice上升，MF累加Volume，若下降则累减Volume

for x in range(len(ICtable.index)):
	print(ICtable.iloc[x].tradedate)
	pre2close = query("SELECT DISTINCT precloseprice FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].pretradedate),False)[0][0]
	preclose = query("SELECT DISTINCT precloseprice FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].tradedate),False)[0][0]
	close = query("SELECT TOP 1 lastprice FROM {} WHERE tradedate = '{}' ORDER BY servertime DESC".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].tradedate), False)[0][0]
	preopen = query("SELECT DISTINCT openprice FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].pretradedate),False)[0][0]
	premax = query("SELECT max(lastprice) as max FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].pretradedate), True)[0]['max']
	premin = query("SELECT min(lastprice) as min FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].pretradedate), True)[0]['min']
	table = query("SELECT lastprice, volume FROM {} WHERE tradedate = '{}'".\
		format(ICtable.iloc[x].instrumentID, ICtable.iloc[x].pretradedate), True)
	table = pd.DataFrame(table)
	table.reset_index(drop = True)
	MF = 0
	SUM = 0
	Temp = pre2close
	for y in range(len(table.index)):
		if table.loc[y, 'lastprice'] > Temp:
			MF += table.loc[y, 'volume']
			SUM += table.loc[y, 'volume']
		if table.loc[y, 'lastprice'] < Temp:
			MF -= table.loc[y, 'volume']
			SUM += table.loc[y, 'volume']
		else:
			SUM += table.loc[y, 'volume']
		Temp = table.loc[y, 'lastprice']
	ICtable.loc[x, 'pre2close'] = pre2close
	ICtable.loc[x, 'preclose'] = preclose
	ICtable.loc[x, 'close'] = close
	ICtable.loc[x, 'preopen'] = preopen
	ICtable.loc[x, 'premax'] = premax 
	ICtable.loc[x, 'premin'] = premin
	ICtable.loc[x,'MF'] = MF / SUM

ICtable['ret'] = ICtable['close'] / ICtable['preclose'] - 1
ICtable['preret'] = ICtable['preclose'] / ICtable['pre2close'] - 1
ICtable['premax'] = ICtable['premax'] / ICtable['preclose']
ICtable['premin'] = ICtable['premin'] / ICtable['preclose']
ICtable.to_csv('IC.CSV')
'''