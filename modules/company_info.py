from service_models import ServiceModels
import pandas as pd

DATA_PATH = '/home/parking/ml/data/MiniProj/data/'

class CompanyInfo:
    def __init__(self):
        self.__service_models = ServiceModels()
    
    def get_company_info(self, company_name):
        pass
    
    def get_news_df(self, company_name):
        daum_news_df = pd.read_csv(f'{DATA_PATH}/news/{company_name}_daum.csv')
        naver_news_df = pd.read_csv(f'{DATA_PATH}/news/{company_name}_naver.csv')
        
        news_df = pd.concat([daum_news_df, naver_news_df])
        
        news_df['summarized'] = news_df['content'].apply(self.__service_models.news_sum)
        news_df['sentiment'] = news_df['content'].apply(self.__service_models.news_sentiment)
        
        return news_df
    
    def get_reviews_df(self, company_name):
        sites = ['jobplanet', 'catch'] # ['saramin', 'jobplanet', 'catch']
        reviews = []
        
        