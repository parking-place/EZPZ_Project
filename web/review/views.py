from django.shortcuts import render, redirect

from .models import CompInfo, CompReview

def review_page(request):
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    if request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
    
    # 아무것도 안넘어왔다면 메인페이지로 redirect
    if comp_uid is None:
        redirect('/')
    
    # 파라미터 넘어옴 : 회사 정보 불러오기
    comp_name = CompInfo.objects.get(comp_uid=comp_uid).comp_name
    
    # html에 넘겨줄 데이터들
    context = {
        'active': 'review',
        'comp_uid': comp_uid,
        'comp_name': comp_name,
    }
    
    # =============================================
    # DATA LOADING START
    # =============================================
    # 사용할  변수들
    rate_sum = 0 # 총 평점 계산
    pos_reivew_list = [] # 긍정적 리뷰 : 20개만 담는다.
    neg_reivew_list = [] # 부정적 리뷰 : 20개만 담는다.
    
    # 리뷰 불러오기
    review_infos = CompReview.objects.filter(comp_uid=comp_uid).order_by('-review_date')
    
    # 1. 리뷰 컨테이너 (낱개)
    if len(review_infos) == 0:
        context['msg'] = '채용공고 정보가 없습니다.'
        
    else:
        # context에 넣어주기 전 처리
        for info in review_infos:
            # 1-1. 평점 계산
            rate_sum += info.review_rate
            
            # ----------------------------------------
            # 긍정적/부정적 리뷰 구분 & append
            # ----------------------------------------
            # [[[모델 서빙 미완성으로 senti_orig로 구분합니다.]]]
            # 20개 까지만 출력합니다.
            # 1-2. 긍정적 리뷰
            if info.review_senti_orig and len(pos_reivew_list) < 20:
                pos_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': info.is_office,
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
                
            # 1-3. 부정적 리뷰
            elif not(info.review_senti_orig) and len(neg_reivew_list) < 20:
                neg_reivew_list.append({
                    'cont': info.review_cont,
                    'is_office': info.is_office,
                    'color': '#699BF7' if info.is_office else '#ff9984',
                })
                
        # 1-4. context에 넣어주기
        context['pos_review'] = pos_reivew_list
        context['neg_review'] = neg_reivew_list
        
        # 1-5. 총 평점 계산
        rate_sum = round((rate_sum / len(review_infos)), 2)
    
    
    # 2. 그래프 - 시계열 데이터
    
    
    
    # DATA LOADING END
    # ============================================= //
    
    
    
    
    return render(request, 'review/review.html', context)



def review_quart(request):
    return render(request, 'review/review.html')