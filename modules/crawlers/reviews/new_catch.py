import os
import sys
from datetime import datetime
import time

import re

import tqdm
import itertools

import json
import urllib.request

import pandas as pd
import numpy as np

import requests
from bs4 import BeautifulSoup
import lxml





SAVE_PATH = r'./data/'
# SAVE_PATH = r'/app/data/reviews/'     <--- for Docker





def RV_123Catch(comp = str): 
    
    search_url = 'https://www.catch.co.kr/Search/SearchList?Keyword={}'
    search_req = requests.get(search_url.format(comp)) # Keyword = comp_name
    # print(search_req.text)

    search_soup = BeautifulSoup(search_req.text, 'lxml')
    # search_soup.text
    search_soup.select('li:nth-child(1) > div.txt > p.name > a')

    comp_id = re.sub(r'[^0-9]', '', str(search_soup.select('li:nth-child(1) > div.txt > p.name > a')))
    comp_name = re.findall('>([^"]*)<', re.sub(r'\s', '', str(search_soup.select('li:nth-child(1) > div.txt > p.name > a'))))[0]




    p_num = 1

    rv = []



    try : 

        while True : 

            url = f'https://www.catch.co.kr/api/v1.0/comp/reviewInfo/{comp_id}/commentList?currentPage={p_num}&pageSize=5000&isNew=false&employType=1&isEmploy=false&jobCode='
            rv.append(requests.get(url).json()['reviewList'])

            p_num += 1

            if len(requests.get(url).json()['reviewList']) == 0 :
                break


        data = list(itertools.chain.from_iterable(rv))
        df = pd.DataFrame(data)


        df.drop(['idx', 'CompID', 'CompName', 'CI', 'Gender2', 'Answer', 'UsefulY', 'CareerYearYN',  'MyUsefulY', 'MyOpinion', 
                'Keyword1', 'Keyword2', 'Keyword3', 'Keyword1YN', 'Keyword2YN', 'Keyword3YN', 
                'EmployType', 'NewOld', 'CareerYear', 'Area'], 
                axis=1, inplace=True)
        

        df['Good'] = df['Good'].apply(lambda x: re.sub(r'\s+', ' ', re.sub(r'\n+', ' ', x)).strip())
        df['Bad'] = df['Bad'].apply(lambda x: re.sub(r'\s+', ' ', re.sub(r'\n+', ' ', x)).strip())

        df['RegDate'] = df['RegDate'].apply(lambda x: re.sub(r'[^0-9]', '', x)[:8].strip())

        df['EmployText'] = df['EmployText'].apply(lambda x: x.replace('현직', '1').strip() == '1')

        df['RecomName'] = df['RecomName'].replace(['추천', '비추'], [1, 0])


        df.rename(columns=
           {'RegDate':'review_date', 
           'EmployText':'is_office', 
           'Good':'review_pos', 
           'Bad':'review_neg', 
           'MyStarScore':'review_rate', 
           'JobName':'position',
           'RecomName':'review_senti'       # 임의로 쓰는 값 (나중에 모델 돌려서 나온 결과 값으로 대체 할 것.)
           }, inplace=True)




        # csv 파일로 저장.

        os.makedirs(SAVE_PATH, exist_ok=True)

        file_name = f"{comp_name}_catch.csv"
        save_file_path = os.path.join(SAVE_PATH, file_name)

        df.to_csv(save_file_path, index=False, encoding = "utf-8")
        
        return pd.read_csv(save_file_path)


        
    except : 
        print("리뷰가 존재하지 않습니다.")



