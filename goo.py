#-*- coding:utf-8 -*-

#因为我是个菜得不行的菜鸟，担心以后就忘了，所以注释会有点多
import urllib.request
import MySQLdb
import json
import time
from datetime import datetime
from sendmail import Sendmail



#连接数据库
def Conn(data):


	'''
	刚开始有个报错:“UnicodeEncodeError: 'latin-1' codec can't encode character....”
		
	编码问题让人头痛，如下设置后解决问题，这是我在网上找到的方法，谢谢！
	
	db.set_character_set('utf8')
	dbc.execute('SET NAMES utf8;') dbc.execute('SET CHARACTER SET utf8;')
	dbc.execute('SET character_set_connection=utf8;')


	意思就是MySQLdb正常情况下会尝试将所有的内容转为latin1字符集处理

	所以处理方法就是，设置连接和游标的charset为你所希望的编码，如utf8

	db是connection连接，dbc是数据库游标
	'''
	try:
	

		conn = MySQLdb.Connect('192.168.0.102', 'root', '1123')
		conn.set_character_set('utf8')
	
		cur = conn.cursor()
		cur.execute('SET NAMES utf8;')
		cur.execute('SET CHARACTER SET utf8;')
		cur.execute('SET character_set_connection=utf8;')

		#判断数据库是否存在，如果数据库不存在则建立,并使用该数据库，语句是网上抄的……
		if not cur.execute('SELECT * FROM information_schema.SCHEMATA where SCHEMA_NAME="goo"'):
			cur.execute('CREATE DATABASE `goo` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci')

		cur.execute('USE goo')
	

		#开始创建表
		sql_w = data
		t_name = sql_w['code']
		#print(t_name)
	
		#判断表是否存在,不存在则建立表，表的名称为股票代码

		#这里要注意，表的名字外面还有引号，语句是: “ SELECT * FROM information_schema.TABLES where table_name = ’表的名字‘ ”
		if not cur.execute('SELECT * FROM information_schema.TABLES where table_name = "%s"' % t_name):
			cur.execute(
				'CREATE TABLE ' + t_name + 
				'(id int auto_increment primary key NOT NULL,'+ #自动增加、关键字、不能为空
				'name varchar(20), '+
				'd_date datetime,'+
				'op float(8), '+
				'cp float(8), '+
				'currentP float(8), '+
				'hPrice float(8), '+
				'lPrice float(8), '+
				'compP float(8), '+
				'auctP float(8), '+
				'total int(10), '+
				'turnover float(20), '+
				'buy1 int(10), buy1_p float(8), '+
				'buy2 int(10), buy2_p float(8), '+
				'buy3 int(10), buy3_p float(8), '+
				'buy4 int(10), buy4_p float(8), '+
				'buy5 int(10), buy5_p float(8), '+
				'sell1 int(10), sell1_p float(8), '+
				'sell2 int(10), sell2_p float(8), '+
				'sell3 int(10), sell3_p float(8), '+
				'sell4 int(10), sell4_p float(8), '+
				'sell5 int(10), sell5_p float(8) )'
				)


		#插入数据
		date_w = sql_w['date'] + ' ' + sql_w['time']

		#先判断目标表中是否有相同时间的数据，如有便跳过
		if not cur.execute('SELECT * FROM %s WHERE d_date = "%s" ' % (sql_w['code'], date_w)):

			#这里也坑死我了，字符串的字段两边也是有引号的，是有引号的，是有引号的！数值字段两边则没有
			#语句是： “INSERT INTO <表的名称> (<列1>, <列2>, <列3>, ....<列n>) values ('<字符串字段>', '<日期 时间 YYYY-MM-DD HH:MM:SS格式>', 数值, .... 数值n)”
			#这是我按我的理解写的……
			#在values()那里也坑了很久，直接"... values('%s', '%s', %.2f, %d) % (字符串变量1, 字符串变量2, 浮点数变量, 整数变量)"就可以了，刚开始照网上教程照葫芦画瓢反而没搞对，都不好意思写出来了。
			cur.execute(
				'INSERT INTO ' + t_name + 
				' (name, d_date, '+
				'op, cp, currentP, hPrice, lPrice, compP, auctP, total, turnover, '+
				'buy1, buy1_p, buy2, buy2_p, buy3, buy3_p, buy4, buy4_p, buy5, buy5_p, '+
				'sell1, sell1_p, sell2, sell2_p, sell3, sell3_p, sell4, sell4_p,sell5, sell5_p) '+
				'values ("%s", "%s", %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %d, %d, %.2f, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f, %d, %.2f)' %
				(sql_w['name'], date_w, 
				sql_w['OpenningPrice'], sql_w['closingPrice'], 
				sql_w['currentPrice'], sql_w['hPrice'], sql_w['lPrice'], 
				sql_w['competitivePrice'], sql_w['auctionPrice'], 
				sql_w['totalNumber'], sql_w['turnover'], 
				sql_w['buyOne'], sql_w['buyOnePrice'], 
				sql_w['buyTwo'], sql_w['buyOnePrice'], 
				sql_w['buyThree'], sql_w['buyThreePrice'], 
				sql_w['buyFour'], sql_w['buyFourPrice'], 
				sql_w['buyFive'], sql_w['buyFivePrice'], 
				sql_w['sellOne'], sql_w['sellOnePrice'], 
				sql_w['sellTwo'], sql_w['sellTwoPrice'], 
				sql_w['sellThree'], sql_w['sellThreePrice'], 
				sql_w['sellFour'], sql_w['sellFourPrice'], 
				sql_w['sellFive'], sql_w['sellFivePrice'])
				)
			#提交
			conn.commit()
			#关闭指针和连接
			cur.close()
			conn.close()

		
	except:
		print('ERROR')
		cur.close()
		conn.close()



