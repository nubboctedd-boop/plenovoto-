from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pandas as pd
import json
import os
import io
import secrets
import matplotlib
matplotlib.use('Agg') # Importante para servidores sin GUI
import matplotlib.pyplot as plt
from datetime import datetime
from pydantic import BaseModel
from typing import List

# Importaciones para PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

# Configuracion Base
app = FastAPI(title="PlenoVoto - Sistema Institucional")
security = HTTPBasic(auto_error=False)

# CONFIGURACIÓN DE ACCESO
# Cambia a True para que cualquiera use la web, o False para pedir contraseña.
MODO_PUBLICO = True

# Credenciales Solicitadas (solo activas si MODO_PUBLICO = False)
USER_SECURE = "maythe"
PASS_SECURE = "0903"

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    # Si el modo público está activo, retornamos un usuario genérico sin verificar nada
    if MODO_PUBLICO:
        return "Invitado"
    
    # Si no es público, verificamos las credenciales
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso no autorizado",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    current_user_bytes = credentials.username.encode("utf8")
    correct_user_bytes = USER_SECURE.encode("utf8")
    is_correct_username = secrets.compare_digest(current_user_bytes, correct_user_bytes)
    
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = PASS_SECURE.encode("utf8")
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SCRIPT_DIR, "static")
# Rutas Relativas para Despliegue
EXCEL_PATH = os.path.join(SCRIPT_DIR, "base_congresistas.xlsx")
FOTOS_DIR = os.path.join(STATIC_DIR, "fotos")

# Servir carpeta estática y fotos (Relative)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/fotos", StaticFiles(directory=FOTOS_DIR), name="fotos")

import unicodedata
import difflib

def normalizar_nombre(n):
    if not n or pd.isna(n): return ""
    # Normalizar para eliminar acentos y caracteres especiales
    s = unicodedata.normalize('NFKD', str(n))
    s = "".join([c for c in s if not unicodedata.combining(c)])
    # Eliminar comas, puntos, guiones y espacios extras
    s = s.replace(",", "").replace(".", "").replace("_", " ").replace("-", " ")
    # Remover caracteres no alfanuméricos (manteniendo espacios)
    import re
    s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
    return " ".join(s.split()).lower()

