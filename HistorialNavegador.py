
class Pila:
    def __init__(self):
        self.elementos = []

    def push(self, elemento):
        self.elementos.append(elemento)

    def pop(self):
        if not self.elementos:
            return None
        return self.elementos.pop()

    def esta_vacia(self):
        return len(self.elementos) == 0


class Navegador:
    def __init__(self):
        self.historial = Pila()
        self.futuro = Pila()
        self.actual = None

    def visitar(self, sitio):
        if self.actual is not None:
            self.historial.push(self.actual)

        self.actual = sitio
        self.futuro = Pila()
        print("Visitando:", self.actual)

    def atras(self):
        anterior = self.historial.pop()

        if anterior is None:
            print("No hay paginas anteriores")
            return

        self.futuro.push(self.actual)
        self.actual = anterior
        print("Pagina actual:", self.actual)

    def adelante(self):
        siguiente = self.futuro.pop()

        if siguiente is None:
            print("No hay paginas siguientes")
            return

        self.historial.push(self.actual)
        self.actual = siguiente
        print("Pagina actual:", self.actual)

    def mostrar(self):
        print("Pagina actual:", self.actual)
        print("Historial anterior:", self.historial.elementos)
        print("Paginas siguientes:", self.futuro.elementos)


navegador = Navegador()

while True:
    print("\n--- MENU DEL NAVEGADOR ---")
    print("1. Visitar sitio")
    print("2. Regresar")
    print("3. Avanzar")
    print("4. Mostrar historial")
    print("5. Salir")

    opcion = input("Selecciona una opcion: ")

    if opcion == "1":
        sitio = input("Escribe la direccion del sitio: ")
        navegador.visitar(sitio)
    elif opcion == "2":
        navegador.atras()
    elif opcion == "3":
        navegador.adelante()
    elif opcion == "4":
        navegador.mostrar()
    elif opcion == "5":
        print("Cerrando navegador")
        break
    else:
        print("Opcion no valida")
