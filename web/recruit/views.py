from django.shortcuts import render, redirect

from .services import RecruitCont

def recruit_page(request):
    # 파라미터 처리
    try:
        if request.method == 'GET':
            comp_uid = request.GET.get('comp_uid', None)
        elif request.method == 'POST':
            comp_uid = request.POST.get('comp_uid', None)
            
        # 파라미터 제대로 안 넘어온 경우 메인 페이지로
        if comp_uid is None:
            return redirect('/')
        
        # 데이터 입력 : 비즈니스 로직 실행
        recruit_cont = RecruitCont(comp_uid)
        context = recruit_cont.get_recruit_info()
        
        return render(request, 'recruit/recruit.html', context)
    
    except Exception as e:
        print(e)
        return redirect('/')
