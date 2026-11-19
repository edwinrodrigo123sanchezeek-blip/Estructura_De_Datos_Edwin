# app.py — PL Solver Definitivo (Formato Cuaderno, Gráfico Explicado, Foto IA)
import streamlit as st
import pandas as pd
import math
from fractions import Fraction
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json
from PIL import Image

# Intentar importar la IA (si el usuario pone su API Key)
try:
    import google.generativeai as genai
    HAS_IA = True
except ImportError:
    HAS_IA = False

st.set_page_config(page_title="PL Solver Cuaderno", page_icon="📝", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# 1. MATEMÁTICAS Y FRACCIONES
# ═══════════════════════════════════════════════════════════════════
def fstr(f):
    if isinstance(f, Fraction):
        return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"
    return str(f)

def parse_frac(s):
    s = str(s).strip().replace(",", ".")
    if s in ("", "+", "-"): return Fraction(0)
    if "/" in s:
        a, b = s.split("/")
        return Fraction(a) / Fraction(b)
    return Fraction(s)

def f2float(s):
    if isinstance(s, Fraction): return float(s)
    if isinstance(s, (int, float)): return float(s)
    a, _, b = str(s).partition('/')
    return float(a)/float(b) if b else float(a)

# ═══════════════════════════════════════════════════════════════════
# 2. MOTOR SIMPLEX FORMATO CUADERNO
# ═══════════════════════════════════════════════════════════════════
def solve_simplex(c_in, A, senses, b_in, is_max):
    n, m = len(c_in), len(A)
    res = {"n": n, "m": m, "isMax": is_max, "status": None, "steps": [], "varNames": []}
    
    c_obj = list(c_in) if is_max else [-x for x in c_in]
    A2 = [row[:] for row in A]; b2 = list(b_in); s2 = list(senses)

    # Estandarización (voltear signos si RHS es negativo)
    for i in range(m):
        if b2[i] < 0:
            A2[i] = [-x for x in A2[i]]; b2[i] = -b2[i]
            s2[i] = ">=" if s2[i] == "<=" else ("<=" if s2[i] == ">=" else "=")

    # Variables extra (Holguras = x3, x4, x5...; Excesos = e; Artificiales = R)
    extras = []
    slack_count = 0
    for i in range(m):
        if s2[i] == "<=":
            slack_count += 1
            extras.append({"type": "slack", "row": i, "name": f"x{n+slack_count}"})
        elif s2[i] == ">=":
            extras.append({"type": "surplus", "row": i, "name": f"e{i+1}"})
            extras.append({"type": "artificial", "row": i, "name": f"R{i+1}"})
        else:
            extras.append({"type": "artificial", "row": i, "name": f"R{i+1}"})

    total_vars = n + len(extras)
    var_names = ["Z"] + [f"x{j+1}" for j in range(n)] + [e["name"] for e in extras] + ["L.D"]
    
    # Matriz: Fila 0 = Z, Filas 1..m = restricciones
    M = [[Fraction(0)] * (total_vars + 2) for _ in range(m + 1)]
    basis = ["Z"] + ["-"] * m

    # Fila Z (1, -c1, -c2, 0, 0...)
    M[0][0] = Fraction(1)
    for j in range(n): M[0][j+1] = -c_obj[j]

    # Restricciones
    for i in range(m):
        for j in range(n): M[i+1][j+1] = A2[i][j]
        M[i+1][total_vars+1] = b2[i]

    # Llenar variables extra
    col_idx = n + 1
    for e in extras:
        if e["type"] == "slack":
            M[e["row"]+1][col_idx] = Fraction(1)
            basis[e["row"]+1] = e["name"]
        elif e["type"] == "surplus":
            M[e["row"]+1][col_idx] = Fraction(-1)
        else:
            M[e["row"]+1][col_idx] = Fraction(1)
            basis[e["row"]+1] = e["name"]
        col_idx += 1

    res["varNames"] = var_names

    # --- ITERACIONES ---
    for it in range(100):
        snap = {"M": [row[:] for row in M], "basis": basis[:], "enter": -1, "leave": -1, "pivot": None, "ops": [], "note": None}
        
        # 1. Variable que entra (el más negativo en Fila Z)
        enter = -1
        for j in range(1, total_vars + 1):
            if M[0][j] < 0 and (enter < 0 or M[0][j] < M[0][enter]):
                enter = j
                
        if enter < 0:
            snap["note"] = "Todos los valores en Z son ≥ 0. ¡Solución Óptima Alcanzada!"
            res["steps"].append(snap)
            res["status"] = "optimal"
            break
            
        # 2. Variable que sale (menor razón RHS / columna)
        leave = -1; best = None
        for i in range(1, m+1):
            if M[i][enter] > 0:
                q = M[i][total_vars+1] / M[i][enter]
                if best is None or q < best:
                    best, leave = q, i
                    
        if leave < 0:
            snap["note"] = "No hay límite para la variable entrante. Problema NO ACOTADO."
            res["steps"].append(snap)
            res["status"] = "unbounded"
            break
            
        snap["enter"] = enter; snap["leave"] = leave; snap["pivot"] = M[leave][enter]
        
        # 3. Hacer Pivote
        p = M[leave][enter]
        for j in range(total_vars + 2): M[leave][j] /= p
        snap["ops"].append(f"F{leave} / {fstr(p)}")
        
        for i in range(m+1):
            if i == leave: continue
            factor = M[i][enter]
            if factor == 0: continue
            for j in range(total_vars + 2): M[i][j] -= factor * M[leave][j]
            snap["ops"].append(f"F{i} - F{leave} * ({fstr(factor)})")
            
        basis[leave] = var_names[enter]
        res["steps"].append(snap)

    # Extraer resultados
    if res["status"] == "optimal":
        x = [Fraction(0)] * n
        for i in range(1, m+1):
            if basis[i] in var_names[1:n+1]:
                idx = var_names.index(basis[i]) - 1
                x[idx] = M[i][total_vars+1]
        res["x"] = x
        res["Z"] = M[0][total_vars+1] if is_max else -M[0][total_vars+1]

    return res

# ═══════════════════════════════════════════════════════════════════
# 3. MÉTODO GRÁFICO Y EXPLICACIÓN DE PUNTOS
# ═══════════════════════════════════════════════════════════════════
def solve_graphical(c, A, senses, b, is_max, opt_x):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.grid(True, linestyle="--", alpha=0.6)
    colors = ['#e11d48', '#0891b2', '#7c3aed', '#ea580c', '#059669']
    maxx, maxy = 10, 10

    for i, (row, sense, rhs) in enumerate(zip(A, senses, b)):
        a1, a2, c1 = f2float(row[0]), f2float(row[1]), f2float(rhs)
        if a1 > 0: maxx = max(maxx, c1/a1 * 1.2)
        if a2 > 0: maxy = max(maxy, c1/a2 * 1.2)
        
        # Dibujar recta
        if a1 != 0:
            ax.plot([0, c1/a1], [c1/a2 if a2!=0 else 0, 0], color=colors[i%len(colors)], label=f"R{i+1}: {fstr(row[0])}x1 + {fstr(row[1])}x2 {sense} {fstr(rhs)}")
        elif a2 != 0:
            ax.axhline(y=c1/a2, color=colors[i%len(colors)], label=f"R{i+1}: {fstr(row[1])}x2 {sense} {fstr(rhs)}")

    if opt_x:
        ax.plot(f2float(opt_x[0]), f2float(opt_x[1]), 'o', markersize=12, color='#f59e0b', markeredgecolor='#b45309', markeredgewidth=2)
        ax.annotate(f"Óptimo ({fstr(opt_x[0])}, {fstr(opt_x[1])})", (f2float(opt_x[0]), f2float(opt_x[1])), 
                    xytext=(10, 10), textcoords='offset points', fontweight='bold', color='#b45309')

    ax.set_xlim(0, maxx); ax.set_ylim(0, maxy)
    ax.set_xlabel("x1"); ax.set_ylabel("x2"); ax.legend()
    
    buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); plt.close(fig); buf.seek(0)
    return buf.read()

