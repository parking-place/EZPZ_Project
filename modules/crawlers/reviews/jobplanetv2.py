# jobplanet.py
# 특정 키워드에 대한 잡플래닛 리뷰 검색, dataframe 반환 모듈
# csv_save=True 설정시 csv 저장.

# crawling
import requests as req
from user_agent import generate_navigator # 랜덤 헤더 생성 모듈
from bs4 import BeautifulSoup as bs

# to sign in
from accounts import jp
import json


# to dataframe
import pandas as pd

# re
import re
from datetime import datetime

# async
import asyncio
import aiohttp


# 나머지는 함수 내에서 import : 해당 함수에서만 사용 

# constants
JOBPLANET_URL = 'https://www.jobplanet.co.kr'
JOBPLANET_LOGIN_URL = JOBPLANET_URL + '/users/sign_in'
JOBPLANET_SEARCH_URL = JOBPLANET_URL + '/search?query={keyword}'
JOBPLANET_REVIEW_URL = JOBPLANET_URL + '/companies/{jp_comp_uid}/reviews?page={p}'
SAVE_PATH = '/app/data/reviews/'

JOBPLANET_JSON_URL = r'https://www.jobplanet.co.kr/companies/{jp_comp_uid}/company_reviews/{page}.json'

# 잡플래닛 로그인 세션 생성함수
def get_login_session():
    """
    잡플래닛 로그인을 시도해, request session 객체와 cookie 값을 반환합니다.
    
    returns ]
        session : request.sessions.Session  - 로그인 된 세션
        cookies : dict                      - 로그인 완료된 쿠키값
    """
    # ==============================
    # Header
    # ==============================
    # 랜덤으로 돌립니다.
    while True:
        HEADERS = generate_navigator(device_type="desktop", os=('mac', 'linux', 'win'))
        if None not in HEADERS.values():
            break
        
    # 나머지 헤더값 넣어주기
    HEADERS['Referer'] = 'https://www.jobplanet.co.kr/users/sign_in?_nav=gb'
    HEADERS['Origin'] = 'https://www.jobplanet.co.kr'
    HEADERS['Content-Type'] = 'application/json'
    HEADERS['Accpet'] = '*/*'
    HEADERS['Accpet-Encoding'] = 'gzip, deflate, br'
    HEADERS['Accept-Language'] = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    
    # ==============================
    # Payload
    # ==============================
    PAYLOAD = {
        'user': {
            'email': jp.ID,
            'password': jp.PW,
            'remember_me': False  
        }
    }
    
    # ==============================
    # make session to use cookie
    # ==============================
    session = req.Session()
    login_cookie = session.post(JOBPLANET_LOGIN_URL, data=json.dumps(PAYLOAD), headers=HEADERS).cookies.get_dict()
    # update cookies & headers
    session.cookies.update(login_cookie)
    session.headers.update(HEADERS)
    
    return session, session.cookies.get_dict() # 쿠키 따로 반환



def get_links_to_keyword(headers, jp_comp_uid, page):
    """
    제목까지 받아와야 하는 경우, 해당 함수의 주석과 get_news_list 함수의 주석을 해제 후 사용해야 합니다.
    parameter ]
        headers : dict  - header 정보
        keyword : str   - 해당 단어로 다음 검색(입력시 global 변수로 저장)
        
    return ]
        links   : list[str] - 리뷰 페이지들 링크
    """
    
    url_list = [JOBPLANET_JSON_URL.format(jp_comp_uid=jp_comp_uid, page=p) for p in range(1, page+1)]
        
    return url_list

