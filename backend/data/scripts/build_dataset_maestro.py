"""
Construye backend/data/dataset_maestro.csv consolidando las dos fuentes brutas.
Ejecutar desde cualquier directorio: python backend/data/scripts/build_dataset_maestro.py
"""
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

SRC1      = os.path.join(ROOT, "dataset_electoral_maestro.csv")
SRC2      = os.path.join(ROOT, "dataset_chequeabolivia_electoral_filtrado.csv")
OUT_PATH  = os.path.join(ROOT, "backend", "data", "dataset_maestro.csv")

df1 = pd.read_csv(SRC1, encoding="utf-8-sig")
df2 = pd.read_csv(SRC2, encoding="utf-8-sig")

df = pd.concat([df1, df2], ignore_index=True)
total_antes = len(df)

df["categoria_original"] = df["categoria_original"].replace("Enganosa", "Engañoso")
df = df.drop_duplicates(subset=["url_origen"],  keep="first")
df = df.drop_duplicates(subset=["texto_crudo"], keep="first")
total_despues = len(df)

label_map = {"Falso": "Alta", "Engañoso": "Media", "Verdadero": "Baja"}
df["label"] = df["categoria_original"].map(label_map)

df = df.reset_index(drop=True)
df["id_registro"] = df.index + 1
df = df[["id_registro", "fuente_verificadora", "url_origen", "texto_crudo", "categoria_original", "label"]]

df.to_csv(OUT_PATH, encoding="utf-8", index=False)

dist_label  = df["label"].value_counts()
dist_fuente = df["fuente_verificadora"].value_counts()

print(f"Total filas antes de deduplicar : {total_antes}")
print(f"Total filas después de deduplicar: {total_despues}")
print(f"Duplicados eliminados            : {total_antes - total_despues}")
print()
print("Distribución de label:")
print(f"  Alta  : {dist_label.get('Alta', 0)}  (Falso)")
print(f"  Media : {dist_label.get('Media', 0)}  (Engañoso)")
print(f"  Baja  : {dist_label.get('Baja', 0)}  (Verdadero)")
print()
print("Distribución por fuente:")
for fuente, count in dist_fuente.items():
    print(f"  {fuente} : {count}")
print()
print(f"Archivo guardado en: backend/data/dataset_maestro.csv")
