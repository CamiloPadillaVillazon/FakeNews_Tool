"""
Incorpora dataset_chequeabolivia_nuevos.csv al dataset_maestro.csv.
Ejecutar desde cualquier directorio: python backend/data/scripts/merge_dataset.py
"""
import os
import pandas as pd

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MAESTRO = os.path.join(ROOT, "backend", "data", "dataset_maestro.csv")
NUEVOS  = os.path.join(ROOT, "backend", "data", "dataset_chequeabolivia_nuevos.csv")
COLS    = ["id_registro", "fuente_verificadora", "url_origen", "texto_crudo", "categoria_original", "label"]

if not os.path.exists(NUEVOS):
    raise FileNotFoundError(f"No se encontró el archivo de nuevos artículos: {NUEVOS}")

df_maestro = pd.read_csv(MAESTRO, encoding="utf-8")
df_nuevos  = pd.read_csv(NUEVOS,  encoding="utf-8")

print(f"Maestro actual  : {len(df_maestro)} filas")
print(f"Nuevos artículos: {len(df_nuevos)} filas")

df = pd.concat([df_maestro, df_nuevos], ignore_index=True)
total_antes = len(df)

df = df.drop_duplicates(subset=["url_origen"],  keep="first")
df = df.drop_duplicates(subset=["texto_crudo"], keep="first")
total_despues = len(df)

df = df.reset_index(drop=True)
df["id_registro"] = df.index + 1
df = df[COLS]

df.to_csv(MAESTRO, encoding="utf-8", index=False)

print(f"Duplicados eliminados: {total_antes - total_despues}")
print(f"Dataset maestro nuevo: {total_despues} filas")
print()
dist  = df["label"].value_counts()
total = len(df)
for label in ["Alta", "Media", "Baja"]:
    n = dist.get(label, 0)
    print(f"  {label:<5}: {n} ({n/total*100:.1f}%)")
print(f"\nGuardado en: backend/data/dataset_maestro.csv")
