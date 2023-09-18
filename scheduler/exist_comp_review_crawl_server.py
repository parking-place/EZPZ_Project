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

import re

from privates.ezpz_db import *

from tqdm import tqdm

def get_all_comp_name_and_uid():
    comp_list = []
    sql = ' select comp_uid, comp_name, comp_jpuid, comp_ctuid from comp_info where is_reged = "Y" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    comp_list = list(comp_temp_list)
    return comp_list #리스트 받아와서 is reged y 회사마다 바꿔주고 modify_date만 바꿔주면됨

def delete_comp_review(comp_uid):
    sql = f'delete from comp_review where comp_uid = {comp_uid}'
    sc.conn_and_exec(sql)

def crawl_review(comp_list):
    comp_bar = tqdm(comp_list,
                    position=0,
                    leave=True,
                    )
    for comp_uid, comp_name, jp_uid, ct_uid in comp_bar:
        
        comp_bar.set_description(comp_name)
        
        catch_reviews = new_catch.get_review(comp_name, ct_uid, save = False)
        jobplanet_reviews = jobplanetv2.get_review(comp_name, jp_uid, csv_save = False)
        # jobplanet_reviews = False
        # print(catch_reviews)
        # print(jobplanet_reviews)
        if catch_reviews is False and jobplanet_reviews is False:
            comp_bar.set_description(comp_name + ' : ' + 'No Reviews')
            continue
        elif catch_reviews is False:
            all_reviews = jobplanet_reviews
        elif jobplanet_reviews is False:
            all_reviews = catch_reviews
        else:
            all_reviews = pd.concat([catch_reviews, jobplanet_reviews], ignore_index=True)
        comp_bar.set_description(comp_name + ' : ' + str(len(all_reviews)))
        # 기존 리뷰 삭제
        delete_comp_review(comp_uid)
        # 리뷰 저장
        save_to_db(all_reviews, comp_name)
        
        comp_bar.set_description(comp_name + ' : ' + 'Saved')
        
    comp_bar.close()
    
    return 

def cleaning_text(text):
    # pattern = r'[^a-z가-힣\s\.]' # 알파벳, 한글, 공백, 마침표만 남기고 삭제
    # 숫자, 알파벳, 한글, 공백, 마침표, 쉼표만 남기고 삭제
    pattern = r'[^0-9a-zA-Z가-힣\s\.\,]'
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.strip()
    return text

def str_replaces(st_data):
    return str.replace('\"', '').replace("\'", '').replace('\\', '').replace('\n', ' ').replace('\r', '').replace('\t', '').replace('\b', '').replace('\f', '').replace('\a', '').replace('\v', '').replace('\0', '').replace('"', '').replace("'", '')
    

def save_to_db(df, comp_name):
    #cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"')
    replace_comp_name = comp_name.replace(' ','')
    sql = f'select comp_uid from comp_info where replace(comp_name , " ", "") like "%{replace_comp_name}%" '
    comp_uid= sc.conn_and_exec(sql)[0][0]

    create_date = datetime.today().strftime('%Y%m%d')
    modify_date = datetime.today().strftime('%Y%m%d')
    
    datas = []
    for _index, row in df.iterrows():
        data = (
            comp_uid,
            cleaning_text(row['review_cont'][:1000]),
            row['review_senti_orig'],
            row['review_rate'],
            int(row['is_office']),
            row['review_date'],
            row['position'],
            create_date,
            modify_date
        )

        datas.append(data)
    
    sql = 'insert into comp_review '
    sql += '    (comp_uid, review_cont, review_senti_orig, review_rate, is_office, review_date, position, create_date, modify_date) '
    sql += 'values ( '
    sql += '   %s, %s, %s, %s, %s, %s, %s, %s, %s '
    sql += ') '
    
    sc.conn_and_exec_many(sql, datas)

def review_crawling_main():
    comp_list = get_all_comp_name_and_uid()
    crawl_review(comp_list)

# 스크립트 실행시 실행되는 영역
if __name__ == '__main__':
    review_crawling_main()