#!/usr/bin/env python
# coding:utf8
'''
简易的密码管理器：
功能：
1.保存密码
2.删除密码
3.新增密码
安全：
1.结合aes与随机token的用户身份认证
2.使用rsa加密用户名，密码
'''
import sys,os,optparse,time;
from random_passwd import *
from email_operation import *
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA

# 清空控制台
def clear_console():
	if sys.platform.find('win')>-1:
		os.system('cls');
	else:
		os.system('clear');

# 继续操作还是返回上一级
def continue_or_return():
	while True:
		x = raw_input('\t\tcontinue(y),back(n)?');
		if x.lower() == 'y':
			return True;
		elif x.lower() == 'n':
			return False;

# 删除文件空白行
def remove_space_line(file):
	with open(file,'r') as f:
		new_lines = [];
		old_lines = f.readlines();
		for line in old_lines:
			if line.split():
				new_lines.append(line);

	with open(file,'wb') as f:
		f.writelines(new_lines);


class Password(object):
	def __init__(self,isInstall,token_len,rsa_len):
		self.token_len = token_len;
		self.rsa_len = rsa_len;
		# aes key值，16位固定，可以修改
		self.aes_key = ''
		# 验证身份的token
		self.id_token = self.__generate_random_token__(token_len);
		# 验证是否有权限操作
		self.pri_token = self.__generate_random_token__(token_len);
		
		# 邮箱登录信息
		self.login_info = {
			'server':SMTP_SERVER['163']['server'],
			'port':SMTP_SERVER['163']['port'],
			'from_addr':'',
			'auth_pwd':"",
			'to_addr':''
		};
		# 邮件参数
		self.email_params = {
			'content':'',
			'type':'plain',
			'charset':'utf-8',
			'From':u'密码管理器<from email>',
			'To':u'You<to email>',
			'Subject':u'密码验证'
		};
		
		# 明文文件
		self.pwd_file = '';
		# 密文文件
		self.encrypt_file = '';
		# rsa公钥文件
		self.rsa_public_file = '';
		# rsa私钥文件
		self.rsa_private_file = '';

		# 如果是第一次运行程序，则默认产生一对rsa公私钥
		if isInstall:
			self.__generate_rsa_key__(rsa_len);
			self.encrypt();
		else:
			self.run();
		

	# 清屏并显示头部信息
	def show_head(self)	:
		clear_console();
		print u'''
		*************************************
			     密码管理器
		*************************************
		'''
	# 运行密码管理器
	def run(self):
		self.show_head();
		self.validate_id();
		self.operate_pwd();

	# 验证身份
	def validate_id(self):
		success = self.send_token();
		if success :
			id_token = raw_input('\t\tinput id token:');
			pri_token = raw_input('\t\tinput pri token:');
			if id_token != self.id_token \
				or pri_token != self.pri_token:
				print u'\t\t口令错误!!!';
				self.__exit_system__();
			else:
				print u'\t\t登录成功';
				if self.decrypt():
					time.sleep(1);
				else:
					self.__exit_system__();
		else:
			self.__exit_system__();

	# 发送加密后的口令到邮箱
	def send_token(self):
		print u'\t\t等待发送邮件';
		aes_text = aes_encrypt(text=self.id_token,\
			key=self.aes_key);
		if os.path.isfile(self.rsa_public_file):
			with open(self.rsa_public_file,'r') as f:
				key = f.read();
				rsa_text = rsa_encrypt(text=self.pri_token,\
				public_key=key);
		else:
			print u'\t\t没有找到公钥文件%s'%self.rsa_public_file;
			self.__exit_system__();


		self.email_params['content'] = u'''
			请用aes key解密以下密文,得到id token
			%s\n
			请用rsa key解密以下密文,得到pri token
			%s\n
		'''%(aes_text,rsa_text);
		email_params = self.email_params;
		msg = set_mail_params(**email_params);
		kargs = {
			'msg':msg,	
			'login_info':self.login_info
		}
		return send_mail(**kargs);

	# 操作密码文件
	def operate_pwd(self):
		self.show_head();
		print u'''
			1.查询密码
			2.删除密码
			3.增加密码
			4.更新公钥与私钥
			5.退出管理器
			'''
		op_id = raw_input('\t\tinput operation id(1-5):');
		if op_id == '1':
			self.__common_operation__(\
				self.pwd_file,self.__check_pwd__);
		elif op_id == '2':
			self.__common_operation__(\
				self.pwd_file,self.__remove_pwd__);
		elif op_id == '3':
			self.__common_operation__(\
				self.pwd_file,self.__add_pwd__);
		elif op_id == '4':
			self.__update_rsa_key__();
		elif op_id == '5':
			self.__exit_system__();

		# 保持公私钥文件与明文密文同步	
		if op_id != '1':
			self.encrypt();
		self.operate_pwd();

	# 加密用户名，密码明文
	def encrypt(self):
		if os.path.isfile(self.pwd_file):
			with open(self.pwd_file,'r') as f:
				pwd_content = f.readlines();
		else:
			print u'\t\t加密失败:无法找到需加密的明文文件%s'%\
			self.pwd_file;

			return False;
		if os.path.isfile(self.rsa_public_file):
			with open(self.rsa_public_file,'r') as f:
				rsa_public_key = f.read();
		else:
			print u'加密失败:无法找到公钥文件:%s'\
			%self.rsa_public_file;
			return False;

		with open(self.encrypt_file,'wb') as f:
			encrypt_text = [];
			# 分段加密，避免明文过长出错
			for line in pwd_content:
				encrypt_text.append(rsa_encrypt(line,rsa_public_key)+
					'\n');
			f.writelines(encrypt_text);

		print u'\t\t密码文件加密成功';
		return True;

	# 解密用户名和密码密文
	def decrypt(self):
		if os.path.isfile(self.encrypt_file):
			with open(self.encrypt_file,'r') as f:
				encrypt_pwd = f.readlines();
		else:
			print u'\t\t解密失败:无法找到密文文件:%s'\
			%self.encrypt_file;
			return False;
		if os.path.isfile(self.rsa_private_file):
			with open(self.rsa_private_file,'r') as f:
				rsa_private_key = f.read();
		else:
			print u'\t\t解密失败:无法找到私钥文件:%s'\
			%self.rsa_private_file;
			return False;

		with open(self.pwd_file,'wb') as f:
			text = [];
			# 分段解密
			for line in encrypt_pwd:
				text.append(rsa_decrypt(line,rsa_private_key));
			f.writelines(text);
			
		print u'\t\t加密的密码文件解密成功';
		return True;

	# 产生随机口令
	def __generate_random_token__(self,token_len):
		str_arr = lambda s : [chr(ord(s)+i) for i in range(0,26)];
		num_arr = lambda max:[str(i) for i in range(0,max+1)];
		a = str_arr('a')+str_arr('A')+num_arr(9);
		spwd = ''.join(a);
		return generate_random_pwd(spwd,token_len);
	
	# 产生rsa的公私钥
	def __generate_rsa_key__(self,rsa_len):
		self.show_head();
		print u'''
		生成公钥文件%s
		与密钥文件%s
		请妥善保管好密钥文件！！！！！！！
		'''%(self.rsa_public_file,self.rsa_private_file);
		rsa_random = Random.new().read;
		rsa = RSA.generate(rsa_len,rsa_random);

		private_key = rsa.exportKey();
		public_key = rsa.publickey().exportKey();

		with open(self.rsa_public_file,'wb') as f:
			f.write(public_key);

		with open(self.rsa_private_file,'wb') as f:
			f.write(private_key);


	# 先判断文件是否存在，再执行具体操作，并询问继续还是返回上一级
	def __common_operation__(self,file,operation):
		while True:
			if os.path.isfile(file):
				remove_space_line(file);
				operation();
				if continue_or_return():
					continue;
				else:
					return True;
			else:
				print u'\t\t不存在文件:%s'\
				%file;
				if continue_or_return():
					continue;
				else:
					return False;

	# 查看密码文件
	def __check_pwd__(self):
		with open(self.pwd_file,'r') as f:
			k = 1;
			print u'\t\t密码文件如下:'
			for line in  f.readlines():
				print '\t\t%d.%s'%(k,line);
				k=k+1;

	
	# 删除某一密码
	def __remove_pwd__(self):
		with open(self.pwd_file,'r') as f:
			k = 1;
			print u'\t\t密码文件如下:';
			lines = f.readlines();
			for l in lines:
				print '\t\t%d.%s'%(k,l);
				k=k+1;
		while True:
			x = raw_input('\t\tinput the id which to remove:');
			try :
				i = int(x)
				if i<1 or i>len(lines):
					continue;
				else:
					del lines[i-1];
					with open(self.pwd_file,'wb') as f:
						f.writelines(lines);
						print u'\t\t删除成功';
					return;
			except:
				continue;

	# 增加密码
	def __add_pwd__(self):
		print u'\t\t输入标识这条数据的名称，比如说用户名和密码用在的网站名称'
		dataname = raw_input('\t\tinput dataname:');
		username = raw_input('\t\tinput username:');
		while True:
			rad = raw_input('\t\tdo you want to generate random password(y/n)');
			if rad.lower() == 'y':
				password = generate_random_pwd();
				print u'\t\t自动生成的密码为:  %s'%password;
				break;
			elif rad.lower() == 'n':
				password = raw_input('\t\tinput password:');
				break;
		data = '\n'+dataname+' '+username+' '+password;
		with open(self.pwd_file,'ab') as f:
			f.write(data);
			print u'\t\t写入文件成功';

	# 更新rsa公私钥
	def __update_rsa_key__(self):
		try:
			self.__generate_rsa_key__(self.rsa_len);
			print u'\t\t更新成功\n\t\t请删除原先的公钥与私钥,防止别人偷窥！！';
			print u'\t\t重新加密中';
		except:
			print u'\t\t更新失败！！！';

		raw_input(u'\t\tpress enter to back');

	# 退出系统并删除私钥文件和明文文件
	def __exit_system__(self):
		while True:
			if os.path.isfile(self.pwd_file)\
			or os.path.isfile(self.rsa_private_file):	
				print u'\t\t是否删除本目录下的明文文件和密钥文件?',
				x = raw_input('(y/n)');
				if x.lower() == 'y':
					os.remove(self.pwd_file);
					os.remove(self.rsa_private_file);
					print u'\t\t文件删除成功';
					break;
				elif x.lower() == 'n':
					break;
			else:
				break;
		print u'\t\t退出系统';
		raw_input(u'\t\tpress enter to exit');
		sys.exit();


if __name__ == '__main__':
	
	parser = optparse.OptionParser(usage='manager your password');
	parser.add_option('-i','--install',dest='install',\
		default=False,action='store_true',\
		help='generate initial rsa keys');
	(options,args) = parser.parse_args();

	pwd = Password(options.install,4,1024);
	