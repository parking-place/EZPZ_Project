from django.shortcuts import render
from django.db.models import Q

from .models import RecruitInfo, CompInfo

def recruit_page(request):
    # 파라미터 처리
    comp_uid = ''
    
    if request.method == 'GET':
        comp_uid = request.GET['comp_uid']
    elif request.method == 'POST':
        comp_uid = request.POST['comp_uid']
    
    # 데이터 로드
    # test_db에 입력된 comp_uid:
    #   1, 2, 3
    
    # 회사 정보 불러오기
    comp_name = CompInfo.objects.filter(
        Q(comp_uid=comp_uid)
    )[0].comp_name
    
    # html에 넘겨줄 데이터들
    context = {
        'active': 'recruit',
        'comp_uid': comp_uid,
        'comp_name': comp_name,
        'recruit_infos': [ ],
    }
    
    # 채용공고 불러오기
    recruit_infos = RecruitInfo.objects.filter(
        Q(comp_uid=comp_uid)
    )
    
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
