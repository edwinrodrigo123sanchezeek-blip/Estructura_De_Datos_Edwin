# app.py — PL Solver Completo y Didáctico (v3)
import streamlit as st
import pandas as pd
import math
from fractions import Fraction
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
# 3. MÉTODO GRÁFICO (MATEMÁTICAS Y DIBUJO)
# ═══════════════════════════════════════════════════════════════════
def _intersect(p0, p1, a, b, c):
    f0 = a*p0[0]+b*p0[1]-c; f1 = a*p1[0]+b*p1[1]-c
    d = f0 - f1
    if abs(d) < 1e-12: return [(p0[0]+p1[0])/2, (p0[1]+p1[1])/2]
    t = f0/d
    return [p0[0]+t*(p1[0]-p0[0]), p0[1]+t*(p1[1]-p0[1])]

def _clip(poly, a, b, c, sense):
    if not poly: return []
    eps = 1e-9
    inside = lambda p: (a*p[0]+b*p[1]-c) <= eps if sense == "<=" else (a*p[0]+b*p[1]-c) >= -eps
    out = []
    for i in range(len(poly)):
        cur, prev = poly[i], poly[(i+len(poly)-1)%len(poly)]
        ci, pi = inside(cur), inside(prev)
        if ci:
            if not pi: out.append(_intersect(prev, cur, a, b, c))
            out.append(cur)
        elif pi: out.append(_intersect(prev, cur, a, b, c))
    clean = []
    for p in out:
        if not any(abs(p[0]-q[0]) < 1e-7 and abs(p[1]-q[1]) < 1e-7 for q in clean):
            clean.append(p)
    return clean

def _line_in_box(a, b, c, X, Y):
    pts = []
    if abs(b) > 1e-12: pts += [[0, c/b], [X, (c-a*X)/b]]
    if abs(a) > 1e-12: pts += [[c/a, 0], [(c-b*Y)/a, Y]]
    pts = [[max(0, min(X, p[0])), max(0, min(Y, p[1]))] for p in pts
           if -1e-9 <= p[0] <= X+1e-9 and -1e-9 <= p[1] <= Y+1e-9]
    uniq = []
    for p in pts:
        if not any(abs(p[0]-q[0]) < 1e-7 and abs(p[1]-q[1]) < 1e-7 for q in uniq):
            uniq.append(p)
    if len(uniq) < 2: return None
    return max(((uniq[i], uniq[j]) for i in range(len(uniq))
                for j in range(i+1, len(uniq))),
               key=lambda s: (s[0][0]-s[1][0])**2 + (s[0][1]-s[1][1])**2)

def _nice(v):
    if v <= 0: return 1
    exp = math.floor(math.log10(v)); base = 10**exp; nn = v/base
    return (1 if nn <= 1 else 2 if nn <= 2 else 5 if nn <= 5 else 10) * base

