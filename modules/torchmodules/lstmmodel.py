import torch
from torch import nn

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

######################
# 레이어 클래스 정의
######################
# 임베딩 레이어 클래스 정의
class EmbeddingLayer(nn.Module):
    def __init__(self, n_class, embedding_size=128):
        super().__init__()
        #n_class는 VOCAB의 개수임 임베딩레이어에서의 아웃풋사이즈가 임베딩사이즈 입력데이터를 고정된 차원(여기서는 128)의 벡터로 표현
        self.emb_layer = nn.Embedding(n_class,    # n_class
                                    embedding_size, # output_size = embedding_size
                                    )

    def forward(self, X):
        return self.emb_layer(X)
# LSTM 레이어 클래스 정의
class LSTMLayer(nn.Module):
    def __init__(self, embedding_size=128, hidden_size=128, num_layers=3, is_bidirectional=True):
        #임베딩사이즈는 위에 설명한대로고 히든사이즈는 LSTM등의 순차적 모델에서 입력 시퀸스를 처리하고 중간상태를 생성하는데 사용하는 노드수
        super().__init__()
        # 변수 저장
        self.shape_size = (2 if is_bidirectional else 1) * num_layers
        self.hidden_size = hidden_size

        self.lstm_layer = nn.LSTM(input_size=embedding_size, # input_size = embedding_size
                                hidden_size=hidden_size,    # 은닉층의 갯수
                                num_layers=num_layers,      # 은닉층 각각의 레이어 갯수
                                bidirectional=is_bidirectional,  # 양방향 LSTM 여부
                                )

    def forward(self, X):
        # 축교환
        _X = X.transpose(0, 1)
        # hidden_state의 마지막 값만 반환 (순차적으로 히든 스테이트에서 마지막 값이 output이고 그 과정은 중간저장 cell 이니까)
        output_raw = self.__get_hidden_state(_X, len(X)) #여기서 마지막 히든스테이트만 가져옴
        return output_raw

    def __get_hidden_state(self, X, lenght):
        # hidden_state와 cell_state의 shape 정의
        shape = (self.shape_size, lenght, self.hidden_size)
        # hidden_state와 cell_state를 초기화
        hidden_state = torch.zeros(shape).to(X.device)
        cell_state = torch.zeros(shape).to(X.device)
        # LSTM 레이어를 통해 output과 hidden_state, cell_state를 반환
        _, (hidden_state, __) = self.lstm_layer(X, (hidden_state, cell_state))
        return hidden_state[-1]
# 이진 출력 레이어 클래스 정의
class BinaryOutputLayer(nn.Module):
    def __init__(self, input_size=128):
        super().__init__()
        self.output_layer = nn.Sequential(
            # 데이터의 양을 반으로 줄임
            nn.Linear(input_size, input_size//2, bias=False),
            # 활성화 함수
            nn.ReLU(),
            # 출력 데이터의 양을 1로 줄임
            nn.Linear(input_size//2, 1, bias=False),
            # 이진분류 이므로 시그모이드 함수를 통해 0~1사이의 값으로 변환
            nn.Sigmoid(),
            )

    def forward(self, X):
        return self.output_layer(X)

######################
# 모델 정의
######################
class LSTMModel(nn.Module):
    def __init__(self, n_class, embedding_size=128, hidden_size=128, num_layers=3, is_bidirectional=True):
        super().__init__()
        self.seq = nn.Sequential(
            # 임베딩 레이어
            EmbeddingLayer(n_class=n_class,
                        embedding_size=embedding_size,
                        ),
            # LSTM 레이어
            LSTMLayer(embedding_size=embedding_size,
                        hidden_size=hidden_size,
                        num_layers=num_layers,
                        is_bidirectional=is_bidirectional,
                        ),
            # 이진 아웃풋 레이어
            BinaryOutputLayer(
                        input_size=hidden_size
                        ),
        )

    def forward(self, X):
        return self.seq(X)

