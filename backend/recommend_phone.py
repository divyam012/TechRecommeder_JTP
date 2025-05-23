import numpy as np

# Define weights for each usage type
USAGE_PROFILES = {
    "gaming": {
        "RAM": 3.5,
        "Storage": 3.0,
        "Battery": 3.0,
        "Rear_cam_mp": 1.0,
        "Front_cam_mp": 1.0,
        "5g": 1.5
    },
    "camera": {
        "Rear_cam_mp": 3.5,
        "Front_cam_mp": 2.5,
        "Num_rear_cam": 2.0,
        "RAM": 1.5,
        "Storage": 1.5,
        "Battery": 1.0
    },
    "business": {
        "Battery": 2.5,
        "RAM": 3.0,
        "Storage": 3.0,
        "5g": 2.0
    },
    "basic": {
        "Battery": 2.0,
        "Price": -3.0,  # Lower price is better
        "RAM": 2.0,
        "Storage": 2.0,
        "5g": 1.0
    }
}


def get_phone_recommendations_by_usage(df, scaler, usage_type, budget):
    if usage_type not in USAGE_PROFILES:
        raise ValueError("Invalid usage type. Choose from gaming, camera, business, or basic.")

    df_filtered = df[df['Price'] <= budget].copy()

    if df_filtered.empty:
        print("No phones found within your budget range.")
        return df.head(5)

    # Define features used
    features = ['Price', '5g', 'RAM', 'Storage', 'Battery',
                'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']

    # Normalize numeric features
    df_normalized = df_filtered.copy()
    df_normalized[features] = scaler.transform(df_filtered[features])

    # Apply weights based on usage
    weights = USAGE_PROFILES[usage_type]
    scores = []

    for idx, row in df_normalized.iterrows():
        score = 0
        for feature, weight in weights.items():
            value = row[feature]
            score += weight * value
        scores.append(score)

    df_filtered['Score'] = scores
    df_sorted = df_filtered.sort_values(by='Score', ascending=False)

    return df_sorted.head(5)
