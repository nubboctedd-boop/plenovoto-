from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import json
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List

# Configuracion Base
app = FastAPI(title="Verificador de Votos")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
EXCEL_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "base_congreso_enriquecida_logos.xlsx"))

# Servir carpeta estática y fotos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/fotos", StaticFiles(directory=r"C:\Users\sergi\fotos_congresistas_originales"), name="fotos")

import unicodedata
import difflib

def normalizar_nombre(n):
    if not n or pd.isna(n): return ""
    # Normalizar para eliminar acentos y caracteres especiales
    s = unicodedata.normalize('NFKD', str(n))
    s = "".join([c for c in s if not unicodedata.combining(c)])
    # Eliminar comas, puntos y espacios extras
    return s.replace(",", "").replace(".", "").strip().lower()

def get_fotos_map():
    try:
        path = r"C:\Users\sergi\OneDrive\Documentos\programasMIOS\VOTACIONES_CR\fotos.xlsx"
        df = pd.read_excel(path)
        fotos_map = {}
        for _, row in df.iterrows():
            nombre_raw = row['Nombre']
            n_name = normalizar_nombre(nombre_raw)
            full_path = str(row['Ruta_Foto_Original'])
            filename = os.path.basename(full_path)
            fotos_map[n_name] = filename
        return fotos_map
    except Exception as e:
        print(f"Error cargando fotos.xlsx: {e}")
        return {}

FOTOS_MAP = get_fotos_map()

def buscar_foto(nombre_buscado):
    # 1. Coincidencia Exacta Normalizada
    norm_n = normalizar_nombre(nombre_buscado)
    if norm_n in FOTOS_MAP:
        return FOTOS_MAP[norm_n]
    
    # 2. Fallback: Fuzzy matching (Cercanía > 85%)
    possibilities = list(FOTOS_MAP.keys())
    closest = difflib.get_close_matches(norm_n, possibilities, n=1, cutoff=0.85)
    if closest:
        return FOTOS_MAP[closest[0]]
    
    return ""

def generar_graficos_temporales(datos):
    # 1. Mapa de Cuadrantes (Scatter Plot)
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    fig1.patch.set_facecolor('white')
    colors_map = {"VOTA A FAVOR": "#10b981", "EN CONTRA": "#ef4444", "ABSTENCIÓN": "#f59e0b", "PENDIENTE": "#94a3b8"}
    
    for estado, color in colors_map.items():
        votos = [d for d in datos if d.voto_estado == estado]
        if votos:
            x = [ (1 if "CONTRA" in estado or "ABSTENCION" in estado else 3) + (i % 5)*0.1 for i in range(len(votos))]
            y = [ (3 if "FAVOR" in estado or "CONTRA" in estado else 1) + (i // 5)*0.1 for i in range(len(votos))]
            ax1.scatter(x, y, c=color, label=estado, s=40, alpha=0.8, edgecolors='white', linewidth=0.5)

    ax1.set_xlim(0, 4)
    ax1.set_ylim(0, 4)
    ax1.axhline(2, color='#e2e8f0', linewidth=1, linestyle='--')
    ax1.axvline(2, color='#e2e8f0', linewidth=1, linestyle='--')
    ax1.set_title("MAPA CARTESIANO DE POSICIONAMIENTO PARLAMENTARIO", fontsize=10, fontweight='bold', pad=15)
    ax1.axis('off')
    
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig1)
    
    # 2. Distribución (Pie Chart)
    counts = {}
    for d in datos:
        counts[d.voto_estado] = counts.get(d.voto_estado, 0) + 1
    
    labels = list(counts.keys())
    values = list(counts.values())
    colors_list = [colors_map.get(l, "#94a3b8") for l in labels]

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    wedges, texts, autotexts = ax2.pie(values, labels=labels, autopct='%1.1f%%', colors=colors_list, startangle=140, pctdistance=0.85)
    plt.setp(autotexts, size=8, weight="bold", color="white")
    plt.setp(texts, size=8)
    ax2.set_title("PROPORCIÓN FINAL DE VOTACIÓN", fontsize=10, fontweight='bold')
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig2.gca().add_artist(centre_circle)
    
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig2)
    
    return buf1, buf2

