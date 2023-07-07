import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
SEPTOKEN_DELETER = lambda x: x.replace('<extra_id_70>', '').strip()

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

class MT5Sum:
    def __init__(self, target_lang='korean'):
        self.__model_name = "csebuetnlp/mT5_m2m_crossSum_enhanced"
        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_name, use_fast=False)
        self.__model = AutoModelForSeq2SeqLM.from_pretrained(self.__model_name)
        
        self.__get_lang_id = lambda lang: self.__tokenizer._convert_token_to_id(
            self.__model.config.task_specific_params["langid_map"][lang][1]
        ) 
    
        self.__target_lang = target_lang
        
    def load_dict(self, model_name):
        self.__model.load_state_dict(torch.load(f'{DICT_PATH}/{model_name}'))
        
    def get_sum(self, text, result_max_length=84, no_repeat_ngram_size=1, num_beams=4):
        clean_text = WHITESPACE_HANDLER(text)
        
        max_len = len(clean_text.split())
        
        input_ids = self.__tokenizer(
            [clean_text],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=max_len,
        )["input_ids"]
        
        model = self.__model.to(DEVICE)
        model.eval()
        
        input_ids = input_ids.to(DEVICE)
        
        output_ids = model.generate(
            input_ids=input_ids,
            decoder_start_token_id=self.__get_lang_id(self.__target_lang),
            max_length=result_max_length,
            no_repeat_ngram_size=no_repeat_ngram_size,
            num_beams=num_beams,
        )[0]
        
        summarized_text = self.__tokenizer.decode(output_ids, skip_special_tokens=True)
        
        summarized_text = SEPTOKEN_DELETER(summarized_text)
        
        return summarized_text