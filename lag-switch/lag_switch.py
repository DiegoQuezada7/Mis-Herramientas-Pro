import tkinter as tk
import subprocess
import keyboard
import threading
import time
import ctypes
import sys
import os

# Colores UI
COLOR_ON = "#00ff00" # Internet Vivo
COLOR_OFF = "#ff0000" # Internet Muerto
COLOR_BG = "#111111"

class LagSwitchApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lag Switch 🛑")
        self.root.geometry("300x150")
        self.root.configure(bg=COLOR_BG)
        self.root.overrideredirect(True) # Sin bordes
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)

        # Centrar en pantalla abajo derecha
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = screen_w - 320
        pos_y = screen_h - 200
        self.root.geometry(f"300x120+{pos_x}+{pos_y}")

        self.is_lagging = False

        # UI
        self.lbl_status = tk.Label(self.root, text="ONLINE 🟢", font=("Impact", 30), fg=COLOR_ON, bg=COLOR_BG)
        self.lbl_status.pack(pady=20)
        
        self.lbl_info = tk.Label(self.root, text="[CTRL + SHIFT + L]", font=("Consolas", 10), fg="white", bg=COLOR_BG)
        self.lbl_info.pack()

        # Botón de Cerrar [X]
        self.btn_close = tk.Label(self.root, text="❌", font=("Arial", 10), fg="white", bg=COLOR_BG, cursor="hand2")
        self.btn_close.place(x=275, y=5)
        self.btn_close.bind("<Button-1>", self.close_app)

        # Hotkey Global
        keyboard.add_hotkey('ctrl+shift+l', self.toggle_lag)
        
        # Arrastrar ventana (click en cualquier lado vacio)
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)

    def close_app(self, event=None):
        # Asegurar que restauramos internet antes de irnos
        if self.is_lagging:
            self.restore_net()
        self.root.destroy()
        sys.exit()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_lag(self):
        self.is_lagging = not self.is_lagging
        
        if self.is_lagging:
            self.lbl_status.config(text="OFFLINE 🔴", fg=COLOR_OFF)
            self.lbl_info.config(text="Cortando conexión...")
            threading.Thread(target=self.kill_net).start()
        else:
            self.lbl_status.config(text="ONLINE 🟢", fg=COLOR_ON)
            self.lbl_info.config(text="Restaurando...")
            threading.Thread(target=self.restore_net).start()

    def kill_net(self):
        # La forma más rápida y recuperable: ipconfig /release
        try:
            # Opción A: Release (Suave, el sistema sabe que no tiene IP)
            subprocess.run(["ipconfig", "/release"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Opción B (Más sucia pero efectiva si release falla): Desactivar adaptador (requiere saber nombre)
            # Nos quedamos con A por compatibilidad.
        except Exception as e:
            print(e)

    def restore_net(self):
        try:
            subprocess.run(["ipconfig", "/renew"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        # Re-ejecutar como admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = LagSwitchApp()
        app.root.mainloop()
