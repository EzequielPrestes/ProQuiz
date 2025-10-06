import mysql.connector
from tkinter import *
from tkinter import messagebox, simpledialog

# =========================
# Conexión a la base de datos "proquizz"
# =========================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="proquizz"
)
cursor = db.cursor()

# =========================
# Crear juego y preguntas de prueba si no existen
# =========================
cursor.execute("SELECT COUNT(*) FROM juegos")
if cursor.fetchone()[0] == 0:
    # Insertar juego de programación
    cursor.execute("INSERT INTO juegos (titulo, tipo_juego) VALUES ('Juego de Programacion', 'Multiple')")
    db.commit()
    juego_id = cursor.lastrowid

    # Insertar preguntas de prueba
    preguntas_prueba = [
        ('¿Qué comando imprime texto en Python?', 'print', 'Python', 'Facil'),
        ('¿Cuál es el tipo de dato de True o False?', 'bool', 'Python', 'Facil'),
        ('¿Qué operador se usa para la división entera?', '//', 'Python', 'Media'),
        ('¿Qué función devuelve la longitud de una lista?', 'len', 'Python', 'Media'),
        ('¿Cuál palabra clave se usa para crear una función?', 'def', 'Python', 'Facil'),
        ('¿Cómo se inicia un comentario en Python?', '#', 'Python', 'Facil'),
        ('¿Qué método convierte una cadena a mayúsculas?', 'upper', 'Python', 'Media'),
        ('¿Qué palabra clave se usa para manejar excepciones?', 'try', 'Python', 'Media'),
        ('¿Qué estructura de datos almacena pares clave-valor?', 'dict', 'Python', 'Media'),
        ('¿Qué bucle se usa para iterar sobre una lista?', 'for', 'Python', 'Facil')
    ]

    for p in preguntas_prueba:
        cursor.execute("INSERT INTO preguntas (pregunta, respuesta_correcta, categoria, dificultad, juego_id) VALUES (%s,%s,%s,%s,%s)",
                       (p[0], p[1], p[2], p[3], juego_id))
    db.commit()

# =========================
# Clases
# =========================
class Juego:
    def __init__(self, id, titulo, tipo_juego):
        self.id = id
        self.titulo = titulo
        self.tipo_juego = tipo_juego

class Pregunta:
    def __init__(self, id, pregunta, respuesta_correcta, juego_id):
        self.id = id
        self.pregunta = pregunta
        self.respuesta_correcta = respuesta_correcta
        self.juego_id = juego_id

class Usuario:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.puntaje = 0

# =========================
# Funciones para cargar datos
# =========================
def cargar_juegos():
    cursor.execute("SELECT id, titulo, tipo_juego FROM juegos")
    resultados = cursor.fetchall()
    return [Juego(r[0], r[1], r[2]) for r in resultados]

def cargar_preguntas(juego_id):
    cursor.execute("SELECT id, pregunta, respuesta_correcta, juego_id FROM preguntas WHERE juego_id=%s", (juego_id,))
    resultados = cursor.fetchall()
    preguntas = [Pregunta(r[0], r[1], r[2], r[3]) for r in resultados]
    print(f"Se cargaron {len(preguntas)} preguntas para el juego {juego_id}")  # <--- Depuración
    return preguntas


def guardar_usuario(nombre, puntaje):
    cursor.execute("INSERT INTO usuarios (nombre, puntaje_total) VALUES (%s,%s)", (nombre, puntaje))
    db.commit()

# =========================
# GUI
# =========================
class ProQuizzGUI:
    def __init__(self, master):
        self.master = master
        master.title("ProQuizz - Programación")
        master.geometry("600x400")

        # Pedir nombre de usuario al iniciar
        self.nombre_usuario = simpledialog.askstring("Bienvenido a ProQuizz", "Ingrese su nombre:")
        if not self.nombre_usuario:
            self.nombre_usuario = "Jugador1"
        self.usuario = Usuario(None, self.nombre_usuario)

        # Cargar juegos
        self.juegos = cargar_juegos()
        self.juego_seleccionado = None
        self.preguntas = []
        self.indice = 0

        # Widgets
        self.label_titulo = Label(master, text=f"Bienvenido, {self.usuario.nombre}. Seleccione un juego", font=("Arial", 12))
        self.label_titulo.pack(pady=10)

        self.lista_juegos = Listbox(master, width=50)
        for j in self.juegos:
            self.lista_juegos.insert(END, f"{j.titulo} ({j.tipo_juego})")
        self.lista_juegos.pack(pady=10)

        self.boton_iniciar = Button(master, text="Iniciar Juego", command=self.iniciar_juego)
        self.boton_iniciar.pack(pady=10)

        self.label_pregunta = Label(master, text="", wraplength=500, font=("Arial", 12))
        self.label_pregunta.pack(pady=20)

        self.entry_respuesta = Entry(master, font=("Arial", 12))
        self.entry_respuesta.pack(pady=10)

        self.boton_responder = Button(master, text="Responder", command=self.verificar)
        self.boton_responder.pack(pady=10)

        self.label_resultado = Label(master, text="", font=("Arial", 12))
        self.label_resultado.pack(pady=10)

    # =========================
    # Funciones de juego
    # =========================
    def iniciar_juego(self):
        seleccionado = self.lista_juegos.curselection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un juego")
            return
        self.juego_seleccionado = self.juegos[seleccionado[0]]
        self.preguntas = cargar_preguntas(self.juego_seleccionado.id)
        if not self.preguntas:
            messagebox.showinfo("Info", "No hay preguntas en este juego")
            return
        self.indice = 0
        self.usuario.puntaje = 0
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        if self.indice < len(self.preguntas):
            self.label_pregunta.config(text=self.preguntas[self.indice].pregunta)
            self.entry_respuesta.delete(0, END)
            self.label_resultado.config(text="")
        else:
            # Guardar puntaje del usuario en la DB
            guardar_usuario(self.usuario.nombre, self.usuario.puntaje)
            messagebox.showinfo("Fin del juego", f"Juego terminado! Puntaje: {self.usuario.puntaje}")
            self.label_pregunta.config(text="")
            self.entry_respuesta.delete(0, END)
            self.label_resultado.config(text="")

    def verificar(self):
        respuesta = self.entry_respuesta.get()
        correcta = self.preguntas[self.indice].respuesta_correcta
        if respuesta.strip().lower() == correcta.strip().lower():
            self.usuario.puntaje += 10
            self.label_resultado.config(text="¡Correcto! +10 puntos", fg="green")
        else:
            self.label_resultado.config(text=f"Incorrecto! La respuesta era: {correcta}", fg="red")
        self.indice += 1
        self.master.after(1500, self.mostrar_pregunta)

# =========================
# Ejecutar GUI
# =========================
root = Tk()
app = ProQuizzGUI(root)
root.mainloop()
