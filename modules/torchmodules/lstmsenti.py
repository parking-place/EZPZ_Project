import pandas as pd
import torch
import pickle
from lstmmodel import LSTMModel
from kiwipiepy import Kiwi 
from torchtext.vocab import Vocab
import re

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

MODEL_PATH = '/app/data/models/lstm/comp_review_model_select_final_last_0.9915.pth'
VOCAB_DICT_PATH = '/app/data/models/lstm/voab_442290_final2.pkl'

class LSTMSenti:
    def __init__(self):
        
        
        
        
        
        self.__kiwi = Kiwi()
        
        vacab_dict = pickle.load(open(VOCAB_DICT_PATH, 'rb'))
        self.__vocab = Vocab(vacab_dict)
        self.__vocab.set_default_index(self.__vocab['<unk>'])
        
        # 단어(클래스) 갯수
        N_CLASS = len(self.__vocab)
        # 임베딩 차원 수 (임베딩된 단어의 벡터 차원 수)
        EMBEDDING_SIZE = 128
        # LSTM 레이어 은닉층의 차원 수
        HIDDEN_SIZE = 10
        # LSTM 레이어 은닉층 각각의 레이어 갯수
        NUM_LAYERS = 3
        # LSTM 레이어 양방향 여부
        IS_BIDIRECTIONAL = True
        
        self.__threshold = 0.5
        
        self.__model = LSTMModel(
            n_class=N_CLASS,
            embedding_size=EMBEDDING_SIZE,
            hidden_size=HIDDEN_SIZE,
            num_layers=NUM_LAYERS,
            is_bidirectional=IS_BIDIRECTIONAL
        )
        self.__model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.__model.eval()
        self.__model.to(DEVICE)
        
        pass
    
    def __pretreatment_and_tokenizer(self, text):
        # pattern = r'[^a-z가-힣\s\.]' # 알파벳, 한글, 공백, 마침표만 남기고 삭제
        # 숫자, 알파벳, 한글, 공백, 마침표, 쉼표만 남기고 삭제
        pattern = r'[^0-9a-zA-Z가-힣\s\.\,]'
        text = re.sub(pattern=pattern, repl='', string=text)
        text = text.strip()
        
        doc = self.__kiwi.tokenize(text)
        return [token.form for token in doc]
    
    def __text_to_tensor(self, text):
        text = self.__pretreatment_and_tokenizer(text)
        if len(text) == 0:
            return None
        text = [self.__vocab[token] for token in text]
        text = torch.tensor(text).unsqueeze(0).to(DEVICE)
        return text
    
    def get_sentiment(self, text):
        text = self.__text_to_tensor(text)
        if text is None:
            return 'N'
        
        output = self.__model(text)
        # 이미 sigmoid를 거쳤기 때문에 sigmoid를 거치지 않음
        # output = torch.sigmoid(output)
        
        if output.item() > self.__threshold:
            return 'P'
        else:
            return 'N'