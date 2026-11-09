import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import math


class Nodo:
    _contador_id = 0
    def __init__(self, valor):
        Nodo._contador_id += 1
        self.id = Nodo._contador_id
        self.valor = valor
        self.izq = None
        self.der = None
        self.padre = None
        self.x = 0
        self.y = 0
        self.tx = 0
        self.ty = 0
        self.prof = 0
        self.indice = 0

class Arbol:
    def __init__(self):
        self.raiz = None

    def insertar(self, valor, id_padre=None, lado='izq'):
        nuevo = Nodo(valor)
        if self.raiz is None:
            self.raiz = nuevo
            return nuevo

        padre = self.buscar_por_id(id_padre) if id_padre else self.raiz
        if not padre:
            return None

        if lado == 'izq':
            if padre.izq: return "ocupado"
            padre.izq = nuevo
            nuevo.padre = padre
        else:
            if padre.der: return "ocupado"
            padre.der = nuevo
            nuevo.padre = padre
        return nuevo

    def eliminar(self, id_nodo):
        nodo = self.buscar_por_id(id_nodo)
        if not nodo: return False
        
        if nodo.padre:
            if nodo.padre.izq == nodo: nodo.padre.izq = None
            else: nodo.padre.der = None
        else:
            self.raiz = None
        return True

    def vaciar(self):
        self.raiz = None

    def buscar_por_id(self, id_nodo, nodo_actual=None):
        if nodo_actual is None: nodo_actual = self.raiz
        if nodo_actual is None: return None
        if nodo_actual.id == id_nodo: return nodo_actual
        
        izq = self.buscar_por_id(id_nodo, nodo_actual.izq)
        if izq: return izq
        return self.buscar_por_id(id_nodo, nodo_actual.der)

    def obtener_nodos(self):
        lista = []
        def rec(n, d, p):
            if n is None: return
            n.padre = p
            rec(n.izq, d + 1, n)
            n.indice = len(lista)
            n.prof = d
            lista.append(n)
            rec(n.der, d + 1, n)
        rec(self.raiz, 0, None)
        return lista

    def obtener_recorrido(self, tipo):
        resultado = []
        def preorden(n):
            if n: resultado.append(n); preorden(n.izq); preorden(n.der)
        def inorden(n):
            if n: inorden(n.izq); resultado.append(n); inorden(n.der)
        def postorden(n):
            if n: postorden(n.izq); postorden(n.der); resultado.append(n)
        def niveles(n):
            if not n: return
            cola = deque([n])
            while cola:
                actual = cola.popleft()
                resultado.append(actual)
                if actual.izq: cola.append(actual.izq)
                if actual.der: cola.append(actual.der)

        if tipo == 'pre': preorden(self.raiz)
        elif tipo == 'in': inorden(self.raiz)
        elif tipo == 'post': postorden(self.raiz)
        elif tipo == 'niv': niveles(self.raiz)
        return resultado

    def obtener_altura(self):
        nodos = self.obtener_nodos()
        return max([n.prof for n in nodos]) + 1 if nodos else 0

    def contar_nodos(self):
        return len(self.obtener_nodos())

