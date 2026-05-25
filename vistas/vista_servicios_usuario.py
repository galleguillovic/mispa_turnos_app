# vistas/vista_servicios_usuario.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk


class VistaServiciosUsuario(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._ico_buscar = None
        self._iconos     = {}
        self._mostrar_listado()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # HELPERS
    def _duracion_a_texto(self, horas_float):
        try:
            horas   = int(horas_float)
            minutos = int(round((horas_float - horas) * 60))
            if horas > 0 and minutos > 0:
                return f"{horas}h {minutos}min"
            elif horas > 0:
                return f"{horas}h"
            else:
                return f"{minutos}min"
        except Exception:
            return str(horas_float)

    def _colorear_icono(self, ruta, color_rgb, size=(16, 16)):
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

    def _get_ico(self, nombre, color_rgb=(214, 128, 146), size=(16, 16)):
        key = (nombre, color_rgb, size)
        if key not in self._iconos:
            ruta = os.path.join("assets", f"ico_{nombre}.png")
            self._iconos[key] = self._colorear_icono(ruta, color_rgb, size)
        return self._iconos[key]

    # CONSULTAS DB
    def _obtener_servicios(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            if busqueda:
                cursor.execute("""
                    SELECT s.*, e.nombre AS especialidad_nombre
                    FROM servicios s
                    LEFT JOIN especialidades e
                           ON s.id_especialidad = e.id_especialidad
                    WHERE s.nombre LIKE %s AND s.activo = 1
                    ORDER BY s.nombre
                """, (f"%{busqueda}%",))
            else:
                cursor.execute("""
                    SELECT s.*, e.nombre AS especialidad_nombre
                    FROM servicios s
                    LEFT JOIN especialidades e
                           ON s.id_especialidad = e.id_especialidad
                    WHERE s.activo = 1 ORDER BY s.nombre
                """)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _obtener_especialidades(self):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_especialidad, nombre, descripcion "
                "FROM especialidades ORDER BY nombre")
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    # LISTADO

    def _mostrar_listado(self):
        self._limpiar()

        frame_top = tk.Frame(self, bg="#F9F0F2")
        frame_top.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(frame_top, text="Servicios",
                 bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)).pack(side="left")

        frame_buscar = tk.Frame(frame_top, bg="white",
                                highlightbackground="#D68092",
                                highlightthickness=1)
        frame_buscar.pack(side="right", padx=(10, 0), ipady=2)

        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar_servicios())

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
        self.frame_scroll = tk.Frame(canvas, bg="#F9F0F2")
        self.frame_scroll.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas_id = canvas.create_window(
            (0, 0), window=self.frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            canvas_id, width=e.width))

        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Servicios
        self.frame_servicios = tk.Frame(self.frame_scroll, bg="#F9F0F2")
        self.frame_servicios.pack(fill="x", pady=(0, 10))
        self._cargar_tarjetas_servicios()

        # Especialidades (solo lectura)
        tk.Label(self.frame_scroll, text="Especialidades",
                 bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)
                 ).pack(anchor="w", pady=(10, 0))
        tk.Frame(self.frame_scroll, bg="#D68092", height=2).pack(
            fill="x", pady=(8, 15))

        self.frame_especialidades = tk.Frame(self.frame_scroll, bg="#F9F0F2")
        self.frame_especialidades.pack(fill="x", pady=(0, 20))
        self._cargar_tarjetas_especialidades()

    # TARJETAS SERVICIOS (ícono 👁)

    def _filtrar_servicios(self):
        for w in self.frame_servicios.winfo_children():
            w.destroy()
        self._renderizar_tarjetas_servicios(
            self._obtener_servicios(self.var_buscar.get()))

    def _cargar_tarjetas_servicios(self):
        self._renderizar_tarjetas_servicios(self._obtener_servicios())

    def _renderizar_tarjetas_servicios(self, servicios):
        if not servicios:
            tk.Label(self.frame_servicios,
                     text="No hay servicios cargados.",
                     bg="#F9F0F2", fg="#999999",
                     font=("Poppins", 11)).grid(row=0, column=0, pady=10)
            return
        for i, s in enumerate(servicios):
            self._crear_tarjeta_servicio(
                self.frame_servicios, s, i // 2, i % 2)
        self.frame_servicios.columnconfigure(0, weight=1, minsize=380)
        self.frame_servicios.columnconfigure(1, weight=1, minsize=380)

    def _crear_tarjeta_servicio(self, frame_padre, servicio, fila, col):
        tarjeta = tk.Frame(frame_padre, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.grid(row=fila, column=col, padx=8, pady=8, sticky="nsew")

        contenido = tk.Frame(tarjeta, bg="white")
        contenido.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(contenido, text=servicio["nombre"],
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 12),
                 wraplength=300, justify="left").pack(anchor="w")

        tk.Label(contenido,
                 text=servicio.get("especialidad_nombre") or "—",
                 bg="white", fg="#D68092",
                 font=("Poppins", 10)).pack(anchor="w")

        frame_meta = tk.Frame(contenido, bg="white")
        frame_meta.pack(anchor="w", pady=(4, 0))
        tk.Label(frame_meta,
                 text=f"${float(servicio['precio']):.2f}",
                 bg="white", fg="#555555",
                 font=("Poppins ExtraBold", 10)).pack(side="left")
        tk.Label(frame_meta, text="  ·  ",
                 bg="white", fg="#CCCCCC",
                 font=("Poppins", 10)).pack(side="left")
        tk.Label(frame_meta,
                 text=self._duracion_a_texto(float(servicio["duracion"])),
                 bg="white", fg="#555555",
                 font=("Poppins", 10)).pack(side="left")

        # Ícono 👁
        frame_iconos = tk.Frame(tarjeta, bg="white")
        frame_iconos.pack(anchor="e", padx=12, pady=(0, 10))

        ico = self._get_ico("ojo")
        if ico:
            lbl = tk.Label(frame_iconos, image=ico,
                           bg="white", cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>",
                     lambda e, s=servicio: self._mostrar_detalles(s))
        else:
            tk.Label(frame_iconos, text="👁", bg="white",
                     font=("Poppins", 13), cursor="hand2",
                     ).pack(side="left", padx=4)

    # VISTA DETALLES SERVICIO

    def _mostrar_detalles(self, servicio):
        self._limpiar()

        tk.Label(self, text="Visualización detalles del servicio",
                 bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)
                 ).pack(anchor="w", padx=30, pady=(20, 0))
        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 10))
        tk.Button(self, text="← Volver", bg="#F9F0F2", fg="#D68092",
                  font=("Poppins", 11), bd=0, relief="flat", cursor="hand2",
                  command=self._mostrar_listado
                  ).pack(anchor="w", padx=30, pady=(0, 10))

        tarjeta = tk.Frame(self, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.pack(fill="x", padx=30, pady=(0, 20))

        frame_enc = tk.Frame(tarjeta, bg="white")
        frame_enc.pack(fill="x", padx=25, pady=(20, 10))

        try:
            img = Image.open(os.path.join(
                "assets", "user_rosa.png")).resize((70, 70), Image.LANCZOS)
            self._foto_srv = ImageTk.PhotoImage(img)
            tk.Label(frame_enc, image=self._foto_srv,
                     bg="white").pack(side="left", padx=(0, 15))
        except Exception:
            pass

        frame_titulo = tk.Frame(frame_enc, bg="white")
        frame_titulo.pack(side="left")
        tk.Label(frame_titulo, text="Información del servicio:",
                 bg="white", fg="#999999",
                 font=("Poppins", 12)).pack(anchor="w")
        tk.Label(frame_titulo, text=servicio["nombre"],
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 20),
                 wraplength=700, justify="left").pack(anchor="w")

        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(fill="x", padx=25, pady=(0, 20))

        for etiqueta, valor in [
            ("Especialidad", servicio.get("especialidad_nombre") or "—"),
            ("Precio",       f"${float(servicio['precio']):.2f}"),
            ("Duración",     self._duracion_a_texto(float(servicio["duracion"]))),
            ("Descripción",  servicio.get("descripcion") or "—"),
            ("Protocolos",   servicio.get("protocolos") or "—"),
        ]:
            fila = tk.Frame(frame_info, bg="white")
            fila.pack(anchor="w", pady=3)
            tk.Label(fila, text=f"{etiqueta}:", bg="white", fg="#555555",
                     font=("Poppins ExtraBold", 11)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white", fg="#555555",
                     font=("Poppins", 11),
                     wraplength=700, justify="left").pack(side="left")

    # ESPECIALIDADES (solo lectura)

    def _cargar_tarjetas_especialidades(self):
        especialidades = self._obtener_especialidades()
        if not especialidades:
            tk.Label(self.frame_especialidades,
                     text="No hay especialidades cargadas.",
                     bg="#F9F0F2", fg="#999999",
                     font=("Poppins", 11)).pack(anchor="w", pady=10)
            return

        for esp in especialidades:
            tarjeta = tk.Frame(self.frame_especialidades, bg="white",
                               highlightbackground="#D68092",
                               highlightthickness=1)
            tarjeta.pack(fill="x", pady=6)

            contenido = tk.Frame(tarjeta, bg="white")
            contenido.pack(fill="x", padx=20, pady=12)

            tk.Label(contenido, text=esp["nombre"],
                     bg="white", fg="#333333",
                     font=("Poppins ExtraBold", 12)).pack(anchor="w")
            tk.Label(contenido,
                     text=esp.get("descripcion") or "—",
                     bg="white", fg="#555555",
                     font=("Poppins", 10),
                     wraplength=800, justify="left").pack(anchor="w")