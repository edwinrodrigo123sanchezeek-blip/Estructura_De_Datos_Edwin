
class Nodo:
    def __init__(self, info):
        self.info = info
        self.liga = None


# CREAR LISTA INSERTANDO AL INICIO
def crear_inicio():
    P = None

    respuesta = input("¿Deseas ingresar un nodo? (1=Sí, 0=No): ")

    while respuesta == "1":
        info = input("Ingresa el dato: ")
        Q = Nodo(info)

        Q.liga = P
        P = Q

        respuesta = input("¿Deseas ingresar otro nodo? (1=Sí, 0=No): ")

    return P


# MOSTRAR LISTA
def mostrar_lista(P):
    if P is None:
        print("La lista está vacía.")
        return

    actual = P
    print("Inicio -> ", end="")

    while actual is not None:
        print(actual.info, end=" -> ")
        actual = actual.liga

    print("NIL")


# INSERTAR AL INICIO
def insertar_inicio(P, info):
    Q = Nodo(info)
    Q.liga = P
    P = Q

    print("Nodo insertado al inicio.")
    return P


# INSERTAR AL FINAL
def insertar_final(P, info):
    Q = Nodo(info)

    if P is None:
        print("Nodo insertado al inicio y al final.")
        return Q

    actual = P

    while actual.liga is not None:
        actual = actual.liga

    actual.liga = Q

    print("Nodo insertado al final.")
    return P


# INSERTAR EN UNA POSICIÓN
# Las posiciones comienzan en 1
def insertar_posicion(P, info, posicion):
    if posicion < 1:
        print("La posición debe ser mayor o igual a 1.")
        return P

    if posicion == 1:
        return insertar_inicio(P, info)

    actual = P
    contador = 1

    while actual is not None and contador < posicion - 1:
        actual = actual.liga
        contador += 1

    if actual is None:
        print("Posición no válida. No se permiten espacios vacíos.")
        return P

    Q = Nodo(info)
    Q.liga = actual.liga
    actual.liga = Q

    print("Nodo insertado en la posición", posicion)
    return P


# INSERTAR DESPUÉS DE UN DATO
def insertar_despues_de(P, buscado, info):
    actual = P

    while actual is not None and actual.info != buscado:
        actual = actual.liga

    if actual is None:
        print("No se encontró el dato", buscado)
        return P

    Q = Nodo(info)
    Q.liga = actual.liga
    actual.liga = Q

    print("Nodo insertado después de", buscado)
    return P


# ELIMINAR AL INICIO
def eliminar_inicio(P):
    if P is None:
        print("La lista está vacía.")
        return P

    eliminado = P.info
    P = P.liga

    print("Se eliminó el nodo:", eliminado)
    return P


# ELIMINAR AL FINAL
def eliminar_final(P):
    if P is None:
        print("La lista está vacía.")
        return P

    if P.liga is None:
        print("Se eliminó el nodo:", P.info)
        return None

    actual = P

    while actual.liga.liga is not None:
        actual = actual.liga

    eliminado = actual.liga.info
    actual.liga = None

    print("Se eliminó el nodo:", eliminado)
    return P


# ELIMINAR POR POSICIÓN
def eliminar_posicion(P, posicion):
    if P is None:
        print("La lista está vacía.")
        return P

    if posicion < 1:
        print("La posición debe ser mayor o igual a 1.")
        return P

    if posicion == 1:
        return eliminar_inicio(P)

    actual = P
    contador = 1

    while actual is not None and contador < posicion - 1:
        actual = actual.liga
        contador += 1

    if actual is None or actual.liga is None:
        print("La posición no existe.")
        return P

    eliminado = actual.liga.info
    actual.liga = actual.liga.liga

    print("Se eliminó el nodo:", eliminado)
    return P


# ELIMINAR POR VALOR
def eliminar_valor(P, buscado):
    if P is None:
        print("La lista está vacía.")
        return P

    if P.info == buscado:
        return eliminar_inicio(P)

    actual = P

    while actual.liga is not None and actual.liga.info != buscado:
        actual = actual.liga

    if actual.liga is None:
        print("No se encontró el dato", buscado)
        return P

    actual.liga = actual.liga.liga

    print("Se eliminó el dato:", buscado)
    return P


# BÚSQUEDA NORMAL
def buscar(P, buscado):
    actual = P
    posicion = 1

    while actual is not None:
        if actual.info == buscado:
            print("Dato encontrado en la posición", posicion)
            return

        actual = actual.liga
        posicion += 1

    print("Dato no encontrado.")


# BÚSQUEDA RECURSIVA
def buscar_recursivo(P, buscado, posicion=1):
    if P is None:
        print("Dato no encontrado.")
        return

    if P.info == buscado:
        print("Dato encontrado en la posición", posicion)
        return

    buscar_recursivo(P.liga, buscado, posicion + 1)


# ORDENAR DE MENOR A MAYOR
# Esta función supone que los datos son números.
def ordenar(P):
    actual = P

    while actual is not None:
        otro = actual.liga

        while otro is not None:
            if int(actual.info) > int(otro.info):
                actual.info, otro.info = otro.info, actual.info

            otro = otro.liga

        actual = actual.liga

    print("Lista ordenada.")
    return P


# BÚSQUEDA ORDENADA
# Usar únicamente después de ordenar los datos numéricos.
def buscar_ordenado(P, buscado):
    actual = P
    posicion = 1

    while actual is not None:
        valor = int(actual.info)

        if valor == buscado:
            print("Dato encontrado en la posición", posicion)
            return

        if valor > buscado:
            print("Dato no encontrado.")
            return

        actual = actual.liga
        posicion += 1

    print("Dato no encontrado.")


