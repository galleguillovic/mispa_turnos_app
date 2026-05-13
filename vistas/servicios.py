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
        self._mostrar_listado()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # HELPERS
    def _duracion_a_texto(self, horas_float):
        try:
            horas = int(horas_float)
            minutos = int(round((horas_float - horas) * 60))
            if horas > 0 and minutos > 0:
                return f"{horas}h {minutos}min"
            elif horas > 0:
                return f"{horas}h"
            else:
                return f"{minutos}min"
        except Exception:
            return str(horas_float)

    def _colorear_icono(self, ruta, color_rgb, size=(18, 18)):
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

    def _placeholder(self, entry, texto):
        entry.insert(0, texto)
        entry.config(fg="#999999")
        entry.bind("<FocusIn>", lambda e: self._limpiar_placeholder(entry, texto))
        entry.bind("<FocusOut>", lambda e: self._restaurar_placeholder(entry, texto))

    def _limpiar_placeholder(self, entry, texto):
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def _restaurar_placeholder(self, entry, texto):
        if entry.get() == "":
            entry.insert(0, texto)
            entry.config(fg="#999999")

    def _obtener_categorias(self):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
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
                    SELECT s.*, c.nombre AS categoria_nombre
                    FROM servicios s
                    JOIN categorias c ON s.id_categoria = c.id_categoria
                    WHERE s.nombre LIKE %s AND s.activo = 1
                    ORDER BY s.nombre
                """, (f"%{busqueda}%",))
            else:
                cursor.execute("""
                    SELECT s.*, c.nombre AS categoria_nombre
                    FROM servicios s
                    JOIN categorias c ON s.id_categoria = c.id_categoria
                    WHERE s.activo = 1
                    ORDER BY s.nombre
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
            text="Servicios/Especialidades",
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

        # Ícono buscar 
        ruta_buscar = os.path.join("assets", "ico_buscar.png")
        self._ico_buscar = self._colorear_icono(ruta_buscar, (214, 128, 146))
        if self._ico_buscar:
            tk.Label(frame_buscar, image=self._ico_buscar,
                     bg="white").pack(side="left", padx=(0, 8))
        else:
            tk.Label(frame_buscar, text="🔍",
                     bg="white", font=("Poppins", 11)).pack(
                side="left", padx=(0, 8))

        # Botón agregar
        tk.Button(
            frame_top,
            text="Agregar servicio",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat",
            cursor="hand2",
            command=self._mostrar_formulario_agregar
        ).pack(side="right", ipady=2, ipadx=10, padx=(0, 10))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(8, 15))

        # Scroll vertical y horizontal
        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#F9F0F2", highlightthickness=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)
        scroll_x = ttk.Scrollbar(container, orient="horizontal",
                                 command=canvas.xview)

        self.frame_lista = tk.Frame(canvas, bg="#F9F0F2")
        self.frame_lista.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set,
                         xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        self._cargar_tarjetas()

    def _filtrar(self):
        busqueda = self.var_buscar.get()
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        servicios = self._obtener_servicios(busqueda)
        self._renderizar_tarjetas(servicios)

    def _cargar_tarjetas(self):
        servicios = self._obtener_servicios()
        self._renderizar_tarjetas(servicios)

    def _renderizar_tarjetas(self, servicios):
        if not servicios:
            tk.Label(
                self.frame_lista,
                text="No hay servicios cargados.",
                bg="#F9F0F2", fg="#999999",
                font=("Poppins", 11)
            ).grid(row=0, column=0, pady=30)
            return

        for i, s in enumerate(servicios):
            fila = i // 2
            col = i % 2
            self._crear_tarjeta(self.frame_lista, s, fila, col)

    def _crear_tarjeta(self, frame_padre, servicio, fila, col):
        tarjeta = tk.Frame(
            frame_padre, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1,
        )
        tarjeta.grid(row=fila, column=col, padx=8, pady=8, sticky="nsew")
        frame_padre.columnconfigure(0, minsize=430)
        frame_padre.columnconfigure(1, minsize=430)

        contenido = tk.Frame(tarjeta, bg="white")
        contenido.pack(fill="x", padx=20, pady=15)

        tk.Label(
            contenido,
            text=servicio["nombre"],
            bg="white", fg="#333333",
            font=("Poppins ExtraBold", 13),
            wraplength=380,
            justify="left"
        ).pack(anchor="w")

        campos = [
            ("Descripción", servicio.get("descripcion") or "—"),
            ("Categoría", servicio.get("categoria_nombre") or "—"),
            ("Precio", f"${servicio['precio']:.2f}"),
            ("Protocolos", servicio.get("protocolos") or "—"),
            ("Duración", self._duracion_a_texto(float(servicio["duracion"]))),
        ]

        for etiqueta, valor in campos:
            fila_w = tk.Frame(contenido, bg="white")
            fila_w.pack(anchor="w", pady=1)
            tk.Label(fila_w, text=f"{etiqueta}:", bg="white", fg="#555555",
                     font=("Poppins ExtraBold", 10)).pack(side="left")
            tk.Label(fila_w, text=f" {valor}", bg="white", fg="#555555",
                     font=("Poppins", 10), wraplength=350,
                     justify="left").pack(side="left")

        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=20, pady=(0, 15))

        tk.Button(
            frame_btns,
            text="Editar información",
            bg="#D68092", fg="white",
            font=("Poppins", 10),
            bd=0, relief="flat", cursor="hand2",
            command=lambda s=servicio: self._mostrar_formulario_editar(s)
        ).pack(side="left", ipadx=10, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Eliminar",
            bg="#D68092", fg="white",
            font=("Poppins", 10),
            bd=0, relief="flat", cursor="hand2",
            command=lambda s=servicio: self._confirmar_eliminar(s)
        ).pack(side="left", ipadx=10, ipady=6)

    # CONFIRMAR ELIMINAR
    def _confirmar_eliminar(self, servicio):
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.configure(bg="#EEEEEE")
        popup.grab_set()

        # Ancho dinámico según largo del nombre
        nombre = servicio['nombre']
        ancho = max(420, len(nombre) * 9 + 100)
        lineas = len(nombre) // 35 + 2
        alto = 130 + (lineas * 22)
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (ancho // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            popup,
            text=f"Estás a punto de eliminar {nombre}\ny su información asociada, ¿estás seguro?",
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
            bd=1, relief="solid",
            cursor="hand2",
            command=lambda: self._eliminar_servicio(servicio, popup)
        ).pack(side="left", ipadx=20, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="white", fg="#333333",
            font=("Poppins", 11),
            bd=1, relief="solid",
            cursor="hand2",
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
                (servicio["id_servicio"],)
            )
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIO AGREGAR 
    def _mostrar_formulario_agregar(self):
        self._limpiar()
        self._construir_formulario(modo="agregar")

    # FORMULARIO EDITAR 
    def _mostrar_formulario_editar(self, servicio):
        self._limpiar()
        self._construir_formulario(modo="editar", servicio=servicio)

    def _construir_formulario(self, modo, servicio=None):
        titulo = "Agregar un servicio/especialidad" if modo == "agregar" \
            else "Editar información del servicio/especialidad"

        tk.Label(
            self,
            text=titulo,
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
        tarjeta.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(form, text="Nombre del servicio/especialidad*:",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))

        self.entry_nombre = tk.Entry(
            form, font=("Poppins", 11), bg="#EEEEEE", bd=0,
            relief="flat", width=70)
        self.entry_nombre.grid(row=1, column=0, columnspan=3,
                               sticky="ew", ipady=8, pady=(0, 15))

        tk.Label(form, text="Duración:*", bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=2, column=0, sticky="w")
        tk.Label(form, text="Precio:*", bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=2, column=1, sticky="w",
                                            padx=(20, 0))
        tk.Label(form, text="Categoría:*", bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=2, column=2, sticky="w",
                                            padx=(20, 0))

        self.entry_duracion = tk.Entry(
            form, font=("Poppins", 11), bg="#EEEEEE", bd=0, relief="flat")
        self.entry_duracion.grid(row=3, column=0, sticky="ew",
                                 ipady=8, pady=(4, 15))

        self.entry_precio = tk.Entry(
            form, font=("Poppins", 11), bg="#EEEEEE", bd=0, relief="flat")
        self.entry_precio.grid(row=3, column=1, sticky="ew",
                               ipady=8, pady=(4, 15), padx=(20, 0))

        categorias = self._obtener_categorias()
        self.cat_nombres = [c["nombre"] for c in categorias]
        self.cat_ids = {c["nombre"]: c["id_categoria"] for c in categorias}

        self.var_categoria = tk.StringVar()
        combo_cat = ttk.Combobox(
            form,
            textvariable=self.var_categoria,
            values=self.cat_nombres,
            state="readonly",
            font=("Poppins", 11)
        )
        combo_cat.grid(row=3, column=2, sticky="ew",
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

        self._placeholder(self.entry_duracion, "Ej: 1.5")

        if modo == "editar" and servicio:
            self.entry_nombre.insert(0, servicio["nombre"])
            self.entry_duracion.delete(0, tk.END)
            self.entry_duracion.config(fg="black")
            self.entry_duracion.insert(0, str(servicio["duracion"]))
            self.entry_precio.insert(0, str(servicio["precio"]))
            if servicio.get("categoria_nombre") in self.cat_nombres:
                self.var_categoria.set(servicio["categoria_nombre"])
            if servicio.get("descripcion"):
                self.text_descripcion.insert("1.0", servicio["descripcion"])
            if servicio.get("protocolos"):
                self.text_protocolos.insert("1.0", servicio["protocolos"])

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

        tk.Button(
            frame_btns,
            text="Guardar cambios",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._guardar(modo, servicio)
        ).pack(side="left", ipadx=15, ipady=8)

    # GUARDAR 
    def _guardar(self, modo, servicio=None):
        nombre = self.entry_nombre.get().strip()
        duracion_str = self.entry_duracion.get().strip()
        precio_str = self.entry_precio.get().strip()
        categoria = self.var_categoria.get()
        descripcion = self.text_descripcion.get("1.0", tk.END).strip()
        protocolos = self.text_protocolos.get("1.0", tk.END).strip()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre es obligatorio.")
            return
        if duracion_str == "Ej: 1.5" or not duracion_str:
            messagebox.showwarning("Atención", "La duración es obligatoria.")
            return
        try:
            duracion = float(duracion_str)
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
                                   "El precio debe ser un número. Ej: 5000")
            return
        if not categoria:
            messagebox.showwarning("Atención", "Seleccioná una categoría.")
            return
        if not descripcion:
            messagebox.showwarning("Atención", "La descripción es obligatoria.")
            return

        id_categoria = self.cat_ids[categoria]

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            if modo == "agregar":
                cursor.execute("""
                    INSERT INTO servicios
                    (id_categoria, nombre, descripcion, precio, duracion,
                     protocolos, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                """, (id_categoria, nombre, descripcion, precio,
                      duracion, protocolos or None))
            else:
                cursor.execute("""
                    UPDATE servicios SET
                        id_categoria = %s, nombre = %s, descripcion = %s,
                        precio = %s, duracion = %s, protocolos = %s
                    WHERE id_servicio = %s
                """, (id_categoria, nombre, descripcion, precio,
                      duracion, protocolos or None, servicio["id_servicio"]))
            conexion.commit()
            messagebox.showinfo("Éxito", "Servicio guardado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)