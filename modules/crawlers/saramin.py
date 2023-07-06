#1.import 할꺼 해주고
#2.전역변수 해줄꺼 해주고
#3.필요한 함수 모듈화
#4. 주석 처리 잘해주기 변수 설명해주고

import os
import requests
import re
import pandas as pd
import time
from bs4 import BeautifulSoup

import selenium
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from accounts import si

service = Service(executable_path='chromedriver.exe')
browser = webdriver.Chrome(service=service)
save_path=r'C:\python_lesson\mini_project\MiniProj\si_crawl\{}_si.csv'
# ChromeBrowser - headless mode

option = webdriver.ChromeOptions()
option.add_argument#("--headless")


def get_si_reviews(company_name): #1.회사 이름 받아서 추출해주는 함수

    

    si.ID, si.PW
    ###################################################################################
    #사람인 url 접속
    ###################################################################################

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    url = r"https://www.saramin.co.kr/zf_user/"
    browser.maximize_window() #윈도우 전체화면
    print(browser.get_window_size()) # WINDOW_SIZE 출력
    browser.get(url) #사람인에서 url을 받아옴

    ###################################################################################
    #로그인
    ###################################################################################

    #로그인 버튼 클릭
    login_screen_btn = browser.find_element(By.CSS_SELECTOR,"#sri_header > div.wrap_header > div.utility > div.sign > a.btn_sign.signin") 
    login_screen_btn.click()
    #아이디 버튼 클릭
    id_btn = browser.find_element(By.CSS_SELECTOR,"#id")
    #id_btn.click()
    #아이디 입력
    id_btn.send_keys(si.ID)

    #비밀번호 버튼 클릭
    pwd_btn = browser.find_element(By.CSS_SELECTOR,"#password")
    pwd_btn.click()
    #비밀번호 입력
    pwd_btn.send_keys(si.PW)

    #로그인 클릭
    login_btn = browser.find_element(By.CSS_SELECTOR,"#login_frm > div > div > div.login-form > button").send_keys(Keys.ENTER)

    ###################################################################################
    #기업 후기까지 접속 및 검색
    ###################################################################################

    #메인 홈페이지로 돌아가기
    main_btn = browser.find_element(By.CSS_SELECTOR,'#sri_gnb_wrap > a > svg.img_ci')
    main_btn.click()

    #카테고리 버튼 클릭
    category_btn = browser.find_element(By.CSS_SELECTOR,'#sri_header > div.wrap_header > div.navigation > ul > div:nth-child(4) > a > span')
    category_btn.click()

    #검색창 클릭
    try: #처음 들어갈 때 팝업창이 떴을 경우
        pop_up_delete_btn= browser.find_element(By.CSS_SELECTOR,'#wrap_review_tutorial > div > button')
        pop_up_delete_btn.click()
        search_btn = browser.find_element(By.CSS_SELECTOR,'#content > div.company_review_main > div.wrap_main_top > div > div > div.area_input > input')
        search_btn.click()
        
    except: #팝업창이 안뜰경우 바로 검색창 클릭  
        search_btn = browser.find_element(By.CSS_SELECTOR,'#content > div.company_review_main > div.wrap_main_top > div > div > div.area_input > input')
        search_btn.click()

    #검색어 입력
    
    #cop=input()
    #print(cop)
    search_btn.send_keys(company_name)
    #print(browser.text)
    #print(browser.find_element(By.CSS_SELECTOR,'#content > div.company_review_main > div.wrap_main_top > div > div > div.area_input.on > button'))

    time.sleep(2)
    #검색어 엔터
    enter_btn = browser.find_element(By.CSS_SELECTOR,'#content > div.company_review_main > div.wrap_main_top > div > div > div.area_input.on > button')
    enter_btn.click()
    time.sleep(2)
    #(주) 앞뒤로 포함돼 있거나 대상 검색 문자열(cop)과 일치할 경우 서치 아니면 예외처리 
    i=1
    while True:
        try: 
            n_btn = browser.find_element(By.CSS_SELECTOR, f" div:nth-child({i}) > div > div.area_info > strong > a:nth-child(1)")
            
            
            if company_name+'(주)' == n_btn.text or '(주)'+company_name == n_btn.text or company_name == n_btn.text: #(주)+검색어 및 검색어 와 정확히 일치
                n_btn.click() #그 회사 클릭   
                break #일치하는 회사 찾으면 반복문 탈출       
            i += 1
                    
                
        except: 
            print(f"No result found for {company_name}") #검색어와 연관된 회사 찾지 못할 시 에러 표시 (에러시 다시 검색어로 돌아가는것도 구현)
            break
    ###################################################################################
    #회사 리뷰 크롤링 
    ###################################################################################

    #한번 크롤링하고 클릭하고 리스트에 넣고 그걸 끝날 때까지 반복하고 break
    review_list=[]
    review_tag=[]#div.bx-wrapper > div > ul > li:nth-child({i}) > p.desc
    i=0
    while True:
        try:
            i+=1 #하나씩 리뷰 넘어가기 위함

            if len(browser.window_handles) >= 2: #브라우저 창이 여러개라면 
            # 새로 띄워진 창으로 전환
                    browser.switch_to.window(browser.window_handles[-1]) # 새로 띄워진 창이 맨 마지막 창이라 가정
                    # 새로 띄워진 창의 URL 가져오기
                    new_window_url = browser.current_url

            html=browser.page_source #페이지 소스 가져오기
            soup = BeautifulSoup(html, "html.parser")# html 파싱 
            review_tag= soup.select(f"div.bx-wrapper > div > ul > li:nth-child({i}) > p.desc") #파싱된 html 내용을 담아주기
            review_list.append(review_tag[0].text.strip()) #담긴 리뷰 리스트를 strip해서 review_list에 담아주고
            
        except: # 아예 리뷰가 끝나버리면 break 
                    break
    ###################################################################################
    #데이터프레임 생성
    ###################################################################################

    si_df=pd.DataFrame(review_list,columns=[f'review'])

    ###################################################################################
    #데이터 전처리
    ###################################################################################

    #데이터프레임의 엔터 특수 문자를 스페이스키 한개로 바꿔주고 strip()처리해줌
    si_df['review'] = si_df['review'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())

    ###################################################################################
    #CSV 파일 저장
    ###################################################################################

    # 데이터프레임을 CSV 파일로 저장
    si_df.to_csv(save_path, index= True, encoding='utf-8-sig')

    return si_df
