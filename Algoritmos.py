import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import math


# ================================================================
#                ALGORITMOS (VERSIONES PASO A PASO)
# ================================================================

def dijkstra_pasos(grafo, inicio, destino=None):
    dist = {v: float('inf') for v in grafo}
    dist[inicio] = 0
    prev = {v: None for v in grafo}
    cola = [(0, inicio)]
    visitados = set()

    yield {'tipo': 'inicio', 'dist': dict(dist), 'visitados': set(),
           'actual': None, 'arista': None, 'prev': dict(prev),
           'msg': f'▶ Inicio: origen {inicio}, distancia 0'}

    while cola:
        d, u = heapq.heappop(cola)
        if d > dist[u]:
            continue
        visitados.add(u)
        yield {'tipo': 'visitar', 'dist': dict(dist),
               'visitados': set(visitados), 'actual': u,
               'arista': None, 'prev': dict(prev),
               'msg': f'● Extraer {u} (d={d:g}) de la cola'}

        for v, w in grafo[u]:
            if v in visitados:
                continue
            nd = d + w
            if nd < dist[v]:
                ant = dist[v]
                dist[v] = nd
                prev[v] = u
                heapq.heappush(cola, (nd, v))
                muestra = '∞' if ant == float('inf') else f'{ant:g}'
                yield {'tipo': 'relajar', 'dist': dict(dist),
                       'visitados': set(visitados), 'actual': u,
                       'arista': (u, v), 'prev': dict(prev),
                       'msg': f'  → Mejorar {u}→{v}: {muestra} → {nd:g}'}
            else:
                yield {'tipo': 'no_mejora', 'dist': dict(dist),
                       'visitados': set(visitados), 'actual': u,
                       'arista': (u, v), 'prev': dict(prev),
                       'msg': f'  · {u}→{v}: sin mejora ({d+w:g} ≥ {dist[v]:g})'}

    if destino and destino in grafo and dist[destino] < float('inf'):
        camino = reconstruir_camino(prev, destino)
        yield {'tipo': 'fin', 'dist': dict(dist),
               'visitados': set(visitados), 'actual': None,
               'arista': None, 'prev': dict(prev),
               'camino_completo': camino,
               'msg': f'✓ Fin. Trazando ruta hacia {destino}...'}
        for i in range(2, len(camino) + 1):
            yield {'tipo': 'traza', 'dist': dict(dist),
                   'visitados': set(visitados), 'actual': None,
                   'arista': None, 'prev': dict(prev),
                   'camino_completo': camino, 'camino_hasta': camino[:i],
                   'msg': f'Ruta: {" → ".join(camino[:i])}'}
    else:
        yield {'tipo': 'fin', 'dist': dict(dist),
               'visitados': set(visitados), 'actual': None,
               'arista': None, 'prev': dict(prev),
               'msg': '✓ Fin del algoritmo'}


def reconstruir_camino(prev, destino):
    camino = []
    a = destino
    while a is not None:
        camino.insert(0, a)
        a = prev[a]
    return camino


def floyd_pasos(matriz, nodos, ini_idx=None, fin_idx=None):
    n = len(matriz)
    dist = [f[:] for f in matriz]
    sig = [[j if dist[i][j] != float('inf') else None for j in range(n)]
           for i in range(n)]

    yield {'tipo': 'inicio', 'k': -1, 'dist': [f[:] for f in dist],
           'msg': '▶ Inicio. Matriz inicial de distancias.'}

    for k in range(n):
        yield {'tipo': 'k_inicio', 'k': k, 'dist': [f[:] for f in dist],
               'msg': f'Analizando k={nodos[k]} como intermediario'}
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    anterior = dist[i][j]
                    dist[i][j] = dist[i][k] + dist[k][j]
                    sig[i][j] = sig[i][k]
                    ma = '∞' if anterior == float('inf') else f'{anterior:g}'
                    yield {'tipo': 'update', 'k': k,
                           'dist': [f[:] for f in dist],
                           'i': i, 'j': j,
                           'msg': (f'  → Mejorar d[{nodos[i]}][{nodos[j]}]: '
                                   f'{ma} → {dist[i][j]:g} (via {nodos[k]})')}
        yield {'tipo': 'k_fin', 'k': k, 'dist': [f[:] for f in dist],
               'msg': f'Fin iteración k={nodos[k]}'}

    yield {'tipo': 'fin', 'k': n, 'dist': [f[:] for f in dist],
           'sig': [s[:] for s in sig],
           'msg': '✓ Algoritmo de Floyd completado'}

    if ini_idx is not None and fin_idx is not None:
        camino = camino_floyd(sig, ini_idx, fin_idx, nodos)
        if camino:
            for i in range(2, len(camino) + 1):
                yield {'tipo': 'traza', 'k': n,
                       'dist': [f[:] for f in dist],
                       'camino_completo': camino,
                       'camino_hasta': camino[:i],
                       'msg': f'Ruta: {" → ".join(camino[:i])}'}


