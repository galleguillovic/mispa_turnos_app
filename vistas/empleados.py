import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk, ImageDraw

class VistaEmpleados(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._ico_buscar = None
        self._mostrar_listado()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # HELPERS
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
                SELECT e.id_empleado, e.especialidad, e.dias_trabajo,
                       p.nombre, p.apellido, p.dni, p.telefono, p.email,
                       u.id_usuario, u.nombre_usuario, u.rol, u.foto
                FROM empleados e
                JOIN personas p ON e.id_persona = p.id_persona
                JOIN usuarios u ON e.id_usuario = u.id_usuario
                WHERE e.activo = 1
            """
            if busqueda:
                query += " AND (p.nombre LIKE %s OR p.apellido LIKE %s)"
                cursor.execute(query + " ORDER BY p.apellido",
                               (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cursor.execute(query + " ORDER BY p.apellido")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _obtener_servicios(self):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_servicio, nombre FROM servicios
                WHERE activo = 1 ORDER BY nombre
            """)
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

        tk.Label(
            frame_top,
            text="Empleados y usuarios",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(side="left")

        # Buscador
        frame_buscar = tk.Frame(frame_top, bg="white",
                                highlightbackground="#D68092",
                                highlightthickness=1)
        frame_buscar.pack(side="right", padx=(10, 0), ipady=2)

        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar())

        tk.Entry(
            frame_buscar,
            textvariable=self.var_buscar,
            font=("Poppins", 11),
            bd=0, width=20
        ).pack(side="left", padx=(8, 4), pady=4)

        ruta_buscar = os.path.join("assets", "ico_buscar.png")
        self._ico_buscar = self._colorear_icono(
            ruta_buscar, (214, 128, 146))
        if self._ico_buscar:
            tk.Label(frame_buscar, image=self._ico_buscar,
                     bg="white").pack(side="left", padx=(0, 8))

        # Botón agregar
        tk.Button(
            frame_top,
            text="Agregar empleado",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._mostrar_formulario_agregar
        ).pack(side="right", ipady=4, ipadx=10, padx=(0, 10))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(8, 15))

        # Scroll
        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#F9F0F2", highlightthickness=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)
        self.frame_lista = tk.Frame(canvas, bg="#F9F0F2")
        self.frame_lista.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        self._canvas_id = canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            self._canvas_id, width=e.width))
        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._cargar_tarjetas()

    def _filtrar(self):
        busqueda = self.var_buscar.get()
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        empleados = self._obtener_empleados(busqueda)
        self._renderizar_tarjetas(empleados)

    def _cargar_tarjetas(self):
        self._renderizar_tarjetas(self._obtener_empleados())

    def _renderizar_tarjetas(self, empleados):
        if not empleados:
            tk.Label(
                self.frame_lista,
                text="No hay empleados cargados.",
                bg="#F9F0F2", fg="#999999",
                font=("Poppins", 11)
            ).pack(pady=30)
            return
        for emp in empleados:
            self._crear_tarjeta(emp)

    def _crear_tarjeta(self, emp):
        tarjeta = tk.Frame(
            self.frame_lista, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", pady=8, expand= True)

        # Foto
        frame_foto = tk.Frame(tarjeta, bg="white")
        frame_foto.pack(side="left", padx=(20, 15), pady=15, anchor="n")

        ruta_foto = None
        if emp.get("foto"):
            ruta_foto = os.path.join("assets", "fotos_perfil", emp["foto"])

        foto = self._foto_circular(ruta_foto, size=80)
        if foto:
            lbl_foto = tk.Label(frame_foto, image=foto, bg="white")
            lbl_foto.image = foto
            lbl_foto.pack()

        # Info + botones
        frame_derecha = tk.Frame(tarjeta, bg="white")
        frame_derecha.pack(side="left", fill="both", expand=True,
                           pady=15, padx=(0, 20))

        nombre_completo = f"{emp['nombre']} {emp['apellido']}"
        tk.Label(
            frame_derecha,
            text=nombre_completo,
            bg="white", fg="#333333",
            font=("Poppins ExtraBold", 13)
        ).pack(anchor="w")

        campos = [
            ("Usuario asociado", emp.get("nombre_usuario") or "—"),
            ("Rol", emp.get("rol") or "—"),
            ("DNI", str(emp.get("dni")) if emp.get("dni") else "—"),
            ("Correo electrónico", emp.get("email") or "—"),
            ("Teléfono", emp.get("telefono") or "—"),
            ("Servicio/Especialidad(es)", emp.get("especialidad") or "—"),
            ("Días de trabajo", emp.get("dias_trabajo") or "—"),
        ]

        for etiqueta, valor in campos:
            fila = tk.Frame(frame_derecha, bg="white")
            fila.pack(anchor="w", pady=1)
            tk.Label(fila, text=f"{etiqueta}:", bg="white",
                     fg="#555555",
                     font=("Poppins ExtraBold", 10)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white",
                     fg="#555555",
                     font=("Poppins", 10),
                     wraplength=600,
                     justify="left").pack(side="left")

        # Botones abajo de la info
        frame_btns = tk.Frame(frame_derecha, bg="white")
        frame_btns.pack(anchor="e", pady=(10, 0))

        tk.Button(
            frame_btns,
            text="Editar información",
            bg="#D68092", fg="white",
            font=("Poppins", 10),
            bd=0, relief="flat", cursor="hand2",
            command=lambda e=emp: self._mostrar_formulario_editar(e)
        ).pack(side="left", ipadx=10, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Eliminar",
            bg="#D68092", fg="white",
            font=("Poppins", 10),
            bd=0, relief="flat", cursor="hand2",
            command=lambda e=emp: self._confirmar_eliminar(e)
        ).pack(side="left", ipadx=10, ipady=6)

    # CONFIRMAR ELIMINAR
    def _confirmar_eliminar(self, emp):
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.configure(bg="#EEEEEE")
        popup.grab_set()

        nombre = f"{emp['nombre']} {emp['apellido']}"
        ancho = max(420, len(nombre) * 9 + 100)
        alto = 170
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (ancho // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            popup,
            text=f"Estás a punto de eliminar a {nombre}\ny su cuenta asociada, ¿estás seguro?",
            bg="#EEEEEE", fg="#333333",
            font=("Poppins", 11),
            justify="center",
            wraplength=ancho - 40
        ).pack(pady=(25, 15))

        frame_btns = tk.Frame(popup, bg="#EEEEEE")
        frame_btns.pack()

        tk.Button(
            frame_btns,
            text="Eliminar",
            bg="white", fg="black",
            font=("Poppins ExtraBold", 11, "italic"),
            bd=1, relief="solid", cursor="hand2",
            command=lambda: self._eliminar_empleado(emp, popup)
        ).pack(side="left", ipadx=20, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="white", fg="#333333",
            font=("Poppins", 11),
            bd=1, relief="solid", cursor="hand2",
            command=popup.destroy
        ).pack(side="left", ipadx=20, ipady=6)

    def _eliminar_empleado(self, emp, popup):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE empleados SET activo = 0 WHERE id_empleado = %s",
                (emp["id_empleado"],))
            cursor.execute(
                "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s",
                (emp["id_usuario"],))
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIOS
    def _mostrar_formulario_agregar(self):
        self._limpiar()
        self._construir_formulario_con_scroll(modo="agregar")

    def _mostrar_formulario_editar(self, emp):
        self._limpiar()
        self._construir_formulario_con_scroll(modo="editar", emp=emp)

    def _construir_formulario_con_scroll(self, modo, emp=None):
        titulo = "Agregar nuevo empleado y usuario" if modo == "agregar" \
            else "Editar información del empleado"

        tk.Label(
            self, text=titulo,
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 10))

        # Scroll vertical
        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#F9F0F2", highlightthickness=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)

        frame_scroll = tk.Frame(canvas, bg="#F9F0F2")
        frame_scroll.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas_id = canvas.create_window((0, 0), window=frame_scroll,
                                         anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            canvas_id, width=e.width))

        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Tarjeta dentro del scroll
        tarjeta = tk.Frame(
            frame_scroll, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", pady=(0, 20))

        self._construir_formulario(modo, emp, tarjeta)

    def _construir_formulario(self, modo, emp=None, tarjeta=None):
        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        # Foto + Nombre + Apellido
        frame_fila1 = tk.Frame(form, bg="white")
        frame_fila1.pack(fill="x", pady=(0, 10))

        self._foto_ref = None
        frame_foto = tk.Frame(frame_fila1, bg="white")
        frame_foto.pack(side="left", padx=(0, 20))

        ruta_foto = None
        if emp and emp.get("foto"):
            ruta_foto = os.path.join("assets", "fotos_perfil", emp["foto"])

        foto = self._foto_circular(ruta_foto, size=80)
        if foto:
            self._foto_ref = foto
            tk.Label(frame_foto, image=foto, bg="white").pack()

        frame_nombres = tk.Frame(frame_fila1, bg="white")
        frame_nombres.pack(side="left", fill="x", expand=True)

        tk.Label(frame_nombres, text="Nombre(s)*:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_nombres, text="Apellido(s)*:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.entry_nombre = tk.Entry(
            frame_nombres, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_nombre.grid(row=1, column=0, sticky="ew",
                               ipady=8, pady=(4, 10))

        self.entry_apellido = tk.Entry(
            frame_nombres, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_apellido.grid(row=1, column=1, sticky="ew",
                                 ipady=8, pady=(4, 10), padx=(20, 0))

        tk.Label(frame_nombres, text="DNI:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=2, column=0, sticky="w")
        tk.Label(frame_nombres, text="Teléfono:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=2, column=1, sticky="w", padx=(20, 0))

        self.entry_dni = tk.Entry(
            frame_nombres, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_dni.grid(row=3, column=0, sticky="ew",
                            ipady=8, pady=(4, 0))

        self.entry_telefono = tk.Entry(
            frame_nombres, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_telefono.grid(row=3, column=1, sticky="ew",
                                 ipady=8, pady=(4, 0), padx=(20, 0))

        frame_nombres.columnconfigure(0, weight=1)
        frame_nombres.columnconfigure(1, weight=1)

        # Correo y Usuario
        frame_fila2 = tk.Frame(form, bg="white")
        frame_fila2.pack(fill="x", pady=(10, 0))

        tk.Label(frame_fila2, text="Correo electrónico:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_fila2, text="Nombre de usuario:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.entry_email = tk.Entry(
            frame_fila2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_email.grid(row=1, column=0, sticky="ew",
                              ipady=8, pady=(4, 10))

        self.entry_usuario = tk.Entry(
            frame_fila2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_usuario.grid(row=1, column=1, sticky="ew",
                                ipady=8, pady=(4, 10), padx=(20, 0))

        frame_fila2.columnconfigure(0, weight=1)
        frame_fila2.columnconfigure(1, weight=1)

        # Servicios y Días de trabajo
        frame_fila3 = tk.Frame(form, bg="white")
        frame_fila3.pack(fill="x", pady=(0, 0))

        tk.Label(frame_fila3, text="Servicios/Especialidades:*",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=0, column=0, sticky="w")
        tk.Label(frame_fila3, text="Día(s) de trabajo (op):",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=0, column=1, sticky="w",
                                            padx=(20, 0))

        servicios = self._obtener_servicios()
        self.servicios_data = {s["nombre"]: s["id_servicio"]
                               for s in servicios}

        frame_listbox = tk.Frame(frame_fila3, bg="white")
        frame_listbox.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        self.listbox_servicios = tk.Listbox(
            frame_listbox,
            selectmode="multiple",
            font=("Poppins", 10),
            bg="#EEEEEE", bd=0,
            height=4,
            exportselection=False
        )
        scroll_lb = ttk.Scrollbar(frame_listbox, orient="vertical",
                                  command=self.listbox_servicios.yview)
        self.listbox_servicios.configure(yscrollcommand=scroll_lb.set)
        self.listbox_servicios.pack(side="left", fill="x", expand=True)
        scroll_lb.pack(side="right", fill="y")

        for nombre in self.servicios_data.keys():
            self.listbox_servicios.insert(tk.END, nombre)

        self.entry_dias = tk.Entry(
            frame_fila3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_dias.grid(row=1, column=1, sticky="ew",
                             ipady=8, pady=(4, 10), padx=(20, 0))

        frame_fila3.columnconfigure(0, weight=1)
        frame_fila3.columnconfigure(1, weight=1)

        # Rol y Contraseña
        frame_fila4 = tk.Frame(form, bg="white")
        frame_fila4.pack(fill="x", pady=(0, 10))

        tk.Label(frame_fila4, text="Rol:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")

        lbl_pass = "Contraseña:*" if modo == "agregar" \
            else "Contraseña: (dejar vacío para no cambiar)"
        tk.Label(frame_fila4, text=lbl_pass, bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.var_rol = tk.StringVar(value="estandar")
        combo_rol = ttk.Combobox(
            frame_fila4,
            textvariable=self.var_rol,
            values=["estandar", "administrador"],
            state="readonly",
            font=("Poppins", 11)
        )
        combo_rol.grid(row=1, column=0, sticky="ew",
                       ipady=6, pady=(4, 0))

        self.entry_contrasena = tk.Entry(
            frame_fila4, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", show="*")
        self.entry_contrasena.grid(row=1, column=1, sticky="ew",
                                   ipady=8, pady=(4, 0), padx=(20, 0))

        frame_fila4.columnconfigure(0, weight=1)
        frame_fila4.columnconfigure(1, weight=1)

        # Prellenar si es editar
        if modo == "editar" and emp:
            self.entry_nombre.insert(0, emp.get("nombre", ""))
            self.entry_apellido.insert(0, emp.get("apellido", ""))
            if emp.get("dni"):
                self.entry_dni.insert(0, str(emp["dni"]))
            self.entry_telefono.insert(0, emp.get("telefono", ""))
            self.entry_email.insert(0, emp.get("email", ""))
            self.entry_usuario.insert(0, emp.get("nombre_usuario", ""))
            if emp.get("dias_trabajo"):
                self.entry_dias.insert(0, emp["dias_trabajo"])
            self.var_rol.set(emp.get("rol", "estandar"))

            if emp.get("especialidad"):
                servicios_emp = [s.strip()
                                 for s in emp["especialidad"].split(",")]
                for i, nombre in enumerate(self.servicios_data.keys()):
                    if nombre in servicios_emp:
                        self.listbox_servicios.selection_set(i)

        # Botones
        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(0, 20))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._mostrar_listado
        ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        texto_btn = "Aceptar" if modo == "agregar" else "Guardar cambios"
        tk.Button(
            frame_btns,
            text=texto_btn,
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._guardar(modo, emp)
        ).pack(side="left", ipadx=15, ipady=8)

    # GUARDAR
    def _guardar(self, modo, emp=None):
        from utils.helpers import hashear_contrasena
        from db.conexion import obtener_conexion, cerrar_conexion

        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()
        usuario = self.entry_usuario.get().strip()
        dias = self.entry_dias.get().strip()
        rol = self.var_rol.get()
        contrasena = self.entry_contrasena.get().strip()

        # Servicios seleccionados
        seleccionados = self.listbox_servicios.curselection()
        nombres_servicios = [list(self.servicios_data.keys())[i]
                             for i in seleccionados]
        especialidad = ", ".join(nombres_servicios)

        # Validaciones
        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if not apellido:
            messagebox.showwarning("Atención", "El apellido es obligatorio.")
            return
        if not telefono:
            messagebox.showwarning("Atención", "El teléfono es obligatorio.")
            return
        if not email:
            messagebox.showwarning("Atención",
                                   "El correo electrónico es obligatorio.")
            return
        if not usuario:
            messagebox.showwarning("Atención",
                                   "El nombre de usuario es obligatorio.")
            return
        if not especialidad:
            messagebox.showwarning("Atención",
                                   "Seleccioná al menos un servicio.")
            return
        if modo == "agregar" and not contrasena:
            messagebox.showwarning("Atención",
                                   "La contraseña es obligatoria.")
            return

        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()

            if modo == "agregar":
                hash_pass = hashear_contrasena(contrasena)

                cursor.execute("""
                    INSERT INTO personas
                    (nombre, apellido, dni, telefono, email)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, apellido, dni or None,
                      telefono, email))
                id_persona = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO usuarios
                    (id_persona, nombre_usuario, contrasena, rol, activo)
                    VALUES (%s, %s, %s, %s, 1)
                """, (id_persona, usuario, hash_pass, rol))
                id_usuario = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO empleados
                    (id_persona, id_usuario, especialidad, dias_trabajo,
                     activo)
                    VALUES (%s, %s, %s, %s, 1)
                """, (id_persona, id_usuario, especialidad,
                      dias or None))

            else:
                cursor.execute("""
                    UPDATE personas SET nombre=%s, apellido=%s,
                    dni=%s, telefono=%s, email=%s
                    WHERE id_persona = (
                        SELECT id_persona FROM empleados
                        WHERE id_empleado = %s)
                """, (nombre, apellido, dni or None,
                      telefono, email, emp["id_empleado"]))

                if contrasena:
                    hash_pass = hashear_contrasena(contrasena)
                    cursor.execute("""
                        UPDATE usuarios SET nombre_usuario=%s,
                        rol=%s, contrasena=%s
                        WHERE id_usuario=%s
                    """, (usuario, rol, hash_pass, emp["id_usuario"]))
                else:
                    cursor.execute("""
                        UPDATE usuarios SET nombre_usuario=%s, rol=%s
                        WHERE id_usuario=%s
                    """, (usuario, rol, emp["id_usuario"]))

                cursor.execute("""
                    UPDATE empleados SET especialidad=%s,
                    dias_trabajo=%s
                    WHERE id_empleado=%s
                """, (especialidad, dias or None, emp["id_empleado"]))

            conexion.commit()
            messagebox.showinfo("Éxito", "Empleado guardado correctamente.")
            self._mostrar_listado()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)