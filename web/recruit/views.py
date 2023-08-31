from django.shortcuts import render, redirect

from .models import RecruitInfo, CompInfo

def recruit_page(request):
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    elif request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
        
    # 아무것도 안넘어왔다면 메인페이지로 redirect
    if comp_uid is None:
        redirect('/')
    
    # 파라미터 넘어옴 : 회사 정보 불러오기
    comp_name = CompInfo.objects.get(comp_uid=comp_uid).comp_name
    
    # html에 넘겨줄 데이터들
    context = {
        'active': 'recruit',
        'comp_uid': comp_uid,
        'comp_name': comp_name,
        'recruit_infos': [ ],
    }
    
    # 채용공고 불러오기
    recruit_infos = RecruitInfo.objects.filter(comp_uid=comp_uid)
    
    # 공고가 없는 경우
    if len(recruit_infos) == 0:
        context['msg'] = '채용공고 정보가 없습니다.'
    
    else:
        # context에 넣어주기
        for info in recruit_infos:
            data = {
                'uid': info.recruit_uid,
                'url': info.recruit_url,
                'thumb': info.recruit_thumb,
                'position': info.recruit_position,
                'desc': info.recruit_desc,
            }
            context['recruit_infos'].append(data)
    
    return render(request, 'recruit/recruit.html', context)
