import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from torchinfo import summary

WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))