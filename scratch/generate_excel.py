import pandas as pd
import json

# Cargar el dataset completo
with open("congresistas_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# DNIs adicionales encontrados en Otorongo (Batch 2 y 3)
extra_dnis = [
  {"name": "Juárez Gallegos Carmen Patricia", "dni": "07831436"},
  {"name": "Rospigliosi Capurro Fernando Miguel", "dni": "07704730"},
  {"name": "Santisteban Suclupe Magaly", "dni": "41029141"},
  {"name": "Cordero Jon Tay Luis Gustavo", "dni": "15300817"},
  {"name": "Elías Ávalos José Luis", "dni": "21569935"},
  {"name": "Flores Ancachi Jorge Luis", "dni": "00422416"},
  {"name": "García Correa Idelso Manuel", "dni": "04072098"},
  {"name": "Heidinger Ballesteros Nelcy", "dni": "10491661"},
  {"name": "Julon Irigoin Elva Edhit", "dni": "46130369"},
  {"name": "Kamiche Morante Luis Roberto", "dni": "10804834"},
  {"name": "Lizarzaburu Juan Carlos", "dni": "07629631"},
  {"name": "Marticorena Mendoza Jorge Alfonso", "dni": "21456255"},
  {"name": "Quiroz Barboza Segundo Teodomiro", "dni": "27361499"},
  {"name": "Ruíz Rodríguez Magaly Rosmery", "dni": "17849641"},
  {"name": "Arriola Tueros, José Alberto", "dni": "25542661"},
  {"name": "Burgos Oliveros Juan Bartolomé", "dni": "18080185"},
  {"name": "Juárez Calle Heidy Lisbeth", "dni": "42335591"},
  {"name": "Espíritu Cavero Raúl", "dni": "01110116"},
  {"name": "Mita Alanoca Isaac", "dni": "00434972"},
  {"name": "Montalvo Cubas Segundo Toribio", "dni": "16655831"},
  {"name": "Portalatino Ávalos Kelly Roxana", "dni": "42699423"},
  {"name": "Reyes Cam Abel Augusto", "dni": "42377791"},
  {"name": "Rivas Chacara Janet Milagros", "dni": "42589181"},
  {"name": "Bazán Calderón Diego Alonso Fernando", "dni": "46847115"},
  {"name": "Patricia Chirinos Venegas", "dni": "10280036"},
  {"name": "Ciccia Vásquez Miguel Angel", "dni": "06049853"},
  {"name": "Córdova Lobatón María Jessica", "dni": "16719182"},
  {"name": "Herrera Medina Noelia Rossvith", "dni": "42846124"},
  {"name": "Jáuregui Martínez María", "dni": "07852432"},
  {"name": "Medina Minaya Esdras Ricardo", "dni": "29423212"},
  {"name": "Trigozo Reátegui Cheryl", "dni": "44886100"},
  {"name": "Bermejo Rojas Guillermo", "dni": "07638265"},
  {"name": "Coayla Juárez Jorge Samuel", "dni": "04413969"},
  {"name": "Cutipa Ccama Víctor Raúl", "dni": "04647085"},
  {"name": "Echevarría Rodríguez Hamlet", "dni": "27080597"},
  {"name": "Limachi Quispe Nieves Esmeralda", "dni": "41258762"},
  {"name": "Quispe Mamani Wilson Rusbel", "dni": "40706318"},
  {"name": "Sánchez Palomino Roberto Helbert", "dni": "16002918"},
  {"name": "Tacuri Valdivia Germán Adolfo", "dni": "31031443"},
  {"name": "Ugarte Mamani Jhakeline Katy", "dni": "24711696"},
  {"name": "Varas Meléndez Elías Marcial", "dni": "32923902"},
  {"name": "Portero López Hilda Marleny", "dni": "17549232"},
  {"name": "Flores Ramírez Alex Randu", "dni": "46517805"},
  {"name": "Acuña Peralta Segundo Héctor", "dni": "18099367"},
  {"name": "Olivos Martínez Leslie Vivian", "dni": "44144875"}
]

# Actualizar dataset con los DNIs encontrados
dni_map = {d['name']: d['dni'] for d in extra_dnis}
for d in data:
    if d['dni'] == 'PENDIENTE' or d['name'] in dni_map:
        d['dni'] = dni_map.get(d['name'], d['dni'])

# 1. Crear BASE_MAESTRA
df_maestra = pd.DataFrame(data)
df_maestra.columns = ['CONGRESISTA', 'REGIÓN', 'ID_BANCADA', 'BANCADA', 'DNI']

# 2. Crear GRID (23-22-20-20-22-23)
# Dividimos los 130 congresistas en bloques
bloques_sizes = [23, 22, 20, 20, 22, 23]
grid_cols = []
current = 0
for size in bloques_sizes:
    bloque = data[current : current + size]
    # Cada bloque tiene 2 columnas: Nombre y Bancada
    nombres = [b['name'] for b in bloque]
    bancadas = [b['bench_name'] for b in bloque]
    # Rellenar con vacíos si es necesario hasta 23 filas
    nombres += [""] * (23 - size)
    bancadas += [""] * (23 - size)
    grid_cols.append(nombres)
    grid_cols.append(bancadas)
    current += size

# Crear el DataFrame del Grid
grid_data = {}
for i in range(12):
    # Saltamos una columna para separadores visuales si queremos, 
    # pero el backend espera columnas específicas.
    # El backend actual usa: (3,4), (6,7), (9,10), (12,13), (15,16), (18,19)
    # Eso significa que hay columnas vacías entre bloques.
    pass

# Vamos a construir un Excel con la estructura de columnas que el backend espera
final_grid = pd.DataFrame()
# Columnas 0,1,2 vacías? header=2 en backend significa fila 3
for i in range(20): # Columnas A hasta T
    final_grid[i] = [""] * 23

col_pairs = [3, 6, 9, 12, 15, 18]
for i, start_col in enumerate(col_pairs):
    final_grid[start_col] = grid_cols[i*2]
    final_grid[start_col + 1] = grid_cols[i*2 + 1]

# Guardar a Excel
output_path = "../../base_congreso_enriquecida_logos.xlsx"
with pd.ExcelWriter(output_path) as writer:
    df_maestra.to_excel(writer, sheet_name="BASE_MAESTRA", index=False)
    # El backend lee desde la fila 2 (0-indexed) como header? header=2 -> fila 3
    # Así que pondremos el grid empezando en la fila 3
    final_grid.to_excel(writer, sheet_name="Grid", index=False, header=False, startrow=2)

print(f"Archivo generado en: {output_path}")
