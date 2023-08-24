import json
from airflow import DAG
from datetime import datetime, timedelta
import pandas as pd

from airflow.operators.bash import BashOperator

# 디폴트 인자를 dictionary 형태로 정의
default_args = {
    'owner': 'ezpz',
    'start_date': datetime(2023, 8, 23),
}

base_command = r'docker exec --workdir /app/EZPZ_Project/scheduler ezpz_torch python3 '

scripts = {
    'new_comp_crawler': 'new_comp_crawler_server.py',
    'exist_comp_news_crawler': 'exist_comp_news_crawl_server.py',
    'exist_comp_recruit_crawler': 'exist_comp_recruit_crawl_server.py',
}

test_cmd = r'docker exec --workdir /app/test ezpz_torch python3 test.py'

# Test DAG
# 한번만 실행
with DAG(
    dag_id='test_dag',
    default_args=default_args,
    schedule_interval='@once', ): 
    
    BashOperator(
        task_id='docker_exec_test',
        bash_command=test_cmd,
    )

# 크롤러 태스크 DAG
# 매일 00:00:00에 실행
# 기존 회사 뉴스 >> 기존 회사 채용 >> 새 회사 크롤러 순으로 실행
with DAG(
    dag_id='crawler_task',
    default_args=default_args,
    schedule_interval='0 0 * * *', ): 
    # 기존 회사 뉴스 크롤러
    exist_comp_news_crawler = BashOperator(
        task_id='docker_exec_exist_comp_news_crawler',
        bash_command=base_command + scripts['exist_comp_news_crawler'],
    )
    # 기존 회사 채용 크롤러
    exist_comp_recruit_crawler = BashOperator(
        task_id='docker_exec_exist_comp_recruit_crawler',
        bash_command=base_command + scripts['exist_comp_recruit_crawler'],
    )
    # 새 회사 크롤러
    new_comp_crawler = BashOperator(
        task_id='docker_exec_new_comp_crawler',
        bash_command=base_command + scripts['new_comp_crawler'],
    )
    
    # 순서대로 파이프라인을 구성
    exist_comp_news_crawler >> exist_comp_recruit_crawler >> new_comp_crawler
    
    

# 새 회사 크롤러 DAG
# 한번만 실행
with DAG(
    dag_id='new_comp_crawler_test',
    default_args=default_args,
    schedule_interval='@once', ): 
    
    BashOperator(
        task_id='docker_exec_new_comp_crawler_test',
        bash_command=base_command + scripts['new_comp_crawler'],
    )

# 기존 회사 뉴스 크롤러 DAG
# 매일 00:00:00에 실행
with DAG(
    dag_id='exist_comp_news_crawler_test',
    default_args=default_args,
    schedule_interval='@once', ):
    
    BashOperator(
        task_id='docker_exec_exist_comp_news_crawler_test',
        bash_command=base_command + scripts['exist_comp_news_crawler'],
    )
    
# 기존 회사 채용 크롤러 DAG
# 매일 00:00:00에 실행
with DAG(
    dag_id='exist_comp_recruit_crawler_test',
    default_args=default_args,
    schedule_interval='@once', ):
    
    BashOperator(
        task_id='docker_exec_exist_comp_recruit_crawler_test',
        bash_command=base_command + scripts['exist_comp_recruit_crawler'],
    )

# # 
# # 매주 월요일 00:00:00에 실행
# with DAG(
#     dag_id='exist_comp_recruit_crawler',
#     default_args=default_args,
#     schedule_interval='0 0 * * 1', ): 
    
#     BashOperator(
#         task_id='docker_exec_exist_comp_recruit_crawler',
#         bash_command=base_command + scripts['exist_comp_recruit_crawler'],
#     )