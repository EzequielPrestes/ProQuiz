# modelos/Usuario

class Usuario:
    def __init__(self, db_id, nombre, email, rol='usuario', puntaje=0):
        self.db_id = db_id
        self.nombre = nombre
        self.email = email
        self.rol = rol
        self.puntaje = puntaje
    
    def es_administrador(self):
        return self.rol == 'administrador'