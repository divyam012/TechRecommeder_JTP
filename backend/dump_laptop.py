import pickle
from preprocess import preprocess_laptop_data

# Step 1: Preprocess the data
df, df_scaled, scaler = preprocess_laptop_data("./data/laptops.csv")

# Step 2: Dump these into a pickle file
with open("laptop_components.pkl", "wb") as f:
    pickle.dump({
        "df": df,
        "df_scaled": df_scaled,
        "scaler": scaler
    }, f)

print("Laptop preprocessing components dumped successfully.")
