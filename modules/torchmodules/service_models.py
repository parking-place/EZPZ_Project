from finbertkr import FinBertKR
from mt5sum import MT5Sum
from t5basesum import T5BaseSum
from lstmsenti import LSTMSenti
class ServiceModels:
    def __init__(self):
        self.__news_sum = MT5Sum()
        self.__news_sentiment = FinBertKR()
        self.__reviews_sum = T5BaseSum()
        self.__reviews_sentiment = LSTMSenti()
        
    def get_summary(self, text, type='news'):
        if type == 'news':
            return self.__news_sum.get_sum(text, type=type)
        elif type == 'reviews_long':
            return self.__reviews_sum.get_sum(text)
        elif type == 'reviews_short':
            return self.__news_sum.get_sum(text, type=type)
    
    def get_long_summary(self, text):
        return self.__reviews_sum.get_sum(text)
    
    def get_sentiment(self, text):
        return self.__news_sentiment.get_sentiment(text)
    
    def get_reviews_sentiment(self, text):
        return self.__reviews_sentiment.get_sentiment(text)