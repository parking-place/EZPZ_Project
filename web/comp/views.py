from django.shortcuts import render, redirect

from .models import CompInfo, CompNews



def comp(request):
    # 파라미터 처리
    if request.method == 'GET':
        comp_uid = request.GET.get('comp_uid', None)
    if request.method == 'POST':
        comp_uid = request.POST.get('comp_uid', None)
    
    # 파라미터 제대로 안 넘어온 경우 메인 페이지로
    if comp_uid is None:
        return redirect('/')
    
    
    # 기업 정보 불러오기
    info = CompInfo.objects.get(comp_uid=comp_uid)
    context = {
        'active': 'comp',
        'comp_uid': comp_uid,
        'comp_info': {
            'name': info.comp_name,
            'found': f'{info.comp_founded[:4]}.{info.comp_founded[4:]}',
            'loc': info.comp_loc,
            'size': info.comp_size,
            'thumb': info.comp_thumb,
            'url': info.comp_url,
            'cont': info.comp_cont,
        },
        'news': [ ]
    }
    
    # 뉴스 정보 넣어주기
    newses = CompNews.objects.filter(comp_uid=comp_uid)
    for news in newses:
        if news.news_sum: # 데이터가 있을때만 넣기
            data = {
                'sum': news.news_sum,
                'senti': news.news_senti,
                'color': '#87ceeb' if news.news_senti == 1 else '#d3d3d3' if news.news_senti == 0 else '#ffc0cb',
            }
        context['news'].append(data)
        
    # 뉴스 정보가 있다면 비율 정보 넣어주기
    if newses is not None and len(newses) >= 1:
        context['pos_ratio'] = len([el for el in context['news'] if el['senti'] == 1]) / len(newses) * 100
        context['neg_ratio'] = len([el for el in context['news'] if el['senti'] == 2]) / len(newses) * 100
        context['neu_ratio'] = len([el for el in context['news'] if el['senti'] == 0]) / len(newses) * 100
    
    return render(request, 'comp/comp.html', context)