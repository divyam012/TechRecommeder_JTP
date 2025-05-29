import pandas as pd
from preprocess import preprocess_laptop_data
from recommend import get_laptop_recommendations_by_usage
from preprocess_phone import preprocess_phone_data
from recommend_phone import get_phone_recommendations_by_usage


def run_laptop_flow():
    # Load and preprocess laptop data
    df, df_scaled, scaler = preprocess_laptop_data("data/laptops.csv")
    print("Please enter the following details for laptop recommendation:\n")
    budget = int(input("Enter your maximum budget (in INR): "))
    usage_type = input("What will you mainly use the laptop for? (gaming/business/basic/student): ").strip().lower()
    recommended = get_laptop_recommendations_by_usage(df, df_scaled, scaler, usage_type, budget)
    print("\nTop 5 Recommended Laptops:")
    print(recommended[['Brand', 'Model', 'Price']])


def run_phone_flow():
    # Load and preprocess phone data
    _, original_df, scaler, os_encoder = preprocess_phone_data("data/phones.csv")
    print("Please enter the following details for phone recommendation:\n")
    budget = int(input("Enter your maximum budget (in INR): "))
    usage_type = input("What will you mainly use the phone for? (gaming/camera/business/basic): ").strip().lower()
    recommended = get_phone_recommendations_by_usage(original_df, scaler, usage_type, budget)
    print("\nTop 5 Recommended Phones:")
    print(recommended[['Brand', 'Model', 'Price']])


if __name__ == "__main__":
    device_type = input("What do you want recommendations for? (laptop/phone): ").strip().lower()
    if device_type == "laptop":
        run_laptop_flow()
    elif device_type == "phone":
        run_phone_flow()
    else:
        print("Invalid input. Please enter 'laptop' or 'phone'.")