def solve_graphical(c, A, senses, b, is_max, simplex_res):
    cons = [{"a": f2float(A[i][0]), "b": f2float(A[i][1]),
             "c": f2float(b[i]), "sense": senses[i]} for i in range(len(A))]

    maxx = maxy = 1.0
    for k in cons:
        maxx = max(maxx, abs(k["c"])); maxy = max(maxy, abs(k["c"]))
    for i in range(len(cons)):
        for j in range(i+1, len(cons)):
            a1, b1, c1 = cons[i]["a"], cons[i]["b"], cons[i]["c"]
            a2, b2, c2 = cons[j]["a"], cons[j]["b"], cons[j]["c"]
            det = a1*b2 - a2*b1
            if abs(det) < 1e-12: continue
            x = (c1*b2-c2*b1)/det; y = (a1*c2-a2*c1)/det
            if x >= 0 and y >= 0: maxx = max(maxx, x); maxy = max(maxy, y)
    for k in cons:
        if abs(k["a"]) > 1e-12:
            x = k["c"]/k["a"]
            if x >= 0: maxx = max(maxx, x)
        if abs(k["b"]) > 1e-12:
            y = k["c"]/k["b"]
            if y >= 0: maxy = max(maxy, y)

    X, Y = _nice(maxx*1.3), _nice(maxy*1.3)
    poly = [[0,0],[X,0],[X,Y],[0,Y]]
    for k in cons:
        if k["sense"] == "<=": poly = _clip(poly, k["a"], k["b"], k["c"], "<=")
        elif k["sense"] == ">=": poly = _clip(poly, k["a"], k["b"], k["c"], ">=")
        else:
            poly = _clip(poly, k["a"], k["b"], k["c"], "<=")
            poly = _clip(poly, k["a"], k["b"], k["c"], ">=")
        if not poly: break

    c1, c2 = f2float(c[0]), f2float(c[1])
    verts = [{"x": p[0], "y": p[1], "Z": c1*p[0]+c2*p[1], "opt": False} for p in poly]
    
    # Marcar el óptimo (viene del simplex)
    if simplex_res and simplex_res.get("status") == "optimal" and simplex_res.get("x"):
        ox, oy = f2float(simplex_res["x"][0]), f2float(simplex_res["x"][1])
        if verts:
            idx = min(range(len(verts)),
                      key=lambda i: (verts[i]["x"]-ox)**2 + (verts[i]["y"]-oy)**2)
            verts[idx]["opt"] = True

    fig, ax = plt.subplots(figsize=(8, 6), dpi=110)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.55)
    if len(poly) >= 3:
        pts = poly + [poly[0]]
        ax.fill([p[0] for p in pts], [p[1] for p in pts],
                color="#10b981", alpha=0.18, edgecolor="#10b981", linewidth=2)
    colors = ["#e11d48","#0891b2","#7c3aed","#ea580c","#059669","#db2777"]
    
    for i, k in enumerate(cons):
        seg = _line_in_box(k["a"], k["b"], k["c"], X, Y)
        if seg:
            ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                    color=colors[i % len(colors)], linewidth=2, alpha=0.85,
                    label=f"R{i+1} ({k['sense']})")
            
    for v in verts:
        if v["opt"]:
            ax.scatter(v["x"], v["y"], s=200, c="#f59e0b", edgecolors="#b45309", linewidths=2.5, zorder=5)
            ax.annotate(f"({v['x']:.2f}, {v['y']:.2f})\nZ={v['Z']:.2f}", (v["x"], v["y"]),
                        xytext=(9, 9), textcoords="offset points", fontsize=10,
                        fontweight="bold", color="#92400e",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#f59e0b"))
        else:
            ax.scatter(v["x"], v["y"], s=60, c="white", edgecolors="#0f172a", linewidths=2, zorder=5)
            ax.annotate(f"({v['x']:.2f}, {v['y']:.2f})", (v["x"], v["y"]),
                        xytext=(6, 6), textcoords="offset points", fontsize=8.5, color="#475569")
            
    ax.set_xlim(0, X); ax.set_ylim(0, Y)
    ax.set_xlabel("x₁", fontsize=12, fontweight="bold"); ax.set_ylabel("x₂", fontsize=12, fontweight="bold")
    ax.set_title("Región factible y vértices", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    buf = BytesIO()
    plt.tight_layout(); fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return {"png": buf.read(), "vertices": verts, "feasible": len(poly) >= 3}

# ═══════════════════════════════════════════════════════════════════
# 4. COMPROBACIÓN Y RENDERIZADO
# ═══════════════════════════════════════════════════════════════════
def generar_comprobacion(x, A, senses, b, c, is_max):
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
            "Tus datos": f"{fstr(A[i][0])}x₁ + {fstr(A[i][1])}x₂ {sense} {fstr(rhs)}",
            "Reemplazando": f"{fstr(lhs)} {sense} {fstr(rhs)}",
            "¿Se cumple?": "✅ Sí" if ok else "❌ No"
        })
    
    Z_calc = sum(x[j] * c[j] for j in range(len(x)))
    return checks, Z_calc

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
            if leave is not None and leave < len(M):
                styles.iloc[leave, enter + 1] = 'background-color: #4f46e5; color: white; font-weight: bold;'
        return styles
    return df.style.apply(style_cell, axis=None)

