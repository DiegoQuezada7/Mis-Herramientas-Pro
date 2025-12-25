import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import cv2
from cv2 import dnn_superres
import os
import threading
import requests
import time
from PIL import Image, ImageTk

# Configuración (CALIDAD MAXIMA - EDSR)
MODEL_URL = "https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x4.pb"
MODEL_NAME = "EDSR_x4.pb"
SCALE_FACTOR = 4
MODELS_DIR = "models"

class NeutronUpscaler(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Neutron Upscaler AI 💎")
        self.geometry("600x450")
        self.configure(bg="#121212")
        
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", background="#121212", foreground="white")
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TProgressbar", thickness=10)
        
        # Header
        self.lbl_title = ttk.Label(self, text="Neutron Upscaler AI", font=("Segoe UI", 24, "bold"), foreground="#00e5ff")
        self.lbl_title.pack(pady=20)
        
        self.lbl_status = ttk.Label(self, text="Esperando imagen...", font=("Segoe UI", 11), foreground="#888")
        self.lbl_status.pack()

        # Zona Drop
        self.frame_drop = tk.Frame(self, bg="#1e1e1e", width=400, height=200, highlightthickness=2, highlightbackground="#333")
        self.frame_drop.pack(pady=30)
        self.frame_drop.pack_propagate(False)
        
        self.lbl_drop = tk.Label(self.frame_drop, text="Arrastra tu imagen pequeña aquí\n(JPG, PNG, WEBP)", 
                                 fg="#666", bg="#1e1e1e", font=("Segoe UI", 12))
        self.lbl_drop.place(relx=0.5, rely=0.5, anchor="center")
        
        # Eventos Drop
        self.frame_drop.drop_target_register(DND_FILES)
        self.frame_drop.dnd_bind('<<Drop>>', self.on_drop)
        
        # ProgressBar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        # Info Model
        self.lbl_model = ttk.Label(self, text=f"Modelo: {MODEL_NAME} (x{SCALE_FACTOR})", font=("Consolas", 8), foreground="#444")
        self.lbl_model.pack(side="bottom", pady=10)
        
        # Check Model al inicio
        self.check_model_thread()

    def check_model_thread(self):
        threading.Thread(target=self.download_model_if_needed, daemon=True).start()

    def download_model_if_needed(self):
        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)
            
        model_path = os.path.join(MODELS_DIR, MODEL_NAME)
        # Verificar existencia Y tamaño (EDSR pesa ~38MB, si es pequeño es error o modelo viejo)
        if not os.path.exists(model_path) or os.path.getsize(model_path) < 10000000:
            self.update_status(f"Descargando Cerebro Gigante ({MODEL_NAME})...", "#ffaa00")
            try:
                response = requests.get(MODEL_URL, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                wrote = 0
                
                with open(model_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        wrote += len(data)
                        f.write(data)
                        # Progreso descarga
                        if total_size > 0:
                            perc = (wrote / total_size) * 100
                            self.progress['value'] = perc
                            
                self.update_status("Modelo EDSR Descargado. Listo.", "#00e5ff")
                self.progress['value'] = 0
            except Exception as e:
                self.update_status(f"Error descarga: {str(e)}", "red")
        else:
            self.update_status("Sistema IA: Online y Listo.", "#00ff00")

    def update_status(self, text, color="white"):
        self.lbl_status.config(text=text, foreground=color)

    def on_drop(self, event):
        file_path = event.data.strip('{}') # Limpiar path
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.jfif')):
            threading.Thread(target=self.process_image, args=(file_path,), daemon=True).start()
        else:
            self.update_status("Archivo no válido. Solo imágenes.", "red")

    def process_image(self, file_path):
        model_path = os.path.join(MODELS_DIR, MODEL_NAME)
        if not os.path.exists(model_path):
            self.update_status("Falta el modelo IA. Reinicia la app.", "red")
            return

        try:
            self.update_status("Cargando neutrones...", "#00e5ff")
            self.progress['mode'] = 'indeterminate'
            self.progress.start(10)
            
            # 1. Cargar Upscaler
            sr = dnn_superres.DnnSuperResImpl_create()
            sr.readModel(model_path)
            # EDSR (Calidad Máxima)
            sr.setModel("edsr", SCALE_FACTOR)
            
            # 2. Leer Imagen
            img = cv2.imread(file_path)
            if img is None: raise Exception("No se pudo leer la imagen")
            
            # 3. Procesar (Upscale)
            self.update_status("Upscaling con Red Neuronal Profunda...", "#ff00ff")
            
            start_time = time.time()
            result = sr.upsample(img) # MAGIA DE ALTA CALIDAD AQUÍ
            elapsed = time.time() - start_time
            
            # 4. Guardar
            folder, filename = os.path.split(file_path)
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_HD_EDSR_x{SCALE_FACTOR}{ext}"
            save_path = os.path.join(folder, new_filename)
            
            cv2.imwrite(save_path, result)
            
            self.progress.stop()
            self.progress['mode'] = 'determinate'
            self.progress['value'] = 100
            self.update_status(f"¡Hecho! en {elapsed:.2f}s", "#00ff00")
            
            time.sleep(3)
            self.update_status("Listo para la siguiente.", "#888")
            self.progress['value'] = 0
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"Error: {str(e)}", "red")
            print(e)
            # Fallback a FSRCNN si falla EDSR
            if "fsrcnn" not in MODEL_NAME.lower():
                 self.update_status("EDSR falló. ¿Memoria insuficiente?", "red")

if __name__ == "__main__":
    app = NeutronUpscaler()
    app.mainloop()
