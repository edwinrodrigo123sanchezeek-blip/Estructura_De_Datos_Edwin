import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB = "finanzas_agricola.db"
VERDE = "#1f6b52"
VERDE_MED = "#8fbf9f"
VERDE_CLARO = "#cfe5d6"
FONDO = "#f6f8f5"
ROJO = "#e05a5a"
ROSA = "#f8d0d0"
MENTA = "#d4f0dc"
CULTIVOS = ["Maíz", "Elote", "Frijol", "Tomate", "Chile", "Calabaza"]
UNIDADES = ["kg", "ton", "costal", "pieza", "litro"]
CONCEPTOS = ["Fertilizante", "Semillas", "Pesticida", "Mano de obra",
             "Riego", "Combustible", "Renta de maquinaria"]

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS movimientos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,          -- AAAA-MM-DD
            tipo TEXT NOT NULL,           -- Ingreso / Gasto
            concepto TEXT NOT NULL,
            cultivo TEXT,
            cantidad REAL, unidad TEXT, precio REAL,
            total REAL NOT NULL,
            descripcion TEXT)""")


def money(x):
    return f"${x:,.0f}" if float(x).is_integer() else f"${x:,.2f}"


def num(s):
    return float(str(s).replace("$", "").replace(",", "").strip())


def fecha_a_iso(s):
    return datetime.strptime(s.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


def iso_a_fecha(s):
    return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control Financiero Agrícola")
        self.geometry("980x600")
        self.minsize(900, 560)
        self.configure(bg=FONDO)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background="#e6eee8")
        style.configure("TCombobox", padding=4)

        self.side = tk.Frame(self, bg=VERDE_CLARO, width=200)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)
        self.content = tk.Frame(self, bg=FONDO)
        self.content.pack(side="right", fill="both", expand=True)

        self.nav = {}
        items = [("inicio", "🏠  Inicio"), ("ingreso", "➕  Registrar ingreso"),
                 ("gasto", "➖  Registrar gasto"), ("mov", "☰  Movimientos"),
                 ("balance", "📊  Balance")]
        tk.Label(self.side, text="🌱 Agro Control", bg=VERDE_CLARO, fg=VERDE,
                 font=("Segoe UI", 13, "bold")).pack(pady=(18, 14))
        for key, txt in items:
            b = tk.Label(self.side, text=txt, anchor="w", padx=16, pady=9,
                         bg=VERDE_CLARO, fg="#1d3b2f", cursor="hand2",
                         font=("Segoe UI", 10))
            b.pack(fill="x", padx=8, pady=2)
            b.bind("<Button-1>", lambda e, k=key: self.ir(k))
            self.nav[key] = b
        self.ir("inicio")

    def limpiar(self):
        for w in self.content.winfo_children():
            w.destroy()

    def ir(self, pantalla, **kw):
        self.limpiar()
        activo = {"detalle": "mov"}.get(pantalla, pantalla)
        for k, b in self.nav.items():
            b.config(bg=VERDE if k == activo else VERDE_CLARO,
                     fg="white" if k == activo else "#1d3b2f")
        getattr(self, "p_" + pantalla)(**kw)

    def titulo(self, texto, icono=""):
        tk.Label(self.content, text=f"{icono} {texto}", bg=FONDO, fg="#173d31",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=28, pady=(22, 10))

    def boton(self, parent, texto, cmd, color=VERDE, fg="white", **pk):
        b = tk.Button(parent, text=texto, command=cmd, bg=color, fg=fg, bd=0,
                      activebackground=color, padx=16, pady=7,
                      font=("Segoe UI", 10, "bold"), cursor="hand2")
        b.pack(**pk)
        return b

    def p_inicio(self):
        tk.Label(self.content, text="Control Financiero\nAgrícola", bg=FONDO,
                 fg="#173d31", justify="left",
                 font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=30, pady=(28, 0))
        tk.Label(self.content, text="Tu cosecha también se planea 🌿", bg=FONDO,
                 fg=VERDE, font=("Segoe UI", 12)).pack(anchor="w", padx=30, pady=(0, 18))
        grid = tk.Frame(self.content, bg=FONDO)
        grid.pack(padx=26, anchor="w")
        tarjetas = [
            ("➕  Registrar ingreso", "Agrega una nueva venta\nde tus productos.", MENTA, "ingreso"),
            ("➖  Registrar gasto", "Registra los gastos de tu\nproducción agrícola.", ROSA, "gasto"),
            ("☰  Ver movimientos", "Consulta todos tus ingresos\ny gastos registrados.", "#d3e6f5", "mov"),
            ("📊  Ver balance", "Revisa tu ganancia o\npérdida actual.", "#e0d9f3", "balance"),
        ]
        for i, (t, d, col, dest) in enumerate(tarjetas):
            f = tk.Frame(grid, bg=col, padx=18, pady=16, cursor="hand2")
            f.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            l1 = tk.Label(f, text=t, bg=col, font=("Segoe UI", 12, "bold"), anchor="w")
            l2 = tk.Label(f, text=d, bg=col, justify="left", fg="#444", anchor="w")
            l1.pack(anchor="w")
            l2.pack(anchor="w", pady=(4, 0))
            for w in (f, l1, l2):
                w.bind("<Button-1>", lambda e, k=dest: self.ir(k))
            f.config(width=300, height=110)

    def p_ingreso(self, mov=None):
        self.titulo("Editar ingreso" if mov else "Registrar ingreso", "➕")
        f = tk.Frame(self.content, bg=FONDO)
        f.pack(anchor="w", padx=34, pady=6)
        v = {k: tk.StringVar() for k in ("cultivo", "cantidad", "unidad", "precio", "total", "fecha")}
        v["unidad"].set("kg")
        v["fecha"].set(datetime.now().strftime("%d/%m/%Y"))
        if mov:
            v["cultivo"].set(mov["cultivo"] or "")
            v["cantidad"].set(f"{mov['cantidad']:g}")
            v["unidad"].set(mov["unidad"] or "kg")
            v["precio"].set(f"{mov['precio']:g}")
            v["fecha"].set(iso_a_fecha(mov["fecha"]))

        def calc(*_):
            try:
                v["total"].set(money(num(v["cantidad"].get()) * num(v["precio"].get())))
            except ValueError:
                v["total"].set("")
        v["cantidad"].trace_add("write", calc)
        v["precio"].trace_add("write", calc)

        def fila(r, txt, w):
            tk.Label(f, text=txt, bg=FONDO, anchor="w", width=18).grid(row=r, column=0, pady=8, sticky="w")
            w.grid(row=r, column=1, pady=8, sticky="w")
        fila(0, "Producto / Cultivo:", ttk.Combobox(f, textvariable=v["cultivo"], values=CULTIVOS, width=28))
        cant = tk.Frame(f, bg=FONDO)
        ttk.Entry(cant, textvariable=v["cantidad"], width=16).pack(side="left")
        ttk.Combobox(cant, textvariable=v["unidad"], values=UNIDADES, width=8).pack(side="left", padx=8)
        fila(1, "Cantidad:", cant)
        fila(2, "Precio por unidad: $", ttk.Entry(f, textvariable=v["precio"], width=30))
        fila(3, "Total:", ttk.Entry(f, textvariable=v["total"], width=30, state="readonly"))
        fila(4, "Fecha (dd/mm/aaaa):", ttk.Entry(f, textvariable=v["fecha"], width=30))
        calc()

        def guardar():
            try:
                cultivo = v["cultivo"].get().strip()
                if not cultivo:
                    raise ValueError("Escribe el producto o cultivo.")
                cant, precio = num(v["cantidad"].get()), num(v["precio"].get())
                if cant <= 0 or precio <= 0:
                    raise ValueError("Cantidad y precio deben ser mayores a 0.")
                fecha = fecha_a_iso(v["fecha"].get())
            except ValueError as e:
                msg = str(e)
                if "does not match" in msg or "could not convert" in msg:
                    msg = "Revisa los números y la fecha (dd/mm/aaaa)."
                return messagebox.showwarning("Datos incompletos", msg)
            datos = (fecha, "Ingreso", f"Venta de {cultivo.lower()}", cultivo, cant,
                     v["unidad"].get(), precio, cant * precio,
                     mov["descripcion"] if mov else f"Venta de {cultivo.lower()}.")
            with conn() as c:
                if mov:
                    c.execute("""UPDATE movimientos SET fecha=?,tipo=?,concepto=?,cultivo=?,
                        cantidad=?,unidad=?,precio=?,total=?,descripcion=? WHERE id=?""",
                              datos + (mov["id"],))
                else:
                    c.execute("""INSERT INTO movimientos(fecha,tipo,concepto,cultivo,cantidad,
                        unidad,precio,total,descripcion) VALUES(?,?,?,?,?,?,?,?,?)""", datos)
            messagebox.showinfo("Listo", "Ingreso guardado.")
            self.ir("mov")

        bar = tk.Frame(self.content, bg=FONDO)
        bar.pack(anchor="w", padx=34, pady=14)
        self.boton(bar, "💾  Guardar", guardar, side="left")
        self.boton(bar, "✕  Cancelar", lambda: self.ir("mov" if mov else "inicio"),
                   color="white", fg="#333", side="left", padx=10)

    def p_gasto(self, mov=None):
        self.titulo("Editar gasto" if mov else "Registrar gasto", "➖")
        f = tk.Frame(self.content, bg=FONDO)
        f.pack(anchor="w", padx=34, pady=6)
        v = {k: tk.StringVar() for k in ("concepto", "cultivo", "cantidad", "fecha")}
        v["fecha"].set(datetime.now().strftime("%d/%m/%Y"))
        v["cultivo"].set("General")
        if mov:
            v["concepto"].set(mov["concepto"])
            v["cultivo"].set(mov["cultivo"] or "General")
            v["cantidad"].set(f"{mov['total']:g}")
            v["fecha"].set(iso_a_fecha(mov["fecha"]))

        def fila(r, txt, w):
            tk.Label(f, text=txt, bg=FONDO, anchor="w", width=18).grid(row=r, column=0, pady=8, sticky="nw")
            w.grid(row=r, column=1, pady=8, sticky="w")
        fila(0, "Concepto:", ttk.Combobox(f, textvariable=v["concepto"], values=CONCEPTOS, width=28))
        fila(1, "Cultivo (opcional):", ttk.Combobox(f, textvariable=v["cultivo"],
                                                    values=["General"] + CULTIVOS, width=28))
        fila(2, "Cantidad: $", ttk.Entry(f, textvariable=v["cantidad"], width=30))
        fila(3, "Fecha (dd/mm/aaaa):", ttk.Entry(f, textvariable=v["fecha"], width=30))
        desc = tk.Text(f, width=32, height=4, font=("Segoe UI", 10))
        fila(4, "Descripción (opcional):", desc)
        if mov and mov["descripcion"]:
            desc.insert("1.0", mov["descripcion"])

        def guardar():
            try:
                concepto = v["concepto"].get().strip()
                if not concepto:
                    raise ValueError("Escribe el concepto del gasto.")
                monto = num(v["cantidad"].get())
                if monto <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0.")
                fecha = fecha_a_iso(v["fecha"].get())
            except ValueError as e:
                msg = str(e)
                if "does not match" in msg or "could not convert" in msg:
                    msg = "Revisa la cantidad y la fecha (dd/mm/aaaa)."
                return messagebox.showwarning("Datos incompletos", msg)
            datos = (fecha, "Gasto", concepto, v["cultivo"].get().strip() or "General",
                     None, None, None, monto, desc.get("1.0", "end").strip())
            with conn() as c:
                if mov:
                    c.execute("""UPDATE movimientos SET fecha=?,tipo=?,concepto=?,cultivo=?,
                        cantidad=?,unidad=?,precio=?,total=?,descripcion=? WHERE id=?""",
                              datos + (mov["id"],))
                else:
                    c.execute("""INSERT INTO movimientos(fecha,tipo,concepto,cultivo,cantidad,
                        unidad,precio,total,descripcion) VALUES(?,?,?,?,?,?,?,?,?)""", datos)
            messagebox.showinfo("Listo", "Gasto guardado.")
            self.ir("mov")

        bar = tk.Frame(self.content, bg=FONDO)
        bar.pack(anchor="w", padx=34, pady=14)
        self.boton(bar, "💾  Guardar", guardar, side="left")
        self.boton(bar, "✕  Cancelar", lambda: self.ir("mov" if mov else "inicio"),
                   color="white", fg="#333", side="left", padx=10)
    # Aque va la PARTE 2
    # Debe reemplazar los 6 métodos de abajo, respetando sus nombres porfis.
    # Pueden usar: conn(), money(), iso_a_fecha(), self.titulo(), self.boton(),
    # self.ir(), los colores (VERDE, ROJO, ROSA, MENTA...) y self.content.

    def _pendiente(self, texto):
        self.titulo(texto)
        tk.Label(self.content, text="🚧 Pendiente: esta pantalla la hará la Parte 2.",
                 bg=FONDO, fg="#777", font=("Segoe UI", 12)).pack(anchor="w", padx=34)

    def p_mov(self):
        self._pendiente("Movimientos")

    def p_detalle(self, mid):
        self._pendiente("Detalle del movimiento")

    def p_balance(self):
        self._pendiente("Balance")

    def obtener(self, mid):
        with conn() as c:
            return c.execute("SELECT * FROM movimientos WHERE id=?", (mid,)).fetchone()

    def editar(self, mid):
        m = self.obtener(mid)
        self.ir("ingreso" if m["tipo"] == "Ingreso" else "gasto", mov=m)

    def eliminar(self, mid):
        if messagebox.askyesno("Eliminar", "¿Seguro que quieres eliminar este movimiento?"):
            with conn() as c:
                c.execute("DELETE FROM movimientos WHERE id=?", (mid,))
            self.ir("mov")


if __name__ == "__main__":
    init_db()
    App().mainloop()