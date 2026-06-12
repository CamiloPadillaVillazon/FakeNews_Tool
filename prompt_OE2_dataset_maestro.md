# Prompt Claude Code — OE2: Construcción del Dataset Maestro

## Contexto del proyecto

Estoy desarrollando una herramienta de clasificación de contenido electoral desinformativo en Bolivia como proyecto de grado. La herramienta usa una arquitectura de tres capas (Streamlit → FastAPI → PostgreSQL) con un pipeline de procesamiento basado en el patrón Pipes & Filters. El modelo de clasificación es TF-IDF + MLPClassifier (scikit-learn). Las etiquetas de salida del clasificador son tres niveles de prioridad de verificación: **Alta**, **Media**, **Baja**.

## Objetivo de esta tarea (OE2)

Construir el `dataset_maestro.csv` consolidado que servirá como insumo para entrenar el modelo ML. Este archivo debe quedar en `backend/data/dataset_maestro.csv`.

## Fuentes de datos disponibles

Ambos archivos tienen el mismo esquema:
`id_registro, fecha_publicacion, fuente_verificadora, url_origen, texto_crudo, categoria_original`

### Fuente 1
- **Ruta:** `dataset_electoral_maestro.csv` (raíz del proyecto)
- **Origen:** boliviaverifica.bo
- **Registros:** 1097 filas
- **Etiquetas presentes:** `Falso` (801), `Verdadero` (110), `Enganosa` (186)
- **Nota:** La etiqueta "Enganosa" es la misma que "Engañoso" pero sin tilde — normalizar.

### Fuente 2
- **Ruta:** `dataset_chequeabolivia_electoral_filtrado.csv` (raíz del proyecto)
- **Origen:** chequeabolivia.bo (ya filtrado para contenido estrictamente electoral)
- **Registros:** 534 filas
- **Etiquetas presentes:** `Falso` (462), `Verdadero` (13), `Engañoso` (59)

## Mapeo de etiquetas

La `categoria_original` de los verificadores debe convertirse a la columna `label` (prioridad de verificación) según esta tabla:

| categoria_original | label |
|---|---|
| Falso | Alta |
| Engañoso / Enganosa | Media |
| Verdadero | Baja |

## Esquema del archivo de salida

El `backend/data/dataset_maestro.csv` debe tener exactamente estas columnas:

```
id_registro, fuente_verificadora, url_origen, texto_crudo, categoria_original, label
```

- `id_registro`: entero secuencial único desde 1
- `fuente_verificadora`: conservar el valor original
- `url_origen`: conservar el valor original
- `texto_crudo`: conservar el texto original sin modificar
- `categoria_original`: conservar el valor original normalizado (usar "Engañoso" en lugar de "Enganosa")
- `label`: columna nueva con el valor mapeado (Alta / Media / Baja)

**No incluir** `fecha_publicacion` en el archivo de salida (no se usará en el entrenamiento).

## Pasos a ejecutar

1. Leer ambos CSVs con `pandas`, especificando `encoding='utf-8-sig'` para el BOM.
2. Concatenar los dos DataFrames.
3. Normalizar `categoria_original`: reemplazar `"Enganosa"` por `"Engañoso"`.
4. Eliminar duplicados por `url_origen` (keep='first') — puede haber solapamiento entre fuentes.
5. Eliminar duplicados por `texto_crudo` (keep='first') — textos idénticos de distintas fuentes.
6. Crear la columna `label` aplicando el mapeo definido arriba.
7. Reindexar `id_registro` desde 1 de forma secuencial.
8. Seleccionar y reordenar columnas al esquema de salida definido.
9. Guardar en `backend/data/dataset_maestro.csv` con `encoding='utf-8'`, `index=False`.

## Validaciones que debes imprimir al final

```
Total filas antes de deduplicar : X
Total filas después de deduplicar: X
Duplicados eliminados            : X

Distribución de label:
  Alta  : X  (Falso)
  Media : X  (Engañoso)
  Baja  : X  (Verdadero)

Distribución por fuente:
  boliviaverifica.bo : X
  chequeabolivia.bo  : X

Archivo guardado en: backend/data/dataset_maestro.csv
```

## Restricciones

- Usar solo `pandas` y `os` (no instalar librerías adicionales).
- No modificar los archivos fuente originales.
- Si `backend/data/models_saved/` no existe, crearlo vacío (lo usará el entrenamiento posterior).
- El texto en `texto_crudo` no debe ser limpiado ni modificado aquí — eso lo hará `filter_cleaner.py` en tiempo de inferencia y el script de entrenamiento en su propio paso de preprocesamiento.
