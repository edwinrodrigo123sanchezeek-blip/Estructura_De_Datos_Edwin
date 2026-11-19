import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fractions import Fraction
from itertools import combinations
from PIL import Image
from fpdf import FPDF
import json
import os
import tempfile
from google import genai
from google.genai import types

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="Aventura Lineal: Programación Lineal Paso a Paso + Escáner + PDF",
    page_icon="🧭",
    layout="wide"
)

st.markdown("""
<style>
    .kid-box {
        background-color: #f0f8ff;
        border-left: 6px solid #2b8cbe;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #1a2530;
    }
    .step-header {
        background-color: #e8f5e9;
        border-left: 6px solid #2e7d32;
        padding: 10px 15px;
        border-radius: 6px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1b5e20;
    }
    .warn-box {
        background-color: #fff3e0;
        border-left: 6px solid #ef6c00;
        padding: 15px;
        border-radius: 8px;
        color: #3e2723;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# UTILIDADES DE FRACCIONES Y FORMATO
# ==============================================================================
def to_frac(val):
    return Fraction(str(val)).limit_denominator(10000)

def fmt_f(val):
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"{val.numerator}/{val.denominator}"
    return str(val)

def fmt_latex_f(val):
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        if val.numerator < 0:
            return f"-\\frac{{{abs(val.numerator)}}}{{{val.denominator}}}"
        return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
    return str(val)

def format_tableau_df(matrix, col_names, row_names):
    str_data = [[fmt_f(cell) for cell in row] for row in matrix]
    return pd.DataFrame(str_data, columns=col_names, index=row_names)

def build_equation_text(coeffs, var_names, sense=None, rhs=None):
    """Construye ecuación en texto plano limpio (ideal para PDF y tablas)."""
    terms = []
    for c, v in zip(coeffs, var_names):
        if c == 0:
            continue
        sign = "+" if c > 0 else "-"
        abs_c = abs(c)
        c_str = "" if abs_c == 1 else fmt_f(abs_c)
        if not terms:
            prefix = "-" if c < 0 else ""
            terms.append(f"{prefix}{c_str}{v}")
        else:
            terms.append(f" {sign} {c_str}{v}")
    expr = "".join(terms) if terms else "0"
    if sense is not None and rhs is not None:
        return f"{expr} {sense} {fmt_f(rhs)}"
    return expr

def build_equation_latex(coeffs, var_names, sense=None, rhs=None):
    terms = []
    for c, v in zip(coeffs, var_names):
        if c == 0:
            continue
        sign = "+" if c > 0 else "-"
        abs_c = abs(c)
        c_str = "" if abs_c == 1 else fmt_latex_f(abs_c)
        if not terms:
            prefix = "-" if c < 0 else ""
            terms.append(f"{prefix}{c_str}{v}")
        else:
            terms.append(f" {sign} {c_str}{v}")
    expr = "".join(terms) if terms else "0"
    if sense is not None and rhs is not None:
        sense_tex = {"<=": "\\le", ">=": "\\ge", "=": "="}[sense]
        return f"{expr} {sense_tex} {fmt_latex_f(rhs)}"
    return expr

# ==============================================================================
# GENERADOR DE REPORTE EN PDF (FPDF2)
# ==============================================================================
class LinearProgPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 60, 114)
        self.cell(0, 8, "Aventura Lineal - Resolucion Paso a Paso", border=0, ln=1, align="C")
        self.set_draw_color(30, 60, 114)
        self.line(10, 18, 200, 18)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

def clean_latin1(text):
    """Limpia caracteres Unicode que Helvetica estándar de FPDF no soporta."""
    replacements = {
        "≤": "<=", "≥": ">=", "≠": "!=", "÷": "/", "×": "x", "→": "->",
        "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6",
        "🏆": "[GANADOR]", "✅": "[OK]", "❌": "[NO]", "🎯": "[PIVOTE]",
        "—": "-", "–": "-", "“": '"', "”": '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_pdf_bytes(report_blocks):
    """
    Convierte una lista de bloques estructurados en bytes de PDF.
    Tipos de bloque:
      - ('title', texto)
      - ('subtitle', texto)
      - ('text', texto)
      - ('table', col_names, row_names, rows_data)
      - ('image', ruta_imagen)
    """
    pdf = LinearProgPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for block in report_blocks:
        b_type = block[0]
        if b_type == "title":
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_fill_color(232, 245, 233)
            pdf.set_text_color(27, 94, 32)
            pdf.multi_cell(0, 8, clean_latin1(block[1]), fill=True)
            pdf.ln(2)
        elif b_type == "subtitle":
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(25, 118, 210)
            pdf.multi_cell(0, 7, clean_latin1(block[1]))
            pdf.ln(1)
        elif b_type == "text":
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, clean_latin1(block[1]))
            pdf.ln(2)
        elif b_type == "table":
            _, col_names, row_names, rows_data = block
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(220, 230, 242)
            pdf.set_text_color(0, 0, 0)

            all_cols = ["Base"] + col_names if row_names else col_names
            usable_w = 190
            col_w = usable_w / max(len(all_cols), 1)

            # Encabezados
            for c in all_cols:
                pdf.cell(col_w, 6, clean_latin1(str(c))[:14], border=1, align="C", fill=True)
            pdf.ln()

            # Filas
            pdf.set_font("Helvetica", "", 8)
            for r_idx, r_vals in enumerate(rows_data):
                if row_names:
                    pdf.set_font("Helvetica", "B", 8)
                    pdf.cell(col_w, 6, clean_latin1(str(row_names[r_idx]))[:14], border=1, align="C")
                    pdf.set_font("Helvetica", "", 8)
                for val in r_vals:
                    pdf.cell(col_w, 6, clean_latin1(str(val))[:18], border=1, align="C")
                pdf.ln()
            pdf.ln(3)
        elif b_type == "image":
            img_path = block[1]
            if os.path.exists(img_path):
                pdf.image(img_path, w=150)
                pdf.ln(3)

    return bytes(pdf.output())

# ==============================================================================
# ESCÁNER CON IA (FOTO DE CUADERNO / PIZARRA -> RELLENO AUTOMÁTICO)
# ==============================================================================
def extract_lp_from_image(image_pil, api_key):
    """Usa Gemini Vision para leer un problema de programación lineal desde una foto."""
    client = genai.Client(api_key=api_key)
    prompt = """
    Analiza esta imagen de un problema de Programación Lineal (puede ser escrito a mano, en pizarrón o impreso).
    Extrae los datos matemáticos exactos y devuélvelos ÚNICAMENTE como un JSON válido con esta estructura exacta:
    {
      "obj_type": "Maximizar" o "Minimizar",
      "num_vars": entero (entre 2 y 6),
      "c": [lista de números flotantes de la función objetivo, longitud num_vars],
      "constraints": [
        {
          "coeffs": [lista de números flotantes de longitud num_vars],
          "sense": "<=" o ">=" o "=",
          "rhs": número flotante del lado derecho
        }
      ]
    }
    Reglas:
    - Ignora las restricciones de no negatividad como x1 >= 0, x2 >= 0, x,y >= 0 (no las incluyas en "constraints").
    - Si las variables se llaman x, y, z, conviértelas en orden a x1, x2, x3.
    - Si falta alguna variable en una restricción, pon 0 en su coeficiente.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image_pil, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    return json.loads(response.text)

# ==============================================================================
# MOTOR 1: MÉTODO GRÁFICO (2 VARIABLES)
# ==============================================================================
def solve_graphical(obj_type, c, constraints, pdf_blocks):
    st.markdown('<div class="step-header">Paso 0: Entendiendo nuestra misión (Planteamiento)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento del Problema (Metodo Grafico)"))

    accion = "ganar la MAYOR cantidad de monedas/puntos" if obj_type == "Maximizar" else "gastar la MENOR cantidad de energía/dinero"
    st.markdown(f"""
    <div class="kid-box">
    <b>🎒 Imagina esta historia:</b><br>
    Tenemos dos decisiones mágicas: <b>x₁</b> y <b>x₂</b> (siempre ≥ 0). Nuestra meta es <b>{accion}</b> siguiendo la Función Objetivo:
    </div>
    """, unsafe_allow_html=True)

    z_tex = build_equation_latex(c, ["x_1", "x_2"])
    z_txt = build_equation_text(c, ["x1", "x2"])
    st.latex(f"\\text{{{obj_type} }} Z = {z_tex}")
    pdf_blocks.append(("text", f"{obj_type} Z = {z_txt}"))

    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        st.latex(f"\\text{{Regla {idx}: }} {build_equation_latex([a1, a2], ['x_1', 'x_2'], sense, b)}")
        pdf_blocks.append(("text", f"Regla {idx}: {build_equation_text([a1, a2], ['x1', 'x2'], sense, b)}"))

    # PASO 1: CRUCES CON EJES
    st.markdown('<div class="step-header">Paso 1: Convertir cada regla en una línea recta (Cruces con los ejes)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Cruces con los ejes para graficar cada recta"))

    all_lines = []
    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        all_lines.append((a1, a2, b, f"R{idx}"))
        with st.expander(f"🔍 Regla {idx}: {fmt_f(a1)}x₁ + {fmt_f(a2)}x₂ = {fmt_f(b)}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if a2 != 0:
                    x2_val = b / a2
                    st.latex(f"x_1 = 0 \\implies {fmt_latex_f(a2)}x_2 = {fmt_latex_f(b)} \\implies x_2 = {fmt_latex_f(x2_val)}")
                    st.write(f"📍 Punto A: **(0, {fmt_f(x2_val)})**")
                    p_a_txt = f"(0, {fmt_f(x2_val)})"
                else:
                    st.write(f"Línea vertical en **x₁ = {fmt_f(b/a1)}**")
                    p_a_txt = f"Vertical x1={fmt_f(b/a1)}"
            with col2:
                if a1 != 0:
                    x1_val = b / a1
                    st.latex(f"x_2 = 0 \\implies {fmt_latex_f(a1)}x_1 = {fmt_latex_f(b)} \\implies x_1 = {fmt_latex_f(x1_val)}")
                    st.write(f"📍 Punto B: **({fmt_f(x1_val)}, 0)**")
                    p_b_txt = f"({fmt_f(x1_val)}, 0)"
                else:
                    st.write(f"Línea horizontal en **x₂ = {fmt_f(b/a2)}**")
                    p_b_txt = f"Horizontal x2={fmt_f(b/a2)}"

            if sense != "=":
                cumple = (0 <= b) if sense == "<=" else (0 >= b)
                lado = "hacia el origen (0,0)" if cumple else "lado contrario al origen (0,0)"
                st.write(f"🎨 Prueba con (0,0): `0 {sense} {fmt_f(b)}` -> **{'SÍ cumple' if cumple else 'NO cumple'}** (se colorea {lado}).")
                pdf_blocks.append(("text", f"Regla {idx}: Puntos {p_a_txt} y {p_b_txt}. Region valida {lado}."))

    all_lines.append((Fraction(1), Fraction(0), Fraction(0), "Eje x2 (x1=0)"))
    all_lines.append((Fraction(0), Fraction(1), Fraction(0), "Eje x1 (x2=0)"))

    # PASO 2: INTERSECCIONES Y REGIÓN FACTIBLE
    st.markdown('<div class="step-header">Paso 2: Encontrar la Región Factible y sus esquinas (Vértices)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 2: Cruce de rectas y validacion de esquinas"))

    candidate_points = []
    intersection_logs = []
    tol = Fraction(1, 10**9)

    for (l1, l2) in combinations(all_lines, 2):
        a1, a2, b1, name1 = l1
        c1, c2, b2, name2 = l2
        det = a1 * c2 - a2 * c1
        if det == 0:
            continue
        x1 = (b1 * c2 - a2 * b2) / det
        x2 = (a1 * b2 - b1 * c1) / det

        is_feasible = (x1 >= -tol) and (x2 >= -tol)
        reasons = []
        if x1 < -tol or x2 < -tol:
            reasons.append("coordenadas negativas")

        for r_idx, (ra1, ra2, rsense, rb) in enumerate(constraints, 1):
            val = ra1 * x1 + ra2 * x2
            if rsense == "<=" and val > rb + tol:
                is_feasible = False
                reasons.append(f"rompe R{r_idx}")
            elif rsense == ">=" and val < rb - tol:
                is_feasible = False
                reasons.append(f"rompe R{r_idx}")
            elif rsense == "=" and abs(val - rb) > tol:
                is_feasible = False
                reasons.append(f"rompe R{r_idx}")

        estado = "✅ SÍ (Vértice válido)" if is_feasible else f"❌ NO ({', '.join(reasons)})"
        intersection_logs.append([f"{name1} con {name2}", f"({fmt_f(x1)}, {fmt_f(x2)})", estado])

        if is_feasible and not any(p[0] == x1 and p[1] == x2 for p in candidate_points):
            candidate_points.append((x1, x2))

    df_inter = pd.DataFrame(intersection_logs, columns=["Cruce", "Punto (x₁, x₂)", "¿Es esquina válida?"])
    st.dataframe(df_inter, use_container_width=True, hide_index=True)
    pdf_blocks.append(("table", ["Cruce", "Punto (x1, x2)", "Validez"], None, intersection_logs))

    if not candidate_points:
        st.error("🚫 No existe ninguna esquina válida (Problema Infactible).")
        pdf_blocks.append(("text", "Resultado: Problema Infactible (no existe region factible)."))
        return

    cx = sum(p[0] for p in candidate_points) / len(candidate_points)
    cy = sum(p[1] for p in candidate_points) / len(candidate_points)
    candidate_points.sort(key=lambda p: np.arctan2(float(p[1] - cy), float(p[0] - cx)))

    # GRÁFICA
    fig, ax = plt.subplots(figsize=(8, 5.5))
    max_x = max([float(p[0]) for p in candidate_points] + [float(b/a1) for a1, a2, _, b in constraints if a1 > 0 and b > 0] + [5.0]) * 1.25
    max_y = max([float(p[1]) for p in candidate_points] + [float(b/a2) for a1, a2, _, b in constraints if a2 > 0 and b > 0] + [5.0]) * 1.25
    x_vals = np.linspace(0, max_x, 400)
    colors = ['#1f77b4', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2']

    for idx, (a1, a2, sense, b) in enumerate(constraints):
        col = colors[idx % len(colors)]
        lbl = f"R{idx+1}: {fmt_f(a1)}x1 + {fmt_f(a2)}x2 {sense} {fmt_f(b)}"
        if a2 != 0:
            ax.plot(x_vals, (float(b) - float(a1) * x_vals) / float(a2), label=lbl, color=col, linewidth=2)
        else:
            ax.axvline(x=float(b / a1), label=lbl, color=col, linewidth=2)

    if len(candidate_points) >= 3:
        ax.fill([float(p[0]) for p in candidate_points], [float(p[1]) for p in candidate_points],
                color='#2ecc71', alpha=0.35, label='Región Factible')
    elif len(candidate_points) == 2:
        ax.plot([float(candidate_points[0][0]), float(candidate_points[1][0])],
                [float(candidate_points[0][1]), float(candidate_points[1][1])],
                color='#2ecc71', linewidth=5, label='Segmento Factible')

    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (vx, vy) in enumerate(candidate_points):
        letra = letras[i % len(letras)]
        ax.scatter(float(vx), float(vy), color='#d62728', zorder=5, s=80)
        ax.annotate(f"{letra} ({fmt_f(vx)}, {fmt_f(vy)})", (float(vx), float(vy)),
                    textcoords="offset points", xytext=(8, 8), fontweight='bold', color='#b71c1c')

    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("Region Factible y Vertices")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    st.pyplot(fig)

    tmp_img = os.path.join(tempfile.gettempdir(), "grafico_pl.png")
    fig.savefig(tmp_img, dpi=150, bbox_inches="tight")
    pdf_blocks.append(("image", tmp_img))

    # PASO 3: EVALUACIÓN DE ESQUINAS
    st.markdown('<div class="step-header">Paso 3: Evaluar cada esquina en Z</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 3: Evaluacion de Vertices en la Funcion Objetivo"))

    eval_rows = []
    best_val = None
    best_points = []

    for i, (vx, vy) in enumerate(candidate_points):
        letra = letras[i % len(letras)]
        z_val = c[0] * vx + c[1] * vy
        calc = f"{fmt_f(c[0])}({fmt_f(vx)}) + {fmt_f(c[1])}({fmt_f(vy)}) = {fmt_f(z_val)}"
        eval_rows.append([letra, f"({fmt_f(vx)}, {fmt_f(vy)})", calc, fmt_f(z_val)])

        if best_val is None or (obj_type == "Maximizar" and z_val > best_val) or (obj_type == "Minimizar" and z_val < best_val):
            best_val = z_val
            best_points = [(letra, vx, vy)]
        elif z_val == best_val:
            best_points.append((letra, vx, vy))

    st.dataframe(pd.DataFrame(eval_rows, columns=["Esquina", "(x₁, x₂)", "Cálculo paso a paso", "Z"]),
                 use_container_width=True, hide_index=True)
    pdf_blocks.append(("table", ["Esquina", "(x1, x2)", "Calculo", "Z"], None, eval_rows))

    ganadores_txt = ", ".join([f"Esquina {l} ({fmt_f(px)}, {fmt_f(py)})" for l, px, py in best_points])
    res_final = f"Solucion Optima ({obj_type}): {ganadores_txt} con Z = {fmt_f(best_val)}"
    st.success(f"🏆 **{res_final}**")
    pdf_blocks.append(("text", res_final))

# ==============================================================================
# MOTOR 2: RESOLUCIÓN DE TABLAS SIMPLEX CELDA POR CELDA (SIN SALTARSE NADA)
# ==============================================================================
def run_simplex_iterations(tableau, col_names, row_names, basic_vars, pdf_blocks, phase_label=""):
    """
    Muestra cada tabla Símplex y explica celda por celda cómo se transforma la tabla
    en la siguiente iteración (división de fila pivote + Gauss-Jordan detallado).
    """
    iteration = 0
    max_iterations = 25

    while iteration < max_iterations:
        iteration += 1
        titulo_it = f"{phase_label}Iteracion #{iteration}"
        st.markdown(f"#### 🔄 {titulo_it}")
        pdf_blocks.append(("subtitle", titulo_it))

        # Mostrar tabla actual
        df_curr = format_tableau_df(tableau, col_names, row_names)
        st.dataframe(df_curr, use_container_width=True)
        pdf_blocks.append(("table", col_names, row_names, [[fmt_f(c) for c in r] for r in tableau]))

        z_row = tableau[0][:-1]
        min_coeff = min(z_row)

        if min_coeff >= 0:
            msg_fin = "¡Tabla óptima alcanzada! Ya no hay números negativos en la fila objetivo."
            st.markdown(f"""
            <div class="kid-box">
            <b>🎉 {msg_fin}</b><br>
            Como todos los números de la fila de arriba son <b>cero o positivos</b>, ninguna variable nueva puede mejorar el resultado.
            </div>
            """, unsafe_allow_html=True)
            pdf_blocks.append(("text", msg_fin))
            return "optimal", tableau, basic_vars, row_names

        # 1. Columna Pivote
        pivot_col = z_row.index(min_coeff)
        entering_var = col_names[pivot_col]
        txt_col = f"1) Columna Pivote (Entra): '{entering_var}' porque tiene el valor mas negativo en la fila superior ({fmt_f(min_coeff)})."
        st.markdown(f"**{txt_col}**")
        pdf_blocks.append(("text", txt_col))

        # 2. Fila Pivote (Prueba del Cociente)
        st.markdown(f"**2) Fila Pivote (Sale) - Prueba del Cociente (`RHS ÷ {entering_var}`):**")
        ratios = []
        ratio_table_rows = []
        for r in range(1, len(tableau)):
            rhs_val = tableau[r][-1]
            col_val = tableau[r][pivot_col]
            b_var = basic_vars[r - 1]
            if col_val > 0:
                ratio = rhs_val / col_val
                ratios.append((ratio, r))
                ratio_table_rows.append([b_var, fmt_f(rhs_val), fmt_f(col_val), f"{fmt_f(rhs_val)} / {fmt_f(col_val)} = {fmt_f(ratio)}", "✅ Válido"])
            else:
                ratio_table_rows.append([b_var, fmt_f(rhs_val), fmt_f(col_val), "No permitido", "❌ Negativo o cero"])

        st.dataframe(pd.DataFrame(ratio_table_rows, columns=["Fila Base", "RHS", f"Columna {entering_var}", "División (Cociente)", "Estado"]),
                     use_container_width=True, hide_index=True)
        pdf_blocks.append(("table", ["Fila", "RHS", entering_var, "Cociente", "Estado"], None, ratio_table_rows))

        if not ratios:
            st.error("🚀 Problema No Acotado: todos los valores en la columna pivote son <= 0.")
            pdf_blocks.append(("text", "Problema No Acotado."))
            return "unbounded", tableau, basic_vars, row_names

        min_ratio, pivot_row = min(ratios, key=lambda x: x[0])
        leaving_var = basic_vars[pivot_row - 1]
        pivot_element = tableau[pivot_row][pivot_col]

        txt_piv = f"-> Sale '{leaving_var}' (menor cociente = {fmt_f(min_ratio)}). Elemento Pivote = {fmt_f(pivot_element)}."
        st.success(f"🎯 **{txt_piv}**")
        pdf_blocks.append(("text", txt_piv))

        # 3. CÁLCULO CELDA POR CELDA DE LA NUEVA TABLA
        st.markdown(f"**3) Cómo se construye la Nueva Tabla paso a paso (Celda por Celda):**")
        new_tableau = [row[:] for row in tableau]
        old_pivot_row = tableau[pivot_row][:]
        new_pivot_row = [cell / pivot_element for cell in old_pivot_row]
        new_tableau[pivot_row] = new_pivot_row

        with st.expander(f"🧮 Ver todas las operaciones celda por celda de la Iteración #{iteration}", expanded=True):
            # PASO A: Fila Pivote
            st.markdown(f"##### 🔹 Paso A: Convertir el Elemento Pivote (`{fmt_f(pivot_element)}`) en `1`")
            st.latex(f"\\text{{Nueva Fila }}_{{{entering_var}}} = \\frac{{\\text{{Fila vieja }}_{{{leaving_var}}}}}{{{fmt_latex_f(pivot_element)}}}")
            pdf_blocks.append(("text", f"Paso A: Nueva Fila {entering_var} = Fila vieja {leaving_var} / {fmt_f(pivot_element)}"))

            piv_cells_table = []
            for c_i, c_name in enumerate(col_names):
                op_str = f"{fmt_f(old_pivot_row[c_i])} ÷ {fmt_f(pivot_element)}"
                piv_cells_table.append([c_name, fmt_f(old_pivot_row[c_i]), op_str, fmt_f(new_pivot_row[c_i])])

            st.dataframe(pd.DataFrame(piv_cells_table, columns=["Columna", "Valor Anterior", "Operación", "Nuevo Valor"]),
                         use_container_width=True, hide_index=True)
            pdf_blocks.append(("table", ["Columna", "Antes", "Operacion", "Despues"], None, piv_cells_table))

            # PASO B: Hacer 0 el resto de la columna pivote
            st.markdown(f"##### 🔹 Paso B: Convertir en `0` los demás números de la columna `{entering_var}`")
            st.write("Fórmula mágica para cada fila: **`Nuevo Valor = Valor Anterior - (Número en Columna Pivote) × (Nuevo Valor Fila Pivote)`**")

            for r in range(len(tableau)):
                if r == pivot_row:
                    continue
                target_name = row_names[r]
                factor = tableau[r][pivot_col]
                old_r = tableau[r][:]

                if factor == 0:
                    st.info(f"✅ **Fila `{target_name}`**: Ya tiene un `0` en `{entering_var}`, se copia idéntica.")
                    pdf_blocks.append(("text", f"Fila {target_name}: ya tiene 0 en {entering_var}, no cambia."))
                    continue

                new_r = [old_r[c_i] - factor * new_pivot_row[c_i] for c_i in range(len(col_names))]
                new_tableau[r] = new_r

                sign_op = "-" if factor > 0 else "+"
                abs_fac = abs(factor)
                st.latex(f"\\text{{Nueva Fila }}_{{{target_name}}} = \\text{{Fila }}_{{{target_name}}} {sign_op} ({fmt_latex_f(abs_fac)}) \\times \\text{{Nueva Fila }}_{{{entering_var}}}")
                pdf_blocks.append(("text", f"Paso B - Fila {target_name}: Nueva = Vieja - ({fmt_f(factor)}) * Nueva_Fila_{entering_var}"))

                row_cells_table = []
                for c_i, c_name in enumerate(col_names):
                    calc_expr = f"{fmt_f(old_r[c_i])} - ({fmt_f(factor)})×({fmt_f(new_pivot_row[c_i])})"
                    row_cells_table.append([c_name, fmt_f(old_r[c_i]), calc_expr, fmt_f(new_r[c_i])])

                st.dataframe(pd.DataFrame(row_cells_table, columns=["Columna", "Valor Anterior", "Operación Exacta", "Nuevo Valor"]),
                             use_container_width=True, hide_index=True)
                pdf_blocks.append(("table", ["Columna", "Antes", "Calculo Exacto", "Despues"], None, row_cells_table))

        tableau = new_tableau
        basic_vars[pivot_row - 1] = entering_var
        row_names[pivot_row] = entering_var
        st.divider()

    return "max_iter", tableau, basic_vars, row_names

# ==============================================================================
# MOTOR 3: MÉTODO SÍMPLEX ESTÁNDAR
# ==============================================================================
def solve_simplex_standard(obj_type, c, constraints, pdf_blocks):
    num_vars = len(c)
    num_cons = len(constraints)

    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        if sense != "<=" or rhs < 0:
            st.error(f"⚠️ La restricción #{idx} tiene signo `{sense}` o RHS negativo. Usa el **Método de las Dos Fases** para resolverla.")
            return

    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento (Metodo Simplex)"))

    var_names = [f"x_{i+1}" for i in range(num_vars)]
    var_plain = [f"x{i+1}" for i in range(num_vars)]
    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, var_names)}")
    pdf_blocks.append(("text", f"{obj_type} Z = {build_equation_text(c, var_plain)}"))

    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, var_names, sense, rhs)}")
        pdf_blocks.append(("text", f"R{idx}: {build_equation_text(coeffs, var_plain, sense, rhs)}"))

    st.markdown('<div class="step-header">Paso 1: Agregar Variables de Holgura (s₁, s₂...)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Forma Estandar con Variables de Holgura"))

    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    if obj_type == "Minimizar":
        st.info("💡 Como queremos **Minimizar Z**, maximizamos **-Z** y al final invertimos el signo.")

    slack_names = [f"s_{i+1}" for i in range(num_cons)]
    all_col_names = var_plain + [f"s{i+1}" for i in range(num_cons)] + ["RHS"]

    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        st.latex(build_equation_latex(coeffs + s_vec, var_names + slack_names, "=", rhs))
        pdf_blocks.append(("text", build_equation_text(coeffs + s_vec, all_col_names[:-1], "=", rhs)))

    z_row = [-mult_z * ci for ci in c] + [Fraction(0)] * num_cons + [Fraction(0)]
    tableau = [z_row]
    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        tableau.append(coeffs + s_vec + [rhs])

    basic_vars = [f"s{i+1}" for i in range(num_cons)]
    row_names = ["Z"] + basic_vars[:]

    st.markdown('<div class="step-header">Paso 2: Iteraciones de la Tabla Símplex</div>', unsafe_allow_html=True)
    status, final_tab, final_basics, _ = run_simplex_iterations(tableau, all_col_names, row_names, basic_vars, pdf_blocks)

    if status == "optimal":
        st.markdown('<div class="step-header">Paso 3: Solución Final</div>', unsafe_allow_html=True)
        pdf_blocks.append(("title", "Paso 3: Solucion Optima Final"))
        sol_dict = {f"x{i+1}": Fraction(0) for i in range(num_vars)}
        for r_idx, b_var in enumerate(final_basics, 1):
            if b_var in sol_dict:
                sol_dict[b_var] = final_tab[r_idx][-1]

        final_z = final_tab[0][-1] * mult_z
        cols = st.columns(num_vars + 1)
        for i in range(num_vars):
            v_key = f"x{i+1}"
            cols[i].metric(label=f"Variable {v_key}", value=fmt_f(sol_dict[v_key]))
        cols[-1].metric(label=f"Valor Óptimo Z", value=fmt_f(final_z))

        res_txt = "Solucion Optima: " + ", ".join([f"{k} = {fmt_f(v)}" for k, v in sol_dict.items()]) + f" | Z = {fmt_f(final_z)}"
        st.success(f"🎊 **{res_txt}**")
        pdf_blocks.append(("text", res_txt))

# ==============================================================================
# MOTOR 4: MÉTODO DE LAS DOS FASES
# ==============================================================================
def solve_two_phase(obj_type, c, constraints, pdf_blocks):
    num_vars = len(c)
    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento (Metodo de las Dos Fases)"))

    var_names = [f"x_{i+1}" for i in range(num_vars)]
    var_plain = [f"x{i+1}" for i in range(num_vars)]
    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, var_names)}")
    pdf_blocks.append(("text", f"{obj_type} Z = {build_equation_text(c, var_plain)}"))

    norm_constraints = []
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, var_names, sense, rhs)}")
        pdf_blocks.append(("text", f"R{idx}: {build_equation_text(coeffs, var_plain, sense, rhs)}"))
        if rhs < 0:
            norm_constraints.append(([-x for x in coeffs], {"<=": ">=", ">=": "<=", "=": "="}[sense], -rhs))
        else:
            norm_constraints.append((coeffs[:], sense, rhs))

    st.markdown('<div class="step-header">Paso 1: Variables de Holgura, Exceso y Artificiales</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Incorporacion de Variables Artificiales"))

    slack_excess_names = []
    artificial_names = []
    row_structures = []

    for idx, (coeffs, sense, rhs) in enumerate(norm_constraints, 1):
        info = {"coeffs": coeffs, "sense": sense, "rhs": rhs, "s_name": None, "s_sign": 0, "a_name": None}
        if sense == "<=":
            s_n = f"s{idx}"
            slack_excess_names.append(s_n)
            info["s_name"] = s_n
            info["s_sign"] = Fraction(1)
        elif sense == ">=":
            e_n = f"e{idx}"
            a_n = f"a{idx}"
            slack_excess_names.append(e_n)
            artificial_names.append(a_n)
            info["s_name"] = e_n
            info["s_sign"] = Fraction(-1)
            info["a_name"] = a_n
        elif sense == "=":
            a_n = f"a{idx}"
            artificial_names.append(a_n)
            info["a_name"] = a_n
        row_structures.append(info)

    if not artificial_names:
        st.info("No se requieren variables artificiales; pasando a Símplex estándar.")
        solve_simplex_standard(obj_type, c, norm_constraints, pdf_blocks)
        return

    col_names_p1 = var_plain + slack_excess_names + artificial_names + ["RHS"]

    for info in row_structures:
        vec = [Fraction(0)] * (len(col_names_p1) - 1)
        for i in range(num_vars):
            vec[i] = info["coeffs"][i]
        if info["s_name"]:
            vec[col_names_p1.index(info["s_name"])] = info["s_sign"]
        if info["a_name"]:
            vec[col_names_p1.index(info["a_name"])] = Fraction(1)
        st.latex(build_equation_latex(vec, col_names_p1[:-1], "=", info["rhs"]))
        pdf_blocks.append(("text", build_equation_text(vec, col_names_p1[:-1], "=", info["rhs"])))

    # FASE 1
    st.markdown('<div class="step-header">🚀 FASE 1: Eliminar Variables Artificiales (Minimizar W)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "FASE 1: Minimizar la suma de variables artificiales (W)"))

    tableau_p1 = []
    basic_vars = []
    for info in row_structures:
        row = [Fraction(0)] * len(col_names_p1)
        for i in range(num_vars):
            row[i] = info["coeffs"][i]
        if info["s_name"]:
            row[col_names_p1.index(info["s_name"])] = info["s_sign"]
        if info["a_name"]:
            row[col_names_p1.index(info["a_name"])] = Fraction(1)
            basic_vars.append(info["a_name"])
        else:
            basic_vars.append(info["s_name"])
        row[-1] = info["rhs"]
        tableau_p1.append(row)

    w_row = [Fraction(0)] * len(col_names_p1)
    for a_n in artificial_names:
        w_row[col_names_p1.index(a_n)] = Fraction(1)

    st.write("**Ajuste inicial de la fila W (restar filas con variables artificiales básicas):**")
    for r_idx, b_var in enumerate(basic_vars):
        if b_var in artificial_names:
            st.latex(f"\\text{{Fila }} W \\leftarrow \\text{{Fila }} W - \\text{{Fila }}_{{{b_var}}}")
            pdf_blocks.append(("text", f"Ajuste inicial: Fila W = Fila W - Fila {b_var}"))
            w_row = [w_row[j] - tableau_p1[r_idx][j] for j in range(len(col_names_p1))]

    status_p1, end_tab_p1, end_basics_p1, _ = run_simplex_iterations(
        [w_row] + tableau_p1, col_names_p1, ["W"] + basic_vars[:], basic_vars, pdf_blocks, phase_label="Fase 1 - "
    )

    if status_p1 != "optimal" or end_tab_p1[0][-1] != 0:
        st.error(f"🚫 Problema Infactible: W final = {fmt_f(abs(end_tab_p1[0][-1]))} ≠ 0. Las restricciones se contradicen.")
        pdf_blocks.append(("text", "Resultado: Problema Infactible (W != 0)."))
        return

    st.success("✅ **¡Fase 1 completada!** W = 0. Todas las variables artificiales salieron.")

    # FASE 2
    st.markdown('<div class="step-header">🏁 FASE 2: Resolver el Problema Original (Z)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "FASE 2: Optimizacion de la Funcion Objetivo Original Z"))

    keep_indices = [i for i, name in enumerate(col_names_p1) if name not in artificial_names]
    col_names_p2 = [col_names_p1[i] for i in keep_indices]
    clean_rows = [[end_tab_p1[r_idx][i] for i in keep_indices] for r_idx in range(1, len(end_tab_p1))]

    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    z_row_p2 = [Fraction(0)] * len(col_names_p2)
    for i in range(num_vars):
        z_row_p2[i] = -mult_z * c[i]

    for r_idx, b_var in enumerate(end_basics_p1):
        if b_var in col_names_p2:
            c_idx = col_names_p2.index(b_var)
            factor = z_row_p2[c_idx]
            if factor != 0:
                st.latex(f"\\text{{Fila }} Z \\leftarrow \\text{{Fila }} Z - ({fmt_latex_f(factor)}) \\times \\text{{Fila }}_{{{b_var}}}")
                pdf_blocks.append(("text", f"Ajuste Fase 2: Fila Z = Fila Z - ({fmt_f(factor)}) * Fila {b_var}"))
                z_row_p2 = [z_row_p2[j] - factor * clean_rows[r_idx][j] for j in range(len(col_names_p2))]

    status_p2, end_tab_p2, end_basics_p2, _ = run_simplex_iterations(
        [z_row_p2] + clean_rows, col_names_p2, ["Z"] + end_basics_p1[:], end_basics_p1, pdf_blocks, phase_label="Fase 2 - "
    )

    if status_p2 == "optimal":
        st.markdown('<div class="step-header">Paso Final: Solución Óptima</div>', unsafe_allow_html=True)
        pdf_blocks.append(("title", "Paso Final: Solucion Optima"))
        sol_dict = {f"x{i+1}": Fraction(0) for i in range(num_vars)}
        for r_idx, b_var in enumerate(end_basics_p2, 1):
            if b_var in sol_dict:
                sol_dict[b_var] = end_tab_p2[r_idx][-1]

        final_z = end_tab_p2[0][-1] * mult_z
        cols = st.columns(num_vars + 1)
        for i in range(num_vars):
            v_key = f"x{i+1}"
            cols[i].metric(label=f"Variable {v_key}", value=fmt_f(sol_dict[v_key]))
        cols[-1].metric(label="Valor Óptimo Z", value=fmt_f(final_z))

        res_txt = "Solucion Optima: " + ", ".join([f"{k} = {fmt_f(v)}" for k, v in sol_dict.items()]) + f" | Z = {fmt_f(final_z)}"
        st.success(f"🏆 **{res_txt}**")
        pdf_blocks.append(("text", res_txt))

# ==============================================================================
# INTERFAZ PRINCIPAL + CÁMARA / SUBIDA DE FOTO
# ==============================================================================
st.title("🧭 Aventura Lineal: Programación Lineal Paso a Paso")
st.write("Resuelve celda por celda, escanea problemas con tu cámara y descarga toda la explicación en PDF.")

# Inicializar estado
if "lp_data" not in st.session_state:
    st.session_state.lp_data = {
        "obj_type": "Maximizar",
        "num_vars": 2,
        "num_cons": 2,
        "c": [3.0, 5.0],
        "cons": [
            ([1.0, 0.0], "<=", 4.0),
            ([2.0, 3.0], "<=", 18.0)
        ]
    }

# --- SIDEBAR ---
st.sidebar.header("⚙️ Configuración")
metodo = st.sidebar.selectbox("1. Elige el Método:", ["Método Gráfico", "Método Símplex", "Método de las Dos Fases"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Ejemplos Rápidos")
if st.sidebar.button("🧸 Ej. 1: Juguetes (Gráfico / Símplex)"):
    st.session_state.lp_data = {
        "obj_type": "Maximizar", "num_vars": 2, "num_cons": 2,
        "c": [3.0, 5.0], "cons": [([1.0, 0.0], "<=", 4.0), ([2.0, 3.0], "<=", 18.0)]
    }
if st.sidebar.button("🥗 Ej. 2: Dieta (Dos Fases - Minimizar)"):
    st.session_state.lp_data = {
        "obj_type": "Minimizar", "num_vars": 2, "num_cons": 2,
        "c": [4.0, 6.0], "cons": [([2.0, 1.0], ">=", 8.0), ([1.0, 3.0], ">=", 9.0)]
    }
if st.sidebar.button("🚀 Ej. 3: Misión Espacial (Dos Fases)"):
    st.session_state.lp_data = {
        "obj_type": "Maximizar", "num_vars": 2, "num_cons": 3,
        "c": [5.0, 4.0], "cons": [([1.0, 1.0], "<=", 10.0), ([2.0, 1.0], ">=", 6.0), ([1.0, 2.0], "=", 12.0)]
    }

# --- SECCIÓN DE ESCÁNER CON CÁMARA O FOTO ---
with st.expander("📸 Escanear problema con Cámara o Subir Foto (Auto-rellenar cuadros)", expanded=False):
    st.write("Toma una foto a tu cuaderno o sube una imagen del ejercicio para rellenar todos los cuadros automáticamente.")
    api_key_input = st.text_input("🔑 Tu Gemini API Key (necesaria para leer la foto):", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    
    cam_col1, cam_col2 = st.columns(2)
    with cam_col1:
        foto_camara = st.camera_input("Tomar foto con la cámara")
    with cam_col2:
        foto_archivo = st.file_uploader("O subir imagen (JPG, PNG)", type=["jpg", "jpeg", "png"])

    imagen_elegida = foto_camara if foto_camara is not None else foto_archivo
    if imagen_elegida is not None:
        img_pil = Image.open(imagen_elegida)
        if st.button("✨ Leer foto y rellenar cuadros automáticamente"):
            if not api_key_input:
                st.warning("⚠️ Por favor escribe tu Gemini API Key arriba para analizar la imagen.")
            else:
                with st.spinner("Leyendo ecuaciones de la imagen..."):
                    try:
                        parsed = extract_lp_from_image(img_pil, api_key_input)
                        st.session_state.lp_data = {
                            "obj_type": parsed.get("obj_type", "Maximizar"),
                            "num_vars": int(parsed.get("num_vars", 2)),
                            "num_cons": len(parsed.get("constraints", [])),
                            "c": [float(x) for x in parsed.get("c", [1.0, 1.0])],
                            "cons": [
                                ([float(v) for v in item["coeffs"]], item["sense"], float(item["rhs"]))
                                for item in parsed.get("constraints", [])
                            ]
                        }
                        st.success("✅ ¡Problema detectado y cargado en los cuadros de abajo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo leer la imagen: {e}")

# --- FORMULARIO DE DATOS ---
data = st.session_state.lp_data
st.subheader(f"🛠️ Datos del Problema ({metodo})")

c1, c2, c3 = st.columns(3)
with c1:
    obj_type = st.selectbox("Objetivo:", ["Maximizar", "Minimizar"], index=0 if data["obj_type"] == "Maximizar" else 1)
with c2:
    if metodo == "Método Gráfico":
        n_vars = 2
        st.number_input("Variables:", value=2, disabled=True)
    else:
        n_vars = st.number_input("Número de variables:", min_value=2, max_value=6, value=max(2, min(6, data["num_vars"])), step=1)
with c3:
    n_cons = st.number_input("Número de restricciones:", min_value=1, max_value=6, value=max(1, min(6, data["num_cons"])), step=1)

st.markdown("**Función Objetivo ($Z$):**")
obj_cols = st.columns(n_vars)
c_inputs = []
for i in range(n_vars):
    val_def = data["c"][i] if i < len(data["c"]) else 1.0
    with obj_cols[i]:
        val = st.number_input(f"x{i+1} en Z:", value=float(val_def), step=1.0, key=f"obj_{i}")
        c_inputs.append(to_frac(val))

st.markdown("**Restricciones:**")
constraints_inputs = []
for r in range(n_cons):
    r_cols = st.columns(n_vars + 2)
    row_coeffs = []
    def_row = data["cons"][r] if r < len(data["cons"]) else ([1.0]*n_vars, "<=", 10.0)
    for i in range(n_vars):
        c_def = def_row[0][i] if i < len(def_row[0]) else 1.0
        with r_cols[i]:
            v = st.number_input(f"R{r+1} · x{i+1}", value=float(c_def), step=1.0, key=f"c_{r}_{i}")
            row_coeffs.append(to_frac(v))
    with r_cols[n_vars]:
        s_opts = ["<="] if metodo == "Método Símplex" else ["<=", ">=", "="]
        s_idx = s_opts.index(def_row[1]) if def_row[1] in s_opts else 0
        sense = st.selectbox("Signo", s_opts, index=s_idx, key=f"s_{r}")
    with r_cols[n_vars + 1]:
        rhs_val = st.number_input("RHS", value=float(def_row[2]), step=1.0, key=f"rhs_{r}")

    if metodo == "Método Gráfico":
        constraints_inputs.append((row_coeffs[0], row_coeffs[1], sense, to_frac(rhs_val)))
    else:
        constraints_inputs.append((row_coeffs, sense, to_frac(rhs_val)))

st.markdown("---")
if st.button("🚀 Resolver Paso a Paso y Generar PDF", type="primary", use_container_width=True):
    pdf_report_blocks = []
    if metodo == "Método Gráfico":
        solve_graphical(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)
    elif metodo == "Método Símplex":
        solve_simplex_standard(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)
    elif metodo == "Método de las Dos Fases":
        solve_two_phase(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)

    if pdf_report_blocks:
        pdf_bytes = generate_pdf_bytes(pdf_report_blocks)
        st.markdown("---")
        st.download_button(
            label="📥 Descargar toda la resolución paso a paso en PDF",
            data=pdf_bytes,
            file_name=f"Resolucion_{metodo.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )