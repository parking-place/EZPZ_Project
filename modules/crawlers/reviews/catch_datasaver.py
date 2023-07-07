
# Import

import os
import sys
from datetime import datetime
import time
import requests
import re

import pandas as pd

import chromedriver_autoinstaller
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException



### 저장 경로 설정

SAVE_PATH = r'C:/DA_30_classes - 2nd Season/Project/data/'



def WC_Catch(corp=str) :
    
    # headless mode

    option = webdriver.ChromeOptions()
    option.add_argument('--headless')        # Head-less 설정
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')
    option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)" + "AppleWebKit/537.36 (KHTML, like Gecko)" + "Chrome/87.0.4280.141 Safari/537.36")

    service = Service(executable_path='chromedriver.exe')
    browser = webdriver.Chrome(service=service, options=option)

    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')

    url = r"https://www.catch.co.kr/"

    browser.maximize_window()
    print(browser.get_window_size())

    browser.get(url)



    # 로그인

    from accounts import ct

    ID = ct.ID
    PW = ct.PW



    browser.find_element(By.CSS_SELECTOR, "a.login").click()

    browser.find_element(By.CSS_SELECTOR, "input#id_login").send_keys(ID)

    browser.find_element(By.CSS_SELECTOR, "input#pw_login").send_keys(PW)

    browser.find_element(By.CSS_SELECTOR, "input#pw_login").send_keys(Keys.ENTER)

    time.sleep(2)



    query = browser.find_element(By.CSS_SELECTOR, "input")

    query.send_keys(corp)

    time.sleep(1)

    query.send_keys(Keys.ENTER)

    time.sleep(2)



    ### 팝업 뜨면 끄기 (예외 처리)

    try : 
        browser.find_element(By.CSS_SELECTOR, 'button.today > span').click()
        
    except : 
        pass

    time.sleep(2)



    # 검색한 기업(최상위 노출) 클릭 
    browser.find_element(By.CSS_SELECTOR, "p.name > a").click()

    time.sleep(1)

    # '현직자 리뷰' 탭 클릭
    browser.find_element(By.XPATH, r'//*[@id="Contents"]/div[1]/div[1]/div[2]/ul/li[4]/a').click()

    time.sleep(1)

    # 핵심 리뷰만 조회 - 정규직/현직자가 3년 이내 작성한 리뷰
    browser.find_element(By.CSS_SELECTOR, 'div.pd_type2 > div > a').click()

    time.sleep(1)





    #########################################################################

    time.sleep(2)

    # Review Crawler

    n_btn = browser.find_element(By.CSS_SELECTOR, 'a.ico.next')

    time.sleep(1)

    good_lst = None
    bad_lst = None


    good_lst = []
    bad_lst = []


    pre_page = 0


    while True : 

        time.sleep(1)

        # 현재 페이지의 숫자
        crt_btn = browser.find_element(By.CSS_SELECTOR, 'div.pd_type2 > p > a.selected')
        crt_page = int(crt_btn.text)

        # 다음 버튼 눌러도 같은 페이지의 경우 (마지막 페이지)
        if crt_page == pre_page:
            break

        try:
            for p in range(1, 5) : 

                grv = browser.find_element(By.CSS_SELECTOR, f"li:nth-child({p}) > p:nth-child(4)").text
                brv = browser.find_element(By.CSS_SELECTOR, f"li:nth-child({p}) > p:nth-child(5)").text

                grv_clean = grv.replace(grv[:5], "").replace('\n', ' ') 
                brv_clean = brv.replace(brv[:4], "").replace('\n', ' ') 

                good_lst.append(grv_clean)
                bad_lst.append(brv_clean)
        
        except NoSuchElementException : 
            break

        time.sleep(2)

        # WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"li:nth-child({i}) > p:nth-child(4)")))


    # 다음 페이지로 이동하기 위한 버튼을 찾기.
        try:
            # 이전페이지의 번호를 갱신
            pre_page = crt_page

            # 다음 버튼 클릭
            n_btn.click()

            # 버튼 누르고나서 정보를 가져올때까지 슬립(몇초동안)걸어두기.
            time.sleep(1)

        except:
            break



    browser.close()


    # list to dataframe

    good_lst = list(set(good_lst))
    bad_lst = list(set(bad_lst))

    good_df = pd.DataFrame({"긍정적 평가" : good_lst})
    bad_df = pd.DataFrame({"부정적 평가" : bad_lst})

    pros_cons = good_df.join(bad_df)



    # dataframe to csv file

    os.makedirs(SAVE_PATH, exist_ok=True)

    # csv 파일로 저장.

    file_name = f"{corp}_reviews.csv"
    save_file_path = os.path.join(SAVE_PATH, file_name)
    
    pros_cons.to_csv(save_file_path, index=False, encoding = "utf-8")



    # 후처리

    pros_cons['긍정적 평가'] = pros_cons['긍정적 평가'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())
    pros_cons['부정적 평가'] = pros_cons['부정적 평가'].apply(lambda x: re.sub(r'\s+', ' ',re.sub(r'\n+', ' ', x)).strip())



    return pros_cons
    
