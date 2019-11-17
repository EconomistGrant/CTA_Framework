import pandas as pd
import pymssql
import numpy as np

def query(chSQL, to_dict = True):
    conn = pymssql.connect('192.168.1.153:1433', 'Traders', 'abcd4321', 'FutureTICkData')
    cursor = conn.cursor(as_dict=to_dict)
    cursor.execute(chSQL)
    results = cursor.fetchall()
    conn.close()
    return results

#---建一个包含交易日和交易日对应的最近一期的期指合同的表---#
#所有的期指合同
IHlist = query("SELECT name FROM sysobjects WHERE xtype='U' AND name LIKE 'IH%'", False)
print(IHlist)
#初始化一张1505的表作为总表，之后再合并
IHtable =  pd.DataFrame(query("SELECT DISTINCT tradedate, instrumentID FROM IH1505"))
IHtable['tradedate'] = pd.to_datetime(IHtable['tradedate'])

print(query("SELECT TOP 1 * FROM IH1907"))

#每个新期指合同，只更新之前的总表中不包含的日期，这样每个日期对应的表就是最近的期指合同
for IH in IHlist:
	print(IH[0])
	contract = pd.DataFrame(query("SELECT DISTINCT tradedate, instrumentID FROM {}".format(IH[0])))
	contract['tradedate'] = pd.to_datetime(contract['tradedate'])
	contract = contract.drop(index = len(contract) - 1)
	for x in range(len(contract.index)):
		if contract.iloc[x]['tradedate'] <= IHtable.iloc[-1]['tradedate']:
			pass
		else:
			IHtable = IHtable.append(contract.iloc[x])
			IHtable = IHtable.reset_index(drop = True)
IHtable.to_csv('IHtable_new.csv')
'''
#---建立因子---#
#数据为：ID, 交易日，前一交易日，前一交易日的收盘价，这个交易日的收盘价，（前一交易日产生的）因子
IHtable = pd.read_csv('IHtable.CSV', header = 0, index_col = 0)
IHtable['pretradedate'] = IHtable['tradedate'].shift(1)
IHtable = IHtable.dropna(how = 'any')
IHtable = IHtable.reset_index(drop = True)
#注意这里：drop掉第一个数据的时候index的起点变成1了？

for x in range(len(IHtable.index)):
	pre2close = query("SELECT DISTINCT precloseprice FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].pretradedate),False)[0][0]
	close = query("SELECT TOP 1 lastprice FROM {} WHERE tradedate = '{}' ORDER BY servertime DESC".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].tradedate), False)[0][0]
	preclose = query("SELECT DISTINCT precloseprice FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].tradedate),False)[0][0]
	preopen = query("SELECT DISTINCT openprice FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].pretradedate),False)[0][0]
	premax = query("SELECT max(lastprice) as max FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].pretradedate), True)[0]['max']
	premin = query("SELECT min(lastprice) as min FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].pretradedate), True)[0]['min']
#调用每一天的tick数据
	table = pd.DataFrame(query("SELECT lastprice, volume FROM {} WHERE tradedate = '{}'".\
		format(IHtable.iloc[x].instrumentID, IHtable.iloc[x].pretradedate), True))
	MF = 0
	Temp = pre2close

	for y in range(len(table.index)):
		if table.loc[y, 'lastprice'] > Temp:
			MF += table.loc[y, 'volume']
		if table.loc[y, 'lastprice'] < Temp:
			MF -= table.loc[y, 'volume']
		else:
			pass
		Temp = table.loc[y, 'lastprice']

	IHtable.loc[x, 'preclose'] = preclose
	IHtable.loc[x, 'pre2close'] = pre2close	
	IHtable.loc[x, 'close'] = close
	IHtable.loc[x, 'preopen'] = preopen
	IHtable.loc[x, 'premax'] = premax 
	IHtable.loc[x, 'premin'] = premin
	IHtable.loc[x,'MF'] = MF

IHtable['ret'] = IHtable['close'] / IHtable['preclose'] - 1
IHtable['preret'] = IHtable['preclose'] / IHtable['pre2close'] - 1
IHtable['premax'] = IHtable['premax'] / IHtable['preclose']
IHtable['premin'] = IHtable['premin'] / IHtable['preclose']
IHtable.to_csv('IH.CSV')
'''