#-*- coding:utf-8 -*-

#这个模块的代码基本都是抄的，还没完全搞懂它的意思

#导入发邮件所需模块
import smtplib
import email.mime.multipart  
import email.mime.text 

from datetime import date


def Sendmail(message):
	
	today = str(date.today())
	from_addr = 'big_sister@yeah.net'
	paswd = 'mima15987532'
	to_addr = 'gc313@qq.com'
	smtp_server = 'smtp.yeah.net'
	

	msg = email.mime.multipart.MIMEMultipart()
	msg['From'] = '莓莓姐姐'
	msg['To'] = to_addr
	msg['Subject'] = '每日数据采集情况 ' + today
	content = message
	txt = email.mime.text.MIMEText(content)
	#print(txt)
	#print('------------------------------------')
	msg.attach(txt)
	#print(msg)

	server = smtplib.SMTP()
	server.connect(smtp_server, '25')
	server.login(from_addr, paswd)
	server.sendmail(from_addr, [to_addr], str(msg))
	server.quit()
	

if __name__ == '__main__':
	
	Sendmail('总是被编码搞得心力交瘁……')




