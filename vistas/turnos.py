import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
import os
from PIL import Image, ImageTk

class VistaTurnos(tk.Frame):
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

    def _obtener_turnos(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT t.id_turno, t.fecha_hora, t.estado, t.precio_total,
                       t.sena, t.total_pagado, t.finalizado, t.observaciones,
                       s.nombre AS servicio, s.duracion AS duracion_servicio,
                       p_cli.nombre AS cli_nombre, p_cli.apellido AS cli_apellido,
                       p_emp.nombre AS emp_nombre, p_emp.apellido AS emp_apellido,
                       u_emp.foto AS emp_foto
                FROM turnos t
                JOIN servicios s ON t.id_servicio = s.id_servicio
                JOIN clientes c ON t.id_cliente = c.id_cliente
                JOIN personas p_cli ON c.id_persona = p_cli.id_persona
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                JOIN usuarios u_emp ON e.id_usuario = u_emp.id_usuario
                WHERE t.estado != 'cancelado'
            """
            if busqueda:
                query += """
                    AND (p_cli.nombre LIKE %s OR p_cli.apellido LIKE %s
                    OR s.nombre LIKE %s OR p_emp.nombre LIKE %s)
                """
                query += " ORDER BY t.fecha_hora DESC"
                b = f"%{busqueda}%"
                cursor.execute(query, (b, b, b, b))
            else:
                query += " ORDER BY t.fecha_hora DESC"
                cursor.execute(query)
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
                SELECT id_servicio, nombre, precio, duracion
                FROM servicios WHERE activo = 1 ORDER BY nombre
            """)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _obtener_empleados(self):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id_empleado, p.nombre, p.apellido
                FROM empleados e
                JOIN personas p ON e.id_persona = p.id_persona
                WHERE e.activo = 1 ORDER BY p.apellido
            """)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _obtener_clientes(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.id_cliente, p.nombre, p.apellido
                FROM clientes c
                JOIN personas p ON c.id_persona = p.id_persona
                WHERE c.estado = 'activo'
                AND (p.nombre LIKE %s OR p.apellido LIKE %s)
                ORDER BY p.apellido
            """, (f"%{busqueda}%", f"%{busqueda}%"))
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cerrar_conexion(conexion, cursor)

    def _verificar_disponibilidad(self, fecha_hora, duracion_min,
                                   id_empleado, id_servicio,
                                   excluir_turno=None):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return True
        try:
            cursor = conexion.cursor(dictionary=True)
            inicio_nuevo = fecha_hora
            fin_nuevo = fecha_hora + datetime.timedelta(minutes=duracion_min)

            query = """
                SELECT t.id_turno, t.fecha_hora, s.duracion
                FROM turnos t
                JOIN servicios s ON t.id_servicio = s.id_servicio
                WHERE t.estado != 'cancelado'
                AND (t.id_empleado = %s OR t.id_servicio = %s)
                AND DATE(t.fecha_hora) = %s
            """
            params = [id_empleado, id_servicio, fecha_hora.date()]
            if excluir_turno:
                query += " AND t.id_turno != %s"
                params.append(excluir_turno)

            cursor.execute(query, params)
            turnos = cursor.fetchall()

            for t in turnos:
                inicio_ex = t["fecha_hora"]
                fin_ex = inicio_ex + datetime.timedelta(
                    minutes=int(t["duracion"] * 60))
                if inicio_nuevo < fin_ex and fin_nuevo > inicio_ex:
                    return False
            return True
        except Exception as e:
            print(f"Error verificando disponibilidad: {e}")
            return True
        finally:
            cerrar_conexion(conexion, cursor)

    # LISTADO
    def _mostrar_listado(self):
        self._limpiar()

        frame_top = tk.Frame(self, bg="#F9F0F2")
        frame_top.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(
            frame_top,
            text="Listado de turnos",
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
        self._ico_buscar = self._colorear_icono(
            ruta_buscar, (214, 128, 146))
        if self._ico_buscar:
            tk.Label(frame_buscar, image=self._ico_buscar,
                     bg="white").pack(side="left", padx=(0, 8))

        tk.Button(
            frame_top,
            text="Agregar turno",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._mostrar_formulario_agregar
        ).pack(side="right", ipady=4, ipadx=10, padx=(0, 10))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(8, 0))

        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Turno.Treeview",
                        background="white",
                        foreground="#333333",
                        rowheight=40,
                        fieldbackground="white",
                        font=("Poppins", 10),
                        borderwidth=0)
        style.configure("Turno.Treeview.Heading",
                        background="#D68092",
                        foreground="white",
                        font=("Poppins ExtraBold", 11),
                        relief="flat")
        style.map("Turno.Treeview",
                  background=[("selected", "#FADADD")],
                  foreground=[("selected", "#333333")])
        style.map("Turno.Treeview.Heading",
                  background=[("active", "#C0607A")])

        cols = ("dia", "hora", "servicio", "cliente",
                "empleado", "editar", "visualizar")
        self.tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            style="Turno.Treeview",
            selectmode="browse"
        )

        encabezados = {
            "dia": "Día", "hora": "Hora", "servicio": "Servicio",
            "cliente": "Cliente", "empleado": "Empleado",
            "editar": "Editar", "visualizar": "Visualizar"
        }
        anchos = {
            "dia": 120, "hora": 70, "servicio": 160,
            "cliente": 150, "empleado": 150,
            "editar": 70, "visualizar": 80
        }

        for col in cols:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, anchor="center",
                             width=anchos[col], minwidth=50)

        self.tree.tag_configure("par", background="#FADADD")
        self.tree.tag_configure("impar", background="white")

        scroll_y = ttk.Scrollbar(container, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self._turnos_cache = []
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
        if idx >= len(self._turnos_cache):
            return
        turno = self._turnos_cache[idx]

        if col == "#6":  # Editar
            self._mostrar_formulario_editar(turno)
        elif col == "#7":  # Visualizar
            self._mostrar_detalles(turno)

    def _filtrar(self):
        busqueda = self.var_buscar.get()
        turnos = self._obtener_turnos(busqueda)
        self._renderizar_filas(turnos)

    def _cargar_filas(self):
        self._renderizar_filas(self._obtener_turnos())

    def _renderizar_filas(self, turnos):
        self.tree.delete(*self.tree.get_children())
        self._turnos_cache = turnos

        if not turnos:
            return

        for i, turno in enumerate(turnos):
            tag = "par" if i % 2 == 0 else "impar"
            fecha = turno["fecha_hora"]
            dia_str = fecha.strftime("%a. %d %b.") if hasattr(
                fecha, "strftime") else str(fecha)
            hora_str = fecha.strftime("%H:%M") if hasattr(
                fecha, "strftime") else ""
            cliente = f"{turno['cli_nombre']} {turno['cli_apellido']}"
            empleado = f"{turno['emp_nombre']} {turno['emp_apellido']}"

            self.tree.insert("", "end", values=(
                dia_str, hora_str, turno["servicio"],
                cliente, empleado, "✎", "👁"
            ), tags=(tag,))

    # DETALLES
    def _mostrar_detalles(self, turno):
        self._limpiar()

        tk.Label(
            self,
            text="Visualización detalles del turno",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 10))

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

        frame_enc = tk.Frame(tarjeta, bg="white")
        frame_enc.pack(fill="x", padx=25, pady=(20, 10))

        ruta_foto = None
        if turno.get("emp_foto"):
            ruta_foto = os.path.join("assets", "fotos_perfil",
                                     turno["emp_foto"])
        try:
            if ruta_foto and os.path.exists(ruta_foto):
                img = Image.open(ruta_foto).resize((70, 70), Image.LANCZOS)
            else:
                img = Image.open(os.path.join(
                    "assets", "user_rosa.png")).resize(
                    (70, 70), Image.LANCZOS)
            self._foto_user = ImageTk.PhotoImage(img)
            tk.Label(frame_enc, image=self._foto_user,
                     bg="white").pack(side="left", padx=(0, 15))
        except Exception:
            pass

        frame_nombre_enc = tk.Frame(frame_enc, bg="white")
        frame_nombre_enc.pack(side="left")

        tk.Label(
            frame_nombre_enc,
            text="Información del turno a cargo de:",
            bg="white", fg="#999999",
            font=("Poppins", 12)
        ).pack(anchor="w")

        emp_nombre = f"{turno['emp_nombre']} {turno['emp_apellido']}"
        tk.Label(
            frame_nombre_enc,
            text=emp_nombre,
            bg="white", fg="#333333",
            font=("Poppins ExtraBold", 20)
        ).pack(anchor="w")

        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(fill="x", padx=25, pady=(0, 10))

        fecha = turno["fecha_hora"]
        fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(
            fecha, "strftime") else str(fecha)

        duracion = turno.get("duracion_servicio", 0)
        duracion_str = self._duracion_a_texto(float(duracion))

        precio = float(turno.get("precio_total") or 0)
        sena = float(turno.get("sena") or 0)
        saldo = precio - sena

        cliente = f"{turno['cli_nombre']} {turno['cli_apellido']}"

        campos = [
            ("Nombre del cliente", cliente),
            ("Servicio requerido", turno["servicio"]),
            ("Fecha y hora", fecha_str),
            ("Duración aproximada", duracion_str),
            ("Seña pagada", f"${sena:.2f}"),
            ("Saldo pendiente", f"${saldo:.2f}"),
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

        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="w", padx=25, pady=(10, 20))

        tk.Button(
            frame_btns,
            text="Cancelar turno",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._confirmar_cancelar(turno)
        ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        if saldo > 0:
            tk.Button(
                frame_btns,
                text="Marcar como pagado",
                bg="#D68092", fg="white",
                font=("Poppins", 11),
                bd=0, relief="flat", cursor="hand2",
                command=lambda: self._marcar_pagado(turno)
            ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Turno finalizado",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=lambda: self._finalizar_turno(turno)
        ).pack(side="left", ipadx=15, ipady=8)

    def _confirmar_cancelar(self, turno):
        popup = tk.Toplevel(self)
        popup.title("")
        popup.resizable(False, False)
        popup.configure(bg="#EEEEEE")
        popup.grab_set()

        ancho, alto = 460, 170
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (ancho // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (alto // 2)
        popup.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            popup,
            text="Estás a punto de cancelar este turno\n¿estás seguro?",
            bg="#EEEEEE", fg="#333333",
            font=("Poppins", 11),
            justify="center"
        ).pack(pady=(25, 15))

        frame_btns = tk.Frame(popup, bg="#EEEEEE")
        frame_btns.pack()

        tk.Button(
            frame_btns,
            text="Eliminar",
            bg="white", fg="black",
            font=("Poppins ExtraBold", 11, "italic"),
            bd=1, relief="solid", cursor="hand2",
            command=lambda: self._cancelar_turno(turno, popup)
        ).pack(side="left", ipadx=20, ipady=6, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="white", fg="#333333",
            font=("Poppins", 11),
            bd=1, relief="solid", cursor="hand2",
            command=popup.destroy
        ).pack(side="left", ipadx=20, ipady=6)

    def _cancelar_turno(self, turno, popup):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE turnos SET estado = 'cancelado' WHERE id_turno = %s",
                (turno["id_turno"],))
            conexion.commit()
            popup.destroy()
            messagebox.showinfo("Éxito", "Turno cancelado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cancelar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    def _marcar_pagado(self, turno):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE turnos SET total_pagado = 1, sena = precio_total
                WHERE id_turno = %s
            """, (turno["id_turno"],))
            conexion.commit()
            messagebox.showinfo("Éxito", "Turno marcado como pagado.")
            turno["total_pagado"] = 1
            turno["sena"] = turno["precio_total"]
            self._mostrar_detalles(turno)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    def _finalizar_turno(self, turno):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE turnos SET finalizado = 1, estado = 'completado'
                WHERE id_turno = %s
            """, (turno["id_turno"],))
            conexion.commit()
            messagebox.showinfo("Éxito", "Turno marcado como finalizado.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo finalizar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)

    # FORMULARIOS
    def _mostrar_formulario_agregar(self):
        self._limpiar()
        self._construir_formulario(modo="agregar")

    def _mostrar_formulario_editar(self, turno):
        self._limpiar()
        self._construir_formulario(modo="editar", turno=turno)

    def _construir_formulario(self, modo, turno=None):
        titulo = "Agregar un nuevo turno" if modo == "agregar" \
            else "Editar información de un turno"

        tk.Label(
            self, text=titulo,
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 10))

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

        form = tk.Frame(tarjeta, bg="white")
        form.pack(fill="both", expand=True, padx=25, pady=20)

        # ── Fecha y Hora ──
        frame_f1 = tk.Frame(form, bg="white")
        frame_f1.pack(fill="x", pady=(0, 15))

        tk.Label(frame_f1, text="Fecha:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f1, text="Hora:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.date_entry = DateEntry(
            frame_f1,
            font=("Poppins", 11),
            date_pattern="dd/mm/yyyy",
            background="#D68092",
            foreground="white",
            borderwidth=0,
            locale="es_AR"
        )
        self.date_entry.grid(row=1, column=0, sticky="ew", ipady=6,
                             pady=(4, 0))

        frame_hora = tk.Frame(frame_f1, bg="white")
        frame_hora.grid(row=1, column=1, sticky="ew",
                        pady=(4, 0), padx=(20, 0))

        self.spin_hora = ttk.Spinbox(
            frame_hora, from_=0, to=23, width=3,
            format="%02.0f", font=("Poppins", 11), wrap=True)
        self.spin_hora.set("08")
        self.spin_hora.pack(side="left")

        tk.Label(frame_hora, text=":", bg="white",
                 font=("Poppins", 14)).pack(side="left")

        self.spin_min = ttk.Spinbox(
            frame_hora, from_=0, to=59, width=3,
            format="%02.0f", font=("Poppins", 11), wrap=True)
        self.spin_min.set("00")
        self.spin_min.pack(side="left")

        frame_f1.columnconfigure(0, weight=1)
        frame_f1.columnconfigure(1, weight=1)

        # Servicio, Empleado, Cliente
        frame_f2 = tk.Frame(form, bg="white")
        frame_f2.pack(fill="x", pady=(0, 15))

        tk.Label(frame_f2, text="Servicio/s:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f2, text="Empleado:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))
        tk.Label(frame_f2, text="Cliente:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=2, sticky="w", padx=(20, 0))

        servicios = self._obtener_servicios()
        self.servicios_data = {s["nombre"]: s for s in servicios}

        frame_lb = tk.Frame(frame_f2, bg="white")
        frame_lb.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self.listbox_servicios = tk.Listbox(
            frame_lb, selectmode="multiple",
            font=("Poppins", 10), bg="#EEEEEE", bd=0,
            height=4, exportselection=False)
        scroll_lb = ttk.Scrollbar(frame_lb, orient="vertical",
                                  command=self.listbox_servicios.yview)
        self.listbox_servicios.configure(yscrollcommand=scroll_lb.set)
        self.listbox_servicios.pack(side="left", fill="x", expand=True)
        scroll_lb.pack(side="right", fill="y")
        self.listbox_servicios.bind("<<ListboxSelect>>",
                                    self._actualizar_duracion_precio)

        for nombre in self.servicios_data.keys():
            self.listbox_servicios.insert(tk.END, nombre)

        empleados = self._obtener_empleados()
        self.empleados_data = {
            f"{e['nombre']} {e['apellido']}": e["id_empleado"]
            for e in empleados}

        self.var_empleado = tk.StringVar()
        combo_emp = ttk.Combobox(
            frame_f2,
            textvariable=self.var_empleado,
            values=list(self.empleados_data.keys()),
            state="readonly",
            font=("Poppins", 11)
        )
        combo_emp.grid(row=1, column=1, sticky="ew",
                       ipady=6, pady=(4, 0), padx=(20, 0))

        frame_cli = tk.Frame(frame_f2, bg="white")
        frame_cli.grid(row=1, column=2, sticky="ew",
                       pady=(4, 0), padx=(20, 0))

        self.var_cliente_buscar = tk.StringVar()
        self.var_cliente_buscar.trace(
            "w", lambda *a: self._filtrar_clientes())

        tk.Entry(
            frame_cli,
            textvariable=self.var_cliente_buscar,
            font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat"
        ).pack(fill="x", ipady=8)

        self.listbox_clientes = tk.Listbox(
            frame_cli, font=("Poppins", 10),
            bg="#EEEEEE", bd=0, height=4,
            exportselection=False)
        self.listbox_clientes.pack(fill="x")

        self.clientes_data = {}
        self._filtrar_clientes()

        frame_f2.columnconfigure(0, weight=1)
        frame_f2.columnconfigure(1, weight=1)
        frame_f2.columnconfigure(2, weight=1)

        # Duración, Seña, Precio
        frame_f3 = tk.Frame(form, bg="white")
        frame_f3.pack(fill="x", pady=(0, 15))

        tk.Label(frame_f3, text="Duración del turno:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f3, text="Seña pagada:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))
        tk.Label(frame_f3, text="Precio total:", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=2, sticky="w", padx=(20, 0))

        self.entry_duracion = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat",
            state="readonly")
        self.entry_duracion.grid(row=1, column=0, sticky="ew",
                                 ipady=8, pady=(4, 0))

        self.entry_sena = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_sena.grid(row=1, column=1, sticky="ew",
                             ipady=8, pady=(4, 0), padx=(20, 0))

        self.entry_precio = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat",
            state="readonly")
        self.entry_precio.grid(row=1, column=2, sticky="ew",
                               ipady=8, pady=(4, 0), padx=(20, 0))

        frame_f3.columnconfigure(0, weight=1)
        frame_f3.columnconfigure(1, weight=1)
        frame_f3.columnconfigure(2, weight=1)

        if modo == "editar" and turno:
            fecha = turno["fecha_hora"]
            if hasattr(fecha, "strftime"):
                self.date_entry.set_date(fecha.date())
                self.spin_hora.set(fecha.strftime("%H"))
                self.spin_min.set(fecha.strftime("%M"))

            emp_nombre = f"{turno['emp_nombre']} {turno['emp_apellido']}"
            if emp_nombre in self.empleados_data:
                self.var_empleado.set(emp_nombre)

            self.var_cliente_buscar.set(
                f"{turno['cli_nombre']} {turno['cli_apellido']}")

            self._set_entry_readonly(
                self.entry_duracion,
                self._duracion_a_texto(float(turno.get(
                    "duracion_servicio", 0))))
            if turno.get("sena"):
                self.entry_sena.insert(0, str(turno["sena"]))
            self._set_entry_readonly(
                self.entry_precio,
                str(turno.get("precio_total", "")))

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
            command=lambda: self._guardar(modo, turno)
        ).pack(side="left", ipadx=15, ipady=8)

    def _set_entry_readonly(self, entry, valor):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, valor)
        entry.config(state="readonly")

    def _actualizar_duracion_precio(self, event=None):
        seleccionados = self.listbox_servicios.curselection()
        nombres = [list(self.servicios_data.keys())[i]
                   for i in seleccionados]

        duracion_total = sum(
            float(self.servicios_data[n]["duracion"]) for n in nombres)
        precio_total = sum(
            float(self.servicios_data[n]["precio"]) for n in nombres)

        self._set_entry_readonly(
            self.entry_duracion,
            self._duracion_a_texto(duracion_total) if nombres else "")
        self._set_entry_readonly(
            self.entry_precio,
            f"{precio_total:.2f}" if nombres else "")

    def _filtrar_clientes(self):
        busqueda = self.var_cliente_buscar.get()
        clientes = self._obtener_clientes(busqueda)
        self.listbox_clientes.delete(0, tk.END)
        self.clientes_data = {}
        for c in clientes:
            nombre = f"{c['nombre']} {c['apellido']}"
            self.clientes_data[nombre] = c["id_cliente"]
            self.listbox_clientes.insert(tk.END, nombre)

    # GUARDAR 
    def _guardar(self, modo, turno=None):
        from db.conexion import obtener_conexion, cerrar_conexion

        try:
            fecha = self.date_entry.get_date()
            hora = int(self.spin_hora.get())
            minuto = int(self.spin_min.get())
            fecha_hora = datetime.datetime.combine(
                fecha, datetime.time(hora, minuto))
        except Exception:
            messagebox.showwarning("Atención", "Fecha u hora inválida.")
            return

        seleccionados = self.listbox_servicios.curselection()
        if not seleccionados:
            messagebox.showwarning("Atención",
                                   "Seleccioná al menos un servicio.")
            return
        nombres_servicios = [list(self.servicios_data.keys())[i]
                             for i in seleccionados]
        id_servicio = self.servicios_data[nombres_servicios[0]]["id_servicio"]

        duracion_total = sum(
            float(self.servicios_data[n]["duracion"])
            for n in nombres_servicios)
        precio_total = sum(
            float(self.servicios_data[n]["precio"])
            for n in nombres_servicios)

        emp_nombre = self.var_empleado.get()
        if not emp_nombre:
            messagebox.showwarning("Atención", "Seleccioná un empleado.")
            return
        id_empleado = self.empleados_data[emp_nombre]

        sel_cli = self.listbox_clientes.curselection()
        if not sel_cli:
            messagebox.showwarning("Atención", "Seleccioná un cliente.")
            return
        cli_nombre = self.listbox_clientes.get(sel_cli[0])
        id_cliente = self.clientes_data[cli_nombre]

        sena_str = self.entry_sena.get().strip()
        sena = float(sena_str) if sena_str else None

        duracion_min = int(duracion_total * 60)
        excluir = turno["id_turno"] if turno else None
        disponible = self._verificar_disponibilidad(
            fecha_hora, duracion_min, id_empleado, id_servicio, excluir)

        if not disponible:
            messagebox.showerror(
                "Horario no disponible",
                "Ya existe un turno que se superpone con este horario\n"
                "para el mismo empleado o servicio."
            )
            return

        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            if modo == "agregar":
                cursor.execute("""
                    INSERT INTO turnos
                    (id_cliente, id_empleado, id_servicio, fecha_hora,
                     estado, precio_total, sena)
                    VALUES (%s, %s, %s, %s, 'programado', %s, %s)
                """, (id_cliente, id_empleado, id_servicio,
                      fecha_hora, precio_total, sena))
            else:
                cursor.execute("""
                    UPDATE turnos SET
                        id_cliente=%s, id_empleado=%s, id_servicio=%s,
                        fecha_hora=%s, precio_total=%s, sena=%s
                    WHERE id_turno=%s
                """, (id_cliente, id_empleado, id_servicio,
                      fecha_hora, precio_total, sena,
                      turno["id_turno"]))
            conexion.commit()
            messagebox.showinfo("Éxito", "Turno guardado correctamente.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)