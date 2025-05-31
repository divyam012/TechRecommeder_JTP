import pickle
from preprocess_phone import preprocess_phone_data

# Step 1: Preprocess the data
features_scaled, df, scaler, os_encoder = preprocess_phone_data("data/phones.csv")

# Step 2: Dump all components
with open("models/phone_components.pkl", "wb") as f:
    pickle.dump({
        "df": df,
        "features_scaled": features_scaled,
        "scaler": scaler,
        "os_encoder": os_encoder
    }, f)

print("Phone preprocessing components dumped successfully.")
