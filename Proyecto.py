

class Persona:
    def __init__(self, nombre, edad, telefono, direccion):
        self.nombre = nombre
        self.edad = edad
        self.telefono = telefono
        self.direccion = direccion
        
    def mostrar(self):
        print("-"*20)
        print(f"Nombre: {self.nombre}")
        print(f"Edad: {self.edad}")
        print(f"Telefono: {self.telefono}")
        print(f"Direccion: {self.direccion}")
        
class Paciente(Persona):
    def __init__(self,nombre, edad, telefono, direccion, graduacion, historial, alergias):
        super().__init__(nombre, edad, telefono, direccion)
        self.graduacion = graduacion
        self.historial = historial
        self.alergias = alergias
        
    def agendarCita(self):
        print(f"{self.nombre} ha agendado una cita")
    
    def verExpediente(self):
        print(f"Historial: {self.historial}")
        print(f"Alergias: {self.alergias}")

class Optometrista(Persona):
    def __init__(self,nombre, edad, telefono, direccion, cedula, especialidad):
        super().__init__(nombre, edad, telefono, direccion)
        self.cedula = cedula
        self.especialidad = especialidad
        
    def diagnosticar(self):
        print(f"El optometrista {self.nombre} realizó un diagnóstico")
       
    def generarReceta(self):
        print(f"El optometrista {self.nombre} generó una receta")
    
class Producto:
    def __init__(self, nombre, codigo, precio, stock):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.stock = stock
        
    def mostrarProducto(self):
        print("-"*20)
        print(f"Nombre: {self.nombre}")
        print(f"Código: {self.codigo}")
        print(f"Precio: ${self.precio}")
        print(f"Stock: {self.stock}")
        
    def calcularPrecio(self):
        pass
        
    
    
class Lente(Producto):
    def __init__(self, nombre, codigo, precio, stock, tipoGraduacion, material, filtroAzul):
        super().__init__(nombre, codigo, precio, stock)
        self.tipoGraduacion = tipoGraduacion
        self.material = material
        self.filtroAzul = filtroAzul
    
    def mostrarProducto(self):
        super().mostrarProducto()
        print(f"Graduación: {self.tipoGraduacion}")
        print(f"Material: {self.material}")
        if self.filtroAzul:
            print("Filtro Azul: Si")
        else:
            print("Filtro Azul: No")
        
    def calcularPrecio(self):
        total = self.precio + 300
        if self.filtroAzul:
            total += 200
        return total
    
class Armazon(Producto):
    def __init__(self, nombre, codigo, precio, stock, marca, color, material):
        super().__init__(nombre, codigo, precio, stock)
        self.marca = marca
        self.color = color
        self.material = material
        
    def mostrarProducto(self):
        super().mostrarProducto()
        print(f"Marca: {self.marca}")
        print(f"Color: {self.color}")
        print(f"Material: {self.material}")
        
    def calcularPrecio(self):
        return self.precio + 150
    
class Accesorio(Producto):
    def __init__(self, nombre, codigo, precio, stock, tipo, descripcion):
        super().__init__(nombre, codigo, precio, stock)
        self.tipo = tipo
        self.descripcion = descripcion
    
    def mostrarProducto(self):
        super().mostrarProducto()
        print(f"Tipo: {self.tipo}")
        print(f"Descripción: {self.descripcion}")
    
    def calcularPrecio(self):
        return self.precio * 0.90
    
class Cita:
    def __init__(self,fecha, hora,paciente, optometrista):
        self.fecha = fecha
        self.hora = hora
        self.paciente = paciente
        self.optometrista = optometrista
        
    def confirmar(self):
        print(f"Cita confirmada para {self.paciente.nombre}")
        
        
    def rechazar(self):
        print(f"La cita de {self.paciente.nombre} fue rechazada")
    
class Expediente:
    def __init__(self, paciente,recetas):
         self.paciente = paciente
         self.diagnosticos = []
         self.recetas = recetas
         
    def agregarDiagnostico(self, nuevo):
        self.diagnosticos.append(nuevo)
    
    def mostrarHistorial(self):
        print(f"Expediente de {self.paciente.nombre}")
    
        print("\nDiagnósticos:")
        for diagnostico in self.diagnosticos:
            print(diagnostico)
        
        print("\nRecetas:")
        for receta in self.recetas:
            print(receta)
    
