# -*- coding:utf-8 -*-
'''
功能：
删除clear_file.py所在目录下的
所有临时文件和空文件夹
'''

import os;
import re;

work_dir = os.getcwd();
#windows下临时文件后缀
EXT = [".\.tmp",".\.TMP"];
file_num = 0;
doc_num = 0;
def clear_file(path):
	global file_num;
	global doc_num;  
	for f in os.listdir(path):
		file_path = os.path.join(path,f);
		if os.path.isdir(file_path):
			clear_file(file_path);
			#清除空文件夹
			if len(os.listdir(file_path))==0:
				print "DELETE %s:empty document"%file_path;
				doc_num = doc_num+1;
				os.rmdir(file_path);
		#清除大小为0的文件	
		elif os.path.getsize(file_path) ==0:
			print "DELETE %s:empty file" %file_path;
			file_num = file_num+1;
			os.remove(file_path);
		#清除临时文件
		else:
			for ext in EXT:
				if re.search(ext,f) is not None:
					print "DELETE %s:temp file" %file_path;
					file_num = file_num+1;
					os.remove(file_path);

if __name__ == '__main__':
	print "%s to clear"%work_dir;

	print "Start clearing"
	clear_file(work_dir);
	print "Completed\n";
	print "totally delete %d files" %file_num;
	print"totally delete %d documents" %doc_num;
	raw_input("Enter to quit");