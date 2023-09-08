import sys
import os
import pandas as pd

sys.path.append('/app/EZPZ_Project/modules/torchmodules') # 토치 모델 뉴스 요약 및 감정평가 가져오기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

import cryptography
from tqdm import tqdm, tqdm_pandas
import sql_connection as sc
from datetime import datetime
import time

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
    datas = [ (row.review_senti_pred, row.review_uid) for row in reviews.itertuples() ]
    
    sql = 'update comp_review set review_senti_pred = %s where review_uid = %s'
    sc.conn_and_exec_many(sql, datas)

def review_senti_main():
    review_df = get_all_reviews()
    review_df['review_senti_pred'] = review_df['review_cont'].progress_apply(get_senti)
    
    if len(review_df) == 0:
        print('예측할 리뷰가 없습니다.')
        return
    
    s_time = time.time()
    update_db(review_df)
    e_time = time.time()
    print(f'예측된 리뷰 {len(review_df)}개 업데이트 완료. DB 적용 소요시간: {e_time - s_time}')

if __name__ == '__main__':
    review_senti_main()
