import tkinter as tk
from vistas.login import VentanaLogin

def main():
    root = tk.Tk()
    root.withdraw()
    app = VentanaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main()