# Prompt Claude Code — OE4 + OE5: Entrenamiento TF-IDF + MLP

## Contexto del proyecto

Herramienta de clasificación de contenido electoral desinformativo en Bolivia. Pipeline de procesamiento: Streamlit → FastAPI → pipeline Pipes & Filters (preprocessor → OCR → cleaner → vectorizer → classifier) → PostgreSQL.

El modelo de clasificación usa **TF-IDF** (scikit-learn `TfidfVectorizer`) para vectorizar texto y **MLP** (scikit-learn `MLPClassifier`) para clasificar en tres niveles de prioridad: `Alta`, `Media`, `Baja`.

## Prerequisito

El archivo `backend/data/dataset_maestro.csv` debe existir y tener datos. Si está vacío, detente e informa al usuario antes de continuar.

## Objetivo de esta tarea (OE4 + OE5)

Crear el directorio `ml_training/` y el script `ml_training/train_model.py` que:
1. Lea el dataset maestro
2. Preprocese el texto (limpieza básica)
3. Entrene el `TfidfVectorizer`
4. Entrene el `MLPClassifier`
5. Evalúe el modelo con métricas
6. Guarde los modelos `.pkl` en `backend/data/models_saved/`

## Estructura a crear

```
ml_training/
├── __init__.py          (vacío)
└── train_model.py       (script principal)
```

## Especificaciones de train_model.py

### 1. Imports necesarios
```python
import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
```

### 2. Rutas (relativas a la raíz del proyecto)
```python
DATASET_PATH     = "backend/data/dataset_maestro.csv"
VECTORIZER_PATH  = "backend/data/models_saved/tfidf_vectorizer.pkl"
CLASSIFIER_PATH  = "backend/data/models_saved/mlp_classifier.pkl"
```

### 3. Función de limpieza de texto
Implementar `clean_text(text: str) -> str` que aplique en este orden:
- Convertir a minúsculas
- Eliminar URLs (patrón `https?://\S+`)
- Eliminar menciones (@usuario) y hashtags (#tema)
- Eliminar caracteres especiales, conservando letras (incluyendo tildes y ñ), números y espacios
- Eliminar espacios múltiples con `strip()`

Esta función debe ser **idéntica** a la que después irá en `backend/app/pipeline/filter_cleaner.py` para que el modelo y el pipeline usen la misma normalización.

### 4. Configuración del TfidfVectorizer
```python
TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),     # unigramas y bigramas
    min_df=2,               # ignorar términos que aparecen en menos de 2 docs
    max_df=0.95,            # ignorar términos en más del 95% de docs
    sublinear_tf=True       # aplicar escala logarítmica a TF
)
```

### 5. Configuración del MLPClassifier
```python
MLPClassifier(
    hidden_layer_sizes=(256, 128),   # dos capas ocultas
    activation='relu',
    solver='adam',
    alpha=0.001,                     # regularización L2
    learning_rate='adaptive',
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=15,
    verbose=False
)
```

### 6. Flujo principal del script

```
1. Cargar dataset_maestro.csv
2. Verificar que tenga columnas 'texto_crudo' y 'label'
3. Eliminar filas con texto_crudo nulo o vacío
4. Aplicar clean_text() a texto_crudo → columna 'texto_limpio'
5. Separar X = texto_limpio, y = label
6. train_test_split(test_size=0.2, random_state=42, stratify=y)
7. Fit del TfidfVectorizer sobre X_train → X_train_vec
8. Transform sobre X_test → X_test_vec
9. Fit del MLPClassifier sobre X_train_vec, y_train
10. Evaluar sobre X_test_vec, y_test
11. Guardar vectorizer y classifier con joblib.dump()
12. Imprimir reporte completo
```

### 7. Reporte que debe imprimir al finalizar

```
============================================================
  ENTRENAMIENTO COMPLETADO — Herramienta Electoral
============================================================

Dataset:
  Total registros        : X
  Registros de entrenamiento: X
  Registros de prueba    : X

Distribución de clases (total):
  Alta  : X (X%)
  Media : X (X%)
  Baja  : X (X%)

--- Métricas sobre conjunto de prueba ---
Accuracy : X.XX

Classification Report:
              precision    recall  f1-score   support
        Alta       X.XX      X.XX      X.XX       X
       Media       X.XX      X.XX      X.XX       X
        Baja       X.XX      X.XX      X.XX       X
    accuracy                           X.XX       X

Matriz de confusión:
[[X X X]
 [X X X]
 [X X X]]

Cross-validation (5-fold, accuracy): X.XX ± X.XX

Modelos guardados:
  backend/data/models_saved/tfidf_vectorizer.pkl
  backend/data/models_saved/mlp_classifier.pkl
============================================================
```

## Restricciones importantes

- **No usar Pipeline de sklearn** para guardar los modelos. Guardar vectorizer y classifier por separado con `joblib.dump()`. Esto es crítico porque el pipeline de FastAPI los carga de forma independiente.
- Usar `encoding='utf-8'` al leer el CSV.
- Crear `backend/data/models_saved/` si no existe (`os.makedirs(..., exist_ok=True)`).
- El script debe poder ejecutarse desde la raíz del proyecto con: `python ml_training/train_model.py`
- Agregar un bloque `if __name__ == "__main__":` que llame a la función principal.

## Después de crear y ejecutar el script

Verifica que existan ambos archivos:
- `backend/data/models_saved/tfidf_vectorizer.pkl`
- `backend/data/models_saved/mlp_classifier.pkl`

Si existen y el accuracy supera 0.70, la tarea está completa.
