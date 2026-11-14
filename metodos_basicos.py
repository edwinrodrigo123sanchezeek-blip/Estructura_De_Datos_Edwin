def ordenamiento_burbuja(arr):
    n = len(arr)
    # Recorrer todos los elementos del arreglo
    for i in range(n):
        # Los últimos i elementos ya están en su lugar correcto
        for j in range(0, n - i - 1):
            # Recorrer el arreglo de 0 a n-i-1
            # Intercambiar si el elemento encontrado es mayor que el siguiente
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def ordenamiento_insercion(arr):
    # Recorrer desde el segundo elemento hasta el final
    for i in range(1, len(arr)):
        clave = arr[i]
        j = i - 1
        # Mover los elementos del arreglo que son mayores que la clave
        # a una posición adelante de su posición actual
        while j >= 0 and clave < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = clave
    return arr

def ordenamiento_seleccion(arr):
    # Recorrer todo el arreglo
    for i in range(len(arr)):
        # Encontrar el elemento mínimo en el arreglo sin ordenar
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[min_idx] > arr[j]:
                min_idx = j
        # Intercambiar el elemento mínimo encontrado con el primer elemento
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def main():
    while True:
        print("\n--- MENÚ DE MÉTODOS DE ORDENAMIENTO BÁSICOS ---")
        print("1. Ordenamiento Burbuja")
        print("2. Ordenamiento por Inserción")
        print("3. Ordenamiento por Selección")
        print("4. Salir")
        
        opcion = input("Seleccione una opción (1-4): ")
        
        if opcion == '4':
            print("Saliendo del programa...")
            break
            
        if opcion in ['1', '2', '3']:
            try:
                cantidad = int(input("Ingrese la cantidad de números a ordenar: "))
                if cantidad <= 0:
                    print("La cantidad debe ser mayor a 0.")
                    continue
                    
                numeros = []
                print(f"Ingrese los {cantidad} números:")
                for i in range(cantidad):
                    while True:
                        try:
                            num = int(input(f"Número {i+1}: "))
                            numeros.append(num)
                            break
                        except ValueError:
                            print("Por favor, ingrese un número entero válido.")
                            
                print(f"\nArreglo original: {numeros}")
                arreglo_copia = numeros.copy()
                
                if opcion == '1':
                    resultado = ordenamiento_burbuja(arreglo_copia)
                    print(f"Ordenado por Burbuja: {resultado}")
                elif opcion == '2':
                    resultado = ordenamiento_insercion(arreglo_copia)
                    print(f"Ordenado por Inserción: {resultado}")
                elif opcion == '3':
                    resultado = ordenamiento_seleccion(arreglo_copia)
                    print(f"Ordenado por Selección: {resultado}")
                    
            except ValueError:
                print("Entrada inválida. Intente de nuevo.")
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()