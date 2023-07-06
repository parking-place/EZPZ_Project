import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import torch
import re


DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

class FinBertKR:
    def __init__(self):
        model_name = "snunlp/KR-FinBert-SC"
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.__model = AutoModelForSequenceClassification.from_pretrained(model_name)
        