import requests as req
import pandas as pd

import json

# constants
SAVE_PATH = './datas/recruit'

V_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
WANTED_SEARCH ='https://www.wanted.co.kr/api/chaos/search/v1/results?1691048648606=&query={}&country=kr&job_sort=company.response_rate_order&years=-1&locations=all'
WANTED_JOB = 'https://www.wanted.co.kr/api/v4/jobs/{}'

def get_recruit_details(uid):
    """
    원티드 채용공고 uid로 상세 설명을 받아오는 함수.
    get_recruit_info()에서 사용합니다.
    
    parameters ]
        uid : str - 원티드 채용공고 id
    
    returns ]
        str : substring 된 intro
    """
    
    # 크롤링 시작
    headers = {
        'user-agent': V_AGENT,
        'Referer': f'https://www.wanted.co.kr/wd/{uid}'
    }
    result = json.loads(req.get(WANTED_JOB.format(uid, 1), headers=headers).text)
    result = result['job']['detail']['intro'][:200]
    
    return result



def get_recruit_info(keyword, csv_save=False):
    """
    기업명을 키워드로 받아 원티드(wanted.co.kr)에서 채용공고를 크롤링 해,
    dataframe으로 반환하는 함수
    
    parameters ]
        keyword     : str   - 검색할 키워드
        csv_save    : bool  - True 설정시 저장 및 로그 기록
    
    returns ]
        padnas.DataFrame
        col ]
            recruit_uid : 원티드 채용공고 ID
            recruit_url : 채용공고 URL
            recruit_position : 채용 포지션
            recruit_thumb : 채용공고 썸네일
            recruit_desc : 채용공고 세부 내용
    """
    # CSV 저장 설정 : import, start time 계측
    if csv_save:
        import os
        import time
        from datetime import date
        st_time = time.time()
    
    # 크롤링 시작
    headers = {
        'user-agent': V_AGENT,
        'Referer': f'https://www.wanted.co.kr/search?query={keyword.encode("UTF-8").decode("iso-8859-1")}'
    }
    
    # return : JSON
    result = json.loads(req.get(WANTED_SEARCH.format(keyword, 1), headers=headers).text)
    result = result['positions']['data']
    
    # dataframe으로 변환
    df = pd.DataFrame({
        'recruit_uid': [{el['id']} for el in result],
        'recruit_url': [f"https://www.wanted.co.kr/wd/{el['id']}" for el in result],
        'recruit_position': [el['position'] for el in result],
        'recruit_thumb': [el['title_img']['origin'] for el in result],
        'recruit_desc': [get_recruit_details(el['id']) for el in result]
    })
    
    # ========== [이하는 csv 저장 로직] ==========
    if csv_save:
        os.makedirs(SAVE_PATH, exist_ok=True) # 디렉토리 생성
        df.to_csv(os.path.join(SAVE_PATH, f'{keyword}_daum.csv'), index=False)
    
        # logging
        ed_time = time.time()
        TODATE = date.today().strftime("%Y%m%d")
        
        print(f'[CSV SAVED] {TODATE} - {SAVE_PATH}/{keyword}_daum.csv at {(ed_time - st_time):.5f} sec')
        
    return df

print(get_recruit_info('카카오'))