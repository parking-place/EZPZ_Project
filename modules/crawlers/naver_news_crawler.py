import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import news_crawlers as nc

# BASE_URL = r'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={comp_name}'
BASE_URL = r'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={comp_name}&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=79&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start={page}'

SAVE_PATH = r'E:\Python\data\MiniProj\datas\news\{}_naver.csv'

def get_url(comp_name, page=1):
    url = BASE_URL.format(comp_name=comp_name, page=page)
    return url

def get_news_in_page(comp_name, page=1):
    url = get_url(comp_name, page)
    r = requests.get(url)
    soup = bs(r.text, 'lxml')
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
        'content': []
    }
    
    for news_link in link_list:
        # print(news_link)
        is_success, data = nc.get_content(news_link)
        if is_success:
            link, content = data
            news_dict['link'].append(link)
            news_dict['content'].append(content)
    
    news_df = pd.DataFrame(news_dict)
    
    return news_df

def get_news(comp_name, page=5):
    news_dfs = []
    for i in range(1, page+1):
        news_dfs.append(get_news_in_page(comp_name, i))
    news_df = pd.concat(news_dfs)
    news_df = pretreatment_data(news_df)
    save_news(news_df, comp_name)
    return news_df

def pretreatment_data(news_df):
    news_df['content'] = news_df['content'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())
    return news_df

def save_news(news_df, comp_name):
    news_df.to_csv(SAVE_PATH.format(comp_name), index=False, encoding='utf-8-sig')