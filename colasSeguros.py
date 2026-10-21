
class Cola:
    def __init__(self):
        self.elementos = []

    def encolar(self, elemento):
        self.elementos.append(elemento)

    def desencolar(self):
        if self.esta_vacia():
            return None
        return self.elementos.pop(0)

    def esta_vacia(self):
        return len(self.elementos) == 0


class SistemaSeguros:
    def __init__(self):
        self.colas = {}
        self.contadores = {}

    def obtener_cola(self, servicio):
        if servicio not in self.colas:
            self.colas[servicio] = Cola()
            self.contadores[servicio] = 0

        return self.colas[servicio]

    def registrar_cliente(self, servicio):
        cola = self.obtener_cola(servicio)

        self.contadores[servicio] += 1
        turno = self.contadores[servicio]

        cola.encolar(turno)

        print(
            f"Cliente registrado en servicio {servicio}. "
            f"Su turno es: {turno}"
        )

    def atender_cliente(self, servicio):
        cola = self.obtener_cola(servicio)

        if cola.esta_vacia():
            print(f"No hay clientes en el servicio {servicio}.")
        else:
            turno = cola.desencolar()
            print(
                f"Llamando al turno {turno}, "
                f"servicio {servicio}."
            )

    def ejecutar(self):
        print("SISTEMA DE ATENCION - SEGUROS")
        print("C seguido del servicio: registrar cliente")
        print("A seguido del servicio: atender cliente")
        print("S: salir")
        print("Ejemplos: C1, A1, C2, A2")

        while True:
            comando = input("\nIngrese un comando: ").strip().upper()

            if comando == "S":
                print("Sistema finalizado.")
                break

            if len(comando) < 2:
                print("Comando invalido.")
                continue

            accion = comando[0]
            numero_servicio = comando[1:]

            if not numero_servicio.isdigit():
                print("Debe indicar un numero de servicio.")
                continue

            servicio = int(numero_servicio)

            if servicio <= 0:
                print("El servicio debe ser mayor que cero.")
                continue

            if accion == "C":
                self.registrar_cliente(servicio)

            elif accion == "A":
                self.atender_cliente(servicio)

            else:
                print("Accion desconocida. Use C, A o S.")


if __name__ == "__main__":
    sistema = SistemaSeguros()
    sistema.ejecutar()
