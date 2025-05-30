import os
import pickle
import pandas as pd
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
from gsmarena_lookup import get_gsmarena_info  # For future use
import time

app = FastAPI()

# Allow CORS for all origins (for dev; restrict in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


base_dir = os.path.dirname(__file__)

# Load preprocessed data and scalers
with open(os.path.join(base_dir, "laptop_components.pkl"), "rb") as f:
    laptop_objects = pickle.load(f)
laptop_scaler = laptop_objects["scaler"]
laptop_df = laptop_objects["df"]

with open(os.path.join(base_dir, "phone_components.pkl"), "rb") as f:
    phone_objects = pickle.load(f)
phone_scaler = phone_objects["scaler"]
phone_df = phone_objects["df"]

# Usage profiles for scoring
LAPTOP_USAGE_PROFILES = {
    "gaming": {"RAM": 3.0, "Storage": 2.5, "gpu_brand_score": 3.0, "num_cores": 2.5, "num_threads": 2.5},
    "business": {"RAM": 3.0, "Storage": 2.5, "num_cores": 2.5, "display_size": 2.0},
    "basic": { "RAM": 2.0, "Storage": 2.0, "display_size": 1.5},
    "student": {"RAM": 2.5, "Storage": 2.5, "num_cores": 2.0}
}

PHONE_USAGE_PROFILES = {
    "gaming": {"RAM": 3.5, "Storage": 3.0, "Battery": 3.0, "Rear_cam_mp": 1.0, "Front_cam_mp": 1.0, "5g": 1.5},
    "camera": {"Rear_cam_mp": 3.5, "Front_cam_mp": 2.5, "Num_rear_cam": 2.0, "RAM": 1.5, "Storage": 1.5, "Battery": 1.0},
    "business": {"Battery": 2.5, "RAM": 3.0, "Storage": 3.0, "5g": 2.0},
    "basic": {"Battery": 2.0, "RAM": 2.0, "Storage": 2.0, "5g": 1.0}
}

@app.post("/recommend")
async def recommend_form(
    request: Request,
    device_type: str = Form(...),
    budget: float = Form(...),
    usage_type: str = Form(...),
    exclude_models: str = Form(None)
):
    device_type = device_type.lower()
    usage_type = usage_type.lower()
    exclude_models_set = set(exclude_models.split(",")) if exclude_models else set()

    if device_type == "laptop":
        if usage_type not in LAPTOP_USAGE_PROFILES:
            return JSONResponse(content={"error": f"Invalid usage type. Choose from {list(LAPTOP_USAGE_PROFILES.keys())}"}, status_code=400)
        df_filtered = laptop_df[laptop_df['Price'] <= budget].copy()
        df_filtered = df_filtered[~df_filtered['Model'].isin(exclude_models_set)]
        if df_filtered.empty:
            return JSONResponse(content={"error": "No laptops found within your budget after filtering."}, status_code=404)
        features = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
        df_normalized = df_filtered.copy()
        df_normalized[features] = laptop_scaler.transform(df_filtered[features])
        weights = LAPTOP_USAGE_PROFILES[usage_type]
        scores = []
        for idx, row in df_normalized.iterrows():
            score = 0
            for feature, weight in weights.items():
                if feature == "gpu_brand_score":
                    gpu = df_filtered.loc[idx, "gpu_brand"].lower()
                    score += weight * {"nvidia": 1.0, "amd": 0.7, "intel": 0.5}.get(gpu, 0.3)
                else:
                    score += weight * row[feature]
            scores.append(score)
        df_filtered["Score"] = scores
        top20 = df_filtered.sort_values(by="Score", ascending=False).head(20)

    elif device_type == "phone":
        if usage_type not in PHONE_USAGE_PROFILES:
            return JSONResponse(content={"error": f"Invalid usage type. Choose from {list(PHONE_USAGE_PROFILES.keys())}"}, status_code=400)
        df_filtered = phone_df[phone_df['Price'] <= budget].copy()
        df_filtered = df_filtered[~df_filtered['Model'].isin(exclude_models_set)]
        if df_filtered.empty:
            return JSONResponse(content={"error": "No phones found within your budget after filtering."}, status_code=404)
        features = ['Price', '5g', 'RAM', 'Storage', 'Battery', 'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']
        df_normalized = df_filtered.copy()
        df_normalized[features] = phone_scaler.transform(df_filtered[features])
        weights = PHONE_USAGE_PROFILES[usage_type]
        scores = []
        for idx, row in df_normalized.iterrows():
            score = sum(weights.get(f, 0) * row[f] for f in features if f in weights)
            scores.append(score)
        df_filtered['Score'] = scores
        top20 = df_filtered.sort_values(by='Score', ascending=False).head(20)

    else:
        return JSONResponse(content={"error": "Invalid device type."}, status_code=400)

    # GSMArena enrichment (for future use, currently disabled)
    if device_type == "laptop":
        recs = top20.to_dict(orient='records')
    elif device_type == "phone":
        recs = top20.to_dict(orient='records')
        # for rec in recs:
        #     gsmarena = get_gsmarena_info(rec["Brand"], rec["Model"])
        #     if gsmarena:
        #         rec.update(gsmarena)
        #     time.sleep(0.5)  # To avoid rate limiting

    return {"recommendations": recs}

@app.post("/similar")
async def similar_items(
    device_type: str = Form(...),
    model: str = Form(...),
):
    device_type = device_type.lower()
    if device_type == "laptop":
        df = laptop_df
        scaler = laptop_scaler
        features = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
    elif device_type == "phone":
        df = phone_df
        scaler = phone_scaler
        features = ['Price', '5g', 'RAM', 'Storage', 'Battery', 'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']
    else:
        return JSONResponse(content={"error": "Invalid device type."}, status_code=400)

    # Normalize features
    df_norm = df.copy()
    df_norm[features] = scaler.transform(df[features])
    df_norm = df_norm.dropna(subset=features)

    # Find the item by model (case-insensitive, stripped)
    item = df_norm[df_norm['Model'].str.strip().str.lower() == model.strip().lower()]
    if item.empty:
        return JSONResponse(content={"error": "Item not found."}, status_code=404)
    item_vec = item[features].values

    # Compute cosine similarity
    all_vecs = df_norm[features].values
    sims = cosine_similarity(item_vec, all_vecs)[0]
    df_norm['similarity'] = sims

    # Exclude the item itself and get top 5 most similar
    similar_items = df_norm[df_norm['Model'].str.strip().str.lower() != model.strip().lower()].sort_values(by='similarity', ascending=False).head(5)
    similar_indices = similar_items.index
    recs = df.loc[similar_indices].to_dict(orient='records')
    return {"recommendations": recs}
