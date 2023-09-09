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
import tokenizer as tk

import re

from privates.ezpz_db import *

col_name = ['review_uid', 'comp_uid', 'review_cont', 'review_senti_orig', 'review_senti_pred', 'review_rate', 'is_office', 'review_date', 'position', 'create_date', 'modify_date']

torch_models = ServiceModels(type = 'reviews_sum') #모델 서빙 모듈 객체

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

def get_reviews(comp_uid):
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

def cleaning_text(text):
    pattern = r'[^0-9a-z가-힣\s\.]' # 숫자, 알파벳, 한글, 공백, 마침표만 남기고 삭제
    text = re.sub(pattern=pattern, repl='', string=text)
    text = text.strip()
    return text

def get_review_summary(review_list):
    all_sentences = ''.join(review_list)
    if len(all_sentences) > 10000:
        all_sentences = all_sentences[:10000]    
    review_summary = torch_models.get_summary(all_sentences, type='reviews_short')
    return review_summary

def get_keyword(review_list):
    keywords = tk.get_keyword_nng(review_list, 'review', size=10)
    keywords = [ word[0] + '_' + str(word[1]) for word in keywords ]
    hashtags = '#'.join(keywords)
    return hashtags

def get_mean_rate(df):
    mean_rate = df['review_rate'].mean()
    return mean_rate

def process_review(grouped_df):
    try:
        review_list = grouped_df['review_cont'].tolist()
        # summary = get_review_summary(review_list)
        keyword = get_keyword(review_list)
        mean_rate = get_mean_rate(grouped_df)
        
        pos_review_list = grouped_df[grouped_df['review_senti_orig'] == 'P']['review_cont'].tolist()
        neg_review_list = grouped_df[grouped_df['review_senti_orig'] == 'N']['review_cont'].tolist()
        
        summary_pos = get_review_summary(pos_review_list)
        summary_neg = get_review_summary(neg_review_list)
        keyword_pos = get_keyword(pos_review_list)
        keyword_neg = get_keyword(neg_review_list)
        
        
        return {
            'keyword': keyword,
            'mean_rate': mean_rate,
            'summary_pos': summary_pos,
            'summary_neg': summary_neg,
            'keyword_pos': keyword_pos,
            'keyword_neg': keyword_neg,
        }
    except Exception as e:
        print(e)
        return False

# def get_sql(comp_uid, year, term, summary, mean_rate, keyword):
#     # print(f'comp_uid: {comp_uid}, year: {year}, term: {term}, summary: {summary}, mean_rate: {mean_rate}, keyword: {keyword}')
#     summary = summary.replace('"', '\\"').replace("'", "\\'")
    
#     sql = 'insert into sum_review '
#     sql += '    (comp_uid, sum_year, sum_term, sum_cont, sum_keyword, avg_rate, create_date, modify_date) '
#     sql += 'values ( '
#     sql += f'{comp_uid}, "{year:04d}", "{term:02d}", "{summary}", "{keyword}", {mean_rate}, "{today_date}", "{today_date}" '
#     sql += ');\n '
#     return sql

def get_sql(comp_uid, year, term, summary_pos, summary_neg, keyword, keyword_pos, keyword_neg, mean_rate ):
    summary_pos = summary_pos.replace('"', '\\"').replace("'", "\\'")
    summary_neg = summary_neg.replace('"', '\\"').replace("'", "\\'")
    
    sql = 'insert into sum_review '
    sql += '    (comp_uid, sum_year, sum_term, sum_cont_pos, sum_cont_neg, sum_keyword, sum_keyword_pos, sum_keyword_neg, avg_rate, create_date, modify_date) '
    sql += 'values ( '
    sql += f'{comp_uid}, "{year:04d}", "{term:02d}", "{summary_pos}", "{summary_neg}", "{keyword}", "{keyword_pos}", "{keyword_neg}", {mean_rate}, "{today_date}", "{today_date}" '
    sql += ');\n '
    return sql

def save_to_db(sql):
    try:
        sc.conn_and_exec(sql)
    except Exception as e:
        print(sql)
        print(e)
        pass

def make_year_month_term(df):
    df['year'] = df['review_date'].apply(lambda x: x[:4]).apply(int)
    df['month'] = df['review_date'].apply(lambda x: x[4:6]).apply(int)
    df['halfyear'] = df.apply(group_halfyear, axis=1)
    df['quater'] = df.apply(group_quater, axis=1)
    return df

def summary_main():
    comp_list = get_all_comp_uid()
    
    for comp_uid in tqdm(comp_list):
        reviews = get_reviews(comp_uid)
        reviews_df = pd.DataFrame(reviews, columns=col_name)
        reviews_df = make_year_month_term(reviews_df)
        
        delete_sum_review(comp_uid)
        
        year = 0
        term = 0
        prosseced_output = process_review(reviews_df)
        if prosseced_output is False:
            continue
        sql = get_sql(comp_uid, year, term, **prosseced_output)
        save_to_db(sql)
        
        groupby_halfyear = reviews_df.groupby(['year', 'halfyear'])
        for (year, term), df in groupby_halfyear:
            prosseced_output = process_review(df)
            if prosseced_output is False:
                continue
            sql = get_sql(comp_uid, year, term, **prosseced_output)
            save_to_db(sql)
            
        groupby_quater = reviews_df.groupby(['year', 'quater'])
        for (year, term), df in groupby_quater:
            prosseced_output = process_review(df)
            if prosseced_output is False:
                continue
            sql = get_sql(comp_uid, year, term, **prosseced_output)
            save_to_db(sql)
        
        # print('SQL: ', sql)

if __name__ == "__main__":
    summary_main()
    
    
############################################################################################################
# 긍정 부정 리뷰 따로 저장해야 함