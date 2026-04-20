import pandas as pd

EXCEL_PATH = r'c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\base_congreso_enriquecida_logos.xlsx'
df = pd.read_excel(EXCEL_PATH, header=2)

names_to_check = ['WONG', 'SAAVEDRA', 'VASQUEZ', 'ANDERSON']

for col_idx, col_name in enumerate(df.columns):
    for row_idx, val in enumerate(df[col_name]):
        val_str = str(val).upper()
        for name in names_to_check:
            if name in val_str:
                print(f"FOUND: '{val}' at Row {row_idx}, Col Index {col_idx} (Header: {col_name})")
