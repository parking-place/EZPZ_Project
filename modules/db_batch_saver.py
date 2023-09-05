# import

import os 

import pymysql

import pandas as pd
import numpy as np

import itertools
from datetime import datetime

from model.tokenizer import tokenizer
from model.t5basesum

# tokenizer
from konlpy.tag import Hannanum
from kiwipiepy import Kiwi, basic_typos # Kiwi 오타정정 커스터마이징 모듈

# 키워드 추출
from collections import Counter




# 디렉터리 지정
DATA_PATH = './data/'
MODEL_PATH = './model/'

# 폴더 생성
os.makedirs(DATA_PATH, exist_ok=True)



################################################################
# 데이터 로드

df = pd.read_csv(DATA_PATH + 'comp_db.csv')

################################################################


### 변수 지정 - comp_uid, year, period
comp_uid = None     # int type  (ex. 777)
year = None         # int type  (ex. 2020)
period = None       # str type  (ex. 'H2', 'Q4')

comp_uid = 1000
year = 2020
period = 'H1'



### comp_uid 고유값 개수 = 리뷰가 등록된 기업들 수
comp_num = df['comp_uid'].nunique()


# 연도, 월 열 추가
df['year'] = df['review_data'].astype(str).str[:4]      # year
df['month'] = df['review_data'].astype(str).str[4:]     # month



# 반기 정보 추출 함수 정의
def extract_half(df : pd.DataFrame):
    if int(df['month']) <= 6:
        return 'H1'
    else:
        return 'H2'

# 'Half' 열 추가
df['half'] = df.apply(extract_half, axis=1)


# 분기 정보 추출 함수 정의
def extract_quarter(df : pd.DataFrame):
    if int(df['month']) <= 3:
        return 'Q1'
    elif int(df['month']) <= 6:
        return 'Q2'
    elif int(df['month']) <= 9:
        return 'Q3'
    else:
        return 'Q4'

# 'Quarter' 열 추가
df['quarter'] = df.apply(extract_quarter, axis=1)







# comp_uid 별로 데이터프레임 split

# 각각의 고유한 comp_uid 값을 키로 가지는 데이터프레임에 접근
grouped_df_dict = dict(tuple(df.groupby('comp_uid')))


def grouping_comp_df() : 

    # 각각의 고유한 comp_uid 값을 키로 가지는 데이터프레임에 접근
    
    for comp_uid in grouped_df_dict:
        grouped_df = grouped_df_dict[comp_uid]
        print(f"comp_uid : {comp_uid}")
        print(len(grouped_df))
    
    return print('\n' + f'등록 된 기업 수 : {comp_uid}')



# comp_uid를 입력하여 데이터프레임 호출
def get_comp_df(comp_uid : int) : 
        
    # 호출하고자 하는 comp_uid 입력

    if comp_uid in grouped_df_dict:
        grouped_df = grouped_df_dict[comp_uid]

    else:
        print(f"comp_uid를 다시 확인해주세요 : {comp_uid}")

    return grouped_df




# comp_uid를 받아 comp_df 생성
comp_df = get_comp_df(comp_uid)

# 데이터프레임 출력 
# comp_df 




# 반기 정보 추출 함수 정의
def extract_half(comp_df):
    if int(comp_df['month']) <= 6:
        return 'H1'
    else:
        return 'H2'

# 'Half' 열 추가
comp_df['half'] = comp_df.apply(extract_half, axis=1)


# 분기 정보 추출 함수 정의
def extract_quarter(comp_df):
    if int(comp_df['month']) <= 3:
        return 'Q1'
    elif int(comp_df['month']) <= 6:
        return 'Q2'
    elif int(comp_df['month']) <= 9:
        return 'Q3'
    else:
        return 'Q4'



# 'Quarter' 열 추가
comp_df['quarter'] = comp_df.apply(extract_quarter, axis=1)




# 필터
class Comp_Filter:

    def __init__(self, comp_uid, year, period):
        self.comp_uid = comp_uid
        self.year = year
        self.period = period


    def year_half(self):
        # comp_uid로부터 comp_df 가져오기
        comp_df = get_comp_df(self.comp_uid)

        # review_data를 기준으로 오름차순 정렬
        comp_df.sort_values(by='review_data', ascending=True, inplace=True)

        grouped_by_year_half = comp_df.groupby(['year', 'half'])

        df_by_year_half = {}

        for (y, h), group in grouped_by_year_half:
            df_by_year_half[(y, h)] = group

        if (str(self.year), str(self.period)) in df_by_year_half:
            return df_by_year_half[(str(self.year), str(self.period))]
        else:
            print(f"해당 연도: {self.year}, 반기: {self.period}에 대한 데이터가 없습니다.")
            return None


    def year_quarter(self):
        # comp_uid로부터 comp_df 가져오기
        comp_df = get_comp_df(self.comp_uid)

        # review_data를 기준으로 오름차순 정렬
        comp_df.sort_values(by='review_data', ascending=True, inplace=True)

        grouped_by_year_quarter = comp_df.groupby(['year', 'quarter'])

        df_by_year_quarter = {}

        for (y, q), group in grouped_by_year_quarter:
            df_by_year_quarter[(y, q)] = group

        if (str(self.year), str(self.period)) in df_by_year_quarter:
            return df_by_year_quarter[(str(self.year), str(self.period))]
        else:
            print(f"해당 연도: {self.year}, 분기: {self.period}에 대한 데이터가 없습니다.")
            return None



    def filter_period(self):
        
        if self.period.startswith('H'):
            half = self.period[-1]
            return self.year_half()

        elif self.period.startswith('Q'):
            quarter = self.period[:-1]
            return self.year_quarter()

        else:
            print("데이터가 없거나 잘못된 기간 형식입니다.")
            return None



# 변수에 객체 정의
comp_filter = Comp_Filter(comp_uid, year, period)


filtered_data = comp_filter.filter_period()


# 평균 별점 추출 -> 소수점 첫째 짜리까지 표시(둘째 자리에서 반올림)
rating = np.round(comp_filter.filter_period()['review_rate'].mean(), decimals=1)





# 키워드 추출
def get_keywords() :

    get_keyword_nnp = tokenizer.get_keyword_nnp     # 고유명사
    get_keyword_nng = tokenizer.get_keyword_nng     # 일반/보통명사

    # - 고유명사 & 일반/보통명사 병합
    comp_kw = get_keyword_nng(comp_filter.filter_period(), 'review') \
        + get_keyword_nnp(comp_filter.filter_period(), 'review')

    return comp_kw



# 리뷰 요약
def sum_reivew() : 

    return None 


