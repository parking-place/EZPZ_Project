import sys
import os# os 필요한지 안한지 몰라서 일단 없이도 해보기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로
sys.path.append('/app/EZPZ_Project/scheduler') #db 연동정보 경로

from privates.ezpz_db import *
import sql_connection as sc

sql  = ''

with open('clear.sql', 'r') as f:
    sql = f.read().replace('\n', '')

if __name__ == '__main__':
    sc.conn_and_exec(sql)
    print('SQL Clear Success!')
    sys.exit(0)