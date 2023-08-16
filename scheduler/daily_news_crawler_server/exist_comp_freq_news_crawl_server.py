import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/news') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import socket
import cryptography

from service_models import ServiceModels



import daum_news_crawler
import naver_news_crawler
import news_crawlers

from privates.ezpz_db import *

data_check= ServiceModels() #모델 서빙 모듈 객체
conn = get_connection('test')
cur = conn.cursor()

def crawl_and_save(comp_list): # 뉴스크롤링 테이블에 넣을 모든 정보 만들어줌 카카오 네이버 구글
    
    
    cur.execute('truncate table comp_news') #기존 뉴스정보 테이블 삭제
    

    for comp in comp_list:
        print(comp)
        daum_news = daum_news_crawler.get_news(comp).head(1) #다음뉴스 크롤러 실행 확인
        naver_news = naver_news_crawler.get_news(comp).head(1) #네이버 뉴스크롤러 실행
        all_news = pd.concat([daum_news, naver_news], ignore_index=True)  #뉴스 전체 합치기
        print(all_news)
        for index, col in enumerate(all_news['news_cont']):
            if len(col)>5000:
                all_news['news_cont'].iloc[index] = col[:5000] #5000자 이상은 cut이므로 이걸로 체크

        #모델 돌리기
        cont_sum_list= [] #df에 넣어줄 요약 리스트
        cont_sent_list=[] # df에 넣어줄 감정평가 리스트
        senti_to_int=[] # 감정을 정수형으로 바꿔줄 리스트

        for text in all_news['news_cont']:
            cont_sum=data_check.get_summary(text, 'news')
            cont_sum_list.append(cont_sum)
            
        
        for text in cont_sum_list:
            cont_sent=data_check.get_sentiment(text)
            cont_sent_list.append(cont_sent)
            # df_news_senti에 값을 0(중립), 1(긍정), 2(부정)으로 바꿔줘야함
        
        for col in (cont_sent_list):
            if col =='neutral':
                senti_to_int.append(0)
            elif col =='positive':
                senti_to_int.append(1)
            else:
                senti_to_int.append(2)
        
        #데이터프레임에 요약 결과와 감정평가 결과 넣어주기
        all_news['news_sum'] = cont_sum_list
        all_news['news_senti'] = senti_to_int

        for index,col in enumerate(all_news['news_sum']):
            if len(col)>256:
                all_news['news_sum'].iloc[index] = col[:256] #5000자 이상은 cut이므로 이걸로 체크

        #기사 내용과 요약본에 따옴표들 전부 삭제 전처리
        clean_cont=[]
        clean_sum=[]
        for i in all_news['news_cont']:
            
            cont_clean = i.replace('"', '').replace("'", '')
            clean_cont.append(cont_clean)
            


        for j in all_news['news_sum']:
            sum_clean = j.replace('"', '').replace("'", '')
            clean_sum.append(sum_clean)

        all_news['news_cont']= clean_cont
        all_news['news_sum'] = clean_sum         
        
        get_comp_news_db(all_news,comp) #실행될때마다 바뀌는 기업별 all_news 테이블화 시키기

            

                
    return True

def get_comp_news_db(all_news,comp): # 만들어진 데이터프레임을 테이블로
    cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"') 
    comp_uid=cur.fetchall()[0][0]
    # news_uid는 auto increment니까 자동생성되지 않을까?
    for index, row in all_news.iterrows():
            sql = 'insert into comp_news '
            sql += '    (comp_uid, pub_date, news_url, news_cont,news_sum, news_senti, create_date, modify_date) '
            sql += 'values ( '
            sql += f'   "{comp_uid}", "{row["pub_date"]}", "{row["news_url"]}", "{row["news_cont"]}", "{row["news_sum"]}", "{row["news_senti"]}" '
            sql += f'    , "{"00000000"}", "{"00000000"}" '
            sql += ') '
            cur.execute(sql)
            conn.commit()

    
    #cur.execute('select * from comp_news')
    #for i in cur:
    #    print(i)
            


if __name__ == '__main__':

    cur.execute('select * from comp_news')
    for i in cur:
        print(i)

    comp_list=['삼성전자(주)','(주)카카오','네이버(주)']
    crawl_and_save(comp_list)

    print('get_news_crawl 실행 완료')

    cur.execute('select * from comp_news')
    for i in cur:
        print(i)
    
    conn.close()
    
    ''' print(df.head())
    print(df.shape) '''
    