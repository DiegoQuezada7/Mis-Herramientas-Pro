import time
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pynput import keyboard
from pynput.keyboard import Key, Controller
from datetime import datetime
import os
import sys

# Archivo de configuración
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(get_base_path(), "TextExpander_Config.json")

# Valores por defecto si no existe archivo
DEFAULT_SHORTCUTS = {
    ";mail": "mi_email_personal@gmail.com",
    ";fecha": "%d/%m/%Y",  # Formato strftime
    ";hora": "%H:%M",
    ";saludo": "Hola, quedo atento a tus comentarios."
}

class TextExpander:
    def __init__(self):
        self.keyboard = Controller()
        self.current_buffer = ""
        self.shortcuts = {}
        self.load_shortcuts()
        self.editor_open = False

    def load_shortcuts(self):
        if not os.path.exists(CONFIG_FILE):
            self.save_shortcuts_to_file(DEFAULT_SHORTCUTS)
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
        else:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.shortcuts = json.load(f)
            except Exception:
                self.shortcuts = DEFAULT_SHORTCUTS.copy()
        print(" [Sys] Atajos cargados:", len(self.shortcuts))

    def save_shortcuts_to_file(self, data):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def on_press(self, key):
        if self.editor_open: return # No expandir mientras editamos

        try:
            if hasattr(key, 'char') and key.char:
                self.current_buffer += key.char
            elif key == Key.space:
                self.current_buffer += " "
            elif key == Key.enter:
                self.current_buffer = ""
            elif key == Key.backspace:
                self.current_buffer = self.current_buffer[:-1]
            
            if len(self.current_buffer) > 50:
                self.current_buffer = self.current_buffer[-50:]

            self.check_triggers()

        except Exception:
            pass

    def check_triggers(self):
        # Trigger especial de configuración
        if self.current_buffer.endswith(";config"):
            self.clean_buffer(";config")
            self.open_editor()
            self.current_buffer = ""
            return

        for trigger, replacement in self.shortcuts.items():
            if self.current_buffer.endswith(trigger):
                self.expand(trigger, replacement)
                self.current_buffer = ""
                break

    def clean_buffer(self, text):
        # Borrar lo escrito (backspace)
        for _ in range(len(text)):
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)
            time.sleep(0.01)

    def expand(self, trigger, replacement):
        self.clean_buffer(trigger)

        # Procesar fechas dinámicas (si el reemplazo parece formato de fecha)
        final_text = replacement
        if "%" in replacement and len(replacement) < 20: 
            try:
                final_text = datetime.now().strftime(replacement)
            except:
                pass # Si no era fecha, escribir literal

        self.keyboard.type(final_text)

    def open_editor(self):
        self.editor_open = True
        
        # GUI
        root = tk.Tk()
        root.title("Editor de Atajos Phantom 👻")
        root.geometry("500x400")
        root.attributes('-topmost', True)

        # Treeview
        cols = ('Trigger', 'Reemplazo')
        tree = ttk.Treeview(root, columns=cols, show='headings')
        tree.heading('Trigger', text='Atajo (ej: ;mail)')
        tree.heading('Reemplazo', text='Texto final')
        tree.column('Trigger', width=100)
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        for t, r in self.shortcuts.items():
            tree.insert("", "end", values=(t, r))

        frame_btns = tk.Frame(root)
        frame_btns.pack(pady=10)

        def add_item():
            trig = simpledialog.askstring("Nuevo", "Escribe el atajo (ej: ;test):", parent=root)
            if not trig: return
            repl = simpledialog.askstring("Nuevo", f"Texto para '{trig}':", parent=root)
            if not repl: return
            
            tree.insert("", "end", values=(trig, repl))
            self.shortcuts[trig] = repl

        def del_item():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            trig = item['values'][0]
            del self.shortcuts[trig]
            tree.delete(sel[0])

        def save_and_close():
            self.save_shortcuts_to_file(self.shortcuts)
            messagebox.showinfo("Guardado", "Atajos actualizados correctamente.")
            root.destroy()
            self.editor_open = False
            self.load_shortcuts() # Recargar en memoria

        tk.Button(frame_btns, text="➕ Agregar", command=add_item).pack(side="left", padx=5)
        tk.Button(frame_btns, text="➖ Eliminar", command=del_item).pack(side="left", padx=5)
        tk.Button(frame_btns, text="💾 Guardar y Cerrar", command=save_and_close, bg="#dddddd").pack(side="left", padx=20)

        root.protocol("WM_DELETE_WINDOW", save_and_close)
        root.mainloop()

    def start(self):
        print(" --- PHANTOM ACTIVO ---")
        print(" Escribe ;config para abrir el editor de atajos.")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

import socket
import sys

# ... (resto de imports)

# ... (clase TextExpander)

def check_singleton():
    """ Evita múltiples instancias usando un socket """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 65432)) # Puerto interno aleatorio alto
        return s
    except OSError:
        print("\n [!] ERROR: Ya hay un Phantom corriendo en segundo plano.")
        return None

if __name__ == "__main__":
    # Intentar obtener el candado
    lock_socket = check_singleton()
    if not lock_socket:
        print("     Cierra la ventana anterior o usa esa.")
        time.sleep(3)
        sys.exit() # Cerrar esta instancia duplicada
        
    TextExpander().start()
