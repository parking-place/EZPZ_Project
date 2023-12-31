import json
from airflow import DAG
from datetime import datetime, timedelta
import pandas as pd

from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.operators.python import PythonOperator

import sys

sys.path.append('/app/EZPZ_Project/privates')

import ezpz_db

ssh_hook_torch = SSHHook(
    remote_host=ezpz_db.TORCH_SERVER_IP,
    username=ezpz_db.TORCH_SERVER_USER,
    port=ezpz_db.TORCH_SERVER_PORT,
    key_file='/app/airflow/.ssh/id_rsa',
    cmd_timeout=None,
    keepalive_interval=20,
)

default_args = {
    'owner': 'ezpz',
    'start_date': datetime(2023, 1, 1),
}
# ssh 서버 도커 컨테이너 내부에서 실행되는 명령어
docker_base_command = r'docker exec --workdir /app/EZPZ_Project/scheduler ezpz_torch python3 '
# 현재 서버 내 기본 배시 명령어
bash_base_command = r'python3 /app/EZPZ_Project/scheduler/'
# 테스트용 명령어
test_cmd = r'python3 /app/test/test.py'
ssh_test_cmd = r'docker exec --workdir /app/test ezpz_torch python3 test.py'
# ssh 서버 도커 컨테이너 시작 명령어
ssh_docker_start_cmd = r'docker start ezpz_torch'

scripts = {
    'new_comp_crawler': 'new_comp_crawler_server.py',
    'exist_comp_news_crawler': 'exist_comp_news_crawl_server.py',
    'exist_comp_news_summary': 'exist_comp_news_summary_server.py',
    'exist_comp_recruit_crawler': 'exist_comp_recruit_crawl_server.py',
    'sql_clear': 'sql_clear.py',
    'set_start_comp_list': 'set_start_comp_list.py',
    'exist_comp_review_crawler': 'exist_comp_review_crawl_server.py',
    'review_sum_server': 'review_sum_server.py',
    'review_senti_server': 'review_senti_serv.py',
}

# TEST DAG
# 한번만 실행
with DAG(
    dag_id='test_dag',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False, ):
    
    BashOperator(
        task_id='test_task',
        bash_command=test_cmd,
    )

