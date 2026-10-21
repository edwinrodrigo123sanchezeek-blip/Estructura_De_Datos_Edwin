import streamlit as st
import pandas as pd
import re

# Configuración de la página
st.set_page_config(page_title="Esquina Noroeste Fácil", page_icon="📦", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    .tabla-contenedor { display: flex; justify-content: center; margin: 20px 0; overflow-x: auto; }
    table.tabla-noroeste { border-collapse: collapse; font-family: 'Segoe UI', Arial, sans-serif; background-color: #ffffff; color: #333333; }
    table.tabla-noroeste th, table.tabla-noroeste td { border: 1px solid #999; width: auto; min-width: 80px; height: 50px; text-align: center; vertical-align: middle; position: relative; padding: 0 10px;}
    table.tabla-noroeste th { background-color: #e2e8f0; font-weight: bold; color: #1e3a5f; }
    
    .header-fabrica { background-color: #f1f5f9; font-weight: bold; color: #1e3a5f; }
    .header-demanda { background-color: #dbeafe; font-weight: bold; color: #1e3a5f; font-size: 1.1em; }
    .header-oferta { background-color: #d1fae5; font-weight: bold; color: #065f46; }
    .oferta-restante { background-color: #d1fae5; font-weight: bold; color: #065f46; font-size: 1.1em; }
    
    .celda-costo { font-size: 10px; color: #666; position: absolute; top: 4px; right: 6px; }
    .celda-asignacion { font-size: 20px; font-weight: bold; color: #dc2626; }
    .celda-actual { border: 3px solid #2563eb !important; background-color: #eff6ff; }
    
    .explicacion { font-size: 1em; color: #333; margin-bottom: 15px; background-color: #eff6ff; padding: 15px; border-radius: 8px; border-left: 5px solid #2563eb; }
    .guia-tabla { font-size: 11px; background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin-bottom: 10px; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

st.title("📦 El Juego de la Esquina Noroeste")
st.markdown("""
**Reglas del juego:** 
1. Empieza siempre arriba a la izquierda. 
2. Toma el número más pequeño entre lo que tienes (Oferta) y lo que te piden (Demanda).
3. Si se acaba la Oferta, bajas ⬇️. Si se acaba la Demanda, vas a la derecha ➡️.
""")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.markdown("### 1. Dimensiones")
col_f, col_c = st.sidebar.columns(2)
num_filas = col_f.number_input("Orígenes (Filas)", min_value=1, max_value=10, value=3)
num_cols = col_c.number_input("Destinos (Columnas)", min_value=1, max_value=10, value=5)

# --- NOMBRES PERSONALIZADOS CON AUTORRELLENO ---
st.sidebar.markdown("### 2. Nombres (Editable)")

# Función para autocompletar nombres basados en una lista previa
def generar_nombres(base_list, cantidad, nombre_defecto):
    # Si la lista base es más corta, agregamos nombres
    lista = base_list.copy()
    if len(lista) < cantidad:
        ultimo_nombre = lista[-1] if lista else f"{nombre_defecto} 0"
        match = re.search(r'^(.*?)\s*(\d+)$', ultimo_nombre)
        if match:
            prefijo = match.group(1).strip()
            num = int(match.group(2))
            for _ in range(cantidad - len(lista)):
                num += 1
                lista.append(f"{prefijo} {num}")
        else:
            for i in range(cantidad - len(lista)):
                lista.append(f"{nombre_defecto} {len(lista)+1}")
    
    # Si la lista es más larga, la recortamos para que no sobre
    return lista[:cantidad]

# Generar los nombres exactos que se necesitan AHORA
# Usamos "keys" dinámicas para que Streamlit sepa que si cambia el número de filas/cols, debe actualizar el texto
default_f = ", ".join(generar_nombres(["Máquina 1", "Máquina 2", "Máquina 3"], num_filas, "Origen"))
default_c = ", ".join(generar_nombres(["Ciudad 1", "Ciudad 2", "Ciudad 3", "Ciudad 4", "Ciudad 5"], num_cols, "Destino"))

nombres_filas_input = st.sidebar.text_input(
    "Nombres de Orígenes", 
    value=default_f, 
    key=f"input_f_{num_filas}" # El key cambia si el número de filas cambia
)
nombres_cols_input = st.sidebar.text_input(
    "Nombres de Destinos", 
    value=default_c, 
    key=f"input_c_{num_cols}" # El key cambia si el número de columnas cambia
)

# Procesar lo que el usuario escribió
nombres_f_actuales = [x.strip() for x in nombres_filas_input.split(",") if x.strip()]
nombres_c_actuales = [x.strip() for x in nombres_cols_input.split(",") if x.strip()]

# Relleno de seguridad por si el usuario borra un nombre manualmente
nombres_f_actuales = generar_nombres(nombres_f_actuales, num_filas, "Origen")
nombres_c_actuales = generar_nombres(nombres_c_actuales, num_cols, "Destino")

# --- TABLA NUMÉRICA ---
st.sidebar.markdown("### 3. Matriz de Datos")
if 'df_inicial' not in st.session_state or st.session_state.get('prev_filas') != num_filas or st.session_state.get('prev_cols') != num_cols:
    costos_def = [[10, 0, 10, 11, 0], [12, 7, 9, 20, 0], [0, 14, 16, 18, 0]]
    oferta_def = [15, 25, 5]
    demanda_def = [5, 15, 15, 5, 5]
    
    matriz = []
    for i in range(num_filas):
        fila = [costos_def[i][j] if i < len(costos_def) and j < len(costos_def[0]) else 0 for j in range(num_cols)]
        fila.append(oferta_def[i] if i < len(oferta_def) else 0)
        matriz.append(fila)
    
    fila_dem = [demanda_def[j] if j < len(demanda_def) else 0 for j in range(num_cols)]
    fila_dem.append(0) 
    matriz.append(fila_dem)

    columnas = [f"D{j+1}" for j in range(num_cols)] + ["Oferta"]
    df_inicial = pd.DataFrame(matriz, columns=columnas)
    
    st.session_state.df_inicial = df_inicial
    st.session_state.prev_filas = num_filas
    st.session_state.prev_cols = num_cols

st.sidebar.markdown(f"""
<div class="guia-tabla">
<b>📌 Guía:</b><br>
• Las primeras <b>{num_filas}</b> filas son costos.<br>
• La última columna es la <b>Oferta</b>.<br>
• La última fila es la <b>Demanda</b>.
</div>
""", unsafe_allow_html=True)

df_editado = st.sidebar.data_editor(
    st.session_state.df_inicial,
    hide_index=True,
    use_container_width=True,
    height=(num_filas + 1) * 38 + 40 
)

# Botón para resolver
if st.sidebar.button("▶ EXPLICAR PASO A PASO", type="primary", use_container_width=True):
    try:
        df_editado = df_editado.fillna(0)
        
        df_sin_demanda = df_editado.iloc[:-1] 
        fila_demanda = df_editado.iloc[-1]    
        
        oferta_base = df_sin_demanda["Oferta"].astype(int).tolist()
        costos_base = df_sin_demanda.drop(columns=["Oferta"]).astype(int).values.tolist()
        demanda_base = fila_demanda.drop("Oferta").astype(int).tolist()[:num_cols] 

        if any(x < 0 for x in oferta_base) or any(x < 0 for x in demanda_base):
            st.error("🚫 **Error:** No puedes ingresar ofertas ni demandas negativas.")
            st.stop()
        if any(x < 0 for fila in costos_base for x in fila):
            st.error("🚫 **Error:** No puedes ingresar costos negativos.")
            st.stop()

    except Exception as e:
        st.error(f"Error en los datos: Detalle: {e}")
        st.stop()

    nombres_filas_alg = nombres_f_actuales.copy()
    nombres_cols_alg = nombres_c_actuales.copy()

    total_o = sum(oferta_base)
    total_d = sum(demanda_base)
    
    if total_o != total_d:
        if total_o < total_d:
            dif = total_d - total_o
            oferta_base.append(dif)
            costos_base.append([0] * len(demanda_base))
            nombres_filas_alg.append("Ficticio")
            st.warning(f"⚠️ ¡Ojo! Faltaban {dif} productos. Se agregó un Origen Ficticio con oferta {dif} y costo 0.")
        else:
            dif = total_o - total_d
            demanda_base.append(dif)
            for fila in costos_base:
                fila.append(0)
            nombres_cols_alg.append("Ficticio")
            st.warning(f"⚠️ ¡Ojo! Sobraban {dif} productos. Se agregó un Destino Ficticio con demanda {dif} y costo 0.")

    filas = len(oferta_base)
    cols = len(demanda_base)
    
    oferta_r = oferta_base.copy()
    demanda_r = demanda_base.copy()
    asignaciones = []

    i, j = 0, 0
    while i < filas and j < cols:
        cant = min(oferta_r[i], demanda_r[j])
        asignaciones.append({
            'i': i, 'j': j, 'cant': cant, 
            'of_ant': oferta_r[i], 'dem_ant': demanda_r[j]
        })
        oferta_r[i] -= cant
        demanda_r[j] -= cant

        if oferta_r[i] == 0 and demanda_r[j] == 0:
            i += 1; j += 1
        elif oferta_r[i] == 0:
            i += 1
        else:
            j += 1

    def generar_tabla_html(paso_actual_idx, es_paso_0=False):
        html = '<div class="tabla-contenedor"><table class="tabla-noroeste">'
        
        html += '<tr><th></th>'
        for c in range(cols):
            html += f'<th>{nombres_cols_alg[c]}</th>'
        html += '<th>Oferta</th></tr>'
        
        for r in range(filas):
            html += '<tr>'
            html += f'<td class="header-fabrica">{nombres_filas_alg[r]}</td>'
            
            of_rest = oferta_base[r]
            if not es_paso_0:
                for k in range(paso_actual_idx + 1):
                    if asignaciones[k]['i'] == r:
                        of_rest -= asignaciones[k]['cant']
            
            for c in range(cols):
                es_actual = False
                if not es_paso_0 and r == asignaciones[paso_actual_idx]['i'] and c == asignaciones[paso_actual_idx]['j']:
                    es_actual = True
                    
                clase_celda = 'class="celda-actual"' if es_actual else ''
                html += f'<td {clase_celda}>'
                html += f'<div class="celda-costo">{costos_base[r][c]}</div>'
                
                cant_asignada = None
                if not es_paso_0:
                    for k in range(paso_actual_idx + 1):
                        if asignaciones[k]['i'] == r and asignaciones[k]['j'] == c:
                            cant_asignada = asignaciones[k]['cant']
                            break
                
                if cant_asignada is not None:
                    html += f'<div class="celda-asignacion">{cant_asignada}</div>'
                html += '</td>'
            
            html += f'<td class="oferta-restante">{of_rest if of_rest > 0 else 0}</td>'
            html += '</tr>'
            
        html += '<tr><td class="header-fabrica">Demanda</td>'
        for c in range(cols):
            dem_rest = demanda_base[c]
            if not es_paso_0:
                for k in range(paso_actual_idx + 1):
                    if asignaciones[k]['j'] == c:
                        dem_rest -= asignaciones[k]['cant']
            html += f'<td class="header-demanda">{dem_rest if dem_rest > 0 else 0}</td>'
        html += '<td></td></tr></table></div>'
        return html

    st.markdown("---")
    st.subheader("Paso 0: La tabla inicial")
    st.markdown(generar_tabla_html(0, es_paso_0=True), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Evolución paso a paso")
    
    for paso_idx, paso in enumerate(asignaciones):
        fila_actual = nombres_filas_alg[paso['i']]
        col_actual = nombres_cols_alg[paso['j']]
        oferta_disp = paso['of_ant']
        demanda_req = paso['dem_ant']
        asignado = paso['cant']
        
        explicacion = f"<b>Paso {paso_idx+1}:</b> Estamos en la celda <b>{fila_actual} → {col_actual}</b> (marcada con borde azul).<br>"
        explicacion += f"➜ Tenemos <b>{oferta_disp}</b> de oferta y nos piden <b>{demanda_req}</b> de demanda.<br>"
        explicacion += f"➜ El número más pequeño es <b>{asignado}</b>. ¡Así que asignamos {asignado} aquí en ROJO!<br>"
        
        if oferta_disp == demanda_req:
            explicacion += "➜ Avanzamos en diagonal (abajo y a la derecha)."
        elif oferta_disp == asignado:
            explicacion += "➜ Avanzamos hacia <b>ABAJO ⬇️</b>."
        else:
            explicacion += "➜ Avanzamos a la <b>DERECHA ➡️</b>."

        st.markdown(f'<div class="explicacion">{explicacion}</div>', unsafe_allow_html=True)
        st.markdown(generar_tabla_html(paso_idx), unsafe_allow_html=True)

    # Final
    st.markdown("---")
    st.subheader("🎉 ¡Juego Terminado! Resultado Final")
    
    terminos = []
    costo_total = 0
    for a in asignaciones:
        r, c, cant = a['i'], a['j'], a['cant']
        if cant > 0:
            terminos.append(f"{cant}({costos_base[r][c]})")
            costo_total += cant * costos_base[r][c]
            
    st.markdown("Para saber cuánto nos cuesta todo, multiplicamos la cantidad roja por el costito de arriba, y sumamos todo:")
    st.code(" + ".join(terminos), language="text")
    st.success(f"### El Costo Total es: {costo_total}")
    #py -m streamlit run web.py