import os
import socket
import threading
import tkinter as tk
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import qrcode
from PIL import ImageTk, Image
import sys

import sys
import logging
from urllib.parse import unquote

# Configuración de Logs (Para ver por qué falla)
# Se guardará en la misma carpeta del exe
log_file = os.path.join(os.path.dirname(sys.executable), '_airdrop_debug.txt')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Determinar ruta base real (donde está el .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(".")

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'shared_files')

# Asegurar que existe
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except Exception as e:
        logging.error(f"Error creando carpeta: {e}")

# ... (Resource path function sigue igual para templates internos) ...
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__, template_folder=resource_path("templates"), static_folder=resource_path("static"))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.info(f"Iniciando servidor. Upload Folder: {UPLOAD_FOLDER}")

# --- Rutas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/files')
def list_files():
    files = []
    try:
        for f in os.listdir(app.config['UPLOAD_FOLDER']):
            if not f.startswith('.'):
                path = os.path.join(app.config['UPLOAD_FOLDER'], f)
                is_dir = os.path.isdir(path)
                files.append({'name': f, 'is_dir': is_dir})
    except Exception as e:
        logging.error(f"Error listando archivos: {e}")
    return jsonify(files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')
    saved_files = []
    
    for file in files:
        if file.filename == '':
            continue
        # Usamos nombre original, secure_filename a veces es muy agresivo
        # Solo aseguramos que no sea una ruta relativa maliciosa
        filename = os.path.basename(file.filename)
            
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(save_path)
            saved_files.append(filename)
            logging.info(f"Archivo subido: {filename}")
        except Exception as e:
            logging.error(f"Error guardando {filename}: {e}")
        
    return jsonify({'success': True, 'files': saved_files})

import mimetypes

@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        # 1. Decodificar URL (por si acaso Flask no lo hizo del todo)
        filename = unquote(filename)
        
        # 2. Log para debug
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logging.info(f"Solicitud de descarga: '{filename}' -> Buscando en: '{file_path}'")
        
        if not os.path.exists(file_path):
            logging.error(f"ARCHIVO NO ENCONTRADO: {file_path}")
            return "File not found on server logs", 404

        # 3. Adivinar tipo MIME
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream' 
            
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True, mimetype=mime_type)
    except Exception as e:
        logging.error(f"Excepcion en descarga: {e}")
        return f"Error interno: {e}", 500

# --- Utils ---
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def show_qr(url):
    root = tk.Tk()
    root.title(f"Local AirDrop - {url}")
    
    # Generar QR
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    tk_img = ImageTk.PhotoImage(img)
    
    lbl_img = tk.Label(root, image=tk_img)
    lbl_img.pack(padx=20, pady=20)
    
    lbl_txt = tk.Label(root, text=f"Escanea o ve a:\n{url}", font=("Segoe UI", 12))
    lbl_txt.pack(pady=10)
    
    lbl_hint = tk.Label(root, text="Mueve archivos a la carpeta 'shared_files'", fg="#666")
    lbl_hint.pack(pady=5)
    
    root.mainloop()

if __name__ == '__main__':
    # Obtener IP
    ip = get_ip()
    port = 5050 # Cambiado para evitar conflicto con Wi-Fi Remote (5000)
    url = f"http://{ip}:{port}"
    
    print(f" --- LOCAL AIRDROP ---")
    print(f" 📂 Carpeta compartida: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f" 🔗 Acceso Web: {url}")
    
    # Lanzar QR en hilo
    threading.Thread(target=show_qr, args=(url,), daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