# SSH TEST DAG
# 매 10분마다 실행
with DAG(
    dag_id='ssh_test_dag',
    default_args=default_args,
    schedule_interval='*/10 * * * *',
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_test_task',
        command=ssh_test_cmd,
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# SSH DOCKER START DAG
# 한번만 실행
with DAG(
    dag_id='ssh_docker_start',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_docker_start',
        command= ssh_docker_start_cmd,
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# SQL Clear DAG
# 한번만 실행
with DAG(
    dag_id='sql_clear',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    BashOperator(
        task_id='sql_clear',
        bash_command= bash_base_command + scripts['sql_clear'],
    )

# SQL start set DAG
# 한번만 실행
with DAG(
    dag_id='sql_start_set',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    db_clear = BashOperator(
        task_id='sql_clear',
        bash_command=bash_base_command + scripts['sql_clear'],
    )
    
    db_start_set = BashOperator(
        task_id='sql_start_set',
        bash_command=bash_base_command + scripts['set_start_comp_list'],
    )
    
    db_clear >> db_start_set
    
# 크롤러 태스크 DAG
# 매일 00:00:00에 실행
# 기존 회사 뉴스 >> 기존 회사 채용 >> 새 회사 크롤러 순으로 실행
with DAG(
    dag_id='crawler_task',
    default_args=default_args,
    schedule_interval='0 0 * * *', 
    catchup=False, ): 
    # 새 회사 크롤러
    new_comp_crawler = SSHOperator(
        task_id='ssh_new_comp_crawler',
        command=docker_base_command + scripts['new_comp_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 뉴스 크롤러
    exist_comp_news_crawler = SSHOperator(
        task_id='ssh_exist_comp_news_crawler',
        command=docker_base_command + scripts['exist_comp_news_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 뉴스 요약
    exist_comp_news_summary = SSHOperator(
        task_id='ssh_exist_comp_news_summary',
        command=docker_base_command + scripts['exist_comp_news_summary'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 채용 크롤러
    exist_comp_recruit_crawler = SSHOperator(
        task_id='ssh_exist_comp_recruit_crawler',
        command=docker_base_command + scripts['exist_comp_recruit_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 리뷰 크롤러
    exist_comp_review_crawler = SSHOperator(
        task_id='ssh_exist_comp_review_crawler',
        command=docker_base_command + scripts['exist_comp_review_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 리뷰 감정평가
    review_senti_server = SSHOperator(
        task_id='ssh_review_senti_server',
        command=docker_base_command + scripts['review_senti_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 리뷰 요약
    review_sum_server = SSHOperator(
        task_id='ssh_review_sum_server',
        command=docker_base_command + scripts['review_sum_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    
    # 순서대로 파이프라인을 구성
    new_comp_crawler >> exist_comp_news_crawler >> exist_comp_news_summary >> exist_comp_recruit_crawler >> exist_comp_review_crawler >> review_senti_server >> review_sum_server

# 크롤러 태스크 TEST DAG
# 한번만 실행
with DAG(
    dag_id='crawler_task_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ): 
    # 새 회사 크롤러
    new_comp_crawler = SSHOperator(
        task_id='ssh_new_comp_crawler',
        command=docker_base_command + scripts['new_comp_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 뉴스 크롤러
    exist_comp_news_crawler = SSHOperator(
        task_id='ssh_exist_comp_news_crawler',
        command=docker_base_command + scripts['exist_comp_news_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 뉴스 요약
    exist_comp_news_summary = SSHOperator(
        task_id='ssh_exist_comp_news_summary',
        command=docker_base_command + scripts['exist_comp_news_summary'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 채용 크롤러
    exist_comp_recruit_crawler = SSHOperator(
        task_id='ssh_exist_comp_recruit_crawler',
        command=docker_base_command + scripts['exist_comp_recruit_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 기존 회사 리뷰 크롤러
    exist_comp_review_crawler = SSHOperator(
        task_id='ssh_exist_comp_review_crawler',
        command=docker_base_command + scripts['exist_comp_review_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 리뷰 감정평가
    review_senti_server = SSHOperator(
        task_id='ssh_review_senti_server',
        command=docker_base_command + scripts['review_senti_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    # 리뷰 요약
    review_sum_server = SSHOperator(
        task_id='ssh_review_sum_server',
        command=docker_base_command + scripts['review_sum_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    
    # 순서대로 파이프라인을 구성
    new_comp_crawler >> exist_comp_news_crawler >> exist_comp_news_summary >> exist_comp_recruit_crawler >> exist_comp_review_crawler >> review_senti_server >> review_sum_server

# 새 회사 크롤러 DAG
# 한번만 실행
with DAG(
    dag_id='new_comp_crawler_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ): 
    
    SSHOperator(
        task_id='ssh_new_comp_crawler_test',
        command=docker_base_command + scripts['new_comp_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# 기존 회사 뉴스 크롤러 DAG
# 한번만 실행
with DAG(
    dag_id='exist_comp_news_crawler_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_exist_comp_news_crawler_test',
        command=docker_base_command + scripts['exist_comp_news_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# 기존 회사 뉴스 요약 DAG
# 한번만 실행
with DAG(
    dag_id='exist_comp_news_summary_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_exist_comp_news_summary_test',
        command=docker_base_command + scripts['exist_comp_news_summary'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# 기존 회사 채용 크롤러 DAG
# 한번만 실행
with DAG(
    dag_id='exist_comp_recruit_crawler_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):

    SSHOperator(
        task_id='ssh_exist_comp_recruit_crawler_test',
        command=docker_base_command + scripts['exist_comp_recruit_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )

# 기존 회사 리뷰 크롤러 DAG
# 한번만 실행
with DAG(
    dag_id='exist_comp_review_crawler_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_exist_comp_review_crawler_test',
        command=docker_base_command + scripts['exist_comp_review_crawler'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    
# 리뷰 감정평가 DAG
# 한번만 실행
with DAG(
    dag_id='review_senti_server_test',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_review_senti_server_test',
        command=docker_base_command + scripts['review_senti_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )
    
# 리뷰 요약 DAG
# 한번만 실행
with DAG(
    dag_id='review_sum_server_test',
    default_args=default_args,
    schedule_interval='@once', 
    catchup=False, ):
    
    SSHOperator(
        task_id='ssh_review_sum_server_test',
        command=docker_base_command + scripts['review_sum_server'],
        ssh_hook=ssh_hook_torch,
        get_pty=True,
    )