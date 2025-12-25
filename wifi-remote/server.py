from flask import Flask, render_template, request, jsonify
import pyautogui
import socket
import qrcode
import threading
import tkinter as tk
from PIL import ImageTk, Image
import io
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app = Flask(__name__, template_folder=resource_path("templates"))

# Configuración PyAutoGUI
pyautogui.FAILSAFE = False # Permitir esquinas (cuidado)
pyautogui.PAUSE = 0

@app.route('/')
def index():
    return render_template('remote.html')

@app.route('/api/mouse')
def mouse_move():
    try:
        dx = float(request.args.get('dx', 0))
        dy = float(request.args.get('dy', 0))
        pyautogui.moveRel(dx, dy)
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/api/cmd/<cmd>')
def command(cmd):
    if cmd == 'click_left':
        pyautogui.click()
    elif cmd == 'click_right':
        pyautogui.click(button='right')
    elif cmd == 'media_play_pause':
        pyautogui.press('playpause')
    elif cmd == 'vol_up':
        pyautogui.press('volumeup')
    elif cmd == 'vol_down':
        pyautogui.press('volumedown')
    elif cmd == 'media_mute':
        pyautogui.press('volumemute')
        
    return jsonify(success=True)

@app.route('/api/type')
def type_text():
    text = request.args.get('text', '')
    if text:
        pyautogui.write(text)
        pyautogui.press('enter')
    return jsonify(success=True)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita ser alcanzable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def show_qr(url):
    root = tk.Tk()
    root.title(f"Escanea para conectar - {url}")
    
    qr = qrcode.QRCode(box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir para Tk
    tk_img = ImageTk.PhotoImage(img)
    
    lbl = tk.Label(root, image=tk_img)
    lbl.pack(padx=20, pady=20)
    
    lbl_txt = tk.Label(root, text=f"Accede desde tu móvil a:\n{url}", font=("Arial", 14), pady=10)
    lbl_txt.pack()
    
    root.mainloop()

if __name__ == '__main__':
    # 1. Obtener IP Local
    local_ip = get_ip()
    port = 5000
    access_url = f"http://{local_ip}:{port}"
    
    print(f" --- WI-FI REMOTE SERVER ---")
    print(f" Dirección: {access_url}")
    
    # 2. Mostrar QR en hilo separado
    threading.Thread(target=show_qr, args=(access_url,), daemon=True).start()
    
    # 3. Iniciar Servidor (Host 0.0.0.0 permite conexiones externas)
    app.run(host='0.0.0.0', port=port, debug=False)
