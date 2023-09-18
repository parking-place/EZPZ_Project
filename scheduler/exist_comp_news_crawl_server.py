
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

import re

import daum_news_crawler
import naver_news_crawler
import news_crawlers

from privates.ezpz_db import *

create_date = datetime.today().strftime('%Y%m%d')
modify_date = datetime.today().strftime('%Y%m%d')

def get_all_comp():
    comp_list = []
    sql = ' select comp_name, comp_uid from comp_info where is_reged = "Y" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    for comp_name, comp_uid in comp_temp_list:
        comp_list.append((comp_name, comp_uid))
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨

def delete_comp_news(comp_uid):
    sql = f'delete from comp_news where comp_uid = {comp_uid}'
    sc.conn_and_exec(sql)
    # delete from comp_news where comp_uid = {comp_uid}
    pass

def cleaning_text(text):
    # pattern = r'[^a-z가-힣\s\.]' # 알파벳, 한글, 공백, 마침표만 남기고 삭제
    # 숫자, 알파벳, 한글, 공백, 마침표, 쉼표만 남기고 삭제
    pattern = r'[^0-9a-zA-Z가-힣\s\.\,]'
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.strip()
    return text

def get_comp_news_db(all_news, comp_uid): # 만들어진 데이터프레임을 테이블로 만드는 함수

    create_date = datetime.today().strftime('%Y%m%d')
    modify_date = datetime.today().strftime('%Y%m%d')

    for index, row in tqdm(all_news.iterrows()):
        sql = 'insert into comp_news '
        sql += '    (comp_uid, pub_date, news_url, news_cont, create_date, modify_date) '
        sql += 'values ( '
        sql += f'   "{comp_uid}", "{row["pub_date"]}", "{row["news_url"]}", "{row["news_cont"]}", '
        sql += f'    ,"{create_date}", "{modify_date}" '
        sql += ') '
        sc.conn_and_exec(sql)

def save_to_db_many(datas):
    
    sql = 'insert into comp_news '
    sql += '    (comp_uid, pub_date, news_url, news_cont, create_date, modify_date) '
    sql += 'values ( '
    sql += '   %s, %s, %s, %s, %s, %s '
    sql += ') '
    
    try:
        sc.conn_and_exec_many(sql, datas)
    except Exception as e:
        print(e)
        print(datas)
        pass


def news_crawl_main(): # 뉴스크롤링 테이블에 넣을 모든 정보 만들어줌 카카오 네이버 구글
    
    comp_list = get_all_comp()
    
    datas = []

    for comp, comp_uid in tqdm(comp_list):
        
        #print(comp + '뉴스 크롤링시작')
        daum_news = daum_news_crawler.get_news(comp) #다음뉴스 크롤러 실행 확인
        #naver_news = naver_news_crawler.get_news(comp) #네이버 뉴스크롤러 실행
        #print(naver_news)
        #all_news = pd.concat([daum_news, naver_news], ignore_index=True)  #뉴스 전체 합치기
        all_news= daum_news
        #print(all_news)
        for index, col in enumerate(all_news['news_cont']):
            if len(col)>5000:
                all_news['news_cont'].iloc[index] = col[:5000] #5000자 이상은 cut이므로 이걸로 체크

        #기사 내용과 요약본에 따옴표들 전부 삭제 전처리
        clean_cont=[]
        
        all_news['news_cont'] = all_news['news_cont'].apply(lambda x: cleaning_text(x))
        all_news['modify_date'] = modify_date
        all_news['create_date'] = create_date
        
        for index, row in all_news.iterrows():
            data = (
                comp_uid,
                row['pub_date'],
                row['news_url'],
                row['news_cont'],
                create_date,
                modify_date
            )
            datas.append(data)
            
        delete_comp_news(comp_uid)
        save_to_db_many(datas)



#테스트용으로 사용하세요
if __name__ == '__main__':
    news_crawl_main()


