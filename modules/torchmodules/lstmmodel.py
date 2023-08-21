import torch
from torch import nn

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

DICT_PATH = '/home/parking/ml/data/MiniProj/models'

class LSTMModel(nn.Module):
    pass