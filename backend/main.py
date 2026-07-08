import random

import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load ML model
# ---------------------------------------------------------------------------
try:
    model = joblib.load("model.pkl")
    feature_names = joblib.load("model_features.pkl")
    print(f"ML model loaded: {len(feature_names)} features")
except Exception:
    model = None
    feature_names = None
    print("WARNING: ML model not found, running in mock-only mode")

# ---------------------------------------------------------------------------
# Load dataset embeddings for semantic similarity
# ---------------------------------------------------------------------------
embedder = None
dataset_embeddings = None
dataset_feature_vectors = None
dataset_texts = None
try:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    dataset_embeddings = np.load("dataset_embeddings.npy")
    dataset_feature_vectors = np.load("dataset_feature_vectors.npy")
    dataset_texts = joblib.load("dataset_texts.pkl")
    print(f"Dataset embeddings loaded: {dataset_embeddings.shape}")
except Exception as e:
    print(f"WARNING: Could not load dataset embeddings ({e}); falling back")
    embedder = None


def _find_similar_startups(idea_text: str, top_k: int = 5):
    if embedder is None or dataset_embeddings is None:
        return None, None, None
    idea_emb = embedder.encode([idea_text])
    sims = np.dot(dataset_embeddings, idea_emb.T).flatten()
    top_idx = np.argsort(sims)[::-1][:top_k]
    weights = np.maximum(sims[top_idx], 0.0)
    if weights.sum() == 0:
        weights = np.ones_like(weights)
    weights = weights / weights.sum()
    avg_vec = np.average(dataset_feature_vectors[top_idx], axis=0, weights=weights)
    return avg_vec, top_idx.tolist(), sims[top_idx].tolist()


class AnalyzeRequest(BaseModel):
    idea: str
    industry: str = ""
    target_audience: str = ""
    country: str = ""


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.post("/analyze")
async def analyze_idea(payload: AnalyzeRequest):
    seed = len(payload.idea) + len(payload.industry) + len(payload.target_audience)
    rng = random.Random(seed)

    score = rng.randint(40, 95)

    if score >= 75:
        verdict = "Promising"
    elif score >= 50:
        verdict = "Needs refinement"
    else:
        verdict = "Underdeveloped"

    strengths_pool = [
        "Clear problem-solution fit",
        "Large addressable market",
        "Strong revenue potential",
        "Low customer acquisition cost",
        "Scalable business model",
        "First-mover advantage in niche",
        "Strong moat via technology",
        "High user retention potential",
    ]
    risks_pool = [
        "High dependency on third-party platforms",
        "Regulatory compliance may be costly",
        "Customer acquisition could be expensive",
        "Long sales cycle in enterprise segment",
        "Technical complexity may delay MVP",
        "Existing competitors have strong foothold",
        "Monetization path is unclear",
        "Team lacks domain expertise",
    ]
    suggestions_pool = [
        "Run a smoke test with a landing page",
        "Interview 20 potential users this week",
        "Study top 3 competitors in detail",
        "Define a clear north-star metric",
        "Build a no-code prototype first",
        "Explore partnership distribution channels",
        "Focus on a single vertical initially",
        "Draft a lean canvas business model",
    ]

    # ------------------------------------------------------------------
    # ML prediction via semantic similarity
    # ------------------------------------------------------------------
    ml_result = None
    if model is not None and feature_names is not None:
        try:
            vec, neighbor_indices, neighbor_sims = _find_similar_startups(
                f"{payload.idea} {payload.industry} {payload.target_audience}"
            )
            if vec is None:
                # Fallback to zeros (safe default)
                vec = np.zeros(len(feature_names))
                neighbor_indices = []
                neighbor_sims = []

            vec_2d = vec.reshape(1, -1)
            proba = model.predict_proba(vec_2d)[0]
            pred_class = int(model.predict(vec_2d)[0])
            success_prob = round(float(proba[1]), 4)
            ml_result = {
                "success_probability": success_prob,
                "prediction": "acquired" if pred_class == 1 else "closed",
                "similar_startups": neighbor_indices,
                "similarity_scores": [round(s, 4) for s in neighbor_sims],
            }
        except Exception as e:
            ml_result = {"error": str(e)}

    return {
        "idea": payload.idea,
        "industry": payload.industry or "Not specified",
        "target_audience": payload.target_audience or "Not specified",
        "country": payload.country or "Not specified",
        "score": score,
        "verdict": verdict,
        "market_size_estimate": f"${rng.randint(1, 50)}B TAM",
        "competition_level": rng.choice(["Low", "Medium", "High"]),
        "strengths": rng.sample(strengths_pool, 3),
        "risks": rng.sample(risks_pool, 3),
        "suggestions": rng.sample(suggestions_pool, 3),
        "ml_prediction": ml_result,
    }
