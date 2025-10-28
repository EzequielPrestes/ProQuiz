'''import mysql.connector
from tkinter import *
from tkinter import messagebox, simpledialog
import sys
import hashlib
import os
import random

# =========================
# Configuración de la Base de Datos
# =========================
# ADVERTENCIA: Por favor, asegúrate de que MySQL esté corriendo
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "proquizz"
}

try:
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Error de Conexión a la Base de Datos: {err}")
    print("Asegúrate de que el servidor MySQL esté corriendo y las credenciales sean correctas.")
    sys.exit(1)

# Función simple para hashear contraseñas (sin librerías externas como bcrypt)
def hashear_password(password):
    """Devuelve el hash SHA256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# Inicialización de la Base de Datos
# (Se limpia y se recrea para evitar conflictos de Foreign Key)
# =========================

def inicializar_db():
    """Limpia, crea las tablas necesarias y añade datos de prueba."""
    try:
        print("Iniciando verificación y creación de la base de datos...")
        
        # Deshabilitar verificación de Foreign Keys temporalmente para permitir DROP TABLE
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # 1. Eliminar tablas en orden inverso de dependencia (hijos primero)
        cursor.execute("DROP TABLE IF EXISTS puntajes")
        cursor.execute("DROP TABLE IF EXISTS preguntas")
        cursor.execute("DROP TABLE IF EXISTS usuarios")
        cursor.execute("DROP TABLE IF EXISTS juegos")

        # 2. Crear tablas limpias

        # Tabla de juegos (PADRE 1)
        cursor.execute("""
            CREATE TABLE juegos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL UNIQUE,
                tipo_juego VARCHAR(50) -- 'Abierta' o 'Multiple'
            )
        """)
        
        # Tabla de usuarios (PADRE 2)
        cursor.execute("""
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE, 
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        
        # Tabla de preguntas (HIJA de juegos) - Ahora con opciones incorrectas para Multiple Choice
        cursor.execute("""
            CREATE TABLE preguntas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pregunta TEXT NOT NULL,
                respuesta_correcta VARCHAR(255) NOT NULL,
                opcion_incorrecta_1 VARCHAR(255),
                opcion_incorrecta_2 VARCHAR(255),
                opcion_incorrecta_3 VARCHAR(255),
                categoria VARCHAR(100),
                dificultad VARCHAR(50),
                juego_id INT,
                FOREIGN KEY (juego_id) REFERENCES juegos(id)
            )
        """)
        
        # Tabla de puntajes (HIJA de usuarios)
        cursor.execute("""
            CREATE TABLE puntajes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                puntaje INT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Habilitar verificación de Foreign Keys
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 3. Insertar datos de prueba
        
        # JUEGO 1: RESPUESTA ABIERTA (Python Básico)
        JUEGO_TITULO_ABIERTA = 'Juego de Python (Abierta)'
        cursor.execute("INSERT INTO juegos (titulo, tipo_juego) VALUES (%s, %s)", (JUEGO_TITULO_ABIERTA, 'Abierta'))
        db.commit()
        juego_id_abierta = cursor.lastrowid
        
        # JUEGO 2: MULTIPLE CHOICE (Programación General)
        JUEGO_TITULO_MULTIPLE = 'Juego de Programación (Multiple)'
        cursor.execute("INSERT INTO juegos (titulo, tipo_juego) VALUES (%s, %s)", (JUEGO_TITULO_MULTIPLE, 'Multiple'))
        db.commit()
        juego_id_multiple = cursor.lastrowid

        # Preguntas para MODO ABIERTA
        preguntas_abiertas = [
            ('¿Qué comando imprime texto en Python?', 'print', None, None, None, 'Python', 'Facil', juego_id_abierta),
            ('¿Cuál es el tipo de dato de True o False?', 'bool', None, None, None, 'Python', 'Facil', juego_id_abierta),
            ('¿Qué operador se usa para la división entera?', '//', None, None, None, 'Python', 'Media', juego_id_abierta),
            ('¿Qué función devuelve la longitud de una lista?', 'len', None, None, None, 'Python', 'Media', juego_id_abierta),
            ('¿Cuál palabra clave se usa para crear una función?', 'def', None, None, None, 'Python', 'Facil', juego_id_abierta),
        ]
        
        # Preguntas para MODO MULTIPLE (Programación)
        preguntas_multiple = [
            ('¿Qué significa HTML?', 'HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Management Logic', 'Hyperlink and Text Markup Language', 'Web', 'Facil', juego_id_multiple),
            ('¿Cuál de estos es un lenguaje de programación orientado a objetos?', 'Java', 'SQL', 'Bash', 'CSS', 'Programacion', 'Media', juego_id_multiple),
            ('En Python, ¿qué estructura se usa para iterar sobre una secuencia?', 'for loop', 'while loop', 'do-while loop', 'switch statement', 'Python', 'Facil', juego_id_multiple),
            ('¿Qué es un bucle infinito?', 'Un bucle que nunca termina su ejecución.', 'Un bucle que se repite 100 veces.', 'Un bucle que se ejecuta solo una vez.', 'Un bucle que tiene múltiples condiciones de salida.', 'Conceptos', 'Media', juego_id_multiple),
            ('¿Qué es un repositorio en Git?', 'Una carpeta donde se almacena el historial de cambios de un proyecto.', 'Un servidor para ejecutar código en la nube.', 'Una herramienta para compilar código C++.', 'Un programa para dibujar diagramas de flujo.', 'Herramientas', 'Media', juego_id_multiple),
        ]
        
        for p in preguntas_abiertas + preguntas_multiple:
            cursor.execute("""
                INSERT INTO preguntas 
                (pregunta, respuesta_correcta, opcion_incorrecta_1, opcion_incorrecta_2, opcion_incorrecta_3, categoria, dificultad, juego_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, p)
        
        # Crear un usuario de prueba para poder hacer Login rápido
        password_hash = hashear_password("12345")
        cursor.execute("INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)", 
                       ("admin", "admin@proquizz.com", password_hash))
                       
        db.commit()
        print("Base de datos inicializada y datos de prueba insertados con éxito.")
    
    except mysql.connector.Error as err:
        messagebox.showerror("Error de DB", f"Error al inicializar la base de datos: {err}")
        sys.exit(1)
        
inicializar_db()

# =========================
# Modelos de Datos
# =========================
class Pregunta:
    """Representa una pregunta del quiz con su respuesta y opciones."""
    def __init__(self, id, pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad):
        self.id = id
        self.pregunta = pregunta
        self.respuesta_correcta = respuesta_correcta
        
        # Las opciones incorrectas se almacenan como lista (puede contener None para modo Abierta)
        self.opciones_incorrectas = [op1, op2, op3] 
        
        self.categoria = categoria
        self.dificultad = dificultad

class Usuario:
    """Representa al usuario logueado."""
    def __init__(self, db_id, nombre, email, puntaje=0):
        self.db_id = db_id
        self.nombre = nombre
        self.email = email
        self.puntaje = puntaje

# =========================
# Funciones de Base de Datos para Auth y Juego
# =========================
# ... (Funciones DB: obtener_juegos, registrar_usuario_db, verificar_login_db, cargar_preguntas, guardar_puntaje, cargar_mejores_puntajes)
# Las funciones de DB no necesitan cambios, solo se incluye su nombre para referencia.

def obtener_juegos():
    """Carga todos los juegos disponibles (título y tipo) desde la DB."""
    try:
        cursor.execute("SELECT titulo, tipo_juego FROM juegos")
        return cursor.fetchall()
    except mysql.connector.Error as err:
        messagebox.showerror("Error de DB", f"Error al cargar juegos: {err}")
        return []

def registrar_usuario_db(nombre, email, password):
    """Registra un nuevo usuario en la base de datos."""
    try:
        password_hash = hashear_password(password)
        cursor.execute("INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)",
                       (nombre, email, password_hash))
        db.commit()
        return True
    except mysql.connector.IntegrityError as err:
        messagebox.showerror("Error de Registro", "El nombre de usuario o email ya están en uso.")
        return False
    except mysql.connector.Error as err:
        messagebox.showerror("Error de DB", f"Error al registrar usuario: {err}")
        return False

def verificar_login_db(email, password):
    """Verifica credenciales y devuelve un objeto Usuario si es válido."""
    try:
        cursor.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = %s", (email,))
        resultado = cursor.fetchone()
        
        if resultado:
            usuario_id, nombre, hash_almacenado = resultado
            password_hash_ingresado = hashear_password(password)
            
            if password_hash_ingresado == hash_almacenado:
                return Usuario(usuario_id, nombre, email)
        
        return None
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error de DB", f"Error al verificar login: {err}")
        return None

def cargar_preguntas(juego_titulo):
    """Carga las preguntas para un juego específico desde la DB."""
    try:
        query = """
            SELECT p.id, p.pregunta, p.respuesta_correcta, 
                   p.opcion_incorrecta_1, p.opcion_incorrecta_2, p.opcion_incorrecta_3,
                   p.categoria, p.dificultad
            FROM preguntas p
            JOIN juegos j ON p.juego_id = j.id
            WHERE j.titulo = %s
        """
        cursor.execute(query, (juego_titulo,))
        resultados = cursor.fetchall()
        # Mapeamos los resultados a objetos Pregunta
        preguntas = [Pregunta(*res) for res in resultados]
        return preguntas
    except mysql.connector.Error as err:
        print(f"Error al cargar preguntas: {err}")
        return []

def guardar_puntaje(usuario_id, puntaje):
    """Registra el puntaje en la DB."""
    try:
        cursor.execute("INSERT INTO puntajes (usuario_id, puntaje) VALUES (%s, %s)", (usuario_id, puntaje))
        db.commit()
        
    except mysql.connector.Error as err:
        print(f"Error al guardar puntaje: {err}")
        messagebox.showerror("Error de DB", f"No se pudo guardar el puntaje: {err}")

def cargar_mejores_puntajes():
    """Carga los 5 mejores puntajes de la DB."""
    try:
        query = """
            SELECT u.nombre, p.puntaje
            FROM puntajes p
            JOIN usuarios u ON p.usuario_id = u.id
            ORDER BY p.puntaje DESC, p.fecha ASC
            LIMIT 5
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error al cargar puntajes: {err}")
        return []


# =========================
# Aplicación Principal Tkinter
# =========================
class ProQuizzApp:
    """Clase principal de la aplicación ProQuizz con interfaz Tkinter."""
    def __init__(self, root):
        self.root = root
        self.root.title("ProQuizz - Sistema de Quiz")
        self.root.geometry("600x600")
        self.root.configure(bg="#e0f7fa")
        
        self.usuario = None
        self.preguntas = []
        self.indice = 0
        self.juego_actual_titulo = None 
        self.juego_actual_tipo = None 
        self.opcion_seleccionada = StringVar() # Variable para Multiple Choice

        # Contenedor principal que se usa para cambiar de vista
        self.current_frame = None 
        self.mostrar_login_registro() # Empezamos por la pantalla de login/registro
        
    def limpiar_frame(self):
        """Destruye el frame actual para cambiar de vista."""
        if self.current_frame:
            self.current_frame.destroy()

    # ====================================================================
    # Pantalla de Login y Registro
    # ====================================================================
    def mostrar_login_registro(self):
        self.limpiar_frame()
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#e0f7fa")
        self.current_frame.pack(expand=True, fill="both")

        Label(self.current_frame, text="PROQUIZZ", font=("Arial", 24, "bold"), bg="#e0f7fa", fg="#004d40").pack(pady=(0, 30))
        
        # Variables de entrada
        self.email_var = StringVar()
        self.password_var = StringVar()
        self.nombre_var = StringVar()
        
        # --- Campos ---
        Label(self.current_frame, text="Email:", bg="#e0f7fa").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.email_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Contraseña:", bg="#e0f7fa").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.password_var, show="*", font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Nombre (Solo para Registro):", bg="#e0f7fa").pack(pady=(20, 0))
        Entry(self.current_frame, textvariable=self.nombre_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)

        # --- Botones ---
        button_frame = Frame(self.current_frame, bg="#e0f7fa")
        button_frame.pack(pady=30)
        
        Button(button_frame, text="Login", command=self.handle_login, 
               font=("Arial", 12, "bold"), bg="#ff6f00", fg="white", padx=20, pady=10, relief="raised").pack(side=LEFT, padx=10)
        
        Button(button_frame, text="Registrarse", command=self.handle_registro, 
               font=("Arial", 12, "bold"), bg="#00838f", fg="white", padx=20, pady=10, relief="raised").pack(side=LEFT, padx=10)

    def handle_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Faltan datos", "Por favor, ingresa tu email y contraseña.")
            return

        usuario_obj = verificar_login_db(email, password)
        
        if usuario_obj:
            self.usuario = usuario_obj
            messagebox.showinfo("Éxito", f"¡Bienvenido, {self.usuario.nombre}!")
            self.mostrar_seleccion_juego() # Pasa a la pantalla de selección
        else:
            messagebox.showerror("Error de Login", "Email o contraseña incorrectos.")

    def handle_registro(self):
        nombre = self.nombre_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not nombre or not email or not password:
            messagebox.showwarning("Faltan datos", "Para registrarte, debes ingresar Nombre, Email y Contraseña.")
            return

        if registrar_usuario_db(nombre, email, password):
            messagebox.showinfo("Éxito", "¡Registro exitoso! Ya puedes iniciar sesión.")
            # Limpiar campos después del registro
            self.email_var.set(email)
            self.password_var.set("")
            self.nombre_var.set("")
    
    def cerrar_sesion(self):
        self.usuario = None
        messagebox.showinfo("Cerrar Sesión", "Sesión cerrada con éxito.")
        self.mostrar_login_registro()

    # ====================================================================
    # Pantalla de Selección de Juego
    # ====================================================================
    def mostrar_seleccion_juego(self):
        self.limpiar_frame()
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#e0f7fa")
        self.current_frame.pack(expand=True, fill="both")

        Label(self.current_frame, text="SELECCIONA UN JUEGO", font=("Arial", 20, "bold"), bg="#e0f7fa", fg="#004d40").pack(pady=(0, 30))
        
        juegos_disponibles = obtener_juegos()
        
        if not juegos_disponibles:
            Label(self.current_frame, text="No hay juegos disponibles.", bg="#e0f7fa").pack(pady=20)
            return

        for titulo, tipo in juegos_disponibles:
            Button(self.current_frame, 
                   text=f"{titulo} (Modo: {tipo.capitalize()})", 
                   command=lambda t=titulo, tp=tipo: self.iniciar_juego_quiz(t, tp), 
                   font=("Arial", 12, "bold"), bg="#4db6ac", fg="white", padx=30, pady=15, relief="raised"
            ).pack(pady=10, fill="x")
            
        Button(self.current_frame, text="Cerrar Sesión", command=self.cerrar_sesion, 
               font=("Arial", 10), bg="#d32f2f", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)


    # ====================================================================
    # Pantalla del Quiz
    # ====================================================================
    
    def iniciar_juego_quiz(self, titulo, tipo):
        """Prepara y comienza un nuevo juego de quiz."""
        self.juego_actual_titulo = titulo
        self.juego_actual_tipo = tipo
        self.preguntas = cargar_preguntas(titulo)
        
        if not self.preguntas:
            messagebox.showinfo("Info", f"No hay preguntas disponibles para el juego: {titulo}.")
            self.mostrar_seleccion_juego()
            return
            
        self.indice = 0
        self.usuario.puntaje = 0
        self.mostrar_juego_quiz() # Carga la vista del juego

    def mostrar_juego_quiz(self):
        self.limpiar_frame()
        
        main_frame = Frame(self.root, padx=30, pady=30, bg="#e0f7fa")
        main_frame.pack(expand=True, fill="both")
        self.current_frame = main_frame
        
        # Referencias para elementos de respuesta
        self.entry_respuesta = None
        self.opciones_frame = None
        self.opcion_seleccionada.set(None)
        self.botones_opcion = []

        # Referencias a botones para habilitar/deshabilitar
        self.boton_verificar = None 
        
        # Título del juego y Bienvenida
        Label(main_frame, text=f"Juego: {self.juego_actual_titulo}", 
              font=("Arial", 18, "bold"), bg="#e0f7fa", fg="#5e35b1").pack(pady=(0, 10))
              
        self.label_bienvenida = Label(main_frame, text=f"Jugador: {self.usuario.nombre}", 
                                      font=("Arial", 14), bg="#e0f7fa", fg="#004d40")
        self.label_bienvenida.pack(pady=(0, 15))
        
        # Etiqueta de Puntaje
        self.label_puntaje = Label(main_frame, text=f"Puntaje: {self.usuario.puntaje}", 
                                   font=("Arial", 12, "italic"), bg="#e0f7fa", fg="#004d40")
        self.label_puntaje.pack(pady=5)

        # Marco para la Pregunta (estilizado como tarjeta)
        pregunta_frame = Frame(main_frame, bg="#ffffff", bd=2, relief="groove", padx=15, pady=15)
        pregunta_frame.pack(pady=10, fill="x")
        
        self.label_pregunta = Label(pregunta_frame, text="Cargando Preguntas...", 
                                    font=("Arial", 12), wraplength=500, justify=CENTER, bg="#ffffff", fg="#333333")
        self.label_pregunta.pack(fill="x")
        
        # Marco para las Opciones/Respuesta (depende del tipo de juego)
        self.respuesta_area_frame = Frame(main_frame, bg="#e0f7fa")
        self.respuesta_area_frame.pack(pady=10, fill="x")
        
        # Resultado (Correcto/Incorrecto)
        self.label_resultado = Label(main_frame, text="", font=("Arial", 12), bg="#e0f7fa")
        self.label_resultado.pack(pady=10)

        # --- Marcos de Botones (Separados para orden) ---
        
        # 1. Botones de Control de Juego
        button_frame_control = Frame(main_frame, bg="#e0f7fa")
        button_frame_control.pack(pady=10)

        self.boton_verificar = Button(button_frame_control, text="Verificar Respuesta", command=self.verificar, 
               font=("Arial", 10, "bold"), bg="#ff6f00", fg="white", padx=10, pady=5, relief="raised")
        self.boton_verificar.pack(side=LEFT, padx=5)
               
        Button(button_frame_control, text="Siguiente Pregunta", command=self.siguiente_pregunta, 
               font=("Arial", 10), bg="#00838f", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)
               
        # 2. Botones de Navegación/Sesión (NUEVO: Cerrar Sesión)
        button_frame_nav = Frame(main_frame, bg="#e0f7fa")
        button_frame_nav.pack(pady=5)
               
        Button(button_frame_nav, text="Volver a Selección", command=self.mostrar_seleccion_juego, 
               font=("Arial", 10), bg="#7cb342", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)
               
        Button(button_frame_nav, text="Cerrar Sesión", command=self.cerrar_sesion, 
               font=("Arial", 10), bg="#d32f2f", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)


        # Marco para Mejores Puntajes
        Button(main_frame, text="Actualizar Puntajes", command=self.mostrar_puntajes, 
               font=("Arial", 9), bg="#5e35b1", fg="white", padx=8, pady=3).pack(pady=(15, 5))
        
        self.puntajes_frame = Frame(main_frame, bg="#ffffff", bd=1, relief="solid", padx=10, pady=10)
        self.puntajes_frame.pack(pady=10, fill="x")
        Label(self.puntajes_frame, text="--- TOP 5 MEJORES PUNTAJES ---", 
              font=("Arial", 10, "underline"), bg="#ffffff", fg="#5e35b1").pack(pady=5)
        
        self.labels_puntajes = []
        for i in range(5):
            label = Label(self.puntajes_frame, text="", bg="#ffffff", fg="#333333")
            label.pack()
            self.labels_puntajes.append(label)
        
        self.mostrar_puntajes() 
        self.mostrar_pregunta() 

    def mostrar_pregunta(self):
        """Muestra la pregunta actual o el mensaje de fin de juego."""
        
        # Limpiar área de respuesta anterior
        for widget in self.respuesta_area_frame.winfo_children():
            widget.destroy()
        self.botones_opcion = []
        self.opcion_seleccionada.set(None) # Resetear selección
        
        if self.indice < len(self.preguntas):
            pregunta_obj = self.preguntas[self.indice]
            self.label_pregunta.config(text=f"Pregunta {self.indice + 1}/{len(self.preguntas)}:\n{pregunta_obj.pregunta}")
            self.label_resultado.config(text="")
            
            # --- Lógica de Interfaz Dinámica ---
            if self.juego_actual_tipo == 'Abierta':
                # Modo Respuesta Abierta (Entry Box)
                self.entry_respuesta = Entry(self.respuesta_area_frame, font=("Arial", 12), width=50, bd=2, relief="flat")
                self.entry_respuesta.pack(ipady=5, padx=10)
                self.entry_respuesta.bind("<Return>", lambda event: self.verificar())
                self.entry_respuesta.focus_set()

            elif self.juego_actual_tipo == 'Multiple':
                # Modo Opción Múltiple (Radio Buttons)
                opciones = [pregunta_obj.respuesta_correcta] + [op for op in pregunta_obj.opciones_incorrectas if op is not None]
                random.shuffle(opciones) # Mezclar las opciones

                self.opciones_frame = Frame(self.respuesta_area_frame, bg="#e0f7fa")
                self.opciones_frame.pack(fill="x", padx=20)
                
                for i, opcion in enumerate(opciones):
                    radio = Radiobutton(self.opciones_frame, 
                                        text=opcion, 
                                        variable=self.opcion_seleccionada, 
                                        value=opcion, 
                                        font=("Arial", 11),
                                        bg="#e0f7fa", 
                                        activebackground="#b2ebf2", 
                                        anchor="w",
                                        justify=LEFT)
                    radio.pack(pady=5, fill="x")
                    self.botones_opcion.append(radio)
                    
            # Habilitar botones y entradas
            if self.entry_respuesta: self.entry_respuesta.config(state='normal')
            if self.boton_verificar: self.boton_verificar.config(state='normal')
            for btn in self.botones_opcion: btn.config(state='normal')
            
        else:
            # Fin del juego
            self._finalizar_juego()

    def _finalizar_juego(self):
        # Deshabilitar entradas/opciones
        if self.entry_respuesta: self.entry_respuesta.config(state='disabled')
        if self.boton_verificar: self.boton_verificar.config(state='disabled') 
        for btn in self.botones_opcion: btn.config(state='disabled')
        
        # Guardar puntaje del usuario en la DB
        guardar_puntaje(self.usuario.db_id, self.usuario.puntaje)
        
        messagebox.showinfo("Fin del juego", 
                            f"¡Juego terminado, {self.usuario.nombre}! Puntaje final: {self.usuario.puntaje} puntos.")
        
        self.label_pregunta.config(text="Juego terminado. Usa 'Volver a Selección' para elegir otro juego o 'Cerrar Sesión'.")
        self.label_resultado.config(text="")
        
        # Limpiar área de respuesta (solo si es Abierta)
        if self.entry_respuesta: self.entry_respuesta.delete(0, END)
        
        self.mostrar_puntajes() 

    def verificar(self):
        """Verifica la respuesta del usuario según el modo de juego."""
        if not self.preguntas or self.indice >= len(self.preguntas):
            return
        
        pregunta_obj = self.preguntas[self.indice]
        correcta = pregunta_obj.respuesta_correcta
        respuesta_usuario = None

        if self.juego_actual_tipo == 'Abierta':
            if not self.entry_respuesta or self.entry_respuesta.cget('state') == 'disabled': return
            respuesta_usuario = self.entry_respuesta.get().strip().lower()
            correcta_check = correcta.strip().lower()

        elif self.juego_actual_tipo == 'Multiple':
            respuesta_usuario = self.opcion_seleccionada.get()
            if not respuesta_usuario:
                messagebox.showwarning("Falta Selección", "Debes seleccionar una opción antes de verificar.")
                return
            correcta_check = correcta # En Multiple Choice, la comparación es exacta

        # Evaluación
        if respuesta_usuario == correcta_check:
            self.usuario.puntaje += 10
            self.label_resultado.config(text="¡Respuesta Correcta! (+10 puntos)", fg="green")
        else:
            self.label_resultado.config(text=f"Incorrecto. La respuesta era: {correcta}", fg="red")
            
        self.label_puntaje.config(text=f"Puntaje de {self.usuario.nombre}: {self.usuario.puntaje}")
        
        # Deshabilitar interacción después de verificar
        if self.entry_respuesta: self.entry_respuesta.config(state='disabled')
        if self.boton_verificar: self.boton_verificar.config(state='disabled')
        for btn in self.botones_opcion: btn.config(state='disabled')

    def siguiente_pregunta(self):
        """Avanza a la siguiente pregunta."""
        
        # Asegurarse de que se respondió la pregunta actual antes de avanzar
        if self.indice < len(self.preguntas) and self.boton_verificar and self.boton_verificar.cget('state') == 'normal':
             messagebox.showwarning("Atención", "Verifica tu respuesta antes de pasar a la siguiente pregunta.")
             return
            
        self.indice += 1
        self.mostrar_pregunta()

    def mostrar_puntajes(self):
        """Actualiza la visualización de los mejores puntajes."""
        puntajes = cargar_mejores_puntajes()
        
        for i, label in enumerate(self.labels_puntajes):
            if i < len(puntajes):
                nombre, puntaje = puntajes[i]
                label.config(text=f"{i+1}. {nombre}: {puntaje} puntos", fg="#004d40", font=("Arial", 10, "bold"))
            else:
                label.config(text=f"{i+1}. ---", fg="#9e9e9e", font=("Arial", 10))

# =========================
# Bucle Principal de Tkinter
# =========================
if __name__ == "__main__":
    root = Tk()
    app = ProQuizzApp(root)
    root.mainloop()

# Cerrar conexión de DB al salir
if 'db' in globals() and db.is_connected():
    db.close()
'''