def DataAPI(url):

	#这里有Python3在请求里添加header的方法
	
	req = urllib.request.Request(url) #请求网页
	req.add_header('apikey', 'APIkey放这里') #添加header
	
	resp = urllib.request.urlopen(req).read().decode('utf-8') #获得数据


	data = json.loads(str(resp)) #json读取数据（dict形式）
	
	if  data['errNum'] == 0:

		goo = data['retData']['stockinfo'] #取出主要数据
		#print(goo)
		if not goo['OpenningPrice'] == 0:#如果当日开盘价不为0就继续，否则下一个
			Conn(goo)#连接数据库

	else:
		print(str(data['errNum']) + ':' + data['errMsg'])

	print('运行中.....' +Now())
	#Sendmail('连接测试..... %s ' % Now())
	time.sleep(3)



def Get_sh_data(url, lis):
	for code in range(600000, 602000):
		url_data = url + 'sh' + str(code) + lis
		DataAPI(url_data)
	for code in range(603000, 604000):
		url_data = url + 'sh' + str(code) + lis
		DataAPI(url_data)

def Get_sz_data(url, lis):
	for code in range(1, 1000):
		url_data = url + 'sz' + str(code.zfill(6)) + lis #zfill()给数字前面补0
		DataAPI(url_data)

def Now():
	return str(datetime.now())[:19]

#每日分析，筛选。发送邮件到指定邮箱
#运行日志功能待添加



if __name__ == '__main__':

	
	target = 'http://apis.baidu.com/apistore/stockservice/stock?stockid='
	lis = '&list=0'
	#DataAPI(' http://apis.baidu.com/apistore/stockservice/stock?stockid=sh600005&list=0')
	while 1:

		#定时运行,每天凌晨00:00开始采集数据
		run_time = Now()[11:16]
		if run_time == '00:00':
			Get_sh_data(target, lis)
			Get_sz_data(target, lis)
			Sendmail('数据采集工作已于 %s 完成' % Now())
		time.sleep(50)
