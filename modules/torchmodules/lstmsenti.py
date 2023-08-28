import pandas as pd
import torch
from lstmmodel import LSTMModel

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

class LSTMSenti:
    def __init__(self):
        self.__model = LSTMModel()
        pass

    def get_sentiment(self, text):
        return 'POSITIVE'