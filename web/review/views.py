from django.shortcuts import render, redirect

import pandas as pd

from .models import CompInfo, CompReview, SumReview # SumReview : 통계 테이블



def load_basic_reviews(comp_uid, review_tab):
    """
    기업 UID가 담긴 comp_uid 변수로 리뷰 데이터를 검색하고
    html에 넘겨줄 dict, context를 생성해 데이터를 채워준 후 넘겨줍니다.
    
    parameters ]
        comp_uid    : int   - 기업 UID
        reivew_tab  : str   - 현재 탭
                                분기별 : half
                                반기별 : quart
    returns ]
        context : dict  - 데이터가 채워진 dict
    """
    # =============================================
    # CONSTANTS
    # =============================================
    term_to_str = {
        # 반기별
        1: '상반기', 2: '하반기',
        # 분기별
        3: '1분기', 4: '2분기', 5: '3분기', 6: '4분기'
    }
    # 회사 이름 불러오기
    comp_name = CompInfo.objects.get(comp_uid=comp_uid).comp_name
    
    # html에 넘겨줄 데이터들
    context = {
        'active': 'review',
        'review_tab': review_tab,
        'comp_uid': comp_uid,
        'comp_name': comp_name,
    }
    
    # 사용할  변수들
    pos_reivew_list = [] # 긍정적 리뷰 : 20개만 담는다.
    neg_reivew_list = [] # 부정적 리뷰 : 20개만 담는다.
    
    # =============================================
    # REVIEW DATA LOADING START
    # =============================================
    
    # 리뷰 불러오기 : 최근순
    review_infos = CompReview.objects.filter(comp_uid=comp_uid).order_by('-review_date')
    
    # -------------------------
    # 1. 리뷰 컨테이너 (낱개)
    # -------------------------
    if len(review_infos) == 0:
        context['msg'] = '리뷰 정보가 없습니다.'
        
    else:
        review_details = {}
        # context에 넣어주기 전 처리
        for info in review_infos:
            # ----------------------------------------
            # 긍정적/부정적 리뷰 구분 & append
            # ----------------------------------------
            # 20개 까지만 출력합니다.
            # 1-1. 긍정적 리뷰
            if info.review_senti_pred == 'P' and len(pos_reivew_list) < 20:
                pos_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
                
            # 1-2. 부정적 리뷰
            elif info.review_senti_pred == 'N' and len(neg_reivew_list) < 20:
                neg_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
        # 1-3. context에 넣어주기
        review_details['pos'] = pos_reivew_list
        review_details['neg'] = neg_reivew_list
        context['review_details'] = review_details
        
        # -------------------------
        # 2. 전체 요약 데이터
        # -------------------------
        # 데이터 로드
        tot_summary = {}
        total_stat = SumReview.objects.get(comp_uid=comp_uid, sum_year=0, sum_term=0)
        
        # 로딩 성공한 경우에만 조회합니다.
        if total_stat is not None:
            # 2-1. 총 별점
            tot_summary['rate'] = round(total_stat.avg_rate, 2)
            # 2-2. 총 키워드
            tot_summary['keywords'] = [el.split('_')[0] for el in total_stat.sum_keyword.split('#')]
            
            # 2-3. 긍정 / 부정 총 요약
            tot_summary['pos_sum'] = total_stat.sum_cont_neg
            tot_summary['neg_sum'] = total_stat.sum_cont_pos
            context['tot_summary'] = tot_summary
        
        # -------------------------
        # 3. 시계열 통계 데이터(그래프, 워드 클라우드)
        # -------------------------
        stat_details = {}
        # # 3-1. 파라미터 처리, 컬럼 지정
        if review_tab == 'half': # 반기별
            stat_datas = SumReview.objects.filter(comp_uid=comp_uid, sum_term__in=[3, 4, 5, 6])
            
        elif review_tab == 'quart': # 분기별
            stat_datas = SumReview.objects.filter(comp_uid=comp_uid, sum_term__in=[1, 2])
            
        else: # return : 정상 접근이 아닌경우
            context['msg'] = '리뷰 통계 데이터를 지원하지 않는 기업입니다.'
            return context
        
        # 3-2. line graph
        # 컬럼 지정
        stat_details['time_cols'] = [f'{el.sum_year} {term_to_str[el.sum_term]}' for el in stat_datas]
        # 별점
        stat_details['time_rate'] = [round(el.avg_rate, 2) for el in stat_datas]
        
        # 키워드는 10개씩 저장된다.
        keyword_str = [el.sum_keyword.split('#') for el in stat_datas]
        keyword_df = pd.DataFrame({
            'keyword': [el.split('_')[0] for row in keyword_str for el in row],
            'value': [el.split('_')[1] for row in keyword_str for el in row]
        })
        
        # 3-3. word cloud
        # 타입변경 + grouping 해 중복 재거
        # 그루핑 해 중복을 재거합니다.
        word_cloud_df = keyword_df.astype({
            'keyword': 'str', 'value': 'int16'
        }).groupby('keyword').sum('value').reset_index()
        # 상위 20개 키워드만 추출합니다.
        word_cloud_df = word_cloud_df.sort_values(by='value', ascending=False).head(20)
        
        # 값을 dict에 넣어 반환
        stat_details['word_cloud'] = []
        for x, value in zip(word_cloud_df['keyword'], word_cloud_df['value']):
            stat_details['word_cloud'].append({
                'x': x, 'value': value
            })
            
        context['stat_details'] = stat_details
        # DATA LOADING END
        # ============================================= //
        
    return context



def review_page(request):
    """
    리뷰 페이지 - 반기별 페이지(기본값)에 들어갈 데이터를 불러옵니다.
    """
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    if request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
    
    # 아무것도 안넘어왔다면 메인페이지로 redirect
    if comp_uid is None:
        redirect('/')
        
    # 파라미터 넘어옴 : 회사 정보 불러오기 & 기본 데이터 로드
    context = load_basic_reviews(comp_uid, 'half')
    
    return render(request, 'review/review.html', context)



def review_quart(request):
    """
    리뷰 페이지 - 반기별 페이지에 들어갈 데이터를 불러옵니다.
    """
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    if request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
    
    # 아무것도 안넘어왔다면 메인페이지로 redirect
    if comp_uid is None:
        redirect('/')
        
    # 파라미터 넘어옴 : 회사 정보 불러오기 & 기본 데이터 로드
    context = load_basic_reviews(comp_uid, 'quart')
    
    return render(request, 'review/review.html', context)