def get_intersections(A, b):
    pts = []
    for i in range(len(A)):
        for j in range(i+1, len(A)):
            a1, b1, c1 = f2float(A[i][0]), f2float(A[i][1]), f2float(b[i])
            a2, b2, c2 = f2float(A[j][0]), f2float(A[j][1]), f2float(b[j])
            det = a1*b2 - a2*b1
            if abs(det) > 1e-9:
                x = (c1*b2 - c2*b1) / det
                y = (a1*c2 - a2*c1) / det
                if x >= -1e-5 and y >= -1e-5: # Solo positivos
                    pts.append(f"Intersección R{i+1} y R{j+1}: ({x:.2f}, {y:.2f})")
    return pts

# ═══════════════════════════════════════════════════════════════════
# 4. RENDERIZADO DE TABLA (Exacto al cuaderno)
# ═══════════════════════════════════════════════════════════════════
def render_table(stp, var_names, total_vars):
    h = '<table style="border-collapse:collapse; width:100%; text-align:center; font-size:14px; border:2px solid #000;">'
    
    # Header
    h += '<tr style="background:#e5e7eb;">'
    for name in var_names:
        h += f'<th style="border:1px solid #000; padding:6px;">{name}</th>'
    h += '</tr>'
    
    # Filas
    for i, row in enumerate(stp["M"]):
        h += '<tr>'
        for j, val in enumerate(row):
            bg = "#fff"
            if i == 0: bg = "#fef08a" # Fila Z
            if j == total_vars + 1: bg = "#dcfce7" # Columna L.D
            
            border = "1px solid #000"
            color = "black"
            if i == stp["leave"] and j == stp["enter"]:
                bg = "#4f46e5"; color = "white"; border = "3px solid #312e81"
            elif j == stp["enter"] and stp["enter"] != -1:
                bg = "#e0e7ff"
                
            # Reemplazar la primera columna (Z, x3, x4...) con el nombre de la base
            if j == 0:
                val_str = stp["basis"][i]
            else:
                val_str = fstr(val)
                
            h += f'<td style="border:{border}; padding:6px; background:{bg}; color:{color}; font-weight:bold;">{val_str}</td>'
        h += '</tr>'
    h += '</table>'
    return h

