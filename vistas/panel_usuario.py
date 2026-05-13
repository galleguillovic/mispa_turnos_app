import tkinter as tk

class PanelUsuario(tk.Toplevel):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.master = master
        self.usuario = usuario
        self.title("MiSpa Turnos - Panel Usuario")
        self.geometry("1100x620")
        self.configure(bg="#D68092")
        self.protocol("WM_DELETE_WINDOW", lambda: self.master.destroy())

        tk.Label(
            self,
            text=f"Bienvenida, {usuario['nombre']}",
            bg="#D68092", fg="white",
            font=("Poppins", 16)
        ).pack(pady=40)