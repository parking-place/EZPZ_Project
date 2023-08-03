import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import news_crawlers as nc

import asyncio
import aiohttp

# BASE_URL = r'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={comp_name}'
BASE_URL = r'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={comp_name}&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=79&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start={page}'

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

SAVE_PATH = r'E:\Python\data\MiniProj\datas\news\{}_naver.csv'

def get_url(comp_name, page=1):
    url = BASE_URL.format(comp_name=comp_name, page=page)
    return url

async def get_news_in_page(comp_name, session, page=1):
    url = get_url(comp_name, page)
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
            'link': [],
            'content': [],
            'date': [],
        }
        
        results = await nc.get_content_async(link_list)
        
        for result in results:
            link, content, date = result
            news_dict['link'].append(link)
            news_dict['content'].append(content)
            news_dict['date'].append(date)
        
        news_df = pd.DataFrame(news_dict)
    
    return news_df

async def async_loop_outer(comp_name, page=5):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        result_list = await asyncio.gather(*[get_news_in_page(comp_name, session, i) for i in range(1, page+1)])
    return result_list

def get_news(comp_name, page=5):
    result_list = asyncio.run(async_loop_outer(comp_name, page))
    result_list = [result for result in result_list if result is not None]
    news_df = pd.concat(result_list)
    news_df = pretreatment_data(news_df)
    # save_news(news_df, comp_name)
    return news_df

def pretreatment_data(news_df):
    news_df['content'] = news_df['content'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())
    return news_df

def save_news(news_df, comp_name):
    news_df.to_csv(SAVE_PATH.format(comp_name), index=False, encoding='utf-8-sig')



if __name__ == '__main__':
    df = get_news('SK 하이닉스', 5)
    
    print(df.head())
    print(df.shape)