def camino_floyd(sig, i, j, nodos):
    if sig[i][j] is None:
        return None
    camino = [nodos[i]]
    while i != j:
        i = sig[i][j]
        camino.append(nodos[i])
    return camino


def warshall_pasos(adj, nodos):
    n = len(adj)
    V = [f[:] for f in adj]

    yield {'tipo': 'inicio', 'k': -1, 'mat': [f[:] for f in V],
           'msg': '▶ Inicio. Matriz inicial de alcanzabilidad.'}

    for k in range(n):
        nuevos = []
        for i in range(n):
            if V[i][k]:
                for j in range(n):
                    if V[k][j] and not V[i][j]:
                        V[i][j] = 1
                        nuevos.append((i, j))
        msg = (f'k={nodos[k]}: {len(nuevos)} nuevas conexiones'
               if nuevos else f'k={nodos[k]}: sin cambios')
        yield {'tipo': 'k', 'k': k, 'mat': [f[:] for f in V],
               'nuevos': nuevos, 'msg': msg}

    yield {'tipo': 'fin', 'k': n, 'mat': [f[:] for f in V],
           'msg': '✓ Algoritmo de Warshall completado'}


class UnionFind:
    def __init__(self, elems):
        self.p = {e: e for e in elems}
        self.r = {e: 0 for e in elems}

    def find(self, u):
        if self.p[u] != u:
            self.p[u] = self.find(self.p[u])
        return self.p[u]

    def union(self, u, v):
        ru, rv = self.find(u), self.find(v)
        if ru == rv:
            return False
        if self.r[ru] > self.r[rv]:
            self.p[rv] = ru
        elif self.r[ru] < self.r[rv]:
            self.p[ru] = rv
        else:
            self.p[rv] = ru
            self.r[ru] += 1
        return True


def kruskal_pasos(grafo):
    aristas = []
    vistos = set()
    for u in grafo:
        for v, w in grafo[u]:
            key = tuple(sorted((u, v))) + (w,)
            if key not in vistos:
                vistos.add(key)
                aristas.append((w, u, v))
    aristas.sort()

    uf = UnionFind(grafo.keys())
    mst = []

    lista_ord = ", ".join(f"{u}-{v}({w:g})" for w, u, v in aristas)
    yield {'tipo': 'inicio', 'mst': [], 'actual': None,
           'msg': f'▶ Aristas ordenadas: {lista_ord}'}

    for w, u, v in aristas:
        if uf.union(u, v):
            mst.append((u, v, w))
            total = sum(x[2] for x in mst)
            yield {'tipo': 'aceptar', 'mst': list(mst),
                   'actual': (u, v, w),
                   'msg': f'✓ Aceptar {u}—{v} (peso {w:g}). Total={total:g}'}
        else:
            yield {'tipo': 'rechazar', 'mst': list(mst),
                   'actual': (u, v, w),
                   'msg': f'✗ Rechazar {u}—{v} (peso {w:g}): formaría ciclo'}

    total = sum(x[2] for x in mst)
    yield {'tipo': 'fin', 'mst': list(mst), 'actual': None,
           'msg': f'✓ MST completado. Peso total = {total:g}'}


# ================================================================
#                    CANVAS DE VISUALIZACIÓN
# ================================================================

