import os
import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import json

app = FastAPI()

# CORS configuration
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

# Consistent usage profiles
LAPTOP_USAGE_PROFILES = {
    "gaming": {"RAM": 3.0, "Storage": 2.5, "gpu_brand_score": 2.0, "num_cores": 2.5, "num_threads": 2.5},
    "business": {"RAM": 2.0, "Storage": 2.0, "num_cores": 2.0, "display_size": 2.0},
    "basic": {"RAM": 2.0, "Storage": 2.0, "display_size": 1.5},
    "student": {"RAM": 2.5, "Storage": 2.5, "num_cores": 2.0}
}

PHONE_USAGE_PROFILES = {
    "gaming": {"RAM": 3.5, "Storage": 3.0, "Battery": 3.0, "Rear_cam_mp": 1.0, "Front_cam_mp": 1.0, "5g": 1.5},
    "camera": {"Rear_cam_mp": 3.5, "Front_cam_mp": 2.5, "Num_rear_cam": 2.0, "RAM": 1.5, "Storage": 1.5, "Battery": 1.0},
    "business": {"Battery": 2.5, "RAM": 3.0, "Storage": 3.0, "5g": 2.0},
    "basic": {"Battery": 2.0, "RAM": 2.0, "Storage": 2.0, "5g": 1.0}
}

class SafeJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        def fix_floats(o):
            if isinstance(o, float):
                if np.isnan(o) or np.isinf(o):
                    return 0.0  # Replace NaN/Inf with 0.0
                return round(o, 4)  # Round floats to 4 decimal places
            elif isinstance(o, dict):
                return {k: fix_floats(v) for k, v in o.items()}
            elif isinstance(o, list):
                return [fix_floats(v) for v in o]
            return o
        
        return super().encode(fix_floats(obj))

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
            return JSONResponse(
                content={"error": f"Invalid usage type. Choose from {list(LAPTOP_USAGE_PROFILES.keys())}"}, 
                status_code=400
            )
        
        # Get laptops within budget
        df_filtered = laptop_df[laptop_df['Price'] <= budget].copy()
        df_filtered = df_filtered[~df_filtered['Model'].isin(exclude_models_set)]
        
        # If no laptops found, find closest above budget
        if df_filtered.empty:
            df_above = laptop_df[laptop_df['Price'] > budget].copy()
            df_above = df_above[~df_above['Model'].isin(exclude_models_set)]
            
            if df_above.empty:
                return JSONResponse(
                    content={"error": "No laptops found in the database."}, 
                    status_code=404
                )
                
            df_above['Price_Diff'] = df_above['Price'] - budget
            closest_matches = df_above.nsmallest(5, 'Price_Diff')
            return JSONResponse(
                content={
                    "error": "No laptops found within your budget. Showing closest matches above your budget.",
                    "recommendations": closest_matches.drop(columns=['Price_Diff']).to_dict(orient="records")
                },
                status_code=200
            )

        # Normalize features
        features = ['Price', 'RAM', 'Storage', 'num_cores', 'num_threads', 'display_size']
        available_features = [f for f in features if f in df_filtered.columns]
        
        df_normalized = df_filtered.copy()
        df_normalized[available_features] = laptop_scaler.transform(df_filtered[available_features])
        
        weights = LAPTOP_USAGE_PROFILES[usage_type]
        scores = []
        
        for idx, row in df_normalized.iterrows():
            score = 0
            # Apply weights to features
            for feature, weight in weights.items():
                if feature in df_normalized.columns:
                    if feature == "gpu_brand_score":
                        gpu = str(df_filtered.loc[idx, "gpu_brand"]).lower().strip()
                        gpu_score = {
                            "nvidia": 1.0, 
                            "amd": 0.7, 
                            "intel": 0.5
                        }.get(gpu, 0.3)
                        score += weight * gpu_score
                    else:
                        score += weight * row[feature]
            scores.append(score)
        
        df_filtered["Score"] = scores
        top_recs = df_filtered.sort_values(by="Score", ascending=False).head(20)
        
        # Convert to safe JSON format
        recommendations = json.loads(
            top_recs.replace({np.nan: None}).to_json(orient="records", date_format="iso")
        )
        
        return JSONResponse(
            content={"recommendations": recommendations}, 
            status_code=200
        )

    elif device_type == "phone":
        if usage_type not in PHONE_USAGE_PROFILES:
            return JSONResponse(
                content={"error": f"Invalid usage type. Choose from {list(PHONE_USAGE_PROFILES.keys())}"}, 
                status_code=400
            )
        
        # Get phones within budget
        df_filtered = phone_df[phone_df['Price'] <= budget].copy()
        df_filtered = df_filtered[~df_filtered['Model'].isin(exclude_models_set)]
        
        if df_filtered.empty:
            return JSONResponse(
                content={"error": "No phones found within your budget."}, 
                status_code=404
            )
        
        # Features to use
        features = ['Price', '5g', 'RAM', 'Storage', 'Battery', 'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']
        
        # Set default values for missing features in budget phones
        for feature in ['5g', 'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']:
            if feature not in df_filtered.columns:
                df_filtered[feature] = 0
            else:
                df_filtered[feature] = df_filtered[feature].fillna(0)
        
        available_features = [f for f in features if f in df_filtered.columns]
        
        df_normalized = df_filtered.copy()
        df_normalized[available_features] = phone_scaler.transform(df_filtered[available_features])
        
        weights = PHONE_USAGE_PROFILES[usage_type]
        scores = []
        
        for idx, row in df_normalized.iterrows():
            score = 0
            # Apply weights to features
            for feature, weight in weights.items():
                if feature in available_features:
                    score += weight * row[feature]
            
            # FIX: Handle basic phones under 20k
            if usage_type == "basic" and budget < 20000:
                # Prioritize battery and RAM for budget phones
                if 'Battery' in available_features:
                    score += row['Battery'] * 1.5
                if 'RAM' in available_features:
                    score += row['RAM'] * 1.5
            
            scores.append(score)
        
        df_filtered['Score'] = scores
        top_recs = df_filtered.sort_values(by='Score', ascending=False).head(20)
        
        # Convert to safe JSON format
        recommendations = json.loads(
            top_recs.replace({np.nan: None}).to_json(orient="records", date_format="iso")
        )
        
        return JSONResponse(
            content={"recommendations": recommendations}, 
            status_code=200
        )

    else:
        return JSONResponse(
            content={"error": "Invalid device type."}, 
            status_code=400
        )

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
        return JSONResponse(
            content={"error": "Invalid device type."}, 
            status_code=400
        )

    # Normalize features
    df_norm = df.copy()
    available_features = [f for f in features if f in df_norm.columns]
    df_norm[available_features] = scaler.transform(df[available_features])
    
    # Handle NaN values
    df_norm = df_norm.fillna(0)
    
    # Clean and find model
    model_clean = model.strip().lower()
    item = df_norm[
        df_norm['Model'].str.strip().str.lower() == model_clean
    ]
    
    if item.empty:
        return JSONResponse(
            content={"error": "Item not found."}, 
            status_code=404
        )
    
    item_vec = item[available_features].values

    # Compute cosine similarity
    all_vecs = df_norm[available_features].values
    sims = cosine_similarity(item_vec, all_vecs)[0]
    df_norm['similarity'] = sims

    # Exclude the item itself and get top 5 most similar
    similar_items = df_norm[
        df_norm['Model'].str.strip().str.lower() != model_clean
    ].sort_values(by='similarity', ascending=False).head(5)
    
    similar_indices = similar_items.index
    recs = df.loc[similar_indices].replace({np.nan: None}).to_dict(orient='records')
    
    # Use custom encoder for safe JSON serialization
    return JSONResponse(
        content={"recommendations": recs}
    )