import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df

def preprocess(df):
    # Expect a column 'is_fraud' target; simple feature handling for demo
    df = df.copy()
    if 'is_fraud' not in df.columns:
        raise ValueError("Dataset must contain 'is_fraud' column")
    X = df.drop(columns=['is_fraud'])
    y = df['is_fraud']
    # Simple fillna + numeric conversion
    X = X.select_dtypes(include=['number']).fillna(0)
    return X, y
