import pandas as pd
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random

def opmonth():
    driver = webdriver.PhantomJS()
    driver.get('http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx')
    driver.get('http://info512.taifex.com.tw/Future/OptQuote_Norl.aspx')

    selectbox = webdriver.support.ui.Select(driver.find_element_by_name('ctl00$ContentPlaceHolder1$ddlFusa_SelMon'))
    selectbox.all_selected_options
    [sel.text for sel in selectbox.options]
    selectbox.select_by_value([sel.text for sel in selectbox.options][1])
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"lxml")

    table = pd.read_html(str(soup.select('#divDG')[0]))[0]

    Call = table.loc[:,:6]
    Put = table.loc[:,6:]
    Call.columns = ['Buy','Sell','Price','Up_Down','Total_Vol','Time','S']
    Call = Call[1:]
    Put.columns = ['S','Buy','Sell','Price','Up_Down','Total_Vol','Time']
    Put = Put[1:]
    def Vol_conversion(input_ele):
        if input_ele == '--':
            return 0
        if input_ele!= '--':
            return int(''.join(input_ele.split(',')))
    def mon_float(input_ele):
        if input_ele == '--':
            return None
        if input_ele!= '--':
            return float(''.join(input_ele.split(',')))
    Call['Total_Vol'] = Call['Total_Vol'].map(Vol_conversion)
    Put['Total_Vol'] = Put['Total_Vol'].map(Vol_conversion)
    Call['Price'] = Call['Price'].map(mon_float)
    Put['Price'] = Put['Price'].map(mon_float)
    Call['S']=Call['S'].map(lambda x:int(x))
    Put['S']=Put['S'].map(lambda x:int(x))
    comp = np.array(Call['S'].tolist())+np.array(Call['Price'].tolist())-np.array(Put['Price'].tolist())
    Call['Combo'] = pd.Series(comp,index=Call.index)
    Put['Combo'] = pd.Series(comp,index=Put.index)
    def EV(Spot_price,Strike_price):
        if Spot_price-Strike_price>0:
            return Spot_price-Strike_price
        else:
            return 0
    Call['Int_value'] = Call.apply(lambda row: EV(row['Combo'],row['S']),axis=1)
    Put['Int_value'] = Put.apply(lambda row: EV(row['Combo'],row['S']),axis=1)
    Call['Time_value'] = Call.apply(lambda row: row['Price']-row['Int_value'] if row['Price']!= 0 else 0,axis=1)
    Put['Time_value'] = Put.apply(lambda row: row['Price']-row['Int_value'] if row['Price']!= 0 else 0,axis=1)
    driver = webdriver.PhantomJS()
    driver.get('http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx?d=080585')
    #先抓出現貨價格
    soup = BeautifulSoup(driver.page_source,'lxml')
    Spot_information = pd.read_html(str(soup.select('#divDG')[0]),header=0)[0].loc[0:0]
    #給定期交所上的保證金A值以及B值
    #賣出買權/賣出CALL : 權利金市值+MAXIMUM(A值-價外值，B值)
    #賣出賣權/賣出PUT : 權利金市值+MAXIMUM(A值-價外值，B值)
    A = 22000
    B = 11000
    S = float(Spot_information.iat[0,6])
    spread1 = S-Call['S']
    spread2 = Put['S']-S
    Call["S-K"]=np.nan
    for i in range(1,len(Call)):
        if spread1[i] > 0:
            Call.loc[i,"S-K"] = spread1[i] 
        else:
            Call.loc[i,"S-K"] = 0
    Call['Margin']=np.nan
    for i in range (1,len(Call)):
        Call.loc[i,'Margin'] = Call.loc[i,'Price']*50 + max(A-Call.loc[i,"S-K"],B)
    Put["S-K"]=np.nan
    for i in range(1,len(Put)):
        if spread2[i] > 0:
            Put.loc[i,"S-K"] = spread2[i] 
        else:
            Put.loc[i,"S-K"] = 0 
    Put['Margin']=np.nan
    for i in range (1,len(Put)):
        Put.loc[i,'Margin'] = Put.loc[i,'Price']*50 + max(A-Put.loc[i,"S-K"],B)
    at_the_money = Call['S'] + Call['Price'] - Put['Price']
    difference = at_the_money - Call['S']
    df = pd.concat([at_the_money,Call['S'],Call['Price']*50,Call['Margin'],Put['Price']*50,Put['Margin']],axis = 1)
    df.columns= ['K+C-P', 'Exercise_Price', 'Premium_Call', 'Margin_Call', 'Premium_Put', 'Margin_Put']
    return df



