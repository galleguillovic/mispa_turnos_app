# servicios.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk


class VistaServicios(tk.Frame):
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

    # LISTADO PRINCIPAL

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

        tk.Button(frame_top, text="Agregar servicio",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=self._mostrar_formulario_agregar_servicio
                  ).pack(side="right", ipady=2, ipadx=10, padx=(0, 10))

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

        self.frame_servicios = tk.Frame(self.frame_scroll, bg="#F9F0F2")
        self.frame_servicios.pack(fill="x", pady=(0, 10))
        self._cargar_tarjetas_servicios()

        frame_esp_top = tk.Frame(self.frame_scroll, bg="#F9F0F2")
        frame_esp_top.pack(fill="x", pady=(10, 0))
        tk.Label(frame_esp_top, text="Especialidades",
                 bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)).pack(side="left")
        tk.Button(frame_esp_top, text="Agregar especialidad",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=self._mostrar_formulario_agregar_especialidad
                  ).pack(side="right", ipady=2, ipadx=10)

        tk.Frame(self.frame_scroll, bg="#D68092", height=2).pack(
            fill="x", pady=(8, 15))

        self.frame_especialidades = tk.Frame(self.frame_scroll, bg="#F9F0F2")
        self.frame_especialidades.pack(fill="x", pady=(0, 20))
        self._cargar_tarjetas_especialidades()

    # TARJETAS SERVICIOS

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
        tk.Label(frame_meta, text=f"${float(servicio['precio']):.2f}",
                 bg="white", fg="#555555",
                 font=("Poppins ExtraBold", 10)).pack(side="left")
        tk.Label(frame_meta, text="  ·  ", bg="white", fg="#CCCCCC",
                 font=("Poppins", 10)).pack(side="left")
        tk.Label(frame_meta,
                 text=self._duracion_a_texto(float(servicio["duracion"])),
                 bg="white", fg="#555555",
                 font=("Poppins", 10)).pack(side="left")

        # Íconos 👁(ver), ✎(editar), 🗑(eliminar)
        frame_iconos = tk.Frame(tarjeta, bg="white")
        frame_iconos.pack(anchor="e", padx=12, pady=(0, 10))

        acciones = [
            ("ojo",    lambda s=servicio: self._mostrar_detalles(s)),
            ("lapiz",  lambda s=servicio: self._mostrar_formulario_editar_servicio(s)),
            ("basura", lambda s=servicio: self._confirmar_eliminar_servicio(s)),
        ]
        fallbacks = {"ojo": "👁", "lapiz": "✎", "basura": "🗑"}

        for nombre_ico, comando in acciones:
            ico = self._get_ico(nombre_ico)
            if ico:
                lbl = tk.Label(frame_iconos, image=ico,
                               bg="white", cursor="hand2")
                lbl.pack(side="left", padx=4)
                lbl.bind("<Button-1>", lambda e, cmd=comando: cmd())
            else:
                tk.Label(frame_iconos, text=fallbacks[nombre_ico],
                         bg="white", font=("Poppins", 13),
                         cursor="hand2").pack(side="left", padx=4)

    # DETALLES SERVICIO

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
        frame_info.pack(fill="x", padx=25, pady=(0, 10))

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

        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(10, 20))

        tk.Button(frame_btns, text="Editar información",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: self._mostrar_formulario_editar_servicio(
                      servicio)
                  ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))
        tk.Button(frame_btns, text="Eliminar servicio",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: self._confirmar_eliminar_servicio(servicio)
                  ).pack(side="left", ipadx=15, ipady=8)

    # TARJETAS ESPECIALIDADES

    def _cargar_tarjetas_especialidades(self):
        self._renderizar_tarjetas_especialidades(self._obtener_especialidades())

    def _renderizar_tarjetas_especialidades(self, especialidades):
        if not especialidades:
            tk.Label(self.frame_especialidades,
                     text="No hay especialidades cargadas.",
                     bg="#F9F0F2", fg="#999999",
                     font=("Poppins", 11)).pack(anchor="w", pady=10)
            return
        for esp in especialidades:
            self._crear_tarjeta_especialidad(self.frame_especialidades, esp)

    def _crear_tarjeta_especialidad(self, frame_padre, especialidad):
        tarjeta = tk.Frame(frame_padre, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.pack(fill="x", pady=6)

        frame_texto = tk.Frame(tarjeta, bg="white")
        frame_texto.pack(side="left", fill="x", expand=True, padx=20, pady=12)

        tk.Label(frame_texto, text=especialidad["nombre"],
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 12)).pack(anchor="w")
        tk.Label(frame_texto,
                 text=especialidad.get("descripcion") or "—",
                 bg="white", fg="#555555", font=("Poppins", 10),
                 wraplength=550, justify="left").pack(anchor="w")

        # Botones visibles a la derecha
        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(side="right", padx=20, pady=12)

        tk.Button(frame_btns, text="Editar información",
                  bg="#D68092", fg="white", font=("Poppins", 10),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda e=especialidad:
                      self._mostrar_formulario_editar_especialidad(e)
                  ).pack(side="left", ipadx=10, ipady=6, padx=(0, 8))
        tk.Button(frame_btns, text="Eliminar",
                  bg="#D68092", fg="white", font=("Poppins", 10),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda e=especialidad:
                      self._confirmar_eliminar_especialidad(e)
                  ).pack(side="left", ipadx=10, ipady=6)

    # POPUPS / ELIMINAR

    def _confirmar_eliminar_servicio(self, servicio):
        self._popup_confirmar(
            nombre=servicio["nombre"],
            accion=lambda popup: self._eliminar_servicio(servicio, popup))

    def _confirmar_eliminar_especialidad(self, especialidad):
        self._popup_confirmar(
            nombre=especialidad["nombre"],
            accion=lambda popup: self._eliminar_especialidad(
                especialidad, popup))

    def _popup_confirmar(self, nombre, accion):
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.configure(bg="#EEEEEE")
        popup.grab_set()

        ancho = max(420, len(nombre) * 9 + 100)
        alto  = 160
        x = self.winfo_rootx() + (self.winfo_width()  // 2) - (ancho // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (alto  // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(popup,
                 text=f"Estás a punto de eliminar \"{nombre}\"\n"
                      "y su información asociada, ¿estás seguro?",
                 bg="#EEEEEE", fg="#333333",
                 font=("Poppins", 11), justify="center",
                 wraplength=ancho - 40).pack(pady=(25, 15))

        frame_btns = tk.Frame(popup, bg="#EEEEEE")
        frame_btns.pack()

        tk.Button(frame_btns, text="Eliminar",
                  bg="white", fg="black",
                  font=("Poppins ExtraBold", 11, "italic"),
                  bd=1, relief="solid", cursor="hand2",
                  command=lambda: accion(popup)
                  ).pack(side="left", ipadx=20, ipady=6, padx=(0, 10))
        tk.Button(frame_btns, text="Cancelar",
                  bg="white", fg="#333333", font=("Poppins", 11),
                  bd=1, relief="solid", cursor="hand2",
                  command=popup.destroy
                  ).pack(side="left", ipadx=20, ipady=6)

    def _eliminar_servicio(self, servicio, popup):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE servicios SET activo = 0 WHERE id_servicio = %s",
                (servicio["id_servicio"],))
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    def _eliminar_especialidad(self, especialidad, popup):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT COUNT(*) AS total FROM servicios "
                "WHERE id_especialidad = %s AND activo = 1",
                (especialidad["id_especialidad"],))
            res   = cursor.fetchone()
            total = res["total"] if isinstance(res, dict) else res[0]
            if total > 0:
                popup.destroy()
                messagebox.showwarning(
                    "No se puede eliminar",
                    f"La especialidad '{especialidad['nombre']}' está siendo "
                    f"usada por {total} servicio(s) activo(s).\n"
                    "Reasigná o eliminá esos servicios primero.")
                return
            cursor.execute(
                "DELETE FROM especialidades WHERE id_especialidad = %s",
                (especialidad["id_especialidad"],))
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito",
                                "Especialidad eliminada correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIOS SERVICIO

    def _mostrar_formulario_agregar_servicio(self):
        self._limpiar()
        self._construir_formulario_servicio(modo="agregar")

    def _mostrar_formulario_editar_servicio(self, servicio):
        self._limpiar()
        self._construir_formulario_servicio(modo="editar", servicio=servicio)

    def _construir_formulario_servicio(self, modo, servicio=None):
        titulo = "Agregar un servicio" if modo == "agregar" \
            else "Editar información del servicio"

        tk.Label(self, text=titulo, bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)
                 ).pack(anchor="w", padx=30, pady=(20, 0))
        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 20))

        tarjeta = tk.Frame(self, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(form, text="Nombre del servicio*:",
                 bg="white", fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
        self.entry_nombre = tk.Entry(
            form, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", width=70)
        self.entry_nombre.grid(row=1, column=0, columnspan=3,
                               sticky="ew", ipady=8, pady=(0, 15))

        for col_i, texto in enumerate(["Duración:*", "Precio:*", "Especialidad:*"]):
            tk.Label(form, text=texto, bg="white", fg="#333333",
                     font=("Poppins", 11)).grid(
                row=2, column=col_i, sticky="w",
                padx=(20 if col_i > 0 else 0, 0))

        self.entry_duracion = tk.Entry(
            form, font=("Poppins", 11), bg="#EEEEEE", bd=0, relief="flat")
        self.entry_duracion.grid(row=3, column=0, sticky="ew",
                                 ipady=8, pady=(4, 15))

        self.entry_precio = tk.Entry(
            form, font=("Poppins", 11), bg="#EEEEEE", bd=0, relief="flat")
        self.entry_precio.grid(row=3, column=1, sticky="ew",
                               ipady=8, pady=(4, 15), padx=(20, 0))

        especialidades = self._obtener_especialidades()
        self.esp_nombres = [e["nombre"] for e in especialidades]
        self.esp_ids     = {e["nombre"]: e["id_especialidad"]
                            for e in especialidades}
        self.var_especialidad = tk.StringVar()
        ttk.Combobox(form, textvariable=self.var_especialidad,
                     values=self.esp_nombres, state="readonly",
                     font=("Poppins", 11)
                     ).grid(row=3, column=2, sticky="ew",
                            ipady=6, pady=(4, 15), padx=(20, 0))

        tk.Label(form, text="Descripción:*", bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(
            row=4, column=0, columnspan=3, sticky="w")
        self.text_descripcion = tk.Text(
            form, font=("Poppins", 11), bg="#EEEEEE",
            bd=0, relief="flat", height=3)
        self.text_descripcion.grid(row=5, column=0, columnspan=3,
                                   sticky="ew", pady=(4, 15))

        tk.Label(form, text="Protocolos:", bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(
            row=6, column=0, columnspan=3, sticky="w")
        self.text_protocolos = tk.Text(
            form, font=("Poppins", 11), bg="#EEEEEE",
            bd=0, relief="flat", height=3)
        self.text_protocolos.grid(row=7, column=0, columnspan=3,
                                  sticky="ew", pady=(4, 15))

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)

        self.entry_duracion.insert(0, "Ej: 1.5")
        self.entry_duracion.config(fg="#999999")
        self.entry_duracion.bind("<FocusIn>",  lambda e: (
            self.entry_duracion.delete(0, tk.END),
            self.entry_duracion.config(fg="black"))
            if self.entry_duracion.get() == "Ej: 1.5" else None)
        self.entry_duracion.bind("<FocusOut>", lambda e: (
            self.entry_duracion.insert(0, "Ej: 1.5"),
            self.entry_duracion.config(fg="#999999"))
            if self.entry_duracion.get() == "" else None)

        if modo == "editar" and servicio:
            self.entry_nombre.insert(0, servicio["nombre"])
            self.entry_duracion.delete(0, tk.END)
            self.entry_duracion.config(fg="black")
            self.entry_duracion.insert(0, str(servicio["duracion"]))
            self.entry_precio.insert(0, str(servicio["precio"]))
            if servicio.get("especialidad_nombre") in self.esp_nombres:
                self.var_especialidad.set(servicio["especialidad_nombre"])
            if servicio.get("descripcion"):
                self.text_descripcion.insert("1.0", servicio["descripcion"])
            if servicio.get("protocolos"):
                self.text_protocolos.insert("1.0", servicio["protocolos"])

        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(0, 20))

        tk.Button(frame_btns, text="Cancelar",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=self._mostrar_listado
                  ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))
        tk.Button(frame_btns, text="Guardar cambios",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: self._guardar_servicio(modo, servicio)
                  ).pack(side="left", ipadx=15, ipady=8)

    # GUARDAR SERVICIO

    def _guardar_servicio(self, modo, servicio=None):
        nombre       = self.entry_nombre.get().strip()
        dur_str      = self.entry_duracion.get().strip()
        precio_str   = self.entry_precio.get().strip()
        especialidad = self.var_especialidad.get()
        descripcion  = self.text_descripcion.get("1.0", tk.END).strip()
        protocolos   = self.text_protocolos.get("1.0", tk.END).strip()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if dur_str in ("Ej: 1.5", ""):
            messagebox.showwarning("Atención", "La duración es obligatoria.")
            return
        try:
            duracion = float(dur_str)
        except ValueError:
            messagebox.showwarning("Atención",
                                   "La duración debe ser un número. Ej: 1.5")
            return
        if not precio_str:
            messagebox.showwarning("Atención", "El precio es obligatorio.")
            return
        try:
            precio = float(precio_str)
        except ValueError:
            messagebox.showwarning("Atención",
                                   "El precio debe ser un número.")
            return
        if not especialidad:
            messagebox.showwarning("Atención", "Seleccioná una especialidad.")
            return
        if not descripcion:
            messagebox.showwarning("Atención",
                                   "La descripción es obligatoria.")
            return

        id_especialidad = self.esp_ids[especialidad]

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            if modo == "agregar":
                cursor.execute("""
                    INSERT INTO servicios
                    (id_especialidad, nombre, descripcion, precio,
                     duracion, protocolos, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                """, (id_especialidad, nombre, descripcion,
                      precio, duracion, protocolos or None))
            else:
                cursor.execute("""
                    UPDATE servicios SET
                        id_especialidad=%s, nombre=%s, descripcion=%s,
                        precio=%s, duracion=%s, protocolos=%s
                    WHERE id_servicio=%s
                """, (id_especialidad, nombre, descripcion,
                      precio, duracion, protocolos or None,
                      servicio["id_servicio"]))
            conexion.commit()
            messagebox.showinfo("Éxito", "Servicio guardado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIOS ESPECIALIDAD

    def _mostrar_formulario_agregar_especialidad(self):
        self._limpiar()
        self._construir_formulario_especialidad(modo="agregar")

    def _mostrar_formulario_editar_especialidad(self, especialidad):
        self._limpiar()
        self._construir_formulario_especialidad(
            modo="editar", especialidad=especialidad)

    def _construir_formulario_especialidad(self, modo, especialidad=None):
        titulo = "Agregar una especialidad" if modo == "agregar" \
            else "Editar información de la especialidad"

        tk.Label(self, text=titulo, bg="#F9F0F2", fg="#D68092",
                 font=("Poppins ExtraBold", 18)
                 ).pack(anchor="w", padx=30, pady=(20, 0))
        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 20))

        tarjeta = tk.Frame(self, bg="white",
                           highlightbackground="#D68092", highlightthickness=1)
        tarjeta.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(form, text="Nombre de la especialidad*:",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).pack(anchor="w", pady=(0, 4))
        self.entry_esp_nombre = tk.Entry(
            form, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_esp_nombre.pack(fill="x", ipady=8, pady=(0, 15))

        tk.Label(form, text="Descripción:*",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).pack(anchor="w")
        self.text_esp_descripcion = tk.Text(
            form, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", height=4)
        self.text_esp_descripcion.pack(fill="x", pady=(4, 15))

        if modo == "editar" and especialidad:
            self.entry_esp_nombre.insert(0, especialidad["nombre"])
            if especialidad.get("descripcion"):
                self.text_esp_descripcion.insert(
                    "1.0", especialidad["descripcion"])

        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(0, 20))

        tk.Button(frame_btns, text="Cancelar",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=self._mostrar_listado
                  ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))
        tk.Button(frame_btns, text="Guardar cambios",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: self._guardar_especialidad(
                      modo, especialidad)
                  ).pack(side="left", ipadx=15, ipady=8)

    # GUARDAR ESPECIALIDAD

    def _guardar_especialidad(self, modo, especialidad=None):
        nombre      = self.entry_esp_nombre.get().strip()
        descripcion = self.text_esp_descripcion.get("1.0", tk.END).strip()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if not descripcion:
            messagebox.showwarning("Atención",
                                   "La descripción es obligatoria.")
            return

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            if modo == "agregar":
                cursor.execute(
                    "INSERT INTO especialidades (nombre, descripcion) "
                    "VALUES (%s, %s)", (nombre, descripcion))
            else:
                cursor.execute(
                    "UPDATE especialidades SET nombre=%s, descripcion=%s "
                    "WHERE id_especialidad=%s",
                    (nombre, descripcion, especialidad["id_especialidad"]))
            conexion.commit()
            messagebox.showinfo("Éxito",
                                "Especialidad guardada correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)