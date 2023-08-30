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

from tqdm import tqdm

def get_all_comp_name_and_uid():
    comp_list = []
    sql = ' select comp_name, comp_jpuid, comp_ctuid from comp_info where is_reged = "Y" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    comp_list = list(comp_temp_list)
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨

def crawl_and_save(comp_list):
    sql = 'truncate table comp_review'
    sc.conn_and_exec(sql)
    # print(comp_list[0])
    for comp_name, jp_uid, ct_uid in tqdm(comp_list):
        print(comp_name)
        catch_reviews = new_catch.get_review(comp_name, ct_uid, save = False)
        jobplanet_reviews = jobplanetv2.get_review(comp_name, jp_uid, csv_save = False)
        # jobplanet_reviews = False
        # print(catch_reviews)
        # print(jobplanet_reviews)
        if catch_reviews is False and jobplanet_reviews is False:
            print(comp_name, '리뷰 없음')
            continue
        elif catch_reviews is False:
            all_reviews = jobplanet_reviews
        elif jobplanet_reviews is False:
            all_reviews = catch_reviews
        else:
            all_reviews = pd.concat([catch_reviews, jobplanet_reviews], ignore_index=True)
        
        print(len(all_reviews))
        pass
    pass

#테스트용으로 사용하세요
if __name__ == '__main__':

    comp_list = get_all_comp_name_and_uid()
    # comp_list = [('이롭게', '89342', None)]
    crawl_and_save(comp_list[:50])

    #print('뉴스정보 전부 DB저장 완료')