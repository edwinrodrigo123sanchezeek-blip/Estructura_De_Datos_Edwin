import time


def hanoi(n, origen, auxiliar, destino):
    """Resuelve recursivamente Hanoi e imprime movimientos; solo para pocos discos."""
    if n == 1:
        print(f"Mover disco de {origen} a {destino}")
        return 1

    movimientos = hanoi(n - 1, origen, destino, auxiliar)
    print(f"Mover disco de {origen} a {destino}")
    movimientos += 1
    movimientos += hanoi(n - 1, auxiliar, origen, destino)
    return movimientos


def contar_movimientos(n):
    """Calcula la cantidad minima sin generar cada movimiento."""
    return 2 ** n - 1


def medir_calculo(n):
    inicio = time.perf_counter()
    movimientos = contar_movimientos(n)
    fin = time.perf_counter()
    return movimientos, fin - inicio


def main():
    print("TORRE DE HANOI: cantidad minima de movimientos")
    print("La medicion siguiente calcula el total matematicamente;")
    print("no ejecuta ni imprime todos los movimientos.")
    print()

    for discos in (5, 10, 30, 64):
        movimientos, segundos = medir_calculo(discos)
        print(f"Discos: {discos}")
        print(f"Movimientos minimos: {movimientos:,}")
        print(f"Tiempo para calcular el total: {segundos:.9f} segundos")
        print("-" * 45)

    print("\nNota: la funcion hanoi() muestra la solucion movimiento a movimiento,")
    print("pero debe usarse solo con pocos discos porque el numero de movimientos")
    print("crece exponencialmente.")


if __name__ == "__main__":
    main()
