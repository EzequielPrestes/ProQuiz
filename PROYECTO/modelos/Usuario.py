# modelos/usuario.py

class Usuario:
    """Modelo para representar un Jugador y su puntaje."""
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.puntaje = 0
