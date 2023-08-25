import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/news') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project/modules/crawlers/job_post') #채용공고 크롤러
sys.path.append('/app/EZPZ_Project/modules/crawlers/comp_info') #기업 정보 크롤러
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import pymysql
import cryptography
import sql_connection as sc #mysql connection
from tqdm import tqdm
from datetime import datetime

from service_models import ServiceModels

import daum_news_crawler #다음뉴스크롤러
import naver_news_crawler #네이버 뉴스크롤러
import news_crawlers #네이버 뉴스 크롤러2
import wanted_recruit_crawler #채용공고 크롤러
import info_crawler #기업정보 크롤러


from privates.ezpz_db import * #db연동 정보


data_check= ServiceModels() #모델 서빙 모듈 객체

#get_comp_list로 update해야될 회사 리스트 받아서 crawler_exec(comp_list)에 받은 리스트 넣어줌

#여기서 함수를 실행해서 각종 정보들 실행
def crawler_exec(comp_list):
    #comp_info_crawl_save(comp_list)
    # #값들을 전부 넣어줬으니 update y로
    #sql= ' UPDATE comp_info SET is_reged = "Y" '
    #sc.conn_and_exec(sql)
    # cur.execute('UPDATE comp_info SET is_reged = "Y" ')
    #comp_news_crawl_save(comp_list)
    recruit_info_crawl(comp_list)
    #comp_review_crawl_save(comp_list) #리뷰 크롤러 serving


def get_comp_list():
    comp_list = []
    sql = ' select comp_name from comp_info where is_reged = "N" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    for comp in comp_temp_list:
        comp_list.append(comp[0])
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨

def comp_info_crawl_save(comp_list):
    for comp in tqdm(comp_list):
        comp_info_df=info_crawler.get_url(comp) #info_crawler 기업정보 데이터 프레임 저장
        comp_info_df['comp_cont']=comp_info_df['comp_cont'].iloc[0][0]
        # 기업 정보 리스트로 저장해서 데이터프레임에 넣어줄수 있게
        col_value=[]
        for i in comp_info_df.iloc[0]:
            col_value.append(i) #테이블에 insert할 수 있는 컬럼값들을 리스트화
        #create_date = datetime.today().strftime('%Y%m%d')
        modify_date = datetime.today().strftime('%Y%m%d')

        col_value[1] = col_value[1].strip() #좌우 공백제거
        col_value[5]=col_value[5][0:7]
        col_value[5] = col_value[5].replace(".", "")
        col_value[5] # 6글자 문자열로 변환 테이블에 형식대로

        #크롤링해온 값 테이블에 저장 저장일자와 수정일자는 스케줄링단계에서 진행이므로 일단 00000000 넣어두었음
        #sql = 'INSERT INTO comp_info '
        #sql += '(comp_name, comp_loc, comp_thumb, comp_cont, comp_founded, comp_size, comp_url, is_reged, modify_date) '
        #sql += f'VALUES (%s, %s, %s, %s, %s, %s, %s, "Y", "{modify_date}")'

        sql = ' UPDATE comp_info '
        sql += ' SET comp_loc=%s, comp_thumb=%s, comp_cont=%s, comp_founded=%s, comp_size=%s, comp_url=%s, is_reged="Y", modify_date= %s '
        sql += ' WHERE comp_name=%s '
        #cur.execute(sql, (col_value[2], col_value[3], col_value[4], col_value[5], col_value[6], col_value[7], col_value[1]))
        #cur.execute(sql, (col_value[1], col_value[2], col_value[3], col_value[4], col_value[5], col_value[6], col_value[7]))
        sc.conn_and_exec(sql, (col_value[2], col_value[3], col_value[4], col_value[5], col_value[6], col_value[7],modify_date,comp))

        #print(f'{comp} 정보 insert 됨')




