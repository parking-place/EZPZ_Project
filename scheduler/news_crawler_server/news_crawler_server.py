'''#먼저 간단 poc 해보기 뉴스 돌아가는지와 모델 돌아가는지
#다음뉴스 크롤링은 잘됨 경로 오류만 빼면
#네이버뉴스는 왜 안될까 3시10분까지 안되면 다음뉴스 그냥 데이터 세이브만  해서 모델 돌려보기 연습해보기 

import sys
import os
import pymysql
import cryptography
sys.path.append('/app/EZPZ_Project/modules/crawlers/news')
#from daum_news_crawler import get_news
import daum_news_crawler
import naver_news_crawler
import news_crawlers

import socket

try :
    DB_IP = socket.gethostbyname('EZPZ_DB')
except:
    DB_IP = 'localhost'
USER='root'
NAME='ezpz'
ENGINE= "django.db.backends.mysql"
DATABASES = {
    "default": {
        "ENGINE": ENGINE,
        "NAME": NAME, #나중에 db이름 고치기 데이터베이스 이름 
        "USER": USER, 
        "PASSWORD": "1234",
        "HOST": DB_IP,
        "PORT": "33306"
    }
}



dir_path='/app/EZPZ_Project/scheduler/news_crawler_server'
keyword='삼성전자'
if __name__ == '__main__': #현재 파일에서 실행될때만 실행됨

    daum_news = daum_news_crawler.get_news(keyword) #다음뉴스 크롤러 실행 확인
    #naver_news = naver_news_crawler.get_news('SK 하이닉스') #네이버 뉴스크롤러 실행이 안되니 천천히 해보기

    #csv저장로직------------------------
    os.makedirs(dir_path) # 디렉토리 생성
    daum_news.to_csv(os.path.join(dir_path, f'\\{keyword}_daum.csv'), index=False, encoding='utf-8')
    #-----------------------------------

    #print(daum_news.head())
    #print(daum_news.shape)
    print(daum_news)

    """#sql 문작성 시작---------------------------
    conn = pymysql.connect(host=DB_IP, user=USER, password='1234',db= NAME ,charset='utf8')
    cur = conn.cursor()
    cur.execute('desc comp_news')"""
'''


