CAPACIDAD = 15  # tamano fijo del arreglo (10 precargados + espacio para agregar mas)

class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None          # NIL


class ListaIngredientes:
    def __init__(self):
        self.cabeza = None

    def esta_vacia(self):
        return self.cabeza is None

    def buscar(self, ingrediente):
        act = self.cabeza
        while act is not None:
            if act.dato == ingrediente:
                return True
            act = act.sig
        return False

    def insertar(self, ingrediente):
        """Inserta al final. Devuelve False si ya existe."""
        if self.buscar(ingrediente):
            return False
        nuevo = Nodo(ingrediente)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            act = self.cabeza
            while act.sig is not None:
                act = act.sig
            act.sig = nuevo
        return True

    def eliminar(self, ingrediente):
        """Elimina un ingrediente. Devuelve False si no existe."""
        ant, act = None, self.cabeza
        while act is not None and act.dato != ingrediente:
            ant, act = act, act.sig
        if act is None:
            return False
        if ant is None:
            self.cabeza = act.sig
        else:
            ant.sig = act.sig
        return True

    def a_lista(self):
        res, act = [], self.cabeza
        while act is not None:
            res.append(act.dato)
            act = act.sig
        return res


class Postres:
    def __init__(self, capacidad=CAPACIDAD):
        self.capacidad = capacidad
        self.nombres = [None] * capacidad     # arreglo de nombres
        self.listas = [None] * capacidad      # arreglo de listas (mismo indice)
        self.n = 0                            # elementos ocupados

    # Busqueda binaria (el arreglo esta ordenado). Devuelve (encontrado, indice)
    def _buscar(self, nombre):
        ini, fin = 0, self.n - 1
        while ini <= fin:
            medio = (ini + fin) // 2
            if self.nombres[medio] == nombre:
                return True, medio
            if self.nombres[medio] < nombre:
                ini = medio + 1
            else:
                fin = medio - 1
        return False, ini     
    @staticmethod
    def _norm(texto):
        return texto.strip().lower()

    def imprimir(self, nombre):
        nombre = self._norm(nombre)
        if self.n == 0:
            return "ERROR: el arreglo POSTRES esta vacio."
        if not nombre:
            return "ERROR: el nombre del postre no puede estar vacio."
        ok, i = self._buscar(nombre)
        if not ok:
            return f"ERROR: el postre '{nombre}' no existe."
        if self.listas[i].esta_vacia():
            return f"El postre '{nombre}' existe pero no tiene ingredientes (NIL)."
        return f"Ingredientes de '{nombre}': " + " -> ".join(self.listas[i].a_lista()) + " -> NIL"

    def insertar_ingredientes(self, nombre, ingredientes):
        nombre = self._norm(nombre)
        ok, i = self._buscar(nombre)
        if not ok:
            return f"ERROR: el postre '{nombre}' no existe."
        msgs = []
        for ing in ingredientes:
            ing = self._norm(ing)
            if not ing:
                msgs.append("ERROR: ingrediente vacio, se omite.")
            elif self.listas[i].insertar(ing):
                msgs.append(f"OK: '{ing}' insertado.")
            else:
                msgs.append(f"AVISO: '{ing}' ya estaba en la lista.")
        return "\n".join(msgs)

    # c) Eliminar un ingrediente
    def eliminar_ingrediente(self, nombre, ingrediente):
        nombre, ingrediente = self._norm(nombre), self._norm(ingrediente)
        ok, i = self._buscar(nombre)
        if not ok:
            return f"ERROR: el postre '{nombre}' no existe."
        if self.listas[i].esta_vacia():
            return f"ERROR: '{nombre}' no tiene ingredientes que eliminar."
        if not self.listas[i].eliminar(ingrediente):
            return f"ERROR: '{ingrediente}' no esta en la lista de '{nombre}'."
        extra = " (la lista quedo vacia)" if self.listas[i].esta_vacia() else ""
        return f"OK: '{ingrediente}' eliminado de '{nombre}'{extra}."

    def alta(self, nombre, ingredientes):
        nombre = self._norm(nombre)
        if not nombre:
            return "ERROR: el nombre del postre no puede estar vacio."
        if self.n == self.capacidad:
            return "ERROR: arreglo lleno (desbordamiento), no se puede dar de alta."
        ok, pos = self._buscar(nombre)
        if ok:
            return f"ERROR: el postre '{nombre}' ya existe."
        self._insertar_en(pos, nombre, ingredientes)
        return f"OK: postre '{nombre}' dado de alta en la posicion {pos}."

    def _insertar_en(self, pos, nombre, ingredientes):
        for k in range(self.n, pos, -1):          # recorrer a la derecha
            self.nombres[k] = self.nombres[k - 1]
            self.listas[k] = self.listas[k - 1]
        lista = ListaIngredientes()
        for ing in ingredientes:
            ing = self._norm(ing)
            if ing:
                lista.insertar(ing)
        self.nombres[pos], self.listas[pos] = nombre, lista
        self.n += 1

    def baja(self, nombre):
        nombre = self._norm(nombre)
        if self.n == 0:
            return "ERROR: arreglo vacio (subdesbordamiento), nada que dar de baja."
        ok, i = self._buscar(nombre)
        if not ok:
            return f"ERROR: el postre '{nombre}' no existe."
        for k in range(i, self.n - 1):            # recorrer a la izquierda
            self.nombres[k] = self.nombres[k + 1]
            self.listas[k] = self.listas[k + 1]
        self.nombres[self.n - 1] = None
        self.listas[self.n - 1] = None            # lista completa descartada
        self.n -= 1
        return f"OK: postre '{nombre}' y todos sus ingredientes dados de baja."

    def mostrar(self):
        if self.n == 0:
            return "(POSTRES vacio)"
        lineas = []
        for i in range(self.n):
            ings = self.listas[i].a_lista()
            lineas.append(f"[{i}] {self.nombres[i]:<12} -> " +
                          (" -> ".join(ings) + " -> NIL" if ings else "NIL"))
        return "\n".join(lineas)

    def mostrar_nombres(self):
        """Muestra solo los nombres de los postres, sin ingredientes."""
        if self.n == 0:
            return "(POSTRES vacio)"
        return "\n".join(f"[{i}] {self.nombres[i]}" for i in range(self.n))

    def baja_indice(self, i):
        """Elimina el elemento en la posicion i y descarta su lista completa."""
        perdidos = self.listas[i].a_lista()       # falla si listas[i] es None
        for k in range(i, self.n - 1):
            self.nombres[k] = self.nombres[k + 1]
            self.listas[k] = self.listas[k + 1]
        self.nombres[self.n - 1] = None
        self.listas[self.n - 1] = None
        self.n -= 1
        return perdidos

    def insertar_sin_validar(self, nombre, ingredientes):
        pos = self.n
        while pos > 0 and self.nombres[pos - 1] > nombre:
            pos -= 1
        self._insertar_en(pos, nombre, ingredientes)

