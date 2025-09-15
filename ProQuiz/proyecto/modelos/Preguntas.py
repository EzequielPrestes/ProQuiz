class Preguntas:
    def __init__(self, pregunta, respuesta_correcta, categoria, dificultad):
        self.pregunta = pregunta
        self.respuesta_correcta = respuesta_correcta
        self.categoria = categoria
        self.dificultad = dificultad

    def mostrar_pregunta(self):
        return f"Pregunta: {self.pregunta}"

    def verificar_respuesta(self, respuesta_usuario):
        if respuesta_usuario == self.respuesta_correcta:
            return "Respuesta correcta."
        else:
            return "Respuesta incorrecta."