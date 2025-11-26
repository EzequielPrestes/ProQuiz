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


# Inicializar el servicio de base de datos
try:
    db_service = DatabaseService(DB_CONFIG)
    print("Conectado a la base de datos 'proquizz'")
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
    resultados = db_service.cargar_preguntas(juego_titulo)
    
    preguntas = []
    for res in resultados:
        if len(res) >= 8:
            preguntas.append(Pregunta(
                id=res[0], pregunta=res[1], respuesta_correcta=res[2],
                op1=res[3], op2=res[4], op3=res[5], 
                categoria=res[6], dificultad=res[7], juego_id=res[8] if len(res) > 8 else None
            ))
    
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
        
        self.root.geometry("800x650") 
        self.root.minsize(600, 600) 
        
        self.usuario = None
        self.preguntas = []
        self.indice = 0
        self.juego_actual_titulo = None 
        self.juego_actual_tipo = None 
        self.opcion_seleccionada = StringVar()

        self.background_image = None
        self.background_canvas = None
        
        self.boton_siguiente = None 
        
        # Configuración del Fondo de Imagen
        if Image and ImageTk:
            try:
                original_image = Image.open(BACKGROUND_IMAGE_FILE)
                resized_image = original_image.resize((600, 600), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(resized_image)
                
                # Crear Canvas y colocar imagen
                self.background_canvas = Canvas(self.root, highlightthickness=0)
                self.background_canvas.pack(fill="both", expand=True)
                self.background_canvas.create_image(300, 300, image=self.background_image, anchor="center") 
                
                self.root.bind('<Configure>', self._on_resize)
                
            except FileNotFoundError:
                print(f"ERROR: No se encontró el archivo de imagen '{BACKGROUND_IMAGE_FILE}'.")
                self.background_canvas = None
            except Exception as e:
                print(f"ERROR: No se pudo cargar o procesar la imagen: {e}")
                self.background_canvas = None

        # vistas principales
        self.current_frame = None 
        self.current_frame_window_id = None 
        self.mostrar_login_registro()


    def _on_resize(self, event): # (tamaño de ventana)
        # centra el frame de contenido y el fondo
        if self.background_canvas:
            # Re-centrar la imagen de fondo
            self.background_canvas.coords(1, self.background_canvas.winfo_width() // 2, self.background_canvas.winfo_height() // 2)
            
            # Recentrar el frame de contenido actual
            if self.current_frame and self.current_frame_window_id:
                center_x = self.background_canvas.winfo_width() // 2
                center_y = self.background_canvas.winfo_height() // 2
                self.background_canvas.coords(self.current_frame_window_id, center_x, center_y)


    def limpiar_frame(self):
        # Destruye el frame actual para cambiar de vista
        if self.current_frame:
            if self.background_canvas and self.current_frame_window_id:
                try:
                    self.background_canvas.delete(self.current_frame_window_id)
                except TclError:
                    pass
            self.current_frame.destroy()
            self.current_frame_window_id = None


    def _get_parent_and_place_method(self):
        # Devuelve el padre y el método de colocación
        if self.background_canvas:
            parent = self.background_canvas
            
            def place_frame(frame):
                center_x = self.background_canvas.winfo_width() // 2
                center_y = self.background_canvas.winfo_height() // 2
                self.current_frame_window_id = self.background_canvas.create_window(
                    center_x, center_y, window=frame, anchor="center"
                )
            return parent, place_frame
        else:
            parent = self.root
            
            def place_frame(frame):
                frame.pack(expand=True, fill="both")
            return parent, place_frame


    def mostrar_login_registro(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()

        # ventanade login
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised") 
        place_method(self.current_frame)

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
        parent, place_method = self._get_parent_and_place_method()
        
        # ventana del menu
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text=f"BIENVENIDO, {self.usuario.nombre}", 
              font=("Newroman", 20, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Botones
        Button(self.current_frame, text="Jugar", command=self.mostrar_seleccion_juego,
               font=("Newroman", 14, "bold"), bg="#4db6ac", fg="white", padx=30, pady=15, width=20).pack(pady=10)

        if self.usuario.es_administrador():
            Button(self.current_frame, text="Panel de Administración", command=self.mostrar_panel_administracion,
                   font=("Newroman", 14, "bold"), bg="#ff9800", fg="white", padx=30, pady=15, width=20).pack(pady=10)

        Button(self.current_frame, text="Cerrar Sesión", command=self.cerrar_sesion,
               font=("Newroman", 10), bg="#d32f2f", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)

    
    def mostrar_panel_administracion(self):
        if not self.usuario.es_administrador():
            messagebox.showerror("Acceso denegado", "No tienes permisos de administrador.")
            return
            
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # ventana de administración
        self.current_frame = Frame(parent, padx=30, pady=30, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="PANEL DE ADMINISTRACIÓN", 
              font=("Arial", 18, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # botones de administración
        Button(self.current_frame, text="Gestionar Usuarios", command=self.gestionar_usuarios,
               font=("Arial", 12, "bold"), bg="#2196f3", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Gestionar Preguntas", command=self.gestionar_preguntas,
               font=("Arial", 12, "bold"), bg="#4caf50", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Crear Nueva Pregunta", command=self.crear_nueva_pregunta,
               font=("Arial", 12, "bold"), bg="#ff9800", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal,
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(pady=20)


     # Funciones de Gestión de Administrador

    def gestionar_usuarios(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame) 

        Label(self.current_frame, text="GESTIÓN DE USUARIOS", 
              font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        # Treeview de usuarios
        columns = ("ID", "Nombre", "Email", "Rol")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Email":
                 tree.column(col, width=180, minwidth=100, stretch=TRUE)
            else:
                 tree.column(col, width=80, minwidth=50, stretch=FALSE)

        tree.pack(pady=10, fill="both", expand=True) 
        
        self.actualizar_lista_usuarios(tree)
        
        # Botones de control
        button_frame = Frame(self.current_frame, bg="#ffffff")
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Eliminar Usuario", 
               command=lambda: self.eliminar_usuario_seleccionado(tree),
               font=("Arial", 10), bg="#f44336", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Actualizar Lista", 
               command=lambda: self.actualizar_lista_usuarios(tree),
               font=("Arial", 10), bg="#2196f3", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Volver", 
               command=self.mostrar_panel_administracion,
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
        parent, place_method = self._get_parent_and_place_method()
        
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="GESTIÓN DE PREGUNTAS", 
              font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        # ventana para agrega preguntas
        columns = ("ID", "Pregunta", "Respuesta", "Categoría", "Dificultad", "Juego")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Pregunta":
                 tree.column(col, width=250, minwidth=150, stretch=TRUE) 
            else:
                 tree.column(col, width=80, minwidth=50, stretch=FALSE)

        tree.pack(pady=10, fill="both", expand=True) 
        
        self.actualizar_lista_preguntas(tree)
        
        # botones de control
        button_frame = Frame(self.current_frame, bg="#ffffff")
        button_frame.pack(pady=10)
        
        Button(button_frame, text="Eliminar Pregunta", 
               command=lambda: self.eliminar_pregunta_seleccionada(tree),
               font=("Arial", 10), bg="#f44336", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Actualizar Lista", 
               command=lambda: self.actualizar_lista_preguntas(tree),
               font=("Arial", 10), bg="#2196f3", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Volver", 
               command=self.mostrar_panel_administracion,
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)


    def actualizar_lista_preguntas(self, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        preguntas = obtener_todas_preguntas()
        for pregunta in preguntas:
            pregunta_texto = pregunta[1]
            if len(pregunta_texto) > 50:
                pregunta_texto = pregunta_texto[:50] + "..."
            tree.insert("", "end", values=(
                pregunta[0], pregunta_texto, pregunta[2], 
                pregunta[6], pregunta[7], pregunta[8]
            ))


    def eliminar_pregunta_seleccionada(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona una pregunta.")
            return
        
        item = seleccion[0]
        pregunta_id = tree.item(item, "values")[0]
        pregunta_texto = tree.item(item, "values")[1]
        
        if messagebox.askyesno("Confirmar", f"¿Seguro de eliminar la pregunta: {pregunta_texto}?"):
            if eliminar_pregunta_db(pregunta_id):
                tree.delete(item)
                messagebox.showinfo("Éxito", "Pregunta eliminada.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la pregunta.")


    def crear_nueva_pregunta(self):
        # Abre un formulario para crear una nueva pregunta (apariencia)
        formulario = Toplevel(self.root)
        formulario.title("Crear Nueva Pregunta")
        formulario.geometry("500x600")
        formulario.configure(bg="#f5f5f5")
        
        # Variables del formulario
        pregunta_var = StringVar()
        respuesta_var = StringVar()
        op1_var = StringVar()
        op2_var = StringVar()
        op3_var = StringVar()
        categoria_var = StringVar(value="Python")
        dificultad_var = StringVar(value="Facil")
        juego_var = StringVar()
        
        # Cargar juegos
        juegos = obtener_juegos_combo()
        
        # Interfaz
        Label(formulario, text="CREAR NUEVA PREGUNTA", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=10)
        
        # Campos de texto
        campos = [
            ("Pregunta:", pregunta_var),
            ("Respuesta Correcta:", respuesta_var),
            ("Opción Incorrecta 1:", op1_var),
            ("Opción Incorrecta 2:", op2_var),
            ("Opción Incorrecta 3:", op3_var)
        ]
        
        for texto, variable in campos:
            Label(formulario, text=texto, bg="#f5f5f5").pack(pady=(10, 0))
            Entry(formulario, textvariable=variable, width=50).pack(pady=5)
        
        # Categoría
        Label(formulario, text="Categoría:", bg="#f5f5f5").pack(pady=(10, 0))
        Entry(formulario, textvariable=categoria_var, width=50).pack(pady=5)
        
        # Dificultad
        Label(formulario, text="Dificultad:", bg="#f5f5f5").pack(pady=(10, 0))
        dificultad_frame = Frame(formulario, bg="#f5f5f5")
        dificultad_frame.pack()
        for dificultad in ["Facil", "Media", "Dificil"]:
            Radiobutton(dificultad_frame, text=dificultad, variable=dificultad_var, 
                       value=dificultad, bg="#f5f5f5").pack(side=LEFT, padx=10)
        
        # Juego
        Label(formulario, text="Juego:", bg="#f5f5f5").pack(pady=(10, 0))
        juego_combobox = ttk.Combobox(formulario, textvariable=juego_var, values=[j[1] for j in juegos], state="readonly")
        juego_combobox.pack(pady=5)
        if juegos:
            juego_combobox.set(juegos[0][1])
        
        # Botones
        button_frame = Frame(formulario, bg="#f5f5f5")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Crear Pregunta", 
               command=lambda: self.guardar_nueva_pregunta(
                   pregunta_var, respuesta_var, op1_var, op2_var, op3_var,
                   categoria_var, dificultad_var, juego_var, juegos, formulario
               ),
               font=("Arial", 10), bg="#4caf50", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="Cancelar", 
               command=formulario.destroy,
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(side=LEFT, padx=5)


    def guardar_nueva_pregunta(self, pregunta_var, respuesta_var, op1_var, op2_var, op3_var,
                              categoria_var, dificultad_var, juego_var, juegos, formulario):
        #   Guarda la nueva pregunta en la base de datos
        if not pregunta_var.get() or not respuesta_var.get() or not juego_var.get():
            messagebox.showerror("Error", "Pregunta, respuesta correcta y juego son obligatorios.")
            return
        
        # Obtener ID del juego
        juego_id = None
        for juego in juegos:
            if juego[1] == juego_var.get():
                juego_id = juego[0]
                break
        
        if not juego_id:
            messagebox.showerror("Error", "Juego no válido.")
            return
        
        # Crear la pregunta
        if crear_pregunta_db(
            pregunta_var.get(), respuesta_var.get(),
            op1_var.get() or None, op2_var.get() or None, op3_var.get() or None,
            categoria_var.get(), dificultad_var.get(), juego_id
        ):
            messagebox.showinfo("Éxito", "Pregunta creada.")
            formulario.destroy()
        else:
            messagebox.showerror("Error", "No se pudo crear la pregunta.")


    def mostrar_seleccion_juego(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # Frame de selección
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="SELECCIONA UN JUEGO", font=("Arial", 20, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        juegos_disponibles = obtener_juegos()
        
        if not juegos_disponibles:
            Label(self.current_frame, text="No hay juegos disponibles.", bg="#ffffff").pack(pady=20)
            return

        for titulo, tipo in juegos_disponibles:
            Button(self.current_frame, 
                   text=f"{titulo} (Modo: {tipo.capitalize()})", 
                   command=lambda t=titulo, tp=tipo: self.iniciar_juego_quiz(t, tp), 
                   font=("Arial", 12, "bold"), bg="#4db6ac", fg="white", padx=30, pady=15, relief="raised"
            ).pack(pady=10, fill="x")
            
        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal, 
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)


    def iniciar_juego_quiz(self, titulo, tipo):
        # comienza un nuevo juego de quiz
        self.juego_actual_titulo = titulo
        self.juego_actual_tipo = tipo
        self.preguntas = cargar_preguntas(titulo)
        
        if not self.preguntas:
            messagebox.showinfo("Info", f"No hay preguntas para el juego: {titulo}.")
            self.mostrar_seleccion_juego()
            return
            
        self.indice = 0
        self.usuario.puntaje = 0
        self.mostrar_juego_quiz()


    def mostrar_juego_quiz(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # ventana juego principal
        main_frame = Frame(parent, padx=30, pady=30, bg="#ffffff", bd=5, relief="raised")
        place_method(main_frame)
        self.current_frame = main_frame

        # Referencias
        self.entry_respuesta = None
        self.opciones_frame = None
        self.opcion_seleccionada.set(None)
        self.botones_opcion = []
        self.boton_verificar = None 
        
        # Título y Bienvenida
        Label(main_frame, text=f"Juego: {self.juego_actual_titulo}", 
            font=("Arial", 18, "bold"), bg="#ffffff", fg="#5e35b1").pack(pady=(0, 10))
            
        self.label_bienvenida = Label(main_frame, text=f"Jugador: {self.usuario.nombre}", 
                                    font=("Arial", 14), bg="#ffffff", fg="#004d40")
        self.label_bienvenida.pack(pady=(0, 15))
        
        # Etiqueta de Puntaje
        self.label_puntaje = Label(main_frame, text=f"Puntaje: {self.usuario.puntaje}", 
                                font=("Arial", 12, "italic"), bg="#ffffff", fg="#004d40")
        self.label_puntaje.pack(pady=5)

        # Marco para la Pregunta
        pregunta_frame = Frame(main_frame, bg="#f0f0f0", bd=2, relief="groove", padx=15, pady=15)
        pregunta_frame.pack(pady=10, fill="x", expand=True) 
        
        self.label_pregunta = Label(pregunta_frame, text="Cargando Preguntas...", 
                                    font=("Arial", 12), wraplength=500, justify=CENTER, bg="#f0f0f0", fg="#333333")
        self.label_pregunta.pack(fill="x", expand=True)
        
        # Marco para las Opciones/Respuesta
        self.respuesta_area_frame = Frame(main_frame, bg="#ffffff")
        self.respuesta_area_frame.pack(pady=10, fill="x")
        
        # Resultado
        self.label_resultado = Label(main_frame, text="", font=("Arial", 12), bg="#ffffff")
        self.label_resultado.pack(pady=10)

        # Botones de Control
        button_frame_control = Frame(main_frame, bg="#ffffff")
        button_frame_control.pack(pady=10)

        self.boton_verificar = Button(button_frame_control, text="Verificar Respuesta", command=self.verificar, 
            font=("Arial", 10, "bold"), bg="#ff6f00", fg="white", padx=10, pady=5, relief="raised")
        self.boton_verificar.pack(side=LEFT, padx=5)
            
        self.boton_siguiente = Button(button_frame_control, text="Siguiente Pregunta", command=self.siguiente_pregunta, 
            font=("Arial", 10), bg="#00838f", fg="white", padx=10, pady=5, relief="raised")
        self.boton_siguiente.pack(side=LEFT, padx=5)
            
        # Botones de Navegación/Sesión
        button_frame_nav = Frame(main_frame, bg="#ffffff")
        button_frame_nav.pack(pady=5)
            
        Button(button_frame_nav, text="Volver a Selección", command=self.mostrar_seleccion_juego, 
            font=("Arial", 10), bg="#7cb342", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)
            
        Button(button_frame_nav, text="Cerrar Sesión", command=self.cerrar_sesion, 
            font=("Arial", 10), bg="#d32f2f", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)

        # Marco para Mejores Puntajes
        Button(main_frame, text="Actualizar Puntajes", command=self.mostrar_puntajes, 
            font=("Arial", 9), bg="#5e35b1", fg="white", padx=8, pady=3).pack(pady=(15, 5))
        
        self.puntajes_frame = Frame(main_frame, bg="#f0f0f0", bd=1, relief="solid", padx=10, pady=10)
        self.puntajes_frame.pack(pady=10, fill="x")
        Label(self.puntajes_frame, text="--- TOP 5 MEJORES PUNTAJES ---", 
            font=("Arial", 10, "underline"), bg="#f0f0f0", fg="#5e35b1").pack(pady=5)
        
        self.labels_puntajes = []
        for i in range(5):
            label = Label(self.puntajes_frame, text="", bg="#f0f0f0", fg="#333333")
            label.pack()
            self.labels_puntajes.append(label)
        
        self.mostrar_puntajes() 
        self.mostrar_pregunta() 


    def verificar(self):
        # Verifica la respuesta del usuario."""
        if self.indice >= len(self.preguntas):
            return
            
        pregunta_actual = self.preguntas[self.indice]
        es_correcta = False
        
        if self.juego_actual_tipo == 'Abierta':
            respuesta_usuario = self.entry_respuesta.get().strip().lower()
            es_correcta = respuesta_usuario == pregunta_actual.respuesta_correcta.lower()
        elif self.juego_actual_tipo == 'Multiple':
            respuesta_usuario = self.opcion_seleccionada.get()
            es_correcta = respuesta_usuario == pregunta_actual.respuesta_correcta
        
        if es_correcta:
            self.usuario.puntaje += 10
            self.label_resultado.config(text="¡Correcto! +10 puntos", fg="green")
        else:
            self.label_resultado.config(text=f"Incorrecto. La respuesta era: {pregunta_actual.respuesta_correcta}", fg="red")
        
        self.label_puntaje.config(text=f"Puntaje: {self.usuario.puntaje}")
        
        if self.boton_verificar:
            self.boton_verificar.config(state='disabled')


    def siguiente_pregunta(self):
        # Avanza a la siguiente pregunta
        if self.indice >= len(self.preguntas):
            if self.boton_siguiente:
                self.boton_siguiente.config(state='disabled')
            return

        self.indice += 1
        if self.boton_verificar:
            self.boton_verificar.config(state='normal')
        self.mostrar_pregunta()


    def mostrar_puntajes(self):
        # Muestra los mejores puntajes en la interfaz
        mejores = cargar_mejores_puntajes()
        for i, label in enumerate(self.labels_puntajes):
            if i < len(mejores):
                usuario, puntaje = mejores[i]
                label.config(text=f"{i+1}. {usuario}: {puntaje} puntos")
            else:
                label.config(text=f"{i+1}. ---")    


    def mostrar_pregunta(self):
        # Muestra la pregunta actual o el mensaje de fin de juego.
        
        # Limpiar área de respuesta anterior
        for widget in self.respuesta_area_frame.winfo_children():
            widget.destroy()
        self.botones_opcion = []
        self.opcion_seleccionada.set(None)
        
        if self.indice < len(self.preguntas):
            pregunta_obj = self.preguntas[self.indice]
            
            self.label_pregunta.config(text=f"Pregunta {self.indice + 1}/{len(self.preguntas)}:\n{pregunta_obj.pregunta}", wraplength=self.label_pregunta.winfo_width() or 500)
            self.label_resultado.config(text="")
            
            if self.juego_actual_tipo == 'Abierta':
                self.entry_respuesta = Entry(self.respuesta_area_frame, font=("Arial", 12), width=50)
                self.entry_respuesta.pack(ipady=5, padx=10, fill="x")
                self.entry_respuesta.bind("<Return>", lambda event: self.verificar())
                self.entry_respuesta.focus_set()

            elif self.juego_actual_tipo == 'Multiple':
                opciones = [pregunta_obj.respuesta_correcta] + [op for op in pregunta_obj.opciones_incorrectas if op is not None]
                random.shuffle(opciones)

                self.opciones_frame = Frame(self.respuesta_area_frame, bg="#ffffff")
                self.opciones_frame.pack(fill="x", padx=20)
                
                for i, opcion in enumerate(opciones):
                    radio = Radiobutton(self.opciones_frame, text=opcion, 
                                      variable=self.opcion_seleccionada, value=opcion,
                                      font=("Arial", 11), bg="#ffffff", anchor="w")
                    radio.pack(pady=5, fill="x")
                    self.botones_opcion.append(radio)
            
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


# Bucle Principal de Tkinter


if __name__ == "__main__":
    root = Tk()
    app = ProQuizzApp(root)
    root.mainloop()


    # cerrar conexion a BD al salir
    
    import mysql.connector
    try:
        mysql.connector.connect(**DB_CONFIG).close()
    except:
        pass

    
    if 'db_service' in globals():
        db_service.cerrar_db()