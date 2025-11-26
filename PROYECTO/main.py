import mysql.connector
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import sys
import hashlib
import os
import random


# Importar servicios y modelos

from servicios.Bdatos import DatabaseService
from modelos.Usuario import Usuario
from modelos.Pregunta import Pregunta
from modelos.Juego import Juego


# clase theme de estetica
try:
    from servicios.Estetica import Theme 
except ImportError:
    class Theme:
        BG_MAIN = "#f0f0f0"
        FG_MAIN = "#333333"
        ACCENT = "#ff6f00"
        BUTTON_BG = "#00838f"
        SUCCESS = "#4caf50"
        ERROR = "#f44336"


# para carga de Imágenes (PIL)
try:
    from PIL import Image, ImageTk
except ImportError:
    print("ADVERTENCIA: La librería PIL (Pillow) no está instalada.")
    Image, ImageTk = None, None


# CONFIGURACIÓN DE IMAGEN DE FONDO
BACKGROUND_IMAGE_FILE = "logo.png" 


# Configuración de la Base de Datos
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "proquizz"
}


# Inicializa el servicio de base de datos
try:
    db_service = DatabaseService(DB_CONFIG)
    print("Conectado a la base de datos existente 'proquizz'")
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    sys.exit(1)


def hashear_password(password): 
    # Devuelve el hash SHA256 de la contraseña
    return hashlib.sha256(password.encode()).hexdigest()


# Funciones de Base de Datos


def obtener_juegos(): 
    #Carga todos los juegos disponibles
    return db_service.obtener_juegos()


def registrar_usuario_db(nombre, email, password):
    # Registra un nuevo usuario
    return db_service.registrar_usuario(nombre, email, password)


def verificar_login_db(email, password):
    # Verifica credenciales
    return db_service.verificar_login(email, password)


def cargar_preguntas(juego_titulo):
    # Carga las preguntas para un juego específico
    resultados = db_service.cargar_preguntas(juego_titulo)#instanciando
    
    preguntas = []
    for res in resultados:
        if len(res) >= 8:
            
            # Asegurar que todos los campos de respuesta son strings válidos.
            respuesta_correcta_str = str(res[2]).strip()
            op1_str = str(res[3]).strip()
            op2_str = str(res[4]).strip()
            op3_str = str(res[5]).strip()
            
            # Salta si no hay respuesta correcta, o asigna un placeholder si las incorrectas están vacías
            if not respuesta_correcta_str: continue 
            if not op1_str: op1_str = "Opción A"
            if not op2_str: op2_str = "Opción B"
            if not op3_str: op3_str = "Opción C"

            # Crear el objeto Pregunta
            pregunta_obj = Pregunta(
                id=res[0], pregunta=res[1], respuesta_correcta=respuesta_correcta_str,
                op1=op1_str, op2=op2_str, op3=op3_str, 
                categoria=res[6], dificultad=res[7], juego_id=res[8] if len(res) > 8 else None
            )
            
            # Asegurar que el objeto Pregunta tenga la lista 'opciones_incorrectas'
            pregunta_obj.opciones_incorrectas = [op1_str, op2_str, op3_str]
            
            preguntas.append(pregunta_obj)
    
    return preguntas


def guardar_puntaje(usuario_id, puntaje):
    # Registra el puntaje en la DB
    db_service.guardar_puntaje(usuario_id, puntaje)


def cargar_mejores_puntajes():
    # Carga los 5 mejores puntajes
    return db_service.cargar_mejores_puntajes()


# Funciones del Administrador

def obtener_todos_usuarios():
    # Obtiene todos los usuarios registrados
    return db_service.obtener_todos_usuarios()


def eliminar_usuario_db(usuario_id):
    # Elimina un usuario
    return db_service.eliminar_usuario(usuario_id)


def obtener_todas_preguntas():
    # Obtiene todas las preguntas
    return db_service.obtener_todas_preguntas()


def eliminar_pregunta_db(pregunta_id):
    # Elimina una pregunta
    return db_service.eliminar_pregunta(pregunta_id)


def crear_pregunta_db(pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id):
    # Crea una nueva pregunta
    return db_service.crear_pregunta(pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id)


def obtener_juegos_combo():
    # Obtiene juegos para combobox
    return db_service.obtener_juegos_combo()


