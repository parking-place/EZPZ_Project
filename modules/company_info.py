import pandas as pd
import sys
sys.path.append(r'/home/parking/ml/MiniProj/modules/')
sys.path.append(r'/home/parking/ml/MiniProj/modules/torchmodules/')

from torchmodules.service_models import ServiceModels

DATA_PATH = '/home/parking/ml/data/MiniProj/data/'

class CompanyInfo:
    def __init__(self):
        self.__service_models = ServiceModels()
    
    def get_company_info(self, company_name):
        news_df = self.__get_news_df(company_name)
        reviews_df = self.__get_reviews_df(company_name)
        
        news_df = self.__get_news_summarized_and_sentiment(news_df)
        reviews_df, review_summarized_dict = self.__get_reviews_summarized(reviews_df)
        
        return news_df, reviews_df, review_summarized_dict
        # return news_df, reviews_df
    
    def __get_news_df(self, company_name):
        daum_news_df = pd.read_csv(f'{DATA_PATH}/news/{company_name}_daum.csv')
        naver_news_df = pd.read_csv(f'{DATA_PATH}/news/{company_name}_naver.csv')
        
        news_df = pd.concat([daum_news_df, naver_news_df])
        
        return news_df
    
    def __get_news_summarized_and_sentiment(self, news_df):
        news_df['summarized'] = news_df['content'].apply(self.__service_models.get_summary)
        news_df['sentiment'] = news_df['summarized'].apply(self.__service_models.get_sentiment)
        return news_df
    
    def __get_reviews_df(self, company_name):
        sites = ['jobplanet', 'catch'] # ['saramin', 'jobplanet', 'catch']
        reviews = []
        
        col_naes = ['good', 'bad']
        
        for site in sites:
            reviews_df = pd.read_csv(f'{DATA_PATH}/reviews/{site}/{company_name}_reviews.csv')
            reviews_df.columns = col_naes
            reviews.append(reviews_df)
        
        reviews_df = pd.concat(reviews)
        
        return reviews_df
    
    def __get_reviews_summarized(self, reviews_df):
        
        good_reviews = ''
        bad_reviews = ''
        
        for good_review, bad_review in zip(reviews_df['good'], reviews_df['bad']):
            good_reviews += good_review + '. '
            bad_reviews += bad_review + '. '
        
        good_summarise_long = self.__service_models.get_summary(good_reviews, type='reviews_long')
        bad_summarise_long = self.__service_models.get_summary(bad_reviews, type='reviews_long')
        
        good_summarise_short = self.__service_models.get_summary(good_reviews, type='reviews_short')
        bad_summarise_short = self.__service_models.get_summary(bad_reviews, type='reviews_short')
        
        review_summarized_dict = {
            'good_summarise_long': good_summarise_long,
            'bad_summarise_long': bad_summarise_long,
            'good_summarise_short': good_summarise_short,
            'bad_summarise_short': bad_summarise_short
        }
        
        return reviews_df, review_summarized_dict