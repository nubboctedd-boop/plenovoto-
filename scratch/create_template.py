import pandas as pd
import os

# Generar una plantilla de ejemplo basada en los datos reales del congreso
excel_path = "../../base_congreso_enriquecida_logos.xlsx"
df_maestra = pd.read_excel(excel_path, sheet_name="BASE_MAESTRA")

# Crear plantilla minimalista
df_plantilla = df_maestra[['DNI', 'CONGRESISTA']].copy()
df_plantilla['VOTO'] = 'PENDIENTE'
df_plantilla['ORALIZADO'] = 'NO'

# Instrucciones en el mismo Excel (opcional, pero mejor en columnas claras)
# Votos válidos: A FAVOR, EN CONTRA, ABSTENCION, NO VOTO, MESA DIRECTIVA, LICENCIA

output_path = "plantilla_importacion.xlsx"
df_plantilla.to_excel(output_path, index=False)

print(f"Plantilla generada en: {output_path}")
