import sys
import os
import pandas as pd

sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import cryptography
from tqdm import tqdm, tqdm_pandas
import sql_connection as sc
from datetime import datetime

from service_models import ServiceModels

from privates.ezpz_db import *

torch_model = ServiceModels(type='reviews_senti') #모델 서빙 모듈 객체

tqdm.pandas()

def get_all_reviews():
    # 예측 안된 리뷰만 가져오기
    sql = 'select review_uid, review_cont from comp_review where review_senti_pred is null'
    reviews = sc.conn_and_exec(sql)
    reviews = pd.DataFrame(reviews, columns = ['review_uid', 'review_cont'])
    return reviews

def get_senti(review):
    senti = torch_model.get_reviews_sentiment(review)
    return senti

def update_db(reviews):
    datas = [ (row.review_uid, row.review_senti_pred) for row in reviews.itertuples() ]
    
    sql = 'update comp_review set review_senti_pred = %s where review_uid = %s'
    sc.conn_and_exec_many(sql, datas)

def review_senti_main():
    review_df = get_all_reviews()
    review_df['review_senti_pred'] = review_df['review_cont'].progress_apply(get_senti)
    update_db(review_df)

if __name__ == '__main__':
    review_senti_main()
