from postre import *


def t(titulo):
    print("\n=== " + titulo + " ===")


p = Postres(capacidad=5)

t("d) ALTA")
print(p.alta("Flan", ["huevo", "leche", "azucar", "vainilla"]))
print(p.alta("Arroz con leche", ["arroz", "leche", "canela"]))
print(p.alta("Gelatina", ["grenetina", "agua"]))
print(p.alta("flan", ["huevo"]))          # repetido
print(p.alta("   ", ["x"]))               # nombre vacio
print(p.mostrar())

t("a) IMPRIMIR")
print(p.imprimir("Flan"))
print(p.imprimir("Pastel"))               # no existe
print(p.imprimir(""))                     # vacio

t("b) INSERTAR INGREDIENTES")
print(p.insertar_ingredientes("Gelatina", ["fruta", "agua", ""]))
print(p.insertar_ingredientes("Pastel", ["harina"]))
print(p.imprimir("Gelatina"))

t("c) ELIMINAR INGREDIENTE")
print(p.eliminar_ingrediente("Flan", "vainilla"))      # primero/ultimo/medio
print(p.eliminar_ingrediente("Flan", "chocolate"))     # no existe
print(p.eliminar_ingrediente("Pastel", "harina"))      # postre no existe
print(p.imprimir("Flan"))

t("d) ARREGLO LLENO")
print(p.alta("Helado", ["leche"]))
print(p.alta("Natilla", ["leche"]))
print(p.alta("Pay", ["queso"]))           # capacidad 5 -> desbordamiento

t("e) BAJA")
print(p.baja("Gelatina"))
print(p.baja("Gelatina"))                 # ya no existe
print(p.mostrar())
v = Postres()
print(v.baja("Flan"))                     # arreglo vacio
print(v.imprimir("Flan"))

# ------------------------------------------------------------ Ejercicio 2
def con_repetidos():
    q = Postres()
    q.insertar_sin_validar("flan", ["huevo", "leche", "azucar"])
    q.insertar_sin_validar("gelatina", ["grenetina", "agua"])
    q.insertar_sin_validar("flan", ["huevo", "caramelo"])      # repetido
    q.insertar_sin_validar("pay", ["queso"])
    q.insertar_sin_validar("pay", ["queso"])                   # repetido
    q.insertar_sin_validar("pay", ["galleta"])                 # repetido
    return q


t("EJ.2 estructura con repetidos")
print(con_repetidos().mostrar())

t("EJ.2 intento ingenuo (for con rango fijo)")
q = con_repetidos()
try:
    eliminar_repetidos_ingenuo(q)
except Exception as e:
    print("Mensaje de error:", type(e).__name__, "-", e)
print("Estado tras el error:")
print(q.mostrar())

t("EJ.2 solucion SIN fusionar listas")
q = con_repetidos()
eliminar_repetidos(q, fusionar=False)
print(q.mostrar())

t("EJ.2 solucion fusionando listas")
q = con_repetidos()
eliminar_repetidos(q, fusionar=True)
print(q.mostrar())