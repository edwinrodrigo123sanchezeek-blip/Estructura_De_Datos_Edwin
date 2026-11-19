# app.py — PL Solver (Corregido para botones de ejemplo)
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
    if isinstance(f, Fraction):
        return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"
    return str(f)

def f2float(s):
    if isinstance(s, Fraction): return float(s)
    if isinstance(s, (int, float)): return float(s)
    a, _, b = str(s).partition('/')
    return float(a)/float(b) if b else float(a)

def parse_frac(s):
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
            snap["note"] = "¡Cuidado! El problema no tiene fin, puede crecer infinitamente (No Acotado)."
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

    for i in range(m):
        if b2[i] < 0:
            A2[i] = [-x for x in A2[i]]; b2[i] = -b2[i]
            s2[i] = ">=" if s2[i] == "<=" else ("<=" if s2[i] == ">=" else "=")
            res["preNotes"].append(f"R{i+1} se multiplicó por −1 para que el lado derecho sea positivo.")

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

    if artif:
        c1 = [Fraction(0)]*total
        for j in artif: c1[j] = Fraction(-1)
        r1 = _build_row(M, basis, c1, total)
        st1, steps1 = _simplex(M, basis, r1, total, set())
        W = r1[total]
        res["phases"].append({"name": "Fase 1", "steps": steps1, "status": st1, "W": fstr(W)})
        if W != 0:
            res["status"] = "infeasible"; return res
        for i in range(m):
            if basis[i] in artif:
                found = next((j for j in range(total) if j not in artif and M[i][j] != 0), -1)
                if found >= 0: _pivot(M, i, found, total); basis[i] = found

    c2 = [Fraction(0)]*total
    for j in range(n): c2[j] = c_obj[j]
    r2 = _build_row(M, basis, c2, total)
    st2, steps2 = _simplex(M, basis, r2, total, set(artif))
    res["phases"].append({"name": "Fase 2" if artif else "Simplex", "steps": steps2, "status": st2})

    if st2 == "unbounded": res["status"] = "unbounded"; return res
    if st2 != "optimal":   res["status"] = "error"; return res

    x = [Fraction(0)]*n
    for i in range(m):
        if basis[i] < n: x[basis[i]] = M[i][total]
    Zmax = -r2[total]
    res.update({"x": x, "Zmax": Zmax, "Z": Zmax if is_max else -Zmax, "status": "optimal"})
    return res

# ═══════════════════════════════════════════════════════════════════
# 3. COMPROBACIÓN
# ═══════════════════════════════════════════════════════════════════
def verificar_solucion(x, A, senses, b, c, is_max):
    checks = []
    for i in range(len(A)):
        lhs = sum(x[j] * A[i][j] for j in range(len(x)))
        rhs = b[i]
        sense = senses[i]
        
        if sense == "<=": ok = lhs <= rhs
        elif sense == ">=": ok = lhs >= rhs
        else: ok = lhs == rhs
        
        checks.append({
            "Restricción": f"R{i+1}",
            "Original": f"{fstr(A[i][0])}x₁ + {fstr(A[i][1])}x₂ {sense} {fstr(rhs)}",
            "Cálculo": f"{fstr(lhs)} {sense} {fstr(rhs)}",
            "¿Cumple?": "✅ Sí" if ok else "❌ No"
        })
    
    Z_calc = sum(x[j] * c[j] for j in range(len(x)))
    return checks, Z_calc

# ═══════════════════════════════════════════════════════════════════
# 4. FUNCIÓN PARA CARGAR EJEMPLOS (Evita el error de Streamlit)
# ═══════════════════════════════════════════════════════════════════
def cargar_ejemplo(id_ejemplo):
    if id_ejemplo == 1:
        st.session_state.obj_0, st.session_state.obj_1 = "3", "5"
        for i, (c0, c1, s, r) in enumerate([("1","0","<=","4"), ("0","2","<=","12"), ("3","2","<=","18")]):
            st.session_state[f"a_{i}_0"] = c0
            st.session_state[f"a_{i}_1"] = c1
            st.session_state[f"s_{i}"] = s
            st.session_state[f"r_{i}"] = r
    elif id_ejemplo == 2:
        st.session_state.obj_0, st.session_state.obj_1 = "2", "3"
        for i, (c0, c1, s, r) in enumerate([("1","1",">=","4"), ("1","3",">=","6"), ("2","1",">=","5")]):
            st.session_state[f"a_{i}_0"] = c0
            st.session_state[f"a_{i}_1"] = c1
            st.session_state[f"s_{i}"] = s
            st.session_state[f"r_{i}"] = r

