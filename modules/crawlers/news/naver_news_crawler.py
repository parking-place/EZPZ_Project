import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import news_crawlers as nc

import asyncio
import aiohttp

import time
import random
import string

from user_agent import generate_navigator

# BASE_URL = r'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={comp_name}'
BASE_URL = r'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={comp_name}&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=79&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start={page}'

def set_headers():
    global HEADERS 
    HEADERS = generate_navigator()
    while None in HEADERS.values():
        HEADERS = generate_navigator()

HEADERS = set_headers()

SAVE_PATH = r'E:\Python\data\MiniProj\datas\news\{}_naver.csv'

def get_url(comp_name, page=1):
    url = BASE_URL.format(comp_name=comp_name, page=page)
    return url

async def get_news_in_page(comp_name, session, page=1):
    url = get_url(comp_name, page)
    # time.sleep(random.randint(1, 3))
    async with session.get(url, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #main_pack > section > div > div.group_news > ul
        mainbox_list = soup.select('#main_pack > section > div > div.group_news > ul > li')
        # li class : sub_bx
        subbox_list = soup.find_all('li', {'class':'sub_bx'})
        
        link_list = []
        
        for box in mainbox_list:
            a_tag = box.select_one('div.news_wrap.api_ani_send > div > a')
            link = a_tag['href']
            link_list.append(link)
        
        for box in subbox_list:
            a_tag = box.select_one('span > a')
            link = a_tag['href']
            link_list.append(link)

        news_dict = {
            'news_url': [],
            'news_cont': [],
            'pub_date': [],
        }
        
        # print('\n\n\n\n\n', html)
        
        results = await nc.get_content_async(link_list)
        
        for result in results:
            link, content, date = result
            news_dict['news_url'].append(link)
            news_dict['news_cont'].append(content)
            news_dict['pub_date'].append(date)
        
        news_df = pd.DataFrame(news_dict)
    
    return news_df

async def async_loop_outer(comp_name, cookies=None, page=5):
    async with aiohttp.ClientSession(headers=HEADERS, cookies=cookies) as session:
        result_list = await asyncio.gather(*[get_news_in_page(comp_name, session, i) for i in range(1, page+1)])
    return result_list

def get_news(comp_name, page=5):
    while True:
        set_headers()
        # print(HEADERS)
        
        # 같은 단어 여러번 검색시 밴당하는 것을 방지하기 위해 랜덤한 문자열로 세션을 열어 쿠키를 받아옴
        randstr = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        cookies = None
        sessoin = requests.Session()
        with sessoin.get( get_url(randstr, 1), headers=HEADERS) as r:
            cookies = sessoin.cookies
        
        result_list = asyncio.run(async_loop_outer(comp_name, cookies, page))
        result_list = [result for result in result_list if result is not None]
        news_df = pd.concat(result_list)
        news_df = pretreatment_data(news_df)
        
        if len(news_df) != 0:
            break
    # save_news(news_df, comp_name)
    return news_df

def pretreatment_data(news_df):
    news_df['news_cont'] = news_df['news_cont'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())
    return news_df

def save_news(news_df, comp_name):
    news_df.to_csv(SAVE_PATH.format(comp_name), index=False, encoding='utf-8-sig')



if __name__ == '__main__':
    
    # sessoin = requests.Session()
    # with sessoin.get( get_url('(주)삼성전자', 1), headers=HEADERS) as r:
    #     html = r.text
    #     print(html)
    #     print(sessoin.cookies)
    
    df = get_news('삼성전자', 5)
    
    print(df.head())
    print(df.shape)
    
    