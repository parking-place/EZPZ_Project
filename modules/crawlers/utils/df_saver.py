import pandas as pd

PATH = r'E:\Python\data\MiniProj\datas\reviews'

def set_path(path):
    global PATH
    PATH = path
    return

def save_df(df):
    df.to_csv(PATH, index=False)
    return