# 데이터 크롤링 함수
async def get_content_to_link(session, url):
    async with session.get(url) as res:
        if res.status == 200:
            
            json_data = await res.json()
            
            review_list = json_data['reviews']
            
            # 리뷰가 없는 경우
            if review_list == []:
                return None
            
            
            review_list = json_data['reviews']
            
            position_list = []
            is_office_list = []
            review_date_list = []
            review_rate_list = []
            neg_cont_list = []
            pos_cont_list = []
            
            for review in review_list:
                # 신고로 삭제된 경우
                if 'contents_blinder' in review.keys():
                    continue
                
                position_list.append(review['occupation_name'])
                is_office_list.append( 1 if review['currently_employed'] else 0)
                review_date_list.append(review['created_at_to_date'].replace('. ', ''))
                review_rate_list.append(review['overall'])
                neg_cont_list.append(review['cons'].replace('<br/>', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('\"', '').replace('\'', ''))
                pos_cont_list.append(review['pros'].replace('<br/>', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('\"', '').replace('\'', ''))
            
            # 쓸 리뷰가 없는 경우
            if position_list == []:
                return None
            
            df = pd.concat([
                pd.DataFrame({
                    'review_date' : review_date_list,
                    'is_office' : is_office_list,
                    'review_cont' : pos_cont_list,
                    'position' : position_list,
                    'review_rate' : review_rate_list,
                    'review_senti_orig' : ['P'] * len(pos_cont_list)
                }), pd.DataFrame({
                    'review_date' : review_date_list,
                    'is_office' : is_office_list,
                    'review_cont' : neg_cont_list,
                    'position' : position_list,
                    'review_rate' : review_rate_list,
                    'review_senti_orig' : ['N'] * len(neg_cont_list)
                }) ],
                join='outer',
                ignore_index=True
            )
                
            return df
            

async def get_content_list(cookies, urls):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        session.cookie_jar.update_cookies(cookies)
        result = await asyncio.gather(*[get_content_to_link(session, url) for url in urls]) # wrapping도 내부 처리
    
    return result

# 페이지 개수를 가져오는 함수
def get_pages(session, url):
    
    r = session.get(url)
    soup = bs(r.text, 'lxml')
    
    # #viewCompaniesMenu > ul > li.viewReviews > a > span
    page = soup.select_one('#viewCompaniesMenu > ul > li.viewReviews > a > span').text
    
    if int(page) == 0:
        return 0
    
    page = int(page)//5+1
    
    return page


def get_review(keyword, uid, csv_save=False):
    """
    회사 명을 키워드를 받아 dataframe으로 반환하는 함수
    
    parameters ]
        keyword     : str   - 검색할 키워드
        csv_save    : bool  - True 설정시 저장 및 로그 기록
        
    returns ]
        pandas.DataFrame
        columns ]
            review_cont : str       - 리뷰 본문
            review_rate : int       - 별점
            is_office   : boolean   - 전직원/현직원 여부
            review_date : str       - 리뷰 작성 날짜(YYYYMM)
    """
    if csv_save:
        import os
        import time
        from datetime import date
        st_time = time.time()
    
    # 헤더 정보부터 만듭니다.
    req_session, req_cookies = get_login_session()
    
    page = get_pages(req_session, JOBPLANET_REVIEW_URL.format(jp_comp_uid=uid, p=1))
    
    if page == 0:
        return False
    
    # 크롤링 준비
    # jp_comp_uid = get_jobplanet_uid(req_session.headers, keyword)
    urls = get_links_to_keyword(req_session.headers, uid, page)
    
    # 데이터 크롤링
    results = asyncio.run(get_content_list(req_cookies, urls))
    
    # result 중 None 제거
    results = [data for data in results if data is not None]
    
    # 데이터프레임으로 변환
    df = pd.concat(results, ignore_index=True, join='outer', axis=0)
    
    if csv_save:
        # ========== [이하는 csv 저장 로직] ==========
        os.makedirs(SAVE_PATH, exist_ok=True) # 디렉토리 생성
        df.to_csv(os.path.join(SAVE_PATH, f'{keyword}_job_planet.csv'), index=False)
    
        # logging
        ed_time = time.time()
        TODATE = date.today().strftime("%Y%m%d")
        
        print(f'[CSV SAVED] {TODATE} - {SAVE_PATH.format(comp_name=keyword)} at {(ed_time - st_time):.5f} sec')
        
    return df 


if __name__ == '__main__':
    # df = get_review('넥슨게임즈', '392405', csv_save=False)
    df = get_review('삼성전자(주)', '30139', csv_save=False)
    # df = get_review('(주)엔코어벤처스', '376861', csv_save=False)
    # df = get_review('(주)한스클린', '349519', csv_save=False)
    if df is not False:
        print(len(df))
        print(df)
    else:
        print('리뷰가 존재하지 않습니다.')
        