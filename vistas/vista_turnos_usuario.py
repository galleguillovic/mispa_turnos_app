# vista_turnos_usuario.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
from PIL import Image, ImageTk


class VistaTurnosUsuario(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._ico_buscar = None
        self._foto_user  = None
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

    # CONSULTA: solo turnos del empleado logueado
    def _obtener_turnos(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            query = """
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
                LEFT JOIN turno_servicio ts ON t.id_turno    = ts.id_turno
                LEFT JOIN servicios      s  ON ts.id_servicio = s.id_servicio
                JOIN clientes  c     ON t.id_cliente  = c.id_cliente
                JOIN personas  p_cli ON c.id_persona  = p_cli.id_persona
                JOIN empleados e     ON t.id_empleado  = e.id_empleado
                JOIN personas  p_emp ON e.id_persona  = p_emp.id_persona
                JOIN usuarios  u_emp ON e.id_usuario  = u_emp.id_usuario
                WHERE t.estado != 'cancelado'
                  AND e.id_usuario = %s
            """
            params = [self.panel.usuario["id_usuario"]]

            if busqueda:
                query += """
                    AND (p_cli.nombre LIKE %s OR p_cli.apellido LIKE %s
                         OR s.nombre LIKE %s)
                """
                b = f"%{busqueda}%"
                params += [b, b, b]

            query += " GROUP BY t.id_turno ORDER BY t.fecha_hora DESC"
            cursor.execute(query, params)
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

        tk.Label(frame_top, text="Listado de turnos",
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
            fill="x", padx=30, pady=(8, 0))

        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Turno.Treeview",
                        background="white", foreground="#333333",
                        rowheight=40, fieldbackground="white",
                        font=("Poppins", 10), borderwidth=0)
        style.configure("Turno.Treeview.Heading",
                        background="#D68092", foreground="white",
                        font=("Poppins ExtraBold", 11), relief="flat")
        style.map("Turno.Treeview",
                  background=[("selected", "#FADADD")],
                  foreground=[("selected", "#333333")])
        style.map("Turno.Treeview.Heading",
                  background=[("active", "#C0607A")])
        cols = ("dia", "hora", "servicio", "cliente", "empleado", "visualizar")
        self.tree = ttk.Treeview(container, columns=cols, show="headings",
                                 style="Turno.Treeview", selectmode="browse")

        encabezados = {
            "dia": "Día", "hora": "Hora", "servicio": "Servicio(s)",
            "cliente": "Cliente", "empleado": "Empleado",
            "visualizar": "Visualizar"
        }
        anchos = {
            "dia": 130, "hora": 70, "servicio": 200,
            "cliente": 150, "empleado": 150, "visualizar": 90
        }
        for col in cols:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, anchor="center",
                             width=anchos[col], minwidth=50)

        self.tree.tag_configure("par",   background="#FADADD")
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
        col  = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return
        idx = self.tree.index(item)
        if idx >= len(self._turnos_cache):
            return
        if col == "#6":   # columna Visualizar
            self._mostrar_detalles(self._turnos_cache[idx])

    def _filtrar(self):
        self._renderizar_filas(self._obtener_turnos(self.var_buscar.get()))

    def _cargar_filas(self):
        self._renderizar_filas(self._obtener_turnos())

    def _renderizar_filas(self, turnos):
        self.tree.delete(*self.tree.get_children())
        self._turnos_cache = turnos
        for i, turno in enumerate(turnos):
            tag      = "par" if i % 2 == 0 else "impar"
            fecha    = turno["fecha_hora"]
            dia_str  = fecha.strftime("%a. %d %b.") if hasattr(fecha, "strftime") else str(fecha)
            hora_str = fecha.strftime("%H:%M")       if hasattr(fecha, "strftime") else ""
            cliente  = f"{turno['cli_nombre']} {turno['cli_apellido']}"
            empleado = f"{turno['emp_nombre']} {turno['emp_apellido']}"
            self.tree.insert("", "end", values=(
                dia_str, hora_str, turno.get("servicios", "—"),
                cliente, empleado, "👁"
            ), tags=(tag,))

    # DETALLES

    def _mostrar_detalles(self, turno):
        self._limpiar()

        tk.Label(self, text="Visualización detalles del turno",
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

        # Encabezado con foto
        frame_enc = tk.Frame(tarjeta, bg="white")
        frame_enc.pack(fill="x", padx=25, pady=(20, 10))

        ruta_foto = None
        if turno.get("emp_foto"):
            ruta_foto = os.path.join("assets", "fotos_perfil", turno["emp_foto"])
        try:
            img = Image.open(ruta_foto).resize((70, 70), Image.LANCZOS) \
                if ruta_foto and os.path.exists(ruta_foto) \
                else Image.open(os.path.join(
                    "assets", "user_rosa.png")).resize((70, 70), Image.LANCZOS)
            self._foto_user = ImageTk.PhotoImage(img)
            tk.Label(frame_enc, image=self._foto_user,
                     bg="white").pack(side="left", padx=(0, 15))
        except Exception:
            pass

        frame_nombre_enc = tk.Frame(frame_enc, bg="white")
        frame_nombre_enc.pack(side="left")
        tk.Label(frame_nombre_enc, text="Información del turno a cargo de:",
                 bg="white", fg="#999999", font=("Poppins", 12)).pack(anchor="w")
        tk.Label(frame_nombre_enc,
                 text=f"{turno['emp_nombre']} {turno['emp_apellido']}",
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 20)).pack(anchor="w")

        # Campos
        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(fill="x", padx=25, pady=(0, 10))

        fecha     = turno["fecha_hora"]
        fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if hasattr(fecha, "strftime") else str(fecha)
        duracion  = turno.get("duracion") or 0
        precio    = float(turno.get("precio_total") or 0)
        sena      = float(turno.get("sena_pagada")  or 0)

        for etiqueta, valor in [
            ("Nombre del cliente",       f"{turno['cli_nombre']} {turno['cli_apellido']}"),
            ("Servicio(s) requerido(s)", turno.get("servicios", "—")),
            ("Fecha y hora",             fecha_str),
            ("Duración aproximada",      self._duracion_a_texto(float(duracion))),
            ("Seña pagada",              f"${sena:.2f}"),
            ("Saldo pendiente",          f"${precio - sena:.2f}"),
        ]:
            fila = tk.Frame(frame_info, bg="white")
            fila.pack(anchor="w", pady=3)
            tk.Label(fila, text=f"{etiqueta}:", bg="white", fg="#555555",
                     font=("Poppins ExtraBold", 11)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white", fg="#555555",
                     font=("Poppins", 11), wraplength=600).pack(side="left")

        # Botones de acción permitidos al usuario estándar
        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="w", padx=25, pady=(10, 20))

        if (precio - sena) > 0:
            tk.Button(frame_btns, text="Marcar como pagado",
                      bg="#D68092", fg="white", font=("Poppins", 11),
                      bd=0, relief="flat", cursor="hand2",
                      command=lambda: self._marcar_pagado(turno)
                      ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        tk.Button(frame_btns, text="Turno finalizado",
                  bg="#D68092", fg="white", font=("Poppins", 11),
                  bd=0, relief="flat", cursor="hand2",
                  command=lambda: self._finalizar_turno(turno)
                  ).pack(side="left", ipadx=15, ipady=8)

    def _marcar_pagado(self, turno):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE turnos SET total_pagado = 1, "
                "sena_pagada = precio_total WHERE id_turno = %s",
                (turno["id_turno"],))
            conexion.commit()
            messagebox.showinfo("Éxito", "Turno marcado como pagado.")
            turno["total_pagado"] = 1
            turno["sena_pagada"]  = turno["precio_total"]
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
            cursor.execute(
                "UPDATE turnos SET estado = 'completado' WHERE id_turno = %s",
                (turno["id_turno"],))
            conexion.commit()
            messagebox.showinfo("Éxito", "Turno marcado como finalizado.")
            self._mostrar_listado()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo finalizar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)