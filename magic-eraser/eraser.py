import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

class MagicEraserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Eraser 🪄🧼 (v2.0 Pro)")
        self.root.geometry("1000x800")
        self.root.configure(bg="#2b2b2b")

        # Estado Datos (Resolución Original)
        self.src_img = None        # Imagen original BGR
        self.mask = None           # Máscara original (0=Fondo, 255=Borrar)
        self.history = []          # Undo stack

        # Estado Visualización
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.tk_img = None
        
        # Pincel
        self.brush_size = 20
        self.drawing = False
        self.last_img_pt = None    # Último punto en coords de IMAGEN

        self._setup_ui()

        # Bindings extra
        self.canvas.bind("<MouseWheel>", self.on_zoom)     # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)       # Linux up
        self.canvas.bind("<Button-5>", self.on_zoom)       # Linux down

    def _setup_ui(self):
        # --- Toolbar ---
        toolbar = tk.Frame(self.root, bg="#1e1e1e", height=50)
        toolbar.pack(side="top", fill="x")

        style = {"bg": "#3e3e42", "fg": "white", "relief": "flat", "padx": 10, "pady": 5}
        
        tk.Button(toolbar, text="📂 Abrir", command=self.load_image, **style).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="💾 Guardar", command=self.save_image, **style).pack(side="left", padx=5)
        
        tk.Label(toolbar, text="| Zoom:", bg="#1e1e1e", fg="#888").pack(side="left", padx=10)
        self.lbl_zoom = tk.Label(toolbar, text="100%", bg="#1e1e1e", fg="white", width=5)
        self.lbl_zoom.pack(side="left")
        
        tk.Label(toolbar, text="| Pincel:", bg="#1e1e1e", fg="white").pack(side="left", padx=10)
        self.scale_brush = tk.Scale(toolbar, from_=5, to=100, orient="horizontal", bg="#1e1e1e", fg="white", 
                                    highlightthickness=0, command=self.update_brush_size)
        self.scale_brush.set(self.brush_size)
        self.scale_brush.pack(side="left")

        tk.Button(toolbar, text="↩ Deshacer", command=self.undo, **style).pack(side="left", padx=10)
        
        # Action Button
        tk.Button(toolbar, text="✨ BORRAR (INPAINT)", command=self.apply_inpaint, 
                  bg="#007fd4", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15).pack(side="right", padx=10)

        # --- Canvas ---
        self.canvas_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Usamos un Canvas que se redimensiona
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<Configure>", self.on_resize_window)
        
        self.root.bind("<Control-z>", lambda e: self.undo())

    def update_brush_size(self, val):
        self.brush_size = int(val)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if not path: return

        img = cv2.imread(path)
        if img is None: return
        
        self.src_img = img
        h, w = img.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8)
        self.history.clear()
        
        # Auto-Zoom para encajar
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw > 10 and ch > 10:
            scale_w = cw / w
            scale_h = ch / h
            self.zoom = min(scale_w, scale_h) * 0.9 # 90% del tamaño
            
            new_w = int(w * self.zoom)
            new_h = int(h * self.zoom)
            self.offset_x = (cw - new_w) // 2
            self.offset_y = (ch - new_h) // 2
        else:
            self.zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0
            
        self.redraw_canvas()

    def on_resize_window(self, event):
        # Si cambiamos el tamaño de ventana, re-centramos la imagen
        if self.src_img is not None:
            self.redraw_canvas()

    def on_zoom(self, event):
        if self.src_img is None: return
        
        # 1. ¿Dónde está el mouse ahora? (Punto Pibote)
        mx, my = event.x, event.y
        
        # 2. ¿Qué pixel de la imagen es ese?
        # mix = Mouse Image X
        mix = (mx - self.offset_x) / self.zoom
        miy = (my - self.offset_y) / self.zoom
        
        # 3. Calcular nuevo Zoom
        if event.num == 5 or event.delta < 0:
            scale = 0.9
        else:
            scale = 1.1
            
        new_zoom = self.zoom * scale
        
        # Límites (0.1x a 20x)
        if new_zoom < 0.1: new_zoom = 0.1
        if new_zoom > 20.0: new_zoom = 20.0
        
        # 4. Recalcular Offsets para mantener el pixel bajo el mouse quieto
        # mx = mix * new_zoom + new_offset_x
        # new_offset_x = mx - (mix * new_zoom)
        
        self.offset_x = mx - (mix * new_zoom)
        self.offset_y = my - (miy * new_zoom)
        
        self.zoom = new_zoom
        self.redraw_canvas()

    def get_image_coords(self, cx, cy):
        # Transforma coordenadas del Canvas -> Coordenadas de la Imagen Original
        # Offset es donde empieza la imagen pintada en el canvas
        ix = (cx - self.offset_x) / self.zoom
        iy = (cy - self.offset_y) / self.zoom
        return int(ix), int(iy)

    def redraw_canvas(self):
        if self.src_img is None: return
        
        # 1. Crear composición (Imagen + Máscara Roja)
        # Hacemos esto en resolución original o reducida? 
        # Para velocidad, mejor redimensionar primero y luego pintar mascara?
        # No, para precisión, redimensionamos ambas.
        
        h, w = self.src_img.shape[:2]
        new_w = int(w * self.zoom)
        new_h = int(h * self.zoom)
        
        # Resize Imagen BGR
        vis_img = cv2.resize(self.src_img, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        # Resize Mascara (para visualizar)
        vis_mask = cv2.resize(self.mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        
        # Pintar rojo donde máscara active (usando NumPy rápido)
        # Creamos una capa roja
        # Donde vis_mask > 0, pintar rojo
        # BGR: Rojo es (0, 0, 255)
        # Truco visual alpha blending manual simple
        
        # Indices donde hay mascara
        idx = vis_mask > 0
        # Aplicar tinte rojo (mezclar 50%)
        vis_img[idx] = vis_img[idx] * 0.5 + np.array([0, 0, 128]) # Tinte rojo oscuro
        
        # 2. Convertir a PIL
        img_rgb = cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        self.tk_img = ImageTk.PhotoImage(img_pil)
        
        # 3. Dibujar en Canvas usando Offset Actual (Zoom/Pan)
        # NOTA: Ya no centramos forzosamente aquí para permitir movernos.
        
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.tk_img, anchor="nw")
        
        # Info
        self.lbl_zoom.config(text=f"{int(self.zoom*100)}%")

    def start_draw(self, event):
        if self.src_img is None: return
        self.drawing = True
        
        # Guardar historial
        self.history.append((self.src_img.copy(), self.mask.copy()))
        if len(self.history) > 10: self.history.pop(0)
        
        ix, iy = self.get_image_coords(event.x, event.y)
        self.last_img_pt = (ix, iy)

    def draw(self, event):
        if not self.drawing or self.src_img is None: return
        
        ix, iy = self.get_image_coords(event.x, event.y)
        pt1 = self.last_img_pt
        pt2 = (ix, iy)
        
        # Pintar EN LA MÁSCARA ORIGINAL (Resolución Completa)
        # Importante: El grosor del pincel debe escalarse?
        # Si el usuario ve un pincel de 20px en pantalla, quiere pintar 20px de pantalla.
        # Por tanto, en la imagen original el grosor es 20 / zoom.
        real_brush = int(self.brush_size / self.zoom)
        if real_brush < 1: real_brush = 1
        
        cv2.line(self.mask, pt1, pt2, 255, real_brush)
        
        self.last_img_pt = pt2
        
        # Optimización: No redibujar TODO el canvas en cada movimiento (muy lento)
        # Podríamos dibujar lineas rojas temporales en el canvas con Tkinter
        # para feedback inmediato, y solo actualizar 'redraw_canvas' al soltar.
        self.draw_temp_line(event.x, event.y)

    def draw_temp_line(self, cx, cy):
        # Feedback visual rápido (sobre el canvas de Tkinter)
        # Necesitamos el punto anterior en coordenadas Canvas
        # last_img_pt está en coords Imagen. Lo pasamos a Canvas.
        
        lx, ly = self.last_img_pt # Esto es el nuevo 'last' después de actualizar draw
        # Espera, en draw() ya actualicé self.last_img_pt al punto actual.
        # Necesito el punto "previo" del evento anterior.
        # Simplificación: Usamos las coordenadas del evento directamente.
        
        # Pero necesito el DE DONDE VENGO.
        # Vamos a recalculardesde last_img_pt ANTES de actualizarlo? No.
        
        # Truco: Dibujar óvalos en el punto actual
        r = self.brush_size / 2
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#ff0000", outline="", stipple="gray50")
    
    def stop_draw(self, event):
        self.drawing = False
        # Ahora sí, regeneramos la imagen real de fondo
        self.redraw_canvas()

    def apply_inpaint(self):
        if self.src_img is None: return
        
        self.history.append((self.src_img.copy(), self.mask.copy()))
        
        # Inpainting
        # Radius debe ser proporcional al pincel
        radius = 5 
        res = cv2.inpaint(self.src_img, self.mask, radius, cv2.INPAINT_TELEA)
        
        self.src_img = res
        self.mask[:] = 0 # Limpiar máscara
        self.redraw_canvas()
        messagebox.showinfo("Magic Eraser", "¡Boom! Desaparecido.")

    def undo(self):
        if not self.history: return
        img, mask = self.history.pop()
        self.src_img = img
        self.mask = mask
        self.redraw_canvas()

    def save_image(self):
        if self.src_img is None: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", ".png"), ("JPG", ".jpg")])
        if path:
            cv2.imwrite(path, self.src_img)

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicEraserApp(root)
    root.mainloop()
