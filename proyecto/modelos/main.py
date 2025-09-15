import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from Juego import juego
from Preguntas import Preguntas
from Usuarios import usuario

# Crear instancias globales
usuario_actual = None
juego_actual = None
preguntas = Preguntas()  # Instancia global de preguntas

# Función que se ejecuta al hacer clic en el botón
def inicio():
    global usuario_actual
    nombre = entrada_nombre.get().strip()  # Eliminar espacios en blanco
    if nombre:
        usuario_actual = usuario(nombre)  # Crear un nuevo usuario
        ventana.withdraw()  # Ocultar la ventana principal
        abrir_ventana_principal(usuario_actual)
    else:
        messagebox.showwarning("Advertencia", "Por favor, ingresa tu nombre")

# Función para abrir la nueva ventana
def abrir_ventana_principal(usuario):
    nueva_ventana = ttk.Toplevel(ventana)
    nueva_ventana.title("Ventana Principal - ProQuiz")
    nueva_ventana.geometry("500x600")
    nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_sesion(nueva_ventana))
    
    # Frame principal para mejor organización
    frame_principal = ttk.Frame(nueva_ventana)
    frame_principal.pack(fill=BOTH, expand=YES, padx=20, pady=20)
    
    # Etiqueta de bienvenida
    etiqueta_bienvenida = ttk.Label(
        frame_principal, 
        text=f"¡Bienvenido, {usuario.nombre}!", 
        font=("Arial", 18, "bold"),
        bootstyle=PRIMARY
    )
    etiqueta_bienvenida.pack(pady=30)
    
    # Frame para botones
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(pady=20)
    
    # Botón para jugar
    boton_jugar = ttk.Button(
        frame_botones, 
        text="Jugar", 
        bootstyle=SUCCESS, 
        width=15,
        command=lambda: iniciar_juego(usuario, nueva_ventana)
    )
    boton_jugar.pack(pady=15)
    
    # Botón para ver estadísticas (nueva funcionalidad)
    boton_estadisticas = ttk.Button(
        frame_botones, 
        text="Ver Estadísticas", 
        bootstyle=INFO, 
        width=15,
        command=lambda: mostrar_estadisticas(usuario)
    )
    boton_estadisticas.pack(pady=15)
    
    # Botón para cerrar sesión
    boton_cerrar = ttk.Button(
        frame_botones, 
        text="Cerrar sesión", 
        bootstyle=DANGER, 
        width=15,
        command=lambda: cerrar_sesion(nueva_ventana)
    )
    boton_cerrar.pack(pady=15)

    # Botón para abrir la ventana de gestión de preguntas
    boton_gestionar = ttk.Button(
        frame_botones,
        text="Gestionar Preguntas",
        bootstyle=WARNING,
        width=15,
        command=gestionar_preguntas
    )
    boton_gestionar.pack(pady=15)

# Función para cerrar sesión y volver a la ventana principal
def cerrar_sesion(nueva_ventana):
    nueva_ventana.destroy()
    ventana.deiconify()  # Mostrar la ventana principal nuevamente
    entrada_nombre.delete(0, END)  # Limpiar el campo de nombre

# Función para iniciar el juego
def iniciar_juego(usuario, ventana_actual):
    global juego_actual
    try:
        juego_actual = juego(usuario)  # Crear una nueva instancia del juego
        mensaje = juego_actual.iniciar()
        messagebox.showinfo("Juego", mensaje)
        
        # Obtener y mostrar preguntas
        pregunta_actual = preguntas.obtener_pregunta(0)
        if pregunta_actual:
            mostrar_pregunta(ventana_actual, pregunta_actual)
        else:
            messagebox.showwarning("Juego", "No hay preguntas disponibles")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar el juego: {str(e)}")

# Función para mostrar una pregunta
def mostrar_pregunta(ventana_padre, pregunta):
    ventana_pregunta = ttk.Toplevel(ventana_padre)
    ventana_pregunta.title("Pregunta")
    ventana_pregunta.geometry("500x400")
    
    frame_pregunta = ttk.Frame(ventana_pregunta)
    frame_pregunta.pack(fill=BOTH, expand=YES, padx=20, pady=20)
    
    # Mostrar la pregunta
    label_pregunta = ttk.Label(
        frame_pregunta,
        text=pregunta['pregunta'],
        font=("Arial", 14),
        wraplength=400
    )
    label_pregunta.pack(pady=20)
    
    # Mostrar opciones de respuesta
    for i, opcion in enumerate(pregunta['opciones']):
        ttk.Radiobutton(
            frame_pregunta,
            text=opcion,
            value=i,
            variable=ttk.IntVar()
        ).pack(anchor=W, pady=5)
    
    # Botón para enviar respuesta
    ttk.Button(
        frame_pregunta,
        text="Enviar respuesta",
        bootstyle=SUCCESS,
        command=lambda: verificar_respuesta(ventana_pregunta, pregunta)
    ).pack(pady=20)

