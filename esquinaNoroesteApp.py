import tkinter as tk
from tkinter import messagebox
import re

class EsquinaNoroesteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Método Esquina Noroeste - Explicado para Principiantes")
        self.root.geometry("1250x800")
        self.root.configure(bg="#f4f4f9")

        self.filas = 3
        self.columnas = 5
        self.costo_entries = []
        self.oferta_entries = []
        self.demanda_entries = []
        self.nombres_filas_entries = []
        self.nombres_cols_entries = []

        self.memoria_nombres_f = ["Fábrica 1", "Fábrica 2", "Fábrica 3", "Fábrica 4", "Fábrica 5", "Fábrica 6", "Fábrica 7", "Fábrica 8"]
        self.memoria_nombres_c = ["Tienda 1", "Tienda 2", "Tienda 3", "Tienda 4", "Tienda 5", "Tienda 6", "Tienda 7", "Tienda 8"]

        self.crear_interfaz()

    def generar_siguiente_nombre(self, lista_memoria, indice):
        if indice < len(lista_memoria) and lista_memoria[indice].strip():
            return lista_memoria[indice]
        
        if len(lista_memoria) > 0:
            ultimo_nombre = lista_memoria[-1]
            match = re.search(r'^(.*?)\s*(\d+)$', ultimo_nombre)
            
            if match:
                prefijo = match.group(1).strip()
                ultimo_num = int(match.group(2))
                nuevo_nombre = f"{prefijo} {ultimo_num + 1}"
                lista_memoria.append(nuevo_nombre)
                return nuevo_nombre
        
        nuevo_nombre = f"Elemento {indice + 1}"
        lista_memoria.append(nuevo_nombre)
        return nuevo_nombre

    def crear_interfaz(self):
        # --- PANEL IZQUIERDO CON SCROLL VERTICAL Y HORIZONTAL ---
        frame_izq_container = tk.Frame(self.root, bg="#f4f4f9", width=380)
        frame_izq_container.pack(side="left", fill="y")
        frame_izq_container.pack_propagate(False)

        # Scrollbars para el panel izquierdo
        scrollbar_izq_y = tk.Scrollbar(frame_izq_container, orient="vertical")
        scrollbar_izq_x = tk.Scrollbar(frame_izq_container, orient="horizontal")

        self.canvas_izq = tk.Canvas(frame_izq_container, bg="#f4f4f9", 
                                    yscrollcommand=scrollbar_izq_y.set, 
                                    xscrollcommand=scrollbar_izq_x.set, 
                                    highlightthickness=0)
        
        scrollbar_izq_y.config(command=self.canvas_izq.yview)
        scrollbar_izq_x.config(command=self.canvas_izq.xview)

        scrollbar_izq_y.pack(side="right", fill="y")
        scrollbar_izq_x.pack(side="bottom", fill="x")
        self.canvas_izq.pack(side="left", fill="both", expand=True)

        # Frame interno
        frame_izq = tk.Frame(self.canvas_izq, bg="#f4f4f9", padx=10, pady=10)
        self.canvas_izq.create_window((0, 0), window=frame_izq, anchor="nw")
        frame_izq.bind("<Configure>", lambda e: self.canvas_izq.configure(scrollregion=self.canvas_izq.bbox("all")))

        # --- ELEMENTOS DEL PANEL IZQUIERDO ---
        tk.Label(frame_izq, text="1. Datos del Problema", font=("Segoe UI", 14, "bold"), bg="#f4f4f9").pack(pady=5)

        frame_dim = tk.Frame(frame_izq, bg="#f4f4f9")
        frame_dim.pack(pady=5)
        
        tk.Label(frame_dim, text="Filas:", bg="#f4f4f9").grid(row=0, column=0)
        self.spin_filas = tk.Spinbox(frame_dim, from_=2, to=100, width=3, command=self.actualizar_tablas)
        self.spin_filas.grid(row=0, column=1, padx=5)
        self.spin_filas.delete(0, "end")
        self.spin_filas.insert(0, "3")

        tk.Label(frame_dim, text="Columnas:", bg="#f4f4f9").grid(row=0, column=2)
        self.spin_columnas = tk.Spinbox(frame_dim, from_=2, to=100, width=3, command=self.actualizar_tablas)
        self.spin_columnas.grid(row=0, column=3, padx=5)
        self.spin_columnas.delete(0, "end")
        self.spin_columnas.insert(0, "5")

        tk.Button(frame_izq, text="Actualizar Tabla", command=self.actualizar_tablas, bg="#007bff", fg="white").pack(pady=5)

        tk.Label(frame_izq, text="Puedes editar los nombres y números:", font=("Segoe UI", 9, "italic"), bg="#f4f4f9", fg="#555").pack()

        self.frame_tabla_entrada = tk.Frame(frame_izq, bg="#f4f4f9")
        self.frame_tabla_entrada.pack(pady=10)

        tk.Button(frame_izq, text="▶ EXPLICAR PASO A PASO", command=self.resolver, bg="#28a745", fg="white", font=("Segoe UI", 11, "bold"), padx=10, pady=5).pack(pady=15)

        # --- PANEL DERECHO CON SCROLL VERTICAL Y HORIZONTAL ---
        frame_der = tk.Frame(self.root, bg="#ffffff", relief="sunken", borderwidth=2)
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        scrollbar_der_y = tk.Scrollbar(frame_der, orient="vertical")
        scrollbar_der_x = tk.Scrollbar(frame_der, orient="horizontal")
        
        self.canvas_resultados = tk.Canvas(frame_der, bg="#ffffff", 
                                           yscrollcommand=scrollbar_der_y.set,
                                           xscrollcommand=scrollbar_der_x.set,
                                           highlightthickness=0)
        
        scrollbar_der_y.config(command=self.canvas_resultados.yview)
        scrollbar_der_x.config(command=self.canvas_resultados.xview)

        scrollbar_der_y.pack(side="right", fill="y")
        scrollbar_der_x.pack(side="bottom", fill="x")
        self.canvas_resultados.pack(side="left", fill="both", expand=True)

        # Scroll con el mouse (detecta si presionas Shift para mover a los lados)
        self.canvas_izq.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas_izq.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas_izq.bind_all("<Button-5>", self._on_mousewheel)

        self.actualizar_tablas()

    def _on_mousewheel(self, event):
        # Identificar en qué panel está el mouse
        x, y = self.root.winfo_pointerxy()
        x_rel = x - self.root.winfo_rootx()
        
        if x_rel < 380:
            canvas = self.canvas_izq
        else:
            canvas = self.canvas_resultados

        # Si presionas Shift, hace scroll horizontal. Si no, vertical.
        if event.state & 0x0001: 
            if event.num == 4:  
                canvas.xview_scroll(-1, "units")
            elif event.num == 5:  
                canvas.xview_scroll(1, "units")
            else:  
                canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:  
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  
                canvas.yview_scroll(1, "units")
            else:  
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def actualizar_tablas(self):
        if self.nombres_filas_entries:
            for i, e in enumerate(self.nombres_filas_entries):
                texto = e.get().strip()
                if texto: self.memoria_nombres_f[i] = texto
        if self.nombres_cols_entries:
            for j, e in enumerate(self.nombres_cols_entries):
                texto = e.get().strip()
                if texto: self.memoria_nombres_c[j] = texto

        try:
            self.filas = int(self.spin_filas.get())
            self.columnas = int(self.spin_columnas.get())
        except ValueError:
            return

        for widget in self.frame_tabla_entrada.winfo_children():
            widget.destroy()

        self.costo_entries = []
        self.oferta_entries = []
        self.demanda_entries = []
        self.nombres_filas_entries = []
        self.nombres_cols_entries = []

        tk.Label(self.frame_tabla_entrada, text="", bg="#f4f4f9", width=8).grid(row=0, column=0)

        for j in range(self.columnas):
            nombre = self.generar_siguiente_nombre(self.memoria_nombres_c, j)
            e_col = tk.Entry(self.frame_tabla_entrada, width=8, justify="center", bg="#e2e8f0", font=("Segoe UI", 9, "bold"))
            e_col.insert(0, nombre)
            e_col.grid(row=0, column=j+1, padx=1, pady=1)
            self.nombres_cols_entries.append(e_col)
            
        tk.Label(self.frame_tabla_entrada, text="Oferta", bg="#d1fae5", font=("Segoe UI", 9, "bold"), width=6).grid(row=0, column=self.columnas+1, padx=1, pady=1)

        for i in range(self.filas):
            nombre = self.generar_siguiente_nombre(self.memoria_nombres_f, i)
            e_row = tk.Entry(self.frame_tabla_entrada, width=8, justify="center", bg="#e2e8f0", font=("Segoe UI", 9, "bold"))
            e_row.insert(0, nombre)
            e_row.grid(row=i+1, column=0, padx=1, pady=1)
            self.nombres_filas_entries.append(e_row)

            fila_costos = []
            for j in range(self.columnas):
                e = tk.Entry(self.frame_tabla_entrada, width=4, justify="center")
                e.grid(row=i+1, column=j+1, padx=1, pady=1)
                fila_costos.append(e)
            self.costo_entries.append(fila_costos)

            e_of = tk.Entry(self.frame_tabla_entrada, width=6, justify="center", bg="#fff3cd")
            e_of.grid(row=i+1, column=self.columnas+1, padx=1, pady=1)
            self.oferta_entries.append(e_of)

        tk.Label(self.frame_tabla_entrada, text="Demanda", bg="#dbeafe", font=("Segoe UI", 9, "bold"), width=8).grid(row=self.filas+1, column=0, padx=1, pady=1)
        for j in range(self.columnas):
            e = tk.Entry(self.frame_tabla_entrada, width=4, justify="center", bg="#fff3cd")
            e.grid(row=self.filas+1, column=j+1, padx=1, pady=1)
            self.demanda_entries.append(e)

        self.llenar_datos_ejemplo()

    def llenar_datos_ejemplo(self):
        costos = [[10, 0, 10, 11, 0], [12, 7, 9, 20, 0], [0, 14, 16, 18, 0]]
        oferta = [15, 25, 5]
        demanda = [5, 15, 15, 5, 5]

        for i in range(self.filas):
            for j in range(self.columnas):
                self.costo_entries[i][j].delete(0, "end")
                self.costo_entries[i][j].insert(0, str(costos[i][j] if i < len(costos) and j < len(costos[0]) else 0))
            self.oferta_entries[i].delete(0, "end")
            self.oferta_entries[i].insert(0, str(oferta[i] if i < len(oferta) else 0))

        for j in range(self.columnas):
            self.demanda_entries[j].delete(0, "end")
            self.demanda_entries[j].insert(0, str(demanda[j] if j < len(demanda) else 0))

    def leer_datos(self):
        try:
            oferta = [int(e.get()) for e in self.oferta_entries]
            demanda = [int(e.get()) for e in self.demanda_entries]
            costos = [[int(self.costo_entries[i][j].get()) for j in range(self.columnas)] for i in range(self.filas)]
            
            nombres_filas = [e.get().strip() or f"F{i+1}" for i, e in enumerate(self.nombres_filas_entries)]
            nombres_cols = [e.get().strip() or f"T{j+1}" for j, e in enumerate(self.nombres_cols_entries)]

            if any(x < 0 for x in oferta) or any(x < 0 for x in demanda):
                messagebox.showerror("Error", "La oferta y la demanda deben ser mayores o iguales a 0.")
                return None, None, None, None, None
                
            if any(x < 0 for fila in costos for x in fila):
                messagebox.showerror("Error", "Los costos no pueden ser negativos.")
                return None, None, None, None, None

            return oferta, demanda, costos, nombres_filas, nombres_cols
        except ValueError:
            messagebox.showerror("Error", "Todos los campos numéricos deben ser enteros.")
            return None, None, None, None, None

    def resolver(self):
        oferta, demanda, costos, nombres_filas, nombres_cols = self.leer_datos()
        if oferta is None: return

        oferta_base = oferta.copy()
        demanda_base = demanda.copy()
        costos_base = [fila.copy() for fila in costos]
        nombres_filas_alg = nombres_filas.copy()
        nombres_cols_alg = nombres_cols.copy()

        total_o = sum(oferta)
        total_d = sum(demanda)
        
        info_ficticia = ""
        if total_o != total_d:
            if total_o < total_d:
                dif = total_d - total_o
                oferta_base.append(dif)
                costos_base.append([0] * len(demanda_base))
                nombres_filas_alg.append("Ficticio")
                info_ficticia = f"¡Ojo! Faltaban {dif} productos. Se agregó una fila 'Ficticio' con oferta {dif} y costo 0."
            else:
                dif = total_o - total_d
                demanda_base.append(dif)
                for fila in costos_base:
                    fila.append(0)
                nombres_cols_alg.append("Ficticio")
                info_ficticia = f"¡Ojo! Sobraban {dif} productos. Se agregó una columna 'Ficticio' con demanda {dif} y costo 0."

        filas_alg = len(oferta_base)
        cols_alg = len(demanda_base)
        oferta_r = oferta_base.copy()
        demanda_r = demanda_base.copy()
        asignaciones = []

        i, j = 0, 0
        while i < filas_alg and j < cols_alg:
            cant = min(oferta_r[i], demanda_r[j])
            asignaciones.append({'i': i, 'j': j, 'cant': cant, 'of_ant': oferta_r[i], 'dem_ant': demanda_r[j]})
            oferta_r[i] -= cant
            demanda_r[j] -= cant

            if oferta_r[i] == 0 and demanda_r[j] == 0:
                i += 1; j += 1
            elif oferta_r[i] == 0:
                i += 1
            else:
                j += 1

        self.dibujar_paso_a_paso(oferta_base, demanda_base, costos_base, asignaciones, info_ficticia, nombres_filas_alg, nombres_cols_alg)

    def dibujar_paso_a_paso(self, oferta, demanda, costos, asignaciones, info_ficticia, nombres_filas, nombres_cols):
        self.canvas_resultados.delete("all")
        
        x_offset = 30
        y_offset = 30
        
        self.canvas_resultados.create_text(x_offset, y_offset, text="El Juego de la Esquina Noroeste", font=("Segoe UI", 18, "bold"), anchor="nw", fill="#1e3a5f")
        y_offset += 40
        
        self.canvas_resultados.create_text(x_offset, y_offset, text="Reglas: Empieza siempre arriba a la izquierda. Toma el número más pequeño entre lo que tienes (Oferta) y lo que te piden (Demanda).", font=("Segoe UI", 10, "italic"), anchor="nw", fill="#555", width=800)
        y_offset += 40
        
        if info_ficticia:
            self.canvas_resultados.create_text(x_offset, y_offset, text=f"⚠️ {info_ficticia}", font=("Segoe UI", 11, "bold"), fill="#d9534f", anchor="nw", width=800)
            y_offset += 40

        filas = len(oferta)
        cols = len(demanda)
        ancho_celda = 90
        alto_celda = 45
        
        self.canvas_resultados.create_text(x_offset, y_offset, text="Paso 0: La tabla inicial", font=("Segoe UI", 12, "bold"), anchor="nw", fill="#007bff")
        y_offset += 30
        
        x_ini = x_offset
        y_ini = y_offset
        
        self.canvas_resultados.create_rectangle(x_ini, y_ini, x_ini + ancho_celda, y_ini + alto_celda, fill="#f0f0f0")
        for j in range(cols):
            x1 = x_ini + ancho_celda * (j + 1)
            self.canvas_resultados.create_rectangle(x1, y_ini, x1 + ancho_celda, y_ini + alto_celda, fill="#f0f0f0")
            self.canvas_resultados.create_text(x1 + ancho_celda/2, y_ini + alto_celda/2, text=nombres_cols[j], font=("Segoe UI", 9, "bold"))
        
        x_of = x_ini + ancho_celda * (cols + 1)
        self.canvas_resultados.create_rectangle(x_of, y_ini, x_of + ancho_celda, y_ini + alto_celda, fill="#e0e0e0")
        self.canvas_resultados.create_text(x_of + ancho_celda/2, y_ini + alto_celda/2, text="Oferta", font=("Segoe UI", 10, "bold"))

        for i in range(filas):
            y_fila = y_ini + alto_celda * (i + 1)
            self.canvas_resultados.create_rectangle(x_ini, y_fila, x_ini + ancho_celda, y_fila + alto_celda, fill="#f0f0f0")
            self.canvas_resultados.create_text(x_ini + ancho_celda/2, y_fila + alto_celda/2, text=nombres_filas[i], font=("Segoe UI", 9, "bold"))
            
            self.canvas_resultados.create_rectangle(x_of, y_fila, x_of + ancho_celda, y_fila + alto_celda, fill="#fff3cd")
            self.canvas_resultados.create_text(x_of + ancho_celda/2, y_fila + alto_celda/2, text=str(oferta[i]), font=("Segoe UI", 11, "bold"), fill="#d9534f")

            for j in range(cols):
                x_celda = x_ini + ancho_celda * (j + 1)
                self.canvas_resultados.create_rectangle(x_celda, y_fila, x_celda + ancho_celda, y_fila + alto_celda, outline="#999")
                self.canvas_resultados.create_text(x_celda + ancho_celda/2, y_fila + alto_celda/2, text=str(costos[i][j]), font=("Segoe UI", 10))

        y_dem = y_ini + alto_celda * (filas + 1)
        self.canvas_resultados.create_rectangle(x_ini, y_dem, x_ini + ancho_celda, y_dem + alto_celda, fill="#f0f0f0")
        self.canvas_resultados.create_text(x_ini + ancho_celda/2, y_dem + alto_celda/2, text="Demanda", font=("Segoe UI", 9, "bold"))
        
        for j in range(cols):
            x_celda = x_ini + ancho_celda * (j + 1)
            self.canvas_resultados.create_rectangle(x_celda, y_dem, x_celda + ancho_celda, y_dem + alto_celda, fill="#fff3cd")
            self.canvas_resultados.create_text(x_celda + ancho_celda/2, y_dem + alto_celda/2, text=str(demanda[j]), font=("Segoe UI", 11, "bold"), fill="#d9534f")

        y_offset = y_dem + alto_celda + 50

        for paso_idx, paso in enumerate(asignaciones):
            nombre_fila_actual = nombres_filas[paso['i']]
            nombre_col_actual = nombres_cols[paso['j']]
            
            explicacion = f"Paso {paso_idx+1}: Estamos en la celda {nombre_fila_actual} → {nombre_col_actual}.\n"
            explicacion += f"➜ Tenemos {paso['of_ant']} de oferta y nos piden {paso['dem_ant']} de demanda.\n"
            explicacion += f"➜ El número más pequeño es {paso['cant']}. ¡Así que asignamos {paso['cant']} aquí en ROJO!\n"
            
            if paso['of_ant'] == paso['dem_ant']:
                explicacion += f"➜ Como se acabó la oferta Y la demanda, avanzamos en diagonal."
            elif paso['of_ant'] == paso['cant']:
                explicacion += f"➜ Como se acabó la oferta, avanzamos hacia ABAJO ⬇️."
            else:
                explicacion += f"➜ Como se acabó la demanda, avanzamos a la DERECHA ➡️."

            self.canvas_resultados.create_text(x_offset, y_offset, text=f"Paso {paso_idx+1}:", font=("Segoe UI", 12, "bold"), anchor="nw", fill="#007bff")
            self.canvas_resultados.create_text(x_offset + 60, y_offset, text=explicacion, font=("Segoe UI", 10), anchor="nw", width=800)
            y_offset += 75 

            x_ini = x_offset
            y_ini = y_offset
            
            self.canvas_resultados.create_rectangle(x_ini, y_ini, x_ini + ancho_celda, y_ini + alto_celda, fill="#f0f0f0")
            for j in range(cols):
                x1 = x_ini + ancho_celda * (j + 1)
                self.canvas_resultados.create_rectangle(x1, y_ini, x1 + ancho_celda, y_ini + alto_celda, fill="#f0f0f0")
                self.canvas_resultados.create_text(x1 + ancho_celda/2, y_ini + alto_celda/2, text=nombres_cols[j], font=("Segoe UI", 9, "bold"))
            
            self.canvas_resultados.create_rectangle(x_of, y_ini, x_of + ancho_celda, y_ini + alto_celda, fill="#e0e0e0")
            self.canvas_resultados.create_text(x_of + ancho_celda/2, y_ini + alto_celda/2, text="Oferta", font=("Segoe UI", 10, "bold"))

            for i in range(filas):
                y_fila = y_ini + alto_celda * (i + 1)
                self.canvas_resultados.create_rectangle(x_ini, y_fila, x_ini + ancho_celda, y_fila + alto_celda, fill="#f0f0f0")
                self.canvas_resultados.create_text(x_ini + ancho_celda/2, y_fila + alto_celda/2, text=nombres_filas[i], font=("Segoe UI", 9, "bold"))
                
                of_rest = oferta[i]
                for k in range(paso_idx + 1):
                    if asignaciones[k]['i'] == i:
                        of_rest -= asignaciones[k]['cant']
                
                self.canvas_resultados.create_rectangle(x_of, y_fila, x_of + ancho_celda, y_fila + alto_celda, fill="#fff3cd")
                self.canvas_resultados.create_text(x_of + ancho_celda/2, y_fila + alto_celda/2, text=str(of_rest if of_rest > 0 else 0), font=("Segoe UI", 10))

                for j in range(cols):
                    x_celda = x_ini + ancho_celda * (j + 1)
                    outline_color = "#007bff" if (i == paso['i'] and j == paso['j']) else "#999"
                    outline_width = 3 if outline_color == "#007bff" else 1
                    
                    self.canvas_resultados.create_rectangle(x_celda, y_fila, x_celda + ancho_celda, y_fila + alto_celda, outline=outline_color, width=outline_width)
                    self.canvas_resultados.create_text(x_celda + ancho_celda - 5, y_fila + 8, text=str(costos[i][j]), font=("Arial", 8), anchor="ne", fill="#555")

                    cant_asignada = None
                    for k in range(paso_idx + 1):
                        if asignaciones[k]['i'] == i and asignaciones[k]['j'] == j:
                            cant_asignada = asignaciones[k]['cant']
                            break
                    
                    if cant_asignada is not None:
                        self.canvas_resultados.create_text(x_celda + ancho_celda/2, y_fila + alto_celda/2 + 4, text=str(cant_asignada), font=("Segoe UI", 14, "bold"), fill="#d9534f")

            y_dem = y_ini + alto_celda * (filas + 1)
            self.canvas_resultados.create_rectangle(x_ini, y_dem, x_ini + ancho_celda, y_dem + alto_celda, fill="#f0f0f0")
            self.canvas_resultados.create_text(x_ini + ancho_celda/2, y_dem + alto_celda/2, text="Demanda", font=("Segoe UI", 9, "bold"))
            
            for j in range(cols):
                dem_rest = demanda[j]
                for k in range(paso_idx + 1):
                    if asignaciones[k]['j'] == j:
                        dem_rest -= asignaciones[k]['cant']

                x_celda = x_ini + ancho_celda * (j + 1)
                self.canvas_resultados.create_rectangle(x_celda, y_dem, x_celda + ancho_celda, y_dem + alto_celda, fill="#fff3cd")
                self.canvas_resultados.create_text(x_celda + ancho_celda/2, y_dem + alto_celda/2, text=str(dem_rest if dem_rest > 0 else 0), font=("Segoe UI", 10))

            y_offset = y_dem + alto_celda + 40 

        self.canvas_resultados.create_text(x_offset, y_offset, text="🎉 ¡Juego Terminado! Resultado Final", font=("Segoe UI", 16, "bold"), anchor="nw", fill="#28a745")
        y_offset += 30
        
        terminos = []
        costo_total = 0
        for a in asignaciones:
            if a['cant'] > 0:
                terminos.append(f"{a['cant']}({costos[a['i']][a['j']]})")
                costo_total += a['cant'] * costos[a['i']][a['j']]
        
        self.canvas_resultados.create_text(x_offset, y_offset, text=f"F.O.: {' + '.join(terminos)}", font=("Consolas", 12), anchor="nw")
        y_offset += 25
        self.canvas_resultados.create_text(x_offset, y_offset, text=f"El Costo Total es: {costo_total}", font=("Segoe UI", 14, "bold"), anchor="nw", fill="#d9534f")
        
        # Actualizar la región de scroll para abarcar TODO (ancho y alto)
        self.canvas_resultados.config(scrollregion=self.canvas_resultados.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = EsquinaNoroesteApp(root)
    root.mainloop()