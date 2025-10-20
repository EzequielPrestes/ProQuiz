from tkinter import *
from tkinter import messagebox, simpledialog
from tkinter import ttk
import random
import sys 
from PIL import Image, ImageTk # Importación de Pillow

# Importa los servicios y modelos
import servicios.Bdatos as db_service
from servicios.Estetica import Theme
from modelos.Juego import Juego
from modelos.Pregunta import Pregunta
from modelos.Usuario import Usuario 

# Clase principal de la GUI
class ProQuizzGUI:
    def __init__(self, master):
        self.master = master
        master.title("AProQuizz - Programación")
        master.geometry("650x550") 
        master.resizable(False, False)

        # CARGA LA IMAGEN DE FONDO 
        self.fondo_img = None
        self.img_tk = None
        try:
            # Abre la imagen (poner ruta del archivo)
            imagen = Image.open("logo.png") 
            # tamaño de la ventana
            imagen = imagen.resize((650, 700), Image.Resampling.LANCZOS)
            # Convierte a formato compatible  Tkinter
            self.img_tk = ImageTk.PhotoImage(imagen)
            print("Logo de fondo cargado exitosamente.")
            
        except FileNotFoundError:
            print("ADVERTENCIA: Archivo de logo no encontrado. Usando solo color de fondo.")
        except Exception as e:
            print(f"ADVERTENCIA: Error al cargar o procesar la imagen de fondo: {e}")

        #Configuración de Estilos (ttk) 
        self._setup_styles(master)

        # Pedir nombre de usuario al iniciar
        self.nombre_usuario = simpledialog.askstring("Bienvenido a ProQuizz", "Ingrese su nombre:")
        if not self.nombre_usuario:
            self.nombre_usuario = "Jugador Invitado"
            
        self.usuario = Usuario(None, self.nombre_usuario)

        # Estado del juego
        self.juegos = db_service.cargar_juegos()
        self.juego_seleccionado = None
        self.preguntas = []
        self.indice = 0
        self.juego_en_curso = False
        self.entry_respuesta = None 
        
        # Crea los widgets
        self._create_widgets(master)


    def _setup_styles(self, master):
        #Configura los estilos Ttk basados en la clase Theme.
        style = ttk.Style()
        master.config(bg=Theme.BG_MAIN)
        style.theme_use('classic')

        # Estilo base
        style.configure('.', background=Theme.BG_MAIN, foreground=Theme.FG_MAIN, font=('Inter', 10))
        
        # TFrame (aca es donde el cuadro tapa el logo) VER!!
        style.configure('TFrame', background=Theme.BG_MAIN) 
        
        # Etiquetas
        style.configure('TLabel', background=Theme.BG_MAIN, foreground=Theme.FG_MAIN, font=('Inter', 12))
        style.configure('Title.TLabel', font=('Inter', 16, 'bold'), foreground=Theme.ACCENT)
        
        # Botones (los estilos dependen de que Theme.py tenga los colores definidos)
        style.configure('TButton', background=Theme.BUTTON_BG, foreground=Theme.FG_MAIN, borderwidth=1, relief="flat", padding=8)
        style.map('TButton', background=[('active', Theme.ACCENT)])
        
        style.configure('Accent.TButton', background=Theme.ACCENT, foreground=Theme.FG_MAIN, font=('Inter', 12, 'bold'))
        style.map('Accent.TButton', background=[('active', Theme.ACCENT)])
        
        style.configure('Option.TButton', background=Theme.BUTTON_BG, foreground=Theme.FG_MAIN)
        style.map('Option.TButton', background=[('active', Theme.ACCENT), ('!disabled', Theme.BUTTON_BG)])

        # Listbox
        master.option_add('*Listbox.selectBackground', Theme.ACCENT)
        master.option_add('*Listbox.selectForeground', Theme.FG_MAIN)


    def _create_widgets(self, master):
        
        # FRAME DE SELECCIÓN (Con Canvas si hay logo)
        if self.img_tk:
            self.canvas_seleccion = Canvas(master, width=650, height=550, bd=0, highlightthickness=0)
            self.canvas_seleccion.pack(fill="both", expand=True)
            # Coloca la imagen de fondo en el Canvas
            self.canvas_seleccion.create_image(0, 0, image=self.img_tk, anchor="nw")
            
            # Crea el Frame para los widgets y lo coloca sobre del Canvas
            self.frame_seleccion = ttk.Frame(self.canvas_seleccion, padding="30 30 30 30") 
            # Usa create_window para centrar el frame dentro del canvas
            self.canvas_seleccion.create_window(325, 275, window=self.frame_seleccion, anchor="center")
            
        else:
            # Si no hay imagen se usa el marco normal
            self.frame_seleccion = ttk.Frame(master, padding="30 30 30 30")
            self.frame_seleccion.pack(fill="both", expand=True)
            
        # Widgets dentro de frame_seleccion
        ttk.Label(self.frame_seleccion, text=f"Bienvenido, {self.usuario.nombre}. Seleccione un juego", style='Title.TLabel').pack(pady=15)
        
        self.lista_juegos = Listbox(self.frame_seleccion, width=40, height=6, font=('Inter', 11), bg=Theme.BUTTON_BG, fg=Theme.FG_MAIN, relief="flat", highlightthickness=0)
        for j in self.juegos:
            self.lista_juegos.insert(END, f"{j.titulo} ({j.tipo_juego})")
        self.lista_juegos.pack(pady=10, padx=10)

        self.boton_iniciar = ttk.Button(self.frame_seleccion, text="Iniciar Juego", style='Accent.TButton', command=self.iniciar_juego)
        self.boton_iniciar.pack(pady=15, ipadx=10)

        
        # MARCO DEL JUEGO
        self.frame_juego = ttk.Frame(master, padding="20 20 20 20")
        
        # cuadro para el texto de la pregunta
        ttk.Label(self.frame_juego, text="--- JUEGO EN CURSO ---", style='Title.TLabel').pack(pady=10)
        self.label_pregunta = ttk.Label(self.frame_juego, text="", wraplength=600, font=("Inter", 14, 'bold'))
        self.label_pregunta.pack(pady=20)
        
        # Marco Dinámico: Contendrá el Entry o los Botones
        self.frame_respuesta_dinamica = ttk.Frame(self.frame_juego, style='TFrame')
        self.frame_respuesta_dinamica.pack(pady=10)

        # Mensajes de resultado y puntaje
        self.label_resultado = ttk.Label(self.frame_juego, text="", font=("Inter", 12))
        self.label_resultado.pack(pady=10)
        self.label_puntaje = ttk.Label(self.frame_juego, text=f"Puntaje: 0", font=("Inter", 12, 'bold'))
        self.label_puntaje.pack(pady=10)

        # Botón para volver al menú
        ttk.Button(self.frame_juego, text="Volver al Menú", command=self.volver_a_seleccion).pack(pady=20)



    # Funciones de juego
    def volver_a_seleccion(self):
        # Muestra el marco de selección de juego
        self.juego_en_curso = False
        self.frame_juego.pack_forget()
        
        if self.img_tk:
             self.canvas_seleccion.pack(fill="both", expand=True)
        else:
             self.frame_seleccion.pack(fill="both", expand=True)

    def iniciar_juego(self):
        # Inicializa el juego, carga preguntas y muestra la primera
        seleccionado = self.lista_juegos.curselection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un juego de la lista")
            return
            
        self.juego_seleccionado = self.juegos[seleccionado[0]]
        self.preguntas = db_service.cargar_preguntas(self.juego_seleccionado.id)
        
        if not self.preguntas:
            messagebox.showinfo("Info", "No hay preguntas en este juego. Intente crear datos de prueba.")
            return

        self.juego_en_curso = True
        self.indice = 0
        self.usuario.puntaje = 0
        self.limpiar_frame_respuesta()
        
        if self.img_tk:
            self.canvas_seleccion.pack_forget()
        else:
            self.frame_seleccion.pack_forget()
            
        self.frame_juego.pack(fill="both", expand=True)
        self.mostrar_pregunta()

    def limpiar_frame_respuesta(self):
        # Limpia todos los widgets del marco de respuesta dinámica.
        for widget in self.frame_respuesta_dinamica.winfo_children():
            widget.destroy()
            
    def mostrar_pregunta(self):
        # Muestra la siguiente pregunta o finaliza el juego.
        if not self.juego_en_curso:
            return

        if self.indice < len(self.preguntas):
            pregunta_actual = self.preguntas[self.indice]
            
            self.limpiar_frame_respuesta()
            self.label_pregunta.config(text=f"Pregunta {self.indice + 1}: {pregunta_actual.pregunta}")
            self.label_resultado.config(text="")
            self.label_puntaje.config(text=f"Puntaje: {self.usuario.puntaje}")

            # muestra la interfaz según el tipo de juego seleccionado
            if self.juego_seleccionado.tipo_juego == 'Multiple Choice':
                
                opciones = [pregunta_actual.respuesta_correcta]
                if pregunta_actual.opciones_incorrectas:
                     opciones.extend(pregunta_actual.opciones_incorrectas) 
                random.shuffle(opciones) 

                for opcion in opciones:
                    btn = ttk.Button(self.frame_respuesta_dinamica, text=opcion, width=40, style='Option.TButton',
                                     command=lambda r=opcion: self.verificar(respuesta_usuario=r))
                    btn.pack(pady=5)
                    
            elif self.juego_seleccionado.tipo_juego == 'Respuesta Abierta':
                
                self.entry_respuesta = ttk.Entry(self.frame_respuesta_dinamica, font=("Inter", 12), width=40)
                self.entry_respuesta.pack(pady=5)
                self.boton_responder = ttk.Button(self.frame_respuesta_dinamica, text="Responder", style='Accent.TButton',
                                              command=lambda: self.verificar(respuesta_usuario=self.entry_respuesta.get()))
                self.boton_responder.pack(pady=10)
                self.entry_respuesta.focus_set()
                
        else:
            self.finalizar_juego()

    def verificar(self, respuesta_usuario):
        # Verifica la respuesta del usuario para ambos tipos de juego.
        if not self.juego_en_curso or self.indice >= len(self.preguntas):
            return
            
        pregunta_actual = self.preguntas[self.indice]
        
        respuesta_usuario_normalizada = respuesta_usuario.strip().lower()
        respuesta_correcta_normalizada = pregunta_actual.respuesta_correcta.strip().lower()

        es_correcta = (respuesta_usuario_normalizada == respuesta_correcta_normalizada)
        
        if es_correcta:
            self.usuario.puntaje += 10
            self.label_resultado.config(text="¡Correcto! +10 puntos", foreground=Theme.ACCENT)
        else:
            self.label_resultado.config(text=f"¡Incorrecto! La respuesta era: {pregunta_actual.respuesta_correcta}", foreground=Theme.ERROR)
            
        self.limpiar_frame_respuesta() 
            
        self.indice += 1
        
        self.master.after(2000, self.mostrar_pregunta)

    def finalizar_juego(self):
        # Finaliza el juego y muestra el puntaje final.
        self.juego_en_curso = False
        db_service.guardar_usuario(self.usuario.nombre, self.usuario.puntaje)
        
        self.label_pregunta.config(text="¡Juego Terminado!")
        self.limpiar_frame_respuesta()
        self.label_resultado.config(text="¡Excelente trabajo!", foreground=Theme.ACCENT)
        self.label_puntaje.config(text=f"Puntaje Final: {self.usuario.puntaje}", font=("Inter", 16, 'bold'))
        
        messagebox.showinfo("Fin del juego", f"Juego terminado! Puntaje final de {self.usuario.nombre}: {self.usuario.puntaje}")

# Ejecutar GUI

if __name__ == "__main__":
    # Intentar conexión a la DB
    #print("Paso 1: Intentando conectar y preparar la base de datos...")
    try:
        db_service.conectar_y_preparar_db()
    except Exception as e:
        print(f"ERROR FATAL AL INICIAR LA BASE DE DATOS: {e}")
        
    # Inicializar y ejecutar la GUI
    try:
       # print("Paso 2: Creando la ventana Tkinter...")
        root = Tk()
        app = ProQuizzGUI(root) 
       # print("Paso 3: Ventana creada. Iniciando mainloop.")
        root.mainloop()
        
    except Exception as e:
        print(f"ERROR DURANTE LA EJECUCIÓN DE TKINTER: {e}")
        
    finally:
        #Asegurar el cierre de la DB
        db_service.cerrar_db()
       # print("--- PROQUIZZ FINALIZADO ---")
