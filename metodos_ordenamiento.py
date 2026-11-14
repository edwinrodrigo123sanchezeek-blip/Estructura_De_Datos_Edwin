def shell_sort(arr):
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr

def counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr):
    if not arr:
        return arr
    max_num = max(arr)
    exp = 1
    while max_num // exp > 0:
        counting_sort(arr, exp)
        exp *= 10
    return arr

def main():
    while True:
        print("\n--- MENÚ DE ORDENAMIENTO ---")
        print("1. ShellSort")
        print("2. Quicksort")
        print("3. Heapsort")
        print("4. Radix")
        print("5. Salir")
        
        opcion = input("Seleccione una opción (1-5): ")
        
        if opcion == '5':
            print("Saliendo del programa...")
            break
            
        if opcion in ['1', '2', '3', '4']:
            try:
                cantidad = int(input("Ingrese la cantidad de números: "))
                if cantidad <= 0:
                    print("La cantidad debe ser mayor a 0.")
                    continue
                    
                numeros = []
                print(f"Ingrese los {cantidad} números:")
                for i in range(cantidad):
                    while True:
                        try:
                            num = int(input(f"Número {i+1}: "))
                            if num < 0 and opcion == '4':
                                print("Radix Sort en esta implementación solo acepta números positivos. Ingrese otro.")
                                continue
                            numeros.append(num)
                            break
                        except ValueError:
                            print("Por favor, ingrese un número entero válido.")
                            
                print(f"\nArreglo original: {numeros}")
                
                if opcion == '1':
                    resultado = shell_sort(numeros.copy())
                    print(f"Ordenado por ShellSort: {resultado}")
                elif opcion == '2':
                    resultado = quick_sort(numeros.copy())
                    print(f"Ordenado por Quicksort: {resultado}")
                elif opcion == '3':
                    resultado = heap_sort(numeros.copy())
                    print(f"Ordenado por Heapsort: {resultado}")
                elif opcion == '4':
                    resultado = radix_sort(numeros.copy())
                    print(f"Ordenado por Radix: {resultado}")
                    
            except ValueError:
                print("Entrada inválida. Intente de nuevo.")
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()