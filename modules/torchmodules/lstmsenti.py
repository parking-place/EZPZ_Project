import pandas as pd
import torch
import lstmmodel

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

class LSTMSenti:
    def __init__(self):
        self.__model = lstmmodel.LSTMModel()
        pass
    
    def get_sentiment(self, text):
        return 'POSITIVE'