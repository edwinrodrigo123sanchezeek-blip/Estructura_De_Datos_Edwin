def buscar_pdfs(carpeta):
    print("Entrando a:", carpeta)

    for elemento in carpeta:
        if isinstance(elemento, list):
            # La carpeta contiene otra carpeta
            buscar_pdfs(elemento)

        elif elemento.endswith(".pdf"):
            print("PDF encontrado:", elemento)


# Estructura de ejemplo
carpetas = [
    "tarea.pdf",
    [
        "documento.txt",
        "investigacion.pdf",
        [
            "proyecto.pdf",
            "imagen.jpg"
        ]
    ],
    "foto.png"
]

buscar_pdfs(carpetas)