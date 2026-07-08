import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer

df = pd.read_csv("dataset.csv")

print(f"Original shape: {df.shape}")
print(f"Target distribution:\n{df['status'].value_counts()}")

# Drop identifier / text columns not useful for prediction
drop_cols = [
    "Unnamed: 0", "state_code", "zip_code", "id", "city", "Unnamed: 6",
    "state_code.1", "name", "labels", "founded_at", "closed_at",
    "first_funding_at", "last_funding_at", "object_id", "category_code",
]
df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

# Encode target: acquired=1, closed=0
df["status"] = df["status"].map({"acquired": 1, "closed": 0})
df.dropna(subset=["status"], inplace=True)

# Separate features and target
y = df["status"]
X = df.drop(columns=["status"])

# Identify numeric columns
num_cols = X.select_dtypes(include=[np.number]).columns.tolist()

# Impute missing numeric values with median
imputer = SimpleImputer(strategy="median")
imputed = imputer.fit_transform(X[num_cols])
X = X.copy()
X[num_cols] = imputed

# Verify no remaining NaNs
nan_counts = X.isna().sum()
nan_cols = nan_counts[nan_counts > 0]
if len(nan_cols):
    print(f"WARNING: NaN cols after imputation: {nan_cols.to_dict()}")
    for c in nan_cols.index:
        X[c] = X[c].fillna(X[c].median() if X[c].dtype.kind in 'iuf' else 'Unknown')
assert X.isna().sum().sum() == 0, f"NaNs still present: {X.isna().sum()[X.isna().sum() > 0].to_dict()}"
assert y.isna().sum() == 0, "NaNs in target"

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")
print(f"Features: {list(X.columns)}")

# Train RandomForest
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_leaf=4,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1,
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {acc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["closed", "acquired"]))

# Feature importance
importances = pd.Series(model.feature_importances_, index=X.columns)
print("\nTop 10 Feature Importances:")
print(importances.sort_values(ascending=False).head(10).to_string())

# Save
joblib.dump(model, "model.pkl")
joblib.dump(X.columns.tolist(), "model_features.pkl")
joblib.dump(imputer, "model_imputer.pkl")
print("\nSaved: model.pkl, model_features.pkl, model_imputer.pkl")
