# modelos/Pregunta

class Pregunta:
    def __init__(self, id, pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id):
        self.id = id
        self.pregunta = pregunta
        self.respuesta_correcta = respuesta_correcta
        self.opciones_incorrectas = [op1, op2, op3] 
        self.categoria = categoria
        self.dificultad = dificultad
        self.juego_id = juego_id