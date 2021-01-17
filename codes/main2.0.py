"""
Created on Thu Jan 14 19:33:47 2021

@author: sijian
"""

import os
mainpath = r'E:\stockautomation-master'
path = os.path.join(mainpath,'codes')
werk = os.path.join(mainpath,'workfiles')
plot = os.path.join(mainpath,'plots')
output = os.path.join(mainpath,'output')

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
import time
import datetime
from jqdatasdk import *

os.chdir(path)
warnings.filterwarnings("ignore")
from gongshi import *

def vc_good(df, label="a", digit=2):
  if isinstance(df, pd.DataFrame):
    c = df[label].value_counts(dropna=False)
    p = df[label].value_counts(dropna=False, normalize=True).mul(100).round(digit).astype(str) + '%'
    print(pd.concat([c,p], axis=1, keys=['counts', '%']))
  elif isinstance(df, pd.Series):
    c = df.value_counts(dropna=False)
    p = df.value_counts(dropna=False, normalize=True).mul(100).round(digit).astype(str) + '%'
    print(pd.concat([c,p], axis=1, keys=['counts', '%']))
  else:
    raise ValueError("check input type!")
    
# auth('18515119438','XSJxsj19940308')

# is_auth = is_auth()
# print(is_auth)

# get_query_count()


# start settings
# everything = get_all_securities()
# print(everything.shape)
# reference = everything.copy()
# reference.reset_index(inplace=True)
# reference['code'] = reference['index'].str[:6]
# reference['shang/shen'] = reference['index'].str[7:]
# vc_good(reference, label="shang/shen")
#       counts       %
# XSHE    2404  56.51%
# XSHG    1850  43.49%

# reference.loc[reference["shang/shen"] == "XSHG","ss1"] = "0" 
# reference.loc[reference["shang/shen"] == "XSHE","ss1"] = "1" 
# reference["url_code"] = reference["ss1"] + reference["code"]
# reference.to_csv(os.path.join(werk,'reference.txt'),sep = "\t",index=False)

converters={'code': lambda x: str(x),
            "url_code": lambda x: str(x),
            "ss1": lambda x: str(x)
            }

reference = pd.read_csv(os.path.join(werk,'reference.txt'),sep = "\t",converters=converters)
print(reference.dtypes)

today = datetime.datetime.today().strftime('%Y%m%d')
sixtydaysb4 = datetime.date.today() - datetime.timedelta(60)
sixtydaysb4 = sixtydaysb4.strftime('%Y%m%d')
yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime('%Y%m%d')

# get raw data            
def get_data2(code=None,file=None,start_date=None,end_date=None):
    """
    Parameters
    ----------
    code : string
        the stock code that need to be filled to get data.
    file : TYPE
        temp file for keeping structure use, not important, keep fixed
    start_date : string
    end_date : string
        load data from start_date to end_date
    Returns
    -------
    output : dataframe
        get data from wangyi API, might have some invalid data
        will remove the header and only retrieve the data value
        output it to a csv and then read it back to keep the structure.

    """
    url = "http://quotes.money.163.com/service/chddata.html?code=" + code + "&start="+start_date + "&end=" + end_date + "&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER"
    
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    r=requests.get(url,headers=headers)
    r.encoding = "gbk"
    if r.status_code == 200:
        text = r.text.replace('\r\n',"\n").replace("日期,股票代码,名称,收盘价,最高价,最低价,开盘价,前收盘,涨跌额,涨跌幅,成交量,成交金额\n","")        
        with open(os.path.join(werk,file),"w", encoding='utf-8-sig') as f:
            f.write(text)
        try:
            output = pd.read_csv(file,header=None)
            return output
        except:
            pass
    else:
        print("cannot get data of {}".format(code))

def data_add_features(data=None):
    """
    Parameters
    ----------
    data : dataframe, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    datawall : dataframe
        with macd, kdj, boll, etc.

    """
    if isinstance(data,type(None)):
        pass
    else:
        if data.isna().sum().sum() != 0:
            data.dropna(inplace=True)
        data.columns = ['date', 'code', 'name', 'close', 'high', 'low', 'open', 'prev_close', 'close_diff', 'close_diff/prev_close','trading_size', 'trans_qty']
        data.sort_values("date",inplace=True)
        data.reset_index(inplace=True,drop=True)
        data_macd = macd(data, n=12, m=26, k=9).drop('date',axis = 1)
        data_kdj = kdj(data).drop('date',axis = 1)
        data_boll = boll(data).drop('date',axis = 1)
        frames = [data, data_macd,data_kdj,data_boll]
        datawall = pd.concat(frames, axis = 1)
        return datawall

def kdjinfo(dataframe,name):

    if isinstance(dataframe,type(None)):
        pass
    else:
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

#plot macd

def macdinfo(dataframe,name):
    if isinstance(dataframe,type(None)):
        pass
    else:
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
        return date_macd_flag


def findgoldenx(dataframe, dataframe1):
    dataframe = dataframe.dropna(axis = 1)     
    dataframe = dataframe.tail(5).T
    dataframe = dataframe.replace('kdj金叉',1)
    dataframe = dataframe.replace('kdj死叉',-2)
    dataframe = dataframe.replace('无',0)

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


a = time.time()
whole_data_frame = []
dataallkdj = pd.DataFrame()
dataallmacd = pd.DataFrame()

for i in range(reference.shape[0]):
# for i in range(30):
    code = reference["url_code"][i]
    code1 = code[1:]
    if i%100 == 0:
        print("process to {}th, {} in total".format(i,reference.shape[0]))
    # print(i)
    data=get_data2(code=code, file=os.path.join(werk, "temp.csv"),start_date=sixtydaysb4,end_date=today)
    data_w_feature = data_add_features(data=data)
    whole_data_frame.append(data_w_feature)
    # find kdj/macd X
    
    data_kdj = kdjinfo(data_w_feature,code1)
    data_macd = macdinfo(data_w_feature,code1)
    
    if isinstance(data_kdj,type(None)):
        continue
    else: 
        dataallkdj[i] = data_kdj[code1]
        dataallkdj = dataallkdj.rename(columns={i:reference["url_code"][i]})
    
    if isinstance(dataallmacd,type(None)):
        continue
    else: 
        dataallmacd[i] = data_macd[code1]
        dataallmacd = dataallmacd.rename(columns={i:reference["url_code"][i]})

    
whole_data_frame1 = pd.concat(whole_data_frame)
whole_data_frame1.sort_values(by = ["code","date"],inplace=True)
b=time.time()
print("running time: {}min".format(round((b-a)/60,2)))

# whole_data_frame1.to_csv(os.path.join(werk,"whole_data.csv"),encoding="utf-8-sig")

whole_data_frame1.reset_index(inplace=True, drop=True)
 
dataallkdj.index = whole_data_frame1.date.unique().tolist()
dataallmacd.index = whole_data_frame1.date.unique().tolist()

dataallkdj.to_csv(os.path.join(werk,"dataallkdj"+ today +".csv"),encoding = "utf-8-sig")
dataallmacd.to_csv(os.path.join(werk,"dataallmacd"+ today +".csv"),encoding = "utf-8-sig")

# dataallkdj=pd.read_csv(os.path.join(werk,"dataallkdj"+ today +".csv"),encoding = "utf-8-sig")
# dataallmacd=pd.read_csv(os.path.join(werk,"dataallmacd"+ today +".csv"),encoding = "utf-8-sig")

# dataallkdj = dataallkdj.drop('Unnamed: 0',axis=1)
# dataallmacd = dataallmacd.drop('Unnamed: 0',axis=1)


goldenx = pd.DataFrame(findgoldenx(dataallkdj,dataallmacd))
goldenx["code"] = goldenx[0].str[1:]
goldenx = goldenx.merge(reference[["code","display_name"]], how="left",on="code")
goldenx = goldenx[["code","display_name"]]


for column in goldenx.columns:
    goldenx[column] = goldenx[column].astype('str')
    
print(goldenx.display_name.tolist())
goldenx.to_csv(os.path.join(output,"goldenx"+today+".txt"),encoding="utf-8-sig")



# get industry information
# data = pd.read_csv("E:\stockautomation-master\output\goldenx20210118.txt", index_col='Unnamed: 0')
# reference = pd.read_csv(os.path.join(werk,'reference.txt'),sep = "\t",converters=converters)

def get_industry(export="Y",data=None,reference=None):
    auth('18515119438','XSJxsj19940308')
    data1 = data.merge(reference[["index","display_name"]], how="left", on ="display_name")
    temp =[]
    for i in range(len(data1["index"])):
    # for i in range(10):
        industry_info = get_industry(data1["index"][i], date=datetime.datetime.today().strftime('%Y-%m-%d'))
        industry_info1 = pd.DataFrame(industry_info).T
        # print(industry_info1)
        temp.append(industry_info1)
        # print(temp)
        
    industry_info_final = pd.concat(temp)
    industry_info_final.reset_index(inplace=True)
    industry_info_final1 = industry_info_final.merge(data1[["index","display_name"]], how="left", on="index")
    if export=="Y":
        industry_info_final1.to_csv(os.path.join(output,"industry_info_"+today+".csv"),encoding="utf-8-sig")


get_industry(export="Y",data=goldenx,reference=reference)












