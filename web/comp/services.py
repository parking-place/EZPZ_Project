# comp/services.py
# 기업 정보에 대한 비즈니스 로직을 작성합니다.
from .models import CompInfo, CompNews

class NewsCont(object):
    
    def __init__(self, comp_uid):
        self.comp_uid = comp_uid
        info = CompInfo.objects.get(comp_uid=self.comp_uid)
        self.context = {
            'active': 'comp',
            'comp_uid': comp_uid,
            'comp_info': {
                'name': info.comp_name,
                'found': f'{info.comp_founded[:4]}.{info.comp_founded[4:]}',
                'loc': info.comp_loc,
                'size': info.comp_size,
                'thumb': info.comp_thumb,
                'url': info.comp_url.replace('http:', 'https:'),
                'cont': info.comp_cont,
            },
        }
    
    def get_comp_news(self) -> dict:
        # 1. 기업 정보 -> 클래스 선언시 로딩합니다.
        # 뉴스 요약, 감정평가에 대한 context 초기화
        self.context['news'] = [ ]
        self.context['pos_ratio'] = 0
        self.context['neg_ratio'] = 0
        self.context['neu_ratio'] = 0
        
        # 2. 뉴스 정보 넣어주기
        news_cnt = 0
        newses = CompNews.objects.filter(comp_uid=self.comp_uid)
        
        self.context['news_len'] = len(newses)
        if len(newses) == 0: # 데이터가 없는 경우 return
            self.context['msg'] = '뉴스 정보가 없습니다.'
            return self.context
        
        # 데이터가 있는 경우에만 넣어줍니다.
        for news in newses:
            if news.news_sum: # 데이터가 있을때만 넣기
                data = {
                    'sum': news.news_sum,
                    'url': news.news_url.replace('http:', 'https:'),
                    # 감정평가에 따른 CSS 컬러값
                    'color': '#87ceeb' if news.news_senti == 1 else '#d3d3d3' if news.news_senti == 0 else '#ffc0cb',
                }
                
                # 3. 감정평가 비율 정보 넣어 주기
                if news.news_senti == 1:
                    self.context['pos_ratio'] += 1
                elif news.news_senti == 2:
                    self.context['neg_ratio'] += 1
                elif news.news_senti == 0:
                    self.context['neu_ratio'] += 1
                
            self.context['news'].append(data)
            
        # 3-2. 감정평가 정보 -> 백분율
        if news_cnt > 0: # 데이터가 있는 경우에만 실행합니다.
            self.context['pos_ratio'] = self.context['pos_ratio'] / news_cnt * 100
            self.context['neg_ratio'] = self.context['neg_ratio'] / news_cnt * 100
            self.context['neu_ratio'] = self.context['neu_ratio'] / news_cnt * 100
        
        return self.context
