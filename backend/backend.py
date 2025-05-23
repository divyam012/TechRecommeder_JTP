import os
import pickle
import pandas as pd
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files (if you have CSS/JS in frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the frontend HTML
@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")


# Load laptop components
base_dir = os.path.dirname(__file__)
laptop_path = os.path.join(base_dir, "laptop_components.pkl")

with open(laptop_path, "rb") as f:
    laptop_objects = pickle.load(f)
laptop_scaler = laptop_objects["scaler"]
laptop_df = laptop_objects["df"]

# Load phone components
phone_path = os.path.join(base_dir, "phone_components.pkl")
with open(phone_path, "rb") as f:

    phone_objects = pickle.load(f)
phone_scaler = phone_objects["scaler"]
phone_df = phone_objects["df"]

# Usage profiles
LAPTOP_USAGE_PROFILES = {
    "gaming": {"RAM": 3.0, "Storage": 2.5, "gpu_brand_score": 3.0, "num_cores": 2.5, "num_threads": 2.5},
    "business": {"RAM": 3.0, "Storage": 2.5, "num_cores": 2.5, "display_size": 2.0},
    "basic": {"Price": -2.5, "RAM": 2.0, "Storage": 2.0, "display_size": 1.5},
    "student": {"RAM": 2.5, "Storage": 2.5, "Price": -2.0, "num_cores": 2.0}
}

PHONE_USAGE_PROFILES = {
    "gaming": {"RAM": 3.5, "Storage": 3.0, "Battery": 3.0, "Rear_cam_mp": 1.0, "Front_cam_mp": 1.0, "5g": 1.5},
    "camera": {"Rear_cam_mp": 3.5, "Front_cam_mp": 2.5, "Num_rear_cam": 2.0, "RAM": 1.5, "Storage": 1.5, "Battery": 1.0},
    "business": {"Battery": 2.5, "RAM": 3.0, "Storage": 3.0, "5g": 2.0},
    "basic": {"Battery": 2.0, "Price": -3.0, "RAM": 2.0, "Storage": 2.0, "5g": 1.0}
}


@app.post("/recommend", response_class=HTMLResponse)
async def recommend_form(
    request: Request,
    device_type: str = Form(...),
    budget: float = Form(...),
    usage_type: str = Form(...)
):
    device_type = device_type.lower()
    usage_type = usage_type.lower()

    if device_type == "laptop":
        if usage_type not in LAPTOP_USAGE_PROFILES:
            return HTMLResponse(content=f"<h3>Invalid usage type. Choose from {list(LAPTOP_USAGE_PROFILES.keys())}</h3>")

        df_filtered = laptop_df[laptop_df['Price'] <= budget].copy()
        if df_filtered.empty:
            return HTMLResponse(content=f"<h3>No laptops found within your budget.</h3>")

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
                    score += weight * {
                        "nvidia": 1.0,
                        "amd": 0.7,
                        "intel": 0.5
                    }.get(gpu, 0.3)
                else:
                    score += weight * row[feature]
            scores.append(score)

        df_filtered["Score"] = scores
        top5 = df_filtered.sort_values(by="Score", ascending=False).head(5)

    elif device_type == "phone":
        if usage_type not in PHONE_USAGE_PROFILES:
            return HTMLResponse(content=f"<h3>Invalid usage type. Choose from {list(PHONE_USAGE_PROFILES.keys())}</h3>")

        df_filtered = phone_df[phone_df['Price'] <= budget].copy()
        if df_filtered.empty:
            return HTMLResponse(content=f"<h3>No phones found within your budget.</h3>")

        features = ['Price', '5g', 'RAM', 'Storage', 'Battery', 'Num_rear_cam', 'Front_cam_mp', 'Rear_cam_mp']
        df_normalized = df_filtered.copy()
        df_normalized[features] = phone_scaler.transform(df_filtered[features])

        weights = PHONE_USAGE_PROFILES[usage_type]
        scores = []
        for idx, row in df_normalized.iterrows():
            score = sum(weights.get(f, 0) * row[f] for f in features if f in weights)
            scores.append(score)

        df_filtered['Score'] = scores
        top5 = df_filtered.sort_values(by='Score', ascending=False).head(5)

    else:
        return HTMLResponse(content="<h3>Invalid device type.</h3>")

    # Render recommendations as HTML
    html_content = "<h2>Top 5 Recommendations</h2><ul>"
    for _, row in top5.iterrows():
        html_content += f"<li>{row['Brand']} {row['Model']} - ₹{int(row['Price'])}</li>"
    html_content += "</ul><br><a href='/'>Go Back</a>"

    return HTMLResponse(content=html_content)
