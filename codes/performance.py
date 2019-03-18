# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 23:13:41 2019

@author: Administrator
"""

mainpath = 'I:/stockautomation/'
path = mainpath + 'codes'
pathworkfile = mainpath + 'workfiles'
pathplot = mainpath + 'plots'
pathoutput = mainpath + 'output'


import numpy as np
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
import os
import time
import datetime
from wordcloud import WordCloud


os.chdir(path)
warnings.filterwarnings("ignore")
from gongshi import *


#from jqdatasdk import *
#auth('18515119438','XSJxsj19940308')
#everything = get_all_securities(types=[], date=None)
#everything.to_csv(path+"/everything.csv",encoding = "utf-8-sig")


#getdata
#name_code = pd.read_csv(path+"/name_code.csv", header = None)
#name_code.columns= ["code","name"]
#name_code['code_num']='haha'

#for i in range(name_code.shape[0]):
#    name_code['code_num'][i] = name_code['code'][i][:6]
#    if i%100 == 0:
#        print(i)
#name_code.to_excel("name_code_num.xlsx")

name_code_new = pd.read_excel(pathworkfile + "/name_code_num.xlsx", dtype = {'code_num':str})
name_code_new = name_code_new[['code_num','name']]

#code, name = '000001', "平安银行"

today = datetime.datetime.today().strftime('%Y-%m-%d')
sixtydaysb4 = datetime.date.today() - datetime.timedelta(60)
sixtydaysb4 = sixtydaysb4.strftime('%Y-%m-%d')



dataallkdj = pd.read_csv(pathworkfile + "/dataallkdj"+ today +".csv",index_col=0)
dataallmacd = pd.read_csv(pathworkfile+"/dataallmacd"+ today +".csv",index_col=0)


goldenx = findgoldenx(dataallkdj,dataallmacd)
print("goldenx find", goldenx)


performace_report = ts.get_report_data(2018,4)

performace_report_rp = performace_report[['code','roe','profits_yoy']]

report = pd.merge(performace_report_rp, pd.DataFrame(goldenx),  left_on='code', right_on=0 )



 for code in goldenx:
     print(code)
     in01, = np.where(performace_report_roe['code'] == code)
     in01 = in01.tolist()
     print(performace_report_roe['roe'][in01])



 for code in goldenx:
     print(code)
     in01, = np.where(performace_report_profits_yoy['code'] == code)
     in01 = in01.tolist()
     print(performace_report_profits_yoy['profits_yoy'][in01])
     
     
     
     
     
     
     