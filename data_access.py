import pandas as pd
import os

FILE_PATH = "studentdata.xlsx"

def read_data():
    if not os.path.exists(FILE_PATH):
        return pd.DataFrame()
    return pd.read_excel(FILE_PATH)

def save_data(df):
    df.to_excel(FILE_PATH, index=False)