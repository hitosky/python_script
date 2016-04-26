# -*- coding:utf-8 -*-
'''
说明：
在matplotlib基础上的画图模块
'''
import matplotlib.pyplot as plt;


#设置figure的中文显示
#黑体 	SimHei
#微软雅黑 	Microsoft YaHei
#微软正黑体 	Microsoft JhengHei
#新宋体 	NSimSun
#新细明体 	PMingLiU
#细明体 	MingLiU
#标楷体 	DFKai-SB
#仿宋 	FangSong
#楷体 	KaiTi
#仿宋_GB2312 	FangSong_GB2312
#楷体_GB2312 	KaiTi_GB2312 
def set_ch():
    from pylab import mpl
    mpl.rcParams['font.sans-serif']=['SimHei'] # 指定默认字体
    mpl.rcParams['axes.unicode_minus']=False # 解决保存图像是负号'-'显示为方块的问题 
#画图的曲线
class Plot(object):
	def __init__(self,x=[],y=[],label='',color='black',linestyle='solid',linewidth=1):
		self.xarray=x;
		self.yarray=y;
		self.label=label;
		self.color=color;
		#'solid'实线，'dashed'虚线
		self.linestyle=linestyle;
		self.linewidth=linewidth;
#坐标轴标签属性
class AxisLabel(object):
	def __init__(self,name='axis',fontsize=10):
		self.name=name;
		self.fontsize=fontsize;
#坐标轴上下限
class AxisLim(object):
	def __init__(self,min,max):
		self.min=min;
		self.max=max;
#x,y坐标轴
class Axis(object):
	def __init__(self,label,lim,ticks,rotation=0):
		self.label=label;
		self.lim=lim;
		self.ticks=ticks;
		self.rotation=rotation;
#axe的position
class AxePosition(object):
	def __init__(self,axe,row,column,position):
		self.axe=axe;
		self.row=row;
		self.column=column;
		self.position=position;
#画图
class Draw2DFigure(object):
	#初始化figure,将figure分割为row*column个axe
	def __init__(self,row=1,column=1):
		self.fig=plt.figure();
		self.axes=[];
		for i in range(1,row*column+1):
			self.set_axe_position(row,column,i);
	#设置axe在画布中的位置
	def set_axe_position(self,row,column,position):
		axe=self.fig.add_subplot(row,column,position); 
		self.axes.append(AxePosition(axe,row,column,position));
	#画曲线图
	def draw_plot(self,row,column,position,xaxis,yaxis,pts,title=''):
		for a in self.axes:
			if a.row==row and a.column==column and a.position==position:
				self.__set_xaxis(a.axe,xaxis);
				self.__set_yaxis(a.axe,yaxis);
				a.axe.set_title(title);
				for pt in pts:
					a.axe.plot(pt.xarray,pt.yarray,label=pt.label,
						color=pt.color,linewidth=pt.linewidth,
						linestyle=pt.linestyle);
	#显示最终画图
	#upper right <--> 1
	#upper left <--> 2
	#lower left <--> 3
	#lower right <--> 4
	#right <--> 5
	#center left <--> 6
	#center right <--> 7
	#lower center <--> 8
	#upper center <--> 9
	#center <--> 10
	def show_figure(self,location=1):
		plt.legend(loc=location);
		plt.show();

	#设置axe的x轴
	def __set_xaxis(self,axe,xaxis):
		axe.set_xlabel(xaxis.label.name,fontsize=xaxis.label.fontsize);
		axe.set_xlim(xaxis.lim.min,xaxis.lim.max);
		axe.xaxis.set_ticks(xaxis.ticks);
		if xaxis.rotation!=0:
			rotation=xaxis.rotation;
			for label  in axe.xaxis.get_ticklabels():
				label.set_rotation(rotation);
	#设置axe的y轴
	def __set_yaxis(self,axe,yaxis):
		axe.set_ylabel(yaxis.label.name,fontsize=yaxis.label.fontsize);
		axe.set_ylim(yaxis.lim.min,yaxis.lim.max);
		axe.yaxis.set_ticks(yaxis.ticks);
		if yaxis.rotation!=0:
			rotation=yaxis.rotation;
			for label  in axe.yaxis.get_ticklabels():
				label.set_rotation(rotation);
	
