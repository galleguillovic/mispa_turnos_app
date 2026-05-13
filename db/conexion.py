import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",        # mi usuario de MySQL
    "password": "",        # mi contraseña de MySQL
    "database": "mispa_turnos"
}

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def cerrar_conexion(conexion, cursor=None):
    if cursor:
        cursor.close()
    if conexion and conexion.is_connected():
        conexion.close()