class GrafoCanvas(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg='#FAFAFA', highlightthickness=1,
                         highlightbackground='#DDDDDD', **kw)
        self.radio_nodo = 24
        self._datos = None
        self.bind('<Configure>', lambda e: self._redibujar())

    def mostrar(self, nodos, aristas, dirigido=False,
                aristas_resaltadas=None, color_resalte='#E63946',
                colores_nodos=None, titulo='', nota='',
                etiquetas_extra=None, arista_actual=None):
        self._datos = dict(
            nodos=nodos, aristas=aristas, dirigido=dirigido,
            aristas_resaltadas=aristas_resaltadas,
            color_resalte=color_resalte, colores_nodos=colores_nodos,
            titulo=titulo, nota=nota,
            etiquetas_extra=etiquetas_extra, arista_actual=arista_actual)
        self._redibujar()

    def _redibujar(self):
        if self._datos is None:
            return
        self._dibujar(**self._datos)

    def _dibujar(self, nodos, aristas, dirigido, aristas_resaltadas,
                 color_resalte, colores_nodos, titulo, nota,
                 etiquetas_extra, arista_actual):
        self.delete('all')
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 50:
            w = 600
        if h < 50:
            h = 500

        if titulo:
            self.create_text(w // 2, 20, text=titulo,
                             font=('Arial', 12, 'bold'), fill='#222')
        if nota:
            self.create_text(w // 2, h - 18, text=nota,
                             font=('Arial', 10, 'italic'),
                             fill='#333', width=w - 30)

        if not nodos:
            self.create_text(w // 2, h // 2,
                             text='Ejecuta el algoritmo\npara ver el grafo',
                             font=('Arial', 13), fill='#888',
                             justify='center')
            return

        cx = w // 2
        cy = h // 2
        radio = min(w, h) * 0.30
        pos = {}
        n = len(nodos)
        for i, nodo in enumerate(nodos):
            ang = 2 * math.pi * i / n - math.pi / 2
            pos[nodo] = (cx + radio * math.cos(ang),
                         cy + radio * math.sin(ang) + 5)

        colores_nodos = colores_nodos or {}
        etiquetas_extra = etiquetas_extra or {}

        resaltadas_set = set()
        if aristas_resaltadas:
            for (a, b) in aristas_resaltadas:
                resaltadas_set.add((a, b))
                resaltadas_set.add((b, a))

        for (u, v, peso) in aristas:
            x1, y1 = pos[u]
            x2, y2 = pos[v]

            es_actual = False
            if arista_actual:
                if dirigido:
                    es_actual = (u, v) == arista_actual
                else:
                    es_actual = ((u, v) == arista_actual or
                                 (v, u) == arista_actual)

            if es_actual:
                color = '#FF8C00'
                grosor = 5
            elif (u, v) in resaltadas_set:
                color = color_resalte
                grosor = 4
            else:
                color = '#AAAAAA'
                grosor = 1.6

            self._dibujar_arista(x1, y1, x2, y2, color, grosor, dirigido)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self._dibujar_peso(mx, my, peso)

        for nodo in nodos:
            x, y = pos[nodo]
            color = colores_nodos.get(nodo, '#87CEEB')
            r = self.radio_nodo
            self.create_oval(x - r, y - r, x + r, y + r,
                             fill=color, outline='#222', width=2)
            self.create_text(x, y, text=str(nodo),
                             font=('Arial', 11, 'bold'), fill='#222')
            if nodo in etiquetas_extra:
                self.create_text(x, y + r + 12,
                                 text=etiquetas_extra[nodo],
                                 font=('Arial', 9, 'bold'), fill='#333')

    def _dibujar_arista(self, x1, y1, x2, y2, color, width, dirigido):
        dx = x2 - x1
        dy = y2 - y1
        d = math.hypot(dx, dy)
        if d < 1:
            return
        ux, uy = dx / d, dy / d
        r = self.radio_nodo
        x1s, y1s = x1 + ux * r, y1 + uy * r
        x2s, y2s = x2 - ux * r, y2 - uy * r
        self.create_line(x1s, y1s, x2s, y2s,
                         fill=color, width=width,
                         arrow=tk.LAST if dirigido else tk.NONE,
                         arrowshape=(14, 16, 5))

    def _dibujar_peso(self, x, y, peso):
        tid = self.create_text(x, y, text=str(peso),
                               font=('Arial', 9, 'bold'), fill='#222')
        bbox = self.bbox(tid)
        if bbox:
            rid = self.create_rectangle(
                bbox[0] - 3, bbox[1] - 1, bbox[2] + 3, bbox[3] + 1,
                fill='white', outline='#CCC')
            self.tag_lower(rid, tid)


# ================================================================
#                    CONTROLADOR DE ANIMACIÓN
# ================================================================

