def mostrarVector(datos):
    for i in range(len(datos)):
        print(datos[i])
def mediana(datos):
    n = len(datos)
    suma = 0
    
    for i in range(n):
        suma += datos[i]
    return suma / n

pares  = [2,4,6,8,10]
inpares = [1,3,5,7,9]

mostrarVector(pares)
print("La mediana de los pares es: ", mediana(pares))
mostrarVector(inpares)
print("La mediana de los impares es: ", mediana(inpares))