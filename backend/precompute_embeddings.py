import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

print("Loading dataset...")
df = pd.read_csv("dataset.csv")

# Build text descriptions for each startup
texts = []
for _, row in df.iterrows():
    parts = [str(row.get("name", ""))]
    cat = str(row.get("category_code", ""))
    if cat and cat != "nan":
        parts.append(f"[{cat}]")
    city = str(row.get("city", ""))
    if city and city != "nan":
        parts.append(f"({city})")
    texts.append(" ".join(parts))

print(f"Loaded {len(texts)} rows")

print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Computing embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
print(f"Embedding shape: {embeddings.shape}")

# Save
np.save("dataset_embeddings.npy", embeddings)
joblib.dump(texts, "dataset_texts.pkl")
print("Saved dataset_embeddings.npy, dataset_texts.pkl")

# Also keep the feature vectors (X) used for training
drop_cols = [
    "Unnamed: 0", "state_code", "zip_code", "id", "city", "Unnamed: 6",
    "state_code.1", "name", "labels", "founded_at", "closed_at",
    "first_funding_at", "last_funding_at", "object_id", "category_code",
]
X_full = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
X_full = X_full.drop(columns=["status"], errors="ignore")
num_cols = X_full.select_dtypes(include=[np.number]).columns.tolist()
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
X_full[num_cols] = imputer.fit_transform(X_full[num_cols])
feature_names = X_full.columns.tolist()
np.save("dataset_feature_vectors.npy", X_full.values)
joblib.dump(feature_names, "dataset_feature_names.pkl")
print(f"Saved dataset_feature_vectors.npy ({X_full.shape}) and feature names")
