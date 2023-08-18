from django.shortcuts import render

def recruit_page(request):
    context = {
        'active': 'recruit',
        'comp_uid': '198102398',
        'comp_name': '포자랩스',
        'recruit_infos': [
            {
                'uid' : '150743',
                'url': 'https://www.wanted.co.kr/wd/150743',
                'thumb': r'https://image.wanted.co.kr/optimize?src=https%3A%2F%2Fstatic.wanted.co.kr%2Fimages%2Fcompany%2F9205%2Fxd05bjd3o7vbf1h4__1080_790.jpg&w=400&q=75',
                'position': 'MLOps 엔지니어',
                'content': '음악은 많은 곳에서 기능을 합니다. 비디오 컨텐츠에 힘을 싣고, 공간의 분위기를 바꿉니다. 사람들은 많은 종류의 컨텐츠에 내 의도를 더 강하게 표현하기 위해 음악에 신경을 씁니다.\n하지만 음악을 찾고, 사용하는 일은 꽤나 어렵습니다. 엄청난 시간을 들이거나, 많은 돈을 내거나 혹은 포기해 버리기도 합니다. 이에 따라 세계적으로 많은 인공지능 작곡 업체가 생겨나고 있지만 사람이 만든 것 이하의 퀄리티로 인하여 아직 시장을 선점하고 있는 업체는 없습니다.'[:200]
            }
        ],
    }
    
    return render(request, 'recruit/recruit.html', context)