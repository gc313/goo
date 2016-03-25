#-*- coding:utf-8 -*-

#因为我是个菜得不行的菜鸟，担心以后就忘了，所以注释会有点多
import urllib.request
#import MySQLdb
import pymysql
import json
import time
from datetime import datetime
from sendmail import Sendmail
import logging

#在当前目录下生成日志文件，并设置日志的等级、格式
#logging 功能还挺多，先简单做一做，以后再慢慢看这个模块
logging.basicConfig(filename = 'log.log', level = logging.INFO, filemode = 'w', format = '%(asctime)s - %(levelname)s : %(message)s')


#连接数据库
def Conn(data):


	'''
	这是import MySQLdb时候出问题的解决办法：

	刚开始有个报错:“UnicodeEncodeError: 'latin-1' codec can't encode character....”
		
	编码问题让人头痛，如下设置后解决问题，这是我在网上找到的方法，谢谢！
	
	db.set_character_set('utf8')
	dbc.execute('SET NAMES utf8;') dbc.execute('SET CHARACTER SET utf8;')
	dbc.execute('SET character_set_connection=utf8;')


	意思就是MySQLdb正常情况下会尝试将所有的内容转为latin1字符集处理

	所以处理方法就是，设置连接和游标的charset为你所希望的编码，如utf8

	db是connection连接，dbc是数据库游标
	-------------------------------------------------------------------------------------------
	但是现在树莓派上面还找不到python3-MySQLdb的安装源，所以我准备换用
	pyMySQL，搞不好又要被编码虐一遍。
	...……结果在Ubuntu上异常的顺利，不知树莓派如何
	'''
	#申明全局变量
	global sh_count, sz_count

	try:
	

		'''
		#用MySQLdb时亲测可行的方法
		conn = MySQLdb.Connect('192.168.0.102', 'root', '1123')
		conn.set_character_set('utf8')
	
		cur = conn.cursor()
		cur.execute('SET NAMES utf8;')
		cur.execute('SET CHARACTER SET utf8;')
		cur.execute('SET character_set_connection=utf8;') 
		'''

		#pyMySQL
		cone = 0
		while cone < 5:

			try:
				conn = pymysql.connect(user = 'root', passwd = '1123', host = '192.168.0.102', charset = 'utf8')
				break
			except Exception as e:
				logging.error('连接错误 %s' % e)
				cone += 1
				continue

		
		cur = conn.cursor()

		#判断数据库是否存在，如果数据库不存在则建立,并使用该数据库，语句是网上抄的……
		if not cur.execute('SELECT * FROM information_schema.SCHEMATA where SCHEMA_NAME="goo"'):
			#创建数据库，goo两边是 ` `，不是'  '或"  "
			cur.execute('CREATE DATABASE `goo` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci')
			logging.info('已建立数据库')


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
			
			logging.debug('已创建表%s' % t_name)


		#插入数据
		date_w = sql_w['date'] + ' ' + sql_w['time']

		#先检查目标表中最后一行数据，是否存在同一时间的数据，如有便跳过（还未修改这里，好像暂时也不必要）

		#检查是否有相同日期时间的数据，如有则跳过
		logging.debug(cur.execute('SELECT * FROM %s WHERE d_date = "%s" ' % (sql_w['code'], date_w)))
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
			logging.debug('已插入%s %s的数据' % (sql_w['name'],date_w))

			if t_name[:2] == 'sh':
				sh_count += 1
			else:
				sz_count += 1
			
			#提交
			conn.commit()
			#关闭指针和连接
			cur.close()
			conn.close()
		else:
			cur.close()
			conn.close()
			logging.debug('数据表中已有相同数据，跳过')

		
	except Exception as e:
		logging.error('%s' % e)

		cur.close()
		conn.close()



def DataAPI(url):

	#这里有Python3在请求里添加header的方法
	
	req = urllib.request.Request(url) #请求网页
	req.add_header('apikey', '9aeaa70065a1053db38cc4657f33ba64') #添加header
	
	resp = urllib.request.urlopen(req).read().decode('utf-8') #获得数据


	data = json.loads(str(resp)) #json读取数据（dict形式）
	
	if  data['errNum'] == 0:

		goo = data['retData']['stockinfo'] #取出主要数据
		#print(goo)
		if not goo['OpenningPrice'] == 0:#如果当日开盘价不为0就继续，否则下一个
			Conn(goo)#连接数据库

	else:
		logging.debug(str(data['errNum']) + ':' + data['errMsg'])
		#print(str(data['errNum']) + ':' + data['errMsg'])


	logging.debug('运行中……')
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
		url_data = url + 'sz' + str(code).zfill(6) + lis #zfill()给字符串类型的数字前面补0
		DataAPI(url_data)

def Now():
	return str(datetime.now())[:19]

#每日分析，筛选。发送邮件到指定邮箱
#运行日志功能待添加



if __name__ == '__main__':


	
	target = 'http://apis.baidu.com/apistore/stockservice/stock?stockid='
	lis = '&list=0'

	'''
	#测试用
	sh_count = 0
	DataAPI('http://apis.baidu.com/apistore/stockservice/stock?stockid=sh600663&list=0')
	logging.info('插入数据%s条' % sh_count)
	'''
	try:
		logging.info('程序运行')
		while 1:

			#定时运行,每天凌晨00:00开始采集数据
			run_time = Now()[11:16]
			if run_time == '00:00':
			#if 1:
				logging.info('开始采集数据')
				#加个计数功能，记录每天插入了多少条记录

				sh_count = 0
				sz_count = 0

				Get_sh_data(target, lis)
				Get_sz_data(target, lis)
				Sendmail('数据采集工作已于 %s 完成，沪市A股采集数据%s条，深市A股采集数据%s条。' % (Now(), sh_count, sz_count))
				logging.info('数据采集完成')
			time.sleep(50)
	except Exception as e:
		logging.error('%s' % e)
		Sendmail('%s 程序报错：%s ' % (Now(), e))
	finally:
		Sendmail('程序已结束运行 at %s ' % Now())
		logging.info('程序结束运行')
	
