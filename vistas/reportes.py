import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import datetime

class VistaReportes(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.pack(fill="both", expand=True)
        self._clientes_data = {}
        self._construir_ui()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

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

    def _construir_ui(self):
        tk.Label(
            self,
            text="Reportes",
            bg="#F9F0F2", fg="#D68092",
            font=("Poppins ExtraBold", 18)
        ).pack(anchor="w", padx=30, pady=(20, 0))

        tk.Frame(self, bg="#D68092", height=2).pack(
            fill="x", padx=30, pady=(6, 20))

        # Área scrollable
        container = tk.Frame(self, bg="#F9F0F2")
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

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

        # Reporte de turnos
        self._construir_reporte_turnos(frame_scroll)

        # Reporte de historial de cliente
        self._construir_reporte_cliente(frame_scroll)

    def _construir_reporte_turnos(self, frame_padre):
        tarjeta = tk.Frame(
            frame_padre, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", pady=(0, 20))

        contenido = tk.Frame(tarjeta, bg="white")
        contenido.pack(fill="x", padx=25, pady=20)

        tk.Label(
            contenido,
            text="Reporte de turnos",
            bg="white", fg="#D68092",
            font=("Poppins ExtraBold", 14)
        ).pack(anchor="w")

        tk.Label(
            contenido,
            text="Seleccioná para ver información detallada de los turnos\nrealizados en el último día/semana/mes.",
            bg="white", fg="#555555",
            font=("Poppins", 11),
            justify="left"
        ).pack(anchor="w", pady=(6, 12))

        self.var_periodo = tk.StringVar(value="Seleccioná")
        combo = ttk.Combobox(
            contenido,
            textvariable=self.var_periodo,
            values=["Último día", "Última semana", "Último mes"],
            state="readonly",
            font=("Poppins", 11)
        )
        combo.pack(fill="x", pady=(0, 15))

        tk.Button(
            contenido,
            text="Descargar PDF",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._descargar_reporte_turnos
        ).pack(anchor="e", ipadx=15, ipady=8)

    def _construir_reporte_cliente(self, frame_padre):
        tarjeta = tk.Frame(
            frame_padre, bg="white",
            highlightbackground="#D68092",
            highlightthickness=1
        )
        tarjeta.pack(fill="x", pady=(0, 20))

        contenido = tk.Frame(tarjeta, bg="white")
        contenido.pack(fill="x", padx=25, pady=20)

        tk.Label(
            contenido,
            text="Reporte de historial de cliente",
            bg="white", fg="#D68092",
            font=("Poppins ExtraBold", 14)
        ).pack(anchor="w")

        tk.Label(
            contenido,
            text="Seleccioná para ver información detallada de todos los\nservicios adquiridos por un cliente.",
            bg="white", fg="#555555",
            font=("Poppins", 11),
            justify="left"
        ).pack(anchor="w", pady=(6, 12))

        # Buscador de clientes
        frame_buscar = tk.Frame(contenido, bg="#EEEEEE",
                                highlightbackground="#CCCCCC",
                                highlightthickness=1)
        frame_buscar.pack(fill="x", pady=(0, 8))

        self.var_cliente_buscar = tk.StringVar()
        self.var_cliente_buscar.trace("w", lambda *a: self._filtrar_clientes())

        tk.Entry(
            frame_buscar,
            textvariable=self.var_cliente_buscar,
            font=("Poppins", 11),
            bg="#EEEEEE", bd=0
        ).pack(side="left", fill="x", expand=True, padx=(10, 4), pady=8)

        tk.Label(frame_buscar, text="🔍", bg="#EEEEEE",
                 font=("Poppins", 11)).pack(side="left", padx=(0, 8))

        # Lista de resultados
        self.listbox_clientes = tk.Listbox(
            contenido,
            font=("Poppins", 10),
            bg="#EEEEEE", bd=0,
            height=4,
            exportselection=False,
            selectbackground="#D68092",
            selectforeground="white"
        )
        self.listbox_clientes.pack(fill="x", pady=(0, 15))
        self._filtrar_clientes()

        tk.Button(
            contenido,
            text="Descargar PDF",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._descargar_reporte_cliente
        ).pack(anchor="e", ipadx=15, ipady=8)

    def _filtrar_clientes(self):
        busqueda = self.var_cliente_buscar.get()
        clientes = self._obtener_clientes(busqueda)
        self.listbox_clientes.delete(0, tk.END)
        self._clientes_data = {}
        for c in clientes:
            nombre = f"{c['nombre']} {c['apellido']}"
            self._clientes_data[nombre] = c["id_cliente"]
            self.listbox_clientes.insert(tk.END, nombre)

    # GENERACIÓN DE PDFs
    def _descargar_reporte_turnos(self):
        periodo = self.var_periodo.get()
        if periodo == "Seleccioná":
            messagebox.showwarning("Atención", "Seleccioná un período.")
            return

        hoy = datetime.date.today()
        if periodo == "Último día":
            desde = hoy - datetime.timedelta(days=1)
        elif periodo == "Última semana":
            desde = hoy - datetime.timedelta(weeks=1)
        else:
            desde = hoy - datetime.timedelta(days=30)

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.fecha_hora, t.estado, t.precio_total, t.sena,
                       p_cli.nombre AS cli_nombre,
                       p_cli.apellido AS cli_apellido,
                       p_emp.nombre AS emp_nombre,
                       p_emp.apellido AS emp_apellido,
                       s.nombre AS servicio
                FROM turnos t
                JOIN clientes c ON t.id_cliente = c.id_cliente
                JOIN personas p_cli ON c.id_persona = p_cli.id_persona
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                JOIN servicios s ON t.id_servicio = s.id_servicio
                WHERE DATE(t.fecha_hora) >= %s
                ORDER BY t.fecha_hora ASC
            """, (desde,))
            turnos = cursor.fetchall()
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {ex}")
            return
        finally:
            cerrar_conexion(conexion, cursor)

        if not turnos:
            messagebox.showinfo("Sin datos",
                                "No hay turnos en el período seleccionado.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"reporte_turnos_{periodo.lower().replace(' ', '_')}.pdf",
            title="Guardar reporte"
        )
        if not ruta:
            return

        self._generar_pdf_turnos(ruta, turnos, periodo, desde, hoy)

    def _descargar_reporte_cliente(self):
        sel = self.listbox_clientes.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un cliente.")
            return

        nombre_cliente = self.listbox_clientes.get(sel[0])
        id_cliente = self._clientes_data[nombre_cliente]

        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.fecha_hora, t.estado, t.precio_total, t.sena,
                       p_emp.nombre AS emp_nombre,
                       p_emp.apellido AS emp_apellido,
                       s.nombre AS servicio
                FROM turnos t
                JOIN empleados e ON t.id_empleado = e.id_empleado
                JOIN personas p_emp ON e.id_persona = p_emp.id_persona
                JOIN servicios s ON t.id_servicio = s.id_servicio
                WHERE t.id_cliente = %s
                ORDER BY t.fecha_hora DESC
            """, (id_cliente,))
            turnos = cursor.fetchall()
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {ex}")
            return
        finally:
            cerrar_conexion(conexion, cursor)

        if not turnos:
            messagebox.showinfo("Sin datos",
                                "Este cliente no tiene turnos registrados.")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=f"historial_{nombre_cliente.replace(' ', '_')}.pdf",
            title="Guardar reporte"
        )
        if not ruta:
            return

        self._generar_pdf_cliente(ruta, turnos, nombre_cliente)

    def _generar_pdf_turnos(self, ruta, turnos, periodo, desde, hasta):
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(ruta, pagesize=landscape(A4),
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        rosa = colors.HexColor("#D68092")

        titulo_style = ParagraphStyle(
            "titulo", parent=styles["Heading1"],
            textColor=rosa, fontSize=16, spaceAfter=6)
        sub_style = ParagraphStyle(
            "sub", parent=styles["Normal"],
            textColor=colors.grey, fontSize=10, spaceAfter=12)

        elementos = []
        elementos.append(Paragraph("Reporte de Turnos - MiSpa Turnos",
                                   titulo_style))
        elementos.append(Paragraph(
            f"Período: {periodo} ({desde.strftime('%d/%m/%Y')} - "
            f"{hasta.strftime('%d/%m/%Y')})", sub_style))
        elementos.append(Spacer(1, 0.3*cm))

        # Encabezados
        encabezados = ["Fecha", "Hora", "Cliente", "Empleado",
                       "Servicio", "Precio", "Seña", "Estado"]
        datos = [encabezados]

        for t in turnos:
            fecha = t["fecha_hora"]
            dia = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
            hora = fecha.strftime("%H:%M") if hasattr(fecha, "strftime") else ""
            cliente = f"{t['cli_nombre']} {t['cli_apellido']}"
            empleado = f"{t['emp_nombre']} {t['emp_apellido']}"
            precio = f"${float(t['precio_total'] or 0):.2f}"
            sena = f"${float(t['sena'] or 0):.2f}"
            datos.append([dia, hora, cliente, empleado,
                          t["servicio"], precio, sena, t["estado"]])

        tabla = Table(datos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rosa),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#FADADD")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(Paragraph(
            f"Total de turnos: {len(turnos)}",
            ParagraphStyle("total", parent=styles["Normal"],
                           fontSize=10, textColor=colors.grey)))

        doc.build(elementos)
        messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")

    def _generar_pdf_cliente(self, ruta, turnos, nombre_cliente):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(ruta, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        rosa = colors.HexColor("#D68092")

        titulo_style = ParagraphStyle(
            "titulo", parent=styles["Heading1"],
            textColor=rosa, fontSize=16, spaceAfter=6)
        sub_style = ParagraphStyle(
            "sub", parent=styles["Normal"],
            textColor=colors.grey, fontSize=10, spaceAfter=12)

        elementos = []
        elementos.append(Paragraph(
            f"Historial de cliente - MiSpa Turnos", titulo_style))
        elementos.append(Paragraph(
            f"Cliente: {nombre_cliente}", sub_style))
        elementos.append(Spacer(1, 0.3*cm))

        encabezados = ["Fecha", "Hora", "Servicio",
                       "Empleado", "Precio", "Seña", "Estado"]
        datos = [encabezados]

        for t in turnos:
            fecha = t["fecha_hora"]
            dia = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
            hora = fecha.strftime("%H:%M") if hasattr(fecha, "strftime") else ""
            empleado = f"{t['emp_nombre']} {t['emp_apellido']}"
            precio = f"${float(t['precio_total'] or 0):.2f}"
            sena = f"${float(t['sena'] or 0):.2f}"
            datos.append([dia, hora, t["servicio"], empleado,
                          precio, sena, t["estado"]])

        tabla = Table(datos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rosa),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#FADADD")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(Paragraph(
            f"Total de servicios: {len(turnos)}",
            ParagraphStyle("total", parent=styles["Normal"],
                           fontSize=10, textColor=colors.grey)))

        doc.build(elementos)
        messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")