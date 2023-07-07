from finbertkr import FinBertKR
from mt5sum import MT5Sum

class ServiceModels:
    def __init__(self):
        self.__news_sum = MT5Sum()
        self.__news_sentiment = FinBertKR()
        
    def news_sum(self, text):
        return self.__news_sum.get_sum(text)
    
    def news_sentiment(self, text):
        return self.__news_sentiment.get_sentiment(text)