@app.post("/api/importar-votos")
async def importar_votos(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        if 'DNI' not in df.columns or 'VOTO' not in df.columns:
            return {"error": "El archivo debe tener las columnas 'DNI' y 'VOTO'"}
        voto_map = {
            "SI": "A FAVOR", "AF": "A FAVOR", "FAVOR": "A FAVOR", "A FAVOR": "A FAVOR",
            "NO": "EN CONTRA", "EC": "EN CONTRA", "CONTRA": "EN CONTRA", "EN CONTRA": "EN CONTRA",
            "ABS": "ABSTENCION", "ABSTENCION": "ABSTENCION", "ABSTENCIÓN": "ABSTENCION",
            "NV": "NO VOTO", "NO VOTO": "NO VOTO",
            "MESA": "MESA DIRECTIVA", "LIC": "LICENCIA"
        }
        resultados = []
        for _, row in df.iterrows():
            dni = str(row['DNI']).strip()
            voto_raw = str(row['VOTO']).strip().upper()
            voto_final = voto_map.get(voto_raw, "PENDIENTE")
            oral = False
            if 'ORALIZADO' in df.columns:
                val_oral = str(row['ORALIZADO']).strip().upper()
                oral = val_oral in ["SI", "SÍ", "TRUE", "X", "1"]
            resultados.append({"dni": dni, "voto": voto_final, "oralizado": oral})
        return {"data": resultados}
    except Exception as e:
        return {"error": str(e)}

class CongresistaVerificado(BaseModel):
    id: str
    dni: str
    nombre: str
    bancada: str
    voto_estado: str
    modificado: bool
    is_empty: bool
    region: str = ""
    oralizado: bool = False
    foto_url: str = ""

@app.get("/")
def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/congresistas")
def get_congresistas():
    try:
        xl = pd.ExcelFile(EXCEL_PATH)
        sheet_name = "Grid" if "Grid" in xl.sheet_names else xl.sheet_names[0]
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None)
        mapping_path = os.path.join(STATIC_DIR, "grid_to_dni.json")
        dni_map = {}
        if os.path.exists(mapping_path):
            with open(mapping_path, "r", encoding="utf-8") as f:
                dni_map = json.load(f)
        df_maestra = pd.read_excel(EXCEL_PATH, sheet_name="BASE_MAESTRA")
        df_maestra['CONGRESISTA'] = df_maestra['CONGRESISTA'].astype(str).str.strip()
        maestra_dict = dict(zip(df_maestra['CONGRESISTA'], df_maestra['DNI']))
        region_dict = dict(zip(df_maestra['CONGRESISTA'], df_maestra['REGIÓN']))
        column_groups = [(3,4), (6,7), (9,10), (12,13), (15,16), (18,19)]
        col_sizes = [23, 22, 20, 20, 22, 23]
        matriz_final = []
        for idx, (n_idx, b_idx) in enumerate(column_groups):
            size = col_sizes[idx]
            for row_offset in range(size):
                row_idx = 2 + row_offset
                try:
                    val_nombre = df.iloc[row_idx, n_idx]
                    val_bancada = df.iloc[row_idx, b_idx]
                    if pd.isna(val_nombre) or str(val_nombre).strip() == "" or str(val_nombre).strip().upper() == "CONGRESISTA":
                        matriz_final.append({"id": f"empty_{row_idx}_{n_idx}", "dni": "0", "nombre": "", "bancada": "", "voto_estado": "", "modificado": False, "is_empty": True, "region": "", "foto_url": ""})
                    else:
                        nombre_str = str(val_nombre).strip()
                        dni_val = str(dni_map.get(nombre_str, maestra_dict.get(nombre_str, "0")))
                        region_val = str(region_dict.get(nombre_str, ""))
                        filename = buscar_foto(nombre_str)
                        foto_url = f"/fotos/{filename}" if filename else ""
                        matriz_final.append({"id": f"c_{row_idx}_{n_idx}", "dni": dni_val, "nombre": nombre_str, "bancada": str(val_bancada).strip(), "voto_estado": "PENDIENTE", "modificado": False, "is_empty": False, "region": region_val, "foto_url": foto_url})
                except Exception:
                    matriz_final.append({"id": f"err_{row_idx}_{n_idx}", "dni": "0", "nombre": "", "bancada": "", "voto_estado": "", "modificado": False, "is_empty": True, "region": "", "foto_url": ""})
        return {"data": matriz_final}
    except Exception as e:
        return {"error": str(e), "data": []}

@app.get("/api/maestra")
def get_maestra():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="BASE_MAESTRA")
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}

class ExportPayload(BaseModel):
    data: List[CongresistaVerificado]
    meta: int
    meta_label: str

@app.post("/api/exportar")
def exportar_resultados(payload: ExportPayload):
    try:
        datos = [d for d in payload.data if not d.is_empty]
        stats = {
            "meta": payload.meta,
            "favor": sum(1 for d in datos if d.voto_estado == "A FAVOR" or d.voto_estado == "MESA DIRECTIVA")
        }
        pdf_filename = os.path.join(SCRIPT_DIR, "Reporte_Final_Sesion.pdf")
        generar_pdf_reporte(datos, stats, pdf_filename)
        if os.name == 'nt': os.startfile(pdf_filename)
        return {"mensaje": "Reportes generados", "pdf": pdf_filename}
    except Exception as e:
        return {"error": str(e)}

