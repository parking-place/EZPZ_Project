from django.shortcuts import render, redirect

from .services import NewsCont


def comp(request):
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    if request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
    
    # 파라미터 제대로 안 넘어온 경우 메인 페이지로
    if comp_uid is None:
        return redirect('/')
    
    # 데이터 입력 : 비즈니스 로직 실행
    news_cont = NewsCont(comp_uid)
    context = news_cont.get_comp_news()
    
    return render(request, 'comp/comp.html', context)
