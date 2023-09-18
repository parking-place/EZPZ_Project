import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/news') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project/modules/crawlers/job_post') #채용공고 크롤러
sys.path.append('/app/EZPZ_Project/modules/crawlers/comp_info') #기업 정보 크롤러
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import sql_connection as sc #mysql connection
from tqdm import tqdm
from datetime import datetime

import info_crawler #기업정보 크롤러


from privates.ezpz_db import * #db연동 정보

#get_comp_list로 update해야될 회사 리스트 받아서 crawler_exec(comp_list)에 받은 리스트 넣어줌

#여기서 함수를 실행해서 각종 정보들 실행
def crawler_exec(comp_list):
    comp_info_crawl_save(comp_list)
    # comp_news_crawl_save(comp_list)
    # recruit_info_crawl(comp_list)
    # comp_review_crawl_save(comp_list) #리뷰 크롤러 serving

def get_comp_list():
    comp_list = []
    sql = ' select comp_uid, comp_jpuid, comp_name from comp_info where is_reged = "N" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    for comp_uid, comp_jpuid, comp_name in comp_temp_list:
        comp_list.append((comp_uid, comp_name))
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨


def comp_info_crawl_save(comp_list):    
    datas = []
    for comp_uid, comp_jpuid, comp in tqdm(comp_list):

        comp_info_df=info_crawler.get_url(comp_jpuid) #info_crawler 기업정보 데이터 프레임 저장
        comp_info_df['comp_cont']=comp_info_df['comp_cont'].iloc[0][0]
        # 기업 정보 리스트로 저장해서 데이터프레임에 넣어줄수 있게
        col_value=[]
        for i in comp_info_df.iloc[0]:
            col_value.append(i) #테이블에 insert할 수 있는 컬럼값들을 리스트화
        #create_date = datetime.today().strftime('%Y%m%d')
        modify_date = datetime.today().strftime('%Y%m%d')

        col_value[0] = col_value[1].strip() #좌우 공백제거
        col_value[4]=col_value[4][0:7]
        col_value[4] = col_value[4].replace(".", "")
        col_value[4] # 6글자 문자열로 변환 테이블에 형식대로

        #크롤링해온 값 테이블에 저장 저장일자와 수정일자는 스케줄링단계에서 진행이므로 일단 00000000 넣어두었음
        #sql = 'INSERT INTO comp_info '
        #sql += '(comp_name, comp_loc, comp_thumb, comp_cont, comp_founded, comp_size, comp_url, is_reged, modify_date) '
        #sql += f'VALUES (%s, %s, %s, %s, %s, %s, %s, "Y", "{modify_date}")'
        data = (
            col_value[1], 
            col_value[2], 
            col_value[3], 
            col_value[4], 
            col_value[5], 
            col_value[6], 
            col_value[7], 
            modify_date, 
            comp_uid
            )

    sql = ' UPDATE comp_info '
    sql += ' SET comp_loc=%s, comp_thumb=%s, comp_cont=%s, comp_founded=%s, comp_size=%s, comp_url=%s, comp_ctuid=%s, is_reged="Y", modify_date= %s '
    sql += ' WHERE comp_uid=%s'
    # sc.conn_and_exec(sql, (col_value[1], col_value[2], col_value[3], col_value[4], col_value[5], col_value[6], col_value[7], modify_date,comp))
    sc.conn_and_exec_many(sql, datas)

        #print(f'{comp} 정보 insert 됨')

#테스트용으로 사용하세요
if __name__ == '__main__':
    comp_list=get_comp_list()
    crawler_exec(comp_list)


    #print('comp_list 실행 완료')
