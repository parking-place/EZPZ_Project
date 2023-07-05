import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

def get_chosunbiz_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #fusion-app > div.article > div:nth-child(2) > div > section > article
    # #fusion-app > div.article > div:nth-child(2) > div > section > article > section
    contents = soup.select_one('#fusion-app > div.article > div:nth-child(2) > div > section > article > section')
    content = ''
    print(contents)
    p_tags = contents.select('p')
    for p in p_tags:
        content += p.text
    return link, content

def get_nocut_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #pnlContent
    content = soup.select_one('div#pnlContent').text
    return link, content

def get_etnews_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # body > section > section > article
    contents = soup.select_one('body > section > section > article')
    content = ''
    p_tags = contents.select('p')
    for p in p_tags:
        content += p.text
    return link, content

def get_hankyung_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #articletxt
    # #articletxt
    content = soup.find('div', {'id':'articletxt'}).text
    return link, content

def get_joongang_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #article_body
    contents = soup.select_one('div#article_body')
    content = ''
    p_tags = contents.select('p')
    for p in p_tags:
        content += p.text
    return link, content

def get_moneytoday_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #textBody
    content = soup.select_one('div#textBody').text
    return link, content

def get_newsone_content(link, headers=HEADERS):
    r = requests.get(link)
    soup = bs(r.text, 'lxml')
    # #articles_detail
    content = soup.select_one('div#articles_detail').text
    return link, content

def get_hankookilbo_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # body > div.wrap.imp-end > div.container.end-uni > div.end-body > div > div.col-main
    contents = soup.select_one('body > div.wrap.imp-end > div.container.end-uni > div.end-body > div > div.col-main')
    content = ''
    p_tags = contents.select('p')
    for p in p_tags:
        content += p.text
    return link, content

def get_zdnet_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #articleBody
    contents = soup.select_one('div#articleBody > div')
    content = ''
    p_tags = contents.select('p')
    for p in p_tags:
        content += p.text
    return link, content

def get_naver_content(link):
    r = requests.get(link, headers=HEADERS)
    soup = bs(r.text, 'lxml')
    # #dic_area
    content = soup.select_one('div#dic_area').get_text()
    return link, content

link_to_get_content = {
    # 'biz.chosun.com': get_chosunbiz_content,
    'www.nocutnews.co.kr': get_nocut_content,
    'www.etnews.com': get_etnews_content,
    'www.hankyung.com': get_hankyung_content,
    'www.joongangilbo.co.kr': get_joongang_content,
    'news.mt.co.kr': get_moneytoday_content,
    'www.news1.kr': get_newsone_content,
    'www.hankookilbo.com': get_hankookilbo_content,
    'www.zdnet.co.kr': get_zdnet_content,
    'n.news.naver.com': get_naver_content,
}