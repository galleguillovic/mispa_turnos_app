import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class VentanaLogin(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("MiSpa Turnos - Iniciar sesión")
        self.resizable(False, False)
        self.configure(bg="#D68092")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        ancho = 1100
        alto = 620
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        self._construir_ui()

    def _construir_ui(self):
        frame_izq = tk.Frame(self, bg="#D68092")
        frame_izq.place(x=0, y=0, width=550, height=620)

        tk.Label(
            frame_izq,
            text="MiSpa Turnos",
            bg="#D68092",
            fg="white",
            font=("Mogra", 34)
        ).place(relx=0.5, y=80, anchor="center")

        ruta_logo = os.path.join("assets", "loto.png")
        try:
            img_loto = Image.open(ruta_logo).resize((220, 220), Image.LANCZOS)
            self.foto_loto = ImageTk.PhotoImage(img_loto)
            tk.Label(frame_izq, image=self.foto_loto, bg="#D68092").place(
                relx=0.5, y=280, anchor="center"
            )
        except Exception:
            pass

        tk.Label(
            frame_izq,
            text="Ingresa para gestionar tus turnos",
            bg="#D68092",
            fg="white",
            font=("Poppins", 12)
        ).place(relx=0.5, y=510, anchor="center")

        canvas_tarjeta = tk.Canvas(
            self, width=420, height=520,
            bg="#D68092", highlightthickness=0
        )
        canvas_tarjeta.place(x=600, y=50)
        self._dibujar_tarjeta_redondeada(canvas_tarjeta, 0, 0, 420, 520, 40, "white")

        contenido = tk.Frame(self, bg="white")
        contenido.place(x=620, y=70, width=380, height=480)

        ruta_user = os.path.join("assets", "user_rosa.png")
        try:
            img_user = Image.open(ruta_user).resize((100, 100), Image.LANCZOS)
            self.foto_user = ImageTk.PhotoImage(img_user)
            tk.Label(contenido, image=self.foto_user, bg="white").pack(pady=(20, 5))
        except Exception:
            canvas_user = tk.Canvas(contenido, width=100, height=100,
                                    bg="white", highlightthickness=0)
            canvas_user.pack(pady=(20, 5))
            canvas_user.create_oval(25, 5, 75, 50, fill="#D68092", outline="")
            canvas_user.create_arc(5, 45, 95, 105, start=0,
                                   extent=180, fill="#D68092", outline="")

        frame_gmail = tk.Frame(contenido, bg="white")
        frame_gmail.pack(fill="x", padx=30, pady=(25, 0))

        ruta_user2 = os.path.join("assets", "user_gris.png")
        try:
            img_ico = Image.open(ruta_user2).resize((22, 22), Image.LANCZOS)
            self.foto_ico = ImageTk.PhotoImage(img_ico)
            tk.Label(frame_gmail, image=self.foto_ico, bg="white").pack(side="left")
        except Exception:
            tk.Label(frame_gmail, text="👤", bg="white",
                     font=("Poppins", 11)).pack(side="left")

        self.entry_email = tk.Entry(
            frame_gmail,
            font=("Poppins", 12),
            bd=0, fg="#999999", bg="white"
        )
        self.entry_email.insert(0, "Gmail")
        self.entry_email.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.entry_email.bind("<FocusIn>", self._limpiar_email)
        self.entry_email.bind("<FocusOut>", self._restaurar_email)

        tk.Frame(contenido, bg="#CCCCCC", height=1).pack(
            fill="x", padx=30, pady=(6, 20))

        frame_pass = tk.Frame(contenido, bg="white")
        frame_pass.pack(fill="x", padx=30, pady=(0, 0))

        ruta_candado = os.path.join("assets", "candado.png")
        try:
            img_candado = Image.open(ruta_candado).resize((22, 22), Image.LANCZOS)
            self.foto_candado = ImageTk.PhotoImage(img_candado)
            tk.Label(frame_pass, image=self.foto_candado, bg="white").pack(side="left")
        except Exception:
            tk.Label(frame_pass, text="🔒", bg="white",
                     font=("Poppins", 11)).pack(side="left")

        self.entry_pass = tk.Entry(
            frame_pass,
            font=("Poppins", 12),
            bd=0, fg="#999999", bg="white"
        )
        self.entry_pass.insert(0, "Contraseña")
        self.entry_pass.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.entry_pass.bind("<FocusIn>", self._limpiar_pass)
        self.entry_pass.bind("<FocusOut>", self._restaurar_pass)

        tk.Frame(contenido, bg="#CCCCCC", height=1).pack(
            fill="x", padx=30, pady=(6, 40))

        frame_botones = tk.Frame(contenido, bg="white")
        frame_botones.pack(fill="x", padx=30)

        tk.Button(
            frame_botones,
            text="Cerrar",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat",
            cursor="hand2", width=11,
            command=self.cerrar
        ).pack(side="left", ipady=10)

        tk.Button(
            frame_botones,
            text="Ingresar",
            bg="#D68092", fg="white",
            font=("Poppins", 11),
            bd=0, relief="flat",
            cursor="hand2", width=11,
            command=self.ingresar
        ).pack(side="right", ipady=10)

    def _dibujar_tarjeta_redondeada(self, canvas, x1, y1, x2, y2, radio, color):
        canvas.create_arc(x1, y1, x1+radio*2, y1+radio*2,
                          start=90, extent=90, fill=color, outline=color)
        canvas.create_arc(x2-radio*2, y1, x2, y1+radio*2,
                          start=0, extent=90, fill=color, outline=color)
        canvas.create_arc(x1, y2-radio*2, x1+radio*2, y2,
                          start=180, extent=90, fill=color, outline=color)
        canvas.create_arc(x2-radio*2, y2-radio*2, x2, y2,
                          start=270, extent=90, fill=color, outline=color)
        canvas.create_rectangle(x1+radio, y1, x2-radio, y2, fill=color, outline=color)
        canvas.create_rectangle(x1, y1+radio, x2, y2-radio, fill=color, outline=color)

    def _limpiar_email(self, event):
        if self.entry_email.get() == "Gmail":
            self.entry_email.delete(0, tk.END)
            self.entry_email.config(fg="black")

    def _restaurar_email(self, event):
        if self.entry_email.get() == "":
            self.entry_email.insert(0, "Gmail")
            self.entry_email.config(fg="#999999")

    def _limpiar_pass(self, event):
        if self.entry_pass.get() == "Contraseña":
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.config(fg="black", show="*")

    def _restaurar_pass(self, event):
        if self.entry_pass.get() == "":
            self.entry_pass.insert(0, "Contraseña")
            self.entry_pass.config(fg="#999999", show="")

    def ingresar(self):
        email = self.entry_email.get()
        password = self.entry_pass.get()

        if email == "Gmail" or email == "":
            messagebox.showwarning("Atención", "Ingresá tu correo electrónico.")
            return
        if password == "Contraseña" or password == "":
            messagebox.showwarning("Atención", "Ingresá tu contraseña.")
            return

        from modelos.usuario import autenticar_usuario
        usuario = autenticar_usuario(email, password)

        if usuario is None:
            messagebox.showerror("Error", "Correo o contraseña incorrectos.")
            return

        self.destroy()

        if usuario["rol"] == "administrador":
            from vistas.panel_admin import PanelAdmin
            PanelAdmin(self.master, usuario)
        else:
            from vistas.panel_usuario import PanelUsuario
            PanelUsuario(self.master, usuario)

    def cerrar(self):
        self.master.destroy()