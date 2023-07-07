from finbertkr import FinBertKR
from mt5sum import MT5Sum

class ServiceModels:
    def __init__(self):
        self.__news_sum = MT5Sum()
        self.__news_sentiment = FinBertKR()
        
    def get_summary(self, text, type='news'):
        return self.__news_sum.get_sum(text, type=type)
    
    def get_sentiment(self, text):
        return self.__news_sentiment.get_sentiment(text)