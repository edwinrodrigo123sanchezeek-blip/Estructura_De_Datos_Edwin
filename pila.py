
pila = []
CAPACIDAD = 8

def mostrar_pila():
    print("\n" + "=" * 30)
    print("        PILA (LIFO)")
    print("=" * 30)
    print("          TOPE")
    print("           |")
    if not pila:
        print("      +-----------+")
        print("      |   VACIA   |")
        print("      +-----------+")
    else:
        for elemento in reversed(pila):
            print("      +-----------+")
            print(f"      | {str(elemento):^9} |")
        print("      +-----------+")
    print("           |")
    print("      _____|_____")
    print(f"   Elementos: {len(pila)}/{CAPACIDAD}")
    print("=" * 30)

def apilar():
    if len(pila) >= CAPACIDAD:
        print("\nLa pila esta llena. No se pueden agregar mas elementos.")
        return
    valor = input("Escribe el valor que deseas apilar: ").strip()
    if not valor:
        print("No ingresaste ningun valor.")
        return
    pila.append(valor)
    print(f"\nPUSH: se agrego '{valor}' al tope de la pila.")
    mostrar_pila()

def desapilar():
    if not pila:
        print("\nPOP: la pila esta vacia; no hay elementos que quitar.")
        mostrar_pila()
        return
    valor = pila.pop()
    print(f"\nPOP: se elimino '{valor}' del tope de la pila.")
    mostrar_pila()

def ver_tope():
    if not pila:
        print("\nPEEK: la pila esta vacia.")
    else:
        print(f"\nPEEK: el elemento del tope es '{pila[-1]}'.")
    mostrar_pila()

def menu():
    while True:
        print("\nMENU DE OPERACIONES")
        print("1. Apilar (PUSH)")
        print("2. Desapilar (POP)")
        print("3. Ver tope (PEEK)")
        print("4. Mostrar pila")
        print("5. Salir")
        opcion = input("Elige una opcion: ").strip()
        if opcion == "1":
            apilar()
        elif opcion == "2":
            desapilar()
        elif opcion == "3":
            ver_tope()
        elif opcion == "4":
            mostrar_pila()
        elif opcion == "5":
            print("\nPrograma finalizado.")
            break
        else:
            print("\nOpcion no valida. Elige un numero del 1 al 5.")

if __name__ == "__main__":
    print("VISUALIZADOR DE PILA EN CONSOLA")
    print("LIFO: el ultimo en entrar es el primero en salir.")
    mostrar_pila()
    menu()