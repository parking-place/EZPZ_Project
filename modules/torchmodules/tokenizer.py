# tokenizer.py
# 키워드 추출 및 다양한 곳에서 사용할 토크나이저를 생성합니다.
# 주요 함수 ]
#   get_keyword_nnp : 고유 명사를 추출합니다.
#   get_keyword_nng : 일반 명사를 추출합니다.

# 총 4개의 라이브러리가 필요하며, 아래의 명령어로 설치 가능합니다.
# 필요 라이브러리(4) ]
# KoNLPy : 한나눔
#   pip install konlpy

# Kiwi 의존 라이브러리
#pip install dataclasses

# Kiwi : Kiwipiepy
#pip install kiwipiepy
# =================================================================
# IMPORT
# =================================================================
import pandas
# tokenizer
from konlpy.tag import Hannanum
from kiwipiepy import Kiwi, basic_typos # Kiwi 오타정정 커스터마이징 모듈

# 불용단어 설정
from kiwipiepy.utils import Stopwords

# 키워드 추출
from collections import Counter

# consts
hann = Hannanum()
kiwi = Kiwi(typos=basic_typos) # 오타 정정 내장 모듈 사용해 선언
stopwords = Stopwords() # 불용(무시)할 단어객체
# 무시할 단어는 여기에 추가
ignore_list = [
    '회사', '업무', '근무', '제도', '사용', '경우', '기업', '단점', '가능'
]

def preprocess_reviews(review_list) -> list:
    """
    리뷰 리스트를 받아 일괄적으로 특수부호 등을 제거합니다.
    
    parameters ]
        reivew_list : list<str> - 처리할 문자열로 이루어진 list
    returns ]
        list<str>   - 전처리 완료된 list
    """
    return list(
        map(
            # escape 문자, 따옴표 등 제외
            lambda x : x.replace('\r', '').replace('\n', '').replace('"', '').replace("'", ''),
            review_list
        )
    )



def get_ncp(sentence) -> list:
    """
    문장을 받으면 동작성명사(ncpa) 상태성명사(ncps)를 구분해 tokenization한다.
    형태소들을 list로 묶어 중복 없이 반환하는 함수.
    
    parameters ]
        sentence    - str   : 분석할 문자열
        
    return ]
        list<str>   : 형태소들이 담긴 list
    """
    # pos를 사용한 것 보다 analyze 토크나이징이 조금 더 원하는 단위로 뽑기 쉬웠다.
    anals = hann.analyze(sentence)
    word_list = []
    
    # 분석된 것이 없다면 return return
    if len(anals) < 1:
        return None
    
    # list 단위로 분석하기 때문에 3dim list
    for words in anals:
        for tokens in words:
            for word, tag in tokens:
                if tag == 'ncpa' or tag == 'ncps':
                    word_list.append(word)
                    
    # 중복 제거해 return
    return list(set(word_list))



def hann_anal(review_list) -> list:
    """
    리뷰 리스트를 받아 한나눔(Hannanum) 형태소 분석기로 명사들을 추출하며,
    추출한 단어들을 중복없이 return 합니다.
    
    parmeters ]
        review_list : list<str> - 분석할 문자열이 담긴 list
        
    returns ]
        list<str> : 최종 분석한 형태소들이 담긴 list
    """
    hann_anal = []
    
    #  필터링 함수 일괄 실행 + 빈 리스트 필터링
    [hann_anal.extend(el) for el in list(map(get_ncp, review_list)) if len(el) > 0]
    hann_anal = list(set(hann_anal)) # 명사 추출용이기 때문에 다시 한번 중복 제거
    
    return hann_anal



def set_kiwi(review_list):
    """
    한나눔으로 추출한 명사를 Kiwi 형태소 분석기에 셋팅해 줍니다.
    
    parameters ]
        review_list : list<str> - 분석할 문자열이 담긴 list
    """
    hann_nouns = hann_anal(review_list)
    map(lambda x : kiwi.add_user_word(x, 'NNP', 2), hann_nouns)
    
    # 불용 단어 설정
    for ignore in ignore_list:
        stopwords.add((ignore, 'NNP'))
        stopwords.add((ignore, 'NNG'))



