# servicios/DatabaseService.py

import mysql.connector
from modelos.Usuario import Usuario
from modelos.Pregunta import Pregunta
from modelos.Juego import Juego

class DatabaseService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db = None
        self.cursor = None
        self.conectar()
    
    def conectar(self):
        try:
            self.db = mysql.connector.connect(**self.db_config)
            # Usar buffered=True para evitar el error "Unread result found"
            self.cursor = self.db.cursor(buffered=True)
            print("✅ Conectado a la base de datos")
        except mysql.connector.Error as err:
            print(f"❌ Error de Conexión a la Base de Datos: {err}")
            raise

    def _ejecutar_consulta(self, query, params=None):
        """Ejecuta una consulta y maneja los resultados correctamente."""
        try:
            self.cursor.execute(query, params or ())
            # Si es una consulta SELECT, obtener y retornar los resultados
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            # Para INSERT, UPDATE, DELETE, hacer commit
            else:
                self.db.commit()
                return True
        except mysql.connector.Error as err:
            print(f"Error en consulta: {err}")
            self.db.rollback()
            return False
    
    def obtener_juegos(self):
        try:
            return self._ejecutar_consulta("SELECT titulo, tipo_juego FROM juegos") or []
        except mysql.connector.Error as err:
            print(f"Error al cargar juegos: {err}")
            return []
    
    def registrar_usuario(self, nombre, email, password):
        try:
            from main import hashear_password
            password_hash = hashear_password(password)
            query = "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, 'usuario')"
            return self._ejecutar_consulta(query, (nombre, email, password_hash))
        except mysql.connector.IntegrityError:
            return False
        except mysql.connector.Error as err:
            print(f"Error al registrar usuario: {err}")
            return False
    
    def verificar_login(self, email, password):
        try:
            from main import hashear_password
            query = "SELECT id, nombre, password_hash, rol FROM usuarios WHERE email = %s"
            resultado = self._ejecutar_consulta(query, (email,))
            
            if resultado and len(resultado) > 0:
                usuario_id, nombre, hash_almacenado, rol = resultado[0]
                password_hash_ingresado = hashear_password(password)
                
                if password_hash_ingresado == hash_almacenado:
                    return Usuario(usuario_id, nombre, email, rol)
            
            return None
        except mysql.connector.Error as err:
            print(f"Error al verificar login: {err}")
            return None
    
    def cargar_preguntas(self, juego_titulo):
        try:
            query = """
                SELECT p.id, p.pregunta, p.respuesta_correcta, 
                       p.opcion_incorrecta_1, p.opcion_incorrecta_2, p.opcion_incorrecta_3,
                       p.categoria, p.dificultad, p.juego_id
                FROM preguntas p
                JOIN juegos j ON p.juego_id = j.id
                WHERE j.titulo = %s
            """
            return self._ejecutar_consulta(query, (juego_titulo,)) or []
        except mysql.connector.Error as err:
            print(f"Error al cargar preguntas: {err}")
            return []
    
    def guardar_puntaje(self, usuario_id, puntaje):
        try:
            query = "INSERT INTO puntajes (usuario_id, puntaje) VALUES (%s, %s)"
            return self._ejecutar_consulta(query, (usuario_id, puntaje))
        except mysql.connector.Error as err:
            print(f"Error al guardar puntaje: {err}")
            return False
    
    def cargar_mejores_puntajes(self):
        try:
            query = """
                SELECT u.nombre, p.puntaje
                FROM puntajes p
                JOIN usuarios u ON p.usuario_id = u.id
                ORDER BY p.puntaje DESC, p.fecha ASC
                LIMIT 5
            """
            return self._ejecutar_consulta(query) or []
        except mysql.connector.Error as err:
            print(f"Error al cargar puntajes: {err}")
            return []
    
    # Funciones de administrador
    def obtener_todos_usuarios(self):
        try:
            return self._ejecutar_consulta("SELECT id, nombre, email, rol FROM usuarios") or []
        except mysql.connector.Error as err:
            print(f"Error al cargar usuarios: {err}")
            return []
    
    def eliminar_usuario(self, usuario_id):
        try:
            # Primero eliminar los puntajes del usuario
            self._ejecutar_consulta("DELETE FROM puntajes WHERE usuario_id = %s", (usuario_id,))
            # Luego eliminar el usuario
            return self._ejecutar_consulta("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        except mysql.connector.Error as err:
            print(f"Error al eliminar usuario: {err}")
            return False
    
    def obtener_todas_preguntas(self):
        try:
            query = """
                SELECT p.id, p.pregunta, p.respuesta_correcta, 
                       p.opcion_incorrecta_1, p.opcion_incorrecta_2, p.opcion_incorrecta_3,
                       p.categoria, p.dificultad, j.titulo
                FROM preguntas p
                JOIN juegos j ON p.juego_id = j.id
            """
            return self._ejecutar_consulta(query) or []
        except mysql.connector.Error as err:
            print(f"Error al cargar preguntas: {err}")
            return []
    
    def eliminar_pregunta(self, pregunta_id):
        try:
            return self._ejecutar_consulta("DELETE FROM preguntas WHERE id = %s", (pregunta_id,))
        except mysql.connector.Error as err:
            print(f"Error al eliminar pregunta: {err}")
            return False
    
    def crear_pregunta(self, pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id):
        try:
            query = """
                INSERT INTO preguntas 
                (pregunta, respuesta_correcta, opcion_incorrecta_1, opcion_incorrecta_2, opcion_incorrecta_3, 
                 categoria, dificultad, juego_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            return self._ejecutar_consulta(query, (pregunta, respuesta_correcta, op1, op2, op3, categoria, dificultad, juego_id))
        except mysql.connector.Error as err:
            print(f"Error al crear pregunta: {err}")
            return False
    
    def obtener_juegos_combo(self):
        try:
            return self._ejecutar_consulta("SELECT id, titulo FROM juegos") or []
        except mysql.connector.Error as err:
            print(f"Error al cargar juegos combo: {err}")
            return []

    def cerrar_db(self):
        """Cierra la conexión a la base de datos."""
        if self.db and self.db.is_connected():
            if self.cursor:
                self.cursor.close()
            self.db.close()
            print("🔌 Conexión a la base de datos cerrada")