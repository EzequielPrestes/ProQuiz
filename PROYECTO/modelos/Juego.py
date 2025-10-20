# modelos/juego.py

class Juego:
    """Modelo para representar un Juego de Trivia."""
    def __init__(self, id, titulo, tipo_juego):
        self.id = id
        self.titulo = titulo
        self.tipo_juego = tipo_juego
