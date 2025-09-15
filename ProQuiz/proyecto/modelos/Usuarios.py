class usuario:
    def __init__(self, id, nombre, email, contraseña):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.contraseña = contraseña
    def iniciar_sesion(self):
        return f"{self.nombre} ha iniciado sesión."
    def cerrar_sesion(self):
        return f"{self.nombre} ha cerrado sesión."
    
class administrador(usuario):
    def __init__(self, id, nombre, email, contraseña, nivel_acceso):
        super().__init__(id, nombre, email, contraseña)
        self.nivel_acceso = nivel_acceso
    def crear_pregunta(self, pregunta):
        return f"Administrador {self.nombre} ha creado la pregunta: {pregunta}"
    def eliminar_pregunta(self, pregunta):
        return f"Administrador {self.nombre} ha eliminado la pregunta: {pregunta}"
    def modificar_pregunta(self, pregunta):
        return f"Administrador {self.nombre} ha modificado la pregunta: {pregunta}"
    
class jugador(usuario):
    def __init__(self, id, nombre, email, contraseña, puntaje):
        super().__init__(id, nombre, email, contraseña)
        self.puntaje = puntaje
    def jugar(self):
        return f"Jugador {self.nombre} está jugando."
    def ver_puntaje(self):
        return f"Jugador {self.nombre} tiene un puntaje de {self.puntaje}."