import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import torch
from peft import get_peft_model, LoraConfig, TaskType, get_peft_model_state_dict, get_peft_config
from peft import PeftModel, PeftConfig

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = r'/app/data/models'
DATA_PATH = r'/app/data/datas'
ORIG_MODEL_NAME = 'snunlp/KR-FinBert-SC'
MODEL_NAME = 'lora_model_last_ephoc_last'

class FinBertKR:
    def __init__(self):
        peft_config = LoraConfig(
            task_type=TaskType.SEQ_CLS,
            inference_mode=False,
            r=8,
            lora_alpha=32,
            lora_dropout=0.1,
        )

        peft_model_id = f"{DICT_PATH}/{MODEL_NAME}_{peft_config.peft_type}_{peft_config.task_type}"

        model_name_or_path = DICT_PATH+'/'+MODEL_NAME

        self.__tokenizer = AutoTokenizer.from_pretrained(ORIG_MODEL_NAME)
        self.__config = PeftConfig.from_pretrained(model_name_or_path)
        self.__model = AutoModelForSequenceClassification.from_pretrained(self.__config.base_model_name_or_path)
        self.__model = PeftModel.from_pretrained(self.__model, model_name_or_path).to(DEVICE)
        self.__softmax = F.softmax
        
        self.__NUM2LABEL = {2: 'positive', 1: 'neutral', 0: 'negative'}
        self.__LABEL2NUM = {'positive': 2, 'neutral': 1, 'negative': 0}

    def get_sentiment(self, text):
        inputs = self.__tokenizer(text, return_tensors='pt')
        outputs = self.__model(
            input_ids=inputs['input_ids'].to(DEVICE),
            attention_mask=inputs['attention_mask'].to(DEVICE),
            token_type_ids=inputs['token_type_ids'].to(DEVICE),
        )
        probs = self.__softmax(outputs.logits, dim=1)
        pred = self.__NUM2LABEL[probs.argmax().item()]
        return pred
    
##############################################################################################################
# 테스트 코드
##############################################################################################################
if __name__ == '__main__':
    finbertkr = FinBertKR()
    news = '삼성전자의 주가가 1% 상승했다.'
    print(news)
    print(finbertkr.get_sentiment(news))