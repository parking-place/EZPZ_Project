# daum_news_list.py
# 특정 키워드에 대한 다음 뉴스 검색, 리스트 반환 모듈

from selenium.webdriver.common.by import By
import pandas as pd
import os
# 나머지는 함수 내에서 import : 해당 함수에서만 사용 

# constants
POTAL_URL = 'https://www.daum.net/'
SAVE_PATH = './datas/daum_news'
keyword = None


def get_service():
    import zipfile
    from selenium.webdriver.chrome.service import Service
    
    TARGET_PATH = './driver'
    ZIP_FILE_PATH = './driver/chromedriver_win32.zip'
    
    service=None
    try:
        service = Service(executable_path='e:ezpz_mini/MiniProj/modules/crawlers/driver/chromedriver_win32/chromedriver.exe')
    except:
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip:
            zip.extractall(TARGET_PATH)
            
    return service

def get_browser():
    from selenium import webdriver
    
    # browser config
    option = webdriver.ChromeOptions()
    option.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')
    option.add_argument('--headless')
    
    return webdriver.Chrome(service=get_service(), options=option)



def serach_by_keyword(browser, keyword):
    """
    parameters ]
        browser : selenium.webdriver.chrome.webdriver.WebDriver
        keyword : str
    """
    
    # 접속
    browser.set_window_size(600, 500)
    browser.get(POTAL_URL)
    
    # 검색
    browser.find_element(By.CSS_SELECTOR, '#q.tf_keyword').send_keys(keyword)
    browser.find_element(By.CSS_SELECTOR, '.ico_pctop.btn_search').click()
    
    return browser



def go_news_tab(browser):
    """
    browser 객체를 받아 '뉴스' 탭 클릭까지 진행
    parameters ]
        browser : selenium.webdriver.chrome.webdriver.WebDriver
    """
    is_tab_exist = False
    
    # find from nav bar
    for nav in browser.find_elements(By.CSS_SELECTOR, 'ul.gnb_search a.tab_tit'):
        
        if nav.text.find('뉴스') > -1:
            news_tab = nav
            is_tab_exist = True
            break
        
    # 최초 노출 nav bar에 뉴스가 없는 경우...
    if is_tab_exist:
        
        pass
    else: # 우선순위에 밀려 더보기 탭에 뉴스 탭 존재
        # 더보기 탭 클릭
        browser.find_element(By.CSS_SELECTOR, '#gnbToggleBtn.btn_tab').click()
        # 뉴스탭 찾기
        news_tab = [nav for nav in browser.find_elements('ul_list_more .tab_tit')  if nav.text.find('뉴스') > -1][0]
        
    news_tab.click()
    
    return browser



def get_news_list(browser):
    """
    browser 객체에서 1면 뉴스들의 링크만 추출
    제목도 같이 추출해야 할 경우, 주석 해제 후 사용하길 권합니다.
    
    parameters ]
        browser : selenium.webdriver.chrome.webdriver.WebDriver
    
    returns ]
        link_list
    """
    from bs4 import BeautifulSoup as bs # 해당 함수 밖에선 실행하지 않음
    #title_list, link_list = [], []
    
    # 단순 조회 : 더 빠른 beautiful soup 사용
    soup = bs(browser.page_source, 'lxml')
    
    #title_list = [el.text.strip() for el in soup.select('a.tit_main.fn_tit_u')]
    #link_list = [el.attrs['href'] for el in soup.select('a.tit_main.fn_tit_u')]
    
    #return title_list, link_list
    return [el.attrs['href'] for el in soup.select('a.tit_main.fn_tit_u')]



def get_df_for_keyword_search(serach_keyword):
    """
    제목까지 받아와야 하는 경우, 해당 함수의 주석과 get_news_list 함수의 주석을 해제 후 사용해야 합니다.
    parameter ]
        keyword : str   - 해당 단어로 다음 검색(입력시 global 변수로 저장)
        
    return ]
        pandas.DataFrame
    """
    
    # 검색
    browser = get_browser()
    serach_by_keyword(browser, serach_keyword)
    
    # 뉴스탭 클릭
    browser = go_news_tab(browser)
    
    # 뉴스 리스트 받기
    #titles, links = get_news_list(browser) # 제목까지 받아옵니다.
    links = get_news_list(browser)
    
    browser.close()
    return pd.DataFrame({
        #"title": titles,
        "link": links,
    })



# main으로 부른 경우에만 save & log
if __name__ == "__main__":
    import time # 해당 함수 밖에선 실행하지 않음
    from datetime import date # 해당 함수 밖에선 실행하지 않음
    
    st_time = time.time() # to log
    
    TODATE = date.today().strftime("%Y%m%d") # to save
    keyword = '카카오' # 테스트용 코드
    
    # 검색해 dataframe 받아오기
    df = get_df_for_keyword_search(keyword)
    
    # 디렉토리 생성
    os.makedirs(SAVE_PATH, exist_ok=True)
    
    # 저장
    df.to_csv(os.path.join(SAVE_PATH, f'{keyword}_daum.csv'), index=False)
    
    # logging
    ed_time = time.time()
    print(f'[CSV SAVED] {TODATE} - {SAVE_PATH}/{keyword}_daum.csv at {(ed_time - st_time):.5f} sec')