# ═══════════════════════════════════════════════════════════════════
# 5. INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
st.title("📝 Solucionador de Programación Lineal")

with st.sidebar:
    st.header("⚙️ Opciones")
    metodo = st.selectbox("Método a usar", ["Simplex / Doble Fase", "Método Gráfico"])
    
    is_max = st.radio("Objetivo", ["Maximizar", "Minimizar"], horizontal=True) == "Maximizar"
    n = st.selectbox("Número de variables", [2, 3, 4])
    n_cons = st.number_input("Número de restricciones", min_value=1, max_value=6, value=3)
    
    st.markdown("### Función Z")
    obj_cols = st.columns(n); obj_vals = []
    for j in range(n):
        with obj_cols[j]:
            obj_vals.append(st.text_input(f"x{j+1}", value="0", key=f"obj_{j}", label_visibility="collapsed"))
            
    st.markdown("### Restricciones")
    constraints = []
    for i in range(n_cons):
        st.markdown(f"**R{i+1}**")
        r_cols = st.columns(n + 2)
        coefs = []
        for j in range(n):
            with r_cols[j]:
                coefs.append(st.text_input(f"c{i}{j}", value="0", key=f"a_{i}_{j}", label_visibility="collapsed"))
        with r_cols[n]:
            sense = st.selectbox(f"s{i}", ["<=", ">=", "="], key=f"s_{i}", label_visibility="collapsed")
        with r_cols[n+1]:
            rhs = st.text_input(f"r{i}", value="0", key=f"r_{i}", label_visibility="collapsed")
        constraints.append({"coefs": coefs, "sense": sense, "rhs": rhs})
        
    st.divider()
    solve_btn = st.button("▶ RESOLVER", type="primary", use_container_width=True)

    if st.button("🔄 Cargar Ejemplo del Cuaderno", use_container_width=True):
        st.session_state.obj_0, st.session_state.obj_1 = "8", "10"
        st.session_state.a_0_0, st.session_state.a_0_1, st.session_state.s_0, st.session_state.r_0 = "20", "30", "<=", "120"
        st.session_state.a_1_0, st.session_state.a_1_1, st.session_state.s_1, st.session_state.r_1 = "2", "2", "<=", "9"
        st.session_state.a_2_0, st.session_state.a_2_1, st.session_state.s_2, st.session_state.r_2 = "6", "4", "<=", "24"
        st.rerun()