def get_fotos_map():
    # Mapear archivos físicos a sus nombres normalizados
    archivos_fisicos = {}
    if os.path.exists(FOTOS_DIR):
        for f in os.listdir(FOTOS_DIR):
            if f.lower().endswith('.jpg'):
                archivos_fisicos[normalizar_nombre(f.replace('.jpg', ''))] = f

    try:
        path = os.path.join(SCRIPT_DIR, "fotos.xlsx")
        df = pd.read_excel(path)
        fotos_map = {}
        for _, row in df.iterrows():
            nombre_raw = row['Nombre']
            n_name = normalizar_nombre(nombre_raw)
            
            # Intentar encontrar el archivo físico más parecido
            possibilities = list(archivos_fisicos.keys())
            closest = difflib.get_close_matches(n_name, possibilities, n=1, cutoff=0.7)
            if closest:
                fotos_map[n_name] = archivos_fisicos[closest[0]]
            else:
                # Fallback: usar el nombre del Excel si existe el archivo con ese nombre exacto
                filename = os.path.basename(str(row['Ruta_Foto_Original']))
                if os.path.exists(os.path.join(FOTOS_DIR, filename)):
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
    # Definir paleta institucional PCM
    colors_map = {
        "A FAVOR": "#10b981", 
        "EN CONTRA": "#ef4444", 
        "ABSTENCION": "#f59e0b", 
        "PENDIENTE": "#94a3b8",
        "MESA DIRECTIVA": "#3b82f6",
        "LICENCIA": "#6366f1",
        "NO VOTO": "#475569"
    }
    
    # 1. ELIMINADO (Polarización y Cohesión)
    
    # 2. Distribución Proporcional (Doughnut Chart)
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
    ax2.set_title("CONSOLIDADO PROPORCIONAL DE VOTACIÓN", fontsize=10, fontweight='bold')
    ax2.text(0.5, -0.15, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax2.transAxes, ha='center', fontsize=7, style='italic') # Aumentado margen inferior
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig2.gca().add_artist(centre_circle)
    
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig2)

    # 3. Gráfico Regional (BARRAS HORIZONTALES - % DE APOYO POR REGIÓN)
    reg_stats = {}
    for d in datos:
        reg = d.region.upper() if d.region else "N.A."
        if reg not in reg_stats:
            reg_stats[reg] = {"TOTAL": 0, "FAVOR": 0}
        reg_stats[reg]["TOTAL"] += 1
        if d.voto_estado == "A FAVOR":
            reg_stats[reg]["FAVOR"] += 1
            
    names = []
    vals = []
    for reg, s in reg_stats.items():
        names.append(reg)
        pct = (s["FAVOR"] / s["TOTAL"] * 100) if s["TOTAL"] > 0 else 0
        vals.append(pct)
            
    # Ordenar por porcentaje
    sorted_data = sorted(zip(names, vals), key=lambda x: x[1], reverse=False)
    names = [x[0] for x in sorted_data]
    vals = [x[1] for x in sorted_data]

    fig3, ax3 = plt.subplots(figsize=(7, 8))
    bars = ax3.barh(names, vals, color='#10b981', alpha=0.8)
    ax3.set_title("APOYO POR REGIÓN (% VOTOS A FAVOR)", fontsize=10, fontweight='bold')
    ax3.text(0.5, -0.05, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax3.transAxes, ha='center', fontsize=7, style='italic')
    ax3.set_xlim(0, 110) # Espacio para la etiqueta
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax3.spines['bottom'].set_visible(False)
    
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 2, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', va='center', fontsize=8, fontweight='bold')

    buf3 = io.BytesIO()
    fig3.savefig(buf3, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig3)
    
    # 4. Gráfico Índice de Rice (BARRAS)
    rice_data = {}
    for d in datos:
        if getattr(d, 'is_empty', False): continue
        b = getattr(d, 'bancada', "N.A.") or "N.A."
        if b not in rice_data:
            rice_data[b] = {"A FAVOR": 0, "EN CONTRA": 0}
        if getattr(d, 'voto_estado', '') == "A FAVOR":
            rice_data[b]["A FAVOR"] += 1
        elif getattr(d, 'voto_estado', '') == "EN CONTRA":
            rice_data[b]["EN CONTRA"] += 1
    
    rice_indices = []
    for b, counts in rice_data.items():
        total = counts["A FAVOR"] + counts["EN CONTRA"]
        if total > 0:
            idx_val = abs(counts["A FAVOR"] - counts["EN CONTRA"]) / total
            rice_indices.append((b, idx_val))
    
    # Ordenar para que el gráfico se dibuje decentemente
    rice_indices.sort(key=lambda x: x[1], reverse=False)
    
    buf4 = None
    if rice_indices:
        fig4, ax4 = plt.subplots(figsize=(7, 5))
        names_r = [x[0] for x in rice_indices]
        vals_r = [x[1] for x in rice_indices]
        ax4.barh(names_r, vals_r, color='#3b82f6', alpha=0.8)
        ax4.set_title("ÍNDICE DE RICE (COHESIÓN PARTIDARIA)", fontsize=10, fontweight='bold')
        ax4.set_xlabel("Índice de Rice (0 = Dividido, 1 = Cohesionado)")
        ax4.text(0.5, -0.15, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax4.transAxes, ha='center', fontsize=7, style='italic')
        ax4.spines['right'].set_visible(False)
        ax4.spines['top'].set_visible(False)
        buf4 = io.BytesIO()
        fig4.savefig(buf4, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
        plt.close(fig4)

    # 5. Termómetro Político (Gauge / Barra Horizontal de apoyo total)
    favor = sum(1 for d in datos if getattr(d, 'voto_estado', '') == 'A FAVOR')
    total = sum(1 for d in datos if getattr(d, 'voto_estado', '') in ['A FAVOR', 'EN CONTRA', 'ABSTENCION'])
    pct = (favor / total * 100) if total > 0 else 0
    fig5, ax5 = plt.subplots(figsize=(6, 1.5))
    ax5.barh(["Apoyo Relativo"], [100], color='lightgray')
    ax5.barh(["Apoyo Relativo"], [pct], color='#ef4444' if pct < 50 else '#10b981')
    ax5.axvline(50, color='black', linestyle='--', linewidth=2)
    ax5.set_title("TERMÓMETRO POLÍTICO (% A FAVOR DE VOTOS VÁLIDOS)", fontsize=10, fontweight='bold')
    for spine in ax5.spines.values(): spine.set_visible(False)
    ax5.set_yticks([])
    ax5.text(0.5, -0.5, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax5.transAxes, ha='center', fontsize=7, style='italic')
    buf5 = io.BytesIO()
    fig5.savefig(buf5, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig5)

    # 6. Perfil de Bancada (Stacked horizontal bar 100%)
    bancada_counts = {}
    for d in datos:
        if getattr(d, 'is_empty', False): continue
        b = getattr(d, 'bancada', 'N.A.') or 'N.A.'
        if b not in bancada_counts: bancada_counts[b] = {"A FAVOR": 0, "EN CONTRA": 0, "ABSTENCION": 0}
        v = getattr(d, 'voto_estado', '')
        if v in bancada_counts[b]: bancada_counts[b][v] += 1
    
    b_names = []
    f_pct = []
    c_pct = []
    a_pct = []
    for b, c in bancada_counts.items():
        t = c["A FAVOR"] + c["EN CONTRA"] + c["ABSTENCION"]
        if t > 0:
            b_names.append(b)
            f_pct.append(c["A FAVOR"]/t*100)
            c_pct.append(c["EN CONTRA"]/t*100)
            a_pct.append(c["ABSTENCION"]/t*100)
    
    fig6, ax6 = plt.subplots(figsize=(7, 5))
    if b_names:
        ax6.barh(b_names, f_pct, color='#10b981', label='A Favor')
        ax6.barh(b_names, c_pct, left=f_pct, color='#ef4444', label='En Contra')
        left_a = [f+c for f, c in zip(f_pct, c_pct)]
        ax6.barh(b_names, a_pct, left=left_a, color='#f59e0b', label='Abstención')
    ax6.set_title("PERFIL IDEOLÓGICO DE BANCADAS", fontsize=10, fontweight='bold')
    ax6.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8)
    ax6.text(0.5, -0.3, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax6.transAxes, ha='center', fontsize=7, style='italic')
    for s in ax6.spines.values(): s.set_visible(False)
    buf6 = io.BytesIO()
    fig6.savefig(buf6, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig6)

    # 7. Matriz de Calor de Votos
    import seaborn as sns
    import numpy as np

    heatmap_data = {}
    for d in datos:
        if getattr(d, 'is_empty', False): continue
        b = getattr(d, 'bancada', 'N.A.') or 'N.A.'
        if b not in heatmap_data: 
            heatmap_data[b] = {"A FAVOR": 0, "EN CONTRA": 0, "ABSTENCION": 0, "NO VOTO": 0}
        v = getattr(d, 'voto_estado', '').upper()
        if v == "A FAVOR": heatmap_data[b]["A FAVOR"] += 1
        elif v == "EN CONTRA": heatmap_data[b]["EN CONTRA"] += 1
        elif v == "ABSTENCION": heatmap_data[b]["ABSTENCION"] += 1
        else: heatmap_data[b]["NO VOTO"] += 1
        
    b_names_hm = sorted(list(heatmap_data.keys()))
    cols_hm = ["A FAVOR", "EN CONTRA", "ABSTENCION", "NO VOTO"]
    matrix = []
    for b in b_names_hm:
        matrix.append([heatmap_data[b][c] for c in cols_hm])
        
    fig7, ax7 = plt.subplots(figsize=(8, 6))
    if matrix:
        # cmap "PuBu" para un look premium e institucional  
        sns.heatmap(matrix, annot=True, fmt="d", cmap="PuBu", xticklabels=cols_hm, yticklabels=b_names_hm, cbar=True, ax=ax7)
    
    ax7.set_title("MAPA DE CALOR: CONCENTRACIÓN DE VOTOS POR BANCADA", fontsize=10, fontweight='bold')
    ax7.text(0.5, -0.2, "Fuente: Sistema PlenoVoto Institucional. Elaboración propia.", transform=ax7.transAxes, ha='center', fontsize=7, style='italic')
    
    buf7 = io.BytesIO()
    fig7.savefig(buf7, format='png', dpi=300, bbox_inches='tight', pad_inches=0.3)
    plt.close(fig7)

    # 8. ELIMINADO: Boxplot de Dispersión
    buf8 = None

    return buf2, buf3, buf4, buf5, buf6, buf7, buf8