def render_metodo(res, is_max, c, A, senses, b, nombres, total):
    for ph in res["phases"]:
        st.markdown(f"### {ph['name']}")
        
        if "Fase 1" in ph["name"]:
            ok = ph["W"] == "0"
            st.warning("🤫 **Fase 1:** Usamos las variables artificiales **R** para poder empezar. Si logramos que su suma (W) sea 0, el truco funcionó y pasamos a la Fase 2." + (" ✅ ¡W es 0, funcionó!" if ok else " ❌ W no es 0. El problema es imposible."))
        
        for k, stp in enumerate(ph["steps"]):
            if stp["note"]:
                st.success(f"🏁 **Fin:** {stp['note']}")
                continue
            
            txt = f"""
            **Iteración {k+1}:**
            * 👀 **Variable que entra:** `{nombres[stp['enter']]}`. ¿Por qué? Porque en la fila de abajo (Cj−Zj) es el número positivo más grande (tiene un **{fstr(stp['r'][stp['enter']])}**).
            * ➗ **Variable que sale:** `{nombres[stp['basis'][stp['leave']]]}`. ¿Por qué? Dividimos la columna RHS entre la columna de `{nombres[stp['enter']]}`. La razón más pequeña fue **{fstr(stp['ratio'])}**.
            * 🎯 **Pivote:** El número donde se cruzan es **{fstr(stp['pivot'])}**. 
            * ⚙️ **Operación:** Dividimos toda la fila del pivote entre `{fstr(stp['pivot'])}` para que se vuelva 1, y luego restamos esta fila a las demás para hacer 0 en la columna de `{nombres[stp['enter']]}`.
            """
            st.info(txt)
            df = build_dataframe(stp["M"], stp["basis"], stp["r"], nombres, total, stp["enter"], stp["leave"])
            st.dataframe(df, use_container_width=True)
            
    # COMPROBACIÓN AL FINAL DEL MÉTODO
    if res["status"] == "optimal":
        st.divider()
        st.markdown("### ✅ Comprobación de la Solución")
        st.write("Aquí reemplazamos los valores de \(x₁, x₂...\) en tus restricciones originales para ver si todo cuadra.")
        
        checks, Z_calc = generar_comprobacion(res["x"], A, senses, b, c, is_max)
        df_check = pd.DataFrame(checks)
        st.dataframe(df_check, use_container_width=True, hide_index=True)
        st.success(f"Al reemplazar en Z, nos da exactamente: **Z = {fstr(Z_calc)}**")

# ═══════════════════════════════════════════════════════════════════
# 5. INTERFAZ (SIDEBAR Y MAIN)
# ═══════════════════════════════════════════════════════════════════
st.markdown("## 🧩 Solucionador de Programación Lineal")

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

with st.sidebar:
    st.title("⚙️ Configuración")
    
    # SELECTOR DE MÉTODO
    metodo = st.selectbox("Método a usar", ["Método Gráfico", "Método Simplex", "Método Doble Fase"])
    
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
    solve_btn = st.button("▶ RESOLVER", type="primary", use_container_width=True)
    
    st.button("🔄 Cargar Ejemplo 1 (Max ≤)", use_container_width=True, on_click=cargar_ejemplo, args=(1,))
    st.button("🔄 Cargar Ejemplo 2 (Min ≥)", use_container_width=True, on_click=cargar_ejemplo, args=(2,))

