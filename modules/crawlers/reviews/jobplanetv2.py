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




# 잡플래닛 내부 회사 uid 가져오는 함수
def get_jobplanet_uid(headers, keyword):
    # 크롤링 준비
    res = req.get(JOBPLANET_SEARCH_URL.format(keyword=keyword), headers=headers)
    soup = bs(res.text, 'lxml')

    # 잡플래닛 내부 회사 ID 크롤링
    # b 태그 갖고 있는 a 태그만 추출 : 정확도 높은게 볼드체 처리됨
    a_tag = [el for el in soup.select('div.is_company_card a') if el.select_one('b')][0]

    # href format : /companies/{잡플래닛_회사ID}/info/{회사이름}?_rs_act=index&_rs_con=search&_rs_element=federated_search
    return a_tag.attrs['href'].split('/')[2]




def get_links_to_keyword(headers, jp_comp_uid, page):
    """
    제목까지 받아와야 하는 경우, 해당 함수의 주석과 get_news_list 함수의 주석을 해제 후 사용해야 합니다.
    parameter ]
        headers : dict  - header 정보
        keyword : str   - 해당 단어로 다음 검색(입력시 global 변수로 저장)
        
    return ]
        links   : list[str] - 리뷰 페이지들 링크
    """
    review_list = []
    p = 1
    
    for p in range(page):
        now_url = JOBPLANET_REVIEW_URL.format(jp_comp_uid=jp_comp_uid, p=p+1)
    
        # res = req.get(now_url, headers=headers)
        # soup = bs(res.text, 'lxml')
        
        # # 리뷰 없는 경우
        # if soup.select_one('article.no_result > .txt'): # '리뷰가 없습니다' 태그
        #     break
        
        # 통과한 경우 : 리뷰 있음, 리스트에 추가
        review_list.append(now_url)
        
    return review_list



def filter_reviewer_info(info):
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



def filter_review_rate(rate):
    """
    비동기 전환용 코드 : 별점 정보 변환
    
    parameters ]
        rate    : str   - 별점(형식 : width:{percent}%)
        
    return ]
        int - 1 ~ 5점사이 별점으로 formatted
    """
    return int(int(rate[6:-2]) / 20)



# 비동기 전환용 함수
def get_elemenet_text(el):
    return el.text



