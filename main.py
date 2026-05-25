# main.py
import tkinter as tk
import sys
import os

# Agregar el directorio del proyecto al path de Python
if getattr(sys, 'frozen', False):
    base = os.path.dirname(sys.executable)
else:
    base = os.path.dirname(os.path.abspath(__file__))
os.chdir(base)
sys.path.insert(0, base)

from vistas.login import VentanaLogin

def main():
    root = tk.Tk()
    root.withdraw()
    app = VentanaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main()