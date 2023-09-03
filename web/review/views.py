from django.shortcuts import render, redirect

from .models import CompInfo, CompReview


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
    rate_sum = 0 # 총 평점 계산
    pos_reivew_list = [] # 긍정적 리뷰 : 20개만 담는다.
    neg_reivew_list = [] # 부정적 리뷰 : 20개만 담는다.
    
    # =============================================
    # REVIEW DATA LOADING START
    # =============================================
    
    # 리뷰 불러오기 : 최근순
    review_infos = CompReview.objects.filter(comp_uid=comp_uid).order_by('-review_date')
    
    # 1. 리뷰 컨테이너 (낱개)
    if len(review_infos) == 0:
        context['msg'] = '리뷰 정보가 없습니다.'
        
    else:
        # context에 넣어주기 전 처리
        for info in review_infos:
            # 2-1. 평점 계산
            # [[[DB에 데이터가 들어오면 삭제합니다.]]]
            rate_sum += info.review_rate
            
            # ----------------------------------------
            # 긍정적/부정적 리뷰 구분 & append
            # ----------------------------------------
            # [[[모델 서빙 미완성으로 senti_orig로 구분합니다.]]]
            # 20개 까지만 출력합니다.
            # 1-1. 긍정적 리뷰
            if info.review_senti_orig == 'P' and len(pos_reivew_list) < 20:
            # [[[감정평가 모델 완성시 주석 해제 후 사용하세요.]]]
            #if info.review_senti_pred and len(pos_reivew_list) < 20:
                pos_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
                
            # 1-2. 부정적 리뷰
            elif info.review_senti_orig == 'N' and len(neg_reivew_list) < 20:
            # [[[감정평가 모델 완성시 주석 해제 후 사용하세요.]]]
            #elif not(info.review_senti_pred) and len(neg_reivew_list) < 20:
                neg_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': '현직자' if info.is_office else '퇴사자',
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
        # 1-3. context에 넣어주기
        context['pos_review'] = pos_reivew_list
        context['neg_review'] = neg_reivew_list
        
        # 2. 전체 요약 데이터
        # [[DB에 데이터가 채워진 경우 connect, 코드 이어서 작성합니다.]]
        # 2-1. 총 평점
        context['rate_sum'] = round((rate_sum / len(review_infos)), 2)
        
        # 2-2. 전체 리뷰 키워드
        total_keywords = '키워드1#키워드2#키워드3#키워드4#키워드5#키워드6'
        total_keywords = total_keywords.split('#')
        print(total_keywords)
        context['total_keywords'] = total_keywords
        
        # 2-3. 긍정 / 부정 요약
        context['pos_sum'] = '긍정 리뷰 요약'
        context['neg_sum'] = '부정 리뷰 요약'
        
        # 3. 그래프 - 시계열 데이터
        # 시계열 데이터
        # : 리뷰 전체 요약 & 평점
        
        
        
        
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