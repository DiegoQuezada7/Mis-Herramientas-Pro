import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from rembg import remove
from PIL import Image, ImageTk
import io
import threading
import os

# Colores y Estilos
BG_COLOR = "#121212"
CARD_COLOR = "#1e1e1e"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#bb86fc"
SUCCESS_COLOR = "#03dac6"

class BGRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Background Remover ✨")
        self.root.geometry("500x400")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Variables
        self.status_var = tk.StringVar(value="Arrastra una imagen aquí")
        self.is_processing = False

        self.setup_ui()
        
        # Configurar Drag & Drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def setup_ui(self):
        # Contenedor principal
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Zona de Drop (Visual)
        self.drop_zone = tk.Label(self.main_frame, 
                                  text="⬇️\n\nArrastra y suelta tu imagen aquí\n(JPG, PNG, WEBP)", 
                                  font=("Segoe UI", 12),
                                  bg=CARD_COLOR, 
                                  fg="#aaaaaa",
                                  relief="flat",
                                  bd=2)
        self.drop_zone.pack(fill="both", expand=True, pady=(0, 20))
        
        # Borde punteado simulado (cambiando el borde del frame padre en una v2 si fuera necesario)
        
        # Estado
        self.lbl_status = tk.Label(self.main_frame, textvariable=self.status_var, bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(fill="x")

        # Barra de progreso (Indeterminada)
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        

    def handle_drop(self, event):
        if self.is_processing:
            return
            
        file_path = event.data
        # Limpiar path (a veces tkinterdnd devuelve llaves {} si hay espacios)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
            
        if not os.path.isfile(file_path):
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            self.status_var.set("❌ Formato no soportado")
            return

        self.start_processing(file_path)

    def start_processing(self, file_path):
        self.is_processing = True
        self.status_var.set("🤖 Procesando con IA... (Espera un poco)")
        self.drop_zone.config(bg=CARD_COLOR, fg=ACCENT_COLOR, text="⏳\n\nTrabajando magia...")
        self.progress.pack(fill="x", pady=10)
        self.progress.start(10)

        thread = threading.Thread(target=self.remove_background, args=(file_path,))
        thread.start()

    def remove_background(self, input_path):
        try:
            # Output path: imagen_rmbg.png
            folder, filename = os.path.split(input_path)
            name, _ = os.path.splitext(filename)
            output_path = os.path.join(folder, f"{name}_rmbg.png")

            # MAGIC HAPPENS HERE
            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input_image = i.read()
                    output_image = remove(input_image)
                    o.write(output_image)

            self.root.after(0, lambda: self.finish_processing(True, output_path))
        
        except Exception as e:
            print(e)
            self.root.after(0, lambda: self.finish_processing(False, str(e)))

    def finish_processing(self, success, result):
        self.progress.stop()
        self.progress.pack_forget()
        self.is_processing = False

        if success:
            self.status_var.set(f"✅ ¡Listo! Guardado como {os.path.basename(result)}")
            self.drop_zone.config(bg=CARD_COLOR, fg=SUCCESS_COLOR, text="✨ ¡Hecho! ✨\n\nArrastra otra imagen")
            
            # Intentar abrir la imagen (opcional)
            # os.startfile(result) 
        else:
            self.status_var.set("❌ Error al procesar")
            self.drop_zone.config(text="⚠️ Error ⚠️\n Intenta con otra imagen")
            messagebox.showerror("Error", f"Fallo en la IA:\n{result}")

if __name__ == "__main__":
    # Usar TkinterDnD en lugar de Tk normal
    root = TkinterDnD.Tk()
    app = BGRemoverApp(root)
    root.mainloop()
