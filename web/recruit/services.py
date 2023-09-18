# recruit/services.py
# 기업 채용 공고에 대한 비즈니스 로직을 작성합니다.
from .models import CompInfo, RecruitInfo

class RecruitCont(object):
    
    def __init__(self, comp_uid) -> None:
        self.comp_uid = comp_uid
        comp_name = CompInfo.objects.get(comp_uid=comp_uid).comp_name
        
        self.context = {
        'active': 'recruit',
        'comp_uid': comp_uid,
        'comp_name': comp_name,
        'recruit_infos': [ ],
        }
    
    def get_recruit_info(self) -> dict:
        # 채용공고 불러오기
        recruit_infos = RecruitInfo.objects.filter(comp_uid=self.comp_uid)
        
        # 채용공고가 없는 경우
        if len(recruit_infos) == 0:
            self.context['msg'] = '채용공고 정보가 없습니다.'
        
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
                self.context['recruit_infos'].append(data)
                
        return self.context