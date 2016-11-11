#!/usr/bin/env python
# coding:utf8
'''
根据候选字符产生随机长度的随机密码,
支持aes,rsa加解密
'''
import math,sys,random,base64,os;
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Cipher import AES
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from binascii import b2a_hex, a2b_hex

# 密码候选字符串，也可以自定义
PWD = '''
`1234567890~!@#$%^&*()-=_+[];'\,./{}:"|<>?qwertyuioplkjhgfdsazxcvbnmMNBVCXZQAWSEDRFTGYHUJIKOLP
'''
PWD = PWD[1:-1];   #去掉前后换行符

# 获取随机或者指定长度的随机密码
def generate_random_pwd(spwd=PWD,pwd_len=None):
	if pwd_len is None:
		pwd_len = int(random.random()*6)+7
	pwd = '';
	for i in range(0,pwd_len):
		index = int(random.random()*len(spwd));
		pwd = pwd + spwd[index];
	return pwd;

# aes的加密
def aes_encrypt(text,key,mode=AES.MODE_CBC):
	aes = AES.new(key,mode,key);
	bs = AES.block_size;
	# 将明文用'\0'填充至bs长度
	pad = lambda s:s+(bs-len(s)%bs)*'\0';
	cipher_text = aes.encrypt(pad(text));
	# cipher_text为二进制字符串，将其转换为16进制
	return b2a_hex(cipher_text);

# aes的解密
def aes_decrypt(cipher_text,key,mode=AES.MODE_CBC):
	aes = AES.new(key,mode,key);
	bs = AES.block_size;
	text = aes.decrypt(a2b_hex(cipher_text));

	return text.rstrip('\0');

# rsa加密
def rsa_encrypt(text,public_key):
	rsa_key = RSA.importKey(public_key);
	cipher = Cipher_pkcs1_v1_5.new(rsa_key);
	cipher_text = base64.b64encode(cipher.encrypt(text));
	return cipher_text;

# rsa解密
def rsa_decrypt(cipher_text,private_key):
	random_generator = Random.new().read;
	rsa_key = RSA.importKey(private_key);
	cipher = Cipher_pkcs1_v1_5.new(rsa_key);
	text = cipher.decrypt(base64.b64decode(cipher_text),random_generator);
	return text;


