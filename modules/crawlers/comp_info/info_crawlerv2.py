import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}


'''
get_url 함수에 '기업명' 인자로 주면 기업정보 크롤링해줌
'''

# 회사 정보 가져오는 함수 (잡플래닛)
def get_comp_info(urls, comp):
    
    for url in urls:
        print(url)
        r = requests.get(url, headers=HEADERS) #requests로 url 접근 요청
        soup = BeautifulSoup(r.content, 'lxml') #r변수에 저장된 content를 파싱해서 soup객체에  content 저장
        #req에 저장한 html을 파싱해서 soup 이라는 변수에 저장
        tags = soup.find_all('dt', class_="us_titb_l3") #is_company_card 클래스인 div 태그에서 a 붙은 태그(a href 찾음)
        
        if len(tags) == 0:
            break
        
        for tag in tags:
            name = tag.select('a')[0].text
            if name == comp:
                comp_uid = tag.select('a')[0]['href'].split('/')[2]
                new_url = f'https://www.jobplanet.co.kr/companies/{comp_uid}/landing'
                return get_comp_info_crawl(new_url,comp_uid)
            
    print('there is no comp founded in all pages')
    return False, None

#회사 정보 요청 함수
def get_info(urls, comp):
    return get_comp_info(urls, comp)

# 회사 이름 입력받아 url로 만들어주는 함수 
def get_url(comp):
    url=r'https://www.jobplanet.co.kr/search/companies/{comp}?page={page}' #여기에 회사 이름 추가해야됨
    urls = [ url.format(comp=comp, page=page) for page in range(1, 99) ] # 1페이지부터 2페이지까지 url 생성
    return get_info(urls, comp)


'''
회사 uid (회사 고유 기업번호로) /get_url로 구하기 완료
회사 이름 (맨 상단 주식회사 이름) 완료
회사 주소 (주소) 완료
회사 로고 (이미지 주소로 저장) 완료
사업 내용 (산업) 완료
회사 설립 년월(설립(df로 저장하고 나중에 저장형식대로 .빼기),저장은 YYYYMM형식의 string) 완료
회사 규모((기업형태)중소/대 기업등) 완료
기업 대표 사이트(웹사이트 링크 주기 링크 없으면 예외처리) 
처리 여부(처리되면 Y 아니면 N)
최초 저장 일자 (YYYYMMDD)
수정 일자 (YYYYMMDD) 
'''
def get_comp_info_crawl(new_url,comp_uid): #get_url(기업명)실행으로 받은 기업정보 url로 접속 테스트는 그냥 바로 기업정보 url로 해보기
    r = requests.get(new_url, headers=HEADERS) #requests로 url 접근 요청
    soup = BeautifulSoup(r.content, 'lxml') #r변수에 저장된 content를 파싱해서 soup객체에  content 저장
    #추출해야할 정보들 죄다 zip로 묶어줌 uid는 저위에 comp_uid

    #회사 uid
    #uid는 get_comp_info 함수에서 인자로 받음
    
    #회사이름
    elements_comp_name = soup.find('div',class_="company_name").find('a')
    comp_name_temp=str(elements_comp_name).split('>')[1]
    comp_name=comp_name_temp.split('<')[0] 

    #회사 주소
    elements_comp_loc= soup.find('ul',class_='basic_info_more')#.find('dl',class_= 'info_item_more') #회사주소'
    loc= elements_comp_loc.text.split('\n'*5) #5개 개행문자로 구분자니까 5개의 개행문자를 제거해서 인덱스 순대로 정보 나오게 설정
    comp_loc=loc[2].split('\n')[1]  # 첫번째 줄을 제외한 부분을 선택

    #회사 로고
    elements_comp_thumb = soup.find('span',class_='img_wrap')
    comp_thumb = str(elements_comp_thumb).split('"')[5] # 큰 따옴표 기준으로 구분

    #사업 내용
    elements_comp_cont = soup.find('strong', class_ = 'info_item_subject')
    comp_cont = elements_comp_cont.text
    
    elements_comp_cont = soup.find('strong', class_ = 'info_item_subject')
    pattern = r"(?<=\>).+?(?=\<)" # 정규표현식 패턴
    comp_cont = re.findall(pattern, str(elements_comp_cont)) # re.findall() 메서드로 일치하는 패턴 추출

    
    #회사 설립 년월
    elements_comp_founded = soup.find('div', class_= 'basic_info_item ico_establish').find('strong')
    pattern_2 = re.search(r'<strong[^>]*>(.*?)</strong>', str(elements_comp_founded))
    comp_founded= pattern_2.group(1) #기업 규모만 추출

    #회사 규모 (어떤 형태들이 있는지 확인 중소 대)
    elements_comp_size = soup.find('div', class_= 'basic_info_item ico_company_shape').find('strong')
    pattern_3 = re.search(r'<strong[^>]*>(.*?)</strong>', str(elements_comp_size))
    comp_size= pattern_3.group(1) #기업 규모만 추출

    #기업 대표 사이트
    elements_comp_url = soup.find('ul', class_="basic_info_more").find('a')
    comp_url = str(elements_comp_url).split('"')[1]
    
    comp_info_dict={
        'comp_uid' : comp_uid,
        'comp_name': comp_name,
        'comp_loc' : comp_loc,
        'comp_thumb' : comp_thumb,
        'comp_cont' : comp_cont,
        'comp_founded': comp_founded,
        'comp_size' : comp_size,
        'comp_url' : comp_url
        
    } #기업 정보 key, value로 담은 딕셔너리
    return get_comp_info_df(comp_info_dict) #기업정보들 튜플로 반환

def get_comp_info_df(comp_info_dict):
    df=pd.DataFrame.from_dict({'':comp_info_dict}, orient='index') #데이터를 데이터프레임으로 저장
    return df

if __name__ == '__main__':
    print(get_url('씨제이(주)'))





