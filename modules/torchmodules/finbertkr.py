import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import torch

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/app/data/MiniProj/models'

class FinBertKR:
    def __init__(self):
        model_name = "snunlp/KR-FinBert-SC"
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.__model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.__model.to(DEVICE)
        self.__softmax = F.softmax
        
    def load_dict(self, model_name):
        self.__model.load_state_dict(torch.load(f'{DICT_PATH}/{model_name}'))

    def get_sentiment(self, text):
        inputs = self.__tokenizer(text, return_tensors='pt').to(DEVICE)
        outputs = self.__model(**inputs)
        probs = self.__softmax(outputs.logits, dim=1)
        pred = self.__model.config.id2label[probs.argmax().item()]
        return pred