#Important: the data used is from JoinQuant API: its website offers 1-year free account

#Main Repo#
IH.py IC.py contract.py 
getting data from Corporate SQL database
得到ICtable_new.csv ICtable_new.csv contract.csv

#JoinQuant文件夹#
Data required from JoinQuant API

winrate.py
API for calculating winning rate of a strategy

joinquant_future.py:
从Joinquant获取期货数据。得到future.csv

get_pre_index_factors:
获得前一天股指的信号数据。得到
pre_factors.csv dpreret.csv dprehigh.csv preret+prehigh.csv
带有信号，merge了指数信号和期货数据的数据

3_signals.py
子策略一
把preret+prehigh.csv和dbasis_60min.csv进行整合和信号生成

firstmins.py
子策略二
当天开盘5min的期货收益，趋势跟随。可以调整时间窗口

multi-strategy.py
两个子策略同时运行

#Basis文件价#
basis_minutes.py
前一交易日收盘前x分钟基差变化
basis.py
前一交易日基差变化
basis_first_mins.py
当日开盘价格变化

#first-mins文件夹#
存储JoinQuant/firstmins.py运行的结果
也被用到basis里面读取并计算

#last_money文件夹#
money.py
研究前日收盘集合竞价的成交金额(成交量)，生成第二天的交易信号
