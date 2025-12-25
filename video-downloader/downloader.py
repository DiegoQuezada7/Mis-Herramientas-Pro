import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os

# Colores Dark Mode
BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
ACCENT_COLOR = "#007acc"
SECONDARY_COLOR = "#2d2d2d"
SUCCESS_COLOR = "#28a745"

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Saver Ultimate ⬇️")
        self.root.geometry("600x450")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Variables
        self.url_var = tk.StringVar()
        self.download_type = tk.StringVar(value="video") # video | audio
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.progress_var = tk.DoubleVar(value=0)
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos personalizados
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_COLOR)
        style.configure("TButton", font=("Segoe UI", 9), padding=6, background=SECONDARY_COLOR, foreground=FG_COLOR, borderwidth=0)
        style.map("TButton", background=[('active', ACCENT_COLOR)])
        
        style.configure("TRadiobutton", background=BG_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10))
        
        style.configure("Horizontal.TProgressbar", troughcolor=SECONDARY_COLOR, background=ACCENT_COLOR, bordercolor=BG_COLOR, lightcolor=ACCENT_COLOR, darkcolor=ACCENT_COLOR)

        # --- Header ---
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        lbl_title = ttk.Label(header_frame, text="Video Saver Ultimate", style="Header.TLabel")
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = ttk.Label(header_frame, text="Descarga videos de YouTube y más sitios en alta calidad.")
        lbl_subtitle.pack(anchor="w")

        # --- Input Area ---
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=20, pady=10)

        lbl_url = ttk.Label(input_frame, text="Pega el enlace del video:")
        lbl_url.pack(anchor="w", pady=(0, 5))

        entry_url = tk.Entry(input_frame, textvariable=self.url_var, font=("Segoe UI", 11), bg=SECONDARY_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, bd=0, relief="flat")
        entry_url.pack(fill="x", ipady=8)

        # --- Options Area ---
        opts_frame = ttk.Frame(self.root)
        opts_frame.pack(fill="x", padx=20, pady=15)

        lbl_type = ttk.Label(opts_frame, text="Formato:")
        lbl_type.grid(row=0, column=0, padx=(0, 10))

        rb_video = ttk.Radiobutton(opts_frame, text="Video (MP4)", variable=self.download_type, value="video", cursor="hand2")
        rb_video.grid(row=0, column=1, padx=10)

        rb_audio = ttk.Radiobutton(opts_frame, text="Solo Audio (MP3)", variable=self.download_type, value="audio", cursor="hand2")
        rb_audio.grid(row=0, column=2, padx=10)
        
        # Folder Selection
        btn_folder = ttk.Button(opts_frame, text="📂 Cambiar Carpeta", command=self.choose_folder)
        btn_folder.grid(row=0, column=3, padx=(20, 0), sticky="e")
        opts_frame.columnconfigure(3, weight=1)

        # --- Action Area ---
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=20, pady=20)

        self.btn_download = tk.Button(action_frame, text="DESCARGAR AHORA", command=self.start_download_thread, 
                                      bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 11, "bold"), 
                                      bd=0, relief="flat", cursor="hand2", activebackground="#005fa3", activeforeground="white")
        self.btn_download.pack(fill="x", ipady=10)

        # --- Progress Area ---
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.lbl_status = ttk.Label(progress_frame, textvariable=self.status_var, font=("Segoe UI", 9))
        self.lbl_status.pack(anchor="center")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder = folder
            messagebox.showinfo("Carpeta seleccionada", f"Las descargas se guardarán en:\n{folder}")

    def start_download_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Error", "Por favor pega un enlace válido.")
            return

        self.btn_download.config(state="disabled", text="Descargando...", bg=SECONDARY_COLOR)
        self.progress_var.set(0)
        
        # Run in thread to not freeze UI
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                self.progress_var.set(float(p))
                self.status_var.set(f"Descargando... {d.get('_percent_str')} | Vel: {d.get('_speed_str')} | Restante: {d.get('eta_str')}")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_var.set("Procesando y convirtiendo...")
            self.progress_var.set(100)

    def download_video(self, url):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
            }

            if self.download_type.get() == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                })

            self.status_var.set("Iniciando conexión...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
            
            self.root.after(0, lambda: self.finish_download(True, title))

        except Exception as e:
            err_msg = str(e)
            self.root.after(0, lambda: self.finish_download(False, err_msg))

    def finish_download(self, success, message):
        self.btn_download.config(state="normal", text="DESCARGAR AHORA", bg=ACCENT_COLOR)
        if success:
            self.status_var.set("✅ ¡Descarga Completa!")
            messagebox.showinfo("Éxito", f"Se descargó correctamente:\n{message}")
        else:
            self.status_var.set("❌ Error en la descarga")
            messagebox.showerror("Error", f"Ocurrió un error:\n{message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