def generar_pdf_reporte(datos, stats, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'Times-Bold'
    styles['Title'].fontSize = 18
    styles['Title'].spaceAfter = 20
    styles['Normal'].fontName = 'Times-Roman'
    styles['Normal'].fontSize = 10
    styles['Normal'].alignment = TA_JUSTIFY
    logo_path = os.path.join(STATIC_DIR, "assets", "pcm_logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=450, height=100)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 10))
    story.append(Paragraph("REPORTE ACADÉMICO DE CONVERGENCIA Y VOTACIÓN NOMINAL", styles['Title']))
    story.append(Paragraph("<b>RESUMEN</b>", styles['Normal']))
    story.append(Spacer(1, 5))
    abstract_text = f"El presente reporte técnico sistematiza los resultados de la votación nominal realizada el {datetime.now().strftime('%d/%m/%Y')}. Se analiza el posicionamiento de los 130 congresistas respecto a la meta establecida de {stats['meta']} votos a favor. El documento integra análisis de cuadrantes cartesianos, distribución proporcional por bancadas y el registro individual verificado visualmente mediante retratos oficiales."
    story.append(Paragraph(f"<i>{abstract_text}</i>", styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>I. RESUMEN EJECUTIVO DE RESULTADOS</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    summary_data = [["INDICADOR", "VALOR", "ESTADO"], ["TOTAL VOTOS A FAVOR", str(stats['favor']), "CONSOLIDADOS"], ["META REQUERIDA", str(stats['meta']), "REFERENCIAL"], ["BRECHA / EXCEDENTE", str(stats['favor'] - stats['meta']), "POSITIVO" if stats['favor'] >= stats['meta'] else "NEGATIVO"]]
    sum_table = Table(summary_data, colWidths=[150, 100, 150])
    sum_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Times-Roman'), ('LINEABOVE', (0,0), (-1,0), 1, colors.black), ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(sum_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>II. ANÁLISIS VISUAL DE POSICIONAMIENTO</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    buf1, buf2 = generar_graficos_temporales(datos)
    img1 = Image(buf1, width=220, height=180)
    img2 = Image(buf2, width=220, height=150)
    chart_table = Table([[img1, img2]], colWidths=[250, 250])
    story.append(chart_table)
    story.append(Paragraph("<font size=8><i>Figura 1. Mapa de dispersión (izq.) y Proporción acumulada de votos (der.). Elaboración propia.</i></font>", styles['Normal']))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>III. COMPOSICIÓN Y CONVERGENCIA POR BANCADA</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    bench_stats = {}
    for d in datos:
        if d.bancada not in bench_stats: bench_stats[d.bancada] = {"TOTAL": 0, "FAVOR": 0, "CONTRA": 0}
        bench_stats[d.bancada]["TOTAL"] += 1
        if d.voto_estado == "A FAVOR": bench_stats[d.bancada]["FAVOR"] += 1
        elif d.voto_estado == "EN CONTRA": bench_stats[d.bancada]["CONTRA"] += 1
    bench_data = [["BANCADA", "TOTAL", "FAVOR", "CONTRA", "% APOYO"]]
    for b, s in bench_stats.items(): bench_data.append([b, s["TOTAL"], s["FAVOR"], s["CONTRA"], f"{(s['FAVOR']/s['TOTAL']*100):.1f}%"])
    b_table = Table(bench_data, colWidths=[100, 70, 70, 70, 80])
    b_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Times-Roman'), ('LINEABOVE', (0,0), (-1,0), 1, colors.black), ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(b_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>IV. CONCLUSIONES</b>", styles['Normal']))
    story.append(Spacer(1, 5))
    resultado_str = "exitoso" if stats['favor'] >= stats['meta'] else "insuficiente"
    conclu_text = f"En conclusión, el proceso de votación analizado refleja un despliegue {resultado_str} de voluntades parlamentarias. Se observa que la bancada con mayor cohesión al voto a favor representa un motor crítico para alcanzar la meta de {stats['meta']} votos. Los datos visualizados en el mapa cartesiano confirman una tendencia de agrupamiento que facilita la toma de decisiones institucionales."
    story.append(Paragraph(conclu_text, styles['Normal']))
    story.append(Spacer(1, 30))
    story.append(PageBreak())
    story.append(Paragraph("<b>V. ANEXO: DETALLE NOMINAL INDIVIDUAL CON REGISTRO FOTOGRÁFICO</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    table_data = [["FOTO", "CONGRESISTA", "BANCADA", "REGION", "VOTO"]]
    datos_ordenados = sorted(datos, key=lambda x: (x.bancada, x.nombre))
    for d in datos_ordenados:
        img_cell = "-"
        filename = buscar_foto(d.nombre)
        if filename:
            full_path = os.path.join(r"C:\Users\sergi\fotos_congresistas_originales", filename)
            if os.path.exists(full_path): img_cell = Image(full_path, width=20, height=25)
        table_data.append([img_cell, d.nombre.upper(), d.bancada, d.region[:15].upper(), d.voto_estado])
    main_table = Table(table_data, colWidths=[35, 180, 80, 80, 90], repeatRows=1)
    main_table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Times-Roman'), ('FONTSIZE', (0,0), (-1,-1), 8), ('LINEABOVE', (0,0), (-1,0), 1, colors.black), ('LINEBELOW', (0,0), (-1,0), 0.5, colors.black), ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (0,-1), 'CENTER'), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke])]))
    story.append(main_table)
    doc.build(story)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
