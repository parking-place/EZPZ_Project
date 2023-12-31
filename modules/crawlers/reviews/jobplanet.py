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


# async
import asyncio
import aiohttp


# 나머지는 함수 내에서 import : 해당 함수에서만 사용 

# constants
JOBPLANET_URL = 'https://www.jobplanet.co.kr'
JOBPLANET_LOGIN_URL = JOBPLANET_URL + '/users/sign_in'
JOBPLANET_SEARCH_URL = JOBPLANET_URL + '/search/companies/{keyword}?page={p}'
JOBPLANET_REVIEW_URL = JOBPLANET_URL + '/companies/{jp_comp_uid}/reviews?page={p}'
SAVE_PATH = '/app/data/reviews/'


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




def get_jobplanet_uid(headers, keyword):
    """
    헤더 정보와 기업 명을 받아
    잡플래닛 내부 기업 id로 반환합니다.
    
    return ]
        str - 잡플래닛 내부 기업 ID
    """
    # 크롤링 준비
    for i in range(30): # 30 페이지동안 서치합니다.
        s_url = JOBPLANET_SEARCH_URL.format(keyword=keyword, p=i+1)
        res = req.get(s_url, headers=headers)
        soup = bs(res.text, 'lxml')
        
        # 잡플래닛 내부 회사 ID 크롤링
        a_tags = soup.select('dt.us_titb_l3 > a')
        
        # 정확도 높은 것으로 검사합니다.
        for a_tag in a_tags:
            if a_tag.text.find(keyword) > -1:
                # href format : /companies/{잡플래닛_회사ID}/info/{회사이름}?_rs_act=index&_rs_con=search&_rs_element=federated_search
                return a_tag.attrs['href'].split('/')[2]



async def filter_reviewer_info(info):
    """
    리뷰어 한 명의 정보가 담겨있는 info를 받아, split해주는 함수
    parameters ]
        info : list    - 리뷰어 한명의 정보
        
    return ]
        position    : str   - 직무
        is_office   : str   - 현직원/전직원 여부
        review_date : str   - 리뷰 작성 날짜
    """
    # 각 컬럼에 맞는 처리를 해줍니다.
    position = info[0]
    is_office = False if info[1] == '전직원' else True
    review_date = info[3].replace('. ', '')
    
    return position, is_office, review_date



async def filter_review_rate(rate):
    """
    비동기 전환용 함수 : 별점 정보 변환
    
    parameters ]
        rate    : str   - 별점(형식 : width:{percent}%)
        
    return ]
        int - 1 ~ 5점사이 별점으로 formatted
    """
    return int(int(rate[6:-2]) / 20)



# 비동기 전환용 함수
async def get_elemenet_text(el):
    return el.text



# 데이터 크롤링 함수
async def get_content_to_link(session, url):
    async with session.get(url) as res:
        if res.status == 200:
            
            html = await res.text()
            soup = bs(html, 'lxml')
            
            # 리뷰 없는 경우
            if soup.select_one('article.no_result > .txt'): # '리뷰가 없습니다' 태그
                return None
            
            # 통과 : 크롤링 시작
            # =========================
            # 작성자 정보 크롤링
            # =========================
            # span.txt1 : [직무, (전직원|현직원), 지역, 작성 날짜] 의 연속으로 구성됨
            reviewer_infos = [el.text.strip() for el in soup.select('span.txt1')]
            
            # 한 사람 단위로 잘라주기
            reviewer_infos = [reviewer_infos[i*4:(i*4+4)] for i in range(int(len(reviewer_infos) / 4))]
            
            # split
            reviewer_infos = asyncio.gather(*[filter_reviewer_info(info) for info in reviewer_infos])
            review_rates = asyncio.gather(*[filter_review_rate(el.attrs['style']) for el in soup.select('div.star_score')])
            
            # get reviews content
            neg_review = asyncio.gather(*[get_elemenet_text(el) for el in soup.select('dt.disadvantages+dd > span')])
            pos_reivew = asyncio.gather(*[get_elemenet_text(el) for el in soup.select('dt.merit+dd > span')])
            
            return reviewer_infos, review_rates, neg_review, pos_reivew



async def get_content_list(cookies, urls):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        session.cookie_jar.update_cookies(cookies)
        result = await asyncio.gather(*[get_content_to_link(session, url) for url in urls]) # wrapping도 내부 처리
    
    return result



def get_review(keyword, csv_save=False):
    """
    회사 명을 키워드를 받아 dataframe으로 반환하는 함수
    
    parameters ]
        keyword     : str   - 검색할 키워드
        csv_save    : bool  - True 설정시 저장 및 로그 기록
        
    returns ]
        pandas.DataFrame
        columns ]
            position    : str       - 직무
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
    
    # 크롤링 준비
    jp_comp_uid = get_jobplanet_uid(req_session.headers, keyword)
    
    # 검색 결과 없는 경우
    if jp_comp_uid is None:
        print(f'[SEARCH FAILED] 잡플래닛 리뷰 검색 "{keyword}" 실패')
        return None
    
    # 성공 : 크롤링 url 생성
    urls = [JOBPLANET_REVIEW_URL.format(jp_comp_uid=jp_comp_uid, p=i+1) for i in range(99)]
    
    # 데이터 크롤링
    results = asyncio.run(get_content_list(req_cookies, urls))
    # None 제거 : 리뷰 없는 페이지
    results = [data for data in results if data is not None]
    
    # 데이터 프레임으로 변환
    position = []
    is_office = []
    review_date = []
    review_rate = []
    neg_cont = []
    pos_cont = []
    
    for i in range(len(urls)):
        result = results[i] # tuple
        
        position.extend([el[0] for el in result[0].result()])
        is_office.extend([el[1] for el in result[0].result()])
        review_date.extend([el[2] for el in result[0].result()])
        
        review_rate += result[1].result()
        
        neg_cont += result[2].result()
        pos_cont += result[3].result()
        
    df = pd.concat([
        pd.DataFrame({
            'position' : position,
            'is_office' : is_office,
            'review_date' : review_date,
            'review_rate' : review_rate,
            'review_cont' : pos_cont,
        }), pd.DataFrame({
            'position' : position,
            'is_office' : is_office,
            'review_date' : review_date,
            'review_rate' : review_rate,
            'review_cont' : neg_cont,
        }) ], join='outer') # union, default
    #print(df)
    
    
    if csv_save:
        # ========== [이하는 csv 저장 로직] ==========
        os.makedirs(SAVE_PATH, exist_ok=True) # 디렉토리 생성
        df.to_csv(os.path.join(SAVE_PATH, f'{keyword}_job_planet.csv'), index=False)
        
        # logging
        ed_time = time.time()
        TODATE = date.today().strftime("%Y%m%d")
        
        print(f'[CSV SAVED] {TODATE} - {SAVE_PATH}{keyword}_job_planet.csv at {(ed_time - st_time):.5f} sec')
        
    return df 


if __name__ == '__main__':
    # 테스트 코드
    get_review('삼성전자', csv_save=True)