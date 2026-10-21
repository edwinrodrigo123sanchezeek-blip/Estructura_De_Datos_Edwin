from collections import deque

class CacheWeb:
    def __init__(self, capacidad_maxima: int):
        self.capacidad_maxima = capacidad_maxima
        # Inicializamos la bicola (deque) para almacenar las URLs
        self.cache = deque()

    def consultar_pagina(self, url: str):
        print(f"\n--- Consultando: '{url}' ---")
        
        # 1. Si ya está en la caché, la removemos de su posición actual
        if url in self.cache:
            self.cache.remove(url)
            print(f"-> La página '{url}' ya estaba en la caché. Se mueve al frente.")
        else:
            # 2. Si no está y hay espacio, solo avisamos
            if len(self.cache) < self.capacidad_maxima:
                print(f"-> La página '{url}' no estaba. Hay espacio, se agrega al frente.")
            else:
                # 3. Si no está y NO hay espacio, eliminamos la más antigua (la del final)
                eliminada = self.cache.pop()
                print(f"-> Caché llena. Se elimina la página más antigua del final: '{eliminada}'")
        
        # Agregamos la nueva página al frente de la bicola
        self.cache.appendleft(url)
        self.mostrar_estado()

    def mostrar_estado(self):
        # Mostramos el estado actual de la bicola (Frente a la izquierda, Final a la derecha)
        print(f"Estado actual de la Caché (Frente -> Final): {list(self.cache)}")


# --- SIMULACIÓN CON UN CONJUNTO DE URLS ---
if __name__ == "__main__":
    # Definimos una capacidad máxima de caché de 3 páginas para la prueba
    capacidad = 3
    mi_cache = CacheWeb(capacidad)

    # Conjunto de URLs de prueba que simulan el tráfico web
    urls_a_visitar = [
        "google.com",
        "github.com",
        "stackoverflow.com",
        "google.com",      # Ya está, debe moverse al frente
        "youtube.com",     # No está, caché llena -> elimina la última
        "github.com",      # Ya está, debe moverse al frente
        "itmerida.mx"      # No está, caché llena -> elimina la última
    ]

    print(f"Iniciando simulación de Caché Web con capacidad máxima = {capacidad}")
    
    for url in urls_a_visitar:
        mi_cache.consultar_pagina(url)