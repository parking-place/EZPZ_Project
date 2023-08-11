# daum_news_list.py
# 특정 키워드에 대한 다음 뉴스 검색, dataframe 반환 모듈
# csv_save=True 설정시 csv 저장.

# crawling
import requests as req
from bs4 import BeautifulSoup as bs

# to dataframe
import pandas as pd

# async
import asyncio
import aiohttp


# 나머지는 함수 내에서 import : 해당 함수에서만 사용 

# constants
SEARCH_FORMAT_URL = 'https://search.daum.net/search?nil_suggest=btn&w=news&DA=PGD&cluster=y&q={}&p={}&show_dns=1'
V_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
SAVE_PATH = './datas/daum_news'



def get_links_to_keyword(keyword):
    """
    제목까지 받아와야 하는 경우, 해당 함수의 주석과 get_news_list 함수의 주석을 해제 후 사용해야 합니다.
    parameter ]
        keyword : str   - 해당 단어로 다음 검색(입력시 global 변수로 저장)
        
    return ]
        links   : list[str] - 기사들의 링크
    """
    news_list = []
    p = 1
    # 검색
    headers = {
        'user-agent': V_AGENT
    }
    cnt = 0 # 무한루프 방지 변수
    # if 
    while len(news_list) < 11:
        # 무한 루프 방지
        if cnt >= 99:
            break
        
        # 뉴스 a 태그 가져오기
        res = req.get(SEARCH_FORMAT_URL.format(keyword, p), headers=headers)
        soup = bs(res.text, 'lxml')
        news = soup.select('.tit-g.clamp-g > a')
        
        # 검색결과 없다면
        if news ==None:
            break
        
        news_list += [el.attrs['href'] for el in news]
        p += 1
            
        cnt+= 1
        
    return news_list



async def get_content_to_link(session, link):
    """
    url로 들어온 개별 뉴스를 크롤링 하는 co-routine 함수
    
    parameters ]
        link    : str   - 뉴스 URL
        
    returns ]
        context : str   - 뉴스 본문
    """
    # .article_view p
    async with session.get(link) as res:
        if res.status == 200:
            
            # Beautiful Soup 객체 생성
            html = await res.text()
            soup = bs(html, 'lxml')
            
            # 기사 내용, 뉴스 작성일
            contents = ''.join([el.text for el in soup.select('.article_view p')])
            pub_date = soup.select_one('span .num_date').text
            # 첫 번째 크롤링 되는 날짜 : 작성일
            # 두 번쨰 크롤링 되는 날짜 : 수정일
            
            # string format : "YYYY. M. D. HH:mm"
            pub_date = pub_date[:-5] # HH:mm 부분 제거
            pub_date = pub_date.split('. ')[: -1] # 맨 뒤 공백 string 제거
            
            # YYYYMMDD 형식으로 변환
            pub_date = pub_date[0] + (2 - len(pub_date[1])) * '0' + pub_date[1] + (2 - len(pub_date[2])) * '0' + pub_date[2]
            
            return contents, pub_date



async def get_content_list(links):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession(
        headers=headers, connector=aiohttp.TCPConnector(ssl=False)
    ) as session :
        result = await asyncio.gather(*[get_content_to_link(session, link) for link in links]) # wrapping도 내부 처리
    
    return result



def get_news(keyword, csv_save=False):
    import re
    """
    기업 관련 키워드를 받아 링크/본문 형태의 dataframe으로 반환하는 함수
    
    parameters ]
        keyword : str   - 검색할 키워드
        csv_save        : bool  - True 설정시 저장 및 로그 기록
        
    returns ]
        df      : pandas.DataFrame  - [news_url, content]
    """
    if csv_save:
        import os
        import time
        from datetime import date
        st_time = time.time()
        
    links = get_links_to_keyword(keyword)
    result = asyncio.run(get_content_list(links))
    
    # 반환값
    df = pd.DataFrame({
        'news_url': links,
        'news_cont': [el[0] for el in result],
        'pub_date': [el[1] for el in result]
    })
    print(df)
    
    df['news_cont'] = df['news_cont'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())
    
    if csv_save:
        # ========== [이하는 csv 저장 로직] ==========
        os.makedirs(SAVE_PATH, exist_ok=True) # 디렉토리 생성
        df.to_csv(os.path.join(SAVE_PATH, f'{keyword}_daum.csv'), index=False)
    
        # logging
        ed_time = time.time()
        TODATE = date.today().strftime("%Y%m%d")
        
        print(f'[CSV SAVED] {TODATE} - {SAVE_PATH}/{keyword}_daum.csv at {(ed_time - st_time):.5f} sec')
        
    else: # 저장 안하고 바로 반환
        return df