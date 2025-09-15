class juego:
    def __init__(self, titulo, descripcion, estado, puntaje_total):
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado
        self.puntaje_total = puntaje_total
    def iniciar(self):
        return f"El juego {self.titulo} ha comenzado."
    def finalizar(self):
        return f"El juego {self.titulo} ha terminado con un puntaje de {self.puntaje_total}."
    def mostrar_resultados(self):
        return f"Resultados del juego {self.titulo}: {self.descripcion}, Estado: {self.estado}, Puntaje Total: {self.puntaje_total}"

class Preguntas_VoF(juego):
    def __init__(self, titulo, descripcion, estado, puntaje_total, numero_preguntas):
        super().__init__(titulo, descripcion, estado, puntaje_total)
        self.numero_preguntas = numero_preguntas
    def mostrar_preguntas(self):
        return f"El juego {self.titulo} tiene {self.numero_preguntas} preguntas de Verdadero o Falso."

class Preguntas_Multiple(juego):
    def __init__(self, titulo, descripcion, estado, puntaje_total, numero_opciones):
        super().__init__(titulo, descripcion, estado, puntaje_total)
        self.numero_opciones = numero_opciones
    def mostrar_opciones(self):
        return f"El juego {self.titulo} tiene {self.numero_opciones} opciones por pregunta."

class Selecciona_respuesta(juego):
    def __init__(self, titulo, descripcion, estado, puntaje_total):
        super().__init__(titulo, descripcion, estado, puntaje_total)
    def seleccionar_respuesta(self, respuesta):
        return f"Has seleccionado la respuesta: {respuesta} en el juego {self.titulo}."
