import numpy as np

# Usage profiles for different laptop use cases
USAGE_PROFILES = {
    "gaming": {
        "RAM": 3.0,
        "Storage": 2.5,
        "gpu_brand_score": 3.0,
        "num_cores": 2.5,
        "num_threads": 2.5
    },
    "business": {
        "RAM": 2.0,
        "Storage": 2.0,
        "num_cores": 2.0,
        "display_size": 2.0
    },
    "basic": {
        "Price": -1.0,
        "RAM": 2.0,
        "Storage": 2.0,
        "display_size": 1.5
    },
    "student": {
        "RAM": 2.5,
        "Storage": 2.5,
        "Price": -0.8,
        "num_cores": 2.0
    }
}

def get_laptop_recommendations_by_usage(df, df_scaled, scaler, usage_type, budget):
    if usage_type not in USAGE_PROFILES:
        raise ValueError("Invalid usage type. Choose from gaming, business, basic, or student.")

    # Filter laptops within budget
    df_filtered = df[df['Price'] <= budget].copy()
    if df_filtered.empty:
        print("No laptops found within your budget.")
        return df.head(5)

    features = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
    df_normalized = df_filtered.copy()
    df_normalized[features] = scaler.transform(df_filtered[features])

    weights = USAGE_PROFILES[usage_type]
    scores = []
    for idx, row in df_normalized.iterrows():
        score = 0
        for feature, weight in weights.items():
            if feature == "gpu_brand_score":
                gpu = df_filtered.loc[idx, "gpu_brand"].lower()
                # Assign a score based on GPU brand
                score += weight * {
                    "nvidia": 1.0,
                    "amd": 0.7,
                    "intel": 0.5
                }.get(gpu, 0.3)
            else:
                score += weight * row[feature]
        # Apple bonus for business use case
        if usage_type == "business" and df_filtered.loc[idx, "Brand"].strip().lower() == "apple":
            score *= 5.0  # Tunable bonus for Apple in business
        scores.append(score)

    df_filtered['Score'] = scores
    df_sorted = df_filtered.sort_values(by='Score', ascending=False)
    return df_sorted.head(5)
