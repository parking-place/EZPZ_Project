import sys
import os
import pandas as pd


import cryptography
import sql_connection as sc
from datetime import datetime


sys.path.append('/app/EZPZ_Project') #db 연동정보 경로
sys.path.append('/app/EZPZ_Project/modules/crawlers/job_post') # 채용공고 경로

import wanted_recruit_crawler

from privates.ezpz_db import *




def recruit_info_update(comp_list):
    for comp in comp_list:
        #채용공고는 회사이름에 (주) 붙어있으면 안됨 제거 전처리
        recruit_comp = comp.replace('(주)',"")
        #print(recruit_comp)

        recruit_info_df=wanted_recruit_crawler.get_recruit_info(recruit_comp, csv_save=False) # 원티드 기업정보 크롤러 모듈

        #테이블 데이터 타입 맞추기 위해 type이 set인 uid를 int로 바꿔준 값을 넣어줌
        new_i=[]
        for i in range(len(recruit_info_df['recruit_uid'])):
            new_i.append(list(recruit_info_df['recruit_uid'][i])[0])
        recruit_info_df['recruit_uid']=new_i

        #회사이름이 comp_info와 같은 recruit_info에서 recruit_info_uid 정보 전부 빼옴
        sql = 'SELECT recruit_info.recruit_uid '
        sql += 'FROM recruit_info JOIN comp_info '
        sql += 'ON recruit_info.comp_uid = comp_info.comp_uid '
        sql += 'WHERE comp_info.comp_name = %s'
        re_uid_set = sc.conn_and_exec(sql,(comp))
        #cur.execute(sql, (comp))
        #cur.execute("SELECT recruit_info.recruit_uid FROM recruit_info JOIN comp_info ON recruit_info.comp_uid = comp_info.comp_uid WHERE comp_info.comp_name = %s", (comp))
        uid_table_list=[]

        for r_uid in re_uid_set:
            uid_table_list.append(r_uid[0])

        if len(recruit_info_df['recruit_uid']) > len(uid_table_list): #추가해야될 채용공고가 있는경우: insert
            #차집합으로 크롤링데이터엔 있고 테이블엔 없는 것들 찾아서 추가
            sub_set = [x for x in recruit_info_df['recruit_uid'].tolist() if x not in uid_table_list]

            #차집합만을 포함한 데이터프레임 만들기(insert목록)
            filtered_recruit_info_df = recruit_info_df[recruit_info_df['recruit_uid'].isin(sub_set)]
            #채용공고에 넣어줄 comp_id
            #cur.execute(f'select comp_uid from comp_info where comp_name = "{comp}"')
            sql = f'select comp_uid from comp_info where comp_name = "{comp}"'
            uid = sc.conn_and_exec(sql)
            comp_uid=uid[0][0]
            #print(comp_uid)

            create_date = datetime.today().strftime('%Y%m%d')
            modify_date = datetime.today().strftime('%Y%m%d')

            for index, row in filtered_recruit_info_df.iterrows():
                sql = 'insert into recruit_info '
                sql += '    (comp_uid, recruit_uid, recruit_url, recruit_position, recruit_thumb, recruit_desc, create_date, modify_date) '
                sql += 'values ( '
                sql += f'   "{comp_uid}", "{row["recruit_uid"]}", "{row["recruit_url"]}", "{row["recruit_position"]}", "{row["recruit_thumb"]}", "{row["recruit_desc"]}" '
                sql += f'    , "{"00000000"}", "{"00000000"}" '
                sql += ') '
                #cur.execute(sql)
                sc.conn_and_exec(sql)

                #for i in cur:
                #    print(i)
            #print(f'{comp} 공고 추가완료')
            #print(filtered_recruit_info_df)
        elif len(recruit_info_df['recruit_uid']) == len(uid_table_list) and sorted(recruit_info_df['recruit_uid']) == sorted(uid_table_list) : # 아예 똑같음 채용공고 변동사항 없음
            #print(f'{comp} 변동없음')
            continue #채용공고 변동없이 다음기업 찾기로 넘어감

        else: #삭제해야될 채용공고가 있는경우: delete
            #차집합으로 테이블엔 있고 크롤링데이터엔 없는 것들 찾아서 삭제 delete해줄 애들
            sub_set = [x for x in  uid_table_list if x not in recruit_info_df['recruit_uid'].tolist()]

            for sub in sub_set:
                #cur.execute(f'delete from recruit_info where recruit_uid = {sub}')
                sql = f'delete from recruit_info where recruit_uid = {sub}'
                sc.conn_and_exec(sql)
            #print(f'{comp} 공고 삭제됨')
    #추가 및 삭제 잘 됐나 여부는 요걸로 확인



#테스트용으로 사용하세요
if __name__ == '__main__':

    comp_list=['삼성전자(주)','(주)카카오','네이버(주)']
    #테스트용으로 아무거나 delete =>공고 추가되나 확인용
    #cur.execute('delete from recruit_info where recruit_position = "[신입] iOS개발"')
    sql = 'delete from recruit_info where recruit_position = "[신입] iOS개발"'
    sc.conn_and_exec(sql)

    #cur.execute('select * from recruit_info')
    #for i in cur:
    #    print(i)

    #함수테스트완료
    recruit_info_update(comp_list)



