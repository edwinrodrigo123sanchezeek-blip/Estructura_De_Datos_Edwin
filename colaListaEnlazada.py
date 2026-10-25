class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class Cola:
    def __init__(self):
        self.frente = None 
        self.final = None   
        self.tamano = 0

    def esta_vacia(self):
        return self.frente is None

    def encolar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.esta_vacia():
            self.frente = nuevo_nodo
            self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self.tamano += 1

    def desencolar(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        
        dato_extraido = self.frente.dato
        self.frente = self.frente.siguiente
        
        if self.frente is None:
            self.final = None
            
        self.tamano -= 1
        return dato_extraido

    def ver_frente(self):
        if self.esta_vacia():
            raise IndexError("La cola está vacía")
        return self.frente.dato

    def __len__(self):
        return self.tamano



if __name__ == "__main__":
    print("--- Iniciando prueba de la Cola ---")
    
    mi_cola = Cola()
    print(f"¿La cola está vacía? {mi_cola.esta_vacia()}")
    
    mi_cola.encolar("Cliente 1")
    mi_cola.encolar("Cliente 2")
    mi_cola.encolar("Cliente 3")
    
    print(f"Elementos en la cola después de encolar: {len(mi_cola)}")
    print(f"El que está al frente es: {mi_cola.ver_frente()}")

    atendido = mi_cola.desencolar()
    print(f"Atendiendo a: {atendido}")
    
    print(f"El nuevo frente es: {mi_cola.ver_frente()}")
    print(f"Elementos restantes: {len(mi_cola)}")


    mi_cola.desencolar()
    mi_cola.desencolar()
    
    print(f"¿La cola está vacía ahora? {mi_cola.esta_vacia()}")

    try:
        mi_cola.desencolar()
    except IndexError as e:
        print(f"Error controlado: {e}")