# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

def add_page(url,page):
    return f"{url}&page={page}"

output = list()
url = 'http://www.travel4u.com.tw/oversea/list_custom.aspx?StartDate=2018/07/19&EndDate=2018/08/24&ROUT=TPE&day=%&MBITN_CD=N0103'


chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(chrome_options=chrome_options,
                          executable_path='chromedriver.exe')

total_pages = 28                   
  
for page in range(1 ,total_pages+1): # TODO get the actual pages.
    print(f"{page}/{total_pages+1}")
    if page == 1:
        driver.get(url)
    else:
        driver.get(add_page(url, page))
    elem = driver.find_element_by_id("ctl00_ContentPlaceHolder1_ctrlGroup")
    source_code = elem.get_attribute('innerHTML')
    output.append(source_code)

driver.close()
driver.quit()    

columns=['序', '出發日期', '團型名稱', '機場', '天數', 
         '機位', '可售', '優惠價', '訂金', '狀況']
df = pd.DataFrame(columns=columns)
for test in output:
    soup = BeautifulSoup(test, 'html.parser')
    routes = soup.find_all('div',{'class':'c_tr'})
    for index_, r in enumerate(routes):
        if index_ in [0]:
            continue
        route = r.find_all('div')
        row = list()
        for index, data in enumerate(route):
            if index in [4,5,6,7,11]:
                continue
            row.append(data.text)
        row_data=pd.Series(row,columns)
        df = df.append([row_data],ignore_index=True)

df = df[df['狀況'] != '滿團']
df['天數'] = df['天數'].astype('int')
df['機位'] = df['機位'].astype('int')
df['可售'] = df['可售'].astype('int')
df['優惠價'] = df['優惠價'].astype('int')
df['訂金'] = df['訂金'].astype('int')

# 挑星期
dates = ['四','五']
df = df[df['出發日期'].str.contains('|'.join(dates))]

# 挑月份
def f(text):
    # 2018/05/16(三)
    s = text.split('/')[1]
    if s in ['07', '08']:
        return True
    else:
        return False
df = df[df['出發日期'].apply(f)]

# 挑天數
df = df[df['天數']<=5]

# 挑座位數
df = df[df['可售']>=15]

df.to_csv('大阪.csv', encoding='utf-8', index=False)