class App:
    RADIO = 22
    SPX = 70
    SPY = 90
    BASE_Y = 80

    def __init__(self, root):
        self.root = root
        root.title("Práctica: Clase Árbol y Nodo")
        root.geometry("1200x720")
        root.configure(bg="#0b0e1a")

        self.arbol = Arbol() # Instanciamos nuestra clase Arbol
        self.seleccionado = None
        self.velocidad = 5
        self.token = 0
        self.animando = False
        self.nodos_vis = {}
        self.aristas_vis = {}
        self._press_xy = None
        self._last_xy = None

        self._construir_ui()
        self._arbol_ejemplo()

    def _construir_ui(self):
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0b0e1a", sashwidth=6, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=10, pady=10)

        panel_container = tk.Frame(self.paned, bg="#141830", width=360)
        self.paned.add(panel_container, minsize=300, stretch="never")

        self.panel_canvas = tk.Canvas(panel_container, bg="#141830", highlightthickness=0, width=340)
        self.panel_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(panel_container, orient="vertical", command=self.panel_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.panel_canvas.configure(yscrollcommand=scrollbar.set)

        panel = tk.Frame(self.panel_canvas, bg="#141830")
        self.panel_canvas.create_window((0, 0), window=panel, anchor="nw", width=340)

        panel.bind("<Configure>", lambda e: self.panel_canvas.configure(scrollregion=self.panel_canvas.bbox("all")))

        tk.Label(panel, text="   Árbol Binario POO", bg="#141830", fg="#e6e9f5",
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x", pady=(12, 5))
                 
        self.lbl_ayuda = tk.Label(panel, text="1. Haz clic en un nodo en el dibujo.\n2. Escribe el valor y elige el lado.\n3. Pulsa Insertar o Editar.", 
                                  bg="#141830", fg="#ffd166", font=("Segoe UI", 10), justify="left")
        self.lbl_ayuda.pack(fill="x", padx=15, pady=(0, 15))

        self._seccion(panel, "CREAR / EDITAR NODO")
        tk.Label(panel, text="Valor:", bg="#141830", fg="#8a91b8").pack(anchor="w", padx=15)
        self.entry_valor = tk.Entry(panel, bg="#0f1329", fg="#e6e9f5",
                                    insertbackground="#e6e9f5", relief="flat",
                                    font=("Segoe UI", 11))
        self.entry_valor.pack(fill="x", padx=15, pady=(2, 10), ipady=4)
        self.entry_valor.bind("<Return>", lambda e: self._insertar())

        tk.Label(panel, text="Como (para insertar):", bg="#141830", fg="#8a91b8").pack(anchor="w", padx=15)
        self.combo_lado = ttk.Combobox(panel, values=["Hijo izquierdo", "Hijo derecho"], state="readonly")
        self.combo_lado.current(0)
        self.combo_lado.pack(fill="x", padx=15, pady=(2, 10))

        fila_acciones = tk.Frame(panel, bg="#141830")
        fila_acciones.pack(fill="x", padx=15, pady=(0, 18))
        
        self._boton(fila_acciones, "Insertar", self._insertar, primario=True).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._boton(fila_acciones, "Editar", self._editar).pack(side="left", expand=True, fill="x", padx=(3, 0))

        self._seccion(panel, "ESTRUCTURA DEL ÁRBOL")
        fila = tk.Frame(panel, bg="#141830")
        fila.pack(fill="x", padx=15, pady=(0, 6))
        self._boton(fila, "Eliminar", self._eliminar).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._boton(fila, "Vaciar",   self._vaciar  ).pack(side="left", expand=True, fill="x", padx=(3, 3))
        self._boton(fila, "Centrar",  self._centrar ).pack(side="left", expand=True, fill="x", padx=(3, 0))
        tk.Frame(panel, bg="#141830", height=14).pack()

        self._seccion(panel, "RECORRIDOS (MÉTODOS)")
        for nombre, tipo in [("Preorden", "pre"), ("Inorden", "in"), ("Postorden", "post"), ("Por niveles", "niv")]:
            self._boton(panel, nombre, lambda t=tipo: self._recorrer(t)).pack(fill="x", padx=15, pady=2)

        self._seccion(panel, "INFORMACIÓN")
        self.lbl_info = tk.Label(panel, text="Nodos: 0\nAltura: 0\nSeleccionado: —", bg="#0f1329", fg="#5b8cff",
                                 font=("Segoe UI", 11), justify="left", anchor="w", padx=10, pady=8,
                                 highlightbackground="#2a3160", highlightthickness=1)
        self.lbl_info.pack(fill="x", padx=15, pady=(0, 12))

        self.lbl_salida = tk.Label(panel, text="Resultado: —", bg="#0f1329", fg="#3ddc97",
                                   font=("Consolas", 10), wraplength=300, justify="left", anchor="w", padx=10, pady=8)
        self.lbl_salida.pack(fill="x", padx=15, pady=(0, 15))

        canvas_container = tk.Frame(self.paned, bg="#0d101e")
        self.paned.add(canvas_container, minsize=300, stretch="always")

        self.canvas = tk.Canvas(canvas_container, bg="#0d101e", highlightthickness=0, xscrollincrement=1, yscrollincrement=1)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._render())
        self.canvas.bind("<ButtonPress-1>", self._canvas_press)
        self.canvas.bind("<B1-Motion>", self._canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._canvas_release)
        self.canvas.bind("<MouseWheel>", self._canvas_wheel)
        self.canvas.bind("<Button-4>", self._canvas_wheel)
        self.canvas.bind("<Button-5>", self._canvas_wheel)

    def _seccion(self, parent, texto):
        tk.Label(parent, text=texto, bg="#141830", fg="#8a91b8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(5, 4))

    def _boton(self, parent, texto, cmd, primario=False):
        bg = "#3a6bff" if primario else "#232a52"
        return tk.Button(parent, text=texto, command=cmd, bg=bg, fg="#e6e9f5", activebackground="#4b7bff",
                         activeforeground="white", relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2", pady=6)

    def _canvas_press(self, e):
        self.root.focus_set()
        self._press_xy = (e.x, e.y)
        self._last_xy  = (e.x, e.y)

    def _canvas_drag(self, e):
        if self._press_xy is None: return
        lx, ly = self._last_xy
        dx, dy = e.x - lx, e.y - ly
        if abs(e.x - self._press_xy[0]) > 3 or abs(e.y - self._press_xy[1]) > 3:
            self.canvas.xview_scroll(-dx, "units")
            self.canvas.yview_scroll(-dy, "units")
            self._last_xy = (e.x, e.y)

    def _canvas_release(self, e):
        self._press_xy = None

    def _on_nodo_click(self, nid):
        self.seleccionado = nid
        self._aplicar_colores()
        self._actualizar_info()
        return "break"

    def _canvas_wheel(self, e):
        if hasattr(e, "num"): d = -1 if e.num == 4 else 1
        elif getattr(e, "delta", 0) != 0: d = -1 if e.delta > 0 else 1
        else: return
        if bool(e.state & 0x1): self.canvas.xview_scroll(d * 30, "units")
        else: self.canvas.yview_scroll(d * 30, "units")

    def _centrar(self):
        sr = str(self.canvas.cget("scrollregion"))
        if not sr: return
        try: sx, sy, ex, ey = map(float, sr.split())
        except ValueError: return
        w = ex - sx; cw = self.canvas.winfo_width()
        if w > cw and w > 0: self.canvas.xview_moveto(max(0, (w - cw) / 2) / w)
        else: self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _render(self):
        lista = self.arbol.obtener_nodos()
        n = len(lista)
        w = self.canvas.winfo_width()
        if w <= 1: w = 800
        offx = max((w - (n - 1) * self.SPX) / 2, 100)

        vivos = set()
        for nodo in lista:
            vivos.add(nodo.id)
            tx = offx + nodo.indice * self.SPX
            ty = self.BASE_Y + nodo.prof * self.SPY

            if nodo.id not in self.nodos_vis:
                nodo.x, nodo.y = tx, ty
                if nodo.padre and nodo.padre.id in self.nodos_vis:
                    nodo.x, nodo.y = self.nodos_vis[nodo.padre.id]["x"], self.nodos_vis[nodo.padre.id]["y"]
                r = self.RADIO
                oval = self.canvas.create_oval(nodo.x-r, nodo.y-r, nodo.x+r, nodo.y+r, fill="#232a52", outline="#5b8cff", width=2)
                text = self.canvas.create_text(nodo.x, nodo.y, text=str(nodo.valor), fill="#e6e9f5", font=("Segoe UI", 12, "bold"))
                
                self.canvas.tag_bind(oval, "<Button-1>", lambda e, nid=nodo.id: self._on_nodo_click(nid))
                self.canvas.tag_bind(text, "<Button-1>", lambda e, nid=nodo.id: self._on_nodo_click(nid))
                self.canvas.tag_bind(oval, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(text, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(oval, "<Leave>", lambda e: self.canvas.config(cursor=""))
                self.canvas.tag_bind(text, "<Leave>", lambda e: self.canvas.config(cursor=""))

                self.nodos_vis[nodo.id] = {"oval": oval, "text": text, "x": nodo.x, "y": nodo.y, "tx": tx, "ty": ty, "nodo": nodo}
            else:
                v = self.nodos_vis[nodo.id]
                v["tx"], v["ty"] = tx, ty
                v["nodo"] = nodo
                self.canvas.itemconfig(v["text"], text=str(nodo.valor))

        for nid in list(self.nodos_vis):
            if nid not in vivos:
                v = self.nodos_vis.pop(nid)
                self.canvas.delete(v["oval"]); self.canvas.delete(v["text"])
                if nid in self.aristas_vis: self.canvas.delete(self.aristas_vis.pop(nid))

        if n > 0:
            xs = [v["tx"] for v in self.nodos_vis.values()]; ys = [v["ty"] for v in self.nodos_vis.values()]
            min_x, max_x = min(xs) - 100, max(xs) + 100; min_y, max_y = min(ys) - 100, max(ys) + 100
        else: min_x, max_x, min_y, max_y = 0, 800, 0, 600
        cw = self.canvas.winfo_width() or 800; ch = self.canvas.winfo_height() or 600
        if max_x - min_x < cw: cx = (min_x + max_x)/2; min_x, max_x = cx - cw/2, cx + cw/2
        if max_y - min_y < ch: cy = (min_y + max_y)/2; min_y, max_y = cy - ch/2, cy + ch/2
        self.canvas.config(scrollregion=(min_x, min_y, max_x, max_y))

        self._aplicar_colores()
        self._actualizar_info()
        self._animar()

    def _aplicar_colores(self):
        for nid, v in self.nodos_vis.items():
            fill, outline, width = "#232a52", "#5b8cff", 2
            if nid == self.seleccionado: fill, outline, width = "#314685", "#ffd166", 4
            self.canvas.itemconfig(v["oval"], outline=outline, width=width, fill=fill)
            self.canvas.itemconfig(v["text"], fill="#e6e9f5")

    def _estilo(self, v, fill, outline, tcolor, width=2):
        self.canvas.itemconfig(v["oval"], fill=fill, outline=outline, width=width)
        self.canvas.itemconfig(v["text"], fill=tcolor)

    def _actualizar_info(self):
        n = self.arbol.contar_nodos(); h = self.arbol.obtener_altura()
        sel = "—"
        if self.seleccionado in self.nodos_vis: sel = self.nodos_vis[self.seleccionado]["nodo"].valor
        self.lbl_info.config(text=f"Nodos: {n}\nAltura: {h}\nSeleccionado: {sel}")

    def _animar(self):
        if self.animando: return
        self.animando = True; self._paso_anim()

    def _paso_anim(self):
        activo = False
        for v in self.nodos_vis.values():
            dx, dy = v["tx"] - v["x"], v["ty"] - v["y"]
            if abs(dx) > 0.5 or abs(dy) > 0.5:
                v["x"] += dx * 0.25; v["y"] += dy * 0.25; activo = True
            else: v["x"], v["y"] = v["tx"], v["ty"]
            r = self.RADIO
            self.canvas.coords(v["oval"], v["x"]-r, v["y"]-r, v["x"]+r, v["y"]+r)
            self.canvas.coords(v["text"], v["x"], v["y"])

        for nid, v in self.nodos_vis.items():
            nodo = v["nodo"]
            if nodo.padre and nodo.padre.id in self.nodos_vis:
                pv = self.nodos_vis[nodo.padre.id]
                dx, dy = v["x"] - pv["x"], v["y"] - pv["y"]
                d = math.hypot(dx, dy) or 1; r = self.RADIO + 1
                x1, y1 = pv["x"] + dx/d*r, pv["y"] + dy/d*r; x2, y2 = v["x"] - dx/d*r, v["y"] - dy/d*r
                if nid not in self.aristas_vis:
                    line = self.canvas.create_line(x1, y1, x2, y2, fill="#3a4480", width=2)
                    self.canvas.tag_lower(line); self.aristas_vis[nid] = line
                else: self.canvas.coords(self.aristas_vis[nid], x1, y1, x2, y2)
            elif nid in self.aristas_vis: self.canvas.delete(self.aristas_vis.pop(nid))

        if activo: self.canvas.after(16, self._paso_anim)
        else: self.animando = False

    def _insertar(self):
        val = self.entry_valor.get().strip()
        if not val: return messagebox.showwarning("Aviso", "Escribe un valor.")
        lado = 'izq' if self.combo_lado.current() == 0 else 'der'

        if self.arbol.raiz is None:
            self.seleccionado = self.arbol.insertar(val).id
        else:
            if self.seleccionado is None: self.seleccionado = self.arbol.raiz.id
            res = self.arbol.insertar(val, self.seleccionado, lado)
            if res == "ocupado":
                nodo_padre = self.arbol.buscar_por_id(self.seleccionado)
                return messagebox.showwarning("Aviso", f"El nodo '{nodo_padre.valor}' ya tiene un hijo en esa posición.")
            elif res: self.seleccionado = res.id

        self.entry_valor.delete(0, tk.END)
        self.entry_valor.focus()
        self._render()

    def _editar(self):
        if self.seleccionado is None: return messagebox.showwarning("Aviso", "Selecciona un nodo.")
        val = self.entry_valor.get().strip()
        if not val: return messagebox.showwarning("Aviso", "Escribe el nuevo valor.")
        nodo = self.arbol.buscar_por_id(self.seleccionado)
        if nodo:
            nodo.valor = val
            self.entry_valor.delete(0, tk.END)
            self._render()

    def _eliminar(self):
        if self.seleccionado is None: return messagebox.showwarning("Aviso", "Selecciona un nodo.")
        nodo = self.arbol.buscar_por_id(self.seleccionado)
        if nodo.izq or nodo.der:
            if not messagebox.askyesno("Confirmar", f'"{nodo.valor}" tiene descendientes.\nSe eliminará todo su subárbol. ¿Continuar?'): return
        self.arbol.eliminar(self.seleccionado)
        self.seleccionado = None
        self.token += 1
        self._render()

    def _vaciar(self):
        if not self.arbol.raiz: return
        if messagebox.askyesno("Confirmar", "¿Vaciar todo el árbol?"):
            self.arbol.vaciar()
            self.seleccionado = None
            self.token += 1
            self._render()

    def _recorrer(self, tipo):
        self.token += 1; tok = self.token
        for v in self.nodos_vis.values(): self._estilo(v, "#232a52", "#5b8cff", "#e6e9f5", 2)

        orden = self.arbol.obtener_recorrido(tipo)
        nombres = {"pre": "Preorden", "in": "Inorden", "post": "Postorden", "niv": "Por niveles"}
        if not orden:
            self.lbl_salida.config(text=f"{nombres[tipo]}: (árbol vacío)")
            return

        self.lbl_salida.config(text=f"{nombres[tipo]}: ")
        delay = int(1200 / self.velocidad)
        valores = []

        def paso(i):
            if tok != self.token or i >= len(orden): return
            if i > 0 and orden[i-1].id in self.nodos_vis:
                self._estilo(self.nodos_vis[orden[i-1].id], "#3ddc97", "#9bffd6", "#052a1c", 2)
            n = orden[i]
            if n.id in self.nodos_vis: self._estilo(self.nodos_vis[n.id], "#ffd166", "#fff6d0", "#2a1f00", 3)
            valores.append(n.valor)
            self.lbl_salida.config(text=f"{nombres[tipo]}: " + " → ".join(valores))
            self.root.after(delay, lambda: paso(i + 1))
        paso(0)

    def _arbol_ejemplo(self):
        a = self.arbol.insertar("A")
        self.arbol.insertar("B", a.id, 'izq')
        self.arbol.insertar("C", a.id, 'der')
        self._render()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()