# MOVER UN NODO A OTRA POSICIÓN
def mover(P, origen, destino):
    if origen < 1 or destino < 1:
        print("Las posiciones deben ser mayores o iguales a 1.")
        return P

    if origen == destino:
        print("El nodo ya está en esa posición.")
        return P

    if P is None:
        print("La lista está vacía.")
        return P

    # Encontrar el nodo de origen
    anterior = None
    actual = P
    posicion = 1

    while actual is not None and posicion < origen:
        anterior = actual
        actual = actual.liga
        posicion += 1

    if actual is None:
        print("La posición de origen no existe.")
        return P

    # Desconectar el nodo
    if anterior is None:
        P = actual.liga
    else:
        anterior.liga = actual.liga

    # Insertar en el destino dentro de la lista resultante
    if destino == 1:
        actual.liga = P
        P = actual
    else:
        anterior_destino = P
        posicion = 1

        while (anterior_destino is not None
               and posicion < destino - 1):
            anterior_destino = anterior_destino.liga
            posicion += 1

        if anterior_destino is None:
            # Destino posterior al final: restaurar la lista
            if P is None:
                actual.liga = None
                return actual

            ultimo = P
            while ultimo.liga is not None:
                ultimo = ultimo.liga

            ultimo.liga = actual
            actual.liga = None
        else:
            actual.liga = anterior_destino.liga
            anterior_destino.liga = actual

    print("Nodo movido correctamente.")
    return P


# HACER QUE DOS NODOS APUNTEN AL MISMO NODO
def compartir_nodo(P, dato_a, dato_b):
    actual = P
    nodo_a = None
    nodo_b = None

    while actual is not None:
        if actual.info == dato_a and nodo_a is None:
            nodo_a = actual

        if actual.info == dato_b and nodo_b is None:
            nodo_b = actual

        actual = actual.liga

    if nodo_a is None or nodo_b is None:
        print("No se encontraron ambos nodos.")
        return P

    if nodo_a is nodo_b:
        print("Ambos datos identifican el mismo nodo.")
        return P

    # El enlace de A ahora apunta al mismo nodo que el de B.
    # Esto modifica la estructura original y puede desconectar
    # parte de la cadena que seguía a A.
    nodo_a.liga = nodo_b.liga

    print("El enlace de", dato_a, "ahora apunta al mismo nodo")
    print("que el enlace siguiente de", dato_b)
    print("Advertencia: la lista puede haber cambiado de estructura.")

    return P


# MENÚ PRINCIPAL
def menu():
    P = None

    while True:
        print("\n===== LISTA SIMPLEMENTE LIGADA =====")
        print("1. Crear lista insertando al inicio")
        print("2. Mostrar lista")
        print("3. Insertar al inicio")
        print("4. Insertar al final")
        print("5. Insertar en una posición")
        print("6. Insertar después de un dato")
        print("7. Eliminar al inicio")
        print("8. Eliminar al final")
        print("9. Eliminar por posición")
        print("10. Eliminar por valor")
        print("11. Buscar un dato")
        print("12. Buscar recursivamente")
        print("13. Ordenar números")
        print("14. Buscar en lista ordenada")
        print("15. Mover nodo a otra posición")
        print("16. Compartir enlace entre dos nodos")
        print("0. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            P = crear_inicio()

        elif opcion == "2":
            mostrar_lista(P)

        elif opcion == "3":
            info = input("Dato: ")
            P = insertar_inicio(P, info)

        elif opcion == "4":
            info = input("Dato: ")
            P = insertar_final(P, info)

        elif opcion == "5":
            info = input("Dato: ")
            try:
                posicion = int(input("Posición: "))
                P = insertar_posicion(P, info, posicion)
            except ValueError:
                print("Ingresa un número entero válido.")

        elif opcion == "6":
            buscado = input("¿Después de qué dato?: ")
            info = input("Dato nuevo: ")
            P = insertar_despues_de(P, buscado, info)

        elif opcion == "7":
            P = eliminar_inicio(P)

        elif opcion == "8":
            P = eliminar_final(P)

        elif opcion == "9":
            try:
                posicion = int(input("Posición que deseas eliminar: "))
                P = eliminar_posicion(P, posicion)
            except ValueError:
                print("Ingresa un número entero válido.")

        elif opcion == "10":
            buscado = input("Dato que deseas eliminar: ")
            P = eliminar_valor(P, buscado)

        elif opcion == "11":
            buscado = input("Dato que deseas buscar: ")
            buscar(P, buscado)

        elif opcion == "12":
            buscado = input("Dato que deseas buscar: ")
            buscar_recursivo(P, buscado)

        elif opcion == "13":
            try:
                P = ordenar(P)
            except ValueError:
                print("Todos los datos deben ser números enteros.")

        elif opcion == "14":
            try:
                buscado = int(input("Número que deseas buscar: "))
                buscar_ordenado(P, buscado)
            except ValueError:
                print("Ingresa un número entero válido.")

        elif opcion == "15":
            try:
                origen = int(input("Posición actual: "))
                destino = int(input("Nueva posición: "))
                P = mover(P, origen, destino)
            except ValueError:
                print("Ingresa posiciones enteras.")

        elif opcion == "16":
            dato_a = input("Dato del primer nodo: ")
            dato_b = input("Dato del segundo nodo: ")
            P = compartir_nodo(P, dato_a, dato_b)

        elif opcion == "0":
            print("Programa terminado.")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()

