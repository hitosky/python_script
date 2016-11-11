#!/usr/bin/env python
# coding:utf8

import smtplib;
from email import encoders;
from email.mime.text  import MIMEText;
from email.header import Header;
from email.utils import parseaddr, formataddr;

SMTP_SERVER = {
	'gmail':{
		"server":"smtp.gmail.com",
		"port":587
	},
	'163':{
		'server':'smtp.163.com',
		'port':25
	},
	'126':{
		'server':'smtp.126.com',
		'port':25
	},
	'yahoo':{
		'server':'smtp.mail.yahoo.com',
		'port':25
	}
};



# 格式化收件地址和发件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

# 设置邮箱发送所需参数
def set_mail_params(**email_params):
	msg = MIMEText(email_params['content'],\
		email_params['type'],email_params['charset']);
	msg['From'] = _format_addr(email_params['From']);
	msg['To'] = _format_addr(email_params['To']);
	msg['Subject'] = Header(email_params['Subject'],email_params['charset']).encode();

	return msg;
# 发送邮件
def send_mail(**kargs):
	msg = kargs['msg'];
	login = kargs['login_info'];
	

	from_addr = login['from_addr'];
	to_addr = login['to_addr'];
	password = login['auth_pwd'];
	try:
		server = smtplib.SMTP(login['server'],login['port']);
		# server.set_debuglevel(1);
		server.login(from_addr, password);
		server.sendmail(from_addr, [to_addr], msg.as_string());
		server.quit();
		print u'\t\t邮件已成功发送';
		return True;
	except Exception as e:
		print u'\t\t邮件发送失败，原因:%s'%e;
		return False;

