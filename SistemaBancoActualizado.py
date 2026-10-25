
from collections import deque
from dataclasses import dataclass
from enum import Enum
from itertools import chain, count


class Tipo(Enum):
    NORMAL = "normal"
    PRIORITARIO = "prioritario"


@dataclass(frozen=True)
class Cliente:
    nombre: str
    tipo: Tipo
    motivo: str = ""
    turno: int = 0

    def __str__(self):
        etiqueta = (
            "PRIORITARIO"
            if self.tipo == Tipo.PRIORITARIO
            else "normal"
        )
        extra = f" - {self.motivo}" if self.motivo else ""
        return (
            f"Turno #{self.turno:02d} | "
            f"{self.nombre} ({etiqueta}{extra})"
        )


class SistemaTurnos:
    def __init__(self, salida=print):
        self._cola_prioritaria = deque()
        self._cola_normal = deque()
        self._orden_atencion = []
        self._contador = count(1)
        self._salida = salida

    # Registro de clientes
    def registrar_cliente(
        self, nombre, tipo=Tipo.NORMAL, motivo=""
    ):
        if not isinstance(tipo, Tipo):
            raise ValueError(
                "El tipo debe ser Tipo.NORMAL o Tipo.PRIORITARIO"
            )

        if not nombre or not nombre.strip():
            raise ValueError(
                "El nombre del cliente no puede estar vacío"
            )

        cliente = Cliente(
            nombre=nombre.strip(),
            tipo=tipo,
            motivo=motivo.strip(),
            turno=next(self._contador)
        )

        if tipo == Tipo.PRIORITARIO:
            self._cola_prioritaria.append(cliente)
        else:
            self._cola_normal.append(cliente)

        self._salida(f"  [LLEGADA]  {cliente}")
        return cliente

    # Atención de clientes
    def atender_siguiente(self):
        cola = (
            self._cola_prioritaria
            or self._cola_normal
        )

        if not cola:
            self._salida(
                "  [AVISO]    No hay clientes en espera."
            )
            return None

        cliente = cola.popleft()
        self._orden_atencion.append(cliente)

        self._salida(f"  [ATENDIDO] {cliente}")
        return cliente

    def atender_todos(self):
        atendidos = []

        while self.hay_clientes():
            cliente = self.atender_siguiente()

            if cliente is not None:
                atendidos.append(cliente)

        return atendidos

  
    def hay_clientes(self):
        return bool(
            self._cola_prioritaria
            or self._cola_normal
        )

    def en_espera(self):
        return tuple(
            chain(
                self._cola_prioritaria,
                self._cola_normal
            )
        )

    @property
    def atendidos(self):
        return tuple(self._orden_atencion)


    def mostrar_cola(self):
        self._salida("  Cola actual:")
        clientes = self.en_espera()

        if not clientes:
            self._salida("    (vacía)")
            return

        for cliente in clientes:
            self._salida(f"    -> {cliente}")

   
    def mostrar_orden_final(self):
        self._salida("\n" + "=" * 62)
        self._salida("ORDEN FINAL DE ATENCIÓN")
        self._salida("=" * 62)

        for posicion, cliente in enumerate(
            self._orden_atencion, start=1
        ):
            self._salida(f"{posicion:2d}. {cliente}")


def simular():
    banco = SistemaTurnos()

    print("=" * 62)
    print("SIMULACIÓN: SISTEMA DE TURNOS DEL BANCO")
    print("=" * 62)

    print("\n--- Llegan los primeros clientes ---")

    banco.registrar_cliente("Crlos Pérez")
    banco.registrar_cliente(
        "Doña Rosa Méndez",
        Tipo.PRIORITARIO,
        "tercera edad"
    )
    banco.registrar_cliente("Laura Gómez")
    banco.registrar_cliente(
        "Miguel Torres",
        Tipo.PRIORITARIO,
        "discapacidad"
    )
    banco.registrar_cliente("Ana Ramírez")

    banco.mostrar_cola()

    print("\n--- Se atienden 2 clientes ---")
    banco.atender_siguiente()
    banco.atender_siguiente()

    print("\n--- Llegan más clientes mientras se atiende ---")

    banco.registrar_cliente("Jorge Herrera")
    banco.registrar_cliente(
        "Don Alberto Ruiz",
        Tipo.PRIORITARIO,
        "tercera edad"
    )
    banco.registrar_cliente("Sofía Castillo")
    banco.registrar_cliente(
        "Lucía Fernández",
        Tipo.PRIORITARIO,
        "discapacidad"
    )
    banco.registrar_cliente("Pedro Navarro")
    banco.registrar_cliente("Elena Vargas")

    banco.mostrar_cola()

    print("\n--- Se atienden 3 clientes más ---")

    for _ in range(3):
        banco.atender_siguiente()

    print("\n--- Llega un último prioritario ---")

    banco.registrar_cliente(
        "Doña Carmen Soto",
        Tipo.PRIORITARIO,
        "tercera edad"
    )

    banco.mostrar_cola()

    print("\n--- Se atiende al resto de la cola ---")
    banco.atender_todos()

    banco.mostrar_orden_final()


if __name__ == "__main__":
    simular()
