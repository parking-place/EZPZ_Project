from accounts import jp
# jp.ID, jp.PW

import os
import time
import requests
import re
import pandas as pd
import selenium

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

SAVE_PATH = f"/Users/gyeonmunju/Desktop/PlayData/jp_company"

def get_jp_reviews(company_name):
    ############################
    # 크롬으로 잡플래닛 사이트 열기
    ############################
    # headless 모드

    option = webdriver.ChromeOptions()
    option.add_argument("--headless")

    service = Service(executable_path='chromedriver.exe')
    browser = webdriver.Chrome(service=service, options=option)

    url = r"https://www.jobplanet.co.kr/job"

    browser.maximize_window()
    print(browser.get_window_size())

    browser.get(url)



    ############################
    # 잡플래닛에 로그인 하기
    ############################

    # 로그인 버튼 찾기 및 클릭
    login_btn = browser.find_element(By.CSS_SELECTOR,"a.btn_txt.login")
    login_btn.click()

    # 로그인 ID와 PW 쳐야할 곳 클릭 + 적기
    login_Id = browser.find_element(By.CSS_SELECTOR, "#user_email")
    login_Id.click()
    login_Id.send_keys(jp.ID)

    login_Pw = browser.find_element(By.CSS_SELECTOR, "#user_password")
    login_Pw.click()
    login_Pw.send_keys(jp.PW)

    # 이메일로 로그인 버튼 누르기
    em_log = browser.find_element(By.CSS_SELECTOR, "fieldset > button")
    em_log.click()
    time.sleep(2)



    ###########################
    # 잡플래닛 검색창에 회사 입력하고 맨 처음에 나오는 기업 클릭하기.
    ###########################
    # 검색창 누르기
    search_bar = browser.find_element(By.CSS_SELECTOR, "#search_bar_search_query")
    search_bar.click()

    # 내가 원하는 회사 입력하기
    search_bar.send_keys(company_name)
    search_bar.send_keys(Keys.RETURN)

    # 검색결과 기다리기.
    time.sleep(1)

    # 맨처음에 나오는 기업 클릭하기
    company = browser.find_element(By.CSS_SELECTOR, "div.is_company_card > div:nth-child(1) > a")
    company.click()

    # 검색결과 기다리기.
    time.sleep(1)



    ###########################
    # 회사페이지에서 리뷰 버튼 누르기
    ###########################
    # 팝업창이 있을 때는 팝업창 버튼을 누르고 리뷰버튼을 누르기
    try:
        pop = browser.find_element(By.CSS_SELECTOR, "div.premium_modal_header > button")
        pop.click()
        review_bar = browser.find_element(By.CSS_SELECTOR, "li.viewReviews > a")
        review_bar.click()

    except NoSuchElementException:
        # 만약 팝업창 버튼이 없다면 리뷰 버튼만 누르기
        try:
            review_bar = browser.find_element(By.CSS_SELECTOR, "li.viewReviews > a")
            review_bar.click()
            time.sleep(1)
            pop = browser.find_element(By.CSS_SELECTOR, "div.premium_modal_header > button")
            pop.click()
        except NoSuchElementException:
            pass
        pass



    ###########################
    # 회사페이지에서 리뷰 가져오기.
    ###########################
    """
    잡플래닛 회사 리뷰 상세 내용을 url을 받아서 내용을 반환.
    연결
    """
    # 리뷰들을 리스트로 저장하는 변수
    review_list = []

    # 이전페이지 변수
    pre_page = 0

    # 무한 루프를 돌기.
    while True:

        # 소스 끌어오기.
        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")

        # 현재 페이지의 숫자를 가져오기.
        crt_btn = soup.select_one('strong.txtlink_page')
        crt_page = int(crt_btn.text[0].strip())

        # 다음버튼을 눌렀은데도 같은 페이지인 경우
        if crt_page == pre_page:
            break

        # html 내용 가져오기
        review = soup.select("div.us_label_wrap > h2")

        # 텍스트로 추출한 내용을 리스트에 추가해서 넣어주기 위해 이용. (데이터 전처리)
        for text in review : # for문은 for 채워져있는 값의 원소 in 채워져있는 리스트
            text_clean_1 = text.get_text().strip()
            text_clean_2 = text_clean_1.replace("\n\n", "").replace('"', '').replace("T","").replace("\n","").replace(text_clean_1[:3], "").replace("      ","")
            review_list.append(text_clean_2)
        time.sleep(1)

        # 다음 페이지로 이동하기 위한 버튼을 찾기.
        try:
            # 이전페이지의 번호를 갱신하기.
            pre_page = crt_page

            # 다음 버튼 찾기
            next_btn = browser.find_element(By.CSS_SELECTOR,f"a.btn_pgnext")

            # 버튼이 있으면 클릭합니다.
            next_btn.click()

            # 버튼 누르고나서 정보를 가져올때까지 슬립(몇초동안)걸어두기.
            time.sleep(3)

        except:
            break

        # local에 디렉토리를 생성.
        os.makedirs(SAVE_PATH, exist_ok=True)

        # 데이터프레임으로 관리하겠다 지정. (데이터 생성하기.)
        jp_df = pd.DataFrame(review_list, columns=[f"jp_review"])

        # csv 파일로 저장.
        file_name = f"{company_name}_reviews.csv"
        save_file_path = os.path.join(SAVE_PATH, file_name)
        jp_df.to_csv(save_file_path, index=False, encoding = "utf-8")
    
    # 브라우저 끄기
    browser.close()
    
    return jp_df