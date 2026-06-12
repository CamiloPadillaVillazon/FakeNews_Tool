"""
Entrena TF-IDF + MLPClassifier sobre dataset_maestro.csv.
Ejecutar desde cualquier directorio: python backend/ml_training/train_model.py
"""
import os
import re
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.utils.class_weight import compute_sample_weight

ROOT            = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH    = os.path.join(ROOT, "backend", "data", "dataset_maestro.csv")
VECTORIZER_PATH = os.path.join(ROOT, "backend", "data", "models_saved", "tfidf_vectorizer.pkl")
CLASSIFIER_PATH = os.path.join(ROOT, "backend", "data", "models_saved", "mlp_classifier.pkl")


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"@\w+|#\w+", "", text)
    text = re.sub(r"[^a-záéíóúüñà-ÿ0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def train():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset no encontrado: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH, encoding="utf-8")

    if df.empty:
        raise ValueError("El dataset está vacío. Ejecuta primero build_dataset_maestro.py")

    for col in ("texto_crudo", "label"):
        if col not in df.columns:
            raise ValueError(f"Columna requerida ausente: {col}")

    df = df.dropna(subset=["texto_crudo"])
    df = df[df["texto_crudo"].str.strip() != ""]
    df["texto_limpio"] = df["texto_crudo"].apply(clean_text)

    X     = df["texto_limpio"]
    y     = df["label"]
    total = len(df)
    dist  = y.value_counts()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    classifier = MLPClassifier(
        hidden_layer_sizes=(256, 128),
        activation="relu",
        solver="adam",
        alpha=0.001,
        learning_rate="adaptive",
        max_iter=500,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=15,
        verbose=False,
    )
    sample_weights = compute_sample_weight("balanced", y_train)
    classifier.fit(X_train_vec, y_train, sample_weight=sample_weights)

    y_pred    = classifier.predict(X_test_vec)
    acc       = accuracy_score(y_test, y_pred)
    report    = classification_report(y_test, y_pred, target_names=["Alta", "Media", "Baja"])
    cm        = confusion_matrix(y_test, y_pred, labels=["Alta", "Media", "Baja"])
    cv_scores = cross_val_score(classifier, X_train_vec, y_train, cv=5, scoring="accuracy")

    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(classifier, CLASSIFIER_PATH)

    print("=" * 60)
    print("  ENTRENAMIENTO COMPLETADO — Herramienta Electoral")
    print("=" * 60)
    print()
    print("Dataset:")
    print(f"  Total registros           : {total}")
    print(f"  Registros de entrenamiento: {len(X_train)}")
    print(f"  Registros de prueba       : {len(X_test)}")
    print()
    print("Distribución de clases (total):")
    for label in ["Alta", "Media", "Baja"]:
        n = dist.get(label, 0)
        print(f"  {label:<5} : {n} ({n/total*100:.1f}%)")
    print()
    print("--- Métricas sobre conjunto de prueba ---")
    print(f"Accuracy : {acc:.4f}")
    print()
    print("Classification Report:")
    print(report)
    print("Matriz de confusión:")
    print(cm)
    print()
    print(f"Cross-validation (5-fold, accuracy): {cv_scores.mean():.2f} ± {cv_scores.std():.2f}")
    print()
    print("Modelos guardados:")
    print(f"  backend/data/models_saved/tfidf_vectorizer.pkl")
    print(f"  backend/data/models_saved/mlp_classifier.pkl")
    print("=" * 60)

    return acc


if __name__ == "__main__":
    train()
