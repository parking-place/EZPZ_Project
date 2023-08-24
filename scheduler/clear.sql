use testdb;
drop table if exists comp_news;
drop table if exists recruit_info;
drop table if exists comp_review;
drop table if exists sum_review;
drop table if exists comp_info;

create table comp_info(
	comp_uid bigint auto_increment,
	comp_name varchar(20) not null,
	comp_loc varchar(200) not null,
	comp_thumb varchar(2000),
    comp_cont varchar(30),
	comp_founded char(6),
	comp_size varchar(20),
	comp_url varchar(2000),
	is_reged char(1) default 'N' not null
        check (is_reged in ('Y', 'N')),
	
    create_date char(8) not null,
	modify_date char(8) not null,
	
	primary key comp_info(comp_uid),
	constraint COMP_NAME_UK unique comp_info(comp_name)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

create table recruit_info(
	recruit_uid bigint auto_increment,
	comp_uid bigint not null,
	recruit_url varchar(2000) not null,
	recruit_position varchar(100) not null,
	recruit_thumb varchar(2000),
    recruit_desc varchar(200),
	
	create_date char(8) not null,
	modify_date char(8) not null,
	
	primary key recruit_info(recruit_uid),
	constraint RECRUIT_COMP_FK foreign key recruit_info(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

create table comp_news(
	news_uid bigint auto_increment,
	comp_uid bigint not null,
	pub_date char(8) not null,
	news_url varchar(2000) not null,
	news_cont varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci not null,
	
	news_sum varchar(256),
	news_senti int(1) check (news_senti in (0, 1, 2)),
	
	create_date char(8) not null,
	modify_date char(8) not null,
	
	primary key comp_news(news_uid),
	constraint NEWS_COMP_FK foreign key comp_news(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

create table comp_review(
	review_uid bigint auto_increment,
	comp_uid bigint not null,
	review_cont varchar(500) not null,
	review_senti char(1) not null,
	review_rate int(1) not null,
	is_office boolean not null,
	review_date char(8) not null,
	position varchar(10) not null,
	
	create_date char(8) not null,
	modify_date char(8) not null,
	
	primary key comp_review(review_uid),
	constraint REVIEW_COMP_FK foreign key comp_review(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

create table sum_review(
	sum_uid bigint auto_increment,
	comp_uid bigint not null,
	sum_year int(4) not null,
	sum_term int(1) not null,
	sum_cont varchar(256) not null,
	sum_keyword varchar(5000),
	
	create_date char(8) not null,
	modify_date char(8) not null,
	
	primary key sum_review(sum_uid),
	constraint REVIEW_S_COMP_FK foreign key sum_review(comp_uid) references comp_info(comp_uid)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;