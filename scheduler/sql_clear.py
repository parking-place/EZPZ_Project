import sys
import os# os 필요한지 안한지 몰라서 일단 없이도 해보기
sys.path.append('/app/EZPZ_Project') #db 연동정보 경로
sys.path.append('/app/EZPZ_Project/scheduler') #db 연동정보 경로

from privates.ezpz_db import *
import sql_connection as sc

sql = r'''
# 테이블 일괄 삭제
use testdb;
drop table if exists comp_news;
drop table if exists recruit_info;
drop table if exists comp_review;
drop table if exists sum_review;
drop table if exists comp_info;

# 기업 정보 테이블
create table comp_info(
	comp_uid bigint auto_increment,
	comp_name varchar(20) not null,
	comp_loc varchar(200) not null,
	# 아래는 nullable
	comp_thumb varchar(2000),
  	comp_cont varchar(30),
	comp_founded char(6),
	comp_size varchar(20), # 회사 규모 : 대기업, 중견기업 등
	comp_url varchar(2000),
	is_reged char(1) default 'N' not null
		 check (is_reged in ('Y', 'N')),
	
 	create_date char(8) not null, # DB 입력 날짜
	modify_date char(8) not null, # 최종 수정 날짜
	
	primary key comp_info(comp_uid),
	constraint COMP_NAME_UK unique comp_info(comp_name)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#describe comp_info;

# 채용 공고 테이블
create table recruit_info(
	recruit_uid bigint auto_increment,
	comp_uid bigint not null, # indexing 문제로 unqiue 제약조건 삭제
	recruit_url varchar(2000) not null,
	recruit_position varchar(100) not null,
	recruit_thumb varchar(2000),
    recruit_desc varchar(200),
	
	create_date char(8) not null, # DB 입력 날짜
	modify_date char(8) not null, # 최종 수정 날짜
	
	primary key recruit_info(recruit_uid),
	constraint RECRUIT_COMP_FK foreign key recruit_info(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#describe recruit_info;

# 기업 뉴스 테이블
create table comp_news(
	news_uid bigint auto_increment,
	comp_uid bigint not null,
	pub_date char(8) not null, # 뉴스 발행 일자
	news_url varchar(2000) not null,
	news_cont varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci not null,
	
	news_sum varchar(256), # 뉴스 요약
	news_senti int(1) check (news_senti in (0, 1, 2)),
	
	create_date char(8) not null, # DB 입력 날짜
	modify_date char(8) not null, # 최종 수정 날짜
	
	primary key comp_news(news_uid),
	constraint NEWS_COMP_FK foreign key comp_news(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#describe comp_news;

# 기업 리뷰 테이블
create table comp_review(
	review_uid bigint auto_increment,
	comp_uid bigint not null,
	review_cont varchar(500) not null, # 리뷰 내용
	review_senti char(1) not null, # 모델 감정평가 결과
	review_rate int(1) not null, # 별점
	is_office boolean not null, # 재직자 여부
	review_date char(8) not null,
	position varchar(10) not null,
	
	create_date char(8) not null, # DB 입력 날짜
	modify_date char(8) not null, # 최종 수정 날짜
	
	primary key comp_review(review_uid),
	constraint REVIEW_COMP_FK foreign key comp_review(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#describe comp_review;

# 리뷰 시계열 데이터 테이블
create table sum_review(
	sum_uid bigint auto_increment,
	comp_uid bigint not null,
	sum_year int(4) not null,
	sum_term int(1) not null,
	sum_cont varchar(256) not null,
	sum_keyword varchar(5000), # 키워드 추출 결과
	
	create_date char(8) not null, # DB 입력 날짜
	modify_date char(8) not null, # 최종 수정 날짜
	
	primary key sum_review(sum_uid),
	constraint REVIEW_S_COMP_FK foreign key sum_review(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#describe sum_review;
'''

if __name__ == '__main__':
    sc.conn_and_exec(sql)
    print('SQL Clear Success!')
    
    sys.exit(0)