# --- IA EN LA BARRA PRINCIPAL ---
st.markdown("### 📷 Escanear Ejercicio con Foto (BETA)")
with st.expander("Haz clic aquí para subir una foto y usar IA"):
    st.write("Esta función usa Google Gemini para leer tu cuaderno. Necesitas una API Key gratuita.")
    api_key = st.text_input("Pega tu API Key de Google Gemini aquí:", type="password")
    foto = st.file_uploader("Sube foto del ejercicio", type=["jpg", "png", "jpeg"])
    
    if st.button("✨ Escanear y Resolver"):
        if not HAS_IA:
            st.error("Falta instalar la librería. Ejecuta: `pip install google-generativeai`")
        elif not api_key:
            st.warning("Por favor, ingresa tu API Key de Gemini.")
        elif not foto:
            st.warning("Por favor, sube una imagen.")
        else:
            with st.spinner("La IA está leyendo tu cuaderno..."):
                genai.configure(api_key=api_key)
                img = Image.open(foto)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = """Lee esta imagen. Extrae el problema de programación lineal.
                Devuelve SOLO un JSON con esta estructura exacta:
                {"is_max": true, "obj": [8, 10], "constraints": [{"coefs": [20, 30], "sense": "<=", "rhs": 120}]}
                No agregues texto extra, solo el JSON."""
                try:
                    response = model.generate_content([prompt, img])
                    text = response.text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(text)
                    
                    # Cargar a session_state
                    st.session_state.is_max_ia = data["is_max"]
                    for j, v in enumerate(data["obj"]):
                        st.session_state[f"obj_{j}"] = str(v)
                    for i, c in enumerate(data["constraints"]):
                        for j, v in enumerate(c["coefs"]):
                            st.session_state[f"a_{i}_{j}"] = str(v)
                        st.session_state[f"s_{i}"] = c["sense"]
                        st.session_state[f"r_{i}"] = str(c["rhs"])
                    st.success("¡Leído con éxito! Revisa los datos en la barra lateral y presiona RESOLVER.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al leer la imagen: {e}")

st.divider()

# --- LÓGICA DE RESOLUCIÓN ---
if solve_btn:
    try:
        c = [parse_frac(v) for v in obj_vals]
        A = [[parse_frac(v) for v in r["coefs"]] for r in constraints]
        senses = [r["sense"] for r in constraints]
        b = [parse_frac(r["rhs"]) for r in constraints]
        
        res = solve_simplex(c, A, senses, b, is_max)
        
        if res["status"] == "optimal":
            st.success(f"**¡Solución Óptima!** Z = {fstr(res['Z'])}")
            x_cols = st.columns(len(res["x"]))
            for i, v in enumerate(res["x"]):
                x_cols[i].metric(f"x{i+1}", fstr(v))
        else:
            st.error("El problema no tiene solución óptima (Infactible o No Acotado).")
            
        st.divider()
        
        if metodo == "Método Gráfico":
            if n != 2:
                st.warning("El método gráfico solo funciona para 2 variables.")
            else:
                st.header("📊 Gráfica y Explicación")
                col1, col2 = st.columns([1.5, 1])
                with col1:
                    img = solve_graphical(c, A, senses, b, is_max, res.get("x"))
                    st.image(img, use_column_width=True)
                with col2:
                    st.markdown("### ¿De dónde salieron los puntos?")
                    st.write("Los puntos de la gráfica son las **intersecciones** de tus restricciones. Aquí están los cálculos:")
                    for pt in get_intersections(A, b):
                        st.info(pt)
                                    
        elif metodo == "Simplex / Doble Fase":
            st.header("🔢 Tablas Paso a Paso (Formato Cuaderno)")
            for k, stp in enumerate(res["steps"]):
                if stp["note"]:
                    st.success(f"**Fin:** {stp['note']}")
                    continue
                    
                st.markdown(f"### Iteración {k+1}")
                
                # Explicación textual
                enter_name = res["varNames"][stp["enter"]]
                leave_name = stp["basis"][stp["leave"]]
                st.info(f"**Entra:** `{enter_name}` (es el más negativo en Z). | **Sale:** `{leave_name}` (menor razón RHS). | **Pivote:** `{fstr(stp['pivot'])}`.")
                st.markdown(f"**Operaciones:** {', '.join(stp['ops'])}")
                
                # Tabla HTML exacta
                total_vars = len(res["varNames"]) - 2 # Restar Z y L.D
                html = render_table(stp, res["varNames"], total_vars)
                st.markdown(html, unsafe_allow_html=True)
                
            # Comprobación
            if res["status"] == "optimal":
                st.divider()
                st.header("✅ Comprobación")
                checks = []
                for i in range(len(A)):
                    lhs = sum(res["x"][j] * A[i][j] for j in range(len(res["x"])))
                    ok = lhs <= b[i] if senses[i] == "<=" else lhs >= b[i] if senses[i] == ">=" else lhs == b[i]
                    checks.append({
                        "Restricción": f"R{i+1}",
                        "Sustituyendo": f"{fstr(lhs)} {senses[i]} {fstr(b[i])}",
                        "Estado": "✅ Se cumple" if ok else "❌ Falla"
                    })
                st.table(pd.DataFrame(checks))
                
    except Exception as e:
        st.error(f"Error al procesar los datos. Asegúrate de escribir números válidos. Detalle: {e}")