def opweek():
    driver = webdriver.PhantomJS()
    driver.get('http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx')
    driver.get('http://info512.taifex.com.tw/Future/OptQuote_Norl.aspx')

    selectbox = webdriver.support.ui.Select(driver.find_element_by_name('ctl00$ContentPlaceHolder1$ddlFusa_SelMon'))
    selectbox.all_selected_options
    [sel.text for sel in selectbox.options]
    selectbox.select_by_value([sel.text for sel in selectbox.options][0])
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source,"lxml")

    table = pd.read_html(str(soup.select('#divDG')[0]))[0]

    Call = table.loc[:,:6]
    Put = table.loc[:,6:]
    Call.columns = ['Buy','Sell','Price','Up_Down','Total_Vol','Time','S']
    Call = Call[1:]
    Put.columns = ['S','Buy','Sell','Price','Up_Down','Total_Vol','Time']
    Put = Put[1:]
    def Vol_conversion(input_ele):
        if input_ele == '--':
            return 0
        if input_ele!= '--':
            return int(''.join(input_ele.split(',')))
    def mon_float(input_ele):
        if input_ele == '--':
            return None
        if input_ele!= '--':
            return float(''.join(input_ele.split(',')))
    Call['Total_Vol'] = Call['Total_Vol'].map(Vol_conversion)
    Put['Total_Vol'] = Put['Total_Vol'].map(Vol_conversion)
    Call['Price'] = Call['Price'].map(mon_float)
    Put['Price'] = Put['Price'].map(mon_float)
    Call['S']=Call['S'].map(lambda x:int(x))
    Put['S']=Put['S'].map(lambda x:int(x))
    comp = np.array(Call['S'].tolist())+np.array(Call['Price'].tolist())-np.array(Put['Price'].tolist())
    Call['Combo'] = pd.Series(comp,index=Call.index)
    Put['Combo'] = pd.Series(comp,index=Put.index)
    def EV(Spot_price,Strike_price):
        if Spot_price-Strike_price>0:
            return Spot_price-Strike_price
        else:
            return 0
    Call['Int_value'] = Call.apply(lambda row: EV(row['Combo'],row['S']),axis=1)
    Put['Int_value'] = Put.apply(lambda row: EV(row['Combo'],row['S']),axis=1)
    Call['Time_value'] = Call.apply(lambda row: row['Price']-row['Int_value'] if row['Price']!= 0 else 0,axis=1)
    Put['Time_value'] = Put.apply(lambda row: row['Price']-row['Int_value'] if row['Price']!= 0 else 0,axis=1)
    driver = webdriver.PhantomJS()
    driver.get('http://info512.taifex.com.tw/Future/FusaQuote_Norl.aspx?d=080585')
    #先抓出現貨價格
    soup = BeautifulSoup(driver.page_source,'lxml')
    Spot_information = pd.read_html(str(soup.select('#divDG')[0]),header=0)[0].loc[0:0]
    #給定期交所上的保證金A值以及B值
    #賣出買權/賣出CALL : 權利金市值+MAXIMUM(A值-價外值，B值)
    #賣出賣權/賣出PUT : 權利金市值+MAXIMUM(A值-價外值，B值)
    A = 22000
    B = 11000
    S = float(Spot_information.iat[0,6])
    spread1 = S-Call['S']
    spread2 = Put['S']-S
    Call["S-K"]=np.nan
    for i in range(1,len(Call)):
        if spread1[i] > 0:
            Call.loc[i,"S-K"] = spread1[i] 
        else:
            Call.loc[i,"S-K"] = 0
    Call['Margin']=np.nan
    for i in range (1,len(Call)):
        Call.loc[i,'Margin'] = Call.loc[i,'Price']*50 + max(A-Call.loc[i,"S-K"],B)
    Put["S-K"]=np.nan
    for i in range(1,len(Put)):
        if spread2[i] > 0:
            Put.loc[i,"S-K"] = spread2[i] 
        else:
            Put.loc[i,"S-K"] = 0 
    Put['Margin']=np.nan
    for i in range (1,len(Put)):
        Put.loc[i,'Margin'] = Put.loc[i,'Price']*50 + max(A-Put.loc[i,"S-K"],B)
    at_the_money = Call['S'] + Call['Price'] - Put['Price']
    difference = at_the_money - Call['S']
    df = pd.concat([at_the_money,Call['S'],Call['Price']*50,Call['Margin'],Put['Price']*50,Put['Margin']],axis = 1)
    df.columns= ['K+C-P', 'Exercise_Price', 'Premium_Call', 'Margin_Call', 'Premium_Put', 'Margin_Put']
    return df

