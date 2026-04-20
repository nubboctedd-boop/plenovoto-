import pandas as pd
import os

EXCEL_PATH = r'c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\base_congreso_enriquecida_logos.xlsx'
df = pd.read_excel(EXCEL_PATH, header=2)
groups = [(3,4), (6,7), (9,10), (12,13), (15,16), (18,19)]

for i, (n, b) in enumerate(groups):
    # We take rows 0 to 22 (23 rows total)
    subset = df.iloc[0:23, n]
    count = subset.notna().sum()
    print(f"Col {i+1} (indices {n},{b}): {count} congressmen")
    # Show the last 5 names in this column
    last_names = subset.dropna().tail(5).tolist()
    print(f"  Last 5: {last_names}")
