# app.py — PL Solver con interfaz didáctica
import streamlit as st
import pandas as pd
import math
from fractions import Fraction
from io import BytesIO

st.set_page_config(page_title="PL Solver Didáctico", page_icon="📐", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# 1. ARITMÉTICA CON FRACCIONES
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
# 2. MOTOR SIMPLEX / DOBLE FASE (Variables: s, e, R)
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
            snap["note"] = "Todos los Cj − Zj ≤ 0 ⟹ Solución óptima alcanzada."
            steps.append(snap); return "optimal", steps
        leave, best = -1, None
        for i in range(len(M)):
            if M[i][enter] > 0:
                q = M[i][total] / M[i][enter]
                if best is None or q < best: best, leave = q, i
        if leave < 0:
            snap["note"] = "Variable entrante sin límite ⟹ Problema NO ACOTADO."
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
            res["preNotes"].append(f"R{i+1} multiplicada por −1 (RHS negativo).")

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
    
    # ASIGNACIÓN DE NOMBRES: s (holgura), e (exceso), R (artificial)
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
        res["phases"].append({"name": "Fase 1 (Doble Fase)", "steps": steps1, "status": st1, "W": fstr(W)})
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
    res["phases"].append({"name": "Fase 2 (Simplex)" if artif else "Simplex", "steps": steps2, "status": st2})

    if st2 == "unbounded": res["status"] = "unbounded"; return res
    if st2 != "optimal":   res["status"] = "error"; return res

    x = [Fraction(0)]*n
    for i in range(m):
        if basis[i] < n: x[basis[i]] = M[i][total]
    Zmax = -r2[total]
    res.update({"x": x, "Zmax": Zmax, "Z": Zmax if is_max else -Zmax, "status": "optimal"})
    return res

# ═══════════════════════════════════════════════════════════════════
# 3. MÉTODO GRÁFICO
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
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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
            ax.annotate(f"({v['x']:.2f}, {v['y']:.2f})", (v["x"], v["y"]),
                        xytext=(9, 9), textcoords="offset points", fontsize=10.5,
                        fontweight="bold", color="#92400e",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#f59e0b"))
        else:
            ax.scatter(v["x"], v["y"], s=60, c="white", edgecolors="#0f172a", linewidths=2, zorder=5)
            ax.annotate(f"({v['x']:.2f}, {v['y']:.2f})", (v["x"], v["y"]),
                        xytext=(6, 6), textcoords="offset points", fontsize=8.5, color="#475569")
    ax.set_xlim(0, X); ax.set_ylim(0, Y)
    ax.set_xlabel("x₁", fontsize=12, fontweight="bold"); ax.set_ylabel("x₂", fontsize=12, fontweight="bold")
    ax.set_title("Región factible · vértices · óptimo", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    buf = BytesIO()
    plt.tight_layout(); fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return {"png": buf.read(), "vertices": verts, "feasible": len(poly) >= 3}

# ═══════════════════════════════════════════════════════════════════
# 4. INTERFAZ STREAMLIT ESTILO "PASO A PASO"
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* Estilos generales de las tablas */
.custom-table { border-collapse: collapse; margin: 15px 0; font-size: 0.95rem; width: 100%; font-variant-numeric: tabular-nums; }
.custom-table th { background-color: #e0f2fe; color: #0369a1; padding: 12px; text-align: center; border: 1px solid #bae6fd; font-weight: bold; }
.custom-table td { padding: 10px 12px; text-align: center; border: 1px solid #e2e8f0; background-color: white; }
.custom-table td.rhs { background-color: #ecfdf5; color: #047857; font-weight: bold; border-left: 2px solid #10b981; }
.custom-table td.basis { background-color: #f8fafc; font-weight: bold; color: #334155; }
.custom-table tr.z-row td { background-color: #fef2f2; color: #991b1b; font-weight: bold; border-top: 2px solid #ef4444; }
.custom-table td.pivot { background-color: #4f46e5; color: white; font-weight: bold; border-radius: 4px; }
.custom-table td.enter-col { background-color: #f3e8ff; }

/* Cajas de explicación */
.explain-box { background-color: #f0f9ff; border-left: 5px solid #3b82f6; padding: 16px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.explain-box h4 { margin-top: 0; color: #1e3a8a; font-size: 1.05rem; margin-bottom: 10px; }
.explain-box ul { margin: 0; padding-left: 20px; color: #334155; font-size: 0.95rem; line-height: 1.6; }
.explain-box li { margin-bottom: 6px; }
.explain-box b { color: #1e293b; }
.explain-box code { background-color: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: bold; }

/* Fracciones */
.frac{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;line-height:1;font-size:.92em;margin:0 2px}
.frac .num{border-bottom:1.4px solid currentColor;padding:0 3px}
.frac .den{padding:0 3px}

/* Cajas de resultados */
.metric-box{background:#f8fafc;border-radius:12px;padding:15px;border:1px solid #e2e8f0;text-align:center;box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
.metric-box small{display:block;color:#64748b;font-size:.8em;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:5px;}
.metric-box .v{font-size:1.4rem;font-weight:800;color:#047857;}
</style>
""", unsafe_allow_html=True)

def html_frac(s):
    s = str(s)
    if "/" not in s: return s
    n, d = s.split("/")
    neg = n.startswith("-")
    nn = n[1:] if neg else n
    return f'{"−" if neg else ""}<span class="frac"><span class="num">{nn}</span><span class="den">{d}</span></span>'

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configuración")
    
    st.markdown("### 1. Dirección de la Función")
    is_max = st.radio("Objetivo", ["Maximizar", "Minimizar"], horizontal=True) == "Maximizar"
    
    st.markdown("### 2. Dimensiones")
    n = st.selectbox("Número de variables", [2, 3, 4, 5])
    n_cons = st.number_input("Número de restricciones", min_value=1, max_value=10, value=3, step=1)
    
    st.markdown("### 3. Función Objetivo (Z)")
    obj_cols = st.columns(n)
    obj_vals = []
    for j in range(n):
        with obj_cols[j]:
            obj_vals.append(st.text_input(f"x{j+1}", value="0", key=f"obj_{j}", label_visibility="collapsed"))
            
    st.markdown("### 4. Restricciones")
    st.caption("Ingresa coeficientes, signo y RHS.")
    constraints = []
    for i in range(n_cons):
        st.markdown(f"**Restricción {i+1}**")
        row = st.columns(n + 2)
        coefs = []
        for j in range(n):
            with row[j]:
                coefs.append(st.text_input(f"a{i}{j}", value="0", key=f"a_{i}_{j}", label_visibility="collapsed", placeholder=f"x{j+1}"))
        with row[n]:
            sense = st.selectbox(f"s{i}", ["<=", ">=", "="], key=f"s_{i}", label_visibility="collapsed")
        with row[n+1]:
            rhs = st.text_input(f"r{i}", value="0", key=f"r_{i}", label_visibility="collapsed", placeholder="RHS")
        constraints.append({"coefs": coefs, "sense": sense, "rhs": rhs})
        
    st.divider()
    solve_btn = st.button("▶ RESOLVER PASO A PASO", type="primary", use_container_width=True)
    
    # Botones de ejemplos
    st.markdown("### 💡 Ejemplos")
    if st.button("Cargar Ejemplo Max ≤", use_container_width=True):
        st.session_state.ejemplo = 0
    if st.button("Cargar Ejemplo Min ≥", use_container_width=True):
        st.session_state.ejemplo = 1

# Lógica para cargar ejemplos
if "ejemplo" in st.session_state:
    ej = st.session_state.ejemplo
    if ej == 0:
        st.session_state.obj_0, st.session_state.obj_1 = "3", "5"
        st.session_state.a_0_0, st.session_state.a_0_1, st.session_state.s_0, st.session_state.r_0 = "1", "0", "<=", "4"
        st.session_state.a_1_0, st.session_state.a_1_1, st.session_state.s_1, st.session_state.r_1 = "0", "2", "<=", "12"
        st.session_state.a_2_0, st.session_state.a_2_1, st.session_state.s_2, st.session_state.r_2 = "3", "2", "<=", "18"
    elif ej == 1:
        st.session_state.obj_0, st.session_state.obj_1 = "2", "3"
        st.session_state.a_0_0, st.session_state.a_0_1, st.session_state.s_0, st.session_state.r_0 = "1", "1", ">=", "4"
        st.session_state.a_1_0, st.session_state.a_1_1, st.session_state.s_1, st.session_state.r_1 = "1", "3", ">=", "6"
        st.session_state.a_2_0, st.session_state.a_2_1, st.session_state.s_2, st.session_state.r_2 = "2", "1", ">=", "5"
    del st.session_state.ejemplo
    st.rerun()


# --- ÁREA PRINCIPAL ---
st.markdown("## 📐 Solución Paso a Paso")

if solve_btn:
    try:
        c = [parse_frac(v) for v in obj_vals]
        A = [[parse_frac(v) for v in r["coefs"]] for r in constraints]
        senses = [r["sense"] for r in constraints]
        b = [parse_frac(r["rhs"]) for r in constraints]
        res = solve_lp(c, A, senses, b, is_max)
        st.session_state.result = res
        st.session_state.c = c; st.session_state.A = A; st.session_state.s = senses; st.session_state.b = b
        st.session_state.is_max = is_max
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.pop("result", None)

if "result" not in st.session_state:
    st.info("👈 Configura tu problema en la barra lateral y presiona **Resolver**.")
else:
    res = st.session_state.result
    c = st.session_state.c; A = st.session_state.A; senses = st.session_state.s; b = st.session_state.b
    is_max = st.session_state.is_max

    # --- RESULTADO FINAL ---
    if res["status"] == "optimal":
        st.success(f"✅ **Solución Óptima Encontrada**")
        boxes = st.columns(len(res["x"]) + 1)
        with boxes[0]:
            st.markdown(f"<div class='metric-box'><small>Z {('Máx' if is_max else 'Mín')}</small><div class='v'>{html_frac(fstr(res['Z']))}</div></div>", unsafe_allow_html=True)
        for i, v in enumerate(res["x"]):
            with boxes[i+1]:
                st.markdown(f"<div class='metric-box'><small>Variable x{i+1}</small><div class='v'>{html_frac(fstr(v))}</div></div>", unsafe_allow_html=True)
    elif res["status"] == "infeasible": st.error("❌ Problema Infactible.")
    elif res["status"] == "unbounded": st.warning("⚠️ Problema No Acotado.")

    st.divider()

    # --- TABS ---
    tab_g, tab_s, tab_df = st.tabs(["📊 Gráfico (2D)", "🔢 Simplex", "⚙️ Doble Fase"])

    # Función para renderizar tablas
    def render_table_html(M, basis, r, names, total, enter=None, leave=None):
        h = '<table class="custom-table"><thead><tr><th>VB</th>'
        for nm in names: h += f'<th>{nm}</th>'
        h += '<th>RHS</th></tr></thead><tbody>'
        for i, row in enumerate(M):
            h += f'<tr><td class="basis">{names[basis[i]]}</td>'
            for j, v in enumerate(row):
                cls = "rhs" if j == total else ""
                if enter is not None and j == enter:
                    cls += " enter-col"
                    if i == leave: cls = "pivot"
                h += f'<td class="{cls}">{html_frac(fstr(v))}</td>'
            h += '</tr>'
        h += '<tr class="z-row"><td class="basis">Cj−Zj</td>'
        for j, v in enumerate(r):
            cls = "rhs" if j == total else ""
            if enter is not None and j == enter: cls += " enter-col"
            h += f'<td class="{cls}">{html_frac(fstr(v))}</td>'
        h += '</tr></tbody></table>'
        return h

    def render_phase(phase, names, total):
        out = ""
        for k, stp in enumerate(phase["steps"]):
            if stp["note"]:
                out += f'<div class="explain-box"><h4>🏁 Fin de la Fase</h4><p>{stp["note"]}</p></div>'
            else:
                out += f'<div class="explain-box"><h4>Paso {k+1}: Iteración</h4>'
                out += '<ul>'
                out += f'<li>➡️ <b>Entra a la base:</b> La variable <code>{names[stp["enter"]]}</code> porque tiene el valor más positivo en Cj−Zj ({html_frac(fstr(stp["r"][stp["enter"]]))}).</li>'
                out += f'<li>⬅️ <b>Sale de la base:</b> La variable <code>{names[stp["basis"][stp["leave"]]]}</code> porque su razón (RHS / columna entrante) es la mínima ({html_frac(fstr(stp["ratio"]))}).</li>'
                out += f'<li>🎯 <b>Elemento Pivote:</b> Es el número <b>{html_frac(fstr(stp["pivot"]))}</b> (intersección).</li>'
                out += '</ul></div>'
            out += render_table_html(stp["M"], stp["basis"], stp["r"], names, total, stp["enter"], stp["leave"])
        return out

    names = res.get("varNames", []); total = res.get("totalCols", 0)

    # --- PESTAÑA GRÁFICO ---
    with tab_g:
        if res["n"] != 2:
            st.info("El método gráfico solo está disponible para 2 variables. Usa las otras pestañas.")
        elif res["status"] in ("optimal", "unbounded"):
            g = solve_graphical(c, A, senses, b, is_max, res)
            col1, col2 = st.columns([1.5, 1])
            with col1:
                st.image(g["png"], use_column_width=True)
            with col2:
                st.markdown("### Vértices Evaluados")
                if g["vertices"]:
                    for i, v in enumerate(g["vertices"]):
                        icon = "⭐" if v["opt"] else "📍"
                        color = "green" if v["opt"] else "black"
                        st.markdown(f"**{icon} Punto {i+1}:** ({round(v['x'], 2)}, {round(v['y'], 2)}) → **Z = {round(v['Z'], 2)}**")

    # --- PESTAÑA SIMPLEX ---
    with tab_s:
        sim_phases = [p for p in res["phases"] if "Fase 1" not in p["name"]]
        if not sim_phases:
            st.info("Este problema se resolvió completamente en la Doble Fase.")
        else:
            st.markdown(f"#### Método Simplex (Variables de holgura: s, exceso: e, artificiales: R)")
            for ph in sim_phases:
                st.markdown(render_phase(ph, names, total), unsafe_allow_html=True)

    # --- PESTAÑA DOBLE FASE ---
    with tab_df:
        if len(res["phases"]) <= 1:
            st.info("Este problema no requiere Doble Fase (no hay restricciones ≥ ni =). Ve a la pestaña Simplex.")
        else:
            st.markdown("#### Método de las Dos Fases")
            for ph in res["phases"]:
                if "Fase 1" in ph["name"]:
                    ok = ph["W"] == "0"
                    msg = "✅ Como W = 0, hemos encontrado una solución factible inicial. Pasamos a la Fase 2." if ok else "❌ Como W ≠ 0, el problema es infactible."
                    st.info(msg)
                st.markdown(render_phase(ph, names, total), unsafe_allow_html=True)