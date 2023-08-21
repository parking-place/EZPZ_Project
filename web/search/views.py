from django.shortcuts import render, redirect

from .models import CompInfo

# 일반 메인 페이지 접근
def main_page(request):
    if request.method == 'GET':
        context = {
            'msg': ''
        }
        
        # form에서 넘어온건지 체크
        comp_name = request.GET.get('q', None)
        
        # 파라미터가 있는 경우
        if comp_name:
            try:
                # comp_uid로 변환시키기
                comp_uid = CompInfo.objects.get(comp_name__contains=comp_name).comp_uid
                
                # 기업정보 페이지로 이동
                return redirect(f'comp/?comp_uid={comp_uid}')
            
            except Exception as e:
                # 다시 검색 화면으로, 메세지 출력
                print(e)
                context['msg'] = f'{comp_name}는(은) 아직 등록되지 않은 기업명입니다.'
                
                
        # 일반 접근 : 파라미터가 없는 경우
        return render(request, 'main.html', context)
