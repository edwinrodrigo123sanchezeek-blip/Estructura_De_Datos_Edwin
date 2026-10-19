from collections import deque
from dataclasses import dataclass, field
from itertools import count

NORMAL = "normal"
PRIORITARIO = "prioritario"


@dataclass
class Cliente:
    nombre: str
    tipo: str  # NORMAL o PRIORITARIO
    motivo: str = ""  # ej. "tercera edad", "discapacidad"
    turno: int = field(default=0)  # número de llegada (se asigna al registrar)

    def __str__(self):
        etiqueta = "PRIORITARIO" if self.tipo == PRIORITARIO else "normal"
        extra = f" - {self.motivo}" if self.motivo else ""
        return f"Turno #{self.turno:02d} | {self.nombre} ({etiqueta}{extra})"


class SistemaTurnos:
    def __init__(self):
        self.cola_prioritaria = deque()
        self.cola_normal = deque()
        self.orden_atencion = []  # historial de clientes atendidos
        self._contador = count(1)

    # -- Llegada de clientes ------------------------------------------------
    def registrar_cliente(self, nombre, tipo=NORMAL, motivo=""):
        if tipo not in (NORMAL, PRIORITARIO):
            raise ValueError("El tipo debe ser 'normal' o 'prioritario'")
        cliente = Cliente(nombre, tipo, motivo, turno=next(self._contador))
        if tipo == PRIORITARIO:
            self.cola_prioritaria.append(cliente)
        else:
            self.cola_normal.append(cliente)
        print(f"  [LLEGADA]  {cliente}")
        return cliente

    # -- Atención -----------------------------------------------------------
    def atender_siguiente(self):
        """Atiende al siguiente cliente según la regla de prioridad."""
        if self.cola_prioritaria:
            cliente = self.cola_prioritaria.popleft()
        elif self.cola_normal:
            cliente = self.cola_normal.popleft()
        else:
            print("  [AVISO]    No hay clientes en espera.")
            return None
        self.orden_atencion.append(cliente)
        print(f"  [ATENDIDO] {cliente}")
        return cliente

    def atender_todos(self):
        while self.hay_clientes():
            self.atender_siguiente()

    # -- Consultas ----------------------------------------------------------
    def hay_clientes(self):
        return bool(self.cola_prioritaria or self.cola_normal)

    def mostrar_cola(self):
        print("  Cola actual:")
        if not self.hay_clientes():
            print("    (vacía)")
            return
        for c in list(self.cola_prioritaria) + list(self.cola_normal):
            print(f"    -> {c}")

    def mostrar_orden_final(self):
        print("\n" + "=" * 62)
        print("ORDEN FINAL DE ATENCIÓN")
        print("=" * 62)
        for posicion, c in enumerate(self.orden_atencion, start=1):
            print(f"{posicion:2d}. {c}")


def simular():
    banco = SistemaTurnos()

    print("=" * 62)
    print("SIMULACIÓN: SISTEMA DE TURNOS DEL BANCO")
    print("=" * 62)

    print("\n--- Llegan los primeros clientes ---")
    banco.registrar_cliente("Carlos Pérez")
    banco.registrar_cliente("Doña Rosa Méndez", PRIORITARIO, "tercera edad")
    banco.registrar_cliente("Laura Gómez")
    banco.registrar_cliente("Miguel Torres", PRIORITARIO, "discapacidad")
    banco.registrar_cliente("Ana Ramírez")
    banco.mostrar_cola()

    print("\n--- Se atienden 2 clientes ---")
    banco.atender_siguiente()
    banco.atender_siguiente()

    print("\n--- Llegan más clientes mientras se atiende ---")
    banco.registrar_cliente("Jorge Herrera")
    banco.registrar_cliente("Don Alberto Ruiz", PRIORITARIO, "tercera edad")
    banco.registrar_cliente("Sofía Castillo")
    banco.registrar_cliente("Lucía Fernández", PRIORITARIO, "discapacidad")
    banco.registrar_cliente("Pedro Navarro")
    banco.registrar_cliente("Elena Vargas")
    banco.mostrar_cola()

    print("\n--- Se atienden 3 clientes más ---")
    for _ in range(3):
        banco.atender_siguiente()

    print("\n--- Llega un último prioritario ---")
    banco.registrar_cliente("Doña Carmen Soto", PRIORITARIO, "tercera edad")
    banco.mostrar_cola()

    print("\n--- Se atiende al resto de la cola ---")
    banco.atender_todos()

    banco.mostrar_orden_final()


if __name__ == "__main__":
    simular()