#Ejercicio 2
def eliminar_repetidos_ingenuo(p):
    for i in range(p.n):
        if p.nombres[i] == p.nombres[i + 1]:      # <- i+1 se sale del rango
            p.baja_indice(i + 1)


def eliminar_repetidos(p, fusionar=True):
    i = 0
    while i < p.n - 1:
        if p.nombres[i] == p.nombres[i + 1]:
            if fusionar:
                for ing in p.listas[i + 1].a_lista():
                    p.listas[i].insertar(ing)
            for k in range(i + 1, p.n - 1):
                p.nombres[k] = p.nombres[k + 1]
                p.listas[k] = p.listas[k + 1]
            p.nombres[p.n - 1] = None
            p.listas[p.n - 1] = None
            p.n -= 1
        else:
            i += 1


def cargar_datos_iniciales(p):
    """Carga postres de ejemplo para que la estructura ya venga con datos.
    Se dan de alta desatordenados a proposito: alta() los deja ordenados."""
    datos = {
        "Flan": ["huevo", "leche", "azucar", "vainilla"],
        "Arroz con leche": ["arroz", "leche", "azucar", "canela"],
        "Gelatina": ["grenetina", "agua", "azucar", "fruta"],
        "Pastel de chocolate": ["harina", "chocolate", "huevo", "mantequilla", "azucar"],
        "Helado": ["leche", "crema", "azucar", "vainilla"],
        "Churros": ["harina", "agua", "azucar", "canela", "aceite"],
        "Brownie": ["chocolate", "harina", "huevo", "mantequilla", "azucar"],
        "Pay de limon": ["galleta", "limon", "leche condensada", "mantequilla"],
        "Tres leches": ["harina", "huevo", "leche", "leche condensada", "crema"],
        "Mousse de fresa": ["fresa", "crema", "azucar", "grenetina"],
    }
    for nombre, ingredientes in datos.items():
        p.alta(nombre, ingredientes)


def menu():
    p = Postres()
    cargar_datos_iniciales(p)
    print("Postres precargados:")
    print(p.mostrar_nombres())
    while True:
        print("\n1.Imprimir  2.Insertar ingredientes  3.Eliminar ingrediente")
        print("4.Alta postre  5.Baja postre  6.Mostrar postres  0.Salir")
        op = input("Opcion: ").strip()
        if op == "1":
            print(p.imprimir(input("Postre: ")))
        elif op == "2":
            n = input("Postre: ")
            print(p.insertar_ingredientes(n, input("Ingredientes (separados por coma): ").split(",")))
        elif op == "3":
            print(p.eliminar_ingrediente(input("Postre: "), input("Ingrediente: ")))
        elif op == "4":
            n = input("Postre: ")
            print(p.alta(n, input("Ingredientes (separados por coma): ").split(",")))
        elif op == "5":
            print(p.baja(input("Postre: ")))
        elif op == "6":
            print(p.mostrar_nombres())
        elif op == "0":
            break
        else:
            print("ERROR: opcion invalida.")


if __name__ == "__main__":
    menu()