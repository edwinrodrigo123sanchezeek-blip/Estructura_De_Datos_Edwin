
# Programa de ventas mensuales
# Departamentos: Ropa, Deportes y Juguetería

departamentos = ["Ropa", "Deportes", "Juguetería"]

meses = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# Crear arreglo bidimensional de 3 departamentos x 12 meses
ventas = [[0 for _ in range(12)] for _ in range(3)]


# Método para insertar una venta
def insertar(departamento, mes, cantidad):
    ventas[departamento][mes] = cantidad
    print("Venta insertada correctamente.")


# Método para buscar una venta
def buscar(departamento, mes):
    venta = ventas[departamento][mes]

    print(
        f"Venta de {departamentos[departamento]} "
        f"en {meses[mes]}: ${venta:.2f}"
    )


# Método para eliminar una venta
def eliminar(departamento, mes):
    ventas[departamento][mes] = 0
    print("Venta eliminada correctamente.")


# Método para mostrar todas las ventas
def mostrar_ventas():
    print("\n========== VENTAS MENSUALES ==========")

    print(f"{'Departamento':<15}", end="")

    for mes in meses:
        print(f"{mes[:3]:>8}", end="")

    print()

    for i in range(len(departamentos)):
        print(f"{departamentos[i]:<15}", end="")

        for j in range(len(meses)):
            print(f"${ventas[i][j]:>7.0f}", end="")

        print()


# Menú principal
while True:

    print("\n========== MENÚ ==========")
    print("1. Insertar venta")
    print("2. Buscar venta")
    print("3. Eliminar venta")
    print("4. Mostrar todas las ventas")
    print("5. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":

        print("\nDepartamentos:")
        for i in range(len(departamentos)):
            print(f"{i + 1}. {departamentos[i]}")

        departamento = int(input("Selecciona el departamento: ")) - 1

        print("\nMeses:")
        for i in range(len(meses)):
            print(f"{i + 1}. {meses[i]}")

        mes = int(input("Selecciona el mes: ")) - 1

        cantidad = float(input("Ingresa la cantidad de la venta: $"))

        insertar(departamento, mes, cantidad)

    elif opcion == "2":

        print("\nDepartamentos:")
        for i in range(len(departamentos)):
            print(f"{i + 1}. {departamentos[i]}")

        departamento = int(input("Selecciona el departamento: ")) - 1

        print("\nMeses:")
        for i in range(len(meses)):
            print(f"{i + 1}. {meses[i]}")

        mes = int(input("Selecciona el mes: ")) - 1

        buscar(departamento, mes)

    elif opcion == "3":

        print("\nDepartamentos:")
        for i in range(len(departamentos)):
            print(f"{i + 1}. {departamentos[i]}")

        departamento = int(input("Selecciona el departamento: ")) - 1

        print("\nMeses:")
        for i in range(len(meses)):
            print(f"{i + 1}. {meses[i]}")

        mes = int(input("Selecciona el mes: ")) - 1

        eliminar(departamento, mes)

    elif opcion == "4":

        mostrar_ventas()

    elif opcion == "5":

        print("Programa finalizado.")
        break

    else:

        print("Opción no válida.")
