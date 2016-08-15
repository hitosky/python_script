#!/usr/bin/python
#-*- coding:utf-8 -*-

import os,sys,re;

#显示使用信息
def showUsage():
    print 'Usage:';
    print ' ./find_param.py -f [filename|directory] -p [param]'
    print '                 -f [filename|directory]:the file or directory you look in'
    print '                 -p [param] : the word you look for'
    print '                 -a : totally match the param '

#显示错误信息
def showError(err):
    paramError = 'no parameter input';
    fileError1 = 'no such file or directory';
    fileError2 = 'no file or directory input';
    if err == 0:
        showUsage();    
    elif err == 1:
        print paramError;
    elif err == 2:
        print fileError1;  
    elif err == 3:
        print fileError2;
    else:
        print 'unknown error';

#处理输入参数 
def processParams():
   params = sys.argv[1:];
   if len(params) == 0:
      showError(0); 
      return;
   parampos = params.index('-p');
   filename = './';
   # 没有输入-p或者-p的参数
   if '-p' not in params or parampos >= len(params)-1:
      showError(1);
      return;
   parameter = params[parampos+1];
   # 输入 -f 后没有输入具体的文件或路径
   if '-f' in params: 
       filepos = params.index('-f');
       if filepos >= len(params)-1 or params[filepos+1].find('-')>-1:
           showError(3);
           return;
       filename = params[filepos+1];

   # 输入的文件或路径不存在
   if os.path.exists(filename) is False:
       showError(2);
       return; 
   totalmatch = '-a' in params;
   return [filename,parameter,totalmatch];

# 从文件中查找参数
def findParam(filename,param,totalmatch=False):
    if os.path.isfile(filename):
        num = 0;
        with open(filename,'r') as f:
            for line in f.readlines():
                if (totalmatch is False and line.find(param)>-1) or \
                   (totalmatch and re.search('^\W?'+param+'\W$',line)):
                    num = num+1;
                    if num == 1:
                        print 'in file:%s' %filename;
                    print 'line %d : %s'  %(num,line.replace('\n',''));
                          
    else:
        files = os.listdir(filename);
        for f in files:
            f = filename+'/'+f;
            findParam(f,param,totalmatch);

if __name__ == '__main__':
    
    file_para = processParams();
    if file_para is not None:
        findParam(file_para[0],file_para[1],file_para[2]);
