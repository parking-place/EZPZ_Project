import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/news') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project/modules/crawlers/job_post') #채용공고 크롤러
sys.path.append('/app/EZPZ_Project/modules/crawlers/comp_info') #기업 정보 크롤러
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import pymysql
import socket
import cryptography

from service_models import ServiceModels

import daum_news_crawler #다음뉴스크롤러
import naver_news_crawler #네이버 뉴스크롤러
import news_crawlers #네이버 뉴스 크롤러2
import wanted_recruit_crawler #채용공고 크롤러
import info_crawler #기업정보 크롤러

from privates.ezpz_db import * #db연동 정보

conn = get_connection('test')
cur = conn.cursor()

data_check= ServiceModels() #모델 서빙 모듈 객체


#여기서 함수를 실행해서 각종 정보들 실행
def crawler_exec(comp_list):
    comp_info_crawl_save(comp_list)
    comp_news_crawl_save(comp_list)
    recruit_info_crawl(comp_list)
    conn.commit()
    conn.close()

#먼저 comp_info 크롤링해와서 테이블에 넣어줘야겠지? 근데 no니까 is_reged 전부 y로 바꿔주고 나중에 테이블 전부다
def comp_info_crawl_save(comp_list):
    for comp in comp_list:
        comp_info_df=info_crawler.get_url(comp) #info_crawler 기업정보 데이터 프레임 잘 어울림
        # 기업 정보 리스트로 저장해서 데이터프레임에 넣어줄수 있게
        col_value=[]
        for i in comp_info_df.iloc[0]:
            col_value.append(i) #테이블에 insert할 수 있는 컬럼값들을 리스트화


        col_value[5]=col_value[5][0:7]
        col_value[5] = col_value[5].replace(".", "")
        col_value[5] # 6글자 문자열로 변환 테이블에 형식대로

        #크롤링해온 값 테이블에 저장 저장일자와 수정일자는 스케줄링단계에서 진행이므로 일단 000000 넣어두었음
        #일단 testdb를 경로로했는데 나중에 바꿔줘야됨
        cur.execute(f"INSERT INTO testdb.comp_info (comp_name, comp_loc, comp_thumb, comp_cont, comp_founded, comp_size, comp_url, is_reged, create_date, modify_date) VALUES (%s, %s, %s, %s, %s, %s, %s, 'N', '000000', '000000')", (col_value[1], col_value[2], col_value[3], col_value[4], col_value[5], col_value[6], col_value[7]))      
        
    #값들을 전부 넣어줬으니 update y로
    cur.execute('UPDATE comp_info SET is_reged = "Y" ')




#얘 잘되는지는 .py 파일에서 확인
def comp_news_crawl_save(comp_list):
        print('실행시작')
        for comp in comp_list:
            daum_news = daum_news_crawler.get_news(comp) #다음뉴스 크롤러 실행 확인
            naver_news = naver_news_crawler.get_news(comp) #네이버 뉴스크롤러 실행
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


def recruit_info_crawl(comp_list):
    print('실행시작')
    for comp in comp_list:
        #채용공고는 주 붙어있으면 안됨 제거 전처리
        recruit_comp = comp.replace('(주)',"")
        print(recruit_comp)
        recruit_info_df=wanted_recruit_crawler.get_recruit_info(recruit_comp, csv_save=False) # 원티드 기업정보 크롤러 모듈
        new_i=[] #집합인 uid를 int로 바꿔준 값을 넣어준 리스트/ 테이블에 넣기위한 전처리
        for i in range(len(recruit_info_df['recruit_uid'])):
            new_i.append(list(recruit_info_df['recruit_uid'][i])[0])
        recruit_info_df['recruit_uid']=new_i #int 값으로 컬럼 대체


        cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"') 
        comp_uid=cur.fetchall()[0][0]
        print(comp_uid)
        for index, row in recruit_info_df.iterrows():
            sql = 'insert into recruit_info '
            sql += '    (comp_uid, recruit_uid, recruit_url, recruit_position, recruit_thumb, create_date, modify_date) '
            sql += 'values ( '
            sql += f'   "{comp_uid}", "{row["recruit_uid"]}", "{row["recruit_url"]}", "{row["recruit_position"]}", "{row["recruit_thumb"]}" '
            sql += f'    , "{"00000000"}", "{"00000000"}" '
            sql += ') '
            cur.execute(sql)
            for i in cur:
                print(i)     


if __name__ == '__main__':


    comp_list=['삼성전자(주)','(주)카카오','네이버(주)']
    crawler_exec(comp_list)
    print('comp_list 실행 완료')

                    