class AnimController:
    def __init__(self, app, delay_var):
        self.app = app
        self.gen = None
        self.after_id = None
        self.render_fn = None
        self.delay_var = delay_var
        self.pausado = True

    def cargar(self, gen, render_fn):
        self.detener()
        self.gen = gen
        self.render_fn = render_fn
        self.pausado = True

    def play(self):
        if self.gen is None:
            return
        self.pausado = False
        self._schedule()

    def _schedule(self):
        if self.after_id:
            try:
                self.app.after_cancel(self.after_id)
            except Exception:
                pass
        self.after_id = self.app.after(self.delay_var.get(), self._advance)

    def _advance(self):
        self.after_id = None
        if self.gen is None or self.pausado:
            return
        try:
            paso = next(self.gen)
        except StopIteration:
            self.gen = None
            return
        self.render_fn(paso)
        self._schedule()

    def step(self):
        self.pausado = True
        if self.after_id:
            try:
                self.app.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
        if self.gen is None:
            return False
        try:
            paso = next(self.gen)
        except StopIteration:
            self.gen = None
            return False
        self.render_fn(paso)
        return True

    def detener(self):
        self.pausado = True
        if self.after_id:
            try:
                self.app.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
        self.gen = None


# ================================================================
#                          INTERFAZ
# ================================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos de Grafos · Paso a paso")
        self.geometry("1320x800")

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TNotebook.Tab', font=('Arial', 11, 'bold'),
                        padding=[15, 8])
        style.configure('Bold.TButton', font=('Arial', 10, 'bold'))

        # Header con título y velocidad
        header = ttk.Frame(self)
        header.pack(fill='x', padx=10, pady=(8, 4))
        ttk.Label(header, text="🎬 Algoritmos de Grafos · Paso a paso",
                  font=('Arial', 14, 'bold')).pack(side='left')
        ttk.Label(header, text="Velocidad de animación:",
                  font=('Arial', 10)).pack(side='right', padx=(0, 8))
        self.vel_var = tk.IntVar(value=700)
        tk.Scale(header, from_=200, to=2000, orient='horizontal',
                 variable=self.vel_var, resolution=100, length=200,
                 showvalue=True).pack(side='right')

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=10, pady=(4, 10))

        self._tab_dijkstra(nb)
        self._tab_floyd(nb)
        self._tab_warshall(nb)
        self._tab_kruskal(nb)

        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _on_close(self):
        for ctrl in [self.dij_ctrl, self.fl_ctrl,
                     self.wa_ctrl, self.kr_ctrl]:
            ctrl.detener()
        self.destroy()

    # ---------- Helpers comunes ----------
    def _pestana(self, nb, titulo):
        f = ttk.Frame(nb)
        nb.add(f, text=f"   {titulo}   ")
        return f

    def _panel_izq(self, parent):
        p = ttk.Frame(parent, width=360)
        p.pack(side='left', fill='y', padx=6, pady=6)
        p.pack_propagate(False)
        return p

    def _set_texto(self, widget, texto):
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', texto)
        widget.config(state='disabled')

    def _fila_botones(self, parent, on_ejecutar, on_paso, on_reiniciar):
        f = ttk.Frame(parent)
        f.pack(fill='x', pady=6)
        ttk.Button(f, text="▶ Ejecutar",
                   style='Bold.TButton',
                   command=on_ejecutar).pack(side='left', expand=True,
                                              fill='x', padx=(0, 2))
        ttk.Button(f, text="⏭ Un paso",
                   command=on_paso).pack(side='left', expand=True,
                                          fill='x', padx=2)
        ttk.Button(f, text="⟲ Reiniciar",
                   command=on_reiniciar).pack(side='left', expand=True,
                                               fill='x', padx=(2, 0))

    # =================== DIJKSTRA ===================
    def _tab_dijkstra(self, nb):
        frame = self._pestana(nb, "Dijkstra")
        left = self._panel_izq(frame)
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(left, text="Aristas (Origen Destino Peso):",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        self.dij_in = tk.Text(left, height=8, font=('Courier', 10))
        self.dij_in.pack(fill='x')
        self.dij_in.insert('1.0', "A B 1\nA C 4\nB C 2\nB D 5\nC D 1")

        f = ttk.Frame(left)
        f.pack(fill='x', pady=6)
        ttk.Label(f, text="Inicio:").pack(side='left')
        self.dij_ini = ttk.Entry(f, width=6)
        self.dij_ini.pack(side='left', padx=3)
        self.dij_ini.insert(0, 'A')
        ttk.Label(f, text="Destino:").pack(side='left', padx=(15, 0))
        self.dij_fin = ttk.Entry(f, width=6)
        self.dij_fin.pack(side='left', padx=3)
        self.dij_fin.insert(0, 'D')

        self._fila_botones(left, self._ejecutar_dijkstra,
                          self._paso_dijkstra, self._reiniciar_dijkstra)

        ttk.Label(left, text="Estado del algoritmo:",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(8, 2))
        self.dij_out = tk.Text(left, height=14, font=('Courier', 9),
                               state='disabled', bg='#F8F9FA', wrap='word')
        self.dij_out.pack(fill='both', expand=True)

        self.dij_canvas = GrafoCanvas(right)
        self.dij_canvas.pack(fill='both', expand=True)

        self.dij_ctrl = AnimController(self, self.vel_var)

    def _preparar_dijkstra(self):
        try:
            grafo = {}
            for linea in self.dij_in.get('1.0', 'end').strip().split('\n'):
                if not linea.strip():
                    continue
                p = linea.split()
                if len(p) != 3:
                    raise ValueError(f"Formato inválido: '{linea}'")
                o, d, w = p[0], p[1], float(p[2])
                grafo.setdefault(o, []).append((d, w))
                grafo.setdefault(d, []).append((o, w))

            inicio = self.dij_ini.get().strip()
            destino = self.dij_fin.get().strip() or None
            if inicio not in grafo:
                raise ValueError(f"'{inicio}' no está en el grafo")
            if destino and destino not in grafo:
                raise ValueError(f"'{destino}' no está en el grafo")

            self.dij_grafo = grafo
            nodos = sorted(grafo.keys())
            aristas, vistos = [], set()
            for u in grafo:
                for v, w in grafo[u]:
                    key = tuple(sorted((u, v))) + (w,)
                    if key not in vistos:
                        vistos.add(key)
                        aristas.append((u, v, w))
            self.dij_nodos = nodos
            self.dij_aristas = aristas

            gen = dijkstra_pasos(grafo, inicio, destino)
            self.dij_ctrl.cargar(gen, self._render_dijkstra)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def _ejecutar_dijkstra(self):
        if self._preparar_dijkstra():
            self.dij_ctrl.play()

    def _paso_dijkstra(self):
        if self.dij_ctrl.gen is None:
            if not self._preparar_dijkstra():
                return
        self.dij_ctrl.step()

    def _reiniciar_dijkstra(self):
        self.dij_ctrl.detener()
        self.dij_canvas.mostrar([], [], titulo="Dijkstra",
                               nota="Presiona ▶ Ejecutar o ⏭ Un paso")
        self._set_texto(self.dij_out, "")

    def _render_dijkstra(self, paso):
        dist = paso['dist']
        visitados = paso.get('visitados', set())
        actual = paso.get('actual')
        arista_actual = paso.get('arista')

        colores = {}
        etiquetas = {}
        for n in self.dij_nodos:
            if n in visitados:
                colores[n] = '#06D6A0'
            elif n == actual:
                colores[n] = '#FFD166'
            elif dist[n] < float('inf'):
                colores[n] = '#87CEEB'
            else:
                colores[n] = '#E0E0E0'
            d = dist[n]
            etiquetas[n] = f"d={d:g}" if d < float('inf') else "d=∞"

        resaltadas = []
        if paso['tipo'] in ('fin', 'traza'):
            camino = paso.get('camino_hasta') or paso.get('camino_completo')
            if camino:
                for i in range(len(camino) - 1):
                    resaltadas.append((camino[i], camino[i + 1]))

        self.dij_canvas.mostrar(
            self.dij_nodos, self.dij_aristas, dirigido=False,
            aristas_resaltadas=resaltadas,
            color_resalte='#E63946',
            colores_nodos=colores,
            titulo='Dijkstra · construcción paso a paso',
            nota=paso['msg'],
            etiquetas_extra=etiquetas,
            arista_actual=arista_actual)

        txt = f"[{paso['tipo'].upper()}]\n{paso['msg']}\n\n"
        txt += "Distancias actuales:\n" + "─" * 30 + "\n"
        for n in self.dij_nodos:
            marca = "✓" if n in visitados else "○"
            d = dist[n]
            d_txt = '∞' if d == float('inf') else f'{d:g}'
            txt += f"  {marca} {n}: {d_txt}\n"
        if paso.get('camino_completo'):
            camino = paso['camino_completo']
            costo = dist[camino[-1]]
            txt += f"\n🏁 Ruta final:\n  {' → '.join(camino)}\n"
            txt += f"  Costo total: {costo:g}\n"
        self._set_texto(self.dij_out, txt)

    # =================== FLOYD ===================
    def _tab_floyd(self, nb):
        frame = self._pestana(nb, "Floyd")
        left = self._panel_izq(frame)
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(left, text="Matriz de adyacencia (usa 'inf'):",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        ttk.Label(left, text="Nodos: 0, 1, 2, 3, ...",
                  font=('Arial', 9, 'italic')).pack(anchor='w')
        self.fl_in = tk.Text(left, height=7, font=('Courier', 10))
        self.fl_in.pack(fill='x')
        self.fl_in.insert('1.0',
                          "0 3 4 inf\ninf 0 1 5\ninf inf 0 2\ninf inf inf 0")

        f = ttk.Frame(left)
        f.pack(fill='x', pady=6)
        ttk.Label(f, text="Desde:").pack(side='left')
        self.fl_ini = ttk.Entry(f, width=6)
        self.fl_ini.pack(side='left', padx=3)
        self.fl_ini.insert(0, '0')
        ttk.Label(f, text="Hasta:").pack(side='left', padx=(15, 0))
        self.fl_fin = ttk.Entry(f, width=6)
        self.fl_fin.pack(side='left', padx=3)
        self.fl_fin.insert(0, '3')

        self._fila_botones(left, self._ejecutar_floyd,
                          self._paso_floyd, self._reiniciar_floyd)

        ttk.Label(left, text="Estado del algoritmo:",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(8, 2))
        self.fl_out = tk.Text(left, height=15, font=('Courier', 9),
                              state='disabled', bg='#F8F9FA', wrap='word')
        self.fl_out.pack(fill='both', expand=True)

        self.fl_canvas = GrafoCanvas(right)
        self.fl_canvas.pack(fill='both', expand=True)

        self.fl_ctrl = AnimController(self, self.vel_var)

    def _preparar_floyd(self):
        try:
            lineas = [l for l in self.fl_in.get('1.0', 'end').strip()
                      .split('\n') if l.strip()]
            matriz = []
            for l in lineas:
                fila = []
                for x in l.split():
                    fila.append(float('inf')
                                if x.lower() in ('inf', '∞', 'infinito')
                                else float(x))
                matriz.append(fila)

            n = len(matriz)
            if any(len(f) != n for f in matriz):
                raise ValueError("La matriz debe ser cuadrada")

            nodos = [str(i) for i in range(n)]
            self.fl_nodos = nodos
            aristas = []
            for i in range(n):
                for j in range(n):
                    if (i != j and matriz[i][j] != float('inf')
                            and matriz[i][j] > 0):
                        aristas.append((nodos[i], nodos[j], matriz[i][j]))
            self.fl_aristas = aristas
            self.fl_matriz = matriz

            ini = self.fl_ini.get().strip()
            fin = self.fl_fin.get().strip()
            ini_idx = nodos.index(ini) if ini in nodos else None
            fin_idx = nodos.index(fin) if fin in nodos else None

            gen = floyd_pasos(matriz, nodos, ini_idx, fin_idx)
            self.fl_ctrl.cargar(gen, self._render_floyd)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def _ejecutar_floyd(self):
        if self._preparar_floyd():
            self.fl_ctrl.play()

    def _paso_floyd(self):
        if self.fl_ctrl.gen is None:
            if not self._preparar_floyd():
                return
        self.fl_ctrl.step()

    def _reiniciar_floyd(self):
        self.fl_ctrl.detener()
        self.fl_canvas.mostrar([], [], dirigido=True,
                               titulo="Floyd",
                               nota="Presiona ▶ Ejecutar o ⏭ Un paso")
        self._set_texto(self.fl_out, "")

    def _render_floyd(self, paso):
        nodos = self.fl_nodos
        k = paso.get('k', -1)
        matriz = paso['dist']

        colores = {}
        for i, n in enumerate(nodos):
            if i < k:
                colores[n] = '#06D6A0'
            elif i == k:
                colores[n] = '#FFD166'
            else:
                colores[n] = '#E0E0E0'

        resaltadas = []
        if paso['tipo'] == 'traza':
            camino = paso.get('camino_hasta', [])
            for i in range(len(camino) - 1):
                resaltadas.append((camino[i], camino[i + 1]))

        self.fl_canvas.mostrar(
            nodos, self.fl_aristas, dirigido=True,
            aristas_resaltadas=resaltadas,
            colores_nodos=colores,
            titulo='Floyd · construcción paso a paso',
            nota=paso['msg'])

        txt = f"[{paso['tipo'].upper()}]\n{paso['msg']}\n\n"
        txt += "Matriz de distancias actuales:\n" + "─" * 44 + "\n     "
        for n in nodos:
            txt += f"{n:>8}"
        txt += "\n"
        for i in range(len(nodos)):
            txt += f" {nodos[i]}  "
            for j in range(len(nodos)):
                v = matriz[i][j]
                s = '∞' if v == float('inf') else f'{v:g}'
                if (paso['tipo'] == 'update'
                        and paso.get('i') == i and paso.get('j') == j):
                    txt += f"*{s:<7}"
                else:
                    txt += f"{s:>8}"
            txt += "\n"
        if paso.get('camino_completo'):
            txt += f"\n🏁 Ruta final:\n  " + \
                   " → ".join(paso['camino_completo']) + "\n"
        self._set_texto(self.fl_out, txt)

    # =================== WARSHALL ===================
    def _tab_warshall(self, nb):
        frame = self._pestana(nb, "Warshall")
        left = self._panel_izq(frame)
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(left, text="Matriz booleana (0 / 1):",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        ttk.Label(left, text="Nodos: 0, 1, 2, 3, ...",
                  font=('Arial', 9, 'italic')).pack(anchor='w')
        self.wa_in = tk.Text(left, height=7, font=('Courier', 10))
        self.wa_in.pack(fill='x')
        self.wa_in.insert('1.0', "0 1 0 0\n0 0 1 0\n1 0 0 1\n0 0 0 0")

        self._fila_botones(left, self._ejecutar_warshall,
                          self._paso_warshall, self._reiniciar_warshall)

        ttk.Label(left, text="Estado del algoritmo:",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(8, 2))
        self.wa_out = tk.Text(left, height=16, font=('Courier', 9),
                              state='disabled', bg='#F8F9FA', wrap='word')
        self.wa_out.pack(fill='both', expand=True)

        self.wa_canvas = GrafoCanvas(right)
        self.wa_canvas.pack(fill='both', expand=True)

        self.wa_ctrl = AnimController(self, self.vel_var)

    def _preparar_warshall(self):
        try:
            lineas = [l for l in self.wa_in.get('1.0', 'end').strip()
                      .split('\n') if l.strip()]
            matriz = [[int(x) for x in l.split()] for l in lineas]
            n = len(matriz)
            if any(len(f) != n for f in matriz):
                raise ValueError("La matriz debe ser cuadrada")

            nodos = [str(i) for i in range(n)]
            self.wa_nodos = nodos
            aristas = []
            for i in range(n):
                for j in range(n):
                    if matriz[i][j]:
                        aristas.append((nodos[i], nodos[j], ''))
            self.wa_aristas = aristas

            gen = warshall_pasos(matriz, nodos)
            self.wa_ctrl.cargar(gen, self._render_warshall)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def _ejecutar_warshall(self):
        if self._preparar_warshall():
            self.wa_ctrl.play()

    def _paso_warshall(self):
        if self.wa_ctrl.gen is None:
            if not self._preparar_warshall():
                return
        self.wa_ctrl.step()

    def _reiniciar_warshall(self):
        self.wa_ctrl.detener()
        self.wa_canvas.mostrar([], [], dirigido=True,
                               titulo="Warshall",
                               nota="Presiona ▶ Ejecutar o ⏭ Un paso")
        self._set_texto(self.wa_out, "")

    def _render_warshall(self, paso):
        nodos = self.wa_nodos
        k = paso.get('k', -1)
        mat = paso['mat']

        colores = {}
        for i, n in enumerate(nodos):
            if i < k:
                colores[n] = '#06D6A0'
            elif i == k:
                colores[n] = '#FFD166'
            else:
                colores[n] = '#E0E0E0'

        self.wa_canvas.mostrar(
            nodos, self.wa_aristas, dirigido=True,
            colores_nodos=colores,
            titulo='Warshall · construcción paso a paso',
            nota=paso['msg'])

        txt = f"[{paso['tipo'].upper()}]\n{paso['msg']}\n\n"
        txt += "Matriz de cierre transitivo:\n" + "─" * 44 + "\n     "
        for n in nodos:
            txt += f"{n:>6}"
        txt += "\n"
        nuevos = paso.get('nuevos', [])
        for i in range(len(nodos)):
            txt += f" {nodos[i]}  "
            for j in range(len(nodos)):
                v = mat[i][j]
                if (i, j) in nuevos:
                    txt += f"*{v:<5}"
                else:
                    txt += f"{v:>6}"
            txt += "\n"
        self._set_texto(self.wa_out, txt)

    # =================== KRUSKAL ===================
    def _tab_kruskal(self, nb):
        frame = self._pestana(nb, "Kruskal")
        left = self._panel_izq(frame)
        right = ttk.Frame(frame)
        right.pack(side='right', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(left, text="Aristas no dirigidas (Origen Destino Peso):",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(4, 2))
        self.kr_in = tk.Text(left, height=8, font=('Courier', 10))
        self.kr_in.pack(fill='x')
        self.kr_in.insert('1.0', "A B 1\nA C 4\nB C 2\nB D 5\nC D 1")

        self._fila_botones(left, self._ejecutar_kruskal,
                          self._paso_kruskal, self._reiniciar_kruskal)

        ttk.Label(left, text="Estado del algoritmo:",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(8, 2))
        self.kr_out = tk.Text(left, height=16, font=('Courier', 9),
                              state='disabled', bg='#F8F9FA', wrap='word')
        self.kr_out.pack(fill='both', expand=True)

        self.kr_canvas = GrafoCanvas(right)
        self.kr_canvas.pack(fill='both', expand=True)

        self.kr_ctrl = AnimController(self, self.vel_var)

    def _preparar_kruskal(self):
        try:
            grafo = {}
            for linea in self.kr_in.get('1.0', 'end').strip().split('\n'):
                if not linea.strip():
                    continue
                p = linea.split()
                if len(p) != 3:
                    raise ValueError(f"Formato inválido: '{linea}'")
                o, d, w = p[0], p[1], float(p[2])
                grafo.setdefault(o, []).append((d, w))
                grafo.setdefault(d, []).append((o, w))

            self.kr_grafo = grafo
            nodos = sorted(grafo.keys())
            aristas, vistos = [], set()
            for u in grafo:
                for v, w in grafo[u]:
                    key = tuple(sorted((u, v))) + (w,)
                    if key not in vistos:
                        vistos.add(key)
                        aristas.append((u, v, w))
            self.kr_nodos = nodos
            self.kr_aristas = aristas

            gen = kruskal_pasos(grafo)
            self.kr_ctrl.cargar(gen, self._render_kruskal)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def _ejecutar_kruskal(self):
        if self._preparar_kruskal():
            self.kr_ctrl.play()

    def _paso_kruskal(self):
        if self.kr_ctrl.gen is None:
            if not self._preparar_kruskal():
                return
        self.kr_ctrl.step()

    def _reiniciar_kruskal(self):
        self.kr_ctrl.detener()
        self.kr_canvas.mostrar([], [], dirigido=False,
                               titulo="Kruskal",
                               nota="Presiona ▶ Ejecutar o ⏭ Un paso")
        self._set_texto(self.kr_out, "")

    def _render_kruskal(self, paso):
        nodos = self.kr_nodos
        mst = paso.get('mst', [])
        actual = paso.get('actual')
        tipo = paso['tipo']

        resaltadas = [(u, v) for u, v, _ in mst]
        arista_actual = None
        color_resalte = '#06D6A0'

        if actual:
            u, v, w = actual
            arista_actual = (u, v)
            if tipo == 'rechazar':
                color_resalte = '#E63946'
            elif tipo == 'aceptar':
                color_resalte = '#2A9D8F'

        nodos_en_mst = set()
        for u, v, _ in mst:
            nodos_en_mst.add(u)
            nodos_en_mst.add(v)
        colores = {n: ('#06D6A0' if n in nodos_en_mst else '#E0E0E0')
                   for n in nodos}

        self.kr_canvas.mostrar(
            nodos, self.kr_aristas, dirigido=False,
            aristas_resaltadas=resaltadas,
            color_resalte=color_resalte,
            colores_nodos=colores,
            titulo='Kruskal · construcción paso a paso',
            nota=paso['msg'],
            arista_actual=arista_actual)

        total = sum(w for _, _, w in mst)
        txt = f"[{tipo.upper()}]\n{paso['msg']}\n\n"
        txt += "Árbol actual (MST):\n" + "─" * 32 + "\n"
        if mst:
            for u, v, w in mst:
                txt += f"  ✓ {u} — {v}   :   {w:g}\n"
        else:
            txt += "  (vacío)\n"
        txt += "─" * 32 + f"\n  Peso total: {total:g}\n"
        txt += f"  Aristas: {len(mst)}\n"
        self._set_texto(self.kr_out, txt)


# ================================================================
#                        EJECUCIÓN
# ================================================================

if __name__ == "__main__":
    App().mainloop()