# Aplicación Principal

class ProQuizzApp:
    # Clase principal de la aplicación ProQuizz
        
    def __init__(self, root):
        self.root = root
        self.root.title("ProQuizz - Sistema de Quiz")
        
        self.usuario = None
        self.preguntas = []
        self.indice = 0
        self.juego_actual_titulo = None 
        self.juego_actual_tipo = None 
        self.opcion_seleccionada = StringVar()

        self.background_image = None
        self.background_canvas = None
        
        self.boton_siguiente = None 
        
        # vistas principales
        self.current_frame = None 
        self.mostrar_login_registro()


    def limpiar_frame(self):
        # Destruye el frame actual para cambiar de vista
        if self.current_frame:
            self.current_frame.destroy()


    def mostrar_login_registro(self):
        self.limpiar_frame()
        
        # ventanade login
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised") 
        self.current_frame.pack(expand=True, fill="both")

        Label(self.current_frame, text="PROQUIZZ", font=("Arial", 24, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Variables de entrada
        self.email_var = StringVar()
        self.password_var = StringVar()
        self.nombre_var = StringVar()
        
        # Campos
        Label(self.current_frame, text="Email:", bg="#ffffff").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.email_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Contraseña:", bg="#ffffff").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.password_var, show="*", font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Nombre (Solo para Registro):", bg="#ffffff").pack(pady=(20, 0))
        Entry(self.current_frame, textvariable=self.nombre_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)

        # Botones
        button_frame = Frame(self.current_frame, bg="#ffffff")
        button_frame.pack(pady=30)
        
        Button(button_frame, text="Login", command=self.handle_login, 
               font=("Arial", 12, "bold"), bg="#ff6f00", fg="white", padx=20, pady=10, relief="raised").pack(side=LEFT, padx=10)
        
        Button(button_frame, text="Registrarse", command=self.handle_registro, 
               font=("Arial", 12, "bold"), bg="#00838f", fg="white", padx=20, pady=10, relief="raised").pack(side=LEFT, padx=10)


    def handle_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showwarning("Faltan datos", "Ingresa tu email y contraseña.")
            return

        usuario_obj = verificar_login_db(email, password)
        
        if usuario_obj:
            self.usuario = usuario_obj
            messagebox.showinfo("Éxito", f"¡Bienvenido, {self.usuario.nombre}!")
            self.mostrar_menu_principal() 
        else:
            messagebox.showerror("Error de Login", "Email o contraseña incorrectos.")


    def handle_registro(self):
        nombre = self.nombre_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not nombre or not email or not password:
            messagebox.showwarning("Faltan datos", "Debes ingresar Nombre, Email y Contraseña.")
            return

        if registrar_usuario_db(nombre, email, password):
            messagebox.showinfo("Éxito", "¡Registro exitoso! Ya puedes iniciar sesión.")
            self.email_var.set(email)
            self.password_var.set("")
            self.nombre_var.set("")
        else:
            messagebox.showerror("Error", "El nombre de usuario o email ya están en uso.")

    
    def cerrar_sesion(self):
        self.usuario = None
        messagebox.showinfo("Cerrar Sesión", "Sesión cerrada con éxito.")
        self.mostrar_login_registro()


    def mostrar_menu_principal(self):
        self.limpiar_frame()
        
        # ventana del menu
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")

        Label(self.current_frame, text=f"BIENVENIDO, {self.usuario.nombre}", 
              font=("Newroman", 20, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Botones
        Button(self.current_frame, text="Jugar", command=self.mostrar_seleccion_juego,
               font=("Newroman", 14, "bold"), bg="#4db6ac", fg="white", padx=30, pady=15, width=20).pack(pady=10)

        if self.usuario.es_administrador():
            Button(self.current_frame, text="Panel de Administración", command=self.mostrar_panel_administracion,
                   font=("Newroman", 14, "bold"), bg="#ff9800", fg="white", padx=30, pady=15, width=20).pack(pady=10)
        
        # Botones adicionales
        Button(self.current_frame, text="Ver Mejores Puntajes", command=self.mostrar_puntajes_admin,
               font=("Newroman", 14, "bold"), bg="#5c6bc0", fg="white", padx=30, pady=15, width=20).pack(pady=10)
        
        Button(self.current_frame, text="Cerrar Sesión", command=self.cerrar_sesion,
               font=("Newroman", 14, "bold"), bg="#f44336", fg="white", padx=30, pady=15, width=20).pack(pady=30)

        
    def mostrar_seleccion_juego(self):
        self.limpiar_frame()
        
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")
        
        Label(self.current_frame, text="SELECCIONA UN JUEGO", 
              font=("Arial", 18, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        juegos = obtener_juegos()
        
        # Contenedor para los botones de juego
        juegos_frame = Frame(self.current_frame, bg="#ffffff")
        juegos_frame.pack(pady=10, padx=10, fill="both", expand=True)

        if not juegos:
            Label(juegos_frame, text="No hay juegos disponibles.", bg="#ffffff", fg="#f44336").pack(pady=20)
        else:
            for juego in juegos:
                # La función lambda pasa el titulo y el tipo de juego (por ejemplo, 'Opción Múltiple')
                Button(juegos_frame, text=juego.titulo, 
                       command=lambda t=juego.titulo, c=juego.tipo_juego: self.iniciar_juego_quiz(t, c),
                       font=("Arial", 12), bg="#4db6ac", fg="white", padx=20, pady=10, width=25).pack(pady=5)
        
        # Botón Volver al Menú
        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal,
               font=("Arial", 12), bg="#757575", fg="white", padx=10, pady=5).pack(pady=20)


    def iniciar_juego_quiz(self, juego_titulo, juego_tipo):
        self.juego_actual_titulo = juego_titulo
    
        self.juego_actual_tipo = juego_tipo.strip().lower()
        
      
        print(f"DEBUG: Tipo de juego normalizado que se está usando: '{self.juego_actual_tipo}'")
        
        self.preguntas = cargar_preguntas(juego_titulo)
        
        if not self.preguntas:
            messagebox.showwarning("Advertencia", f"El juego '{juego_titulo}' no tiene preguntas cargadas o las preguntas son inválidas.")
            return

        self.usuario.puntaje = 0 
        self.indice = 0
        self.mostrar_juego_quiz()


    def mostrar_juego_quiz(self):
        self.limpiar_frame()
        
        main_frame = Frame(self.root, padx=30, pady=30, bg="#ffffff", bd=5, relief="raised")
        main_frame.pack(expand=True, fill="both")
        self.current_frame = main_frame 

        # Referencias
        self.entry_respuesta = None
        self.opcion_seleccionada.set("") # Importante: resetear la variable de selección
        self.botones_opcion = []
        self.boton_verificar = None 

        # Título y Bienvenida
        Label(main_frame, text=f"Juego: {self.juego_actual_titulo}", font=("Arial", 18, "bold"), bg="#ffffff", fg="#5e35b1").pack(pady=(0, 10))
        self.label_bienvenida = Label(main_frame, text=f"Jugador: {self.usuario.nombre}", font=("Arial", 14), bg="#ffffff", fg="#004d40")
        self.label_bienvenida.pack(pady=(0, 15))

        # Etiqueta de Puntaje
        self.label_puntaje = Label(main_frame, text=f"Puntaje: {self.usuario.puntaje}", font=("Arial", 12, "italic"), bg="#ffffff", fg="#004d40")
        self.label_puntaje.pack(pady=5)

        # Marco para la Pregunta
        pregunta_frame = Frame(main_frame, bg="#f0f0f0", bd=2, relief="groove", padx=15, pady=15)
        pregunta_frame.pack(pady=10, fill="x", expand=True)

        self.label_pregunta = Label(pregunta_frame, text="Cargando Preguntas...", font=("Arial", 12), wraplength=500, justify=CENTER, bg="#f0f0f0", fg="#333333")
        self.label_pregunta.pack(fill="x", expand=True)

        # Marco para las Opciones/Respuesta 
        self.respuesta_area_frame = Frame(main_frame, bg="#ffffff")
        self.respuesta_area_frame.pack(pady=10, fill="x", expand=True)

        # Marco para el resultado de la verificación
        self.label_resultado = Label(main_frame, text="", font=("Arial", 12, "bold"), bg="#ffffff")
        self.label_resultado.pack(pady=10)

        # Marco para los botones de control
        control_frame = Frame(main_frame, bg="#ffffff")
        control_frame.pack(pady=20)
        
        # Botones de Control
        self.boton_verificar = Button(control_frame, text="Verificar Respuesta", command=self.verificar,
                                      font=("Arial", 12, "bold"), bg="#4caf50", fg="white", padx=10, pady=5)
        self.boton_verificar.pack(side=LEFT, padx=10)

        self.boton_siguiente = Button(control_frame, text="Siguiente Pregunta", command=self.siguiente_pregunta,
                                      font=("Arial", 12), bg="#ff6f00", fg="white", padx=10, pady=5, state='disabled')
        self.boton_siguiente.pack(side=LEFT, padx=10)

        Button(control_frame, text="Volver a Selección", command=self.mostrar_seleccion_juego,
               font=("Arial", 12), bg="#757575", fg="white", padx=10, pady=5).pack(side=RIGHT, padx=10)

        # Cargar la primera pregunta
        self.mostrar_pregunta()


    def verificar(self):
        pregunta_actual = self.preguntas[self.indice]
        es_correcta = False

        if self.juego_actual_tipo == 'opcion multiple':
            respuesta_usuario = self.opcion_seleccionada.get().strip()
            
            if not respuesta_usuario:
                messagebox.showwarning("Atención", "Debes seleccionar una opción.")
                return
            
            es_correcta = (respuesta_usuario == pregunta_actual.respuesta_correcta)
            
        elif self.juego_actual_tipo == 'abierta':
            if not self.entry_respuesta: 
                messagebox.showwarning("Error", "No se encontró el campo de respuesta.")
                return
                
            respuesta_usuario = self.entry_respuesta.get().strip().lower()
            
            if not respuesta_usuario:
                messagebox.showwarning("Atención", "Debes escribir tu respuesta.")
                return
            
            es_correcta = (respuesta_usuario == pregunta_actual.respuesta_correcta.lower())

        
        # Lógica de Puntaje y Feedback
        if es_correcta:
            self.usuario.puntaje += 10 
            self.label_resultado.config(text="¡Respuesta Correcta!", fg="#4caf50")
        else:
            self.label_resultado.config(text=f"Respuesta Incorrecta. La correcta era: {pregunta_actual.respuesta_correcta}", fg="#f44336")

        self.label_puntaje.config(text=f"Puntaje: {self.usuario.puntaje}")
        
        # Deshabilitar botones/opciones y habilitar Siguiente
        if self.boton_verificar: self.boton_verificar.config(state='disabled')
        if self.entry_respuesta: self.entry_respuesta.config(state='disabled')
        for btn in self.botones_opcion: btn.config(state='disabled')
        
        if self.boton_siguiente:
            self.boton_siguiente.config(state='normal')


    def siguiente_pregunta(self):
        # Deshabilitar Siguiente y habilitar Verificar
        if self.boton_siguiente: self.boton_siguiente.config(state='disabled')
        if self.boton_verificar: self.boton_verificar.config(state='normal')
        
        self.indice += 1
        self.mostrar_pregunta()


    def mostrar_pregunta(self):
        # Muestra la pregunta actual o el mensaje de fin de juego.
        
        # Limpiar área de respuesta anterior
        for widget in self.respuesta_area_frame.winfo_children():
            widget.destroy()
        
        self.botones_opcion = []
        self.opcion_seleccionada.set("") # Resetear la variable de selección a una cadena vacía.
        
        if self.indice < len(self.preguntas):
            pregunta_obj = self.preguntas[self.indice]
            
            self.label_pregunta.config(text=f"Pregunta {self.indice + 1}/{len(self.preguntas)}:\n{pregunta_obj.pregunta}", 
                                       wraplength=500, justify=CENTER)
            self.label_resultado.config(text="") # Limpiar mensaje de resultado anterior
            
            # Usamos el tipo normalizado (en minúsculas y sin acento)
            if self.juego_actual_tipo == 'abierta':
                
                # --- Lógica para Respuesta Abierta ---
                self.entry_respuesta = Entry(self.respuesta_area_frame, font=("Arial", 12), width=50)
                self.entry_respuesta.pack(pady=10)
                self.entry_respuesta.config(state='normal')
                
            elif self.juego_actual_tipo == 'opcion multiple':
                
                # Lógica para Opción Múltiple
                print("DEBUG: Entrando a bloque de Opción Múltiple. Generando opciones...") 
                
                # Mezclar opciones 
                opciones_mezcladas = [pregunta_obj.respuesta_correcta] + pregunta_obj.opciones_incorrectas
                random.shuffle(opciones_mezcladas)
                
                # Opciones usando Radiobuttons
                for i, opcion in enumerate(opciones_mezcladas):
                    radio = Radiobutton(self.respuesta_area_frame, text=opcion, variable=self.opcion_seleccionada,
                                        value=opcion, command=lambda: self.label_resultado.config(text=""),
                                        font=("Arial", 11), bg="#ffffff", anchor="w")
                    
                    # Asegurar que se empaqueta correctamente
                    radio.pack(pady=5, padx=20, fill="x") 
                    self.botones_opcion.append(radio)
            
            else:
                # Caso de error final
                print(f"ERROR: Tipo de juego inválido en la base de datos: '{self.juego_actual_tipo}'")
                self.label_pregunta.config(text=f"ERROR: Tipo de juego inválido: '{self.juego_actual_tipo}'. Revisar consola.", fg="red")

        else:
            self._finalizar_juego()
            
    
    def _finalizar_juego(self):
        # Deshabilitar botones/opciones
        if self.boton_verificar: self.boton_verificar.config(state='disabled') 
        for btn in self.botones_opcion: btn.config(state='disabled')

        if self.entry_respuesta and self.entry_respuesta.winfo_exists():
            self.entry_respuesta.config(state='disabled')
            self.entry_respuesta.delete(0, END) 
        
        # Guardar puntaje
        guardar_puntaje(self.usuario.db_id, self.usuario.puntaje)
        
        messagebox.showinfo("Fin del juego", 
                            f"¡Juego terminado, {self.usuario.nombre}! Puntaje final: {self.usuario.puntaje} puntos.")
        
        self.label_pregunta.config(text="Juego terminado.")
        self.label_resultado.config(text="")
        
        self.mostrar_puntajes() 

# (Funciones de administración, puntajes y bucle principal)

    def mostrar_panel_administracion(self):
        self.limpiar_frame()
        
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")
        
        Label(self.current_frame, text="PANEL DE ADMINISTRACIÓN", 
              font=("Arial", 18, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        Button(self.current_frame, text="Gestión de Usuarios", command=self.gestionar_usuarios,
               font=("Arial", 12, "bold"), bg="#2196f3", fg="white", padx=20, pady=10, width=30).pack(pady=10)
        
        Button(self.current_frame, text="Gestión de Preguntas", command=self.gestionar_preguntas,
               font=("Arial", 12, "bold"), bg="#4caf50", fg="white", padx=20, pady=10, width=30).pack(pady=10)

        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal,
               font=("Arial", 12), bg="#757575", fg="white", padx=20, pady=10, width=30).pack(pady=30)


    def gestionar_usuarios(self):
        self.limpiar_frame()
        
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")

        Label(self.current_frame, text="GESTIÓN DE USUARIOS", font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))

        columns = ("ID", "Nombre", "Email", "Rol", "Puntaje")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.column("Nombre", width=150)
        tree.column("Email", width=200)

        tree.pack(pady=10)

        # Cargar datos
        self.actualizar_lista_usuarios(tree)

        # Botones de control
        button_frame = Frame(self.current_frame, bg="#ffffff")
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Actualizar Lista", command=lambda: self.actualizar_lista_usuarios(tree), 
               font=("Arial", 10), bg="#2196f3", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Eliminar Usuario", command=lambda: self.eliminar_usuario_seleccionado(tree),
               font=("Arial", 10), bg="#f44336", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Volver", command=self.mostrar_panel_administracion, 
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)


    def actualizar_lista_usuarios(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        usuarios = obtener_todos_usuarios()
        for usuario in usuarios:
            tree.insert("", "end", values=usuario)


    def eliminar_usuario_seleccionado(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona un usuario.")
            return

        item = seleccion[0]
        usuario_id = tree.item(item, "values")[0]
        usuario_nombre = tree.item(item, "values")[1]

        # No permitir que el admin se elimine a sí mismo
        if usuario_id == str(self.usuario.db_id):
            messagebox.showerror("Error", "No puedes eliminar tu propio usuario.")
            return

        if messagebox.askyesno("Confirmar", f"¿Seguro de eliminar a {usuario_nombre}?"):
            if eliminar_usuario_db(usuario_id):
                tree.delete(item)
                messagebox.showinfo("Éxito", "Usuario eliminado.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.")


    def gestionar_preguntas(self):
        self.limpiar_frame()
        
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")
        
        Label(self.current_frame, text="GESTIÓN DE PREGUNTAS", font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))

        # Configuración del Treeview para preguntas
        columns = ("ID", "Pregunta", "Respuesta", "Categoría", "Dificultad", "Juego")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            if col == "Pregunta":
                tree.column(col, width=250)
            elif col == "Respuesta":
                tree.column(col, width=150)
            else:
                 tree.column(col, width=100, anchor="center")

        tree.pack(pady=10)
        
        # Cargar datos
        self.actualizar_lista_preguntas(tree)

        # Botones de control
        button_frame = Frame(self.current_frame, bg="#ffffff")
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Actualizar Lista", command=lambda: self.actualizar_lista_preguntas(tree), 
               font=("Arial", 10), bg="#2196f3", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Crear Nueva", command=self.mostrar_form_crear_pregunta,
               font=("Arial", 10), bg="#4caf50", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)

        Button(button_frame, text="Eliminar Pregunta", command=lambda: self.eliminar_pregunta_seleccionada(tree),
               font=("Arial", 10), bg="#f44336", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Volver", command=self.mostrar_panel_administracion, 
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)


    def actualizar_lista_preguntas(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        preguntas = obtener_todas_preguntas() 
        for pregunta in preguntas:
            tree.insert("", "end", values=pregunta)


    def eliminar_pregunta_seleccionada(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona una pregunta.")
            return

        item = seleccion[0]
        pregunta_id = tree.item(item, "values")[0]

        if messagebox.askyesno("Confirmar", f"¿Seguro de eliminar la pregunta con ID {pregunta_id}?"):
            if eliminar_pregunta_db(pregunta_id):
                tree.delete(item)
                messagebox.showinfo("Éxito", "Pregunta eliminada.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la pregunta.")


    def mostrar_form_crear_pregunta(self):
        
        juegos = obtener_juegos_combo() 
        if not juegos:
            messagebox.showwarning("Advertencia", "Debes tener juegos creados antes de crear preguntas.")
            return

        formulario = Toplevel(self.root)
        formulario.title("Crear Nueva Pregunta")
        formulario.geometry("600x650") 
        formulario.resizable(False, False)
        
        formulario_frame = Frame(formulario, padx=20, pady=20, bg="#f5f5f5")
        formulario_frame.pack(fill="both", expand=True)

        Label(formulario_frame, text="NUEVA PREGUNTA", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="#004d40").pack(pady=(0, 20))
        
        # Variables de entrada
        pregunta_var = StringVar()
        respuesta_var = StringVar()
        op1_var = StringVar()
        op2_var = StringVar()
        op3_var = StringVar()
        categoria_var = StringVar()
        dificultad_var = StringVar(value="Facil")
        juego_var = StringVar()

        # Campos de texto
        campos = [
            ("Pregunta:", pregunta_var),
            ("Respuesta Correcta:", respuesta_var),
            ("Opción Incorrecta 1:", op1_var),
            ("Opción Incorrecta 2:", op2_var),
            ("Opción Incorrecta 3:", op3_var)
        ]
        for texto, variable in campos:
            Label(formulario_frame, text=texto, bg="#f5f5f5").pack(pady=(10, 0))
            Entry(formulario_frame, textvariable=variable, width=50).pack(pady=5)

        # Categoría
        Label(formulario_frame, text="Categoría:", bg="#f5f5f5").pack(pady=(10, 0))
        Entry(formulario_frame, textvariable=categoria_var, width=50).pack(pady=5)

        # Dificultad
        Label(formulario_frame, text="Dificultad:", bg="#f5f5f5").pack(pady=(10, 0))
        dificultad_frame = Frame(formulario_frame, bg="#f5f5f5")
        dificultad_frame.pack()
        for dificultad in ["Facil", "Media", "Dificil"]:
            Radiobutton(dificultad_frame, text=dificultad, variable=dificultad_var, value=dificultad, bg="#f5f5f5").pack(side=LEFT, padx=10)

        # Juego (Combobox)
        Label(formulario_frame, text="Juego:", bg="#f5f5f5").pack(pady=(10, 0))
        juego_combobox = ttk.Combobox(formulario_frame, textvariable=juego_var, values=[j[1] for j in juegos], state="readonly")
        juego_combobox.pack(pady=5)
        if juegos:
            juego_combobox.set(juegos[0][1])

        # Botones
        button_frame = Frame(formulario_frame, bg="#f5f5f5")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Crear Pregunta", 
               command=lambda: self.guardar_nueva_pregunta(
                   pregunta_var, respuesta_var, op1_var, op2_var, op3_var, 
                   categoria_var, dificultad_var, juego_var, juegos, formulario
               ), 
               font=("Arial", 10), bg="#4caf50", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Cancelar", command=formulario.destroy, 
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)


    def guardar_nueva_pregunta(self, pregunta_var, respuesta_var, op1_var, op2_var, op3_var, categoria_var, dificultad_var, juego_var, juegos, formulario):
        
        pregunta = pregunta_var.get().strip()
        respuesta = respuesta_var.get().strip()
        op1 = op1_var.get().strip()
        op2 = op2_var.get().strip()
        op3 = op3_var.get().strip()
        categoria = categoria_var.get().strip()
        dificultad = dificultad_var.get()
        juego_titulo = juego_var.get()

        if not all([pregunta, respuesta, op1, op2, op3, categoria, dificultad, juego_titulo]):
            messagebox.showwarning("Faltan Datos", "Todos los campos de la pregunta y opciones deben estar llenos.")
            return

        # Obtener el ID del juego
        juego_id = next((j[0] for j in juegos if j[1] == juego_titulo), None)

        if not juego_id:
             messagebox.showerror("Error", "No se encontró el ID del juego seleccionado.")
             return

        if crear_pregunta_db(pregunta, respuesta, op1, op2, op3, categoria, dificultad, juego_id):
            messagebox.showinfo("Éxito", "Pregunta creada con éxito.")
            formulario.destroy()
            
            # Buscar el Treeview para actualizar la lista de preguntas si la ventana de gestión está abierta
            try:
                # La lista de preguntas es el tercer widget del frame de gestión (índice 2)
                tree = self.current_frame.winfo_children()[2]
                if isinstance(tree, ttk.Treeview):
                    self.actualizar_lista_preguntas(tree)
            except Exception:
                # Ignorar si el panel de gestión no está abierto o la estructura ha cambiado
                pass

        else:
            messagebox.showerror("Error", "No se pudo crear la pregunta en la base de datos.")


    def mostrar_puntajes_admin(self):
        self.limpiar_frame()
        
        self.current_frame = Frame(self.root, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        self.current_frame.pack(expand=True, fill="both")
        
        Label(self.current_frame, text="MEJORES PUNTAJES GLOBALES", 
              font=("Arial", 18, "bold"), bg="#ffffff", fg="#5e35b1").pack(pady=(0, 20))
        
        # Crear etiquetas para puntajes (referencias para actualizar)
        self.labels_puntajes = []
        for i in range(5):
            label = Label(self.current_frame, text=f"{i+1}. ---", font=("Arial", 12), bg="#ffffff", fg="#9e9e9e")
            label.pack(pady=5, anchor="w")
            self.labels_puntajes.append(label)
        
        # Cargar y mostrar puntajes
        self.mostrar_puntajes()

        # Botón Volver
        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal,
               font=("Arial", 12), bg="#757575", fg="white", padx=10, pady=5).pack(pady=30)


    def mostrar_puntajes(self):
        # Actualiza la visualización de los mejores puntajes
        puntajes = cargar_mejores_puntajes()
        
        for i, label in enumerate(self.labels_puntajes):
            if i < len(puntajes):
                nombre, puntaje = puntajes[i]
                label.config(text=f"{i+1}. {nombre}: {puntaje} puntos", fg="#004d40", font=("Arial", 12, "bold"))
            else:
                label.config(text=f"{i+1}. ---", fg="#9e9e9e", font=("Arial", 12))


# Bucle Principal de Tkinter

if __name__ == "__main__":
    root = Tk()
    app = ProQuizzApp(root)
    root.mainloop()