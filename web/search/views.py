from django.shortcuts import render, redirect

from .models import CompInfo, CompNews

# 일반 메인 페이지 접근
def main_page(request):
    if request.method == 'GET':
        context = {
            'msg': ''
        }
        
        # form에서 넘어온건지 체크
        comp_name_list = [el.comp_name for el in CompInfo.objects.all()] # 전체 회사 이름 리스트
        comp_name = request.GET.get('q', None)
        
        # 파라미터가 있는 경우
        if comp_name:
            try:
                # 검색어 보정
                comp_name = [el for el in comp_name_list if el.find(comp_name) > -1][0]
                
                # comp_uid로 변환시키기
                comp_uid = CompInfo.objects.filter(comp_name=comp_name)[0].comp_uid
                
                # 기업정보 페이지로 이동
                return redirect(f'comp/?comp_uid={comp_uid}')
            
            except Exception as e:
                # 다시 검색 화면으로, 메세지 출력
                print(e)
                context['msg'] = f'{comp_name}는(은) 아직 등록되지 않은 기업명입니다.'
                
                
        # 일반 접근 : 파라미터가 없는 경우
        return render(request, 'main.html', context)
