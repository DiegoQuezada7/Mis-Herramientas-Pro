import tkinter as tk
from tkinter import font
from PIL import ImageGrab, ImageTk, Image
from pynput import mouse, keyboard
import ctypes
import threading
import time
import pyperclip

# Configuración
ZOOM_LEVEL = 4
LENS_SIZE = 150
OFFSET_X = 20
OFFSET_Y = 20

# Constantes Windows
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

def make_click_through(hwnd):
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
    except Exception:
        pass

class PixelMaster:
    def __init__(self):
        # Eliminamos DPI Awareness forzado para no romper ImageGrab
        self.dpi_scale = 1.0
        try:
            # Obtener escala del monitor principal (ej: 125 -> 1.25)
            self.dpi_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0
        except Exception:
            pass
        print(f" [Debug] DPI Scale: {self.dpi_scale}")

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        self.canvas = tk.Canvas(self.root, width=LENS_SIZE, height=LENS_SIZE, 
                                bg='black', highlightthickness=1, highlightbackground='#007fd4')
        self.canvas.pack()
        
        self.lbl_info = tk.Label(self.root, text="#000000", font=("Consolas", 10, "bold"), 
                                 bg='#1e1e1e', fg='white', pady=5)
        self.lbl_info.pack(fill='x')
        
        tk.Label(self.root, text="F7: Guías | F8: Congelar", font=("Arial", 7), bg='#1e1e1e', fg='#888').pack(fill='x')
        tk.Label(self.root, text="F9: Copiar | ESC: Salir", font=("Arial", 7), bg='#1e1e1e', fg='#888').pack(fill='x')

        self.mouse_x = 0
        self.mouse_y = 0
        self.frozen = False
        self.current_hex = "#000000"
        
        # Crosshair Lines (Ventanas independientes)
        self.h_win = None
        self.v_win = None

        self.k_listener = keyboard.Listener(on_press=self.on_press)
        self.k_listener.start()
        
        self.m_listener = mouse.Listener(on_move=self.on_move)
        self.m_listener.start()
        
        self.update_lens()
        self.root.mainloop()

    def on_press(self, key):
        if key == keyboard.Key.f7: self.toggle_crosshair()
        elif key == keyboard.Key.f8: self.toggle_freeze()
        elif key == keyboard.Key.f9: self.copy_color()
        elif key == keyboard.Key.esc: self.quit()

    def on_move(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    # --- Wrappers ---
    def toggle_crosshair(self): self.root.after(0, self._toggle_crosshair)
    def toggle_freeze(self): self.root.after(0, self._toggle_freeze)
    def copy_color(self): self.root.after(0, self._copy_color)
    def quit(self): self.root.after(0, self._quit)

    # --- Logic ---
    def _toggle_crosshair(self):
        if self.h_win:
            self.h_win.destroy()
            self.v_win.destroy()
            self.h_win = None
            self.v_win = None
            print(" [HUD] Crosshair OFF")
        else:
            # Horizontal (Rojo)
            self.h_win = tk.Toplevel(self.root)
            self.h_win.overrideredirect(True)
            self.h_win.attributes('-topmost', True)
            tk.Frame(self.h_win, bg='red').pack(fill='both', expand=True)
            
            # Vertical (Rojo)
            self.v_win = tk.Toplevel(self.root)
            self.v_win.overrideredirect(True)
            self.v_win.attributes('-topmost', True)
            tk.Frame(self.v_win, bg='red').pack(fill='both', expand=True)
            
            self.h_win.update()
            self.v_win.update()
            
            make_click_through(ctypes.windll.user32.GetParent(self.h_win.winfo_id()))
            make_click_through(ctypes.windll.user32.GetParent(self.v_win.winfo_id()))
            print(" [HUD] Crosshair ON")

    def _toggle_freeze(self): self.frozen = not self.frozen

    def _copy_color(self):
        pyperclip.copy(self.current_hex)
        self.lbl_info.config(bg='green')
        self.root.after(200, lambda: self.lbl_info.config(bg='#1e1e1e'))

    def _quit(self):
        if self.h_win: 
            self.h_win.destroy()
            self.v_win.destroy()
        self.root.quit()
        self.k_listener.stop()
        self.m_listener.stop()

    def update_lens(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        
        # 1. Mover Crosshair (Corregido por escala)
        if self.h_win:
            # Compensar el zoom de Windows dividiendo coordenadas
            fix_x = int(self.mouse_x / self.dpi_scale)
            fix_y = int(self.mouse_y / self.dpi_scale)
            
            # Horizontal
            self.h_win.geometry(f"{screen_w}x2+0+{fix_y}")
            # Vertical
            self.v_win.geometry(f"2x{screen_h}+{fix_x}+0")
            
            self.h_win.lift()
            self.v_win.lift()

        # 2. Mover Lupa (rest of logic)
        # La lupa puede usar coordenadas normales porque pynput e ImageGrab suelen coincidir en modo 'unaware'
        if not self.frozen:
            x, y = self.mouse_x, self.mouse_y
            
            # Posicionamiento de la ventana (también compensado si es necesario, pero probemos normal)
            # Tkinter 'unaware' ya escala las ventanas, así que si le damos coords físicas, se va lejos.
            # Necesitamos darle coords lógicas.
            
            log_x = int(x / self.dpi_scale)
            log_y = int(y / self.dpi_scale)
            
            win_x, win_y = log_x + OFFSET_X, log_y + OFFSET_Y
            
            # Limites pantalla
            if win_x + LENS_SIZE > screen_w: win_x = log_x - LENS_SIZE - OFFSET_X
            if win_y + LENS_SIZE + 50 > screen_h: win_y = log_y - LENS_SIZE - OFFSET_Y
            
            self.root.geometry(f"{LENS_SIZE}x{LENS_SIZE+50}+{win_x}+{win_y}")
            
            # Captura
            grab_radius = (LENS_SIZE // ZOOM_LEVEL) // 2
            bbox = (x - grab_radius, y - grab_radius, x + grab_radius, y + grab_radius)
            try:
                img = ImageGrab.grab(bbox=bbox)
                cx, cy = img.width//2, img.height//2
                pixel = img.getpixel((cx, cy))
                self.current_hex = '#{:02x}{:02x}{:02x}'.format(*pixel).upper()
                
                self.lbl_info.config(text=f"{self.current_hex}")
                self.canvas.config(highlightbackground=self.current_hex)
                
                img = img.resize((LENS_SIZE, LENS_SIZE), Image.Resampling.NEAREST)
                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, image=self.tk_img, anchor='nw')
                
                mid = LENS_SIZE // 2
                self.canvas.create_line(mid-10, mid, mid+10, mid, fill='red')
                self.canvas.create_line(mid, mid-10, mid, mid+10, fill='red')
            except: pass
        
        self.root.after(20, self.update_lens)

if __name__ == "__main__":
    PixelMaster()
