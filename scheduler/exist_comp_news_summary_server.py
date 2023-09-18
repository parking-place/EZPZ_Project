import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/news') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import cryptography
from tqdm import tqdm
import sql_connection as sc
from datetime import datetime

from service_models import ServiceModels

import re

import daum_news_crawler
import naver_news_crawler
import news_crawlers

from privates.ezpz_db import *

torch_models = ServiceModels(tpye = 'news') #모델 서빙 모듈 객체

modify_date = datetime.today().strftime('%Y%m%d')

tqdm.pandas()

def get_all_news():
    '''
    뉴스중에서 요약이 안된 뉴스들만 가져는 함수
    '''
    news_list = []
    sql = 'select news_uid, news_cont from news_info where news_sum is null'
    all_news = sc.conn_and_exec(sql)
    for news in all_news:
        news_list.append(news)
    return news_list

def cleaning_text(text):
    '''
    뉴스 내용에서 필요없는 문자들을 제거하는 함수
    '''
    # pattern = r'[^a-z가-힣\s\.]' # 알파벳, 한글, 공백, 마침표만 남기고 삭제
    # 숫자, 알파벳, 한글, 공백, 마침표, 쉼표만 남기고 삭제
    pattern = r'[^0-9a-zA-Z가-힣\s\.\,]'
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.strip()
    return text

def save_to_db_many(datas):
    '''
    뉴스 요약 및 감정평가를 통해 나온 데이터를 db에 저장하는 함수
    data = (news_sum, news_senti, modify_date, news_uid)
    '''
    sql = 'update comp_news set news_sum = %s, news_senti = %s, modify_date = %s where news_uid = %s'
    
    try:
        sc.conn_and_exec_many(sql, datas)
    except Exception as e:
        print(e)
        print(datas)
        pass
    
def get_news_sum(news_cont):
    '''
    뉴스 내용을 요약하는 함수
    '''
    news_sum = torch_models.get_summary(news_cont)
    return news_sum

def get_news_senti(news_sum):
    '''
    뉴스 요약본을 감정평가하는 함수
    '''
    news_senti = torch_models.get_sentiment(news_sum)
    return cleaning_text(news_senti[:256])

def senti_to_int(news_senti):
    '''
    감정평가 결과를 숫자로 변환하는 함수
    '''
    if news_senti == 'neutral':
        return 0
    elif news_senti == 'positive':
        return 1
    elif news_senti == 'negative':
        return 2
    else:
        return 0

def new_summary_senti_main():
    
    # 뉴스 불러오기
    news_list = get_all_news()
    # 뉴스 데이터프레임 만들기
    news_df = pd.DataFrame(news_list, columns=['news_uid', 'news_cont'])
    datas = []
    # 뉴스 내용 정제
    news_df['news_cont'] = news_df['news_cont'].apply(cleaning_text)
    # 뉴스 요약 및 감정평가
    news_df['news_sum'] = news_df['news_cont'].progress_apply(get_news_sum)
    # 뉴스 감정평가 결과 정제
    news_df['news_senti'] = news_df['news_sum'].progress_apply(get_news_senti).progress_apply(senti_to_int)
    news_df['modify_date'] = modify_date
    
    for index, row in news_df.iterrows():
        datas.append((row['news_sum'], row['news_senti'], row['modify_date'], row['news_uid']))
    
    save_to_db_many(datas)
    
if __name__ == '__main__':
    new_summary_senti_main()