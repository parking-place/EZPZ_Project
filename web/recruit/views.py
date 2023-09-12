from django.shortcuts import render, redirect

from .services import RecruitCont

def recruit_page(request):
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    elif request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
        
    # 아무것도 안넘어왔다면 메인페이지로 redirect
    if comp_uid is None:
        redirect('/')
        
    # 데이터 입력 : 비즈니스 로직 실행
    recruit_cont = RecruitCont(comp_uid)
    context = recruit_cont.get_recruit_info()
    
    return render(request, 'recruit/recruit.html', context)
