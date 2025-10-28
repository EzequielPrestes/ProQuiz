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


# Manejo de Imágenes con PIL (Pillow)

try:
    from PIL import Image, ImageTk
except ImportError:
    print("ADVERTENCIA: La librería PIL (Pillow) no está instalada. El fondo de imagen no se mostrará.")
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
    print("Conectado a la base de datos existente 'proquizz'")
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
    sys.exit(1)

def hashear_password(password):
    """Devuelve el hash SHA256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


# Funciones de Base de Datos (usando el servicio)


def obtener_juegos():
    """Carga todos los juegos disponibles desde la DB."""
    return db_service.obtener_juegos()

def registrar_usuario_db(nombre, email, password):
    """Registra un nuevo usuario en la base de datos."""
    return db_service.registrar_usuario(nombre, email, password)

def verificar_login_db(email, password):
    """Verifica credenciales y devuelve un objeto Usuario si es válido."""
    return db_service.verificar_login(email, password)
def cargar_preguntas(juego_titulo):
    """Carga las preguntas para un juego específico desde la DB."""
    print(f"🔍 Cargando preguntas para: {juego_titulo}")  # Debug
    resultados = db_service.cargar_preguntas(juego_titulo)
    print(f"📊 Resultados obtenidos: {len(resultados)} preguntas")  # Debug
    
    # Convertir resultados a objetos Pregunta
    preguntas = []
    for res in resultados:
        # CORRECCIÓN: Verificar que tenemos suficientes elementos
        if len(res) >= 8:
            preguntas.append(Pregunta(
                id=res[0], pregunta=res[1], respuesta_correcta=res[2],
                op1=res[3], op2=res[4], op3=res[5], 
                categoria=res[6], dificultad=res[7], juego_id=res[8] if len(res) > 8 else None
            ))
    
    print(f"Preguntas convertidas: {len(preguntas)}")  # Debug
    return preguntas

def guardar_puntaje(usuario_id, puntaje):
    """Registra el puntaje en la DB."""
    db_service.guardar_puntaje(usuario_id, puntaje)

def cargar_mejores_puntajes():
    """Carga los 5 mejores puntajes de la DB."""
    return db_service.cargar_mejores_puntajes()

# =========================
# Funciones de Administrador
# =========================

def obtener_todos_usuarios():
    """Obtiene todos los usuarios registrados."""
    return db_service.obtener_todos_usuarios()

def eliminar_usuario_db(usuario_id):
    """Elimina un usuario de la base de datos."""
    return db_service.eliminar_usuario(usuario_id)

def obtener_todas_preguntas():
    """Obtiene todas las preguntas de la base de datos."""
    return db_service.obtener_todas_preguntas()

def eliminar_pregunta_db(pregunta_id):
    """Elimina una pregunta de la base de datos."""
    return db_service.eliminar_pregunta(pregunta_id)

def crear_pregunta_db(pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id):
    """Crea una nueva pregunta en la base de datos."""
    return db_service.crear_pregunta(pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id)

def obtener_juegos_combo():
    """Obtiene juegos para combobox."""
    return db_service.obtener_juegos_combo()


# Aplicación Principal Tkinter

class ProQuizzApp:
    """Clase principal de la aplicación ProQuizz con interfaz Tkinter."""
    def __init__(self, root):
        self.root = root
        self.root.title("ProQuizz - Sistema de Quiz")
        self.root.geometry("600x600")
        
        self.usuario = None
        self.preguntas = []
        self.indice = 0
        self.juego_actual_titulo = None 
        self.juego_actual_tipo = None 
        self.opcion_seleccionada = StringVar()

        # Variables para el fondo de imagen
        self.background_image = None
        self.background_canvas = None
        
        # --- Configuración del Fondo de Imagen ---
        if Image and ImageTk:
            try:
                # Usamos la variable de configuración global para la ruta
                original_image = Image.open(BACKGROUND_IMAGE_FILE)
                
                # Redimensionar la imagen para que coincida con el tamaño de la ventana (600x600)
                resized_image = original_image.resize((600, 600), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(resized_image)
                
                # Crear un Canvas en la ventana principal para sostener la imagen
                self.background_canvas = Canvas(self.root, width=600, height=600, highlightthickness=0)
                self.background_canvas.pack(fill="both", expand=True)
                # Colocar la imagen en el centro del canvas
                self.background_canvas.create_image(0, 0, image=self.background_image, anchor="nw")
                
            except FileNotFoundError:
                print(f"ERROR: No se encontró el archivo de imagen '{BACKGROUND_IMAGE_FILE}'.")
                self.background_canvas = None
            except Exception as e:
                print(f"ERROR: No se pudo cargar o procesar la imagen: {e}")
                self.background_canvas = None
        # --- Fin de Configuración de Fondo ---

        # Contenedor principal que se usa para cambiar de vista
        self.current_frame = None 
        self.mostrar_login_registro() # Empezamos por la pantalla de login/registro
        
    def limpiar_frame(self):
        """Destruye el frame actual para cambiar de vista."""
        if self.current_frame:
            self.current_frame.destroy()

    def _get_parent_and_place_method(self):
        """Devuelve el padre para el Frame y el método de colocación (pack o create_window)."""
        if self.background_canvas:
            parent = self.background_canvas
            # Función Lambda para colocar el frame en el centro del canvas (300, 300)
            def place_frame(frame):
                # El frame es colocado como una ventana dentro del canvas
                self.background_canvas.create_window(300, 300, window=frame, anchor="center")
            return parent, place_frame
        else:
            parent = self.root
            # Función Lambda para colocar con pack si no hay canvas
            def place_frame(frame):
                frame.pack(expand=True, fill="both")
            return parent, place_frame

    # ====================================================================
    # Pantalla de Login y Registro
    # ====================================================================
    def mostrar_login_registro(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()

        # Usamos un fondo blanco  para la legibilidad del texto
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised") 
        place_method(self.current_frame)

        Label(self.current_frame, text="PROQUIZZ", font=("Arial", 24, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Variables de entrada
        self.email_var = StringVar()
        self.password_var = StringVar()
        self.nombre_var = StringVar()
        
        # --- Campos ---
        Label(self.current_frame, text="Email:", bg="#ffffff").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.email_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Contraseña:", bg="#ffffff").pack(pady=(10, 0))
        Entry(self.current_frame, textvariable=self.password_var, show="*", font=("Arial", 12)).pack(ipady=5, ipadx=10)
        
        Label(self.current_frame, text="Nombre (Solo para Registro):", bg="#ffffff").pack(pady=(20, 0))
        Entry(self.current_frame, textvariable=self.nombre_var, font=("Arial", 12)).pack(ipady=5, ipadx=10)

        # --- Botones ---
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
            messagebox.showwarning("Faltan datos", "Por favor, ingresa tu email y contraseña.")
            return

        usuario_obj = verificar_login_db(email, password)
        
        if usuario_obj:
            self.usuario = usuario_obj
            messagebox.showinfo("Éxito", f"¡Bienvenido, {self.usuario.nombre}!")
            self.mostrar_menu_principal() # Cambiado a menú principal
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
        else:
            messagebox.showerror("Error", "El nombre de usuario o email ya están en uso.")
    
    def cerrar_sesion(self):
        self.usuario = None
        messagebox.showinfo("Cerrar Sesión", "Sesión cerrada con éxito.")
        self.mostrar_login_registro()

    # ====================================================================
    # Menú Principal con opciones de Administrador
    # ====================================================================
    def mostrar_menu_principal(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # Fondo blanco para el frame de selección
        self.current_frame = Frame(parent, padx=50, pady=50, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text=f"BIENVENIDO, {self.usuario.nombre}", 
              font=("Arial", 20, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Botón para jugar
        Button(self.current_frame, text="Jugar", command=self.mostrar_seleccion_juego,
               font=("Arial", 14, "bold"), bg="#4db6ac", fg="white", padx=30, pady=15, width=20).pack(pady=10)
        
        # Botón para administración (solo para admin)
        if self.usuario.es_administrador():
            Button(self.current_frame, text="Panel de Administración", command=self.mostrar_panel_administracion,
                   font=("Arial", 14, "bold"), bg="#ff9800", fg="white", padx=30, pady=15, width=20).pack(pady=10)
        
        Button(self.current_frame, text="Cerrar Sesión", command=self.cerrar_sesion, 
               font=("Arial", 10), bg="#d32f2f", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)

    # ====================================================================
    # Panel de Administración
    # ====================================================================
    def mostrar_panel_administracion(self):
        if not self.usuario.es_administrador():
            messagebox.showerror("Acceso denegado", "No tienes permisos de administrador.")
            return
            
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        self.current_frame = Frame(parent, padx=30, pady=30, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="PANEL DE ADMINISTRACIÓN", 
              font=("Arial", 18, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 30))
        
        # Botones de administración
        Button(self.current_frame, text="Gestionar Usuarios", command=self.gestionar_usuarios,
               font=("Arial", 12, "bold"), bg="#2196f3", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Gestionar Preguntas", command=self.gestionar_preguntas,
               font=("Arial", 12, "bold"), bg="#4caf50", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Crear Nueva Pregunta", command=self.crear_nueva_pregunta,
               font=("Arial", 12, "bold"), bg="#ff9800", fg="white", padx=20, pady=10, width=25).pack(pady=10)
        
        Button(self.current_frame, text="Volver al Menú", command=self.mostrar_menu_principal,
               font=("Arial", 10), bg="#757575", fg="white", padx=10, pady=5).pack(pady=20)

    def gestionar_usuarios(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        self.current_frame = Frame(parent, padx=20, pady=20, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="GESTIÓN DE USUARIOS", 
              font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        # Treeview para mostrar usuarios
        columns = ("ID", "Nombre", "Email", "Rol")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(pady=10)
        
        # Cargar usuarios
        self.actualizar_lista_usuarios(tree)
        
        # Frame para botones
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
            messagebox.showwarning("Selección", "Por favor selecciona un usuario.")
            return
        
        item = seleccion[0]
        usuario_id = tree.item(item, "values")[0]
        usuario_nombre = tree.item(item, "values")[1]
        
        # No permitir eliminar al propio administrador
        if usuario_id == str(self.usuario.db_id):
            messagebox.showerror("Error", "No puedes eliminar tu propio usuario.")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar al usuario {usuario_nombre}?"):
            if eliminar_usuario_db(usuario_id):
                tree.delete(item)
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.")

    def gestionar_preguntas(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        self.current_frame = Frame(parent, padx=20, pady=20, bg="#ffffff", bd=5, relief="raised")
        place_method(self.current_frame)

        Label(self.current_frame, text="GESTIÓN DE PREGUNTAS", 
              font=("Arial", 16, "bold"), bg="#ffffff", fg="#004d40").pack(pady=(0, 20))
        
        # Treeview para mostrar preguntas
        columns = ("ID", "Pregunta", "Respuesta", "Categoría", "Dificultad", "Juego")
        tree = ttk.Treeview(self.current_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        tree.pack(pady=10)
        
        # Cargar preguntas
        self.actualizar_lista_preguntas(tree)
        
        # Frame para botones
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
            # Acortar la pregunta si es muy larga para mostrar
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
            messagebox.showwarning("Selección", "Por favor selecciona una pregunta.")
            return
        
        item = seleccion[0]
        pregunta_id = tree.item(item, "values")[0]
        pregunta_texto = tree.item(item, "values")[1]
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar la pregunta: {pregunta_texto}?"):
            if eliminar_pregunta_db(pregunta_id):
                tree.delete(item)
                messagebox.showinfo("Éxito", "Pregunta eliminada correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la pregunta.")

    def crear_nueva_pregunta(self):
        """Abre un formulario para crear una nueva pregunta."""
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
        
        # Cargar juegos para el combobox
        juegos = obtener_juegos_combo()
        
        # Interfaz del formulario
        Label(formulario, text="CREAR NUEVA PREGUNTA", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=10)
        
        # Campos del formulario
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
        """Guarda la nueva pregunta en la base de datos."""
        # Validar campos obligatorios
        if not pregunta_var.get() or not respuesta_var.get() or not juego_var.get():
            messagebox.showerror("Error", "Pregunta, respuesta correcta y juego son obligatorios.")
            return
        
        # Obtener ID del juego seleccionado
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
            messagebox.showinfo("Éxito", "Pregunta creada correctamente.")
            formulario.destroy()
        else:
            messagebox.showerror("Error", "No se pudo crear la pregunta.")

    # ====================================================================
    # Pantalla de Selección de Juego (modificada para volver al menú principal)
    # ====================================================================
    def mostrar_seleccion_juego(self):
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # Fondo blanco para el frame de selección
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

    # ====================================================================
    # El resto de las funciones del juego se mantienen igual
    # ====================================================================
    def iniciar_juego_quiz(self, titulo, tipo):
        """Prepara y comienza un nuevo juego de quiz."""
        print(f"🔄 Iniciando juego: {titulo}, tipo: {tipo}")  # Debug
        
        self.juego_actual_titulo = titulo
        self.juego_actual_tipo = tipo
        self.preguntas = cargar_preguntas(titulo)
        
        print(f"✅ Preguntas cargadas: {len(self.preguntas)}")  # Debug
        
        if not self.preguntas:
            messagebox.showinfo("Info", f"No hay preguntas disponibles para el juego: {titulo}.")
            self.mostrar_seleccion_juego()
            return
            
        self.indice = 0
        self.usuario.puntaje = 0
        print("🎯 Mostrando juego quiz...")  # Debug
        self.mostrar_juego_quiz() # Carga la vista del juego

    def mostrar_juego_quiz(self):
        print("🔄 Mostrando interfaz del juego...")  # Debug
        self.limpiar_frame()
        parent, place_method = self._get_parent_and_place_method()
        
        # Fondo blanco para el frame de juego
        main_frame = Frame(parent, padx=30, pady=30, bg="#ffffff", bd=5, relief="raised")
        place_method(main_frame)
        self.current_frame = main_frame
        
        print("✅ Frame de juego creado")  # Debug
        
        # Referencias para elementos de respuesta
        self.entry_respuesta = None
        self.opciones_frame = None
        self.opcion_seleccionada.set(None) # Resetear selección
        self.botones_opcion = []

        # Referencias a botones para habilitar/deshabilitar
        self.boton_verificar = None 
        
        # Título del juego y Bienvenida
        Label(main_frame, text=f"Juego: {self.juego_actual_titulo}", 
            font=("Arial", 18, "bold"), bg="#ffffff", fg="#5e35b1").pack(pady=(0, 10))
            
        self.label_bienvenida = Label(main_frame, text=f"Jugador: {self.usuario.nombre}", 
                                    font=("Arial", 14), bg="#ffffff", fg="#004d40")
        self.label_bienvenida.pack(pady=(0, 15))
        
        # Etiqueta de Puntaje
        self.label_puntaje = Label(main_frame, text=f"Puntaje: {self.usuario.puntaje}", 
                                font=("Arial", 12, "italic"), bg="#ffffff", fg="#004d40")
        self.label_puntaje.pack(pady=5)

        # Marco para la Pregunta (estilizado como tarjeta)
        pregunta_frame = Frame(main_frame, bg="#f0f0f0", bd=2, relief="groove", padx=15, pady=15)
        pregunta_frame.pack(pady=10, fill="x")
        
        self.label_pregunta = Label(pregunta_frame, text="Cargando Preguntas...", 
                                    font=("Arial", 12), wraplength=500, justify=CENTER, bg="#f0f0f0", fg="#333333")
        self.label_pregunta.pack(fill="x")
        
        # Marco para las Opciones/Respuesta (depende del tipo de juego)
        self.respuesta_area_frame = Frame(main_frame, bg="#ffffff")
        self.respuesta_area_frame.pack(pady=10, fill="x")
        
        # Resultado (Correcto/Incorrecto)
        self.label_resultado = Label(main_frame, text="", font=("Arial", 12), bg="#ffffff")
        self.label_resultado.pack(pady=10)

        # --- Marcos de Botones (Separados para orden) ---
        
        # 1. Botones de Control de Juego
        button_frame_control = Frame(main_frame, bg="#ffffff")
        button_frame_control.pack(pady=10)

        self.boton_verificar = Button(button_frame_control, text="Verificar Respuesta", command=self.verificar, 
            font=("Arial", 10, "bold"), bg="#ff6f00", fg="white", padx=10, pady=5, relief="raised")
        self.boton_verificar.pack(side=LEFT, padx=5)
            
        Button(button_frame_control, text="Siguiente Pregunta", command=self.siguiente_pregunta, 
            font=("Arial", 10), bg="#00838f", fg="white", padx=10, pady=5, relief="raised").pack(side=LEFT, padx=5)
            
        # 2. Botones de Navegación/Sesión
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
        
        # CORRECCIÓN: Estas líneas estaban mal indentadas
        self.mostrar_puntajes() 
        print("🔄 Llamando a mostrar_pregunta...")  # Debug
        self.mostrar_pregunta() 
        print("✅ Juego completamente cargado")  # Debug

    def verificar(self):
            """Verifica la respuesta del usuario."""
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
            
            # Deshabilitar el botón de verificar hasta la siguiente pregunta
            if self.boton_verificar:
                self.boton_verificar.config(state='disabled')

    def siguiente_pregunta(self):
            """Avanza a la siguiente pregunta."""
            self.indice += 1
            if self.boton_verificar:
                self.boton_verificar.config(state='normal')
            self.mostrar_pregunta()

    def mostrar_puntajes(self):
            """Muestra los mejores puntajes en la interfaz."""
            mejores = cargar_mejores_puntajes()
            for i, label in enumerate(self.labels_puntajes):
                if i < len(mejores):
                    usuario, puntaje = mejores[i]
                    label.config(text=f"{i+1}. {usuario}: {puntaje} puntos")
                else:
                    label.config(text=f"{i+1}. ---")    



    def mostrar_pregunta(self):
        # Muestra la pregunta actual o el mensaje de fin de juego.
        print(f"🔍 DEBUG: Entrando a mostrar_pregunta - índice: {self.indice}, total: {len(self.preguntas)}")
        
        # Limpiar área de respuesta anterior
        for widget in self.respuesta_area_frame.winfo_children():
            widget.destroy()
        self.botones_opcion = []
        self.opcion_seleccionada.set(None)
        
        if self.indice < len(self.preguntas):
            pregunta_obj = self.preguntas[self.indice]
            print(f"🔍 DEBUG: Mostrando pregunta {self.indice + 1}")
            
            self.label_pregunta.config(text=f"Pregunta {self.indice + 1}/{len(self.preguntas)}:\n{pregunta_obj.pregunta}")
            self.label_resultado.config(text="")
            
            if self.juego_actual_tipo == 'Abierta':
                print("🔍 DEBUG: Creando entrada para respuesta abierta")
                self.entry_respuesta = Entry(self.respuesta_area_frame, font=("Arial", 12), width=50)
                self.entry_respuesta.pack(ipady=5, padx=10)
                self.entry_respuesta.bind("<Return>", lambda event: self.verificar())
                self.entry_respuesta.focus_set()

            elif self.juego_actual_tipo == 'Multiple':
                print("🔍 DEBUG: Creando opciones múltiples")
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
            
            print("🔍 DEBUG: Pregunta mostrada exitosamente")
            
        else:
            print("🔍 DEBUG: No hay más preguntas, finalizando juego")
            self._finalizar_juego()
            
    def _finalizar_juego(self):
        print("🔄 Finalizando juego...")  # Debug
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
        print("✅ Juego finalizado correctamente")  # Debug         

# Bucle Principal de Tkinter
if __name__ == "__main__":
    root = Tk()
    app = ProQuizzApp(root)
    root.mainloop()

    # Limpiar cualquier conexión previa
import mysql.connector
try:
    # Intentar cerrar cualquier conexión existente
    mysql.connector.connect(**DB_CONFIG).close()
except:
    pass

# Cerrar conexión de DB al salir
if 'db_service' in globals():
    db_service.cerrar_db()