# Lógica de importación movida abajo con seguridad

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

# Los endpoints se definen abajo con seguridad integrada

# La lógica de carga de congresistas se movió al endpoint protegido al final del archivo

# La ruta /api/maestra se movió al bloque final para mayor orden

class ExportPayload(BaseModel):
    data: List[CongresistaVerificado]
    meta: int
    meta_label: str

# Lógica de exportación movida abajo con seguridad

def generar_pdf_reporte(datos, stats, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].fontSize = 16
    styles['Title'].spaceAfter = 15
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14  # Aumentamos el interlineado para evitar la sensación de 'letra achatada'
    styles['Normal'].alignment = TA_JUSTIFY

    logo_path = os.path.join(STATIC_DIR, "assets", "pcm_logo.png")
    if os.path.exists(logo_path):
        # Image(filename, width=None, height=None, kind='proportional', mask=None, lazy=1)
        logo = Image(logo_path, width=180, height=50) # Removido preserveAspectRatio (parámetro no válido en ReportLab platypus.Image)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 20))

    time_now = datetime.now().strftime('%H:%M:%S')
    story.append(Paragraph(f"REPORTE OFICIAL DE VOTACIÓN NOMINAL Y POSICIONAMIENTO [{time_now}]", styles['Title']))
    
    story.append(Paragraph("<b>I. RESUMEN TÉCNICO</b>", styles['Normal']))
    story.append(Spacer(1, 5))
    fech_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    intro_text = f"El presente documento detalla el escrutinio verificado de la sesión parlamentaria del {fech_str}. El análisis integra la meta legal de {stats['meta']} votos y desglosa el comportamiento de los 130 representantes mediante métricas de convergencia, dispersión cartográfica regional y registro individualizado."
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 15))

    summary_data = [
        ["INDICADOR ESTRATÉGICO", "CANTIDAD", "ESTADO RESULTANTE"],
        ["TOTAL VOTOS A FAVOR", str(stats['favor']), "CONSOLIDADOS"],
        ["QUÓRUM REQUERIDO (META)", str(stats['meta']), "ESTÁNDAR"],
        ["DIFERENCIA (BRECHA)", str(stats['favor'] - stats['meta']), "ALCANZADA" if stats['favor'] >= stats['meta'] else "PENDIENTE"]
    ]
    sum_table = Table(summary_data, colWidths=[200, 100, 150])
    sum_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>II. ANÁLISIS DE POSICIONAMIENTO</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    buf2, buf3, buf4, buf5, buf6, buf7, buf8 = generar_graficos_temporales(datos)
    img2 = Image(buf2, width=350, height=250)
    img2.hAlign = 'CENTER'
    story.append(img2)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>III. DISTRIBUCIÓN DE APOYO REGIONAL (TODAS LAS REGIONES)</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    img3 = Image(buf3, width=450, height=520)
    img3.hAlign = 'CENTER'
    story.append(img3)
    story.append(PageBreak())

    # Índice de Rice
    if buf4:
        story.append(Paragraph("<b>IV. ÍNDICE DE RICE (COHESIÓN PARTIDARIA)</b>", styles['Normal']))
        story.append(Spacer(1, 10))
        img4 = Image(buf4, width=450, height=350)
        img4.hAlign = 'CENTER'
        story.append(img4)
        story.append(Spacer(1, 10))
        story.append(Paragraph("El Índice de Rice ilustra qué tan cohesionadas votaron las bancadas. Valores cercanos a 1 indican alta cohesión interna, mientras que valores bajos muestran posiciones divididas.", styles['Normal']))
        story.append(PageBreak())

    # Gráficos Dinámicos
    story.append(Paragraph("<b>V. ANÁLISIS POLÍTICO Y DISPERSIÓN</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    
    dinamicos = [
        (buf5, "Termómetro Político", "Medición de intensidad y margen de apoyo general en el legislativo.", 350, 100),
        (buf6, "Perfil de Bancada", "Distribución proporcional del voto interno de los grupos parlamentarios.", 350, 250),
        (buf7, "Mapa de Calor de Votos", "Concentración y densidad de los tipos de voto por cada bancada, agrupando inasistencias y licencias.", 350, 280)
    ]
    
    for bufX, title, desc, w, h in dinamicos:
        if bufX:
            story.append(Paragraph(f"<b>{title}</b>", styles['Normal']))
            story.append(Spacer(1, 5))
            img_dyn = Image(bufX, width=w, height=h)
            img_dyn.hAlign = 'CENTER'
            story.append(img_dyn)
            story.append(Spacer(1, 5))
            story.append(Paragraph(desc, styles['Normal']))
            story.append(Spacer(1, 20))
            
    story.append(PageBreak())

    story.append(Paragraph("<b>VI. ANEXO: RESUMEN CONSOLIDADO POR BANCADA</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    
    bench_stats = {}
    for d in datos:
        b = d.bancada or "N.A."
        if b not in bench_stats: bench_stats[b] = {"TOTAL": 0, "FAVOR": 0, "CONTRA": 0, "ABS": 0, "NV": 0}
        bench_stats[b]["TOTAL"] += 1
        if d.voto_estado == "A FAVOR": bench_stats[b]["FAVOR"] += 1
        elif d.voto_estado == "EN CONTRA": bench_stats[b]["CONTRA"] += 1
        elif d.voto_estado == "ABSTENCION": bench_stats[b]["ABS"] += 1
        else: bench_stats[b]["NV"] += 1

    def style_cell(val):
        if val > 0: return Paragraph(f"<b>{val}</b>", styles['Normal'])
        return Paragraph(f"<font color='#cbd5e1'>{val}</font>", styles['Normal'])

    bench_data = [["BANCADA", "A FAVOR", "EN CONTRA", "ABS.", "NO VOTO", "TOTAL"]]
    for b in sorted(bench_stats.keys()):
        s = bench_stats[b]
        bench_data.append([
            b, 
            style_cell(s["FAVOR"]), 
            style_cell(s["CONTRA"]), 
            style_cell(s["ABS"]), 
            style_cell(s["NV"]),
            style_cell(s["TOTAL"])
        ])

    b_table = Table(bench_data, colWidths=[110, 70, 70, 70, 70, 70])
    b_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke])
    ]))
    story.append(b_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>VII. ANEXO: LISTADO NOMINAL VERIFICADO</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    
    table_data = [["FOTO", "CONGRESISTA", "BANCADA", "REGION", "VOTO"]]
    pdf_colors = {
        "A FAVOR": colors.HexColor("#dcfce7"), 
        "EN CONTRA": colors.HexColor("#fee2e2"), 
        "ABSTENCION": colors.HexColor("#fef3c7"), 
        "NO VOTO": colors.HexColor("#f1f5f9"),
        "LICENCIA": colors.HexColor("#f1f5f9"),
        "MESA DIRECTIVA": colors.HexColor("#f1f5f9"),
        "PENDIENTE": colors.white
    }

    datos_ordenados = sorted(datos, key=lambda x: (x.bancada, x.nombre))
    for i, d in enumerate(datos_ordenados):
        img_cell = "-"
        filename = buscar_foto(d.nombre)
        if filename:
            full_path = os.path.join(FOTOS_DIR, filename)
            if os.path.exists(full_path): img_cell = Image(full_path, width=18, height=22)
        
        nombre_display = d.nombre.upper()
        if getattr(d, 'oralizado', False):
            nombre_display += "*"

        table_data.append([img_cell, nombre_display, d.bancada, d.region[:15].upper(), d.voto_estado])

    main_table = Table(table_data, colWidths=[35, 180, 70, 90, 85], repeatRows=1)
    main_style = [
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.3, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ]
    
    for row_idx, d in enumerate(datos_ordenados, 1):
        color = pdf_colors.get(d.voto_estado, colors.white)
        main_style.append(('BACKGROUND', (4, row_idx), (4, row_idx), color))
        if d.voto_estado == "A FAVOR":
            main_style.append(('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.HexColor("#166534")))

    main_table.setStyle(TableStyle(main_style))
    story.append(main_table)
    
    story.append(Spacer(1, 20))
    footer_text = "(*) El asterisco indica que el voto fue emitido de manera oral durante la sesión.<br/>Fuente: Sistema PlenoVoto Institucional. Elaboración propia. | Verificación Institucional v2.5 (300 DPI)"
    story.append(Paragraph(f"<font size=7 color='#94a3b8'>{footer_text}</font>", styles['Normal']))
    
    doc.build(story)

@app.get("/", response_class=HTMLResponse)
async def read_root(user: str = Depends(get_current_user)):
    # Nota: get_current_user ahora respeta la variable MODO_PUBLICO
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Aplicar seguridad a todos los endpoints de API
@app.get("/api/congresistas")
async def get_congresistas(user: str = Depends(get_current_user)):
    try:
        xl = pd.ExcelFile(EXCEL_PATH)
        sheet = "BASE_MAESTRA" if "BASE_MAESTRA" in xl.sheet_names else xl.sheet_names[0]
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
        df.columns = [str(c).upper().strip() for c in df.columns]
        
        col_c = 'CONGRESISTA' if 'CONGRESISTA' in df.columns else df.columns[0]
        matriz_final = []
        
        for i, row in df.iterrows():
            if len(matriz_final) >= 130: break
            raw_nom = str(row[col_c]).replace('\uFFFD', 'I').strip()
            if not raw_nom or raw_nom.upper() == "CONGRESISTA" or raw_nom.lower() == "nan": continue
            
            filename = buscar_foto(raw_nom)
            foto_url = f"/fotos/{filename}" if filename else ""
            
            matriz_final.append({
                "id": f"c_{len(matriz_final)}",
                "dni": str(row.get('DNI', '0')),
                "nombre": raw_nom,
                "bancada": str(row.get('BANCADA', 'N.A.')),
                "voto_estado": "PENDIENTE",
                "modificado": False,
                "is_empty": False,
                "region": str(row.get('REGIÓN', '')),
                "foto_url": foto_url
            })
            
        while len(matriz_final) < 130:
            matriz_final.append({
                "id": f"empty_{len(matriz_final)}", 
                "dni": "0", "nombre": "", "bancada": "", 
                "voto_estado": "", "modificado": False, 
                "is_empty": True, "region": "", "foto_url": ""
            })
            
        return {"data": matriz_final}
    except Exception as e:
        return {"error": str(e), "data": []}

@app.get("/api/maestra")
def get_maestra(user: str = Depends(get_current_user)):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="BASE_MAESTRA")
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/importar-votos")
async def importar_votos(file: UploadFile = File(...), user: str = Depends(get_current_user)):
    try:
        df = pd.read_excel(file.file)
        df.columns = [str(c).strip().upper() for c in df.columns]
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

@app.post("/api/exportar")
def exportar_resultados(payload: ExportPayload, user: str = Depends(get_current_user)):
    try:
        # Limpieza de archivo antiguo para evitar confusiones
        old_pdf = os.path.join(SCRIPT_DIR, "Reporte_Final_Sesion.pdf")
        if os.path.exists(old_pdf):
            try: os.remove(old_pdf)
            except: pass

        datos = [d for d in payload.data if not d.is_empty]
        stats = {
            "meta": payload.meta,
            "favor": sum(1 for d in datos if d.voto_estado == "A FAVOR")
        }
        
        # Nombre con Hora de Descarga para el usuario
        hora_str = datetime.now().strftime("%H-%M-%S")
        filename = f"Reporte_PlenoVoto_{hora_str}.pdf"
        pdf_path = os.path.join(SCRIPT_DIR, filename)
        
        print(f"DEBUG: Generando PDF en {pdf_path}")
        generar_pdf_reporte(datos, stats, pdf_path)
        
        return FileResponse(
            path=pdf_path, 
            filename=filename, 
            media_type='application/pdf'
        )
    except Exception as e:
        print(f"ERROR EXPORTAR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 4000))
    # Activamos reload=True para que el servidor detecte cambios automáticamente
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
