import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import news_crawlers as nc

BASE_URL = r'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={comp_name}'
# BASE_URL = r'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={comp_name}sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=79&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start={page_num}'

def get_content(link):
    site_url = link.split('/')[2]
    get_content_func = nc.link_to_get_content.get(site_url, None)
    if get_content_func:
        return True, get_content_func(link)
    else:
        return False, None

def get_url(comp_name):
    url = BASE_URL.format(comp_name=comp_name)
    return url

def get_news(comp_name):
    url = get_url(comp_name)
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
    
    for news in link_list:
        print(news)
        is_success, data = get_content(news)
        if is_success:
            link, content = data
            news_dict['link'].append(link)
            news_dict['content'].append(content)
    
    return pd.DataFrame(news_dict)