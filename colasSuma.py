
class Cola:
    def __init__(self):
        self.elementos = []

    def encolar(self, elemento):
        self.elementos.append(elemento)

    def desencolar(self):
        if self.esta_vacia():
            raise ValueError("La cola esta vacia")
        return self.elementos.pop(0)

    def esta_vacia(self):
        return len(self.elementos) == 0

    def __str__(self):
        return str(self.elementos)


def sumar_colas(cola_a, cola_b):
    if len(cola_a.elementos) != len(cola_b.elementos):
        raise ValueError("Las colas deben tener igual longitud")

    resultado = Cola()

    while not cola_a.esta_vacia():
        numero_a = cola_a.desencolar()
        numero_b = cola_b.desencolar()
        resultado.encolar(numero_a + numero_b)

    return resultado


# Ingresar los datos de las colas
cola_a = Cola()
cola_b = Cola()

cantidad = int(input("¿Cuantos elementos tendra cada cola?: "))

print("\nIngrese los elementos de la Cola A:")
for i in range(cantidad):
    numero = int(input(f"Elemento {i + 1}: "))
    cola_a.encolar(numero)

print("\nIngrese los elementos de la Cola B:")
for i in range(cantidad):
    numero = int(input(f"Elemento {i + 1}: "))
    cola_b.encolar(numero)

# Mostrar las colas originales
print("\nCola A:", cola_a)
print("Cola B:", cola_b)

# Sumar las colas
cola_resultado = sumar_colas(cola_a, cola_b)

print("Cola resultado:", cola_resultado)