def args_to_list(args:(pandas.DataFrame|list), cont_type=None) -> list:
    """
    DataFrame이나 list에 받아, 데이터에 맞는 처리를 해 list로 반환합니다.
    
    parameters ]
        raw_str     - pandas.DataFrame | list<str>  : 원문
        cont_type   - str (default None)            : review | news
                                                => 리뷰 분석 or 뉴스 분석
            
    returns ]
        list<str>   : 처리된 list
    """
    # list : 그대로 반환
    if type(args) is list:
        return args
    
    # DataFrame : 처리해 줍니다.
    elif type(args) is pandas.DataFrame:
        # 파라미터 처리
        if cont_type == 'review':
            col_name = 'review_cont'
        elif cont_type == 'news':
            col_name = 'news_cont'
            
        else:
            if cont_type:
                raise KeyError(f"This DataFrame doesn't have column '{col_name}'!\nDid you check the parameter 'cont_type'?")
            # DataFrame을 입력했는데 type을 입력하지 않았다면 raise 
            raise KeyError(f"Did you check the parameter 'cont_type'?")
        
        # 통과한 경우
        try:
            return args[col_name]
        
        except Exception as e:
            print(e)
            
    # 통과하지 못했다면 : 다른 타입의 파라미터가 들어온 경우
    raise TypeError('args_to_list can get parameter for only list and pandas.DataFrame')



# ========================================
# MAIN FUNCTIONS
# ========================================
def get_keyword_nnp(raw_str:(pandas.DataFrame|list), cont_type=None, size:int=10) -> list:
    """
    분석할 문자열이 담긴 list 혹은 DataFrame을 받아
    고유 명사를 추출해 (단어, 빈도수) 형태의 리스트로 반환합니다.
    parameters ]
        raw_str     - pandas.DataFrame | list<str>  : 분석할 원문
        cont_type   - str                           : review | news
                                                => 리뷰 분석 or 뉴스 분석
        size        - int (default 10)              : 출력할 키워드 개수
        
    returns ]
        list<tuple<keyword, int>>   : 추출된 키워드 리스트
                                    => (키워드, 빈도수) 형태의 튜플로 구성됨
    """
    # 파라미터 처리
    review_list = args_to_list(raw_str, cont_type)
    # kiwi 준비
    set_kiwi(review_list)
    
    # main 로직
    kiwi_result = []
    
    # 2 dim list에 담기지 않도록 comprehension 처리
    [kiwi_result.extend(el) for el in list(map(
        # split_complex = False : 너무 자잘하게 분석하지 않도록 한다.
        # normalize_coda = True : ㅋㅋㅋ, ㅎㅎㅎ 등 분리
        lambda x : kiwi.tokenize(x, split_complex=False, normalize_coda=True, stopwords=stopwords),
        review_list
    ))]
    
    # 고유명사 추출
    tokens = [token.form for token in kiwi_result if token.tag.find('NNP') != -1]
    # 가장 많이 나오는 단어 (기업명 추정) 제외
    return Counter(tokens).most_common(size+1)[1:]



def get_keyword_nng(raw_str:(pandas.DataFrame|list), cont_type, size:int=10) -> list:
    """
    분석할 문자열이 담긴 list 혹은 DataFrame을 받아
    일반 명사를 추출해 (단어, 빈도수) 형태의 리스트로 반환합니다.
    parameters ]
        raw_str     - pandas.DataFrame | list<str>  : 분석할 원문
        cont_type   - str                           : review | news
                                                => 리뷰 분석 or 뉴스 분석
        size        - int (default 10)              : 출력할 키워드 개수
        
    returns ]
        list<tuple<keyword, int>>   : 추출된 키워드 리스트
                                    => (키워드, 빈도수) 형태의 튜플로 구성됨
    """
    # 파라미터 처리
    review_list = args_to_list(raw_str, cont_type)
    # kiwi 준비
    set_kiwi(review_list)
    
    # main 로직
    kiwi_result = []
    
    # 2 dim list에 담기지 않도록 comprehension 처리
    [kiwi_result.extend(el) for el in list(map(
        # split_complex = False : 너무 자잘하게 분석하지 않도록 한다.
        # normalize_coda = True : ㅋㅋㅋ, ㅎㅎㅎ 등 분리
        lambda x : kiwi.tokenize(x, split_complex=False, normalize_coda=True, stopwords=stopwords),
        review_list
    ))]
    
    # 일반 명사 : 한 글자 단어는 제외했다.
    return Counter([token.form for token in kiwi_result if token.tag.find('NNG') != -1 and len(token.form) > 1]).most_common(size)


