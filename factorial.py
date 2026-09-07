
import time

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)


inicio = time.perf_counter()

# Código que quieres medir

for i in range(1000000):
    pass

fin = time.perf_counter()

a = 990

print(factorial(a))
print(f"Tiempo: {fin - inicio:.6f} segundos")  