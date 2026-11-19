import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fractions import Fraction
from itertools import combinations

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="Aventura Lineal: Aprende Programación Lineal Paso a Paso",
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
# FUNCIONES AUXILIARES DE FORMATO Y FRACCIONES EXACTAS
# ==============================================================================
def to_frac(val):
    """Convierte un número flotante o entero a Fraction exacto."""
    return Fraction(str(val)).limit_denominator(10000)

def fmt_f(val):
    """Formatea una fracción como cadena limpia (ej. 3/2 o 4)."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"{val.numerator}/{val.denominator}"
    return str(val)

def fmt_latex_f(val):
    """Formatea una fracción en LaTeX bonito."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        if val.numerator < 0:
            return f"-\\frac{{{abs(val.numerator)}}}{{{val.denominator}}}"
        return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
    return str(val)

def format_tableau_df(matrix, col_names, row_names):
    """Convierte una matriz de Fractions a DataFrame legible para Streamlit."""
    str_data = [[fmt_f(cell) for cell in row] for row in matrix]
    return pd.DataFrame(str_data, columns=col_names, index=row_names)

def build_equation_latex(coeffs, var_names, sense=None, rhs=None):
    """Construye una expresión lineal en LaTeX sin signos raros."""
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
# MOTOR 1: MÉTODO GRÁFICO (2 VARIABLES)
# ==============================================================================
def solve_graphical(obj_type, c, constraints):
    """
    Resuelve y explica paso a paso el Método Gráfico para 2 variables (x1, x2).
    constraints: lista de tuplas (a1, a2, sense, b)
    """
    st.markdown('<div class="step-header">Paso 0: Entendiendo nuestra misión (Planteamiento)</div>', unsafe_allow_html=True)
    
    accion = "ganar la MAYOR cantidad de monedas/puntos" if obj_type == "Maximizar" else "gastar la MENOR cantidad de energía/dinero"
    st.markdown(f"""
    <div class="kid-box">
    <b>🎒 Imagina esta historia:</b><br>
    Tenemos dos decisiones mágicas que tomar: cuánto fabricar o usar de <b>x₁</b> y cuánto de <b>x₂</b> (siempre cantidades positivas o cero, porque no podemos fabricar "-3 juguetes").<br>
    Nuestra meta es <b>{accion}</b> siguiendo esta fórmula mágica (llamada <i>Función Objetivo</i>):
    </div>
    """, unsafe_allow_html=True)
    
    z_latex = build_equation_latex(c, ["x_1", "x_2"])
    st.latex(f"\\text{{{obj_type} }} Z = {z_latex}")

    st.write("**Nuestras reglas del juego (Restricciones):** No podemos romper ninguna de estas condiciones:")
    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        eq_tex = build_equation_latex([a1, a2], ["x_1", "x_2"], sense, b)
        regla_txt = {
            "<=": "no pasarnos de este límite (como no gastar más fichas de las que tenemos).",
            ">=": "cumplir al menos con este mínimo (como hacer al menos cierta tarea).",
            "=": "caer exactamente sobre esta línea (ni más ni menos)."
        }[sense]
        st.latex(f"\\text{{Regla {idx}: }} {eq_tex}")
        st.caption(f"👉 Esto significa que debemos {regla_txt}")
    st.latex("x_1 \\ge 0, \\quad x_2 \\ge 0 \\quad \\text{(No existen cosas negativas)}")

    # PASO 1: DIBUJAR CADA RECTA (CRUCES CON EJES)
    st.markdown('<div class="step-header">Paso 1: Convertir cada regla en una línea recta en el mapa</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kid-box">
    <b>📏 ¿Cómo dibujamos una línea recta?</b><br>
    Para dibujar una línea solo necesitamos <b>dos puntos</b> y unirlos con una regla. Los puntos más fáciles de encontrar son donde la línea choca contra las paredes del mapa (los ejes):<br>
    1. Si ponemos <b>x₁ = 0</b>, vemos dónde choca con el eje vertical (<b>x₂</b>).<br>
    2. Si ponemos <b>x₂ = 0</b>, vemos dónde choca con el eje horizontal (<b>x₁</b>).
    </div>
    """, unsafe_allow_html=True)

    all_lines = [] # (a1, a2, b, nombre)
    for idx, (a1, a2, sense, b) in enumerate(constraints, 1):
        all_lines.append((a1, a2, b, f"R{idx}"))
        with st.expander(f"🔍 Ver cálculo de puntos para la Regla {idx}: {fmt_f(a1)}x₁ + {fmt_f(a2)}x₂ = {fmt_f(b)}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**1. Si x₁ = 0 (nos pegamos a la pared vertical):**")
                if a2 != 0:
                    x2_val = b / a2
                    st.latex(f"{fmt_latex_f(a1)}(0) + {fmt_latex_f(a2)}x_2 = {fmt_latex_f(b)} \\implies x_2 = \\frac{{{fmt_latex_f(b)}}}{{{fmt_latex_f(a2)}}} = {fmt_latex_f(x2_val)}")
                    st.write(f"📍 Punto A: **(0, {fmt_f(x2_val)})**")
                else:
                    st.write(f"Como no hay x₂, esta es una línea completamente vertical en **x₁ = {fmt_f(b/a1)}**.")
            with col2:
                st.write("**2. Si x₂ = 0 (nos quedamos en el suelo horizontal):**")
                if a1 != 0:
                    x1_val = b / a1
                    st.latex(f"{fmt_latex_f(a1)}x_1 + {fmt_latex_f(a2)}(0) = {fmt_latex_f(b)} \\implies x_1 = \\frac{{{fmt_latex_f(b)}}}{{{fmt_latex_f(a1)}}} = {fmt_latex_f(x1_val)}")
                    st.write(f"📍 Punto B: **({fmt_f(x1_val)}, 0)**")
                else:
                    st.write(f"Como no hay x₁, esta es una línea completamente horizontal en **x₂ = {fmt_f(b/a2)}**.")

            # Prueba del origen (0,0) para saber qué lado colorear
            if sense != "=":
                lhs_origin = a1 * 0 + a2 * 0
                cumple = (lhs_origin <= b) if sense == "<=" else (lhs_origin >= b)
                st.write(f"**¿Qué lado de la línea vale? Probamos el punto (0, 0):**")
                st.write(f"Sustituimos (0,0): `{fmt_f(a1)}(0) + {fmt_f(a2)}(0) = 0`. ¿Es `0 {sense} {fmt_f(b)}`? **{'¡SÍ cumple!' if cumple else 'NO cumple'}**")
                if cumple:
                    st.write("🎨 Por eso, la zona válida está **hacia el lado donde está el origen (0,0)**.")
                else:
                    st.write("🎨 Por eso, la zona válida está **hacia el lado contrario al origen (0,0)**.")

    # Agregar ejes x1 = 0 y x2 = 0 como líneas límite para buscar intersecciones
    all_lines.append((Fraction(1), Fraction(0), Fraction(0), "Eje x₂ (x₁=0)"))
    all_lines.append((Fraction(0), Fraction(1), Fraction(0), "Eje x₁ (x₂=0)"))

    # PASO 2: ENCONTRAR TODAS LAS INTERSECCIONES Y FILTRAR LA REGIÓN FACTIBLE
    st.markdown('<div class="step-header">Paso 2: Encontrar la "Zona Permitida" (Región Factible) y sus esquinas</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kid-box">
    <b>🏰 ¿Qué es la Región Factible y por qué importan las esquinas?</b><br>
    Cuando pintamos todas las reglas juntas, el lugar donde <b>TODOS los colores se mezclan</b> es nuestro castillo seguro: la <b>Región Factible</b>.<br>
    Un súper secreto de las matemáticas dice que <b>el mejor tesoro SIEMPRE está escondido en una de las esquinas (vértices)</b> de ese castillo. ¡Así que vamos a calcular cada cruce de líneas y ver cuáles esquinas sí están dentro del castillo!
    </div>
    """, unsafe_allow_html=True)

    candidate_points = []
    intersection_logs = []

    for (l1, l2) in combinations(all_lines, 2):
        a1, a2, b1, name1 = l1
        c1, c2, b2, name2 = l2
        det = a1 * c2 - a2 * c1
        if det == 0:
            continue # Líneas paralelas
        x1 = (b1 * c2 - a2 * b2) / det
        x2 = (a1 * b2 - b1 * c1) / det

        # Verificar si cumple TODAS las restricciones y no negatividad
        tol = Fraction(1, 10**9)
        is_feasible = (x1 >= -tol) and (x2 >= -tol)
        failed_reasons = []
        if x1 < -tol or x2 < -tol:
            failed_reasons.append("tiene coordenadas negativas")

        for r_idx, (ra1, ra2, rsense, rb) in enumerate(constraints, 1):
            val = ra1 * x1 + ra2 * x2
            if rsense == "<=" and val > rb + tol:
                is_feasible = False
                failed_reasons.append(f"rompe Regla {r_idx} ({fmt_f(val)} > {fmt_f(rb)})")
            elif rsense == ">=" and val < rb - tol:
                is_feasible = False
                failed_reasons.append(f"rompe Regla {r_idx} ({fmt_f(val)} < {fmt_f(rb)})")
            elif rsense == "=" and abs(val - rb) > tol:
                is_feasible = False
                failed_reasons.append(f"rompe Regla {r_idx} ({fmt_f(val)} ≠ {fmt_f(rb)})")

        intersection_logs.append({
            "Cruce": f"{name1} con {name2}",
            "Punto (x₁, x₂)": f"({fmt_f(x1)}, {fmt_f(x2)})",
            "¿Es esquina válida?": "✅ SÍ (Vértice Factible)" if is_feasible else f"❌ NO ({', '.join(failed_reasons)})",
            "x1": x1,
            "x2": x2,
            "feasible": is_feasible
        })

        if is_feasible:
            # Evitar duplicados exactos
            if not any(p[0] == x1 and p[1] == x2 for p in candidate_points):
                candidate_points.append((x1, x2))

    st.write("**Tabla de todos los cruces de líneas revisados uno por uno:**")
    log_df = pd.DataFrame(intersection_logs)[["Cruce", "Punto (x₁, x₂)", "¿Es esquina válida?"]]
    st.dataframe(log_df, use_container_width=True, hide_index=True)

    if not candidate_points:
        st.markdown("""
        <div class="warn-box">
        <b>🚫 ¡Ups! No existe ninguna esquina válida (Problema Infactible).</b><br>
        Las reglas se contradicen entre sí, como pedirte que tengas <i>menos de 3 manzanas</i> y al mismo tiempo <i>más de 5 manzanas</i>. No hay zona permitida.
        </div>
        """, unsafe_allow_html=True)
        return

    # Ordenar vértices en sentido antihorario alrededor de su centroide para dibujarlos bonito
    cx = sum(p[0] for p in candidate_points) / len(candidate_points)
    cy = sum(p[1] for p in candidate_points) / len(candidate_points)
    candidate_points.sort(key=lambda p: np.arctan2(float(p[1] - cy), float(p[0] - cx)))

    # PASO 3: DIBUJAR EL MAPA CON MATPLOTLIB
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Determinar límites del gráfico
    max_x = max([float(p[0]) for p in candidate_points] + [float(b/a1) for a1, a2, _, b in constraints if a1 > 0 and b > 0] + [5.0]) * 1.25
    max_y = max([float(p[1]) for p in candidate_points] + [float(b/a2) for a1, a2, _, b in constraints if a2 > 0 and b > 0] + [5.0]) * 1.25
    
    x_vals = np.linspace(0, max_x, 400)
    colors = ['#1f77b4', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2']

    for idx, (a1, a2, sense, b) in enumerate(constraints):
        col = colors[idx % len(colors)]
        lbl = f"R{idx+1}: {fmt_f(a1)}x₁ + {fmt_f(a2)}x₂ {sense} {fmt_f(b)}"
        if a2 != 0:
            y_vals = (float(b) - float(a1) * x_vals) / float(a2)
            ax.plot(x_vals, y_vals, label=lbl, color=col, linewidth=2)
        else:
            x_const = float(b / a1)
            ax.axvline(x=x_const, label=lbl, color=col, linewidth=2)

    # Rellenar región factible si tiene al menos 3 puntos (polígono)
    if len(candidate_points) >= 3:
        poly_x = [float(p[0]) for p in candidate_points]
        poly_y = [float(p[1]) for p in candidate_points]
        ax.fill(poly_x, poly_y, color='#2ecc71', alpha=0.35, label='Región Factible (Zona Permitida)')
    elif len(candidate_points) == 2:
        ax.plot([float(candidate_points[0][0]), float(candidate_points[1][0])],
                [float(candidate_points[0][1]), float(candidate_points[1][1])],
                color='#2ecc71', linewidth=5, label='Segmento Factible')

    # Dibujar vértices
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, (vx, vy) in enumerate(candidate_points):
        letra = letras[i % len(letras)]
        ax.scatter(float(vx), float(vy), color='#d62728', zorder=5, s=80)
        ax.annotate(f"{letra} ({fmt_f(vx)}, {fmt_f(vy)})",
                    (float(vx), float(vy)),
                    textcoords="offset points", xytext=(8, 8),
                    fontweight='bold', fontsize=10, color='#b71c1c')

    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.set_xlabel("Variable x₁", fontsize=11, fontweight='bold')
    ax.set_ylabel("Variable x₂", fontsize=11, fontweight='bold')
    ax.set_title("Mapa de la Región Factible y sus Esquinas", fontsize=13, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    st.pyplot(fig)

    # PASO 4: EVALUAR CADA ESQUINA EN LA FUNCIÓN OBJETIVO
    st.markdown('<div class="step-header">Paso 3: Probar cada esquina en nuestra fórmula mágica (Evaluación)</div>', unsafe_allow_html=True)
    st.write("Ahora vamos esquina por esquina metiendo sus números en $Z$ para ver cuál gana:")

    eval_rows = []
    best_val = None
    best_points = []

    for i, (vx, vy) in enumerate(candidate_points):
        letra = letras[i % len(letras)]
        z_val = c[0] * vx + c[1] * vy
        calculo_str = f"{fmt_f(c[0])}({fmt_f(vx)}) + {fmt_f(c[1])}({fmt_f(vy)}) = {fmt_f(c[0]*vx)} + {fmt_f(c[1]*vy)} = {fmt_f(z_val)}"
        eval_rows.append({
            "Esquina": letra,
            "Coordenadas (x₁, x₂)": f"({fmt_f(vx)}, {fmt_f(vy)})",
            "Sustitución paso a paso": calculo_str,
            "Valor de Z": fmt_f(z_val),
            "z_num": z_val
        })

        if best_val is None:
            best_val = z_val
            best_points = [(letra, vx, vy)]
        else:
            if (obj_type == "Maximizar" and z_val > best_val) or (obj_type == "Minimizar" and z_val < best_val):
                best_val = z_val
                best_points = [(letra, vx, vy)]
            elif z_val == best_val:
                best_points.append((letra, vx, vy))

    st.dataframe(pd.DataFrame(eval_rows)[["Esquina", "Coordenadas (x₁, x₂)", "Sustitución paso a paso", "Valor de Z"]],
                 use_container_width=True, hide_index=True)

    # Nota sobre acotamiento
    ganadores_txt = ", ".join([f"**Esquina {l} ({fmt_f(px)}, {fmt_f(py)})**" for l, px, py in best_points])
    st.success(f"🏆 **¡Tesoro encontrado!** Como queremos **{obj_type.lower()}**, la mejor solución está en {ganadores_txt} con un valor óptimo de **Z = {fmt_f(best_val)}**.")
    if len(best_points) > 1:
        st.info("💡 **Dato curioso:** ¡Hay un empate entre dos esquinas! Eso significa que cualquier punto sobre la línea que une esas dos esquinas también da el mismo resultado óptimo (soluciones múltiples).")

# ==============================================================================
# MOTOR 2: PIVOTEO Y TABLAS SIMPLEX DETALLADAS (COMPARTIDO POR SIMPLEX Y 2 FASES)
# ==============================================================================
def run_simplex_iterations(tableau, col_names, row_names, basic_vars, obj_type_internal="max", phase_label=""):
    """
    Ejecuta iteraciones del Método Símplex mostrando:
    - Tabla actual
    - Elección de columna pivote y explicación
    - Cálculo exacto de cocientes para fila pivote
    - Operaciones elementales fila por fila escritas explícitamente
    Retorna: (status, final_tableau, final_basic_vars, final_row_names)
    status puede ser: 'optimal', 'unbounded', 'max_iter'
    """
    iteration = 0
    max_iterations = 25

    while iteration < max_iterations:
        iteration += 1
        st.markdown(f"#### 🔄 {phase_label}Iteración #{iteration}")

        # Mostrar tabla actual
        df_curr = format_tableau_df(tableau, col_names, row_names)
        st.dataframe(df_curr, use_container_width=True)

        # Fila Z es la fila 0
        z_row = tableau[0][:-1] # Excluir RHS

        # En formato estándar de maximización: Z - c1*x1 - c2*x2 = 0
        # Buscamos el coeficiente MÁS NEGATIVO en la fila Z para entrar a la base.
        min_coeff = min(z_row)
        if min_coeff >= 0:
            st.markdown("""
            <div class="kid-box">
            <b>🎉 ¡Llegamos a la cima!</b><br>
            Mira la fila <b>Z</b> (la fila de arriba): ya <b>no queda ningún número negativo</b>.<br>
            Eso significa que ninguna variable nueva puede mejorar nuestro puntaje. ¡Hemos terminado esta etapa!
            </div>
            """, unsafe_allow_html=True)
            return "optimal", tableau, basic_vars, row_names

        # Elegir columna pivote (más negativo; desempate por menor índice - Regla de Bland)
        pivot_col = z_row.index(min_coeff)
        entering_var = col_names[pivot_col]

        st.markdown(f"""
        **1️⃣ Elegir la Columna Pivote (¿Quién entra al equipo?):**
        - Revisamos la fila **Z** buscando el número **más negativo** (el que más nos ayuda a subir Z).
        - El más negativo es **{fmt_f(min_coeff)}** en la columna de **{entering_var}**.
        - 👉 **Columna Pivote = `{entering_var}`** (Columna #{pivot_col + 1}).
        """)

        # Calcular cocientes (RHS / elemento en columna pivote) para filas de restricciones (1..m)
        st.markdown("**2️⃣ Elegir la Fila Pivote (¿Quién sale del equipo? - Prueba del Cociente):**")
        st.write(f"Dividimos el resultado derecho (**RHS**) entre el número positivo de la columna **{entering_var}** para no pasarnos de ningún límite:")

        ratios = []
        ratio_logs = []
        for r in range(1, len(tableau)):
            rhs_val = tableau[r][-1]
            col_val = tableau[r][pivot_col]
            b_var = basic_vars[r - 1]
            if col_val > 0:
                ratio = rhs_val / col_val
                ratios.append((ratio, r))
                ratio_logs.append(f"- Fila **{b_var}**: `{fmt_f(rhs_val)} ÷ {fmt_f(col_val)} = {fmt_f(ratio)}` ✅ (Válido)")
            else:
                ratio_logs.append(f"- Fila **{b_var}**: `{fmt_f(rhs_val)} ÷ {fmt_f(col_val)}` ❌ (No se divide entre cero o negativos)")

        for log in ratio_logs:
            st.markdown(log)

        if not ratios:
            st.markdown("""
            <div class="warn-box">
            <b>🚀 ¡Problema No Acotado!</b><br>
            Todos los números en la columna pivote son cero o negativos. Eso significa que podemos hacer crecer <b>Z</b> hacia el infinito sin romper ninguna regla. ¡No hay un tope máximo!
            </div>
            """, unsafe_allow_html=True)
            return "unbounded", tableau, basic_vars, row_names

        # Elegir el menor cociente no negativo
        min_ratio, pivot_row = min(ratios, key=lambda x: x[0])
        leaving_var = basic_vars[pivot_row - 1]
        pivot_element = tableau[pivot_row][pivot_col]

        st.markdown(f"""
        - El cociente más pequeño es **{fmt_f(min_ratio)}**, que pertenece a la fila de **{leaving_var}**.
        - 👉 **Fila Pivote = Fila `{leaving_var}`** (sale `{leaving_var}` y entra `{entering_var}`).
        - 🎯 **Elemento Pivote = `{fmt_f(pivot_element)}`** (el cruce entre la columna `{entering_var}` y la fila `{leaving_var}`).
        """)

        # PASO 3: OPERACIONES DE FILA PASO A PASO (GAUSS-JORDAN)
        st.markdown("**3️⃣ Hacer magia con las filas (Operaciones de Gauss-Jordan):**")
        st.write("Queremos que el **Elemento Pivote** se convierta en **1**, y que todos los demás números arriba y abajo en su columna se vuelvan **0**:")

        new_tableau = [row[:] for row in tableau]
        
        # A) Normalizar fila pivote
        old_pivot_row = tableau[pivot_row][:]
        new_pivot_row = [cell / pivot_element for cell in old_pivot_row]
        new_tableau[pivot_row] = new_pivot_row

        with st.expander(f"📝 Ver TODAS las cuentas de las filas en esta iteración #{iteration}", expanded=True):
            st.markdown(f"**Paso A: Convertir el Elemento Pivote (`{fmt_f(pivot_element)}`) en `1`**")
            if pivot_element == 1:
                st.write(f"El elemento pivote ya es `1`, así que la **Nueva Fila {entering_var}** queda igual:")
            else:
                st.latex(f"\\text{{Nueva Fila }}_{{{entering_var}}} = \\frac{{\\text{{Fila }}_{{{leaving_var}}}}}{{{fmt_latex_f(pivot_element)}}}")
            
            old_str = "[" + ", ".join(fmt_f(x) for x in old_pivot_row) + "]"
            new_str = "[" + ", ".join(fmt_f(x) for x in new_pivot_row) + "]"
            st.code(f"Antes : {old_str}\nDespués: {new_str}")

            st.markdown(f"**Paso B: Convertir en `0` los demás números de la columna `{entering_var}`**")
            for r in range(len(tableau)):
                if r == pivot_row:
                    continue
                target_name = row_names[r]
                factor = tableau[r][pivot_col]
                old_r = tableau[r][:]
                if factor == 0:
                    st.write(f"- **Fila `{target_name}`**: Ya tiene un `0` en la columna `{entering_var}`, ¡no necesita cambios!")
                    continue
                
                new_r = [old_r[c_i] - factor * new_pivot_row[c_i] for c_i in range(len(col_names))]
                new_tableau[r] = new_r

                sign_op = "-" if factor > 0 else "+"
                abs_fac = abs(factor)
                st.latex(f"\\text{{Nueva Fila }}_{{{target_name}}} = \\text{{Fila }}_{{{target_name}}} {sign_op} ({fmt_latex_f(abs_fac)}) \\times \\text{{Nueva Fila }}_{{{entering_var}}}")
                
                # Mostrar cálculo elemento por elemento
                elem_calcs = []
                for c_i, c_name in enumerate(col_names):
                    calc_detail = f"{c_name}: {fmt_f(old_r[c_i])} - ({fmt_f(factor)})*({fmt_f(new_pivot_row[c_i])}) = {fmt_f(new_r[c_i])}"
                    elem_calcs.append(calc_detail)
                st.code(" | ".join(elem_calcs))

        # Actualizar estado de tabla y variables básicas
        tableau = new_tableau
        basic_vars[pivot_row - 1] = entering_var
        row_names[pivot_row] = entering_var
        st.divider()

    return "max_iter", tableau, basic_vars, row_names

# ==============================================================================
# MOTOR 3: PREPARACIÓN Y RESOLUCIÓN SIMPLEX ESTÁNDAR
# ==============================================================================
def solve_simplex_standard(obj_type, c, constraints):
    """
    Resuelve problemas con restricciones <= y RHS >= 0 usando Método Símplex Estándar.
    """
    num_vars = len(c)
    num_cons = len(constraints)

    # Validar si cumple condiciones de Símplex estándar puro
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        if sense != "<=" or rhs < 0:
            st.error(f"⚠️ La restricción #{idx} tiene signo `{sense}` o lado derecho negativo (`{fmt_f(rhs)}`). El **Método Símplex Estándar** solo acepta restricciones `≤` con lado derecho positivo o cero. ¡Usa el **Método de las Dos Fases** en el menú de la izquierda para resolver este problema!")
            return

    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema</div>', unsafe_allow_html=True)
    var_names = [f"x_{i+1}" for i in range(num_vars)]
    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, var_names)}")
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, var_names, sense, rhs)}")

    st.markdown('<div class="step-header">Paso 1: Convertir desigualdades en igualdades (Variables de Holgura)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kid-box">
    <b>🎒 ¿Qué es una Variable de Holgura (s₁, s₂...)?</b><br>
    Imagina que tienes una mochila donde caben <b>10 manzanas</b> (<code>x₁ + x₂ ≤ 10</code>). Si solo metes 7 manzanas, te sobra espacio para 3.<br>
    A ese <b>espacio que sobra</b> lo llamamos <b>Variable de Holgura (s)</b>. Así podemos escribir una igualdad exacta: <code>x₁ + x₂ + s₁ = 10</code>. ¡Como es espacio vacío, vale 0 puntos en Z!
    </div>
    """, unsafe_allow_html=True)

    # Si es Minimizar, recordamos que Min Z = - Max (-Z)
    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    if obj_type == "Minimizar":
        st.info("💡 **Truco para Minimizar:** Minimizar $Z$ es exactamente lo mismo que Maximizar $W = -Z$. Al final solo le cambiamos el signo al resultado.")

    slack_names = [f"s_{i+1}" for i in range(num_cons)]
    all_col_names = [f"x{i+1}" for i in range(num_vars)] + [f"s{i+1}" for i in range(num_cons)] + ["RHS"]
    
    # Mostrar ecuaciones en forma estándar
    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        st.latex(build_equation_latex(coeffs + s_vec, var_names + slack_names, "=", rhs))

    # Construir Tabla Inicial
    # Fila 0: Z - c1*x1 - c2*x2 ... = 0  (si mult_z = -1, Z + c1*x1 ... = 0)
    z_row = [-mult_z * ci for ci in c] + [Fraction(0)] * num_cons + [Fraction(0)]
    tableau = [z_row]
    for idx, (coeffs, sense, rhs) in enumerate(constraints):
        s_vec = [Fraction(1) if j == idx else Fraction(0) for j in range(num_cons)]
        tableau.append(coeffs + s_vec + [rhs])

    basic_vars = [f"s{i+1}" for i in range(num_cons)]
    row_names = ["Z"] + basic_vars[:]

    st.markdown('<div class="step-header">Paso 2: Iteraciones de la Tabla Símplex</div>', unsafe_allow_html=True)
    status, final_tab, final_basics, _ = run_simplex_iterations(tableau, all_col_names, row_names, basic_vars)

    if status == "optimal":
        st.markdown('<div class="step-header">Paso 3: Leer la Solución Final</div>', unsafe_allow_html=True)
        sol_dict = {f"x{i+1}": Fraction(0) for i in range(num_vars)}
        for r_idx, b_var in enumerate(final_basics, 1):
            if b_var in sol_dict:
                sol_dict[b_var] = final_tab[r_idx][-1]
        
        raw_z = final_tab[0][-1]
        final_z = raw_z * mult_z

        cols = st.columns(num_vars + 1)
        for i in range(num_vars):
            v_key = f"x{i+1}"
            cols[i].metric(label=f"Variable {v_key}", value=fmt_f(sol_dict[v_key]))
        cols[-1].metric(label=f"Valor Óptimo Z ({obj_type})", value=fmt_f(final_z))

        st.success(f"🎊 **¡Resuelto!** Los valores óptimos son: " + ", ".join([f"**{k} = {fmt_f(v)}**" for k, v in sol_dict.items()]) + f" con **Z = {fmt_f(final_z)}**.")

# ==============================================================================
# MOTOR 4: MÉTODO DE LAS DOS FASES
# ==============================================================================
def solve_two_phase(obj_type, c, constraints):
    """
    Resuelve problemas con restricciones <=, >= y = mediante el Método de las Dos Fases.
    """
    num_vars = len(c)
    st.markdown('<div class="step-header">Paso 0: Planteamiento del Problema</div>', unsafe_allow_html=True)
    var_names = [f"x_{i+1}" for i in range(num_vars)]
    st.latex(f"\\text{{{obj_type} }} Z = {build_equation_latex(c, var_names)}")
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        st.latex(f"\\text{{R{idx}: }} {build_equation_latex(coeffs, var_names, sense, rhs)}")

    # Asegurar que todos los RHS sean >= 0 (si alguno es negativo, multiplicar fila por -1)
    norm_constraints = []
    flipped_any = False
    for idx, (coeffs, sense, rhs) in enumerate(constraints, 1):
        if rhs < 0:
            flipped_any = True
            new_c = [-x for x in coeffs]
            new_s = {"<=": ">=", ">=": "<=", "=": "="}[sense]
            new_rhs = -rhs
            norm_constraints.append((new_c, new_s, new_rhs))
        else:
            norm_constraints.append((coeffs[:], sense, rhs))

    if flipped_any:
        st.info("🔄 **Ajuste de signos:** Como había un número negativo del lado derecho, multiplicamos esa restricción por `-1` (y volteamos el signo `≤` por `≥` o viceversa).")

    # PASO 1: CONSTRUIR VARIABLES DE HOLGURA, EXCESO Y ARTIFICIALES
    st.markdown('<div class="step-header">Paso 1: Preparar el equipo (Holgura, Exceso y Variables Artificiales)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kid-box">
    <b>🤖 ¿Por qué necesitamos "Variables Artificiales" (a₁, a₂...)?</b><br>
    - Cuando una regla es <b>≤</b>, agregamos una <b>variable de holgura (+s)</b> y ya tenemos nuestro punto de inicio fácil.<br>
    - Cuando una regla es <b>≥</b>, nos sobra cantidad, así que restamos una <b>variable de exceso (-e)</b>. Pero como tiene signo menos, ¡no nos sirve para arrancar!<br>
    - Cuando una regla es <b>=</b> o <b>≥</b>, inventamos una <b>Variable Artificial (+a)</b>. Piensa en ella como <b>rueditas de entrenamiento en una bicicleta</b>: nos ayudan a arrancar, pero en la <b>Fase 1</b> nuestra única misión es <b>deshacernos de todas las rueditas artificiales (hacer que valgan 0)</b> antes de resolver el problema real en la <b>Fase 2</b>.
    </div>
    """, unsafe_allow_html=True)

    slack_excess_names = []
    artificial_names = []
    
    # Determinar columnas extra por cada restricción
    row_structures = [] # lista de dicts con info de cada fila
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

    x_names = [f"x{i+1}" for i in range(num_vars)]
    col_names_p1 = x_names + slack_excess_names + artificial_names + ["RHS"]

    # Si no hay variables artificiales, redirigir explicación a Símplex directo
    if not artificial_names:
        st.success("✨ ¡Buenas noticias! Todas las restricciones son `≤`, así que **no necesitamos variables artificiales**. Pasamos directo a resolver:")
        solve_simplex_standard(obj_type, c, norm_constraints)
        return

    # Mostrar ecuaciones extendidas
    st.write("**Ecuaciones con todas las variables agregadas:**")
    for idx, info in enumerate(row_structures, 1):
        vec = [Fraction(0)] * (len(col_names_p1) - 1)
        for i in range(num_vars):
            vec[i] = info["coeffs"][i]
        if info["s_name"]:
            vec[col_names_p1.index(info["s_name"])] = info["s_sign"]
        if info["a_name"]:
            vec[col_names_p1.index(info["a_name"])] = Fraction(1)
        st.latex(build_equation_latex(vec, col_names_p1[:-1], "=", info["rhs"]))

    # ==========================================================================
    # FASE 1: MINIMIZAR W = SUMA DE VARIABLES ARTIFICIALES
    # ==========================================================================
    st.markdown('<div class="step-header">🚀 FASE 1: Quitar las rueditas de entrenamiento (Minimizar W = suma de artificiales)</div>', unsafe_allow_html=True)
    st.markdown(f"""
    En la **Fase 1**, ignoramos temporalmente la función objetivo original $Z$. Nuestro único objetivo es minimizar la suma de las variables artificiales:
    """)
    st.latex(f"\\text{{Minimizar }} W = {' + '.join(artificial_names)} \\iff \\text{{Maximizar }} (-W) = {' - '.join(artificial_names)}")

    # Construir filas de restricciones
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

    # Fila objetivo inicial de Fase 1: (-W) + a1 + a2 ... = 0
    w_row = [Fraction(0)] * len(col_names_p1)
    for a_n in artificial_names:
        w_row[col_names_p1.index(a_n)] = Fraction(1)

    st.write("**Preparación de la Fila W (hacer 0 las columnas de variables artificiales básicas):**")
    st.write("Como las variables artificiales empiezan dentro de la base, debemos restar sus filas de la fila `W` para que su columna tenga un `0` arriba:")
    
    for r_idx, b_var in enumerate(basic_vars):
        if b_var in artificial_names:
            st.latex(f"\\text{{Fila }} W \\leftarrow \\text{{Fila }} W - \\text{{Fila }}_{{{b_var}}}")
            w_row = [w_row[j] - tableau_p1[r_idx][j] for j in range(len(col_names_p1))]

    full_tableau_p1 = [w_row] + tableau_p1
    row_names_p1 = ["W"] + basic_vars[:]

    status_p1, end_tab_p1, end_basics_p1, _ = run_simplex_iterations(
        full_tableau_p1, col_names_p1, row_names_p1, basic_vars, phase_label="Fase 1 - "
    )

    if status_p1 != "optimal":
        st.error("La Fase 1 no pudo alcanzar un óptimo acotado.")
        return

    w_final = end_tab_p1[0][-1]
    if w_final != 0:
        st.markdown(f"""
        <div class="warn-box">
        <b>🚫 ¡Problema Infactible detectado al terminar la Fase 1!</b><br>
        El valor final de <b>W</b> fue <b>{fmt_f(abs(w_final))}</b> (distinto de cero). Esto significa que <b>no pudimos quitar todas las rueditas artificiales</b>.<br>
        En palabras sencillas: <b>las restricciones se contradicen</b> y no existe ninguna solución que cumpla todas las reglas al mismo tiempo. ¡Aquí nos detenemos!
        </div>
        """, unsafe_allow_html=True)
        return

    st.success("✅ **¡Fase 1 completada con éxito!** Todas las variables artificiales valen **0** (`W = 0`). Ya tenemos un punto de partida 100% válido dentro de la zona permitida.")

    # ==========================================================================
    # FASE 2: RESOLVER EL PROBLEMA ORIGINAL SIN VARIABLES ARTIFICIALES
    # ==========================================================================
    st.markdown('<div class="step-header">🏁 FASE 2: Resolver el problema real (Maximizar/Minimizar Z)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kid-box">
    <b>🧹 Limpiando la mesa para la Fase 2:</b><br>
    1. Borramos las columnas de las variables artificiales (<i>a₁, a₂...</i>) porque ya cumplieron su misión.<br>
    2. Ponemos nuestra verdadera función objetivo <b>Z</b> en la fila de arriba.<br>
    3. Si alguna variable que ya está en nuestro equipo (básica) tiene un número distinto de cero en la fila <b>Z</b>, restamos su fila para dejarla en <b>0</b> y arrancamos el Símplex normal.
    </div>
    """, unsafe_allow_html=True)

    # Eliminar columnas artificiales
    keep_indices = [i for i, name in enumerate(col_names_p1) if name not in artificial_names]
    col_names_p2 = [col_names_p1[i] for i in keep_indices]

    # Extraer filas de restricciones limpias
    clean_rows = []
    for r_idx in range(1, len(end_tab_p1)):
        clean_rows.append([end_tab_p1[r_idx][i] for i in keep_indices])

    # Construir fila Z original
    mult_z = Fraction(1) if obj_type == "Maximizar" else Fraction(-1)
    z_row_p2 = [Fraction(0)] * len(col_names_p2)
    for i in range(num_vars):
        z_row_p2[i] = -mult_z * c[i]

    # Hacer cero los coeficientes en fila Z de las variables que son básicas
    for r_idx, b_var in enumerate(end_basics_p1):
        if b_var in col_names_p2:
            c_idx = col_names_p2.index(b_var)
            factor = z_row_p2[c_idx]
            if factor != 0:
                st.write(f"Ajustando fila **Z** para que la variable básica `{b_var}` tenga `0` en la fila objetivo:")
                st.latex(f"\\text{{Fila }} Z \\leftarrow \\text{{Fila }} Z - ({fmt_latex_f(factor)}) \\times \\text{{Fila }}_{{{b_var}}}")
                z_row_p2 = [z_row_p2[j] - factor * clean_rows[r_idx][j] for j in range(len(col_names_p2))]

    full_tableau_p2 = [z_row_p2] + clean_rows
    row_names_p2 = ["Z"] + end_basics_p1[:]

    status_p2, end_tab_p2, end_basics_p2, _ = run_simplex_iterations(
        full_tableau_p2, col_names_p2, row_names_p2, end_basics_p1, phase_label="Fase 2 - "
    )

    if status_p2 == "optimal":
        st.markdown('<div class="step-header">Paso Final: ¡Resultado Óptimo Encontrado!</div>', unsafe_allow_html=True)
        sol_dict = {f"x{i+1}": Fraction(0) for i in range(num_vars)}
        for r_idx, b_var in enumerate(end_basics_p2, 1):
            if b_var in sol_dict:
                sol_dict[b_var] = end_tab_p2[r_idx][-1]

        raw_z = end_tab_p2[0][-1]
        final_z = raw_z * mult_z

        cols = st.columns(num_vars + 1)
        for i in range(num_vars):
            v_key = f"x{i+1}"
            cols[i].metric(label=f"Variable {v_key}", value=fmt_f(sol_dict[v_key]))
        cols[-1].metric(label=f"Valor Óptimo Z ({obj_type})", value=fmt_f(final_z))

        st.success(f"🏆 **¡Misión cumplida!** Solución óptima: " + ", ".join([f"**{k} = {fmt_f(v)}**" for k, v in sol_dict.items()]) + f" con **Z = {fmt_f(final_z)}**.")

# ==============================================================================
# INTERFAZ DE USUARIO (SIDEBAR + PESTAÑAS)
# ==============================================================================
st.title("🧭 Aventura Lineal: Programación Lineal Paso a Paso")
st.write("Aprende y resuelve problemas de optimización con explicaciones súper claras, tablas completas y cero pasos saltados.")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración del Problema")
metodo = st.sidebar.selectbox(
    "1. Elige el Método:",
    ["Método Gráfico", "Método Símplex", "Método de las Dos Fases"]
)

# Ejemplos prearmados en Session State
if "preset_loaded" not in st.session_state:
    st.session_state.preset_loaded = None

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Cargar Ejemplo Rápido")
if st.sidebar.button("🧸 Ejemplo 1: Fábrica de Juguetes (Gráfico / Símplex)"):
    st.session_state.preset_loaded = "juguetes"
if st.sidebar.button("🥗 Ejemplo 2: Dieta Saludable (Dos Fases - Minimizar)"):
    st.session_state.preset_loaded = "dieta"
if st.sidebar.button("🚀 Ejemplo 3: Misión Espacial (Dos Fases Mixto)"):
    st.session_state.preset_loaded = "espacial"

# Configuración según preset o manual
if st.session_state.preset_loaded == "juguetes":
    default_obj = "Maximizar"
    default_n_vars = 2
    default_n_cons = 2
    default_c = [3.0, 5.0]
    default_cons = [
        ([1.0, 0.0], "<=", 4.0),
        ([2.0, 3.0], "<=", 18.0)
    ]
elif st.session_state.preset_loaded == "dieta":
    default_obj = "Minimizar"
    default_n_vars = 2
    default_n_cons = 2
    default_c = [4.0, 6.0]
    default_cons = [
        ([2.0, 1.0], ">=", 8.0),
        ([1.0, 3.0], ">=", 9.0)
    ]
elif st.session_state.preset_loaded == "espacial":
    default_obj = "Maximizar"
    default_n_vars = 2
    default_n_cons = 3
    default_c = [5.0, 4.0]
    default_cons = [
        ([1.0, 1.0], "<=", 10.0),
        ([2.0, 1.0], ">=", 6.0),
        ([1.0, 2.0], "=", 12.0)
    ]
else:
    default_obj = "Maximizar"
    default_n_vars = 2
    default_n_cons = 2
    default_c = [3.0, 2.0]
    default_cons = [
        ([2.0, 1.0], "<=", 10.0),
        ([1.0, 2.0], "<=", 8.0)
    ]

# PESTAÑAS PRINCIPALES
tab_resolver, tab_aprender = st.tabs(["🧮 Resolver Paso a Paso", "📚 ¿Cómo funciona este método? (Explicación fácil)"])

with tab_aprender:
    st.header("🎓 Guía Súper Fácil de Programación Lineal")
    
    st.markdown("""
    ### 🌟 ¿Qué es la Programación Lineal?
    Imagina que tienes una tienda de limonadas y galletas. Quieres **ganar la mayor cantidad de monedas posible**, pero tienes reglas:
    - Solo tienes **10 limones**.
    - Solo tienes **2 horas** para hornear.
    - No puedes hacer cantidades negativas de galletas.
    
    La **Programación Lineal** es como un mapa del tesoro que nos dice exactamente **cuántas limonadas y cuántas galletas hacer** para ganar el premio máximo sin romper ninguna regla.
    """)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("""
        **1. Método Gráfico 🗺️**
        - **¿Cuándo se usa?** Cuando solo tenemos **2 decisiones** ($x_1$ y $x_2$).
        - **¿Cómo funciona?** Dibujamos cada regla como una línea en un cuaderno cuadriculado. Donde se juntan todos los colores se forma un polígono llamado **Región Factible**. ¡El tesoro siempre está en una de sus esquinas!
        """)
    with c2:
        st.success("""
        **2. Método Símplex 🪜**
        - **¿Cuándo se usa?** Cuando tenemos 2, 3, 10 o 100 variables y todas las reglas son límites máximos ($\le$).
        - **¿Cómo funciona?** En vez de dibujar, usamos una **tabla mágica**. Empezamos en la esquina $(0,0)$ y vamos saltando de esquina en esquina, siempre subiendo hacia donde hay más puntos, hasta que ya no se puede subir más.
        """)
    with c3:
        st.warning("""
        **3. Método de las Dos Fases 🚲**
        - **¿Cuándo se usa?** Cuando hay reglas difíciles con signos $\ge$ (mínimos) o $=$ (exactos).
        - **¿Cómo funciona?** 
          - **Fase 1:** Ponemos *rueditas de entrenamiento* (variables artificiales) para poder arrancar y las vamos quitando hasta llegar a una esquina válida.
          - **Fase 2:** Quitamos las rueditas y resolvemos con el Símplex normal.
        """)

with tab_resolver:
    st.subheader(f"🛠️ Configura tu problema para: {metodo}")

    col_top1, col_top2, col_top3 = st.columns(3)
    with col_top1:
        obj_type = st.selectbox("¿Qué queremos hacer?", ["Maximizar", "Minimizar"], index=0 if default_obj == "Maximizar" else 1)
    with col_top2:
        if metodo == "Método Gráfico":
            n_vars = 2
            st.number_input("Número de variables:", value=2, disabled=True, help="El método gráfico solo se puede dibujar en 2D (2 variables).")
        else:
            n_vars = st.number_input("Número de variables (x₁, x₂...):", min_value=2, max_value=6, value=default_n_vars, step=1)
    with col_top3:
        n_cons = st.number_input("Número de restricciones (reglas):", min_value=1, max_value=6, value=default_n_cons, step=1)

    st.markdown("### 1️⃣ Función Objetivo (¿Cuánto vale cada variable?)")
    obj_cols = st.columns(n_vars)
    c_inputs = []
    for i in range(n_vars):
        val_def = default_c[i] if i < len(default_c) else 1.0
        with obj_cols[i]:
            val = st.number_input(f"Valor de x{i+1} en Z:", value=float(val_def), step=1.0, key=f"c_{i}")
            c_inputs.append(to_frac(val))

    st.markdown("### 2️⃣ Restricciones (Las reglas del juego)")
    constraints_inputs = []
    for r in range(n_cons):
        st.markdown(f"**Regla #{r+1}:**")
        r_cols = st.columns(n_vars + 2)
        row_coeffs = []
        
        def_row = default_cons[r] if r < len(default_cons) else ([1.0]*n_vars, "<=", 10.0)
        for i in range(n_vars):
            c_def = def_row[0][i] if i < len(def_row[0]) else 1.0
            with r_cols[i]:
                v = st.number_input(f"x{i+1}", value=float(c_def), step=1.0, key=f"r_{r}_x_{i}")
                row_coeffs.append(to_frac(v))
        
        with r_cols[n_vars]:
            s_options = ["<="] if metodo == "Método Símplex" else ["<=", ">=", "="]
            s_def_idx = s_options.index(def_row[1]) if def_row[1] in s_options else 0
            sense = st.selectbox("Signo", s_options, index=s_def_idx, key=f"r_{r}_sense")
        
        with r_cols[n_vars + 1]:
            rhs_val = st.number_input("Límite (RHS)", value=float(def_row[2]), step=1.0, key=f"r_{r}_rhs")
        
        if metodo == "Método Gráfico":
            constraints_inputs.append((row_coeffs[0], row_coeffs[1], sense, to_frac(rhs_val)))
        else:
            constraints_inputs.append((row_coeffs, sense, to_frac(rhs_val)))

    st.markdown("---")
    if st.button("🚀 ¡Resolver Paso a Paso sin saltarse nada!", type="primary", use_container_width=True):
        if metodo == "Método Gráfico":
            solve_graphical(obj_type, c_inputs, constraints_inputs)
        elif metodo == "Método Símplex":
            solve_simplex_standard(obj_type, c_inputs, constraints_inputs)
        elif metodo == "Método de las Dos Fases":
            solve_two_phase(obj_type, c_inputs, constraints_inputs)