def triangle(df):
    diff=df['K+C-P']-df['Exercise_Price']
    diff=abs(diff)
    diff.min(skipna=True)

    loc=abs(diff)==diff.min(skipna=True)
    loc=list(loc)
    loc=loc.index(1)
    df2=df[(loc):(loc+1)]
    long_call=df2['Premium_Call'].iloc[0]
    long_put=df2['Premium_Put'].iloc[0]

    money_need=long_call+long_put
    return money_need


def square(df):
    diff=df['K+C-P']-df['Exercise_Price']
    diff=abs(diff)
    diff.min(skipna=True)

    loc=abs(diff)==diff.min(skipna=True)
    loc=list(loc)
    loc=loc.index(1)
    data=df[(loc-2):(loc+3)]
    long_low_put=data['Premium_Put'].iloc[1]
    long_high_call=data['Premium_Call'].iloc[4]

    money_need=long_low_put+long_high_call
    return money_need
    


def bullish_spread(df):
    diff=df['K+C-P']-df['Exercise_Price']
    diff=abs(diff)
    diff.min(skipna=True)

    loc=abs(diff)==diff.min(skipna=True)
    loc=list(loc)
    loc=loc.index(1)
    data=df[(loc-2):(loc+3)]
    long_low_call=data['Premium_Call'].iloc[0]
    long_low_call_K=data['Exercise_Price'].iloc[0]

    short_high_call=data['Premium_Call'].iloc[4]
    short_high_call_K=data['Exercise_Price'].iloc[4]
    short_high_call_margin=data['Margin_Call'].iloc[4]

    Premium_cost=round(long_low_call)
    Premium_cost_K=round(long_low_call_K)
    Premium_rev=round(short_high_call)
    Premium_rev_K=round(short_high_call_K)
    return [Premium_cost_K,Premium_cost,Premium_rev_K,Premium_rev,short_high_call_margin]


def bearish_spread(df):
    diff=df['K+C-P']-df['Exercise_Price']
    diff=abs(diff)
    diff.min(skipna=True)

    loc=abs(diff)==diff.min(skipna=True)
    loc=list(loc)
    loc=loc.index(1)
    data=df[(loc-2):(loc+3)]
    long_high_call=data['Premium_Call'].iloc[4]
    long_high_call_K=data['Exercise_Price'].iloc[4]

    short_low_call=data['Premium_Call'].iloc[0]
    short_low_call_K=data['Exercise_Price'].iloc[0]
    short_low_call_margin=data['Margin_Call'].iloc[0]

    Premium_cost=round(long_high_call)
    Premium_cost_K=round(long_high_call_K)

    Premium_rev=round(short_low_call)
    Premium_rev_K=round(short_low_call_K)

    money_need=long_high_call+short_low_call_margin
    return [Premium_cost_K,Premium_cost,Premium_rev_K,Premium_rev,short_low_call_margin]


def good_word():
    a=random.randint(0,4)
    list=["股票不是漲，就是跌",
          "年輕人不要計較薪水比別人低",
          "年輕人不要怪政府，要想辦法彌補自己不足的地方",
          "年輕人剛出社會就想擁有房子很奇怪",
          "共體時艱，年輕人要懂的吃苦"]
    return list[a]


