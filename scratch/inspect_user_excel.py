import pandas as pd
import sys

file_path = r'C:\Users\sergi\Downloads\PROYECCIÓN INVESTIDURA - VERSION FINAL - GABINETE ARROYO.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Hojas encontradas: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Analizando Hoja: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet)
        print(f"Columnas: {df.columns.tolist()[:10]}")
        print("Muestra (primeras 5 filas):")
        print(df.iloc[:5, :10].to_string())
except Exception as e:
    print(f"Error: {e}")
