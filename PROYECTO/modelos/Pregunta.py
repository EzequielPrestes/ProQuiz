# modelos/pregunta.py

class Pregunta:
    """Modelo para representar una Pregunta individual con opciones."""
    def __init__(self, id, pregunta, respuesta_correcta, juego_id, opcion_2=None, opcion_3=None, opcion_4=None):
        self.id = id
        self.pregunta = pregunta
        self.respuesta_correcta = respuesta_correcta
        self.juego_id = juego_id
        # Opciones para Multiple Choice (filtra opciones nulas)
        self.opciones_incorrectas = [o for o in [opcion_2, opcion_3, opcion_4] if o is not None]
