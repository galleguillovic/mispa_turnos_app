# vista_clientes_usuario.py
import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk


class VistaClientesUsuario(tk.Frame):
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

    def _obtener_clientes(self, busqueda=""):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            if busqueda:
                cursor.execute("""
                    SELECT c.id_cliente, p.nombre, p.apellido,
                           p.telefono, p.dni, p.email,
                           c.preferencias, c.estado, c.notas
                    FROM clientes c
                    JOIN personas p ON c.id_persona = p.id_persona
                    WHERE c.estado = 'activo'
                      AND (p.nombre LIKE %s OR p.apellido LIKE %s)
                    ORDER BY p.apellido
                """, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cursor.execute("""
                    SELECT c.id_cliente, p.nombre, p.apellido,
                           p.telefono, p.dni, p.email,
                           c.preferencias, c.estado, c.notas
                    FROM clientes c
                    JOIN personas p ON c.id_persona = p.id_persona
                    WHERE c.estado = 'activo'
                    ORDER BY p.apellido
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

        tk.Label(frame_top, text="Listado de clientes",
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
        style.configure("CLI.Treeview",
                        background="white", foreground="#333333",
                        rowheight=40, fieldbackground="white",
                        font=("Poppins", 10), borderwidth=0)
        style.configure("CLI.Treeview.Heading",
                        background="#D68092", foreground="white",
                        font=("Poppins ExtraBold", 11), relief="flat")
        style.map("CLI.Treeview",
                  background=[("selected", "#FADADD")],
                  foreground=[("selected", "#333333")])

        cols = ("nombre", "apellido", "telefono", "detalles")
        self.tree = ttk.Treeview(container, columns=cols, show="headings",
                                 style="CLI.Treeview", selectmode="browse")

        encabezados = {"nombre": "Nombre", "apellido": "Apellido",
                       "telefono": "Teléfono", "detalles": "Detalles"}
        anchos = {"nombre": 200, "apellido": 200,
                  "telefono": 160, "detalles": 90}

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

        self._clientes_cache = []
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
        if idx >= len(self._clientes_cache):
            return
        if col == "#4":
            self._mostrar_detalles(self._clientes_cache[idx])

    def _filtrar(self):
        self._renderizar_filas(self._obtener_clientes(self.var_buscar.get()))

    def _cargar_filas(self):
        self._renderizar_filas(self._obtener_clientes())

    def _renderizar_filas(self, clientes):
        self.tree.delete(*self.tree.get_children())
        self._clientes_cache = clientes
        for i, c in enumerate(clientes):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=(
                c["nombre"], c["apellido"],
                c.get("telefono") or "—", "👁"
            ), tags=(tag,))

    # DETALLES

    def _mostrar_detalles(self, cliente):
        self._limpiar()

        tk.Label(self, text="Visualización detalles del cliente",
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

        # Ícono genérico de cliente
        try:
            img = Image.open(os.path.join(
                "assets", "user_rosa.png")).resize((70, 70), Image.LANCZOS)
            self._foto_cli = ImageTk.PhotoImage(img)
            tk.Label(frame_enc, image=self._foto_cli,
                     bg="white").pack(side="left", padx=(0, 15))
        except Exception:
            pass

        frame_nombre_enc = tk.Frame(frame_enc, bg="white")
        frame_nombre_enc.pack(side="left")
        tk.Label(frame_nombre_enc, text="Información del cliente:",
                 bg="white", fg="#999999", font=("Poppins", 12)).pack(anchor="w")
        tk.Label(frame_nombre_enc,
                 text=f"{cliente['nombre']} {cliente['apellido']}",
                 bg="white", fg="#333333",
                 font=("Poppins ExtraBold", 20)).pack(anchor="w")

        frame_info = tk.Frame(tarjeta, bg="white")
        frame_info.pack(fill="x", padx=25, pady=(0, 20))

        for etiqueta, valor in [
            ("Teléfono",              cliente.get("telefono") or "—"),
            ("DNI (op)",              str(cliente["dni"]) if cliente.get("dni") else "—"),
            ("Correo electrónico (op)", cliente.get("email") or "—"),
            ("Preferencias (op)",     cliente.get("preferencias") or "—"),
            ("Estado",                cliente.get("estado") or "—"),
            ("Notas adicionales (op)", cliente.get("notas") or "—"),
        ]:
            fila = tk.Frame(frame_info, bg="white")
            fila.pack(anchor="w", pady=3)
            tk.Label(fila, text=f"{etiqueta}:", bg="white", fg="#555555",
                     font=("Poppins ExtraBold", 11)).pack(side="left")
            tk.Label(fila, text=f" {valor}", bg="white", fg="#555555",
                     font=("Poppins", 11), wraplength=700).pack(side="left")