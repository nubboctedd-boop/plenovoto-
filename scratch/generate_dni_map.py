import pandas as pd
import unidecode
import json

def normalize(s):
    return unidecode.unidecode(str(s).upper().strip())

df_cong = pd.read_excel('../base_congreso_enriquecida_logos.xlsx')
d_cong = df_cong.iloc[2:, [22, 23]].dropna().reset_index(drop=True)
d_cong.columns = ['ID', 'CONGRESISTA']
d_cong['CONGRESISTA_normalized'] = d_cong['CONGRESISTA'].astype(str).str.strip().str.upper()

d_maestra = pd.read_excel('../base_congreso_enriquecida_logos.xlsx', sheet_name='BASE_MAESTRA')
d_maestra['NOMBRE_COMPLETO_normalized'] = d_maestra['NOMBRE_COMPLETO'].astype(str).str.strip().str.upper()
d_maestra.loc[d_maestra['NOMBRE_COMPLETO_normalized'] == 'ROJAS LAURA JUDITH', 'NOMBRE_COMPLETO_normalized'] = 'LAURA ROJAS JUDITH'

merged = pd.merge(d_cong, d_maestra[['NOMBRE_COMPLETO_normalized', 'ID']], left_on='CONGRESISTA_normalized', right_on='NOMBRE_COMPLETO_normalized', how='left')
merged = merged.rename(columns={'ID_y': 'DNI', 'ID_x': 'numero_orden'})
dict_cong = dict(zip(merged['CONGRESISTA_normalized'], merged['DNI']))

df_header2 = pd.read_excel('../base_congreso_enriquecida_logos.xlsx', header=2)
column_groups = [(3,4), (6,7), (9,10), (12,13), (15,16), (18,19)]

grid_to_dni = {}
for row_idx in range(23):
    for n_idx, b_idx in column_groups:
        val_nombre = df_header2.iloc[row_idx, n_idx]
        if pd.notna(val_nombre) and str(val_nombre).strip() != '':
            g = str(val_nombre).strip()
            g_norm = normalize(g).replace('.', '').replace(',', '')
            g_parts = g_norm.split()
            
            best_match = None
            for idx, r in merged.iterrows():
                f_norm = normalize(r['CONGRESISTA_normalized'])
                f_parts = f_norm.split()
                if len(f_parts) >= 3 and len(g_parts) >= 3:
                     if f_parts[0] == g_parts[0] and f_parts[1].startswith(g_parts[1]) and f_parts[2].startswith(g_parts[2]):
                         best_match = r['DNI']
                         break
                elif len(f_parts) >= 2 and len(g_parts) >= 2:
                     if f_parts[0] == g_parts[0] and f_parts[1].startswith(g_parts[1]):
                         best_match = r['DNI']
                elif len(f_parts) >= 1 and len(g_parts) >= 1:
                     if f_parts[0] == g_parts[0]:
                         best_match = r['DNI']
            if best_match:
                grid_to_dni[g] = best_match

grid_to_dni['CORDERO J., L.'] = dict_cong.get('CORDERO JON TAY LUIS GUSTAVO')
grid_to_dni['ALEGRA G., A.'] = dict_cong.get('ALEGRA GARCA LUIS ARTURO')
grid_to_dni['TRIGOZO C., R.'] = dict_cong.get('TRIGOZO RETEGUI CHERYL')
grid_to_dni['ZEA O., O.'] = dict_cong.get('ZEA CHOQUECHAMBI OSCAR')
grid_to_dni['JULN J., E.'] = dict_cong.get('JULON IRIGOIN ELVA EDHIT')
grid_to_dni['LIZARZABURU L., J.'] = dict_cong.get('LIZARZABURU JUAN CARLOS ')
grid_to_dni['ALVA C., C.'] = dict_cong.get('ALVA ROJAS CARLOS ENRIQUE') # Or Cavero Alva? wait. Cavero Alva is CAVERO A., A. So Alva C is Alva Rojas Carlos Enrique. Alva P is Alva Prieto Maria
grid_to_dni['ECHAIZ D., G.'] = dict_cong.get('ECHAZ RAMOS VDA DE NUEZ, GLADYS MARGOT')
grid_to_dni['ECHEVERRA R., H.'] = dict_cong.get('ECHEVARRA RODRGUEZ HAMLET')
grid_to_dni['QUIROZ B.,S.'] = dict_cong.get('QUIROZ BARBOZA SEGUNDO TEODOMIRO')
grid_to_dni['BAZN D., C.'] = dict_cong.get('BAZN CALDERN DIEGO ALONSO FERNANDO')
grid_to_dni['ANDERSON R., C.'] = 120 # Actually we will see if we can find it
grid_to_dni['OLIVOS M., V.'] = dict_cong.get('OLIVOS MARTNEZ LESLIE VIVIAN')

print(json.dumps(grid_to_dni, indent=2))
