import sys
import os
import pandas as pd


sys.path.append('/app/EZPZ_Project/modules/crawlers/reviews') # 뉴스 정보 크롤러 경로
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import cryptography
from tqdm import tqdm
import sql_connection as sc
from datetime import datetime

import new_catch
import jobplanetv2

from privates.ezpz_db import *

def get_all_comp_name_and_uid():
    comp_list = []
    sql = ' select comp_name, comp_jpuid, comp_ctuid from comp_info where is_reged = "Y" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    for comp in comp_temp_list:
        comp_list.append(comp[0])
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨

def crawl_and_save(comp_list):
    sql = 'truncate table comp_review'
    sc.conn_and_exec(sql)
    
    for comp_name in comp_list:
        catch_review = new_catch.get_review(comp_name, save = False)
        jobplanet_review = jobplanetv2.get_review(comp_name, csv_save = False)
        
        print(catch_review)
        
        all_review = pd.concat([catch_review, jobplanet_review], ignore_index=True)
        
        print(all_review)
        pass
    pass

#테스트용으로 사용하세요
if __name__ == '__main__':

    comp_list = get_all_comp_name_and_uid()
    comp_list = ['한국은행']
    crawl_and_save(comp_list)

    #print('뉴스정보 전부 DB저장 완료')