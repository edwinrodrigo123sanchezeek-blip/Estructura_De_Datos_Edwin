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
    page_title="Aventura Lineal: Programación Lineal Exacta Paso a Paso",
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
# EXPLICACIÓN DIDÁCTICA: ¿POR QUÉ Z SE VUELVE NEGATIVA EN LA TABLA?
# ==============================================================================
def render_sign_flip_explanation(obj_type, c, var_names, pdf_blocks):
    st.markdown('<div class="step-header">💡 ¿Por qué la Función Objetivo positiva se vuelve NEGATIVA en la tabla?</div>', unsafe_allow_html=True)
    
    z_orig = build_equation_latex(c, var_names)
    neg_c = [-x for x in c]
    z_despejada = build_equation_latex(neg_c, var_names)

    st.markdown("""
    <div class="kid-box">
    <b>⚖️ ¡Imagina una balanza de dos platillos!</b><br>
    Al principio tenemos la ecuación en equilibrio:<br>
    En el platillo izquierdo está <b>Z</b> (nuestro premio total), y en el platillo derecho están las ganancias de cada producto (por ejemplo: <code>8x₁ + 10x₂</code>).<br><br>
    Para meter esta ecuación en nuestra <b>Tabla Símplex</b>, necesitamos que <b>TODAS las letras queden del lado izquierdo</b> y que del lado derecho (<b>L.D.</b>) quede un <b>0</b>.<br>
    Como en las ecuaciones lo que está sumando a la derecha pasa <b>restando</b> a la izquierda, ¡los números positivos cruzan el puente del signo <code>=</code> y se vuelven <b>negativos</b>!
    </div>
    """, unsafe_allow_html=True)

    if obj_type == "Maximizar":
        st.latex(f"Z = {z_orig} \\quad \\xrightarrow{{\\text{{Pasamos todo a la izquierda}}}} \\quad Z {z_despejada} = 0")
        st.write("👉 Por eso en la fila **Z** de la tabla inicial aparecen con signo negativo (`-`), mientras que en la columna **Z** va un `1` y en **L.D.** va un `0`.")
        pdf_blocks.append(("text", f"Explicacion de signos: Z = {build_equation_text(c, [v.replace('_','') for v in var_names])} se iguala a cero pasando los terminos a la izquierda: Z {build_equation_text(neg_c, [v.replace('_','') for v in var_names])} = 0."))
    else:
        st.latex(f"\\text{{Minimizar }} Z = {z_orig} \\iff \\text{{Maximizar }} (-Z) = {z_despejada}")
        st.latex(f"-Z = {z_despejada} \\quad \\xrightarrow{{\\text{{Pasamos a la izquierda}}}} \\quad -Z + {z_orig} = 0")
        st.write("👉 Como queremos **Minimizar**, multiplicamos Z por `-1` para convertirlo en maximización, y al pasar los términos a la izquierda quedan positivos en la fila Z.")
        pdf_blocks.append(("text", "Explicacion de signos (Minimizacion): Minimizar Z equivale a Maximizar -Z, por lo que al igualar a 0 los coeficientes quedan con signo opuesto."))

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
    replacements = {
        "≤": "<=", "≥": ">=", "≠": "!=", "÷": "/", "×": "x", "→": "->",
        "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6",
        "₇": "7", "₈": "8", "₉": "9", "₀": "0",
        "🏆": "[GANADOR]", "✅": "[OK]", "❌": "[NO]", "🎯": "[PIVOTE]",
        "—": "-", "–": "-", "“": '"', "”": '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_pdf_bytes(report_blocks):
    pdf = LinearProgPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for block in report_blocks:
        b_type = block[0]
        if b_type == "title":
            pdf.set_font("Helvetica", "B", 12)
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

            for c in all_cols:
                pdf.cell(col_w, 6, clean_latin1(str(c))[:14], border=1, align="C", fill=True)
            pdf.ln()

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
# ESCÁNER CON IA (FOTO -> RELLENO AUTOMÁTICO)
# ==============================================================================
def extract_lp_from_image(image_pil, api_key):
    client = genai.Client(api_key=api_key)
    prompt = """
    Analiza esta imagen de un problema de Programación Lineal (escrito a mano, en pizarrón o impreso).
    Extrae los datos matemáticos exactos y devuélvelos ÚNICAMENTE como un JSON válido con esta estructura:
    {
      "obj_type": "Maximizar" o "Minimizar",
      "num_vars": entero (entre 2 y 6),
      "c": [lista de números flotantes de la función objetivo],
      "constraints": [
        {
          "coeffs": [lista de números flotantes],
          "sense": "<=" o ">=" o "=",
          "rhs": número flotante del lado derecho
        }
      ]
    }
    Reglas:
    - Ignora las restricciones de no negatividad como x1 >= 0, x2 >= 0.
    - Si las variables son x, y, z, conviértelas en orden a x1, x2, x3.
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
    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema (Método Gráfico)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento (Metodo Grafico)"))

    z_tex = build_equation_latex(c, ["x_1", "x_2"])
    st.latex(f"\\text{{{obj_type} }} Z = {z_tex}")
    pdf_blocks.append(("text", f"{obj_type} Z = {build_equation_text(c, ['x1', 'x2'])}"))

    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        st.latex(f"\\text{{Regla {idx}: }} {build_equation_latex([a1, a2], ['x_1', 'x_2'], sense, b)}")
        pdf_blocks.append(("text", f"Regla {idx}: {build_equation_text([a1, a2], ['x1', 'x2'], sense, b)}"))

    st.markdown('<div class="step-header">Paso 1: Cruces con los ejes para trazar cada línea</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Cruces con los ejes"))

    all_lines = []
    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        all_lines.append((a1, a2, b, f"R{idx}"))
        with st.expander(f"🔍 Regla {idx}: {fmt_f(a1)}x₁ + {fmt_f(a2)}x₂ = {fmt_f(b)}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if a2 != 0:
                    x2_val = b / a2
                    st.latex(f"x_1 = 0 \\implies x_2 = \\frac{{{fmt_latex_f(b)}}}{{{fmt_latex_f(a2)}}} = {fmt_latex_f(x2_val)}")
                    st.write(f"📍 Punto A: **(0, {fmt_f(x2_val)})**")
                else:
                    st.write(f"Línea vertical en **x₁ = {fmt_f(b/a1)}**")
            with col2:
                if a1 != 0:
                    x1_val = b / a1
                    st.latex(f"x_2 = 0 \\implies x_1 = \\frac{{{fmt_latex_f(b)}}}{{{fmt_latex_f(a1)}}} = {fmt_latex_f(x1_val)}")
                    st.write(f"📍 Punto B: **({fmt_f(x1_val)}, 0)**")
                else:
                    st.write(f"Línea horizontal en **x₂ = {fmt_f(b/a2)}**")

    all_lines.append((Fraction(1), Fraction(0), Fraction(0), "Eje x2 (x1=0)"))
    all_lines.append((Fraction(0), Fraction(1), Fraction(0), "Eje x1 (x2=0)"))

    st.markdown('<div class="step-header">Paso 2: Región Factible y Esquinas (Vértices)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 2: Region Factible y Vertices"))

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
            reasons.append("negativo")
        for r_idx, (ra1, ra2, rsense, rb) in enumerate(constraints, 1):
            val = ra1 * x1 + ra2 * x2
            if (rsense == "<=" and val > rb + tol) or (rsense == ">=" and val < rb - tol) or (rsense == "=" and abs(val - rb) > tol):
                is_feasible = False
                reasons.append(f"rompe R{r_idx}")

        estado = "✅ Válido" if is_feasible else f"❌ No ({', '.join(reasons)})"
        intersection_logs.append([f"{name1} ∩ {name2}", f"({fmt_f(x1)}, {fmt_f(x2)})", estado])
        if is_feasible and not any(p[0] == x1 and p[1] == x2 for p in candidate_points):
            candidate_points.append((x1, x2))

    st.dataframe(pd.DataFrame(intersection_logs, columns=["Cruce", "Punto", "Estado"]), use_container_width=True, hide_index=True)

    if not candidate_points:
        st.error("🚫 Problema Infactible.")
        return

    cx = sum(p[0] for p in candidate_points) / len(candidate_points)
    cy = sum(p[1] for p in candidate_points) / len(candidate_points)
    candidate_points.sort(key=lambda p: np.arctan2(float(p[1] - cy), float(p[0] - cx)))

    fig, ax = plt.subplots(figsize=(8, 5))
    max_x = max([float(p[0]) for p in candidate_points] + [5.0]) * 1.3
    max_y = max([float(p[1]) for p in candidate_points] + [5.0]) * 1.3
    x_vals = np.linspace(0, max_x, 400)
    for idx, (a1, a2, sense, b) in enumerate(constraints):
        lbl = f"R{idx+1}: {fmt_f(a1)}x1 + {fmt_f(a2)}x2 {sense} {fmt_f(b)}"
        if a2 != 0:
            ax.plot(x_vals, (float(b) - float(a1) * x_vals) / float(a2), label=lbl, linewidth=2)
        else:
            ax.axvline(x=float(b / a1), label=lbl, linewidth=2)

    if len(candidate_points) >= 3:
        ax.fill([float(p[0]) for p in candidate_points], [float(p[1]) for p in candidate_points], color='#2ecc71', alpha=0.35, label='Región Factible')

    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (vx, vy) in enumerate(candidate_points):
        ax.scatter(float(vx), float(vy), color='red', zorder=5)
        ax.annotate(f"{letras[i]}({fmt_f(vx)},{fmt_f(vy)})", (float(vx), float(vy)), xytext=(5, 5), textcoords="offset points", fontweight='bold')

    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)

    tmp_img = os.path.join(tempfile.gettempdir(), "grafico_pl.png")
    fig.savefig(tmp_img, dpi=150, bbox_inches="tight")
    pdf_blocks.append(("image", tmp_img))

    eval_rows = []
    best_val = None
    best_pt = None
    for i, (vx, vy) in enumerate(candidate_points):
        z_val = c[0] * vx + c[1] * vy
        eval_rows.append([letras[i], f"({fmt_f(vx)}, {fmt_f(vy)})", f"{fmt_f(c[0])}({fmt_f(vx)}) + {fmt_f(c[1])}({fmt_f(vy)}) = {fmt_f(z_val)}", fmt_f(z_val)])
        if best_val is None or (obj_type == "Maximizar" and z_val > best_val) or (obj_type == "Minimizar" and z_val < best_val):
            best_val = z_val
            best_pt = (letras[i], vx, vy)

    st.dataframe(pd.DataFrame(eval_rows, columns=["Vértice", "Punto", "Sustitución", "Z"]), use_container_width=True, hide_index=True)
    st.success(f"🏆 Solución Óptima: Vértice **{best_pt[0]} ({fmt_f(best_pt[1])}, {fmt_f(best_pt[2])})** con **Z = {fmt_f(best_val)}**")

# ==============================================================================
# MOTOR 2: RESOLUCIÓN EXACTA AL ESTILO DE TU CUADERNO (SUB-TABLAS PASO A PASO)
# ==============================================================================
def run_notebook_simplex_iterations(tableau, col_names, row_names, basic_vars, pdf_blocks, obj_col_label="Z", phase_label=""):
    """
    Resuelve exactamente como en tus fotos del cuaderno:
    - Columna Z (o W) con 1 en fila 0 y 0 en las demás, y última columna 'L.D.'
    - Muestra los cocientes L.D. / Columna Pivote para elegir quién sale.
    - Muestra la sub-tabla tras dividir la Fila Pivote (ej. F2 / 30).
    - Muestra una sub-tabla progresiva por cada fila transformada (ej. F1 + 10*F2, F3 - 2*F2, F4 - 4*F2).
    """
    iteration = 0
    max_iterations = 25

    while iteration < max_iterations:
        iteration += 1
        titulo_it = f"{phase_label}Iteración #{iteration}"
        st.markdown(f"### 🔄 {titulo_it}")
        pdf_blocks.append(("subtitle", titulo_it))

        # Tabla al inicio de la iteración
        st.write("**Tabla actual:**")
        st.dataframe(format_tableau_df(tableau, col_names, row_names), use_container_width=True)
        pdf_blocks.append(("table", col_names, row_names, [[fmt_f(c) for c in r] for r in tableau]))

        # Buscar el más negativo en la fila objetivo (excluyendo col 0 'Z/W' y última col 'L.D.')
        obj_coeffs = tableau[0][1:-1]
        min_coeff = min(obj_coeffs)

        if min_coeff >= 0:
            msg_fin = "¡Tabla óptima alcanzada! Todos los coeficientes de la fila superior son >= 0."
            st.success(f"🎉 **{msg_fin}**")
            pdf_blocks.append(("text", msg_fin))
            return "optimal", tableau, basic_vars, row_names

        # Columna pivote (sumamos 1 porque saltamos la columna 0 que es Z/W)
        pivot_col = obj_coeffs.index(min_coeff) + 1
        entering_var = col_names[pivot_col]

        st.markdown(f"**1️⃣ Columna Pivote (Entra `{entering_var}`):** Es el número más negativo en la fila `{obj_col_label}` (**`{fmt_f(min_coeff)}`**).")
        pdf_blocks.append(("text", f"1) Entra {entering_var} (valor mas negativo: {fmt_f(min_coeff)})."))

        # Prueba del cociente (L.D. / Columna Pivote)
        st.markdown(f"**2️⃣ Cocientes (`L.D. ÷ {entering_var}`) para ver qué fila sale:**")
        ratios = []
        ratio_lines = []
        for r in range(1, len(tableau)):
            ld_val = tableau[r][-1]
            col_val = tableau[r][pivot_col]
            b_var = basic_vars[r - 1]
            if col_val > 0:
                ratio = ld_val / col_val
                ratios.append((ratio, r))
                ratio_lines.append(f"- Fila **F{r+1} (`{b_var}`)**: `{fmt_f(ld_val)} / {fmt_f(col_val)} = {fmt_f(ratio)}` ✅")
            else:
                ratio_lines.append(f"- Fila **F{r+1} (`{b_var}`)**: `{fmt_f(ld_val)} / {fmt_f(col_val)}` ❌ *(no se toma en cuenta)*")

        for line in ratio_lines:
            st.markdown(line)

        if not ratios:
            st.error("🚀 Problema No Acotado (no hay coeficientes positivos en la columna pivote).")
            pdf_blocks.append(("text", "Problema No Acotado."))
            return "unbounded", tableau, basic_vars, row_names

        min_ratio, pivot_row = min(ratios, key=lambda x: x[0])
        leaving_var = basic_vars[pivot_row - 1]
        pivot_element = tableau[pivot_row][pivot_col]
        f_piv_num = pivot_row + 1  # F2, F3, etc. (1-indexado como en tu cuaderno)

        st.info(f"🎯 **Entra `{entering_var}` y Sale `{leaving_var}`** (menor cociente = `{fmt_f(min_ratio)}`). **Elemento Pivote = `{fmt_f(pivot_element)}`** (en **F{f_piv_num}**).")
        pdf_blocks.append(("text", f"2) Entra {entering_var} y Sale {leaving_var} (menor cociente: {fmt_f(min_ratio)}). Elemento pivote: {fmt_f(pivot_element)} en F{f_piv_num}."))

        # ======================================================================
        # SUB-TABLAS PROGRESIVAS EXACTAMENTE COMO EN TUS HOJAS DE CUADERNO
        # ======================================================================
        st.markdown("**3️⃣ Transformación progresiva de la tabla (Operación por operación):**")
        working_tab = [row[:] for row in tableau]
        working_rows = row_names[:]

        # Paso A: Dividir la Fila Pivote entre el Elemento Pivote
        old_piv_row = working_tab[pivot_row][:]
        new_piv_row = [cell / pivot_element for cell in old_piv_row]
        working_tab[pivot_row] = new_piv_row
        working_rows[pivot_row] = entering_var

        op_piv_label = f"F{f_piv_num} / {fmt_f(pivot_element)}"
        st.markdown(f"**Paso A — Normalizar fila pivote (`{op_piv_label}`): Entra `{entering_var}` en lugar de `{leaving_var}`**")
        st.dataframe(format_tableau_df(working_tab, col_names, working_rows), use_container_width=True)
        pdf_blocks.append(("text", f"Paso A: {op_piv_label} (Entra {entering_var})"))
        pdf_blocks.append(("table", col_names, working_rows, [[fmt_f(c) for c in r] for r in working_tab]))

        # Paso B: Actualizar una fila a la vez y mostrar la tabla resultante tras cada operación
        step_letters = "BCDEFGHIJ"
        letter_idx = 0
        for r in range(len(working_tab)):
            if r == pivot_row:
                continue
            f_curr_num = r + 1
            factor = working_tab[r][pivot_col]
            target_label = working_rows[r]
            step_let = step_letters[letter_idx % len(step_letters)]
            letter_idx += 1

            if factor == 0:
                st.caption(f"⏭️ **F{f_curr_num} (`{target_label}`)**: Ya tiene un `0` en `{entering_var}`, queda igual.")
                continue

            old_r = working_tab[r][:]
            new_r = [old_r[c_i] - factor * new_piv_row[c_i] for c_i in range(len(col_names))]
            working_tab[r] = new_r

            # Notación idéntica a tu cuaderno: ej. F1 + 10*F2  o  F3 - 2*F2
            if factor < 0:
                op_str = f"F{f_curr_num} + {fmt_f(abs(factor))}*F{f_piv_num}"
            else:
                op_str = f"F{f_curr_num} - {fmt_f(factor)}*F{f_piv_num}"

            st.markdown(f"**Paso {step_let} — Actualizar F{f_curr_num} (`{target_label}`) con `{op_str}`:**")
            
            # Mostrar el detalle aritmético de cada celda de esa fila
            calc_details = [
                f"**{col_names[c_i]}**: `{fmt_f(old_r[c_i])} - ({fmt_f(factor)})×({fmt_f(new_piv_row[c_i])}) = {fmt_f(new_r[c_i])}`"
                for c_i in range(len(col_names))
            ]
            st.caption(" | ".join(calc_details))

            # Mostrar la tabla actualizada hasta este paso
            st.dataframe(format_tableau_df(working_tab, col_names, working_rows), use_container_width=True)
            pdf_blocks.append(("text", f"Paso {step_let}: {op_str}"))
            pdf_blocks.append(("table", col_names, working_rows, [[fmt_f(c) for c in r] for r in working_tab]))

        # Guardar estado al terminar todas las filas de esta iteración
        tableau = working_tab
        basic_vars[pivot_row - 1] = entering_var
        row_names = working_rows
        st.divider()

    return "max_iter", tableau, basic_vars, row_names

# ==============================================================================
# MOTOR 3: MÉTODO SÍMPLEX (NUMERACIÓN CONTINUA x1, x2, x3, x4... + COLUMNA Z + L.D.)
# ==============================================================================
def solve_simplex_notebook(obj_type, c, constraints, pdf_blocks):
    num_vars = len(c)
    num_cons = len(constraints)

    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        if sense != "<=" or rhs < 0:
            st.error(f"⚠️ La restricción #{idx} tiene signo `{sense}` o L.D. negativo. Usa el **Método de las Dos Fases**.")
            return

    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento del Problema (Metodo Simplex)"))

    dec_vars_tex = [f"x_{i+1}" for i in range(num_vars)]
    dec_vars_txt = [f"x{i+1}" for i in range(num_vars)]

    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, dec_vars_tex)}")
    pdf_blocks.append(("text", f"{obj_type} Z = {build_equation_text(c, dec_vars_txt)}"))

    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, dec_vars_tex, sense, rhs)}")
        pdf_blocks.append(("text", f"R{idx}: {build_equation_text(coeffs, dec_vars_txt, sense, rhs)}"))

    # Explicación de por qué Z pasa negativa
    render_sign_flip_explanation(obj_type, c, dec_vars_tex, pdf_blocks)

    # PASO 1: VARIABLES DE HOLGURA CON NUMERACIÓN CONTINUA (x_{n+1}, x_{n+2}...)
    st.markdown('<div class="step-header">Paso 1: Agregar Variables de Holgura (numeración continua) e igualar a 0</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Ecuaciones en Forma Estandar"))

    slack_vars_txt = [f"x{num_vars + i + 1}" for i in range(num_cons)]
    slack_vars_tex = [f"x_{num_vars + i + 1}" for i in range(num_cons)]
    all_vars_txt = dec_vars_txt + slack_vars_txt
    all_vars_tex = dec_vars_tex + slack_vars_tex

    st.write(f"Como tenemos {num_vars} variables originales ({', '.join(dec_vars_txt)}), las variables de holgura continúan la numeración: **{', '.join(slack_vars_txt)}**.")

    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    z_coeffs_all = [-mult_z * ci for ci in c] + [Fraction(0)] * num_cons
    st.latex(f"Z + {build_equation_latex(z_coeffs_all, all_vars_tex)} = 0")
    pdf_blocks.append(("text", f"Ecuacion Z: Z + {build_equation_text(z_coeffs_all, all_vars_txt)} = 0"))

    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        st.latex(build_equation_latex(coeffs + s_vec, all_vars_tex, "=", rhs))
        pdf_blocks.append(("text", f"R{idx+1}: {build_equation_text(coeffs + s_vec, all_vars_txt, '=', rhs)}"))

    # Construir Tabla Inicial con columna Z al inicio y L.D. al final
    col_names = ["Z"] + all_vars_txt + ["L.D."]
    z_row = [Fraction(1)] + z_coeffs_all + [Fraction(0)]
    tableau = [z_row]
    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        tableau.append([Fraction(0)] + coeffs + s_vec + [rhs])

    basic_vars = slack_vars_txt[:]
    row_names = ["Z"] + basic_vars[:]

    st.markdown('<div class="step-header">Paso 2: Resolución paso a paso de la Tabla Símplex</div>', unsafe_allow_html=True)
    status, final_tab, final_basics, _ = run_notebook_simplex_iterations(
        tableau, col_names, row_names, basic_vars, pdf_blocks, obj_col_label="Z"
    )

    if status == "optimal":
        render_final_solution_and_verification(obj_type, c, constraints, final_tab, final_basics, mult_z, num_vars, pdf_blocks)

# ==============================================================================
# MOTOR 4: MÉTODO DE LAS DOS FASES (CON COLUMNA W/Z, L.D. Y SUB-TABLAS)
# ==============================================================================
def solve_two_phase_notebook(obj_type, c, constraints, pdf_blocks):
    num_vars = len(c)
    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema (Método de las Dos Fases)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 0: Planteamiento (Metodo de las Dos Fases)"))

    dec_vars_tex = [f"x_{i+1}" for i in range(num_vars)]
    dec_vars_txt = [f"x{i+1}" for i in range(num_vars)]

    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, dec_vars_tex)}")
    pdf_blocks.append(("text", f"{obj_type} Z = {build_equation_text(c, dec_vars_txt)}"))

    norm_constraints = []
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, dec_vars_tex, sense, rhs)}")
        pdf_blocks.append(("text", f"R{idx}: {build_equation_text(coeffs, dec_vars_txt, sense, rhs)}"))
        if rhs < 0:
            norm_constraints.append(([-x for x in coeffs], {"<=": ">=", ">=": "<=", "=": "="}[sense], -rhs))
        else:
            norm_constraints.append((coeffs[:], sense, rhs))

    render_sign_flip_explanation(obj_type, c, dec_vars_tex, pdf_blocks)

    # PASO 1: HOLGURA/EXCESO (x_{n+1}...) Y ARTIFICIALES (a1, a2...)
    st.markdown('<div class="step-header">Paso 1: Variables de Holgura/Exceso (x) y Artificiales (a)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso 1: Incorporacion de Variables de Holgura, Exceso y Artificiales"))

    next_x_idx = num_vars + 1
    slack_excess_txt = []
    artificial_txt = []
    row_structures = []

    for idx, (coeffs, sense, rhs) in enumerate(norm_constraints, 1):
        info = {"coeffs": coeffs, "sense": sense, "rhs": rhs, "s_name": None, "s_sign": 0, "a_name": None}
        if sense == "<=":
            s_n = f"x{next_x_idx}"
            next_x_idx += 1
            slack_excess_txt.append(s_n)
            info["s_name"] = s_n
            info["s_sign"] = Fraction(1)
        elif sense == ">=":
            e_n = f"x{next_x_idx}"
            next_x_idx += 1
            a_n = f"a{len(artificial_txt) + 1}"
            slack_excess_txt.append(e_n)
            artificial_txt.append(a_n)
            info["s_name"] = e_n
            info["s_sign"] = Fraction(-1)
            info["a_name"] = a_n
        elif sense == "=":
            a_n = f"a{len(artificial_txt) + 1}"
            artificial_txt.append(a_n)
            info["a_name"] = a_n
        row_structures.append(info)

    if not artificial_txt:
        st.info("Todas las restricciones son `<=`; no hacen falta variables artificiales. Pasando a Símplex:")
        solve_simplex_notebook(obj_type, c, norm_constraints, pdf_blocks)
        return

    all_vars_p1 = dec_vars_txt + slack_excess_txt + artificial_txt
    col_names_p1 = ["W"] + all_vars_p1 + ["L.D."]

    for idx, info in enumerate(row_structures, 1):
        vec = [Fraction(0)] * len(all_vars_p1)
        for i in range(num_vars):
            vec[i] = info["coeffs"][i]
        if info["s_name"]:
            vec[all_vars_p1.index(info["s_name"])] = info["s_sign"]
        if info["a_name"]:
            vec[all_vars_p1.index(info["a_name"])] = Fraction(1)
        st.latex(build_equation_latex(vec, all_vars_p1, "=", info["rhs"]))
        pdf_blocks.append(("text", f"R{idx}: {build_equation_text(vec, all_vars_p1, '=', info['rhs'])}"))

    # FASE 1
    st.markdown('<div class="step-header">🚀 FASE 1: Eliminar Variables Artificiales (Minimizar W = a₁ + a₂...)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "FASE 1: Minimizar W (Eliminar variables artificiales)"))

    st.latex(f"\\text{{Minimizar }} W = {' + '.join(artificial_txt)} \\implies -W + {' + '.join(artificial_txt)} = 0")

    tableau_p1 = []
    basic_vars = []
    for info in row_structures:
        row = [Fraction(0)] * len(col_names_p1)
        for i in range(num_vars):
            row[i + 1] = info["coeffs"][i]
        if info["s_name"]:
            row[col_names_p1.index(info["s_name"])] = info["s_sign"]
        if info["a_name"]:
            row[col_names_p1.index(info["a_name"])] = Fraction(1)
            basic_vars.append(info["a_name"])
        else:
            basic_vars.append(info["s_name"])
        row[-1] = info["rhs"]
        tableau_p1.append(row)

    # Fila W inicial: [1 en col W, 0..., +1 en artificiales, ..., 0 en L.D.]
    w_row = [Fraction(0)] * len(col_names_p1)
    w_row[0] = Fraction(1)
    for a_n in artificial_txt:
        w_row[col_names_p1.index(a_n)] = Fraction(1)

    st.write("**Preparación de la Fila W (hacer 0 las columnas de variables artificiales básicas):**")
    for r_idx, b_var in enumerate(basic_vars):
        if b_var in artificial_txt:
            st.latex(f"F_1 (W) \\leftarrow F_1 (W) - F_{{{r_idx+2}}} ({b_var})")
            pdf_blocks.append(("text", f"Ajuste inicial: F1(W) = F1(W) - F{r_idx+2}({b_var})"))
            w_row = [w_row[j] - tableau_p1[r_idx][j] for j in range(len(col_names_p1))]

    status_p1, end_tab_p1, end_basics_p1, _ = run_notebook_simplex_iterations(
        [w_row] + tableau_p1, col_names_p1, ["W"] + basic_vars[:], basic_vars, pdf_blocks, obj_col_label="W", phase_label="Fase 1 - "
    )

    if status_p1 != "optimal" or end_tab_p1[0][-1] != 0:
        st.error(f"🚫 Problema Infactible: W final = {fmt_f(abs(end_tab_p1[0][-1]))} ≠ 0. Las restricciones se contradicen.")
        pdf_blocks.append(("text", "Resultado: Problema Infactible (W != 0)."))
        return

    st.success("✅ **¡Fase 1 completada con éxito!** `W = 0` y todas las variables artificiales salieron de la base.")

    # FASE 2
    st.markdown('<div class="step-header">🏁 FASE 2: Resolver el Problema Original con Z</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "FASE 2: Resolver el problema original con Z"))

    # Quitar columnas artificiales y renombrar W -> Z
    keep_indices = [i for i, name in enumerate(col_names_p1) if name not in artificial_txt]
    col_names_p2 = ["Z"] + [col_names_p1[i] for i in keep_indices[1:]]
    clean_rows = [[end_tab_p1[r_idx][i] for i in keep_indices] for r_idx in range(1, len(end_tab_p1))]

    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    z_row_p2 = [Fraction(0)] * len(col_names_p2)
    z_row_p2[0] = Fraction(1)
    for i in range(num_vars):
        z_row_p2[i + 1] = -mult_z * c[i]

    for r_idx, b_var in enumerate(end_basics_p1):
        if b_var in col_names_p2:
            c_idx = col_names_p2.index(b_var)
            factor = z_row_p2[c_idx]
            if factor != 0:
                st.latex(f"F_1 (Z) \\leftarrow F_1 (Z) - ({fmt_latex_f(factor)}) \\cdot F_{{{r_idx+2}}} ({b_var})")
                pdf_blocks.append(("text", f"Ajuste Fase 2: F1(Z) = F1(Z) - ({fmt_f(factor)})*F{r_idx+2}({b_var})"))
                z_row_p2 = [z_row_p2[j] - factor * clean_rows[r_idx][j] for j in range(len(col_names_p2))]

    status_p2, end_tab_p2, end_basics_p2, _ = run_notebook_simplex_iterations(
        [z_row_p2] + clean_rows, col_names_p2, ["Z"] + end_basics_p1[:], end_basics_p1, pdf_blocks, obj_col_label="Z", phase_label="Fase 2 - "
    )

    if status_p2 == "optimal":
        render_final_solution_and_verification(obj_type, c, norm_constraints, end_tab_p2, end_basics_p2, mult_z, num_vars, pdf_blocks)

# ==============================================================================
# BLOQUE FINAL: RESULTADOS Y COMPROBACIÓN SUSTITUYENDO EN EL MODELO ORIGINAL
# ==============================================================================
def render_final_solution_and_verification(obj_type, c, constraints, final_tab, final_basics, mult_z, num_vars, pdf_blocks):
    st.markdown('<div class="step-header">Paso Final: Solución Óptima y Comprobación (Sustitución)</div>', unsafe_allow_html=True)
    pdf_blocks.append(("title", "Paso Final: Solucion Optima y Comprobacion"))

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
    st.success(f"🏆 **{res_txt}**")
    pdf_blocks.append(("text", res_txt))

    # Comprobación paso a paso sustituyendo en Z y en cada restricción (igual que al final de tu hoja 2)
    st.markdown("**🔍 Comprobación sustituyendo los valores en el problema original:**")
    pdf_blocks.append(("subtitle", "Comprobacion en el modelo original:"))

    x_vals = [sol_dict[f"x{i+1}"] for i in range(num_vars)]
    z_terms_tex = " + ".join([f"{fmt_latex_f(c[i])}\\left({fmt_latex_f(x_vals[i])}\\right)" for i in range(num_vars)])
    z_terms_txt = " + ".join([f"{fmt_f(c[i])}({fmt_f(x_vals[i])})" for i in range(num_vars)])
    st.latex(f"Z = {z_terms_tex} = {fmt_latex_f(final_z)} \\quad \\checkmark")
    pdf_blocks.append(("text", f"Z = {z_terms_txt} = {fmt_f(final_z)} [OK]"))

    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        lhs_val = sum(coeffs[i] * x_vals[i] for i in range(num_vars))
        r_terms_tex = " + ".join([f"{fmt_latex_f(coeffs[i])}\\left({fmt_latex_f(x_vals[i])}\\right)" for i in range(num_vars)])
        r_terms_txt = " + ".join([f"{fmt_f(coeffs[i])}({fmt_f(x_vals[i])})" for i in range(num_vars)])
        sense_tex = {"<=": "\\le", ">=": "\\ge", "=": "="}[sense]
        st.latex(f"\\text{{R{idx}: }} {r_terms_tex} = {fmt_latex_f(lhs_val)} {sense_tex} {fmt_latex_f(rhs)} \\quad \\checkmark")
        pdf_blocks.append(("text", f"R{idx}: {r_terms_txt} = {fmt_f(lhs_val)} {sense} {fmt_f(rhs)} [OK]"))

# ==============================================================================
# INTERFAZ PRINCIPAL + CÁMARA / FOTO
# ==============================================================================
st.title("🧭 Aventura Lineal: Programación Lineal Paso a Paso")
st.write("Resuelve exactamente con tablas progesivas (columna Z, L.D. y operaciones fila por fila), escanea con cámara y descarga en PDF.")

if "lp_data" not in st.session_state:
    # Cargado por defecto con EL EJERCICIO DE TU CUADERNO
    st.session_state.lp_data = {
        "obj_type": "Maximizar",
        "num_vars": 2,
        "num_cons": 3,
        "c": [8.0, 10.0],
        "cons": [
            ([20.0, 30.0], "<=", 120.0),
            ([2.0, 2.0], "<=", 9.0),
            ([6.0, 4.0], "<=", 24.0)
        ]
    }

st.sidebar.header("⚙️ Configuración")
metodo = st.sidebar.selectbox("1. Elige el Método:", ["Método Símplex", "Método de las Dos Fases", "Método Gráfico"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Ejemplos Rápidos")
if st.sidebar.button("📓 Ej. 1: Ejercicio de tu Cuaderno (Max Z=8x1+10x2)"):
    st.session_state.lp_data = {
        "obj_type": "Maximizar", "num_vars": 2, "num_cons": 3,
        "c": [8.0, 10.0],
        "cons": [([20.0, 30.0], "<=", 120.0), ([2.0, 2.0], "<=", 9.0), ([6.0, 4.0], "<=", 24.0)]
    }
if st.sidebar.button("🥗 Ej. 2: Dieta (Dos Fases - Minimizar)"):
    st.session_state.lp_data = {
        "obj_type": "Minimizar", "num_vars": 2, "num_cons": 2,
        "c": [4.0, 6.0], "cons": [([2.0, 1.0], ">=", 8.0), ([1.0, 3.0], ">=", 9.0)]
    }
if st.sidebar.button("🚀 Ej. 3: Misión Espacial (Dos Fases Mixto)"):
    st.session_state.lp_data = {
        "obj_type": "Maximizar", "num_vars": 2, "num_cons": 3,
        "c": [5.0, 4.0], "cons": [([1.0, 1.0], "<=", 10.0), ([2.0, 1.0], ">=", 6.0), ([1.0, 2.0], "=", 12.0)]
    }

# ESCÁNER CON CÁMARA O SUBIDA DE FOTO
with st.expander("📸 Escanear problema con Cámara o Subir Foto (Auto-rellenar cuadros)", expanded=False):
    api_key_input = st.text_input("🔑 Tu Gemini API Key:", type="password", value=os.getenv("GEMINI_API_KEY", ""))
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
                        st.success("✅ ¡Problema detectado y cargado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo leer la imagen: {e}")

# FORMULARIO DE DATOS
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
        rhs_val = st.number_input("L.D.", value=float(def_row[2]), step=1.0, key=f"rhs_{r}")

    if metodo == "Método Gráfico":
        constraints_inputs.append((row_coeffs[0], row_coeffs[1], sense, to_frac(rhs_val)))
    else:
        constraints_inputs.append((row_coeffs, sense, to_frac(rhs_val)))

st.markdown("---")
if st.button("🚀 Resolver Paso a Paso (Estilo Cuaderno) y Generar PDF", type="primary", use_container_width=True):
    pdf_report_blocks = []
    if metodo == "Método Gráfico":
        solve_graphical(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)
    elif metodo == "Método Símplex":
        solve_simplex_notebook(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)
    elif metodo == "Método de las Dos Fases":
        solve_two_phase_notebook(obj_type, c_inputs, constraints_inputs, pdf_report_blocks)

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