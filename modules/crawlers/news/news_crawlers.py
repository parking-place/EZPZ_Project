import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import asyncio
import aiohttp

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

async def get_chosunbiz_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #fusion-app > div.article > div:nth-child(2) > div > section > article
        # #fusion-app > div.article > div:nth-child(2) > div > section > article > section
        contents = soup.select_one('#fusion-app > div.article > div:nth-child(2) > div > section > article > section')
        content = ''
        print(contents)
        p_tags = contents.select('p')
        for p in p_tags:
            content += p.text
        #fusion-app > div.article > div:nth-child(2) > div > section > article > div.article-dateline.\|.flex--wrap.flex.flex--justify-space-between.flex--align-items-center.box--border.box--border-grey-40.box--border-horizontal.box--border-horizontal-bottom.box--pad-bottom-sm > span
        #fusion-app > div.article > div:nth-child(2) > div > section > article > div.article-dateline.\|.flex--wrap.flex.flex--justify-space-between.flex--align-items-center.box--border.box--border-grey-40.box--border-horizontal.box--border-horizontal-bottom.box--pad-bottom-sm > span
        date = soup.select_one('#fusion-app > div.article > div:nth-child(2) > div > section > article > div.article-dateline.\|.flex--wrap.flex.flex--justify-space-between.flex--align-items-center.box--border.box--border-grey-40.box--border-horizontal.box--border-horizontal-bottom.box--pad-bottom-sm > span').text
        
        # text예시) 입력 2023.08.03 10:46
        date = re.findall(r'\d{4}.\d{2}.\d{2}', date)[0]
        date = date.replace('.', '')
        
    return link, content, date

async def get_nocut_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #pnlContent
        content = soup.select_one('div#pnlContent').text
        #pnlViewTop > div.h_info > ul > li:nth-child(2)
        date = soup.select_one('#pnlViewTop > div.h_info > ul > li:nth-child(2)').text
        # text예시) 2023-08-01 09:02 
        date = re.findall(r'\d{4}-\d{2}-\d{2}', date)[0]
        date = date.replace('-', '')
    return link, content, date

async def get_etnews_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # body > section > section > article
        contents = soup.select_one('body > section > section > article')
        content = ''
        p_tags = contents.select('p')
        for p in p_tags:
            content += p.text
        #body > section > section > article > div.article_header > div > time
        date = soup.select_one('body > section > section > article > div.article_header > div > time').text
        # text예시) 발행일 : 2023-08-01 09:47
        date = re.findall(r'\d{4}-\d{2}-\d{2}', date)[0]
        date = date.replace('-', '')
        
    return link, content, date

async def get_hankyung_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #articletxt
        # #articletxt
        content = soup.find('div', {'id':'articletxt'}).text
        #container > div > div > article > div > div > div.article-timestamp > div.datetime > span:nth-child(1) > span
        #container > div > div > article > div > div > div.article-timestamp > div.datetime > span:nth-child(1) > span
        date = soup.select_one('#container > div > div > article > div > div > div.article-timestamp > div.datetime > span:nth-child(1) > span').text
        # text예시) 2023.08.01 09:47
        date = re.findall(r'\d{4}.\d{2}.\d{2}', date)[0]
        date = date.replace('.', '')
    return link, content, date

# async def get_joongang_content(link, session):
#     async with session.get(link, headers=HEADERS) as r:
#         html = await r.text()
#         soup = bs(html, 'lxml')
#         # #article_body
#         contents = soup.select_one('div#article_body')
#         content = ''
#         p_tags = contents.select('p')
#         for p in p_tags:
#             content += p.text
#     return link, content

async def get_moneytoday_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #textBody
        content = soup.select_one('div#textBody').text
        #view_wrapc01-scroll-in > div.vc_top > div > ul > li
        date = soup.select_one('#view_wrapc01-scroll-in > div.vc_top > div > ul > li').text
        # text예시) 2023.08.01 09:47
        date = re.findall(r'\d{4}.\d{2}.\d{2}', date)[0]
        date = date.replace('.', '')
    return link, content, date

async def get_newsone_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #articles_detail
        content = soup.select_one('div#articles_detail').text
        #article_body_content > div.title > div.info
        date = soup.select_one('#article_body_content > div.title > div.info').text
        # text예시) (서울=뉴스1) 김정은 기자, 강은성 기자 | 2023-08-03 06:53 송고 | 2023-08-03 08:52 최종수정
        date = re.findall(r'\d{4}-\d{2}-\d{2}', date)[0]
        date = date.replace('-', '')
    return link, content, date

async def get_hankookilbo_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # body > div.wrap.imp-end > div.container.end-uni > div.end-body > div > div.col-main
        contents = soup.select_one('body > div.wrap.imp-end > div.container.end-uni > div.end-body > div > div.col-main')
        content = ''
        p_tags = contents.select('p')
        for p in p_tags:
            content += p.text
        #body > div.wrap.imp-end > div.container.end-uni > div.end-top > div > div > div.info > dl > dd:nth-child(2)
        date = soup.select_one('body > div.wrap.imp-end > div.container.end-uni > div.end-top > div > div > div.info > dl > dd:nth-child(2)').text
        # text예시) 2023.08.03 10:45 
        date = re.findall(r'\d{4}.\d{2}.\d{2}', date)[0]
        date = date.replace('.', '')
    return link, content, date

async def get_zdnet_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #articleBody
        contents = soup.select_one('div#articleBody > div')
        content = ''
        p_tags = contents.select('p')
        for p in p_tags:
            content += p.text
        # #content > div > div.article_header > div > span.date
        date = soup.select_one('#content > div > div.article_header > div > span.date').text
        # text예시) 입력 :2023/07/27 11:15    수정: 2023/07/27 13:57
        date = re.findall(r'\d{4}/\d{2}/\d{2}', date)[0]
        date = date.replace('/', '')
    return link, content, date

async def get_naver_content(link, session):
    async with session.get(link, headers=HEADERS) as r:
        html = await r.text()
        soup = bs(html, 'lxml')
        # #dic_area
        content = soup.select_one('#dic_area').get_text()
        #ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span
        date = soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span').text
        # text예시) 2023.07.28. 오전 10:14
        date = re.findall(r'\d{4}.\d{2}.\d{2}', date)[0]
        date = date.replace('.', '')
    return link, content, date

link_to_get_content = {
    # 'biz.chosun.com': get_chosunbiz_content,
    'www.nocutnews.co.kr': get_nocut_content,
    'www.etnews.com': get_etnews_content,
    'www.hankyung.com': get_hankyung_content,
    # 'www.joongangilbo.co.kr': get_joongang_content,
    'news.mt.co.kr': get_moneytoday_content,
    # 'www.news1.kr': get_newsone_content,
    'www.hankookilbo.com': get_hankookilbo_content,
    'www.zdnet.co.kr': get_zdnet_content,
    'n.news.naver.com': get_naver_content,
}

def get_content(link):
    site_url = link.split('/')[2]
    get_content_func = link_to_get_content.get(site_url, None)
    if get_content_func:
        return True, get_content_func(link)
    else:
        return False, None
    
async def get_content_async(links):
    url_and_funcs = []
    for link in links:
        site_url = link.split('/')[2]
        func = link_to_get_content.get(site_url, None)
        if func:
            url_and_funcs.append((func, link))

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async_results = await asyncio.gather(*[get_content_func(link, session) for get_content_func, link in url_and_funcs])
    
    return async_results