# =========================
# TEST CODE
# =========================
if __name__ == '__main__':
    # import only for test
    import time # 모델 로딩 속도 확인
    
    #st_time = time.time()
    
    DATA_DIRECTORY_PATH = '/app/data/reviews/'
    # list test
    review_list = [el for el in pandas.read_csv(DATA_DIRECTORY_PATH + '삼성전자_job_planet.csv')['review_cont']]
    #review_list = args_to_list(review_list) pass
    # DataFrame test
    review_df = pandas.read_csv(DATA_DIRECTORY_PATH + '삼성전자_job_planet.csv')
    #review_list = args_to_list(review_df, 'review') pass
    
    #ed_time = time.time()
    #print(f'for read csv : {ed_time - st_time} sec')  0.1548004150390625 sec
    
    
    
    
    # ========================================
    # MAIN FUNCTION TEST
    # ========================================
    # NNG
    st_time = time.time()
    print(get_keyword_nng(review_list, 'review', 20))
    ed_time = time.time()
    print(f'run main function(NNG) : {ed_time - st_time} sec')# 38.47996139526367 sec
    
    # NNP
    st_time = time.time()
    print(get_keyword_nng(review_df, 'review', 20))
    ed_time = time.time()
    print(f'run main function(NNG) : {ed_time - st_time} sec')# 9.4391028881073 sec
    
    
    
    # ========================================
    # TEST EACH FUNCTIONS
    # ========================================
    # set_kiwi() START
    #st_time = time.time()
    #hann_nouns = hann_anal(review_list)
    #ed_time = time.time()
    #print(f'for noun tokenization : {ed_time - st_time} sec') for noun tokenization : 17.434030055999756 sec
    
    #st_time = time.time()
    # kiwi vocabulary에 한나눔으로 추출한 명사를 넣어줍시다.
    #map(lambda x : kiwi.add_user_word(x, 'NNP', 2), hann_nouns) # 중요도는 2정도로 설정해 줍니다.
    #ed_time = time.time()
    #print(f"for set kiwi's vocabulary : {ed_time - st_time} sec") 0.0 sec
    # set_kiwi() END
    # ========================================//
    
    
    # get_keyword_nn* START
    #size = 20 # param
    #kiwi_result = []
    
    #[kiwi_result.extend(el) for el in list(map(
        # split_complex = False : 너무 자잘하게 분석하지 않도록 한다.
        # normalize_coda = True : ㅋㅋㅋ, ㅎㅎㅎ 등 분리
    #    lambda x : kiwi.tokenize(x, split_complex=False, normalize_coda=True),
    #    review_list
    #))]
    
    # 테스트 시 주석 풀어 사용
    # get_keyword_nng
    #st_time = time.time()
    #print(Counter([token.form for token in kiwi_result if token.tag.find('NNG') != -1 and len(token.form) > 1]).most_common(size))
    #ed_time = time.time()
    #print(f'get nnp : {ed_time - st_time} sec')
    
    # get_keyowrd_nnp
    #st_time = time.time()
    #tokens = [token.form for token in kiwi_result if token.tag.find('NNP') != -1]
    # 가장 많이 나오는 단어 (기업명 추정) 제외
    #print(Counter(tokens).most_common(size+1)[1:])
    #ed_time = time.time()
    #print(f'get nng : {ed_time - st_time} sec')
    
    # get_keyword_nn* END
    # ========================================//
    
# TEST CODE END