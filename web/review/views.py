from django.shortcuts import render, redirect

import pandas as pd

from .services import ReviewCont



def review_half(request):
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
    # 데이터 입력 : 비즈니스 로직 실행
    review_cont = ReviewCont(comp_uid, 'half')
    context = review_cont.get_review_stat_half()
    
    return render(request, 'review/review.html', context)



def review_quarter(request):
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
    # 데이터 입력 : 비즈니스 로직 실행
    review_cont = ReviewCont(comp_uid, 'quarter')
    context = review_cont.get_review_stat_quarter()
    
    return render(request, 'review/review.html', context)
