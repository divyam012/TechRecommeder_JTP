import numpy as np

USAGE_PROFILES = {
    "gaming": {
        "RAM": 3.0,
        "Storage": 2.5,
        "gpu_brand_score": 3.0,
        "num_cores": 2.5,
        "num_threads": 2.5
    },
    "business": {
        "RAM": 3.0,
        "Storage": 2.5,
        "num_cores": 2.5,
        "display_size": 2.0
    },
    "basic": {
        "Price": -2.5,
        "RAM": 2.0,
        "Storage": 2.0,
        "display_size": 1.5
    },
    "student": {
        "RAM": 2.5,
        "Storage": 2.5,
        "Price": -2.0,
        "num_cores": 2.0
    }
}

def get_laptop_recommendations_by_usage(df, df_scaled, scaler, usage_type, budget):
    if usage_type not in USAGE_PROFILES:
        raise ValueError("Invalid usage type. Choose from gaming, business, basic, or student.")

    df_filtered = df[df['Price'] <= budget].copy()
    if df_filtered.empty:
        print("No laptops found within your budget.")
        return df.head(5)

    features = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
    df_normalized = df_filtered.copy()
    df_normalized[features] = scaler.transform(df_filtered[features])

    scores = []
    weights = USAGE_PROFILES[usage_type]

    for idx, row in df_normalized.iterrows():
        score = 0
        for feature, weight in weights.items():
            if feature == "gpu_brand_score":
                gpu = df_filtered.loc[idx, "gpu_brand"].lower()
                if gpu == "nvidia":
                    score += weight * 1.0
                elif gpu == "amd":
                    score += weight * 0.7
                elif gpu == "intel":
                    score += weight * 0.5
                else:
                    score += weight * 0.3
            else:
                score += weight * row[feature]
        scores.append(score)

    df_filtered['Score'] = scores
    df_sorted = df_filtered.sort_values(by='Score', ascending=False)
    return df_sorted.head(5)
