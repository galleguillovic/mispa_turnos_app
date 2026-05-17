# modelos/usuario.py
from db.conexion import obtener_conexion, cerrar_conexion
from utils.helpers import verificar_contrasena


def autenticar_usuario(credencial, contrasena):
    """
    Autentica por correo electrónico (personas.email)
    O por nombre de usuario (usuarios.nombre_usuario).
    """
    conexion = obtener_conexion()
    if not conexion:
        return None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.id_usuario, u.nombre_usuario, u.rol,
                   u.contrasena, u.foto,
                   p.nombre, p.apellido
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id_persona
            WHERE (p.email = %s OR u.nombre_usuario = %s)
              AND u.activo = 1
            LIMIT 1
        """, (credencial, credencial))
        usuario = cursor.fetchone()

        if usuario and verificar_contrasena(contrasena, usuario["contrasena"]):
            return {
                "id_usuario":      usuario["id_usuario"],
                "nombre_usuario":  usuario["nombre_usuario"],
                "nombre":          usuario["nombre"],
                "apellido":        usuario["apellido"],
                "rol":             usuario["rol"],
                "foto":            usuario.get("foto"),
            }
        return None

    except Exception as e:
        print(f"Error al autenticar: {e}")
        return None

    finally:
        cerrar_conexion(conexion, cursor)