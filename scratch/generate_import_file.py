import pandas as pd
from thefuzz import process, fuzz
import os

# Rutas
BASE_MAESTRA_PATH = r'c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\base_congreso_enriquecida_logos.xlsx'
USER_EXCEL_PATH = r'C:\Users\sergi\Downloads\PROYECCIÓN INVESTIDURA - VERSION FINAL - GABINETE ARROYO.xlsx'
OUTPUT_PATH = r'c:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\verificador_votos\scratch\VOTACION_GABINETE_ARROYO_PROYECTADA.xlsx'

def normalizar_voto(val):
    val = str(val).strip().upper()
    if any(x in val for x in ["A FAVOR", "SI", "SI VOTA", "ASISTIÓ", "ASISTIO", "FAVOR"]):
        return "A FAVOR"
    if any(x in val for x in ["EN CONTRA", "NO", "RECHAZO", "CONTRA"]):
        return "EN CONTRA"
    if any(x in val for x in ["ABSTENCION", "ABSTENCIÓN", "ABS"]):
        return "ABSTENCION"
    return "PENDIENTE"

def main():
    print("Cargando Base Maestra...")
    df_maestra = pd.read_excel(BASE_MAESTRA_PATH, sheet_name='BASE_MAESTRA')
    congresistas = df_maestra['CONGRESISTA'].tolist()
    dnis = df_maestra['DNI'].tolist()
    dni_map = dict(zip(congresistas, dnis))
    
    # Lista de resultados finales
    final_votes = {str(dni): {"voto": "PENDIENTE", "oralizado": "NO"} for dni in dnis}

    print("Cargando Proyección del Usuario...")
    xl = pd.ExcelFile(USER_EXCEL_PATH)
    
    # Recorrer todas las hojas para buscar votos
    for sheet in xl.sheet_names:
        print(f"Buscando en hoja: {sheet}")
        df = pd.read_excel(USER_EXCEL_PATH, sheet_name=sheet)
        
        # Convertir todo a string para búsqueda fácil
        df_str = df.astype(str)
        
        for idx, row in df_str.iterrows():
            row_list = row.tolist()
            for cell_idx, cell_val in enumerate(row_list):
                # Si el valor de la celda parece un nombre de congresista
                if len(cell_val) > 10: 
                    match, score = process.extractOne(cell_val, congresistas, scorer=fuzz.token_sort_ratio)
                    if score > 85:
                        dni = str(dni_map[match])
                        
                        # Buscar voto en celdas adyacentes (izquierda o derecha)
                        # Comprobamos celdas cercanas (dentro de un rango de 5)
                        potential_votes = []
                        start = max(0, cell_idx - 5)
                        end = min(len(row_list), cell_idx + 5)
                        
                        for i in range(start, end):
                            if i != cell_idx:
                                v = normalizar_voto(row_list[i])
                                if v != "PENDIENTE":
                                    potential_votes.append(v)
                        
                        if potential_votes:
                            final_votes[dni]["voto"] = potential_votes[0] # Tomamos el primero encontrado

    # Generar DataFrame final
    output_data = []
    for dni, info in final_votes.items():
        output_data.append({
            "DNI": dni,
            "VOTO": info["voto"],
            "ORALIZADO": info["oralizado"]
        })
    
    df_final = pd.DataFrame(output_data)
    df_final.to_excel(OUTPUT_PATH, index=False)
    print(f"Archivo generado con éxito: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
