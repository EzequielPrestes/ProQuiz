# Servicios/Db_Service.py

import mysql.connector
# Importación Absoluta (CORREGIDO: Usando capitalización Modelos.Juego y Modelos.Pregunta)
from modelos.Juego import Juego
from modelos.Pregunta import Pregunta

# --- Constantes para nombres de juegos (usadas para la limpieza de datos de prueba) ---
TITULO_ABIERTA = 'Programación: Respuesta Abierta'
TITULO_MULTIPLE = 'Programación: Múltiple Choice'

# --- Conexión global a la DB ---
db = None
cursor = None

def conectar_y_preparar_db():
    """Establece la conexión a la DB y asegura la existencia de datos de prueba."""
    global db, cursor
    try:
        # REVISA ESTOS PARÁMETROS: host, user, password, database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",  # <--- ¡REVISA ESTO!
            database="proquizz" # <--- ¡REVISA ESTO!
        )
        cursor = db.cursor()
        print("Conexión a MySQL exitosa.")
        asegurar_datos_prueba()
        
    except mysql.connector.Error as err:
        print(f"============================================================")
        print(f"  ERROR DE CONEXIÓN A MYSQL: {err}")
        print(f"  Asegúrate de que el servidor MySQL está encendido y que")
        print(f"  la contraseña ({db.password if db else '1234'}) y la DB (proquizz) son correctas.")
        print(f"  El juego continuará SIN persistencia de datos.")
        print(f"============================================================")
        db = None
        cursor = None

def asegurar_datos_prueba():
    """Asegura que haya al menos dos juegos, Respuesta Abierta y Multiple Choice."""
    if not db: return

    # --- Tipo 1: Respuesta Abierta ---
    cursor.execute("SELECT COUNT(*) FROM juegos WHERE titulo=%s", (TITULO_ABIERTA,))
    if cursor.fetchone()[0] == 0:
        print(f"Creando datos de prueba para '{TITULO_ABIERTA}'...")
        cursor.execute("INSERT INTO juegos (titulo, tipo_juego) VALUES (%s, 'Respuesta Abierta')", (TITULO_ABIERTA,))
        db.commit()
        juego_id_abierta = cursor.lastrowid

        preguntas_prueba_abierta = [
            ('¿Qué comando imprime texto en Python?', 'print', 'Python', 'Facil'),
            ('¿Cuál es el tipo de dato de True o False?', 'bool', 'Python', 'Facil'),
            ('¿Qué operador se usa para la división entera?', '//', 'Python', 'Media'),
        ]

        for p in preguntas_prueba_abierta:
            cursor.execute("INSERT INTO preguntas (pregunta, respuesta_correcta, categoria, dificultad, juego_id, opcion_2, opcion_3, opcion_4) VALUES (%s,%s,%s,%s,%s, NULL, NULL, NULL)",
                        (p[0], p[1], p[2], p[3], juego_id_abierta))
        db.commit()
    
    # --- Tipo 2: Multiple Choice ---
    cursor.execute("SELECT COUNT(*) FROM juegos WHERE titulo=%s", (TITULO_MULTIPLE,))
    if cursor.fetchone()[0] == 0:
        print(f"Creando datos de prueba para '{TITULO_MULTIPLE}'...")
        cursor.execute("INSERT INTO juegos (titulo, tipo_juego) VALUES (%s, 'Multiple Choice')", (TITULO_MULTIPLE,))
        db.commit()
        juego_id_multiple = cursor.lastrowid

        preguntas_prueba_multiple = [
            ('¿Qué palabra reservada se utiliza para definir una CLASE en Python?', 'class', 'define', 'structure', 'objeto', 'Python', 'Facil'),
            ('Según POO, ¿cómo se llama al molde para crear objetos?', 'Clase', 'Instancia', 'Función', 'Método', 'POO', 'Facil'),
            ('¿Qué lenguaje utiliza la palabra reservada `final` para evitar la herencia?', 'Java', 'Python', 'JavaScript', 'C++', 'Java', 'Media'),
            ('¿Cuál de los siguientes no es un pilar de la POO?', 'Tipado Fuerte', 'Encapsulamiento', 'Herencia', 'Polimorfismo', 'POO', 'Media'),
        ]
        
        for p in preguntas_prueba_multiple:
             cursor.execute("INSERT INTO preguntas (pregunta, respuesta_correcta, opcion_2, opcion_3, opcion_4, categoria, dificultad, juego_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        (p[0], p[1], p[2], p[3], p[4], p[5], p[6], juego_id_multiple))
        db.commit()

def cerrar_db():
    """Cierra la conexión a la base de datos."""
    global db, cursor
    if db and db.is_connected():
        if cursor: cursor.close()
        db.close()

def cargar_juegos():
    """Carga los juegos disponibles desde la DB."""
    global db, cursor
    if not db: 
        print("Advertencia: No hay conexión a DB, devolviendo lista de juegos vacía.")
        return []
    try:
        cursor.execute("SELECT id, titulo, tipo_juego FROM juegos")
        resultados = cursor.fetchall()
        
        juegos_filtrados = []
        nombres_validos = [TITULO_ABIERTA, TITULO_MULTIPLE]
        for r in resultados:
            if r[1] in nombres_validos:
                juegos_filtrados.append(Juego(r[0], r[1], r[2]))
        
        return juegos_filtrados
    except Exception as e:
        print(f"Error al cargar juegos: {e}")
        return []

def cargar_preguntas(juego_id):
    """Carga las preguntas para un juego específico, incluyendo opciones si existen."""
    global db, cursor
    if not db: return []
    try:
        sql = "SELECT id, pregunta, respuesta_correcta, juego_id, opcion_2, opcion_3, opcion_4 FROM preguntas WHERE juego_id=%s"
        cursor.execute(sql, (juego_id,))
        resultados = cursor.fetchall()
        
        preguntas = []
        for r in resultados:
            preguntas.append(Pregunta(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
        return preguntas
        
    except Exception as e:
        print(f"Error al cargar preguntas: {e}")
        return []


def guardar_usuario(nombre, puntaje):
    """Guarda el puntaje final del usuario en la DB."""
    global db, cursor
    if not db: return
    try:
        cursor.execute("INSERT INTO usuarios (nombre, puntaje_total) VALUES (%s,%s)", (nombre, puntaje))
        db.commit()
    except Exception as e:
        print(f"Error al guardar usuario: {e}")