class Venta:
    def __init__(self,paciente):
        self.productos = []
        self.paciente = paciente
        self.total = 0
        
    def agregarProducto(self, producto):
        self.productos.append(producto)
    
    def calcularTotal(self):
        total = 0
        for producto in self.productos:
            total += producto.calcularPrecio()
        self.total = total
        return total
    
    def generarTicket(self):
        self.calcularTotal()
        print(f"TOTAL: ${self.total}")
        
    
class Pedido:
    def __init__(self, proveedor, productos, fecha):
        self.proveedor = proveedor
        self.productos = productos
        self.fecha = fecha
        
    def realizarPedido(self):
        print(f"Pedido realizado al proveedor {self.proveedor}")
        
    def mostrarPedido(self):
        print("-"*20)
        print(f"Proveedor: {self.proveedor}")
        print(f"Fecha: {self.fecha}")
        for producto in self.productos:
            print(producto.nombre)
            
pacientes = []
optometristas = []
productos = []

while True:
    print("\nÓPTICA")
    print("1. Registrar paciente.")
    print("2. Registrar optometrista.")
    print("3. Registrar lente.")
    print("4. Registrar armazón.")
    print("5. Registrar accesorio.")
    print("6. Mostrar productos.")
    print("7. Mostrar pacientes.")
    print("8. Mostrar optometristas.")
    print("9. Guardar los productos en el archivo.")
    print("10. Leer los productos en el archivo.")
    print("11. Mostrar Producto por tipo")
    print("12. Buscar producto.") 
    print("13. Salir.")
    
    
    try:
        opcion = int(input("Selecciona una opción: "))
        
        match opcion:
            case 1:
                while True: 
                    try:
                        nombre = input("Ingresa el nombre del paciente: ")
                        if not nombre.replace(" ", "").isalpha():
                            raise ValueError ("Error en nombre!!!")
                        break
                    except ValueError as e:
                        print("Error:", e)            
                while True: 
                    try: 
                        edad = int(input("Ingresa la edad del paciente: "))
                        if edad <= 0:
                            raise ValueError ("Error en edad!!!")
                        break
                    except ValueError as e:
                        print("Error:", e)
                while True:
                    try: 
                        telefono = input("Ingresa el número telefónico del paciente: ")
                        if not telefono.strip().isdigit():
                            raise ValueError ("Error en Telefono")
                        break
                    except ValueError as e:
                        print("Error:", e)
                    
                while True: 
                    try:
                        direccion = input("Ingresa la dirección del del domicilio del paciente: ")
                        if not direccion.replace(" ", ""):
                            raise ValueError("Error en direccion")
                        break
                    except ValueError as e:
                        print("Error:", e)
                while True: 
                    try:
                        graduacion = input("Ingresa la graduación del paciente: ")
                        if not graduacion.strip():
                            raise ValueError ("Error en graduacion")
                        break
                    except ValueError as e:
                        print("Error:", e)
                while True: 
                    try:
                        historial = input("Ingresa el historial del paciente: ")
                        if not historial.replace(" ", "").isalpha():
                            raise ValueError ("Error en historial")
                        break
                    except ValueError as e:
                        print("Error:" , e)
                    
                while True:
                    try:
                        alergias = input("Ingresa cuales son las alergias del paciente: ")
                        if not alergias.replace(" ", "").isalpha():
                            raise ValueError ("Error en alergias")
                        break
                    except ValueError as e:
                        print("Error", e)
                paciente = Paciente(nombre, edad, telefono, direccion, graduacion, historial, alergias)
                pacientes.append(paciente)
                print("Paciente registrado exitosamente.")
            case 2:
                while True: 
                    try:
                        nombre = input("Ingresa el nombre del optometrista: ")
                        if not nombre.replace(" ", "").isalpha():
                            raise ValueError ("Error en nombre!!!")
                        break
                    except ValueError as e:
                        print("Error", e)            
                while True: 
                    try: 
                        edad = int(input("Ingresa la edad del optometrista: "))
                        if edad <= 0:
                            raise ValueError ("Error en edad!!!")
                        break
                    except ValueError as e:
                         print("Error", e)
                while True:
                    try: 
                        telefono = input("Ingresa el número telefónico del optometrista: ") 
                        if not telefono.strip().isdigit():
                            raise ValueError ("Error en Telefono")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                while True: 
                    try:
                        direccion = input("Ingresa la dirección del del domicilio del optometrista: ")
                        if not direccion.replace(" ", ""):
                            raise ValueError("Error en direccion")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                while True:
                    try:
                        cedula = input("Ingresa la cédula del optometrista: ")
                        if not cedula.replace(" ", ""):
                            raise ValueError ("Erroe en cedula")
                        break
                    except ValueError as e:
                        print("Error", e)
                while True:
                    try:
                        especialidad = input("Ingresa la especialidad del optometrista: ")
                        if not especialidad.replace(" ", ""):
                            raise ValueError ("Error en especialidad")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                optometrista = Optometrista(nombre,edad, telefono, direccion, cedula, especialidad)
                optometristas.append(optometrista)
                print("Optometrista registrado exitosamente.")
            case 3:
                while True:
                    try:
                        nombre = input("Ingresa el nombre del lente: ")
                        if not nombre.replace(" ", "").isalpha():
                            raise ValueError ("Error en nombre")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                while True:
                    try:
                        codigo = input("Ingersa el código del lente: ")
                        if not codigo.replace(' ', ''):
                            raise ValueError("Error en codigo")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                    
                while True:
                    try:
                        precio = float(input("Ingresa el precio del lente: "))
                        if precio <= 0:
                            raise ValueError ("Error en precio")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        stock = int(input("Ingresa el stock del lente: "))
                        if stock <= 0:
                            raise ValueError ("Error en stock")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        graduacion = input("Ingresa la graduación del lente: ")
                        if not graduacion.strip():
                            raise ValueError("Error en graduacion")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        material = input("Ingresa de que material es el lente: ")
                        if not material.replace(" ", "").isalpha():
                            raise ValueError ("Error en material")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                filtro = input("¿Tiene filtro azul? (si/no): ")
                filtroAzul = False
                if filtro.lower() == "si":
                    filtroAzul = True
                lente = Lente(nombre, codigo, precio, stock, graduacion, material, filtroAzul)
                productos.append(lente)
                print("Lente registrado exitosamente.")
            case 4:
                while True:
                    try:
                        nombre = input("Ingresa el nombre del armazon: ")
                        if not nombre.replace(" ", "").isalpha():
                            raise ValueError ("Error en nombre")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                while True:
                    try:
                        codigo = input("Ingersa el código del armazon: ")
                        if not codigo.replace(' ', ''):
                            raise ValueError("Error en codigo")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                    
                while True:
                    try:
                        precio = float(input("Ingresa el precio del armazon: "))
                        if precio <= 0:
                            raise ValueError ("Error en precio")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        stock = int(input("Ingresa el stock del armazon: "))
                        if stock <= 0:
                            raise ValueError ("Error en stock")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                    
                while True:
                    try:
                        marca = input("Ingresa la marca del armazón: ")
                        if not marca.replace(" ", ""):
                            raise ValueError ("Error en marca")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                
                while True: 
                    try:
                        color = input("Ingresa el color: ")
                        if not color.replace(" ", "").isalpha():
                            raise ValueError("Error en color")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        material = input("Ingresa de que material es el armazón: ")
                        if not material.replace(" ", "").isalpha():
                            raise ValueError ("Error en material")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                    
                armazon = Armazon(nombre, codigo, precio, stock, marca, color, material)
                productos.append(armazon)
                print("Armazón registrado exitosamente.")
            case 5:
                while True:
                    try:
                        nombre = input("Ingresa el nombre del accesorio: ")
                        if not nombre.replace(" ", "").isalpha():
                            raise ValueError ("Error en nombre")
                        break
                    except ValueError as e:
                        print("Error", e)
                    
                while True:
                    try:
                        codigo = input("Ingersa el código del accesorio: ")
                        if not codigo.replace(' ', ''):
                            raise ValueError("Error en codigo")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                    
                while True:
                    try:
                        precio = float(input("Ingresa el precio del accesorio: "))
                        if precio <= 0:
                            raise ValueError ("Error en precio")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True:
                    try:
                        stock = int(input("Ingresa el stock del accesorio: "))
                        if stock <= 0:
                            raise ValueError ("Error en stock")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True: 
                    try:
                        tipo = input("Ingresa el tipo de accesorio: ")
                        if not tipo.replace(" ", ""):
                            raise ValueError ("Error en tipo")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                while True: 
                    try:
                        descripcion = input("Escribe la descripción del accesorio: ")
                        if not descripcion.replace(" ", ""):
                            raise ValueError ("Error en descripcion")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                
                accesorio = Accesorio(nombre, codigo, precio, stock, tipo, descripcion)
                productos.append(accesorio)
                print("Accesorio registrado exitosamente.")
            case 6:
                if len(productos) == 0:
                    print("No se ha registrado ningún producto.")
                else:
                    for producto in productos:
                        producto.mostrarProducto()
                        print(f"Costo total: ${producto.calcularPrecio()}")
            case 7:
                if not pacientes:
                    print("No hay pacientes registrados.")
                else:
                    for paciente in pacientes:
                        paciente.mostrar()
                        
                        print(f"Graduación: {paciente.graduacion}")
                        print(f"Historial: {paciente.historial}")
                        print(f"Alergias: {paciente.alergias}")           
            
            case 8:
                if not optometristas:
                    print("No hay optometristas registrados.")
                else:
                    for optometrista in optometristas:
                        optometrista.mostrar()
                        print(f"Cédula: {optometrista.cedula}")
                        print(f"Especialidad: {optometrista.especialidad}")          
            
            case 9:
                with open("productos.txt", "w") as archivo:
                    for producto in productos:
                        if isinstance(producto, Lente):
                            archivo.write(f"Lente, {producto.nombre}, {producto.codigo}, {producto.precio}, {producto.stock}, {producto.tipoGraduacion}, {producto.material}, {producto.filtroAzul}\n")
                        elif isinstance(producto, Armazon):
                            archivo.write(f"Armazon, {producto.nombre}, {producto.codigo}, {producto.precio}, {producto.stock},{producto.marca}, {producto.color}, {producto.material}\n")
                        elif isinstance(producto, Accesorio):
                            archivo.write(f"Accesorio, {producto.nombre}, {producto.codigo}, {producto.precio}, {producto.stock}, {producto.tipo}, {producto.descripcion}\n")
                print("Datos guardados exitosamente.")
            case 10:
                try:
                    with open("productos.txt", "r") as archivo:
                        for linea in archivo:
                            datos = [dato.strip() for dato in linea.strip().split(",")]
                            TipodeProducto = datos[0]
                            if TipodeProducto == "Lente":
                                producto = Lente(datos[1], datos[2], float(datos[3]), int(datos[4]), datos[5], datos[6], datos[7] == "True")
                            elif TipodeProducto == "Armazon":
                                producto = Armazon(datos[1], datos[2], float(datos[3]), int(datos[4]), datos[5], datos[6], datos[7])
                            elif TipodeProducto == "Accesorio":
                                producto = Accesorio(datos[1], datos[2], float(datos[3]), int(datos[4]), datos[5], datos[6])
                            producto.mostrarProducto()
                except FileNotFoundError:
                    print("No hay nada guardado en el archivo.")           
            case 11:
                while True:
                    try:
                        print("1. Lentes")
                        print("2. Armazones")
                        print("3. Accesorios")
                        
                        tipo = int(input("Selecciona el tipo: "))
                        if tipo <1 or tipo >3:
                            raise ValueError ("Error de tipo")
                        break
                    except ValueError as e:
                        print("Error: ", e)
                if tipo == 1:
                    for producto in productos:
                        if isinstance(producto, Lente):
                            producto.mostrarProducto()
                elif tipo == 2:
                    for producto in productos:
                        if isinstance(producto, Armazon):
                            producto.mostrarProducto()

                elif tipo == 3:
                    for producto in productos:
                        if isinstance(producto, Accesorio):
                            producto.mostrarProducto()

                else:
                    print("Tipo inválido.")
            case 12:
                    buscar = input("Ingresa nombre o código del producto: ").lower()

                    encontrado = False

                    for producto in productos:
                        if (buscar in producto.nombre.lower() or
                            buscar in producto.codigo.lower()):
                            producto.mostrarProducto()
                            encontrado = True
                    if not encontrado:
                        print("Producto no encontrado.")

            case 13:
                print("Saliendo...")
                break
         
            case _:
                print("Opción inválida.")
                
    except ValueError as e:
        print("Entrada inválida.", e)