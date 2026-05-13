import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk, ImageDraw

class VistaClientes(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._ico_lapiz = None
        self._ico_ojo = None
        self._ico_buscar = None
        self._foto_user = None
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

    def _placeholder(self, entry, texto):
        entry.insert(0, texto)
        entry.config(fg="#BBBBBB")
        entry.bind("<FocusIn>", lambda e: self._limpiar_ph(entry, texto))
        entry.bind("<FocusOut>", lambda e: self._restaurar_ph(entry, texto))

    def _limpiar_ph(self, entry, texto):
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def _restaurar_ph(self, entry, texto):
        if entry.get() == "":
            entry.insert(0, texto)
            entry.config(fg="#BBBBBB")

    def _obtener_clientes(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            if busqueda:
                cursor.execute("""
                    SELECT c.id_cliente, c.preferencias, c.notas, c.estado,
                           p.id_persona, p.nombre, p.apellido, p.dni,
                           p.telefono, p.email
                    FROM clientes c
                    JOIN personas p ON c.id_persona = p.id_persona
                    WHERE c.estado != 'inactivo'
                    AND (p.nombre LIKE %s OR p.apellido LIKE %s)
                    ORDER BY p.apellido
                """, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cursor.execute("""
                    SELECT c.id_cliente, c.preferencias, c.notas, c.estado,
                           p.id_persona, p.nombre, p.apellido, p.dni,
                           p.telefono, p.email
                    FROM clientes c
                    JOIN personas p ON c.id_persona = p.id_persona
                    WHERE c.estado != 'inactivo'
                    ORDER BY p.apellido
                """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
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
            text="Listado de clientes",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(side="left")

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
        self._ico_buscar = self._colorear_icono(ruta_buscar, (214, 128, 146))
        if self._ico_buscar:
            tk.Label(frame_buscar, image=self._ico_buscar,
                     bg="white").pack(side="left", padx=(0, 8))

        tk.Button(
            frame_top,
            text="Agregar cliente",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._mostrar_formulario_agregar
        ).pack(side="right", ipady=4, ipadx=10, padx=(0, 10))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(8, 15))

        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Estilo Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cliente.Treeview",
                        background="white",
                        foreground="#333333",
                        rowheight=40,
                        fieldbackground="white",
                        font=("Poppins", 10),
                        borderwidth=0)
        style.configure("Cliente.Treeview.Heading",
                        background="#D68092",
                        foreground="white",
                        font=("Poppins ExtraBold", 11),
                        relief="flat")
        style.map("Cliente.Treeview",
                  background=[("selected", "#FADADD")],
                  foreground=[("selected", "#333333")])
        style.map("Cliente.Treeview.Heading",
                  background=[("active", "#C0607A")])

        self._ico_lapiz = self._colorear_icono(
            os.path.join("assets", "ico_lapiz.png"), (214, 128, 146))
        self._ico_ojo = self._colorear_icono(
            os.path.join("assets", "ico_ojo.png"), (214, 128, 146))

        # Treeview
        cols = ("nombre", "apellido", "telefono", "editar", "detalles")
        self.tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            style="Cliente.Treeview",
            selectmode="browse"
        )

        encabezados = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "telefono": "Teléfono",
            "editar": "Editar",
            "detalles": "Detalles"
        }
        anchos = {
            "nombre": 200,
            "apellido": 200,
            "telefono": 200,
            "editar": 80,
            "detalles": 80
        }

        for col in cols:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, anchor="center",
                             width=anchos[col], minwidth=60)

        # Tags
        self.tree.tag_configure("par", background="#FADADD")
        self.tree.tag_configure("impar", background="white")

        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Guardar clientes 
        self._clientes_cache = []
        self._cargar_filas()

        self.tree.bind("<ButtonRelease-1>", self._on_click_tabla)

    def _on_click_tabla(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return

        idx = self.tree.index(item)
        if idx >= len(self._clientes_cache):
            return
        cliente = self._clientes_cache[idx]

        if col == "#4":  # Editar
            self._mostrar_formulario_editar(cliente)
        elif col == "#5":  # Detalles
            self._mostrar_detalles(cliente)

    def _filtrar(self):
        busqueda = self.var_buscar.get()
        clientes = self._obtener_clientes(busqueda)
        self._renderizar_filas(clientes)

    def _cargar_filas(self):
        self._renderizar_filas(self._obtener_clientes())

    def _renderizar_filas(self, clientes):
        self.tree.delete(*self.tree.get_children())
        self._clientes_cache = clientes

        if not clientes:
            return

        for i, cliente in enumerate(clientes):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=(
                cliente.get("nombre", ""),
                cliente.get("apellido", ""),
                cliente.get("telefono", "—"),
                "✎",
                "👁"
            ), tags=(tag,))

    # DETALLES 
    def _mostrar_detalles(self, cliente):
        self._limpiar()

        tk.Label(
            self,
            text="Visualización detalles del cliente",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 20))

        tk.Button(
            self,
            text="← Volver",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._mostrar_listado
        ).pack(anchor="w", padx=30, pady=(0, 10))

        tarjeta = tk.Frame(
            self, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", padx=30, pady=(0, 20))

        # Encabezado
        frame_enc = tk.Frame(tarjeta, bg="white")
        frame_enc.pack(fill="x", padx=25, pady=(20, 10))

        ruta_user = os.path.join("assets", "user_rosa.png")
        try:
            img = Image.open(ruta_user).resize((70, 70), Image.LANCZOS)
            self._foto_user = ImageTk.PhotoImage(img)
            tk.Label(frame_enc, image=self._foto_user,
                     bg="white").pack(side="left", padx=(0, 15))
        except Exception:
            pass

        frame_nombre_enc = tk.Frame(frame_enc, bg="white")
        frame_nombre_enc.pack(side="left")

        tk.Label(
            frame_nombre_enc,
            text="Información del cliente:",
            bg="white", fg="#999999",
            font=("Poppins", 12)
        ).pack(anchor="w")

        nombre_completo = f"{cliente['nombre']} {cliente['apellido']}"
        tk.Label(
            frame_nombre_enc,
            text=nombre_completo,
            bg="white", fg="#333333",
            font=("Poppins ExtraBold", 20)
        ).pack(anchor="w")

        # Campos info
        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(fill="x", padx=25, pady=(0, 10))

        campos = [
            ("Teléfono", cliente.get("telefono") or "—"),
            ("DNI", str(cliente.get("dni")) if cliente.get("dni") else "—"),
            ("Correo electrónico", cliente.get("email") or "—"),
            ("Preferencias", cliente.get("preferencias") or "—"),
            ("Estado", cliente.get("estado") or "—"),
            ("Notas adicionales", cliente.get("notas") or "—"),
        ]

        for etiqueta, valor in campos:
            fila = tk.Frame(frame_info, bg="white")
            fila.pack(anchor="w", pady=3)
            tk.Label(fila, text=f"{etiqueta}:", bg="white",
                     fg="#555555",
                     font=("Poppins ExtraBold", 11)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white",
                     fg="#555555",
                     font=("Poppins", 11)).pack(side="left")

        # Botones
        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(10, 20))

        tk.Button(
            frame_btns,
            text="Editar información",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._mostrar_formulario_editar(cliente)
        ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Eliminar cliente",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._confirmar_eliminar(cliente)
        ).pack(side="left", ipadx=15, ipady=8)

    # CONFIRMAR ELIMINAR
    def _confirmar_eliminar(self, cliente):
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.configure(bg="#EEEEEE")
        popup.grab_set()

        nombre = f"{cliente['nombre']} {cliente['apellido']}"
        ancho = max(420, len(nombre) * 9 + 100)
        alto = 170
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (ancho // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            popup,
            text=f"Estás a punto de eliminar a {nombre}\ny su información, ¿estás seguro?",
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
            command=lambda: self._eliminar_cliente(cliente, popup)
        ).pack(side="left", ipadx=20, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="white", fg="#333333",
            font=("Poppins", 11),
            bd=1, relief="solid", cursor="hand2",
            command=popup.destroy
        ).pack(side="left", ipadx=20, ipady=6)

    def _eliminar_cliente(self, cliente, popup):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE clientes SET estado = 'inactivo' WHERE id_cliente = %s",
                (cliente["id_cliente"],))
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIOS
    def _mostrar_formulario_agregar(self):
        self._limpiar()
        self._construir_formulario(modo="agregar")

    def _mostrar_formulario_editar(self, cliente):
        self._limpiar()
        self._construir_formulario(modo="editar", cliente=cliente)

    def _construir_formulario(self, modo, cliente=None):
        titulo = "Agregar un nuevo cliente" if modo == "agregar" \
            else "Editar información del cliente"

        tk.Label(
            self, text=titulo,
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 20))

        tarjeta = tk.Frame(
            self, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", padx=30, pady=(0, 20))

        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        # ── Fila 1: Nombre, Apellido, Teléfono ──
        frame_f1 = tk.Frame(form, bg="white")
        frame_f1.pack(fill="x", pady=(0, 10))

        tk.Label(frame_f1, text="Nombre(s)*:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f1, text="Apellido(s)*:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))
        tk.Label(frame_f1, text="Teléfono:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=2, sticky="w", padx=(20, 0))

        self.entry_nombre = tk.Entry(
            frame_f1, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_nombre.grid(row=1, column=0, sticky="ew",
                               ipady=8, pady=(4, 0))

        self.entry_apellido = tk.Entry(
            frame_f1, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_apellido.grid(row=1, column=1, sticky="ew",
                                 ipady=8, pady=(4, 0), padx=(20, 0))

        self.entry_telefono = tk.Entry(
            frame_f1, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_telefono.grid(row=1, column=2, sticky="ew",
                                 ipady=8, pady=(4, 0), padx=(20, 0))

        frame_f1.columnconfigure(0, weight=1)
        frame_f1.columnconfigure(1, weight=1)
        frame_f1.columnconfigure(2, weight=1)

        # ── Fila 2: DNI, Correo ──
        frame_f2 = tk.Frame(form, bg="white")
        frame_f2.pack(fill="x", pady=(10, 0))

        tk.Label(frame_f2, text="DNI:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f2, text="Correo electrónico:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.entry_dni = tk.Entry(
            frame_f2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_dni.grid(row=1, column=0, sticky="ew",
                            ipady=8, pady=(4, 10))
        self._placeholder(self.entry_dni, "(Opcional)")

        self.entry_email = tk.Entry(
            frame_f2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_email.grid(row=1, column=1, sticky="ew",
                              ipady=8, pady=(4, 10), padx=(20, 0))
        self._placeholder(self.entry_email, "(Opcional)")

        frame_f2.columnconfigure(0, weight=1)
        frame_f2.columnconfigure(1, weight=1)

        # ── Fila 3: Estado, Preferencias ──
        frame_f3 = tk.Frame(form, bg="white")
        frame_f3.pack(fill="x", pady=(0, 0))

        tk.Label(frame_f3, text="Estado:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f3, text="Preferencias:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.var_estado = tk.StringVar(value="activo")
        combo_estado = ttk.Combobox(
            frame_f3,
            textvariable=self.var_estado,
            values=["activo", "inactivo"],
            state="readonly",
            font=("Poppins", 11)
        )
        combo_estado.grid(row=1, column=0, sticky="ew",
                          ipady=6, pady=(4, 10))

        self.entry_preferencias = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_preferencias.grid(row=1, column=1, sticky="ew",
                                     ipady=8, pady=(4, 10), padx=(20, 0))
        self._placeholder(self.entry_preferencias, "(Opcional)")

        frame_f3.columnconfigure(0, weight=1)
        frame_f3.columnconfigure(1, weight=1)

        # ── Notas adicionales ──
        tk.Label(form, text="Notas adicionales:", bg="white",
                 fg="#333333", font=("Poppins", 11)).pack(anchor="w")

        self.text_notas = tk.Text(
            form, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", height=4)
        self.text_notas.pack(fill="x", pady=(4, 15))

        # Placeholder para Text
        self.text_notas.insert("1.0", "(Opcional)")
        self.text_notas.config(fg="#BBBBBB")
        self.text_notas.bind("<FocusIn>", self._limpiar_notas)
        self.text_notas.bind("<FocusOut>", self._restaurar_notas)

        # Prellenar si es editar
        if modo == "editar" and cliente:
            self.entry_nombre.insert(0, cliente.get("nombre", ""))
            self.entry_apellido.insert(0, cliente.get("apellido", ""))
            self.entry_telefono.insert(0, cliente.get("telefono", ""))

            if cliente.get("dni"):
                self.entry_dni.delete(0, tk.END)
                self.entry_dni.config(fg="black")
                self.entry_dni.insert(0, str(cliente["dni"]))

            if cliente.get("email"):
                self.entry_email.delete(0, tk.END)
                self.entry_email.config(fg="black")
                self.entry_email.insert(0, cliente["email"])

            if cliente.get("preferencias"):
                self.entry_preferencias.delete(0, tk.END)
                self.entry_preferencias.config(fg="black")
                self.entry_preferencias.insert(0, cliente["preferencias"])

            self.var_estado.set(cliente.get("estado", "activo"))

            if cliente.get("notas"):
                self.text_notas.delete("1.0", tk.END)
                self.text_notas.config(fg="black")
                self.text_notas.insert("1.0", cliente["notas"])

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
            command=lambda: self._guardar(modo, cliente)
        ).pack(side="left", ipadx=15, ipady=8)

    def _limpiar_notas(self, event):
        if self.text_notas.get("1.0", tk.END).strip() == "(Opcional)":
            self.text_notas.delete("1.0", tk.END)
            self.text_notas.config(fg="black")

    def _restaurar_notas(self, event):
        if self.text_notas.get("1.0", tk.END).strip() == "":
            self.text_notas.insert("1.0", "(Opcional)")
            self.text_notas.config(fg="#BBBBBB")

    # GUARDAR
    def _guardar(self, modo, cliente=None):
        from db.conexion import obtener_conexion, cerrar_conexion

        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        telefono = self.entry_telefono.get().strip()
        dni_raw = self.entry_dni.get().strip()
        email_raw = self.entry_email.get().strip()
        pref_raw = self.entry_preferencias.get().strip()
        notas_raw = self.text_notas.get("1.0", tk.END).strip()
        estado = self.var_estado.get()

        dni = None if dni_raw in ("", "(Opcional)") else dni_raw
        email = None if email_raw in ("", "(Opcional)") else email_raw
        preferencias = None if pref_raw in ("", "(Opcional)") else pref_raw
        notas = None if notas_raw in ("", "(Opcional)") else notas_raw

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if not apellido:
            messagebox.showwarning("Atención", "El apellido es obligatorio.")
            return
        if not telefono:
            messagebox.showwarning("Atención", "El teléfono es obligatorio.")
            return

        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            if modo == "agregar":
                cursor.execute("""
                    INSERT INTO personas (nombre, apellido, dni, telefono, email)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, apellido, dni, telefono, email))
                id_persona = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO clientes (id_persona, preferencias, notas, estado)
                    VALUES (%s, %s, %s, %s)
                """, (id_persona, preferencias, notas, estado))
            else:
                cursor.execute("""
                    UPDATE personas SET nombre=%s, apellido=%s,
                    dni=%s, telefono=%s, email=%s
                    WHERE id_persona=%s
                """, (nombre, apellido, dni, telefono, email,
                      cliente["id_persona"]))

                cursor.execute("""
                    UPDATE clientes SET preferencias=%s, notas=%s, estado=%s
                    WHERE id_cliente=%s
                """, (preferencias, notas, estado, cliente["id_cliente"]))

            conexion.commit()
            messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)