# Función para verificar la respuesta
def verificar_respuesta(ventana_pregunta, pregunta):
    # Aquí iría la lógica para verificar la respuesta
    messagebox.showinfo("Respuesta", "Respuesta verificada")
    ventana_pregunta.destroy()

# Función para mostrar estadísticas (nueva funcionalidad)
def mostrar_estadisticas(usuario):
    # Aquí iría la lógica para mostrar estadísticas del usuario
    messagebox.showinfo("Estadísticas", f"Estadísticas de {usuario.nombre}\n\nPuntuación: 0\nPartidas jugadas: 0")

# Función para abrir la ventana de gestión de preguntas
def gestionar_preguntas():
    ventana_gestion = ttk.Toplevel(ventana)
    ventana_gestion.title("Gestión de Preguntas")
    ventana_gestion.geometry("600x500")

    frame_gestion = ttk.Frame(ventana_gestion)
    frame_gestion.pack(fill=BOTH, expand=YES, padx=20, pady=20)

    # Etiqueta de título
    ttk.Label(
        frame_gestion,
        text="Gestión de Preguntas",
        font=("Arial", 18, "bold"),
        bootstyle=PRIMARY
    ).pack(pady=10)

    # Lista de preguntas
    lista_preguntas = ttk.Treeview(
        frame_gestion,
        columns=("Pregunta", "Respuesta", "Categoría", "Dificultad"),
        show="headings",
        height=10
    )
    lista_preguntas.pack(fill=BOTH, expand=YES, pady=10)

    # Configurar encabezados
    lista_preguntas.heading("Pregunta", text="Pregunta")
    lista_preguntas.heading("Respuesta", text="Respuesta Correcta")
    lista_preguntas.heading("Categoría", text="Categoría")
    lista_preguntas.heading("Dificultad", text="Dificultad")

    # Configurar columnas
    lista_preguntas.column("Pregunta", width=200)
    lista_preguntas.column("Respuesta", width=100)
    lista_preguntas.column("Categoría", width=100)
    lista_preguntas.column("Dificultad", width=100)

    # Cargar preguntas en la lista
    for i, pregunta in enumerate(preguntas.preguntas):
        lista_preguntas.insert("", "end", iid=i, values=(
            pregunta["pregunta"],
            pregunta["respuesta_correcta"],
            pregunta["categoria"],
            pregunta["dificultad"]
        ))

    # Botones para agregar, modificar y eliminar preguntas
    frame_botones = ttk.Frame(frame_gestion)
    frame_botones.pack(pady=10)

    ttk.Button(
        frame_botones,
        text="Agregar Pregunta",
        bootstyle=SUCCESS,
        command=lambda: agregar_pregunta(lista_preguntas)
    ).pack(side=LEFT, padx=10)

    ttk.Button(
        frame_botones,
        text="Modificar Pregunta",
        bootstyle=INFO,
        command=lambda: modificar_pregunta(lista_preguntas)
    ).pack(side=LEFT, padx=10)

    ttk.Button(
        frame_botones,
        text="Eliminar Pregunta",
        bootstyle=DANGER,
        command=lambda: eliminar_pregunta(lista_preguntas)
    ).pack(side=LEFT, padx=10)

# Función para agregar una nueva pregunta
def agregar_pregunta(lista_preguntas):
    ventana_agregar = ttk.Toplevel(ventana)
    ventana_agregar.title("Agregar Pregunta")
    ventana_agregar.geometry("400x400")

    frame_agregar = ttk.Frame(ventana_agregar)
    frame_agregar.pack(fill=BOTH, expand=YES, padx=20, pady=20)

    # Campos para ingresar datos
    campos = {
        "Pregunta": ttk.Entry(frame_agregar, width=40),
        "Respuesta Correcta": ttk.Entry(frame_agregar, width=40),
        "Categoría": ttk.Entry(frame_agregar, width=40),
        "Dificultad": ttk.Entry(frame_agregar, width=40)
    }

    for i, (label, entry) in enumerate(campos.items()):
        ttk.Label(frame_agregar, text=label, font=("Arial", 12)).grid(row=i, column=0, pady=5, sticky=W)
        entry.grid(row=i, column=1, pady=5)

    # Botón para guardar la pregunta
    ttk.Button(
        frame_agregar,
        text="Guardar",
        bootstyle=SUCCESS,
        command=lambda: guardar_pregunta(campos, lista_preguntas, ventana_agregar)
    ).grid(row=len(campos), column=0, columnspan=2, pady=20)

