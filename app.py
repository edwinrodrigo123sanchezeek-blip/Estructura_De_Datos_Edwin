# app.py — PL Solver Completo y Didáctico
import streamlit as st
import pandas as pd
import math
from fractions import Fraction
from io import BytesIO

st.set_page_config(page_title="PL Solver Fácil", page_icon="🧩", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# 1. MATEMÁTICAS Y FRACCIONES
# ═══════════════════════════════════════════════════════════════════
def fstr(f):
    """Convierte una fracción a string legible"""
    if isinstance(f, Fraction):
        return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"
    return str(f)

def f2float(s):
    """Convierte una fracción a número decimal"""
    if isinstance(s, Fraction): return float(s)
    if isinstance(s, (int, float)): return float(s)
    a, _, b = str(s).partition('/')
    return float(a)/float(b) if b else float(a)

def parse_frac(s):
    """Lee lo que escribe el usuario y lo convierte a Fracción exacta"""
    s = str(s).strip().replace(",", ".").replace(" ", "")
    if s in ("", "+", "-"): return Fraction(0)
    if "/" in s:
        a, b = s.split("/")
        return Fraction(a) / Fraction(b)
    return Fraction(s)

# ═══════════════════════════════════════════════════════════════════
# 2. MOTOR SIMPLEX / DOBLE FASE (s = holgura, e = exceso, R = artificial)
# ═══════════════════════════════════════════════════════════════════
def _build_row(M, basis, cvec, total):
    m = len(M); r = [Fraction(0)]*(total+1)
    for j in range(total): r[j] = cvec[j]
    z = Fraction(0)
    for i in range(m):
        cb = cvec[basis[i]]
        if cb == 0: continue
        for j in range(total): r[j] -= cb * M[i][j]
        z += cb * M[i][total]
    r[total] = -z
    return r

def _pivot(M, row, col, total):
    p = M[row][col]
    for j in range(total+1): M[row][j] /= p
    for i in range(len(M)):
        if i == row: continue
        f = M[i][col]
        if f == 0: continue
        for j in range(total+1): M[i][j] -= f * M[row][j]

def _simplex(M, basis, r, total, forbidden):
    steps = []
    for _ in range(400):
        enter = -1
        for j in range(total):
            if j in forbidden: continue
            if r[j] > 0 and (enter < 0 or r[j] > r[enter]): enter = j
        snap = {"M": [row[:] for row in M], "basis": basis[:], "r": r[:],
                "enter": enter, "leave": -1, "pivot": None, "ratio": None, "note": None}
        
        if enter < 0:
            snap["note"] = "¡Ya no hay números positivos en la fila de abajo! Hemos llegado a la mejor solución."
            steps.append(snap); return "optimal", steps
        
        leave, best = -1, None
        for i in range(len(M)):
            if M[i][enter] > 0:
                q = M[i][total] / M[i][enter]
                if best is None or q < best: best, leave = q, i
                
        if leave < 0:
            snap["note"] = "¡Cuidado! La variable que entra puede crecer infinitamente. El problema NO ESTÁ ACOTADO."
            steps.append(snap); return "unbounded", steps
            
        snap["leave"] = leave; snap["pivot"] = M[leave][enter]; snap["ratio"] = best
        steps.append(snap)
        
        _pivot(M, leave, enter, total); basis[leave] = enter
        re = r[enter]
        for j in range(total+1): r[j] -= re * M[leave][j]
    return "maxiter", steps

def solve_lp(c_in, A, senses, b_in, is_max):
    n, m = len(c_in), len(A)
    res = {"n": n, "m": m, "isMax": is_max, "status": None, "phases": [], "preNotes": []}
    c_obj = list(c_in) if is_max else [-x for x in c_in]
    A2 = [row[:] for row in A]; b2 = list(b_in); s2 = list(senses)

    # Arreglar lados derechos negativos
    for i in range(m):
        if b2[i] < 0:
            A2[i] = [-x for x in A2[i]]; b2[i] = -b2[i]
            s2[i] = ">=" if s2[i] == "<=" else ("<=" if s2[i] == ">=" else "=")
            res["preNotes"].append(f"R{i+1} se multiplicó por −1 para que el lado derecho sea positivo.")

    # Contar variables extra
    extras = []
    for i in range(m):
        if s2[i] == "<=": extras.append({"type": "slack", "row": i})
        elif s2[i] == ">=":
            extras.append({"type": "surplus", "row": i})
            extras.append({"type": "artificial", "row": i})
        else: extras.append({"type": "artificial", "row": i})

    total = n + len(extras)
    M = [[Fraction(0)]*(total+1) for _ in range(m)]
    for i in range(m):
        for j in range(n): M[i][j] = A2[i][j]
        M[i][total] = b2[i]

    names = [f"x{j+1}" for j in range(n)]
    basis = [-1]*m; artif = []
    
    # Asignar nombres s, e, R
    for e in extras:
        col = len(names)
        if e["type"] == "slack":
            names.append(f"s{e['row']+1}"); M[e["row"]][col] = Fraction(1); basis[e["row"]] = col
        elif e["type"] == "surplus":
            names.append(f"e{e['row']+1}"); M[e["row"]][col] = Fraction(-1)
        else:
            names.append(f"R{e['row']+1}"); M[e["row"]][col] = Fraction(1)
            basis[e["row"]] = col; artif.append(col)

    res.update({"varNames": names, "totalCols": total, "artifCols": artif})

    # --- FASE 1 (Solo si hay artificiales) ---
    if artif:
        c1 = [Fraction(0)]*total
        for j in artif: c1[j] = Fraction(-1)
        r1 = _build_row(M, basis, c1, total)
        st1, steps1 = _simplex(M, basis, r1, total, set())
        W = r1[total]
        res["phases"].append({"name": "Fase 1", "steps": steps1, "status": st1, "W": fstr(W)})
        
        if W != 0:
            res["status"] = "infeasible"; return res
            
        # Limpiar artificiales de la base si se quedaron ahí
        for i in range(m):
            if basis[i] in artif:
                found = next((j for j in range(total) if j not in artif and M[i][j] != 0), -1)
                if found >= 0: _pivot(M, i, found, total); basis[i] = found

    # --- FASE 2 ---
    c2 = [Fraction(0)]*total
    for j in range(n): c2[j] = c_obj[j]
    r2 = _build_row(M, basis, c2, total)
    st2, steps2 = _simplex(M, basis, r2, total, set(artif))
    res["phases"].append({"name": "Fase 2" if artif else "Simplex", "steps": steps2, "status": st2})

    if st2 == "unbounded": res["status"] = "unbounded"; return res
    if st2 != "optimal":   res["status"] = "error"; return res

    # Extraer resultados
    x = [Fraction(0)]*n
    for i in range(m):
        if basis[i] < n: x[basis[i]] = M[i][total]
    Zmax = -r2[total]
    res.update({"x": x, "Zmax": Zmax, "Z": Zmax if is_max else -Zmax, "status": "optimal"})
    return res

# ═══════════════════════════════════════════════════════════════════
# 3. COMPROBACIÓN DE LA SOLUCIÓN
# ═══════════════════════════════════════════════════════════════════
def generar_comprobacion(x, A, senses, b, c, is_max):
    checks = []
    for i in range(len(A)):
        lhs = sum(x[j] * A[i][j] for j in range(len(x)))
        rhs = b[i]
        sense = senses[i]
        
        # Evaluar si cumple
        if sense == "<=": ok = lhs <= rhs
        elif sense == ">=": ok = lhs >= rhs
        else: ok = lhs == rhs
        
        checks.append({
            "Restricción": f"R{i+1}",
            "Tus datos": f"{fstr(A[i][0])}x₁ + {fstr(A[i][1])}x₂ {sense} {fstr(rhs)}",
            "Reemplazando": f"{fstr(lhs)} {sense} {fstr(rhs)}",
            "¿Se cumple?": "✅ Sí" if ok else "❌ No"
        })
    
    Z_calc = sum(x[j] * c[j] for j in range(len(x)))
    return checks, Z_calc

# ═══════════════════════════════════════════════════════════════════
# 4. FUNCIONES DE INTERFAZ GRÁFICA
# ═══════════════════════════════════════════════════════════════════
def cargar_ejemplo(id_ejemplo):
    if id_ejemplo == 1:
        st.session_state.obj_0, st.session_state.obj_1 = "3", "5"
        st.session_state.a_0_0, st.session_state.a_0_1, st.session_state.s_0, st.session_state.r_0 = "1", "0", "<=", "4"
        st.session_state.a_1_0, st.session_state.a_1_1, st.session_state.s_1, st.session_state.r_1 = "0", "2", "<=", "12"
        st.session_state.a_2_0, st.session_state.a_2_1, st.session_state.s_2, st.session_state.r_2 = "3", "2", "<=", "18"
    elif id_ejemplo == 2:
        st.session_state.obj_0, st.session_state.obj_1 = "2", "3"
        st.session_state.a_0_0, st.session_state.a_0_1, st.session_state.s_0, st.session_state.r_0 = "1", "1", ">=", "4"
        st.session_state.a_1_0, st.session_state.a_1_1, st.session_state.s_1, st.session_state.r_1 = "1", "3", ">=", "6"
        st.session_state.a_2_0, st.session_state.a_2_1, st.session_state.s_2, st.session_state.r_2 = "2", "1", ">=", "5"

def build_dataframe(M, basis, r, names, total, enter=None, leave=None):
    """Construye la tabla visual con colores"""
    data = []
    for i, row in enumerate(M):
        data.append([names[basis[i]]] + [fstr(v) for v in row])
    data.append(["Cj−Zj"] + [fstr(v) for v in r])
    cols = ["Base"] + names + ["RHS"]
    df = pd.DataFrame(data, columns=cols)

    def style_cell(x):
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        # Columna RHS verde
        styles.iloc[:, -1] = 'background-color: #dcfce7; color: #166534; font-weight: bold;'
        # Fila Cj-Zj amarilla
        styles.iloc[-1, :] = 'background-color: #fef08a; color: #854d0e; font-weight: bold; border-top: 2px solid #eab308;'
        # Columna Base gris
        styles.iloc[:, 0] = 'background-color: #f1f5f9; color: #334155; font-weight: bold;'
        
        if enter is not None:
            # Columna entrante morada
            styles.iloc[:, enter + 1] = 'background-color: #f3e8ff;'
            # Pivote azul oscuro
            if leave is not None and leave < len(M):
                styles.iloc[leave, enter + 1] = 'background-color: #4f46e5; color: white; font-weight: bold;'
        return styles
    return df.style.apply(style_cell, axis=None)

def render_metodo(res, is_max, c, A, senses, b, names, total, mostrar_comprobacion=True):
    """Dibuja los pasos y tablas de un método en particular"""
    for ph in res["phases"]:
        st.markdown(f"### {ph['name']}")
        
        # Texto introductorio de Fase 1
        if "Fase 1" in ph["name"]:
            ok = ph["W"] == "0"
            st.warning("🤫 **Fase 1:** Usamos las variables artificiales **R** para poder empezar. Si logramos que su suma (W) sea 0, el truco funcionó y pasamos a la Fase 2." + (" ✅ ¡W es 0, funcionó!" if ok else " ❌ W no es 0. El problema es imposible."))
        
        # Iteraciones
        for k, stp in enumerate(ph["steps"]):
            # Si terminó
            if stp["note"]:
                st.success(f"🏁 **Fin:** {stp['note']}")
                continue
            
            # Explicación detallada
            txt = f"""
            **Iteración {k+1}:**
            * 👀 **Variable que entra:** `{names[stp['enter']]}`. ¿Por qué? Porque en la fila de abajo (Cj−Zj) es el número positivo más grande (tiene un **{fstr(stp['r'][stp['enter']])}**).
            * ➗ **Variable que sale:** `{names[stp['basis'][stp['leave']]]}`. ¿Por qué? Dividimos la columna RHS entre la columna de `{names[stp['enter']]}`. La razón más pequeña fue **{fstr(stp['ratio'])}**.
            * 🎯 **Pivote:** El número donde se cruzan es **{fstr(stp['pivot'])}**. 
            * ⚙️ **Operación:** Dividimos toda la fila del pivote entre `{fstr(stp['pivot'])}` para que se vuelva 1, y luego restamos esta fila a las demás para hacer 0 en la columna de `{names[stp['enter']]}`.
            """
            st.info(txt)
            
            # Tabla
            df = build_dataframe(stp["M"], stp["basis"], stp["r"], names, total, stp["enter"], stp["leave"])
            st.dataframe(df, use_container_width=True)
            
    # COMPROBACIÓN AL FINAL
    if mostrar_comprobacion and res["status"] == "optimal":
        st.divider()
        st.markdown("### ✅ Comprobación de la Solución")
        st.write("Aquí reemplazamos los valores de \(x₁, x₂...\) en tus restricciones originales para ver si todo cuadra.")
        
        checks, Z_calc = generar_comprobacion(res["x"], A, senses, b, c, is_max)
        df_check = pd.DataFrame(checks)
        st.dataframe(df_check, use_container_width=True, hide_index=True)
        
        st.success(f"Al reemplazar en Z, nos da exactamente: **Z = {fstr(Z_calc)}**")

# ═══════════════════════════════════════════════════════════════════
# 5. CONSTRUCCIÓN DE LA PÁGINA
# ═══════════════════════════════════════════════════════════════════
st.markdown("## 🧩 Solucionador de Programación Lineal")
st.caption("Aprende paso a paso de forma sencilla.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Configuración")
    is_max = st.radio("¿Qué quieres hacer?", ["Maximizar", "Minimizar"], horizontal=True) == "Maximizar"
    n = st.selectbox("Número de variables", [2, 3, 4, 5])
    n_cons = st.number_input("Número de restricciones", min_value=1, max_value=10, value=3)
    
    st.markdown("### Función Objetivo (Z)")
    obj_cols = st.columns(n); obj_vals = []
    for j in range(n):
        with obj_cols[j]:
            obj_vals.append(st.text_input(f"x{j+1}", value="0", key=f"obj_{j}", label_visibility="collapsed"))
            
    st.markdown("### Restricciones")
    constraints = []
    for i in range(n_cons):
        st.markdown(f"**Restricción {i+1}**")
        row = st.columns(n + 2); coefs = []
        for j in range(n):
            with row[j]: coefs.append(st.text_input(f"a{i}{j}", value="0", key=f"a_{i}_{j}", label_visibility="collapsed"))
        with row[n]: sense = st.selectbox(f"s{i}", ["<=", ">=", "="], key=f"s_{i}", label_visibility="collapsed")
        with row[n+1]: rhs = st.text_input(f"r{i}", value="0", key=f"r_{i}", label_visibility="collapsed")
        constraints.append({"coefs": coefs, "sense": sense, "rhs": rhs})
        
    st.divider()
    solve_btn = st.button("▶ RESOLVER PASO A PASO", type="primary", use_container_width=True)
    
    st.button("🔄 Cargar Ejemplo 1", use_container_width=True, on_click=cargar_ejemplo, args=(1,))
    st.button("🔄 Cargar Ejemplo 2", use_container_width=True, on_click=cargar_ejemplo, args=(2,))

# --- ÁREA PRINCIPAL ---
if solve_btn:
    try:
        c = [parse_frac(v) for v in obj_vals]
        A = [[parse_frac(v) for v in r["coefs"]] for r in constraints]
        senses = [r["sense"] for r in constraints]
        b = [parse_frac(r["rhs"]) for r in constraints]
        res = solve_lp(c, A, senses, b, is_max)
        st.session_state.update({"result": res, "c": c, "A": A, "senses": senses, "b": b, "is_max": is_max})
    except Exception as e:
        st.error(f"❌ Error: {e}")

if "result" not in st.session_state:
    st.info("👈 Llena los datos en la barra lateral y presiona **RESOLVER**.")
else:
    res, c, A, senses, b, is_max = [st.session_state[k] for k in ("result", "c", "A", "senses", "b", "is_max")]

    # Pestañas
    tab_res, tab_simplex, tab_dob = st.tabs(["🏆 Resultado", "🔢 Método Simplex", "⚙️ Método Doble Fase"])

    with tab_res:
        if res["status"] == "optimal":
            st.success("¡Lo logramos! Encontramos la mejor solución.")
            cols = st.columns(len(res["x"]) + 1)
            cols[0].metric("Valor de Z", fstr(res["Z"]))
            for i, v in enumerate(res["x"]):
                cols[i+1].metric(f"Variable x{i+1}", fstr(v))
        elif res["status"] == "infeasible": st.error("❌ No hay solución posible (Infactible). Las reglas se contradicen.")
        elif res["status"] == "unbounded": st.warning("⚠️ La solución puede crecer infinitamente (No Acotado).")

    with tab_simplex:
        sim_phases = [p for p in res["phases"] if "Fase 1" not in p["name"]]
        if not sim_phases:
            st.info("Este problema no necesita Simplex normal. Ve a la pestaña de Doble Fase.")
        else:
            # Creamos un mini-diccionario para pasar solo las fases de simplex
            res_simplex = {"phases": sim_phases, "status": res["status"], "x": res["x"]}
            render_metodo(res_simplex, is_max, c, A, senses, b, res["varNames"], res["totalCols"])

    with tab_dob:
        if len(res["phases"]) <= 1:
            st.info("Este problema no necesita Doble Fase (no hay restricciones ≥ ni =). Ve a la pestaña Simplex.")
        else:
            # Pasamos todas las fases
            render_metodo(res, is_max, c, A, senses, b, res["varNames"], res["totalCols"])