# 데이터 크롤링 함수
async def get_content_to_link(session, url):
    async with session.get(url) as res:
        if res.status == 200:
            
            # print(f'[SUCCESS] {url}')
            
            html = await res.text()
            soup = bs(html, 'lxml')
            
            # 리뷰 없는 경우
            if soup.select_one('article.no_result > .txt'): # '리뷰가 없습니다' 태그
                return None
            
            # div.content_wrap
            reviews = soup.select('div.content_wrap')
            
            reviewer_info_list = []
            review_rate_list = []
            neg_review_list = []
            pos_review_list = []
            
            for review in reviews:
                # 신고로 삭제된 경우
                # div.cont_discontinu.discontinu_category
                if review.select_one('div.cont_discontinu.discontinu_category'):
                    continue
                # 기업 추천 리뷰인 경우
                # div.card_right.flag_review
                if review.select_one('div.card_right.flag_review'):
                    continue
                # div.job_tooltip_box.top.hover
                if review.select_one('div.job_tooltip_box.top.hover'):
                    continue
                
                # 작성자 정보
                # div.content_top_ty2 : 작성자 정보가 담겨있는 태그
                # span.txt1 : [직무, (전직원|현직원), 지역, 작성 날짜] 의 연속으로 구성됨
                reviewer_info_tag = review.select_one('div.content_top_ty2')
                reviewer_info = [el.text.strip() for el in reviewer_info_tag.select('span.txt1')]
                
                # 길이가 3인 경우, 2번인덱스 값을 3번으로 복사
                # 마지막 인덱스의 값이 'yyyy. mm' 형식이 아닌 경우, 현재 날짜로 3번 인덱스에 추가
                if len(reviewer_info) == 3:
                    reviewer_info.append(reviewer_info[2])
                    if not re.search(r'\d{4}\.\s\d{2}', reviewer_info[3]):
                        reviewer_info[3] = datetime.now().strftime('%Y. %m')
                # 후처리
                reviewer_info = filter_reviewer_info(reviewer_info)
                
                # 별점 정보
                review_rate = filter_review_rate(review.select_one('div.star_score').attrs['style'])
                
                # 리뷰 내용
                neg_review = review.select_one('dt.disadvantages+dd > span').text.strip()
                pos_review = review.select_one('dt.merit+dd > span').text.strip()
                
                # 리스트에 추가
                reviewer_info_list.append(reviewer_info)
                review_rate_list.append(review_rate)
                neg_review_list.append(neg_review)
                pos_review_list.append(pos_review)
            
            return reviewer_info_list, review_rate_list, neg_review_list, pos_review_list
                
                
            
            # # =========================
            # # 작성자 정보 크롤링
            # # =========================
            # # span.txt1 : [직무, (전직원|현직원), 지역, 작성 날짜] 의 연속으로 구성됨
            # reviewer_infos = [el.text.strip() for el in soup.select('span.txt1')]
            
            # # print(reviewer_infos)
            
            # # '이 기업의 댓글'인 경우 제거
            # reviewer_infos = [el for el in reviewer_infos if '이 기업의 댓글' != el]
            
            # # print(reviewer_infos)
            
            # # 한 사람 단위로 잘라주기
            # # reviewer_infos = [reviewer_infos[i*4:(i*4+4)] for i in range(int(len(reviewer_infos) / 4))]
            # # 날자형식 'yyyy. mm'이 나올떄마다 나누어줌
            # # 또는 날자 형식이 없고 지역까지만 있을 경우, 
            # reviewer_infos_fix = []
            # infos = []
            # i = 0
            # for info, idx in zip(reviewer_infos, range(len(reviewer_infos))):
            #     i += 1
            #     infos.append(info)
            #     # 날짜 형식이 나오면, infos에 append하고 infos를 리셋
            #     if re.search(r'\d{4}\.\s\d{2}', info):
            #         reviewer_infos_fix.append(infos)
            #         infos = []
            #         i = 0
            #     # i가 3이지만, 날짜 형식이 아닌 경우, 
            #     # infos의 마지막 원소를 삭제하고,
            #     # infos에 append하고 infos를 리셋
            #     elif i == 4 and not re.search(r'\d{4}\.\s\d{2}', info):
            #         del infos[-1]
            #         # 현재 날자 'yyyy. mm'형식의 데이터를 만들어 입력
            #         infos.append(datetime.now().strftime('%Y. %m'))
            #         reviewer_infos_fix.append(infos)
            #         infos = []
            #         infos.append(info)
            #         i = 1
            #     else:
            #         continue
            
            # # reviewer_infos_fix 안의 리스트 길이가 4인 경우, 2번 인덱스 값을 삭제
            # for info in reviewer_infos_fix:
            #     if len(info) == 4:
            #         del info[2]

            # # split
            # reviewer_infos = asyncio.gather(*[filter_reviewer_info(info) for info in reviewer_infos_fix])
            # review_rates = asyncio.gather(*[filter_review_rate(el.attrs['style']) for el in soup.select('div.star_score')])
            
            # # get reviews content
            # neg_review = asyncio.gather(*[get_elemenet_text(el) for el in soup.select('dt.disadvantages+dd > span')])
            # pos_reivew = asyncio.gather(*[get_elemenet_text(el) for el in soup.select('dt.merit+dd > span')])
            
            # return reviewer_infos, review_rates, neg_review, pos_reivew
            



async def get_content_list(cookies, urls):
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        session.cookie_jar.update_cookies(cookies)
        result = await asyncio.gather(*[get_content_to_link(session, url) for url in urls]) # wrapping도 내부 처리
    
    return result

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
    
    # 데이터가 없는 경우
    if len(results) == 0:
        return False
    
    # 데이터 프레임으로 변환
    position = []
    is_office = []
    review_date = []
    review_rate = []
    neg_cont = []
    pos_cont = []
    
    for result in results:
        position.extend([el[0] for el in result[0]])
        is_office.extend([el[1] for el in result[0]])
        review_date.extend([el[2] for el in result[0]])
        
        review_rate.extend(result[1])
        
        neg_cont.extend(result[2])
        pos_cont.extend(result[3])
    
    # print(len(results), len(urls))
    # print(results)
    # for i in range(len(results)):
    #     result = results[i] # tuple
        
    #     position.extend([el[0] for el in result[0].result()])
    #     is_office.extend([el[1] for el in result[0].result()])
    #     review_date.extend([el[2] for el in result[0].result()])
        
    #     review_rate += result[1].result()
        
    #     neg_cont += result[2].result()
    #     pos_cont += result[3].result()
        
    # print(keyword)
    # print(len(position), len(is_office), len(review_date), len(review_rate), len(neg_cont), len(pos_cont))
    # print(position)
    # print(is_office)
    # print(review_date)
    # print(review_rate)
    # print(neg_cont)
    # print(pos_cont)
    
    pos_senit = ['P'] * len(pos_cont)
    neg_senit = ['N'] * len(neg_cont)
        
    df = pd.concat([
        pd.DataFrame({
            'review_date' : review_date,
            'is_office' : is_office,
            'review_cont' : pos_cont,
            'position' : position,
            'review_rate' : review_rate,
            'review_senti_orig' : pos_senit
        }), pd.DataFrame({
            'review_date' : review_date,
            'is_office' : is_office,
            'review_cont' : pos_cont,
            'position' : position,
            'review_rate' : review_rate,
            'review_senti_orig' : pos_senit
        }) ],
        join='outer',
        ignore_index=True
        ) # union, default
    # print(df)
    
    
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
        