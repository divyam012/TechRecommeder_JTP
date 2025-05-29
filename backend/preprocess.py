import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

def preprocess_laptop_data(file_path):
    df = pd.read_csv(file_path)

    df['OS'] = df['OS'].str.lower()
    df['processor_brand'] = df['processor_brand'].str.lower()
    df['gpu_brand'] = df['gpu_brand'].str.lower()

    os_encoder = LabelEncoder()
    df['os_encoded'] = os_encoder.fit_transform(df['OS'])

    numeric_cols = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(df[numeric_cols])

    return df, features_scaled, scaler
