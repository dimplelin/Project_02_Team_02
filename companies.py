import pandas as pd
import numpy as np
import MyMod
from flask import Flask
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import re
import time
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *



app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])



@app.route('/')
def index():
    message = """Hello, My Friends!"""
    return message

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

@app.route('/op')
def op():
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

    return table.to_html()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)

#簡單訊息測試   
    if event.message.text == "hello":
        list=['嗶——',"歡迎使用選擇權自動裝置","本裝置提供的資訊是從網頁即時抓取，請耐心等候","使用服務請輸入「服務」"]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='\n\n'.join(list)))
    if event.message.text == "嗨":
        list=['嗶——',"歡迎使用選擇權自動裝置","本裝置提供的資訊是從網頁即時抓取，請耐心等候","使用服務請輸入「服務」"]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='\n\n'.join(list)))
    if event.message.text == "你好":
        list=['嗶——',"歡迎使用選擇權自動裝置","本裝置提供的資訊是從網頁即時抓取，請耐心等候","使用服務請輸入「服務」"]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='\n\n'.join(list)))                

    
#服務選單
    if event.message.text == "服務":
        buttons_template = TemplateSendMessage(
            alt_text='服務選單',
            template=ButtonsTemplate(
                title='選擇服務',
                text='來賓請選擇',
                thumbnail_image_url='https://i.imgur.com/Hn2nJJN.jpg',
                actions=[
                    MessageTemplateAction(
                        label='週選擇權策略所需金額計算',
                        text='週選擇權策略所需金額計算'
                    ),
                    MessageTemplateAction(
                        label='月選擇權策略所需金額計算',
                        text='月選擇權策略所需金額計算'
                    ),
                    MessageTemplateAction(
                        label='選擇權不太即時報價表',
                        text='爬蟲爬起來爬起來'
                    ),

                    MessageTemplateAction(
                        label='淨化心靈的聲音',
                        text='播放'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    


    if event.message.text == "播放":
        line_bot_api.reply_message(
            event.reply_token,
            AudioSendMessage(
            original_content_url='https://drive.google.com/uc?export=download&id=1e2J4zbWdTnMyAr0qmfTMATzzhq7W28Sb',
            duration=10000))

    if event.message.text == "來個每日心靈小語":
        content=MyMod.good_word()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))    

    if event.message.text == "爬蟲爬起來爬起來":
        content=MyMod.good_word()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='https://rocky-beyond-10519.herokuapp.com/op'))  



#週選策略金額計算

    if event.message.text == "週選擇權策略所需金額計算":
        buttons_template = TemplateSendMessage(
            alt_text='週選擇權策略所需金額計算',
            template=ButtonsTemplate(
                title='週選擇權策略所需金額計算',
                text='來賓請選擇',
                thumbnail_image_url='https://i.imgur.com/Hn2nJJN.jpg',
                actions=[
                    MessageTemplateAction(
                        label='跨式策略',
                        text='買入週選價平跨式'
                    ),
                    MessageTemplateAction(
                        label='勒式勿賭',
                        text='買入週選價平勒式'
                    ),
                    MessageTemplateAction(
                        label='多頭價差',
                        text='買入週選多頭價差，價平上下兩檔'
                    ),
                    MessageTemplateAction(
                        label='空頭價差',
                        text='買入週選空頭價差，價平上下兩檔'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)



    if event.message.text == "買入週選多頭價差，價平上下兩檔":

        df=MyMod.opweek()
        content=MyMod.bullish_spread(df)
        a=['買入Call履約價為',str(content[0]),'\n\n',
           '權利金成本為',str(content[1]),'\n\n',
           '賣出Call履約價為',str(content[2]),'\n\n',
           '權利金收入為',str(content[3]),'\n\n',
           '所需保證金為',str(content[4])]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入週選空頭價差，價平上下兩檔":

        df=MyMod.opweek()
        content=MyMod.bearish_spread(df)
        a=['買入Call履約價為',str(content[0]),'\n\n',
           '權利金成本為',str(content[1]),'\n\n',
           '賣出Call履約價為',str(content[2]),'\n\n',
           '權利金收入為',str(content[3]),'\n\n',
           '所需保證金為',str(content[4])]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入週選價平跨式":

        df=MyMod.opweek()
        content=MyMod.triangle(df)
        a=['權利金成本為',str(content)]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入週選價平上下兩檔勒式":

        df=MyMod.opweek()
        content=MyMod.square(df)
        a=['權利金成本為',str(content)]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))



#月選策略金額計算

    if event.message.text == "月選擇權策略所需金額計算":
        buttons_template = TemplateSendMessage(
            alt_text='月選擇權策略所需金額計算',
            template=ButtonsTemplate(
                title='月選擇權策略所需金額計算',
                text='來賓請選擇',
                thumbnail_image_url='https://i.imgur.com/Hn2nJJN.jpg',
                actions=[
                    MessageTemplateAction(
                        label='跨式策略',
                        text='買入月選價平跨式'
                    ),
                    MessageTemplateAction(
                        label='勒式勿賭',
                        text='買入月選價平上下兩檔勒式'
                    ),
                    MessageTemplateAction(
                        label='多頭價差',
                        text='買入月選多頭價差，價平上下兩檔'
                    ),
                    MessageTemplateAction(
                        label='空頭價差',
                        text='買入月選空頭價差，價平上下兩檔'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)



    if event.message.text == "買入月選多頭價差，價平上下兩檔":

        df=MyMod.opmonth()
        content=MyMod.bullish_spread(df)
        a=['買入Call履約價為',str(content[0]),'\n\n',
           '權利金成本為',str(content[1]),'\n\n',
           '賣出Call履約價為',str(content[2]),'\n\n',
           '權利金收入為',str(content[3]),'\n\n',
           '所需保證金為',str(content[4])]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入月選空頭價差，價平上下兩檔":

        df=MyMod.opmonth()
        content=MyMod.bearish_spread(df)
        a=['買入Call履約價為',str(content[0]),'\n\n',
           '權利金成本為',str(content[1]),'\n\n',
           '賣出Call履約價為',str(content[2]),'\n\n',
           '權利金收入為',str(content[3]),'\n\n',
           '所需保證金為',str(content[4])]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入月選價平跨式":

        df=MyMod.opmonth()
        content=MyMod.triangle(df)
        a=['權利金成本為',str(content)]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    if event.message.text == "買入月選價平勒式":

        df=MyMod.opmonth()
        content=MyMod.square(df)
        a=['權利金成本為',str(content)]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="".join(a)))

    return 0





if __name__=="__main__":
    app.run(debug=True)
