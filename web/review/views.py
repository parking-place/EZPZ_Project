from django.shortcuts import render, redirect

from .services import ReviewCont

def review_half(request):
    try:
        # 파라미터 처리
        if request.method == 'GET':
            comp_uid = request.GET.get('comp_uid', None)
        if request.method == 'POST':
            comp_uid = request.POST.get('comp_uid', None)
        
        # 파라미터 제대로 안 넘어온 경우 메인 페이지로
        if comp_uid is None:
            return redirect('/')
            
        # 파라미터 넘어옴 : 회사 정보 불러오기 & 기본 데이터 로드
        # 데이터 입력 : 비즈니스 로직 실행
        review_cont = ReviewCont(comp_uid, 'half')
        context = review_cont.get_review_stat_half()
        
        return render(request, 'review/review.html', context)
    
    except Exception as e:
        print(e)
        return redirect('/')



def review_quarter(request):
    try:
        # 파라미터 처리
        if request.method == 'GET':
            comp_uid = request.GET.get('comp_uid', None)
        if request.method == 'POST':
            comp_uid = request.POST.get('comp_uid', None)
        
        # 파라미터 제대로 안 넘어온 경우 메인 페이지로
        if comp_uid is None:
            return redirect('/')
        
        # 파라미터 넘어옴 : 회사 정보 불러오기 & 기본 데이터 로드
        # 데이터 입력 : 비즈니스 로직 실행
        review_cont = ReviewCont(comp_uid, 'quarter')
        context = review_cont.get_review_stat_quarter()
        
        return render(request, 'review/review.html', context)
    
    except Exception as e:
        print(e)
        return redirect('/')
