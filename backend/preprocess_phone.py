import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler


def preprocess_phone_data(file_path):
    df = pd.read_csv(file_path)
    # Ensure 5g is binary and OS is lowercase
    df['5g'] = df['5g'].astype(bool).astype(int)
    df['OS'] = df['OS'].str.lower()
    # Encode OS for ML use
    os_encoder = LabelEncoder()
    df['OS Encoded'] = os_encoder.fit_transform(df['OS'])
    # Select features and normalize
    features = df[['Price', '5g', 'RAM', 'Storage', 'Battery',
                   'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']]
    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    return features_scaled, df, scaler, os_encoder
