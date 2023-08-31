import sys
import os# os 필요한지 안한지 몰라서 일단 없이도 해보기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로

from privates.ezpz_db import *

def conn_and_exec(sql,param=None): #return문이 필요할 때
	conn = get_connection()
	cur = conn.cursor()
	try:	
		cur.execute(sql,param)
		exec = cur.fetchall()
		conn.commit()
	except Exception as e:
		print('Error : ', e)
		print('SQL : ', sql)
		conn.rollback()
	conn.close()

	#select 문 정보를 저장해서 사용해야되는경우 반환값이 있어야함(ex comp_uid)
	return exec