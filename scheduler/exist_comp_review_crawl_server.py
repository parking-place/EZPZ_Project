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

def delete_comp_review(comp):
    sql = f'select comp_uid from comp_info where replace(comp_name , " ", "") like "%{comp}%" '
    comp_uid = sc.conn_and_exec(sql)
    comp_uid= comp_uid[0][0]
    sql = f'delete from comp_review where comp_uid = {comp_uid}'
    sc.conn_and_exec(sql)

def crawl_review(comp_list):
    # sql = 'truncate table comp_review'
    # sc.conn_and_exec(sql)
    
    # print(comp_list[0])
    comp_bar = tqdm(comp_list,
                    position=0,
                    leave=True,
                    )
    for comp_name, jp_uid, ct_uid in comp_bar:
        
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
        delete_comp_review(comp_name)
        # 리뷰 저장
        save_to_db(all_reviews, comp_name)
        
        comp_bar.set_description(comp_name + ' : ' + 'Saved')
        
    comp_bar.close()
    
    return 

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
            str_replaces(row['review_cont'][:1000]),
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
    
    # for index, row in df.iterrows():
    #     review = row['review_cont'][:1000].replace('"', '').replace("'", '').replace('\\', '').replace('\n', ' ')
        
    #     sql = 'insert into comp_review '
    #     sql += '    (comp_uid, review_cont, review_senti_orig, review_rate, is_office, review_date, position, create_date, modify_date) '
    #     sql += 'values ( '
    #     sql += f'   "{comp_uid}", "{review}", "{row["review_senti_orig"]}", "{row["review_rate"]}", "{int(row["is_office"])}", "{row["review_date"]}", "{row["position"]}" '
    #     sql += f'    ,"{create_date}", "{modify_date}" '
    #     sql += ') '
    #     try :
    #         sc.conn_and_exec(sql)
    #     except Exception as e:
    #         print(sql)
    #         print(row)
    #         print(e)
    #         continue

#테스트용으로 사용하세요
if __name__ == '__main__':

    comp_list = get_all_comp_name_and_uid()
    crawl_review(comp_list)
    # comp_list = [('(주)트레드링스', '318498', None)]
    # crawl_review(comp_list)

    #print('뉴스정보 전부 DB저장 완료')