import os
import json
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_DIR = "model"
EMB_PATH = os.path.join(MODEL_DIR, "recommender_embeddings.npy")
META_PATH = os.path.join(MODEL_DIR, "recommender_metadata.pkl")
INFO_PATH = os.path.join(MODEL_DIR, "recommender_model_info.json")

# Load metadata
meta_df = joblib.load(META_PATH)

# Load recipe embeddings
recipe_embeddings = np.load(EMB_PATH)

# Load embedding model info
with open(INFO_PATH, "r") as f:
    info = json.load(f)

embed_model = SentenceTransformer(info["embedding_model"])


def normalize_text(x):
    if not x:
        return ""
    return str(x).lower().strip()


def recommend_recipes(pantry_ingredients, top_k=5, category=None):
    pantry_norm = normalize_text(pantry_ingredients)

    pantry_emb = embed_model.encode([f"Ingredients: {pantry_norm}"])[0]
    pantry_emb = pantry_emb.reshape(1, -1)

    sims = cosine_similarity(pantry_emb, recipe_embeddings)[0]

    # CATEGORY FILTER
    if category:
        category = category.lower().strip()
        mask = meta_df["categories"].str.lower().str.contains(category)
        meta_filtered = meta_df[mask].copy()
        sims_filtered = sims[mask]
    else:
        meta_filtered = meta_df.copy()
        sims_filtered = sims

    # TOP K
    top_idx = np.argsort(sims_filtered)[::-1][:top_k]

    results = []
    for idx in top_idx:
        row = meta_filtered.iloc[idx]
        results.append({
            "title": row["Title"],
            "ingredients_text": row["ingredients_text"],
            "categories": row["categories"],
            "score": float(sims_filtered[idx])
        })

    return results