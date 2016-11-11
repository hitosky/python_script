#!/usr/bin/env python
#coding:utf8

'''
从sameip和whois网站
收集某个网站的信息:
1.输入参数为ip地址，进入第二步；
  若输入参数为网址或者域名，通过ping 命令获取其ip地址，进入第二步；
2.根据1得来的ip地址，去sameip网站反查域名,进入第三步；
3.根据2中获得的域名，通过whois网站获取其注册人，注册邮箱，dns服务器等信息。
'''
import sys,requests,re;
import threading,subprocess,json;
from bs4 import BeautifulSoup;

IP,SITE = None,None;

# 显示使用方式
def usage():
	print u'''
	#####################################################
	usage:
	-h          show usage
	-p [ip]     collector site info according ip address
	-s [site]   collector site info according site
	#####################################################
	'''


# 解析脚本输入参数
def parse_argv():
	params = ['-p','-s','-h'];
	global IP,SITE;

	if len(sys.argv) <= 1 or len(sys.argv) > 3:
		usage();
		sys.exit();
	elif sys.argv[1] not in params:
		print 'unknown params';
		sys.exit();

	elif sys.argv[1] == '-p':
		IP = parse_ip(sys.argv[2]);

	elif sys.argv[1] == '-s':
		SITE = parse_site(sys.argv[2]);
	else:
		usage();

# 解析ip
def parse_ip(ip):
	ip = ip.strip();
	ips = ip.split('.');
	ip_re = r'^(25[0-5]|2[0-4]\d|1\d{1,2}|\d.){3}25[0-5]|24\d|1\d{1,2}|\d$';
	if len(re.findall(ip_re,ip)):
		return ip;

	print 'invalid ip address';
	sys.exit()

# 解析site
def parse_site(site):
	site = site.strip();
	site_re = '^(https?://)?[a-zA-Z0-9]+(\.[a-zA-Z0-9]+){1,}/{0,}$';
	if len(re.findall(site_re,site)):
		site = site.replace('https://','');
		site = site.replace('http://','');
		site = site.replace('/','');
		return site;
	
	print 'invalid site';
	sys.exit();

# unix与win下的ping命令
def pinger(site):
	if sys.platform.find('win') > -1:
		cmd = 'ping -n 2 %s'%(site);
		ip_re = r'\[(.*)\]';
	else: 
		cmd = 'ping -c 2 %s'%(site);
		ip_re = r'\((.*?)\)';

	p = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,
			stdout=subprocess.PIPE);
	(out,err) = p.communicate();
	ip = re.findall(ip_re,out);
	if len(err) or len(ip)<1:
		return None;
	else:
		return ip[0];

# 搜索同一ip的不同域名:
def reverse_ip_lookup(ip):
	domains = [];
	SAMEIP = 'http://www.sameip.org/';
	url = SAMEIP+ip;
	headers = {
	'Host':'www.sameip.org',
	'Referer':url,
	'Upgrade-Insecure-Requests':'1',
	'Cookie':'''
		_ga=GA1.2.995076706.1477732992; __atuvc=7%7C43%2C4%7C44; __atuvs=5815980f361d3033003; laravel_session_4=eyJpdiI6IjNLamFCcDVVenFOUmxyNXBSUHpldXFYcmhkbDgycWhEM2FXNVhhQm9Jcnc9IiwidmFsdWUiOiJsdndGQkNwM2ErMlRjNzZvb3dSeXVoTVwvTWxZQUN2UVM4TVZiOVlpZUFhR0NIbjBROVVrMHVaOVJPTUNtakZTOG9waDlFRkhNMitXcFJWVnRvWTVPRGc9PSIsIm1hYyI6IjhjOTBiMzhlYmRhYmZlODYwZjQ2ZDRiNjQwNTY1ZTcyN2VmYmZjMGUyYTIwMTgyYmM4MDk3Y2M3MGM0OTk2OWYifQ%3D%3D
	'''
	}
	rsp = requests.get(url,headers=headers);
	content = rsp.content.replace('\n','');
	domain_re = r'<li\>(.*?)\<\/li\>';
	
	content = re.findall(r'\<ol\>(.*)\<\/ol\>',content);
	if len(content)<=0:
		return [];
	domains = re.findall(domain_re,content[0]);
	return domains;

# whois搜索域名信息
def whois(domain):
	domain_info={};
	url = 'http://s1.aa2.cn/ajax/ajax.php';
	headers={
		'Host':'s1.aa2.cn',
		'Referer':'http://whois.aa2.cn'
	}
	cookies={
		'PHPSESSID':'dgdn8f4sh6d233q4bmtp73vvc4'
	}
	data={
		'type':10,
		'domain':domain,
		'g_div':'d_domain|d_whois|d_status|d_create|d_expire|d_email|d_age|d_whois_all',
		'g_type':'html',
		1477905195000:'',
		'_':1477905195884
	}
	rsp = requests.get(url,headers=headers,cookies=cookies,params=data);

	if domain not in rsp.content:
		return None;

	registrant_re = r'Registrant( Name)?: (.*?)<br';
	email_re  = r'Registrant( Contact)? Email: (.*?)<br';
	dns_re = r'Name Server: (.*?)<br';
	registrant = re.findall(registrant_re,rsp.content);
	email = re.findall(email_re,rsp.content);
	dns = re.findall(dns_re,rsp.content);

	registrant = len(registrant) and \
			registrant[0][1].decode('utf8') or '';
	email = len(email) and email[0][1] or '';
	dns = len(dns) and dns or '';
	domain_info = {
		'Registrant':registrant,
		'Registrant Contact Email':email,
		'DNS Server':dns
	}
	return domain_info;

# 显示域名信息
def show_domain_info(domain):
	print '\nDomain Name: %s'%domain;
	domain_info = whois(domain);
	if domain_info is None:
		print 'no info about this domain';
		return;

	for j in domain_info:
		print '%s: %s'%(j,domain_info[j]);

# 搜索信息
def collect_info():
	global IP,SITE;
	print '''start collecting''';
	domains = [];
	if SITE:
		IP = pinger(SITE);
		domains.append(SITE);

	if IP is None:
		print 'can not ping %s'%SITE;
		IP = 'unknown';
	else:
		 domains = domains+reverse_ip_lookup(IP);

	print u'''
	site:%s
	ip:%s
	'''% (SITE,IP);
		
	for i in domains:
		t=threading.Thread(target=show_domain_info,args=(i,));
		t.start();
		t.join();
	
if __name__ == '__main__':
	parse_argv();
	collect_info();
