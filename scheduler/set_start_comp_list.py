import sys
import os# os 필요한지 안한지 몰라서 일단 없이도 해보기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로
sys.path.append('/app/EZPZ_Project/scheduler') #db 연동정보 경로

from privates.ezpz_db import *
import sql_connection as sc

from pprint import pprint
import pandas as pd

from datetime import datetime

top_comp_list_path = '/app/data/datas/comp_list/top100_comp.csv'

if __name__ == '__main__':
    
    df = pd.read_csv(top_comp_list_path, encoding='utf-8')
    
    comp_list = df['Company'].tolist()
    
    create_date = datetime.today().strftime('%Y%m%d')
    modify_date = datetime.today().strftime('%Y%m%d')
    
    for comp_name in comp_list:
        sql = 'INSERT INTO comp_info '
        sql += '(comp_name, comp_loc, comp_thumb, comp_cont, comp_founded, comp_size, comp_url, is_reged, create_date, modify_date) '
        sql += f'VALUES ("{comp_name}", "null", "null", "null", "null", "null", "null", "N", "{create_date}", "{modify_date}")'
        
        sc.conn_and_exec(sql)
    
    pass