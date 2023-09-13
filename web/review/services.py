# review/services.py
# 기업 리뷰에 대한 비즈니스 로직을 작성합니다.

# 수정 예정 사항
# 키워드 집계에서 다음의 단어 제외 : 회사, 업무, 근무, 제도, 사용, 경우, 기업, 단점, 가능
import pandas as pd

from .models import CompInfo, CompReview, SumReview # SumReview : 통계 테이블

class ReviewCont(object):
    
    def __init__(self, comp_uid, review_tab):
        self.term_to_str = {
            1: '상반기', 2: '하반기', # 반기별(half)
            3: '1분기', 4: '2분기', 5: '3분기', 6: '4분기' # 분기별(quarter)
        }
        # 기본 정보 불러오기
        self.comp_uid = comp_uid
        comp_name = CompInfo.objects.get(comp_uid=comp_uid).comp_name
        self.context = {
            'active': 'review',
            'review_tab': review_tab,
            'comp_uid': comp_uid,
            'comp_name': comp_name,
        }
        
        # 통계 데이터 담을 dict
        self.stat_details = {}
    
    def get_comp_review(self) -> dict:
        # 리뷰 정보 담을 리스트 초기화
        pos_reivew_list = []
        neg_reivew_list = []
        
        # 리뷰 불러오기 : 최근순
        review_infos = CompReview.objects.filter(comp_uid=self.comp_uid).order_by('-review_date')
        
        if len(review_infos) == 0:
            self.context['msg'] = '리뷰 정보가 없습니다.'
            return self.context
        
        # 리뷰 정보 있는 경우
        # 각 리뷰는 20개까지만 불러와 출력합니다.
        review_details = {}
        for info in review_infos:
            # 긍정적 리뷰
            if info.review_senti_pred == 'P' and len(pos_reivew_list) < 20:
                pos_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
                
            # 부정적 리뷰
            elif info.review_senti_pred == 'N' and len(neg_reivew_list) < 20:
                neg_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
        # context에 넣어줍니다.
        review_details['pos'] = pos_reivew_list
        review_details['neg'] = neg_reivew_list
        review_details['pos_len'] = len(pos_reivew_list)
        review_details['neg_len'] = len(neg_reivew_list)
        
        return review_details
        
        
        
    def get_total_summarized(self) -> dict:
        tot_summary = {}
        total_stat = SumReview.objects.get(comp_uid=self.comp_uid, sum_year=0, sum_term=0)
        
        # 로딩 성공한 경우에만 조회합니다.
        if total_stat is not None:
            # 총 별점, 키워드
            tot_summary['rate'] = round(total_stat.avg_rate, 2)
            tot_summary['keywords'] = [el.split('_')[0] for el in total_stat.sum_keyword.split('#')]
            
            # 긍정 / 부정 총 요약
            tot_summary['pos_sum'] = total_stat.sum_cont_neg
            tot_summary['neg_sum'] = total_stat.sum_cont_pos
            return tot_summary
        
        
        
    def organize_stat_datas(self) -> None:
        # line graph
        self.stat_details['time_cols'] = [f'{el.sum_year} {self.term_to_str[el.sum_term]}' for el in self.stat_datas]
        # 별점 : 소수점 두자리
        self.stat_details['time_rate'] = [round(el.avg_rate, 2) for el in self.stat_datas]
        self.stat_details['time_keywords'] = []
        
        # 키워드 : hasing & to string
        keyword_list = []
        value_list = []
        for row in self.stat_datas:
            data = row.sum_keyword.split('#')
            keyword_str = ''.join([el.split('_')[0] + ', ' if idx < (len(data) - 1) else el.split('_')[0] for idx, el in enumerate(data)])
            
            self.stat_details['time_keywords'].append(keyword_str)
            
            keyword_list.extend([el.split('_')[0] for el in data])
            value_list.extend([el.split('_')[1] for el in data])
            
        # word cloud
        word_cloud_df = pd.DataFrame({
            'keyword': keyword_list, 'value': value_list
        }).astype({
            'keyword': 'object', 'value': 'int16'
        })
        
        # grouping, get top 20
        word_cloud_df = word_cloud_df.groupby('keyword').sum('value').reset_index()
        word_cloud_df = word_cloud_df.sort_values(by='value', ascending=False).head(20)
        
        # 값을 dict에 넣어 반환
        self.stat_details['word_cloud'] = []
        for x, value in zip(word_cloud_df['keyword'], word_cloud_df['value']):
            self.stat_details['word_cloud'].append({
                'x': x, 'value': value
            })
        
        
        
    def get_review_stat_half(self):
        # 기본 데이터 load
        self.context['review_details'] = self.get_comp_review()
        self.context['tot_summary'] = self.get_total_summarized()
        
        # 통계 데이터 load
        self.stat_datas = SumReview.objects.filter(comp_uid=self.comp_uid, sum_term__in=[1, 2])
        
        # 데이터가 없다면 return
        if len(self.stat_datas) == 0:
            self.context['msg'] = '리뷰 통계 데이터를 지원하지 않는 기업입니다.'
            return self.context
        
        # 데이터 있는 경우 데이터 형태 맞춰 return
        self.organize_stat_datas()
        self.context['stat_details'] = self.stat_details
        
        return self.context
        
        
        
    def get_review_stat_quarter(self):
        
        # 기본 데이터 load
        self.context['review_details'] = self.get_comp_review()
        self.context['tot_summary'] = self.get_total_summarized()
        
        # 통계 데이터 load
        self.stat_datas = SumReview.objects.filter(comp_uid=self.comp_uid, sum_term__in=[3, 4, 5, 6])
        
        # 데이터가 없다면 return
        if len(self.stat_datas) == 0:
            self.context['msg'] = '리뷰 통계 데이터를 지원하지 않는 기업입니다.'
            return self.context
        
        # 데이터 있는 경우 데이터 형태 맞춰 return
        self.organize_stat_datas()
        self.context['stat_details'] = self.stat_details
        
        return self.context
