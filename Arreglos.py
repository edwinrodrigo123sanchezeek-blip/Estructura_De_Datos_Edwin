import random
import statistics

# Generar una lista de 50 números enteros entre 1 y 100
numeros = [random.randint(150, 250) for _ in range(50)]

# Calcular estadísticas
media = statistics.mean(numeros)
mediana = statistics.median(numeros)
moda = statistics.mode(numeros)
desviacion_estandar = statistics.stdev(numeros)
varianza = statistics.variance(numeros)

# Mostrar resultados
print("Lista de números:")
print(numeros)

print("\nResultados:")
print("Media:", media)
print("Mediana:", mediana)
print("Moda:", moda)
print("Desviación estándar:", desviacion_estandar)
print("Varianza:", varianza)