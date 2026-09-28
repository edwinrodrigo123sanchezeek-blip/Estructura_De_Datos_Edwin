def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


terminos = int(input("¿Cuántos términos quieres mostrar? "))

for i in range(terminos):
    print(fibonacci(i), end=" ")