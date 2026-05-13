from db.conexion import obtener_conexion, cerrar_conexion
from utils.helpers import verificar_contrasena

def autenticar_usuario(email, contrasena):
    conexion = obtener_conexion()
    if not conexion:
        return None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, u.rol, u.contrasena,
                   p.nombre, p.apellido
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id_persona
            WHERE p.email = %s AND u.activo = 1
        """, (email,))
        usuario = cursor.fetchone()

        if usuario and verificar_contrasena(contrasena, usuario["contrasena"]):
            return {
                "id_usuario": usuario["id_usuario"],
                "nombre_usuario": usuario["nombre_usuario"],
                "nombre": usuario["nombre"],
                "apellido": usuario["apellido"],
                "rol": usuario["rol"]
            }
        return None

    except Exception as e:
        print(f"Error al autenticar: {e}")
        return None

    finally:
        cerrar_conexion(conexion, cursor)