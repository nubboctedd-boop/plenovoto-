import pandas as pd
import unicodedata
import os
import sys

def norm(n):
    if not n or pd.isna(n): return ""
    s = unicodedata.normalize('NFKD', str(n))
    s = "".join([c for c in s if not unicodedata.combining(c)])
    return s.replace(",", "").replace(".", "").strip().lower()

# PATHS
PATH_FOTOS = r"C:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\fotos.xlsx"
PATH_GRID = r"c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\base_congreso_enriquecida_logos.xlsx"

# 1. CARGAR FOTOS
df_fotos = pd.read_excel(PATH_FOTOS)
fotos_norms = {norm(n): os.path.basename(str(p)) for n, p in zip(df_fotos['Nombre'], df_fotos['Ruta_Foto_Original'])}

# 2. CARGAR GRID (como lo hace main.py)
df_grid = pd.read_excel(PATH_GRID, sheet_name="Grid", header=None)
column_groups = [3, 6, 9, 12, 15, 18]
names_in_data = []
for c in column_groups:
    col = df_grid.iloc[2:25, c].dropna().tolist() # Máximo 23 filas
    names_in_data.extend([str(n).strip() for n in col if str(n).strip() != "" and str(n).strip().upper() != "CONGRESISTA"])

matches = 0
for name in names_in_data:
    n_name = norm(name)
    if n_name in fotos_norms:
        matches += 1
    else:
        # Intento fuzzy similar a buscar_foto
        import difflib
        possibilities = list(fotos_norms.keys())
        closest = difflib.get_close_matches(n_name, possibilities, n=1, cutoff=0.85)
        if closest:
            matches += 1

print(f"Total Nombres en Grid: {len(names_in_data)}")
print(f"Matches con fotos: {matches}")
