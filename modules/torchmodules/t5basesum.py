import nltk
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

class T5BaseSum:
    def __init__(self):
        nltk.download('punkt')
        
        self.__model_name = 'eenzeenee/t5-small-korean-summarization'
        
        self.__model = AutoModelForSeq2SeqLM.from_pretrained(self.__model_name).to(DEVICE)
        self.__model.eval()
        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_name)
        
        self.__prefix = "summarize: "
        
        self.__preprocess = lambda x: re.sub('\s+', ' ', re.sub('\n+', ' ', x.strip()))
    
    def get_sum(self, text):
        clean_text = self.__preprocess(text)
        
        inputs = [self.__prefix + clean_text]
        inputs_ids = self.__tokenizer(inputs, max_length=1024, truncation=True, return_tensors="pt").to(DEVICE)
        output = self.__model.generate(**inputs_ids, num_beams=3, do_sample=True, min_length=128, max_length=256)
        decoded_output = self.__tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        result = nltk.sent_tokenize(decoded_output.strip())[0]
        
        return result