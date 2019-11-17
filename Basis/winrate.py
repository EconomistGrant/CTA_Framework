import pandas as pd

def test (data):
	positive = 0
	total = 0
	for x in data.ret:
		if x == 0:
			pass
		else:
			total += 1
			if x > 0:
				positive+=1
			else:
				pass

	print('正收益天数占{:.4f}, {}, {}'.format(positive / total, positive, total))

	positive2019= 0
	total2019 = 0
	for x in data.index:
		if data.tradedate[x] < pd.to_datetime('20190101'):
			pass
		else:
			if data.ret[x] != 0: 
				total2019 += 1
				if data.ret[x] > 0:
					positive2019 +=1
				else: 
					pass
			else:
				pass

	print('2019年正收益天数占{:.4f}, {}, {}'.format(positive2019 / total2019, positive2019, total2019))
	 
	positive2018 = 0
	total2018 = 0
	for x in data.index:
		if data.tradedate[x] < pd.to_datetime('20180101'):
			pass
		elif data.tradedate[x] > pd.to_datetime('20181231'):
			pass
		else:
			if data.ret[x] != 0: 
				total2018 += 1
				if data.ret[x] > 0:
					positive2018 +=1
				else: 
					pass
			else:
				pass

	print('2018年正收益天数占{:.4f}, {}, {}'.format(positive2018 / total2018, positive2018, total2018))

	positive2017 = 0
	total2017 = 0
	for x in data.index:
		if data.tradedate[x] < pd.to_datetime('20170101'):
			pass
		elif data.tradedate[x] > pd.to_datetime('20171231'):
			pass
		else:
			if data.ret[x] != 0: 
				total2017 += 1
				if data.ret[x] > 0:
					positive2017 +=1
				else: 
					pass
			else:
				pass


	print('2017年正收益天数占{:.4f}, {}, {}'.format(positive2017 / total2017, positive2017, total2017))

	positive2016 = 0
	total2016 = 0
	for x in data.index:
		if data.tradedate[x] < pd.to_datetime('20160101'):
			pass
		elif data.tradedate[x] > pd.to_datetime('20161231'):
			pass
		else:
			if data.ret[x] != 0: 
				total2016 += 1
				if data.ret[x] > 0:
					positive2016 +=1
				else: 
					pass
			else:
				pass

	print('2016年正收益天数占{:.4f}, {}, {}'.format(positive2016 / total2016, positive2016, total2016))

	positive2015 = 0
	total2015 = 0
	for x in data.index:
		if data.tradedate[x] < pd.to_datetime('20150101'):
			pass
		elif data.tradedate[x] > pd.to_datetime('20151231'):
			pass
		else:
			if data.ret[x] != 0: 
				total2015 += 1
				if data.ret[x] > 0:
					positive2015 +=1
				else: 
					pass
			else:
				pass

	print('2015年正收益天数占{:.4f},{}, {}'.format(positive2015 / total2015, positive2015, total2015))
