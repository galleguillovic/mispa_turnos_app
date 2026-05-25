# vista_empleados_usuario.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk, ImageDraw


class VistaEmpleadosUsuario(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._ico_buscar = None
        self._mostrar_listado()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _colorear_icono(self, ruta, color_rgb, size=(18, 18)):
        try:
            img = Image.open(ruta).convert("RGBA").resize(size, Image.LANCZOS)
            r, g, b = color_rgb
            datos = img.getdata()
            nuevos = [(r, g, b, p[3]) if p[3] > 0 else (0, 0, 0, 0)
                      for p in datos]
            img.putdata(nuevos)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _foto_circular(self, ruta, size=80):
        try:
            img = Image.open(ruta).resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)
            return ImageTk.PhotoImage(img)
        except Exception:
            try:
                img = Image.open(os.path.join(
                    "assets", "user_rosa.png")).resize(
                    (size, size), Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None

    def _obtener_empleados(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT e.id_empleado, e.dias_trabajo,
                       p.nombre, p.apellido, p.dni, p.telefono, p.email,
                       u.nombre_usuario, u.rol, u.foto,
                       GROUP_CONCAT(
                           esp.nombre ORDER BY esp.nombre SEPARATOR ', '
                       ) AS especialidades
                FROM empleados e
                JOIN personas  p   ON e.id_persona = p.id_persona
                JOIN usuarios  u   ON e.id_usuario = u.id_usuario
                LEFT JOIN empleado_especialidad ee
                       ON e.id_empleado = ee.id_empleado
                LEFT JOIN especialidades esp
                       ON ee.id_especialidad = esp.id_especialidad
                WHERE e.activo = 1
            """
            if busqueda:
                query += (" AND (p.nombre LIKE %s OR p.apellido LIKE %s)"
                          " GROUP BY e.id_empleado ORDER BY p.apellido")
                cursor.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                query += " GROUP BY e.id_empleado ORDER BY p.apellido"
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _mostrar_listado(self):
        self._limpiar()

        frame_top = tk.Frame(self, bg="#F9F0F2")
        frame_top.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(frame_top, text="Empleados y usuarios",
                 bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)).pack(side="left")

        frame_buscar = tk.Frame(frame_top, bg="white",
                                highlightbackground="#D68092",
                                highlightthickness=1)
        frame_buscar.pack(side="right", padx=(10, 0), ipady=2)

        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar())

        tk.Entry(frame_buscar, textvariable=self.var_buscar,
                 font=("Poppins", 11), bd=0, width=20
                 ).pack(side="left", padx=(8, 4), pady=4)

        ruta_buscar = os.path.join("assets", "ico_buscar.png")
        self._ico_buscar = self._colorear_icono(ruta_buscar, (214, 128, 146))
        if self._ico_buscar:
            tk.Label(frame_buscar, image=self._ico_buscar,
                     bg="white").pack(side="left", padx=(0, 8))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(8, 15))

        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#F9F0F2", highlightthickness=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)
        self.frame_lista = tk.Frame(canvas, bg="#F9F0F2")
        self.frame_lista.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas_id = canvas.create_window(
            (0, 0), window=self.frame_lista, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            canvas_id, width=e.width))

        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._cargar_tarjetas()

    def _filtrar(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()
        self._renderizar_tarjetas(
            self._obtener_empleados(self.var_buscar.get()))

    def _cargar_tarjetas(self):
        self._renderizar_tarjetas(self._obtener_empleados())

    def _renderizar_tarjetas(self, empleados):
        if not empleados:
            tk.Label(self.frame_lista,
                     text="No hay empleados cargados.",
                     bg="#F9F0F2", fg="#999999",
                     font=("Poppins", 11)).pack(pady=30)
            return
        for emp in empleados:
            self._crear_tarjeta(emp)

    def _crear_tarjeta(self, emp):
        tarjeta = tk.Frame(self.frame_lista, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.pack(fill="x", pady=8, expand=True)

        frame_foto = tk.Frame(tarjeta, bg="white")
        frame_foto.pack(side="left", padx=(20, 15), pady=15, anchor="n")

        ruta_foto = None
        if emp.get("foto"):
            ruta_foto = os.path.join("assets", "fotos_perfil", emp["foto"])
        foto = self._foto_circular(ruta_foto, size=80)
        if foto:
            lbl = tk.Label(frame_foto, image=foto, bg="white")
            lbl.image = foto
            lbl.pack()

        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(side="left", fill="both", expand=True,
                        pady=15, padx=(0, 20))

        tk.Label(frame_info,
                 text=f"{emp['nombre']} {emp['apellido']}",
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 13)).pack(anchor="w")

        for etiqueta, valor in [
            ("Usuario asociado",   emp.get("nombre_usuario") or "—"),
            ("Rol",                emp.get("rol") or "—"),
            ("DNI",                str(emp["dni"]) if emp.get("dni") else "—"),
            ("Correo electrónico", emp.get("email") or "—"),
            ("Teléfono",          emp.get("telefono") or "—"),
            ("Especialidad(es)",   emp.get("especialidades") or "—"),
            ("Días de trabajo",    emp.get("dias_trabajo") or "—"),
        ]:
            fila = tk.Frame(frame_info, bg="white")
            fila.pack(anchor="w", pady=1)
            tk.Label(fila, text=f"{etiqueta}:", bg="white", fg="#555555",
                     font=("Poppins ExtraBold", 10)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white", fg="#555555",
                     font=("Poppins", 10), wraplength=600,
                     justify="left").pack(side="left")