# ═══════════════════════════════════════════════════════════════════
# 5. INTERFAZ GRÁFICA
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
    
    # AQUÍ ESTÁ LA MAGIA: Usamos on_click para cambiar los datos sin romper la app
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

    # --- TABLAS ---
    def build_dataframe(M, basis, r, names, total, enter=None, leave=None):
        data = []
        for i, row in enumerate(M):
            data.append([names[basis[i]]] + [fstr(v) for v in row])
        data.append(["Cj−Zj"] + [fstr(v) for v in r])
        cols = ["Base"] + names + ["RHS"]
        df = pd.DataFrame(data, columns=cols)

        def style_cell(x):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            styles.iloc[:, -1] = 'background-color: #dcfce7; color: #166534; font-weight: bold;'
            styles.iloc[-1, :] = 'background-color: #fef08a; color: #854d0e; font-weight: bold; border-top: 2px solid #eab308;'
            styles.iloc[:, 0] = 'background-color: #f1f5f9; color: #334155; font-weight: bold;'
            
            if enter is not None:
                styles.iloc[:, enter + 1] = 'background-color: #f3e8ff;'
                if leave is not None:
                    styles.iloc[leave, enter + 1] = 'background-color: #4f46e5; color: white; font-weight: bold;'
            return styles

        return df.style.apply(style_cell, axis=None)

    def render_phase(phase, names, total):
        out = []
        for k, stp in enumerate(phase["steps"]):
            if stp["note"]:
                out.append(st.info(f"🏁 **Fin:** {stp['note']}"))
            else:
                txt = f"""
                **Paso {k+1}:**
                1. 👀 Mira la fila de abajo (Cj−Zj) y busca el número positivo más grande. Ese nos dice qué variable entra. Aquí es **`{names[stp['enter']]}`** (porque tiene {fstr(stp['r'][stp['enter']])}).
                2. ➗ Divide la columna RHS entre la columna de **`{names[stp['enter']]}`**. El resultado más pequeño (y positivo) nos dice quién sale. Aquí sale **`{names[stp['basis'][stp['leave']]]}`** (porque {fstr(stp['M'][stp['leave']][total])} ÷ {fstr(stp['pivot'])} = {fstr(stp['ratio'])}).
                3. 🎯 El número donde se cruzan (el **Pivote**) es **{fstr(stp['pivot'])}**. Hacemos las operaciones de resta para hacer un 1 en el pivote y 0 en su columna.
                """
                out.append(st.info(txt))
            out.append(build_dataframe(stp["M"], stp["basis"], stp["r"], names, total, stp["enter"], stp["leave"]))
        return out

    names = res.get("varNames", []); total = res.get("totalCols", 0)

    tab_res, tab_simplex, tab_dob, tab_verif = st.tabs(["🏆 Resultado", "🔢 Simplex", "⚙️ Doble Fase", "✅ Comprobación"])

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
        if not sim_phases: st.info("Este problema no necesita Simplex normal, ve a Doble Fase.")
        for ph in sim_phases:
            st.markdown(f"### {ph['name']}")
            for el in render_phase(ph, names, total): st.write(el)

    with tab_dob:
        if len(res["phases"]) <= 1: st.info("Este problema no necesita Doble Fase (no hay restricciones ≥ ni =).")
        else:
            for ph in res["phases"]:
                st.markdown(f"### {ph['name']}")
                if "Fase 1" in ph["name"]:
                    ok = ph["W"] == "0"
                    st.info("🤫 **Fase 1:** Usamos las variables artificiales **R** como un 'truco' para poder empezar. Si al final logramos que su suma sea 0, el truco funcionó y pasamos a la Fase 2." + ("" if ok else " Pero la suma no dio 0, así que el problema es imposible."))
                for el in render_phase(ph, names, total): st.write(el)

    with tab_verif:
        if res["status"] == "optimal":
            st.markdown("### 🕵️‍♂️ Comprobando la Solución")
            st.write("Aquí reemplazamos los valores de \(x₁, x₂...\) en tus restricciones originales para ver si todo cuadra.")
            checks, Z_calc = verificar_solucion(res["x"], A, senses, b, c, is_max)
            
            df_check = pd.DataFrame(checks)
            st.dataframe(df_check, use_container_width=True, hide_index=True)
            
            st.success(f"Al reemplazar en Z, nos da exactamente: **Z = {fstr(Z_calc)}**")
        else:
            st.info("No hay solución óptima para comprobar.")