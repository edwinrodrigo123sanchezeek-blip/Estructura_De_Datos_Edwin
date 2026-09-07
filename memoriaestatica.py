calificaciones = [0] * 5

for i in range(5):
    calificaciones[i] = int(input("Captura la calificación: "))

for i in range(5):
    print("Calificación", i + 1, ":", calificaciones[i])