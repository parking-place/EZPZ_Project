# ezpz_tokenizer.py
# tokenizer.py를 클래스화 시킨 모듈입니다.
# import
import pandas
from collections import Counter

from konlpy.tag import Hannanum
from kiwipiepy import Kiwi, basic_typos
from kiwipiepy.utils import Stopwords

class EZPZTokenizer():
    
    def __init__(self, ignore_list):
        self.hann = Hannanum()
        self.kiwi = Kiwi(typos=basic_typos) # 오타 정정 내장 모듈 사용해 선언
        
        # 불용(무시) 단어 설정
        self.stopwords = Stopwords()
        for ignore in ignore_list:
            self.stopwords.add((ignore, 'NNP'))
            self.stopwords.add((ignore, 'NNG'))
            
            
            
    def __get_ncp_only(self, sentence) -> list:
        """
        문장을 받으면 동작성명사(ncpa) 상태성명사(ncps)를 구분해 tokenization한다.
        형태소들을 list로 묶어 중복 없이 반환하는 함수.
        """
        # pos를 사용한 것 보다 analyze 토크나이징이 조금 더 원하는 단위로 뽑기 쉬웠다.
        anals = self.hann.analyze(sentence)
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
    
    
    
    def __set_hannannum_nouns_to_kiwi(self, review_list):
        noun_list = []
        
        #  필터링 함수 일괄 실행 + 빈 리스트 필터링
        [noun_list.extend(el) for el in list(map(self.__get_ncp_only, review_list)) if len(el) > 0]
        hann_nouns = list(set(noun_list)) # 명사 추출용이기 때문에 다시 한번 중복 제거
        
        map(lambda x : self.kiwi.add_user_word(x, 'NNP', 2), hann_nouns)
    
    
    
    def __args_to_list(self, args:(pandas.DataFrame|list), cont_type=None) -> list:
        """
        DataFrame이나 list에 받아, 데이터에 맞는 처리를 해 list로 반환합니다.
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
    def get_keyword_nnp(self, raw_str:(pandas.DataFrame|list), cont_type=None, size:int=10) -> list:
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
        review_list = self.__args_to_list(raw_str, cont_type)
        
        # 명사 설정
        self.__set_hannannum_nouns_to_kiwi(review_list)
        
        # 2 dim list에 담기지 않도록 comprehension 처리
        kiwi_result = []
        [kiwi_result.extend(el) for el in list(map(
            # split_complex = False : 너무 자잘하게 분석하지 않도록 한다.
            # normalize_coda = True : ㅋㅋㅋ, ㅎㅎㅎ 등 분리
            lambda x : self.kiwi.tokenize(x, split_complex=False, normalize_coda=True, stopwords=self.stopwords),
            review_list
        ))]
        
        # 고유명사(NNP) 추출
        tokens = [token.form for token in kiwi_result if token.tag.find('NNP') != -1]
        # 가장 많이 나오는 단어 (기업명 추정) 제외
        return Counter(tokens).most_common(size+1)[1:]




    def get_keyword_nng(self, raw_str:(pandas.DataFrame|list), cont_type, size:int=10) -> list:
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
        review_list = self.__args_to_list(raw_str, cont_type)
        
        # 명사 설정
        self.__set_hannannum_nouns_to_kiwi(review_list)
        
        # 2 dim list에 담기지 않도록 comprehension 처리
        kiwi_result = []
        [kiwi_result.extend(el) for el in list(map(
            # split_complex = False : 너무 자잘하게 분석하지 않도록 한다.
            # normalize_coda = True : ㅋㅋㅋ, ㅎㅎㅎ 등 분리
            lambda x : self.kiwi.tokenize(x, split_complex=False, normalize_coda=True, stopwords=self.stopwords),
            review_list
        ))]
        
        # 일반명사(NNG) 추출 : 한 글자 단어 제외
        return Counter([token.form for token in kiwi_result if token.tag.find('NNG') != -1 and len(token.form) > 1]).most_common(size)



# =========================
# TEST CODE
# =========================
if __name__ == '__main__':
    # import only for test
    import time # 모델 로딩 속도 확인
    
    DATA_DIRECTORY_PATH = '/app/data/reviews/'
    # list test
    review_list = [el for el in pandas.read_csv(DATA_DIRECTORY_PATH + '삼성전자_job_planet.csv')['review_cont']]
    review_df = pandas.read_csv(DATA_DIRECTORY_PATH + '삼성전자_job_planet.csv')
    
    # EZPZTokenzier 선언
    st_time = time.time()
    tokenizer = EZPZTokenizer(ignore_list=['회사', '업무', '근무', '제도', '사용', '경우', '기업', '단점', '가능'])
    ed_time = time.time()
    print(f'to declare EZPZ tokenizer : {ed_time - st_time} sec') # 1.692871332168579 sec
    
    
    # ========================================
    # MAIN FUNCTION TEST
    # ========================================
    # NNG
    st_time = time.time()
    print(tokenizer.get_keyword_nng(review_list, 'review', 20))
    ed_time = time.time()
    print(f'run main function(NNG) : {ed_time - st_time} sec')# 35.244385957717896 sec
    
    # NNP
    st_time = time.time()
    print(tokenizer.get_keyword_nng(review_df, 'review', 20))
    ed_time = time.time()
    print(f'run main function(NNG) : {ed_time - st_time} sec')# 8.629792213439941 sec
