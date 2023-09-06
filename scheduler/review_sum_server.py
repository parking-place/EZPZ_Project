import sys
import os
import pandas as pd

sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import cryptography
from tqdm import tqdm
import sql_connection as sc
from datetime import datetime

from service_models import ServiceModels

from privates.ezpz_db import *

col_name = ['review_uid', 'comp_uid', 'review_cont', 'review_senti_orig', 'review_senti_pred', 'review_rate', 'is_office', 'review_date', 'position', 'create_date', 'modify_date']

torch_models = ServiceModels() #모델 서빙 모듈 객체

today_date = datetime.today().strftime('%Y%m%d')

def get_all_comp_uid():
    comp_list = []
    sql = ' select comp_uid from comp_info where is_reged = "Y" ' #처리안된 회사들만 가져옴
    comp_temp_list = sc.conn_and_exec(sql)
    for comp in comp_temp_list:
        comp_list.append(comp[0])
    return comp_list

def delete_sum_review(comp_uid):
    # 해당 회사 리뷰 요약만 삭제하도록 수정해야함
    sql = f'delete from sum_review where comp_uid = {comp_uid}'
    sc.conn_and_exec(sql)
    # delete from comp_news where comp_uid = {comp_uid}
    pass

def get_revuews(comp_uid):
    sql = f'select * from comp_review where comp_uid = {comp_uid}'
    reviews = sc.conn_and_exec(sql)
    return reviews

def group_halfyear(df):
    if df['month'] <= 6:
        return 1
    else:
        return 2

def group_quater(df):
    if df['month'] <= 3:
        return 3
    elif df['month'] <= 6:
        return 4
    elif df['month'] <= 9:
        return 5
    else:
        return 6

def get_review_summary(review_list):
    pass

def get_keyword(review_list):
    pass

def get_mean_rate(df):
    mean_rate = df['review_rate'].mean()
    return mean_rate

def process_review(grouped_df):
    review_list = grouped_df['review_cont'].tolist()
    summary = get_review_summary(review_list)
    keyword = get_keyword(review_list)
    mean_rate = get_mean_rate(grouped_df)
    
    return {'summary': summary, 'mean_rate': mean_rate, 'keyword': keyword}

def add_value_to_sql(sql, comp_uid, year, term, summary, mean_rate, keyword):
    sql += 'INSERT INTO sum_review '
    sql += '(comp_uid, sum_year, sum_term, sum_cont, sum_keyword, avg_rate, create_date, modify_date) '
    sql += f'VALUES ({comp_uid}, {year:04d}, {term:02d}, "{summary}", "{keyword}", {mean_rate}, "{today_date}", "{today_date}");'
    return sql

def make_year_month_term(df):
    df['year'] = df['review_date'].apply(lambda x: x[:4]).apply(int)
    df['month'] = df['review_date'].apply(lambda x: x[5:7]).apply(int)
    df['halfyear'] = df.apply(group_halfyear, axis=1)
    df['quater'] = df.apply(group_quater, axis=1)
    return df

def summary_main():
    comp_list = get_all_comp_uid()
    
    for comp_uid in tqdm(comp_list):
        reviews = get_revuews(comp_uid)
        reviews_df = pd.DataFrame(reviews, columns=col_name)
        reviews_df = make_year_month_term(reviews_df)
        
        sql = ''
        
        year = '0000'
        term = '00'
        prosseced_output = process_review(reviews_df)
        add_value_to_sql(comp_uid, year, term, **prosseced_output)
        
        groupby_halfyear = reviews_df.groupby(['year', 'halfyear'])
        for df in groupby_halfyear:
            year = df['year'].iloc[0]
            term = df['halfyear'].iloc[0]
            prosseced_output = process_review(df)
            add_value_to_sql(comp_uid, year, term, **prosseced_output)
            
        groupby_quater = reviews_df.groupby(['year', 'quater'])
        for df in groupby_quater:
            year = df['year'].iloc[0]
            term = df['quater'].iloc[0]
            prosseced_output = process_review(df)
            add_value_to_sql(comp_uid, year, term, **prosseced_output)
        
        delete_sum_review(comp_uid)
        sc.conn_and_exec(sql)
        pass
    
    pass

if __name__ == "__main__":
    summary_main()