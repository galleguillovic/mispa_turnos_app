#panel_admin.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
from tkcalendar import Calendar
import datetime
import os

class PanelAdmin(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.master = master
        self.usuario = usuario
        self.title("MiSpa Turnos - Panel Administrador")
        self.resizable(False, False)
        self.configure(bg="#D68092")
        self.protocol("WM_DELETE_WINDOW", lambda: self.master.destroy())

        ancho, alto = 1200, 700
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = max(0, (self.winfo_screenheight() // 2) - (alto // 2) - 40)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.menu_activo = "Inicio"
        self.iconos_blancos = {}
        self.iconos_rosados = {}
        self._cargar_iconos()
        self._construir_ui()

    def _colorear_icono(self, ruta, color_rgb, size=(22, 22)):
        try:
            img = Image.open(ruta).convert("RGBA").resize(size, Image.LANCZOS)
            r, g, b = color_rgb
            datos = img.getdata()
            nuevos = []
            for pixel in datos:
                if pixel[3] > 0:
                    nuevos.append((r, g, b, pixel[3]))
                else:
                    nuevos.append((0, 0, 0, 0))
            img.putdata(nuevos)
            return ImageTk.PhotoImage(img)
        except Exception:
            return None

    def _cargar_iconos(self):
        items = ["inicio", "turnos", "clientes", "empleados",
                 "servicios", "reportes", "cerrar", "lapiz"]
        for nombre in items:
            ruta = os.path.join("assets", f"ico_{nombre}.png")
            self.iconos_blancos[nombre] = self._colorear_icono(
                ruta, (255, 255, 255))
            self.iconos_rosados[nombre] = self._colorear_icono(
                ruta, (214, 128, 146))

    def _construir_ui(self):
        self.sidebar = tk.Frame(self, bg="#D68092", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.area_contenido = tk.Frame(self, bg="#F9F0F2")
        self.area_contenido.pack(side="left", fill="both", expand=True)

        self._construir_sidebar()
        self._mostrar_inicio()

    def _construir_sidebar(self):
        frame_perfil = tk.Frame(self.sidebar, bg="#D68092")
        frame_perfil.pack(pady=(30, 10))
        self._mostrar_foto_perfil(frame_perfil)

        tk.Label(
            self.sidebar,
            text=self.usuario["nombre"],
            bg="#D68092", fg="white",
            font=("Poppins ExtraBold", 13)
        ).pack()

        frame_config = tk.Frame(self.sidebar, bg="#D68092", cursor="hand2")
        frame_config.pack(pady=(4, 20))
        frame_config.bind("<Button-1>", lambda e: self._abrir_configurar_perfil())

        if self.iconos_blancos.get("lapiz"):
            lbl_lap = tk.Label(frame_config, image=self.iconos_blancos["lapiz"],
                     bg="#D68092", cursor="hand2")
            lbl_lap.pack(side="left", padx=(0, 4))
            lbl_lap.bind("<Button-1>", lambda e: self._abrir_configurar_perfil())

        lbl_cfg = tk.Label(
            frame_config,
            text="Configurar perfil",
            bg="#D68092", fg="white",
            font=("Poppins", 9),
            cursor="hand2",
            underline=0
        )
        lbl_cfg.pack(side="left")
        lbl_cfg.bind("<Button-1>", lambda e: self._abrir_configurar_perfil())

        tk.Frame(self.sidebar, bg="white", height=1).pack(
            fill="x", padx=20, pady=(0, 10))

        self.botones_menu = {}
        menu_items = [
            ("Inicio", "inicio"),
            ("Ver turnos", "turnos"),
            ("Ver clientes", "clientes"),
            ("Ver empleados", "empleados"),
            ("Ver servicios", "servicios"),
            ("Reportes", "reportes"),
        ]

        for texto, clave in menu_items:
            self._crear_item_menu(texto, clave)

        tk.Frame(self.sidebar, bg="white", height=1).pack(
            fill="x", padx=20, pady=(10, 10))

        btn_cerrar = tk.Frame(self.sidebar, bg="#D68092", cursor="hand2")
        btn_cerrar.pack(fill="x", padx=15, pady=5)
        btn_cerrar.bind("<Button-1>", lambda e: self._cerrar_sesion())

        if self.iconos_blancos.get("cerrar"):
            lbl_ico = tk.Label(btn_cerrar, image=self.iconos_blancos["cerrar"],
                               bg="#D68092", cursor="hand2")
            lbl_ico.pack(side="left", padx=(10, 8), pady=8)
            lbl_ico.bind("<Button-1>", lambda e: self._cerrar_sesion())

        lbl_cerrar = tk.Label(
            btn_cerrar,
            text="Cerrar sesión",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            cursor="hand2"
        )
        lbl_cerrar.pack(side="left")
        lbl_cerrar.bind("<Button-1>", lambda e: self._cerrar_sesion())

    def _mostrar_foto_perfil(self, frame_padre):
        foto_path = None
        if self.usuario.get("foto"):
            foto_path = os.path.join("assets", "fotos_perfil",
                                     self.usuario["foto"])
        size = 80
        try:
            if foto_path and os.path.exists(foto_path):
                img = Image.open(foto_path).resize((size, size), Image.LANCZOS)
            else:
                raise FileNotFoundError
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)
            self.foto_perfil = ImageTk.PhotoImage(img)
            tk.Label(frame_padre, image=self.foto_perfil,
                     bg="#D68092").pack()
        except Exception:
            ruta_default = os.path.join("assets", "user_rosa.png")
            try:
                img = Image.open(ruta_default).resize((size, size), Image.LANCZOS)
                self.foto_perfil = ImageTk.PhotoImage(img)
                tk.Label(frame_padre, image=self.foto_perfil,
                         bg="#D68092").pack()
            except Exception:
                tk.Label(frame_padre, text="👤", bg="#D68092",
                         font=("Poppins", 30)).pack()

    def _crear_item_menu(self, texto, clave):
        activo = (self.menu_activo == texto)
        bg = "white" if activo else "#D68092"
        fg = "#D68092" if activo else "white"

        frame = tk.Frame(self.sidebar, bg=bg, cursor="hand2")
        frame.pack(fill="x", padx=15, pady=3)

        icono = self.iconos_rosados.get(clave) if activo \
            else self.iconos_blancos.get(clave)

        if icono:
            lbl_ico = tk.Label(frame, image=icono, bg=bg, cursor="hand2")
            lbl_ico.pack(side="left", padx=(10, 8), pady=8)
            lbl_ico.bind("<Button-1>",
                         lambda e, t=texto: self._seleccionar_menu(t))

        lbl = tk.Label(frame, text=texto, bg=bg, fg=fg,
                       font=("Poppins", 11), cursor="hand2")
        lbl.pack(side="left", pady=8)
        lbl.bind("<Button-1>", lambda e, t=texto: self._seleccionar_menu(t))
        frame.bind("<Button-1>", lambda e, t=texto: self._seleccionar_menu(t))

        self.botones_menu[texto] = frame

    def _abrir_configurar_perfil(self):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()
        self.menu_activo = ""
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._construir_sidebar()
        from vistas.configurar_perfil import VistaConfigurarPerfil
        VistaConfigurarPerfil(self.area_contenido, self)

    def _seleccionar_menu(self, texto):
        self.menu_activo = texto
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._construir_sidebar()

        for widget in self.area_contenido.winfo_children():
            widget.destroy()

        if texto == "Inicio":
            self._mostrar_inicio()
        elif texto == "Ver turnos":
            from vistas.turnos import VistaTurnos
            VistaTurnos(self.area_contenido, self)
        elif texto == "Ver clientes":
            from vistas.clientes import VistaClientes
            VistaClientes(self.area_contenido, self)
        elif texto == "Ver empleados":
            from vistas.empleados import VistaEmpleados
            VistaEmpleados(self.area_contenido, self)
        elif texto == "Ver servicios":
            from vistas.servicios import VistaServicios
            VistaServicios(self.area_contenido, self)
        elif texto == "Reportes":
            from vistas.reportes import VistaReportes
            VistaReportes(self.area_contenido, self)

    def _cerrar_sesion(self):
        self.master.destroy()

    def _mostrar_inicio(self):
        frame_centro = tk.Frame(self.area_contenido, bg="#F9F0F2")
        frame_centro.pack(side="left", fill="both", expand=True,
                          padx=30, pady=20)

        frame_derecha = tk.Frame(self.area_contenido, bg="white", width=320)
        frame_derecha.pack(side="right", fill="y")
        frame_derecha.pack_propagate(False)

        tk.Label(
            frame_centro,
            text="Vista de Turnos",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w")

        tk.Frame(frame_centro, bg="#D68092", height=2).pack(
            fill="x", pady=(4, 20))

        hoy = datetime.date.today()
        cal = Calendar(
            frame_centro,
            selectmode="day",
            year=hoy.year,
            month=hoy.month,
            day=hoy.day,
            background="#D68092",
            foreground="white",
            selectbackground="#A0526A",
            headersbackground="#D68092",
            headersforeground="white",
            weekendforeground="white",
            othermonthforeground="#cccccc",
            font=("Poppins", 9),
            showweeknumbers=False,
            locale="es_AR"
        )
        cal.pack(anchor="w", fill="both", expand=True)
        self._marcar_dias_con_turnos(cal)

        self._frame_dia = tk.Frame(frame_centro, bg="#F9F0F2")
        self._frame_dia.pack(fill="x", pady=(15, 0))

        cal.bind("<<CalendarSelected>>",
                 lambda e: self._mostrar_turnos_dia(
                     cal.selection_get(), self._frame_dia))

        tk.Label(
            frame_derecha,
            text="Turnos Programados",
            bg="white", fg="#D68092",
            font=("Poppins ExtraBold", 14)
        ).pack(anchor="w", padx=20, pady=(20, 10))

        canvas_scroll = tk.Canvas(frame_derecha, bg="white",
                                  highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_derecha, orient="vertical",
                                  command=canvas_scroll.yview)
        frame_lista = tk.Frame(canvas_scroll, bg="white")

        frame_lista.bind("<Configure>", lambda e: canvas_scroll.configure(
            scrollregion=canvas_scroll.bbox("all")))

        canvas_id = canvas_scroll.create_window(
            (0, 0), window=frame_lista, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.itemconfig(
            canvas_id, width=e.width))

        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        self._cargar_turnos_proximos(frame_lista)

    def _marcar_dias_con_turnos(self, cal):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT DISTINCT DATE(fecha_hora) AS fecha
                FROM turnos
                WHERE estado = 'programado'
            """)
            fechas = cursor.fetchall()
            for f in fechas:
                fecha = f["fecha"]
                cal.calevent_create(
                    datetime.datetime(fecha.year, fecha.month, fecha.day),
                    "turno", "turno")
            cal.tag_config("turno", background="#A0526A", foreground="white")
        except Exception as e:
            print(f"Error marcando días: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    def _cargar_turnos_proximos(self, frame_lista):
        from db.conexion import obtener_conexion, cerrar_conexion
        hoy = datetime.date.today()
        manana = hoy + datetime.timedelta(days=1)

        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id_turno, t.fecha_hora, t.estado,
                       p_emp.nombre AS emp_nombre,
                       p_emp.apellido AS emp_apellido,
                       u_emp.foto AS emp_foto,
                       GROUP_CONCAT(s.nombre SEPARATOR ', ') AS servicios
                FROM turnos t
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                JOIN usuarios u_emp ON e.id_usuario = u_emp.id_usuario
                LEFT JOIN turno_servicio ts ON t.id_turno = ts.id_turno
                LEFT JOIN servicios s ON ts.id_servicio = s.id_servicio
                WHERE DATE(t.fecha_hora) IN (%s, %s)
                AND t.estado = 'programado'
                GROUP BY t.id_turno
                ORDER BY t.fecha_hora ASC
            """, (hoy, manana))
            turnos = cursor.fetchall()
        except Exception as e:
            print(f"Error cargando turnos: {e}")
            turnos = []
        finally:
            cerrar_conexion(conexion, cursor)

        if not turnos:
            tk.Label(frame_lista, text="Sin turnos para hoy\nni mañana",
                     bg="white", fg="#999999",
                     font=("Poppins", 10)).pack(pady=30)
            return

        for turno in turnos:
            self._crear_tarjeta_turno(frame_lista, turno)

    def _crear_tarjeta_turno(self, frame_padre, turno):
        tarjeta = tk.Frame(frame_padre, bg="white",
                           highlightbackground="#D68092",
                           highlightthickness=1)
        tarjeta.pack(fill="x", padx=15, pady=6)

        frame_foto = tk.Frame(tarjeta, bg="white")
        frame_foto.pack(side="left", padx=(10, 8), pady=8)
        self._foto_empleada(frame_foto, turno.get("emp_foto"))

        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(side="left", fill="x", expand=True, pady=8)

        nombre = f"{turno['emp_nombre']} {turno['emp_apellido']}"
        tk.Label(frame_info, text=nombre, bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 10)).pack(anchor="w")
        tk.Label(frame_info, text=turno.get("servicios", "—"), bg="white",
                 fg="#666666", font=("Poppins", 9), wraplength=150).pack(anchor="w")

        fecha = turno["fecha_hora"]
        fecha_str = fecha.strftime("%a. %d - %H:%Mhs") \
            if hasattr(fecha, "strftime") else str(fecha)
        tk.Label(frame_info, text=fecha_str, bg="white",
                 fg="#666666", font=("Poppins", 9)).pack(anchor="w")

        ruta_ojo = os.path.join("assets", "ico_ojo.png")
        try:
            img_ojo = self._colorear_icono(ruta_ojo, (214, 128, 146))
            lbl_ojo = tk.Label(tarjeta, image=img_ojo, bg="white",
                               cursor="hand2")
            lbl_ojo.image = img_ojo
            lbl_ojo.pack(side="right", padx=10)
            lbl_ojo.bind("<Button-1>",
                         lambda e, t=turno: self._ver_detalle_turno(t))
        except Exception:
            tk.Label(tarjeta, text="👁", bg="white",
                     font=("Poppins", 14), cursor="hand2").pack(
                side="right", padx=10)

    def _foto_empleada(self, frame_padre, nombre_foto):
        size = 45
        try:
            if nombre_foto:
                ruta = os.path.join("assets", "fotos_perfil", nombre_foto)
                img = Image.open(ruta).resize((size, size), Image.LANCZOS)
            else:
                raise FileNotFoundError
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)
            foto = ImageTk.PhotoImage(img)
        except Exception:
            ruta_default = os.path.join("assets", "user_rosa.png")
            try:
                img = Image.open(ruta_default).resize(
                    (size, size), Image.LANCZOS)
                foto = ImageTk.PhotoImage(img)
            except Exception:
                tk.Label(frame_padre, text="👤", bg="white",
                         font=("Poppins", 18)).pack()
                return

        lbl = tk.Label(frame_padre, image=foto, bg="white")
        lbl.image = foto
        lbl.pack()

    def _ver_detalle_turno(self, turno):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id_turno, t.fecha_hora, t.estado, t.precio_total,
                       t.sena_pagada, t.total_pagado, t.duracion,
                       t.observaciones,
                       GROUP_CONCAT(s.nombre SEPARATOR ', ') AS servicios,
                       p_cli.nombre AS cli_nombre,
                       p_cli.apellido AS cli_apellido,
                       p_emp.nombre AS emp_nombre,
                       p_emp.apellido AS emp_apellido,
                       u_emp.foto AS emp_foto
                FROM turnos t
                LEFT JOIN turno_servicio ts ON t.id_turno = ts.id_turno
                LEFT JOIN servicios s ON ts.id_servicio = s.id_servicio
                JOIN clientes c ON t.id_cliente = c.id_cliente
                JOIN personas p_cli ON c.id_persona = p_cli.id_persona
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                JOIN usuarios u_emp ON e.id_usuario = u_emp.id_usuario
                WHERE t.id_turno = %s
                GROUP BY t.id_turno
            """, (turno["id_turno"],))
            turno_completo = cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
            return
        finally:
            cerrar_conexion(conexion, cursor)

        if not turno_completo:
            return

        for widget in self.area_contenido.winfo_children():
            widget.destroy()
        self.menu_activo = "Ver turnos"
        from vistas.turnos import VistaTurnos
        vista = VistaTurnos(self.area_contenido, self)
        vista._mostrar_detalles(turno_completo)

    def _mostrar_turnos_dia(self, fecha, frame_padre):
        for widget in frame_padre.winfo_children():
            widget.destroy()

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.fecha_hora,
                       p_emp.nombre AS emp_nombre,
                       p_emp.apellido AS emp_apellido,
                       GROUP_CONCAT(s.nombre SEPARATOR ', ') AS servicios
                FROM turnos t
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                LEFT JOIN turno_servicio ts ON t.id_turno = ts.id_turno
                LEFT JOIN servicios s ON ts.id_servicio = s.id_servicio
                WHERE DATE(t.fecha_hora) = %s
                AND t.estado = 'programado'
                GROUP BY t.id_turno
                ORDER BY t.fecha_hora ASC
            """, (fecha,))
            turnos = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            turnos = []
        finally:
            cerrar_conexion(conexion, cursor)

        fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(
            fecha, "strftime") else str(fecha)

        tk.Label(
            frame_padre,
            text=f"Turnos del {fecha_str}:",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 11)
        ).pack(anchor="w")

        if not turnos:
            tk.Label(
                frame_padre,
                text="Aún no se registró ninguna cita.",
                bg="#F9F0F2", fg="#999999",
                font=("Poppins", 10)
            ).pack(anchor="w", pady=4)
            return

        for t in turnos:
            hora = t["fecha_hora"].strftime("%H:%M")
            nombre = f"{t['emp_nombre']} {t['emp_apellido']}"
            texto = f"• {hora}hs — {nombre} — {t.get('servicios', '—')}"
            tk.Label(
                frame_padre,
                text=texto,
                bg="#F9F0F2", fg="#555555",
                font=("Poppins", 10)
            ).pack(anchor="w", pady=2)