# --- ÁREA PRINCIPAL ---
if solve_btn:
    if metodo == "Método Gráfico" and n != 2:
        st.error("El Método Gráfico solo funciona con exactamente 2 variables. Cambia el número de variables o elige otro método.")
    else:
        try:
            c = [parse_frac(v) for v in obj_vals]
            A = [[parse_frac(v) for v in r["coefs"]] for r in constraints]
            senses = [r["sense"] for r in constraints]
            b = [parse_frac(r["rhs"]) for r in constraints]
            
            # Siempre resolvemos con Simplex por debajo para saber el resultado óptimo
            res = solve_lp(c, A, senses, b, is_max)
            
            st.session_state.update({
                "result": res, "c": c, "A": A, "senses": senses, "b": b, "is_max": is_max,
                "metodo": metodo, "n_vars": n
            })
        except Exception as e:
            st.error(f"❌ Error: {e}")

if "result" not in st.session_state:
    st.info("👈 Configura tu problema en la barra lateral, elige un método y presiona **RESOLVER**.")
else:
    res = st.session_state.result
    c, A, senses, b = st.session_state.c, st.session_state.A, st.session_state.senses, st.session_state.b
    is_max, metodo, n_vars = st.session_state.is_max, st.session_state.metodo, st.session_state.n_vars

    st.markdown(f"## 📝 Resolución por {metodo}")
    
    if res["status"] == "optimal":
        st.success("¡Lo logramos! Encontramos la mejor solución.")
        cols = st.columns(len(res["x"]) + 1)
        cols[0].metric("Valor de Z", fstr(res["Z"]))
        for i, v in enumerate(res["x"]):
            cols[i+1].metric(f"Variable x{i+1}", fstr(v))
    elif res["status"] == "infeasible": st.error("❌ No hay solución posible (Infactible). Las reglas se contradicen.")
    elif res["status"] == "unbounded": st.warning("⚠️ La solución puede crecer infinitamente (No Acotado).")
    
    st.divider()

    # --- RENDERIZADO SEGÚN EL MÉTODO ELEGIDO ---
    if metodo == "Método Gráfico":
        st.markdown("### 📊 Gráfico de la Región Factible")
        g = solve_graphical(c, A, senses, b, is_max, res)
        col_img, col_info = st.columns([1.5, 1])
        with col_img:
            st.image(g["png"], use_column_width=True)
        with col_info:
            st.markdown("#### Vértices Evaluados")
            if g["vertices"]:
                for i, v in enumerate(g["vertices"]):
                    icon = "⭐" if v["opt"] else "📍"
                    color = "green" if v["opt"] else "black"
                    st.markdown(f"**{icon} Punto {i+1}:** ({round(v['x'], 2)}, {round(v['y'], 2)}) → **Z = {round(v['Z'], 2)}**")
        
        # Comprobación también para el gráfico
        if res["status"] == "optimal":
            st.divider()
            st.markdown("### ✅ Comprobación de la Solución")
            checks, Z_calc = generar_comprobacion(res["x"], A, senses, b, c, is_max)
            st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)
            st.success(f"Al reemplazar en Z, nos da exactamente: **Z = {fstr(Z_calc)}**")

    elif metodo == "Método Simplex":
        sim_phases = [p for p in res["phases"] if "Fase 1" not in p["name"]]
        if not sim_phases:
            st.warning("Este problema no se puede resolver con Simplex directo porque tiene restricciones ≥ o =. Ve a 'Método Doble Fase'.")
        else:
            res_simplex = {"phases": sim_phases, "status": res["status"]}
            if "x" in res: res_simplex["x"] = res["x"]
            render_metodo(res_simplex, is_max, c, A, senses, b, res["varNames"], res["totalCols"])

    elif metodo == "Método Doble Fase":
        if len(res["phases"]) <= 1:
            st.warning("Este problema no necesita Doble Fase (no hay restricciones ≥ ni =). Ve a 'Método Simplex'.")
        else:
            render_metodo(res, is_max, c, A, senses, b, res["varNames"], res["totalCols"])