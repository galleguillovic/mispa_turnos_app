# db/conexion.py
import mysql.connector
from mysql.connector import Error
import configparser
import os
import sys

def _get_config():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.join(base, "..")
    
    config = configparser.ConfigParser()
    config.read(os.path.join(base, "config.ini"), encoding="utf-8")
    return config["database"]

def obtener_conexion():
    try:
        cfg = _get_config()
        conexion = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg.get("password", ""),
            database=cfg["database"],
            use_pure=True
        )
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