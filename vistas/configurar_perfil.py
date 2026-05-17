#configurar_perfil.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from PIL import Image, ImageTk, ImageDraw

class VistaConfigurarPerfil(tk.Frame):
    def __init__(self, master, panel):
        super().__init__(master, bg="#F9F0F2")
        self.panel = panel
        self.usuario = panel.usuario
        self.pack(fill="both", expand=True)
        self._nueva_foto_path = None
        self._foto_ref = None
        self._construir_ui()

    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _foto_circular(self, ruta, size=90):
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

    def _construir_ui(self):
        tk.Label(
            self,
            text="Editar información de perfil",
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

        # ── Fila 1: Foto + Nombre + Apellido ──
        frame_f1 = tk.Frame(form, bg="white")
        frame_f1.pack(fill="x", pady=(0, 10))

        # Foto
        frame_foto = tk.Frame(frame_f1, bg="white")
        frame_foto.pack(side="left", padx=(0, 25))

        tk.Label(frame_foto, text="Foto de perfil",
                 bg="white", fg="#999999",
                 font=("Poppins", 10)).pack(anchor="w")

        self.lbl_foto = tk.Label(frame_foto, bg="white")
        self.lbl_foto.pack()
        self._actualizar_foto_preview()

        tk.Button(
            frame_foto,
            text="✏ Cambiar foto",
            bg="white", fg="#999999",
            font=("Poppins", 9),
            bd=0, relief="flat", cursor="hand2",
            command=self._cambiar_foto
        ).pack(pady=(5, 0))

        # Nombre y Apellido
        frame_nombres = tk.Frame(frame_f1, bg="white")
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

        # ── Fila 2: Correo y Usuario ──
        frame_f2 = tk.Frame(form, bg="white")
        frame_f2.pack(fill="x", pady=(10, 0))

        tk.Label(frame_f2, text="Correo electrónico:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=0, sticky="w")
        tk.Label(frame_f2, text="Nombre de usuario:*", bg="white",
                 fg="#333333", font=("Poppins", 11)).grid(
            row=0, column=1, sticky="w", padx=(20, 0))

        self.entry_email = tk.Entry(
            frame_f2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_email.grid(row=1, column=0, sticky="ew",
                              ipady=8, pady=(4, 15))

        self.entry_usuario = tk.Entry(
            frame_f2, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat")
        self.entry_usuario.grid(row=1, column=1, sticky="ew",
                                ipady=8, pady=(4, 15), padx=(20, 0))

        frame_f2.columnconfigure(0, weight=1)
        frame_f2.columnconfigure(1, weight=1)

        # ── Fila 3: Contraseñas ──
        frame_f3 = tk.Frame(form, bg="white")
        frame_f3.pack(fill="x", pady=(0, 10))

        tk.Label(frame_f3, text="Cambiar contraseña:",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=0, column=0, sticky="w")
        tk.Label(frame_f3, text="Confirmar nueva contraseña:",
                 bg="white", fg="#333333",
                 font=("Poppins", 11)).grid(row=0, column=1, sticky="w",
                                            padx=(20, 0))

        self.entry_pass = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", show="*")
        self.entry_pass.grid(row=1, column=0, sticky="ew",
                             ipady=8, pady=(4, 0))

        self.entry_pass2 = tk.Entry(
            frame_f3, font=("Poppins", 11),
            bg="#EEEEEE", bd=0, relief="flat", show="*")
        self.entry_pass2.grid(row=1, column=1, sticky="ew",
                              ipady=8, pady=(4, 0), padx=(20, 0))

        frame_f3.columnconfigure(0, weight=1)
        frame_f3.columnconfigure(1, weight=1)

        # Prellenar datos
        self._prellenar()

        # Botones
        frame_btns = tk.Frame(tarjeta, bg="white")
        frame_btns.pack(anchor="e", padx=25, pady=(10, 20))

        tk.Button(
            frame_btns,
            text="Cancelar",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._cancelar
        ).pack(side="left", ipadx=15, ipady=8, padx=(0, 10))

        tk.Button(
            frame_btns,
            text="Guardar cambios",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat", cursor="hand2",
            command=self._guardar
        ).pack(side="left", ipadx=15, ipady=8)

    def _actualizar_foto_preview(self):
        if self._nueva_foto_path:
            ruta = self._nueva_foto_path
        elif self.usuario.get("foto"):
            ruta = os.path.join("assets", "fotos_perfil",
                                self.usuario["foto"])
        else:
            ruta = None

        foto = self._foto_circular(ruta, size=90)
        if foto:
            self._foto_ref = foto
            self.lbl_foto.config(image=foto)

    def _cambiar_foto(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto de perfil",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            self._nueva_foto_path = ruta
            self._actualizar_foto_preview()

    def _prellenar(self):
        from db.conexion import obtener_conexion, cerrar_conexion
        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.nombre, p.apellido, p.dni, p.telefono, p.email,
                       u.nombre_usuario
                FROM usuarios u
                JOIN personas p ON u.id_persona = p.id_persona
                WHERE u.id_usuario = %s
            """, (self.usuario["id_usuario"],))
            datos = cursor.fetchone()
        except Exception:
            datos = None
        finally:
            cerrar_conexion(conexion, cursor)

        if datos:
            self.entry_nombre.insert(0, datos.get("nombre", ""))
            self.entry_apellido.insert(0, datos.get("apellido", ""))
            if datos.get("dni"):
                self.entry_dni.insert(0, str(datos["dni"]))
            self.entry_telefono.insert(0, datos.get("telefono", "") or "")
            self.entry_email.insert(0, datos.get("email", "") or "")
            self.entry_usuario.insert(0, datos.get("nombre_usuario", ""))

    def _cancelar(self):
        for widget in self.panel.area_contenido.winfo_children():
            widget.destroy()
        self.panel.menu_activo = "Inicio"
        for widget in self.panel.sidebar.winfo_children():
            widget.destroy()
        self.panel._construir_sidebar()
        self.panel._mostrar_inicio()

    def _guardar(self):
        from utils.helpers import hashear_contrasena
        from db.conexion import obtener_conexion, cerrar_conexion

        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip() or None
        telefono = self.entry_telefono.get().strip()
        email = self.entry_email.get().strip()
        usuario = self.entry_usuario.get().strip()
        pass1 = self.entry_pass.get().strip()
        pass2 = self.entry_pass2.get().strip()

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
            messagebox.showwarning("Atención", "El correo es obligatorio.")
            return
        if not usuario:
            messagebox.showwarning("Atención",
                                   "El nombre de usuario es obligatorio.")
            return
        if pass1 or pass2:
            if pass1 != pass2:
                messagebox.showwarning("Atención",
                                       "Las contraseñas no coinciden.")
                return
            if len(pass1) < 6:
                messagebox.showwarning("Atención",
                                       "La contraseña debe tener al menos 6 caracteres.")
                return

        # Guardar foto si se seleccionó una nueva
        nombre_foto = self.usuario.get("foto")
        if self._nueva_foto_path:
            ext = os.path.splitext(self._nueva_foto_path)[1].lower()
            nombre_foto = f"perfil_{self.usuario['id_usuario']}{ext}"
            destino = os.path.join("assets", "fotos_perfil", nombre_foto)
            shutil.copy2(self._nueva_foto_path, destino)

        conexion = obtener_conexion()
        if not conexion:
            return
        try:
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE personas SET nombre=%s, apellido=%s,
                dni=%s, telefono=%s, email=%s
                WHERE id_persona = (
                    SELECT id_persona FROM usuarios
                    WHERE id_usuario = %s)
            """, (nombre, apellido, dni, telefono, email,
                  self.usuario["id_usuario"]))

            if pass1:
                hash_pass = hashear_contrasena(pass1)
                cursor.execute("""
                    UPDATE usuarios SET nombre_usuario=%s,
                    contrasena=%s, foto=%s
                    WHERE id_usuario=%s
                """, (usuario, hash_pass, nombre_foto,
                      self.usuario["id_usuario"]))
            else:
                cursor.execute("""
                    UPDATE usuarios SET nombre_usuario=%s, foto=%s
                    WHERE id_usuario=%s
                """, (usuario, nombre_foto, self.usuario["id_usuario"]))

            conexion.commit()

            # Actualizar datos en memoria
            self.usuario["nombre"] = nombre
            self.usuario["foto"] = nombre_foto

            messagebox.showinfo("Éxito", "Perfil actualizado correctamente.")
            self._cancelar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
        finally:
            cerrar_conexion(conexion, cursor)