# Función para guardar la nueva pregunta
def guardar_pregunta(campos, lista_preguntas, ventana_agregar):
    nueva_pregunta = {
        "pregunta": campos["Pregunta"].get(),
        "respuesta_correcta": campos["Respuesta Correcta"].get(),
        "categoria": campos["Categoría"].get(),
        "dificultad": campos["Dificultad"].get()
    }
    preguntas.preguntas.append(nueva_pregunta)  # Agregar a la lista global
    lista_preguntas.insert("", "end", values=(
        nueva_pregunta["pregunta"],
        nueva_pregunta["respuesta_correcta"],
        nueva_pregunta["categoria"],
        nueva_pregunta["dificultad"]
    ))
    ventana_agregar.destroy()

# Función para modificar una pregunta existente
def modificar_pregunta(lista_preguntas):
    seleccion = lista_preguntas.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona una pregunta para modificar")
        return

    indice = int(seleccion[0])
    pregunta_seleccionada = preguntas.preguntas[indice]

    ventana_modificar = ttk.Toplevel(ventana)
    ventana_modificar.title("Modificar Pregunta")
    ventana_modificar.geometry("400x400")

    frame_modificar = ttk.Frame(ventana_modificar)
    frame_modificar.pack(fill=BOTH, expand=YES, padx=20, pady=20)

    # Campos para modificar datos
    campos = {
        "Pregunta": ttk.Entry(frame_modificar, width=40),
        "Respuesta Correcta": ttk.Entry(frame_modificar, width=40),
        "Categoría": ttk.Entry(frame_modificar, width=40),
        "Dificultad": ttk.Entry(frame_modificar, width=40)
    }

    for i, (label, entry) in enumerate(campos.items()):
        ttk.Label(frame_modificar, text=label, font=("Arial", 12)).grid(row=i, column=0, pady=5, sticky=W)
        entry.grid(row=i, column=1, pady=5)
        entry.insert(0, pregunta_seleccionada[label.lower().replace(" ", "_")])

    # Botón para guardar los cambios
    ttk.Button(
        frame_modificar,
        text="Guardar Cambios",
        bootstyle=SUCCESS,
        command=lambda: guardar_cambios(campos, lista_preguntas, ventana_modificar, indice)
    ).grid(row=len(campos), column=0, columnspan=2, pady=20)

# Función para guardar los cambios en una pregunta
def guardar_cambios(campos, lista_preguntas, ventana_modificar, indice):
    preguntas.preguntas[indice] = {
        "pregunta": campos["Pregunta"].get(),
        "respuesta_correcta": campos["Respuesta Correcta"].get(),
        "categoria": campos["Categoría"].get(),
        "dificultad": campos["Dificultad"].get()
    }
    lista_preguntas.item(indice, values=(
        preguntas.preguntas[indice]["pregunta"],
        preguntas.preguntas[indice]["respuesta_correcta"],
        preguntas.preguntas[indice]["categoria"],
        preguntas.preguntas[indice]["dificultad"]
    ))
    ventana_modificar.destroy()

# Función para eliminar una pregunta
def eliminar_pregunta(lista_preguntas):
    seleccion = lista_preguntas.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona una pregunta para eliminar")
        return

    indice = int(seleccion[0])
    preguntas.preguntas.pop(indice)  # Eliminar de la lista global
    lista_preguntas.delete(seleccion[0])  # Eliminar del Treeview

# Crear la ventana principal
ventana = ttk.Window(themename="flatly")  # Cambia el tema aquí
ventana.title("PROQUIZ")
ventana.geometry("500x500")  # Ancho x Alto

# Frame principal para mejor organización
frame_principal = ttk.Frame(ventana)
frame_principal.pack(fill=BOTH, expand=YES, padx=40, pady=40)

# Crear y colocar widgets
etiqueta_titulo = ttk.Label(
    frame_principal, 
    text="Bienvenido a ProQuiz", 
    font=("Arial", 20, "bold"),
    bootstyle=PRIMARY
)
etiqueta_titulo.pack(pady=30)

etiqueta_nombre = ttk.Label(
    frame_principal, 
    text="Ingresa tu nombre:", 
    font=("Arial", 12)
)
etiqueta_nombre.pack(pady=10)

entrada_nombre = ttk.Entry(
    frame_principal, 
    font=("Arial", 12), 
    width=25
)
entrada_nombre.pack(pady=10)
entrada_nombre.focus()  # Poner foco en el campo de nombre

# Botón para iniciar sesión
boton_inicio = ttk.Button(
    frame_principal, 
    text="Iniciar sesión", 
    bootstyle=PRIMARY,
    width=15,
    command=inicio
)
boton_inicio.pack(pady=20)

# Permitir iniciar sesión con la tecla Enter
ventana.bind('<Return>', lambda event: inicio())

# Botón para salir
boton_salir = ttk.Button(
    frame_principal, 
    text="Salir", 
    bootstyle=DANGER,
    width=15,
    command=ventana.quit
)
boton_salir.pack(pady=10)

# Iniciar el bucle principal de la aplicación
ventana.mainloop()