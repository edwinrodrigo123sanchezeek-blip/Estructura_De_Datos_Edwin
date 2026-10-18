class Pila:
    def __init__(self):
        self.elementos = []
        
    def push (self, elemento):
        self.elementos.append(elemento)
        
    def pop(self):
       if not self.elementos:
           raise ValueError("La pila esta vacia") 
       return self.elementos.pop()
    def estaVacia(self):
        return len(self.elementos) == 0
def operar(a,b,operador):
    if operador == "+":
        return a + b
    elif operador == "-":
        return a - b
    elif operador == "*":
        return a * b
    elif operador == "/":
        return a / b
    elif operador == "^":
        return a ** b
    else:
        raise ValueError ("Operador no valido")

def evaluar_posfija(expresion):
    pila = Pila()
    
    for token in expresion.split():
        if token not in ["+", "-", "*", "/", "^"]:
            pila.push(float(token))
        else:
            b = pila.pop()
            a = pila.pop()
            pila.push(operar(a,b,token))
    
    resultado = pila.pop()
    
    if not pila.estaVacia():
        raise ValueError("Expresion incorrecta")
    
    return resultado

def evaluarProfija(expresion):
    pila = Pila()
    tokens = expresion.split()[::-1]
    
    for token in tokens:
        if token not in ["+", "-", "*", "/", "^"]:
            pila.push(float(token))
            
        else:
            a = pila.pop()
            b = pila.pop()
            pila.push(operar(a,b, token))
            
    resultado = pila.pop()
    
    if not pila.estaVacia():
        raise ValueError('Expresion incorrecta')
    
    return resultado

print("Evaluador de expresioness")
print("1. Notacion posfija")
print("2. Notacion Profija")
print("3. Salir")
while True:
    opcion = input("Elige una opcion: ")

    if opcion == "3":
        print("Programa finalizado")
        break

    if opcion not in ["1", "2"]:
        print("Opcion no valida")
        continue

    expresion = input(
        "Escribe la expresion separada por espacios: "
    )

    try:
        if opcion == "1":
            print("Resultado:",evaluar_posfija(expresion))
        elif opcion == "2":
            print("Resultado:", evaluarProfija(expresion))
        else:
            print("opcion no valida")
    except (ValueError, ZeroDivisionError) as error:
        print("Error: ", error)
