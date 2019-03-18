# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 10:15:34 2019

@author: sijian.xuan
"""
mainpath = 'I:/jointquantnew/'
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

def get_data(code):
    data = ts.get_hist_data(code,start=sixtydaysb4 ,end = today)

    data.reset_index(inplace = True)
    data = data.sort_values(by = 'date')
    data.reset_index(inplace = True, drop = True)
         
    data_macd = macd(data, n=12, m=26, k=9).drop('date',axis = 1)
    data_kdj = kdj(data).drop('date',axis = 1)
    data_boll = boll(data).drop('date',axis = 1)
    #data_boll = data_boll.fillna(0)
        
    frames = [data, data_macd,data_kdj,data_boll]
    datawall = pd.concat(frames, axis = 1)
    
    return datawall

#data = get_data(code)
#data.head()

def kdjinfo(dataframe,name):


    
    #find kdj information
    find_cross_kdj_df = dataframe[['date','k','d','j']]
    find_cross_kdj_df['k-j'] = find_cross_kdj_df['k'] - find_cross_kdj_df['j']
    find_cross_kdj_df['k-j_shift']  = find_cross_kdj_df['k-j'].shift()
    find_cross_kdj_df['mul'] = find_cross_kdj_df['k-j']*find_cross_kdj_df['k-j_shift']
    
    
    find_cross_kdj_df[name] = '无'
    in01, = np.where((find_cross_kdj_df['mul'] < 0) & (find_cross_kdj_df['k-j_shift'] < 0))
    in01 = in01.tolist()
    find_cross_kdj_df[name][in01] = 'kdj死叉'
    
    in02, = np.where((find_cross_kdj_df['mul'] < 0) & (find_cross_kdj_df['k-j_shift'] > 0))
    in02 = in02.tolist()
    find_cross_kdj_df[name][in02] = 'kdj金叉'
    
    date_kdj_flag = find_cross_kdj_df[['date',name]]
#    date_kdj_flag.to_csv(path + "/date_kdj_flag_"+name+".csv", encoding = "utf-8-sig")
    return date_kdj_flag

#data_kdj = kdj(data,name)
#data_kdj_warning = data_kdj[data_kdj[name] !='无']



#plot macd

def macdinfo(dataframe,name):


    
    #find macd information
    find_cross_macd_df = dataframe[['date','diff','dea']]
    find_cross_macd_df['diff-dea'] = find_cross_macd_df['diff'] - find_cross_macd_df['dea']
    find_cross_macd_df['diff-dea_shift']  = find_cross_macd_df['diff-dea'].shift()
    find_cross_macd_df['mul'] = find_cross_macd_df['diff-dea']*find_cross_macd_df['diff-dea_shift']
    
    
    find_cross_macd_df[name] = '无'
    in01, = np.where((find_cross_macd_df['mul'] < 0) & (find_cross_macd_df['diff-dea'] < 0))
    in01 = in01.tolist()
    find_cross_macd_df[name][in01] = 'macd死叉'
    
    in02, = np.where((find_cross_macd_df['mul'] < 0) & (find_cross_macd_df['diff-dea'] > 0))
    in02 = in02.tolist()
    find_cross_macd_df[name][in02] = 'macd金叉'
    
    date_macd_flag = find_cross_macd_df[['date',name]]
#    date_macd_flag.to_csv(path + "/date_macd_flag_"+name+".csv", encoding = "utf-8-sig")
    return date_macd_flag
#
#data_macd = macdinfo(data,name)
#data_macd_warning = data_macd[data_macd[name] !='无']

def findgoldenx(dataframe, dataframe1):
    dataframe = dataframe.dropna(axis = 1)     
    dataframe = dataframe.tail(5).T
    dataframe = dataframe.replace('kdj金叉',1)
    dataframe = dataframe.replace('kdj死叉',-2)
    dataframe = dataframe.replace('无',0)
    
#    dataframe1  = dataframe.T
    dataframe['sum'] = dataframe.sum(axis = 1)
    dataframe = dataframe[dataframe['sum']>0]
    dataframe.reset_index(inplace = True)
    kdjlist = dataframe['index']
    
    dataframe1 = dataframe1.dropna(axis = 1)
    dataframe1 = dataframe1.tail(5).T
    dataframe1 = dataframe1.replace('macd金叉',1)
    dataframe1 = dataframe1.replace('macd死叉',-2)
    dataframe1 = dataframe1.replace('无',0)
    
    dataframe1['sum'] = dataframe1.sum(axis = 1)
    dataframe1 = dataframe1[dataframe1['sum']>0]
    dataframe1.reset_index(inplace = True)
    macdlist = dataframe1['index']
    
    result = pd.Series(list(set(kdjlist).intersection(set(macdlist))))

    return result



"""
call functions
"""
dataallkdj = pd.DataFrame()
dataallmacd = pd.DataFrame()

time1 = time.time()
for i in range(name_code_new.shape[0]):
#for i in range(2240,2245):
#for i in range(5):
    code, name = name_code_new['code_num'][i],name_code_new['name'][i]
#    print(code)
#    print(name)
    
    try:
        data = get_data(code)
#    print(data.head())
    except:
        print(name)
        print("this is not good")
        continue
    #kdj info
    else:
        data_kdj = kdjinfo(data,code)
    #    data_kdj_warning = data_kdj[data_kdj[name] !='无']
        
        #macd info    
        data_macd = macdinfo(data,code)
    #    data_macd_warning = data_macd[data_macd[name] !='无']
    
        dataallkdj[i] = data_kdj[code]
        dataallkdj = dataallkdj.rename(columns={i:code})
        
        dataallmacd[i] = data_macd[code]
        dataallmacd = dataallmacd.rename(columns={i:code})
    
        if i%100 == 0:
            print(i)
            
print("finished! time used:")
time2 = time.time()
print(time2-time1)



temp = get_data("000001")
datecol = temp['date']

dataallkdj.index = datecol
dataallmacd.index = datecol

dataallkdj.to_csv(pathworkfile + "/dataallkdj"+ today +".csv",encoding = "utf-8-sig")
dataallmacd.to_csv(pathworkfile + "/dataallmacd"+ today +".csv",encoding = "utf-8-sig")


#dataallkdj = pd.read_csv(pathworkfile + "/dataallkdj"+ today +".csv",index_col=0)
#dataallmacd = pd.read_csv(pathworkfile+"/dataallmacd"+ today +".csv",index_col=0)


goldenx = findgoldenx(dataallkdj,dataallmacd)
print("goldenx find", goldenx)

goldenx.to_csv(pathworkfile + "/goldenx"+today+".csv")

for code in goldenx:
#        plot kdj
    dataframe = get_data(code)
    x = dataframe['date']
    xi = [i for i in range(0, len(x))]
        
    fig, ax = plt.subplots(1,1,figsize=(200,20))
    ax.plot(xi,dataframe['k'], color = 'orange')
    ax.plot(xi,dataframe['d'], color = 'red')
    ax.plot(xi,dataframe['j'], color = 'black')
    ax.grid()
    plt.xticks(xi, x, rotation=45)
    ax.legend()
    #   plt.show()
    plt.savefig(pathplot + '/kdj_'+ code + today +'.png')

#        plot macd
       
    x = dataframe['date']
    xi = [i for i in range(0, len(x))]
    
    y_above = np.zeros(dataframe.shape[0])
    y_below = np.zeros(dataframe.shape[0])

    for i in range(dataframe.shape[0]):
        if dataframe['macd'][i] > 0:
            y_above[i] = dataframe['macd'][i]
        elif dataframe['macd'][i] < 0:
            y_below[i] = dataframe['macd'][i]
        
    fig, ax = plt.subplots(1,1,figsize=(200,20))
    ax.plot(xi,dataframe['diff'], color = 'black')
    ax.plot(xi,dataframe['dea'], color = 'blue')
    ax.bar(xi, y_above, color="red",label="Above average")
    ax.bar(xi, y_below, color="green",label="below average")
    ax.grid()
    plt.xticks(xi, x, rotation=45)
    ax.legend()
    #    plt.show()
    plt.savefig(pathplot + '/macd_'+ code + today +'.png')



#concept classification
class_info = ts.get_concept_classified() 
class_df = pd.DataFrame()
class_df['code'] = goldenx

class_df = pd.merge(class_df,class_info)
class_df.to_csv(pathworkfile + "/classinfo"+today+".csv",encoding = "utf-8-sig")


industry_info = ts.get_industry_classified()
industry_df = pd.DataFrame()
industry_df['code'] = goldenx
 


industry_df = pd.merge(industry_df,industry_info)
industry_df.to_csv(pathworkfile + "/industry_info"+today+".csv",encoding = "utf-8-sig")


# performace_report = ts.get_report_data(2018,3)
# performace_report.to_csv(path+"/performace_report.csv")
# #performace_report = pd.read_csv(path+"/performace_report.csv")
# performace_report_roe = performace_report[['code','roe']]
# performace_report_profits_yoy = performace_report[['code','profits_yoy']]

# for code in goldenx:
#     print(code)
#     in01, = np.where(performace_report_roe['code'] == code)
#     in01 = in01.tolist()
#     print(performace_report_roe['roe'][in01])



# for code in goldenx:
#     print(code)
#     in01, = np.where(performace_report_profits_yoy['code'] == code)
#     in01 = in01.tolist()
#     print(performace_report_profits_yoy['profits_yoy'][in01])

#report
classgroup = class_df.groupby('c_name')
classword = classgroup.size().reset_index().sort_values(by = 0, ascending=False)

industrygroup = industry_df.groupby('c_name')
industryword = industrygroup.size().reset_index().sort_values(by = 0, ascending=False)

classword.to_csv(pathoutput + "/classinfo"+today+".csv",encoding = "utf-8-sig" )
industryword.to_csv(pathoutput + "/industryinfo"+today+".csv",encoding = "utf-8-sig" )



#wordcloud

text = class_df['c_name'].to_string()
wordcloud = WordCloud(font_path='C:\windows\Fonts\simfang.ttf',background_color="white",width=1000, height=860, margin=2).generate(text)

# width,height,margin可以设置图片属性
# generate 可以对全部文本进行自动分词,但是对中文支持不好
# 可以设置font_path参数来设置字体集
#background_color参数为设置背景颜色,默认颜色为黑色

plt.imshow(wordcloud)
plt.axis("off")
plt.show()
wordcloud.to_file(pathoutput+'/class_wordcloud_'+today+'_.png')


text = industry_df['c_name'].to_string()
wordcloud = WordCloud(font_path='C:\windows\Fonts\simfang.ttf',background_color="white",width=1000, height=860, margin=2).generate(text)

# width,height,margin可以设置图片属性
# generate 可以对全部文本进行自动分词,但是对中文支持不好
# 可以设置font_path参数来设置字体集
#background_color参数为设置背景颜色,默认颜色为黑色

plt.imshow(wordcloud)
plt.axis("off")
plt.show()
wordcloud.to_file(pathoutput+'/industry_wordcloud_'+today+'_.png')



   