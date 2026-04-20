import pandas as pd
import unicodedata
import os

def norm(n):
    if not n or pd.isna(n): return ""
    s = unicodedata.normalize('NFKD', str(n))
    s = "".join([c for c in s if not unicodedata.combining(c)])
    return s.replace(",", "").replace(".", "").strip().lower()

# Cargar fotos
try:
    df_fotos = pd.read_excel(r"C:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\fotos.xlsx")
    fotos_norms = {norm(n): n for n in df_fotos['Nombre'].tolist()}
    print(f"Fotos cargadas: {len(fotos_norms)}")
except Exception as e:
    print(f"Error fotos: {e}")

# Cargar Grid
try:
    path_grid = r"c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\base_congreso_enriquecida_logos.xlsx"
    df_grid = pd.read_excel(path_grid, sheet_name="Grid", header=None)
    grid_names = []
    column_groups = [3, 6, 9, 12, 15, 18]
    for c in column_groups:
        names_col = df_grid.iloc[2:, c].dropna().tolist()
        grid_names.extend([str(n).strip() for n in names_col if str(n).strip() != "" and str(n).strip().upper() != "CONGRESISTA"])
    
    grid_norms = {norm(n): n for n in grid_names}
    print(f"Nombres en Grid: {len(grid_norms)}")
    
    matches = []
    mismatches = []
    for gn in grid_norms:
        if gn in fotos_norms:
            matches.append(grid_norms[gn])
        else:
            mismatches.append(grid_norms[gn])
            
    print(f"Coincidencias: {len(matches)}")
    if matches:
        print(f"Ejemplo coincidencia: {matches[0]} -> {fotos_norms[norm(matches[0])]}")
    if mismatches:
        print(f"Ejemplo fallo: {mismatches[0]}")
        # Buscar el más parecido
        import difflib
        possibilities = fotos_norms.keys()
        closest = difflib.get_close_matches(norm(mismatches[0]), possibilities, n=1)
        if closest:
             print(f"  Sugerencia más cercana en fotos: {fotos_norms[closest[0]]}")
except Exception as e:
    print(f"Error grid: {e}")
