from typing import List, Optional, Dict, Any

import numpy as np

from ..deps import get_recommender_data, get_embed_model
from ..config import ALPHA_INGREDIENT, BETA_EMBEDDING


def _normalize_text(x):
    if x is None:
        return ""
    return str(x).strip().lower()


def _to_word_set(text: str):
    import re
    WORD_SPLIT_RE = re.compile(r"[,\s;:\(\)\[\]\.\-]+")
    if not isinstance(text, str):
        return set()
    words = [w.strip() for w in WORD_SPLIT_RE.split(text.lower()) if w.strip()]
    return set(words)


def _ingredient_overlap_score(pantry_words, recipe_words):
    if not pantry_words:
        return 0.0
    inter = pantry_words & recipe_words
    return len(inter) / float(len(pantry_words))


def _build_pantry_embedding(pantry_ingredients: str):
    embed_model = get_embed_model()
    text = _normalize_text(pantry_ingredients)
    embed_text = f"Ingredients: {text}"
    emb = embed_model.encode([embed_text])
    return emb[0]


def _filter_by_category(df, category: Optional[str]):
    if category is None or not str(category).strip():
        return df.index.to_list()
    category = category.strip().lower()
    mask = df["categories_list"].apply(
        lambda cats: category in [c.lower() for c in cats]
    )
    return df[mask].index.to_list()


def recommend_recipes(pantry_ingredients: str, top_k: int = 5,
                      category: Optional[str] = None) -> List[Dict[str, Any]]:
    df, recipe_embeddings, _ = get_recommender_data()

    pantry_norm = _normalize_text(pantry_ingredients)
    pantry_words = _to_word_set(pantry_norm)

    candidate_idx = _filter_by_category(df, category)
    if not candidate_idx:
        return []

    cand_embeddings = recipe_embeddings[candidate_idx]
    cand_df = df.iloc[candidate_idx].reset_index(drop=True)

    overlap_scores = []
    for _, row in cand_df.iterrows():
        score = _ingredient_overlap_score(pantry_words, row["ingredients_words"])
        overlap_scores.append(score)
    overlap_scores = np.array(overlap_scores)

    pantry_emb = _build_pantry_embedding(pantry_ingredients)
    pantry_emb = pantry_emb.reshape(1, -1)
    from sklearn.metrics.pairwise import cosine_similarity

    cos_sims = cosine_similarity(pantry_emb, cand_embeddings)[0]

    def min_max_norm(x):
        if np.allclose(x.max(), x.min()):
            return np.zeros_like(x)
        return (x - x.min()) / (x.max() - x.min())

    overlap_norm = min_max_norm(overlap_scores)
    cos_norm = min_max_norm(cos_sims)

    final_scores = ALPHA_INGREDIENT * overlap_norm + BETA_EMBEDDING * cos_norm

    cand_df = cand_df.copy()
    cand_df["overlap_score"] = overlap_scores
    cand_df["cosine_score"] = cos_sims
    cand_df["final_score"] = final_scores

    cand_df = cand_df.sort_values("final_score", ascending=False)
    top = cand_df.head(top_k)

    results = []
    for _, row in top.iterrows():
        results.append({
            "title": row["Title"],
            "ingredients_text": row["ingredients_text"],
            "categories": row["categories"],
            "final_score": float(row["final_score"]),
            "overlap_score": float(row["overlap_score"]),
            "cosine_score": float(row["cosine_score"]),
        })

    return results


def list_all_categories() -> List[str]:
    df, _, _ = get_recommender_data()
    cats = set()
    for cat_str in df["categories"]:
        if isinstance(cat_str, str) and cat_str.strip():
            for c in cat_str.split("|"):
                if c.strip():
                    cats.add(c.strip())
    return sorted(cats)