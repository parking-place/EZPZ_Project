import sys
import os# os 필요한지 안한지 몰라서 일단 없이도 해보기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로
sys.path.append('/app/EZPZ_Project/scheduler') #db 연동정보 경로

from privates.ezpz_db import *
import sql_connection as sc

from pprint import pprint

if __name__ == '__main__':
    
    sql_ori = open('/app/EZPZ_Project/scheduler/clear.sql').read().replace('\n', ' ')
    sqls = sql_ori.split(';')

    # pprint(sqls)
    for sql in sqls[:-1]:
        sc.conn_and_exec(sql)
    print('SQL Clear Success!')
    sys.exit(0)