#얘 잘되는지는 .py 파일에서 확인
def comp_news_crawl_save(comp_list):

        for comp in tqdm(comp_list):
            daum_news = daum_news_crawler.get_news(comp) #다음뉴스 크롤러 실행 확인
            # naver_news = naver_news_crawler.get_news(comp) #네이버 뉴스크롤러 실행
            # print(naver_news)

            # all_news = pd.concat([daum_news, naver_news], ignore_index=True)  #뉴스 전체 합치기
            all_news = daum_news


            for index, col in enumerate(all_news['news_cont']):
                if len(col)>5000:
                    all_news['news_cont'].iloc[index] = col[:5000] #5000자 이상은 cut이므로 이걸로 체크

            #모델 돌리기
            cont_sum_list= [] #df에 넣어줄 요약 리스트
            cont_sent_list=[] # df에 넣어줄 감정평가 리스트
            senti_to_int=[] # 감정을 정수형으로 바꿔줄 리스트

            for text in all_news['news_cont']: #크롤링한 뉴스 요약
                cont_sum=data_check.get_summary(text, 'news')
                cont_sum_list.append(cont_sum)

            for text in cont_sum_list: #요약한 뉴스 감정평가
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

            get_comp_news_db(all_news,comp) #기업별 news 테이블화 시키기



def get_comp_news_db(all_news,comp): # 만들어진 데이터프레임을 테이블로
    #cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"')
    print(comp)
    replace_comp = comp.replace(' ','')
    print(replace_comp)
    sql = f'select comp_uid from comp_info where replace(comp_name , " ", "") like "%{replace_comp}%" '
    print(sql)
    uid = sc.conn_and_exec(sql)
    comp_uid= uid[0][0]

    create_date = datetime.today().strftime('%Y%m%d')
    modify_date = datetime.today().strftime('%Y%m%d')
    # news_uid는 auto increment니까 자동생성되지 않을까?
    for index, row in all_news.iterrows():
            sql = 'insert into comp_news '
            sql += '    (comp_uid, pub_date, news_url, news_cont,news_sum, news_senti, create_date, modify_date) '
            sql += 'values ( '
            sql += f'   "{comp_uid}", "{row["pub_date"]}", "{row["news_url"]}", "{row["news_cont"]}", "{row["news_sum"]}", "{row["news_senti"]}" '
            sql += f'    , "{create_date}", "{modify_date}" '
            sql += ') '
            #cur.execute(sql)
            sc.conn_and_exec(sql)


def recruit_info_crawl(comp_list):

    for comp in tqdm(comp_list):
        #채용공고는 주 붙어있으면 안됨 제거 전처리

        recruit_comp = comp.replace('(주)',"")
        #print(recruit_comp)
        recruit_info_df=wanted_recruit_crawler.get_recruit_info(recruit_comp, csv_save=False) # 원티드 기업정보 크롤러 모듈
        new_i=[] #집합인 uid를 int로 바꿔준 값을 넣어준 리스트/ 테이블에 넣기위한 전처리
        for i in range(len(recruit_info_df['recruit_uid'])):
            new_i.append(list(recruit_info_df['recruit_uid'][i])[0])
        recruit_info_df['recruit_uid']=new_i #int 값으로 컬럼 대체

        desc_list= []
        position_list = []
        for desc in recruit_info_df['recruit_desc']:
            desc = desc.replace('"', '').replace("'", '')
            desc_list.append(desc)
        recruit_info_df['recruit_desc'] = desc_list

        for position in recruit_info_df['recruit_position']:
            position = position.replace('"', '').replace("'", '')
            position_list.append(position)
        recruit_info_df['recruit_position'] = position_list

        #cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"')
        replace_comp = comp.replace(' ','')
        sql = f'select comp_uid from comp_info where replace(comp_name , " ", "") like "%{replace_comp}%" '
        uid = sc.conn_and_exec(sql)
        comp_uid= uid[0][0]

        create_date = datetime.today().strftime('%Y%m%d')
        modify_date = datetime.today().strftime('%Y%m%d')
        #print(comp_uid)
        for index, row in recruit_info_df.iterrows():
            sql = 'insert into recruit_info '
            sql += '    (comp_uid, recruit_uid, recruit_url, recruit_position, recruit_thumb, recruit_desc, create_date, modify_date) '
            sql += 'values ( '
            sql += f'   "{comp_uid}", "{row["recruit_uid"]}", "{row["recruit_url"]}", "{row["recruit_position"]}", "{row["recruit_thumb"]}", "{row["recruit_desc"]}" '
            sql += f'    , "{create_date}", "{modify_date}" '
            sql += ') '
            sc.conn_and_exec(sql)
            #cur.execute(sql)


def comp_review_crawl_save(comp_list):
    pass

#테스트용으로 사용하세요
if __name__ == '__main__':
    comp_list=get_comp_list()
    crawler_exec(comp_list)


    #print('comp_list 실행 완료')
