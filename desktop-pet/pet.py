import tkinter as tk
from PIL import Image, ImageTk
import time
import random
import threading
import pygetwindow as gw
import sys
import os

# CONFIGURACIÓN
TARGET_HEIGHT = 100 # Altura deseada
WALK_SPEED = 5
ROAST_INTERVAL = 8
TRANS_COLOR = "#ff00ff" # Magenta (Clave de transparencia de Windows)

ROASTS = {
    # NAVEGADORES
    "chrome": ["Sé lo que buscas en incógnito...", "¿'Cómo tener talentos'?", "Cierra pestañas, tu PC pide auxilio.", "Google no tiene respuesta a tu incompetencia."],
    "brave": ["¿Te crees anónimo? Te veo igual.", "Bloqueas anuncios, pero no tu procrastinación.", "Usar Brave no te hace hacker, te hace hipster."],
    "edge": ["¿En serio usas Edge? Qué triste.", "Instala Chrome y ten dignidad.", "El explorador para descargar otros exploradores."],

    # CODIGO Y DEV
    "code": ["¿Llamas código a esa basura?", "ChatGPT programa mejor dormido.", "Borra eso antes de que alguien lo vea.", "Ese bug eres tú."],
    "visual studio": ["Ese tema oscuro no oculta tu mal código.", "¿Cuántas extensiones necesitas para escribir 'Hola Mundo'?", "Tu indentación ofende."],
    "docker": ["¿El contenedor pesa 2GB? Optimiza.", "Docker run 'tu_fracaso'.", "Levanta el servicio, no tu ego.", "Tus contenedores tienen fugas, como tu cerebro."],
    "python": ["Indentación nivel preescolar.", "¿Te crees hacker por usar print()?", "Ese script da cáncer visual.", "Deja de copiar de StackOverflow."],
    "powershell": ["Hacker de películas de los 90.", "rm -rf tu_dignidad", "¿Te sientes poderoso con esa ventanita azul?"],
    "cmd": ["Qué retro... y qué inútil.", "cls no borra tus errores de vida.", "Estás a un comando de romper todo."],

    # JUEGOS Y LAUNCHERS
    "league": ["¿Otra vez fideando?", "El Yasuo 0/10 eres tú.", "Desinstala y toca pasto.", "Bronce mentalidad.", "Reportado por manco."],
    "legends": ["¿Otra vez fideando?", "El Yasuo 0/10 eres tú.", "Desinstala y toca pasto.", "Bronce mentalidad.", "Reportado por manco."],
    "riot": ["¿Le vas a dar más dinero a Riot?", "Tu aim da pena.", "¿Instalock Jett? Qué original.", "Sal de hierro primero."],
    "valorant": ["Tu aim es inexistente.", "Deja de smurfear en hierro, das pena.", "¿Tienes skins para compensar tu falta de skill?"],
    "steam": ["¿Comprando juegos que nunca vas a jugar?", "Tu 'backlog' llora.", "Esas ofertas no llenarán tu vacío."],
    "epic": ["Solo entras por los juegos gratis, rata.", "Epic Games... Epic Fail.", "¿Dónde está tu dignidad?"],
    "battle.net": ["¿Sigues pagando suscripción?", "Blizzard te odia y tú les pagas.", "Qué buenos tiempos... hace 10 años."],
    "skyrim": ["¿Otra vez arquero sigiloso? Qué básico.", "Deja de modear y juega de una vez.", "Flecha en la rodilla... excusa barata."],
    "scrolls": ["¿Otra vez arquero sigiloso? Qué básico.", "Deja de modear y juega de una vez.", "Flecha en la rodilla... excusa barata."],
    "need for speed": ["Corres en el juego, te arrastras en la vida.", "Ese tuning es hortera hasta para 2005.", "Chocaste otra vez."],
    "pokemon": ["¿Atrapándolos a todos menos a un trabajo?", "Pikachu está decepcionado de ti.", "Ese shiny no existe, pierde el tiempo."],
    "pokemmo": ["Farmeando píxeles... qué vida.", "¿Te sientes mejor ganando a niños de 10 años?"],

    # UTILIDADES
    "nvidia": ["¿Drivers actualizados? Tu cerebro no.", "RTX ON, Productividad OFF.", "¿Para qué tanta gráfica si solo ves YouTube?"],
    "geforce": ["¿Para qué tanta gráfica si solo ves YouTube?", "Grabar tus partidas mancas no las mejora."],
    "discord": ["Nadie te quiere leer ahí.", "Simp detectado.", "Sal a tocar pasto, por favor.", "Tus 'amigos' online se ríen de ti."],
    "spotify": ["¿Llamas música a ese ruido?", "Mis oídos sangran píxeles.", "Ponte audífonos, das lástima.", "Qué gusto tan nefasto tienes."],
    "malwarebytes": ["El único virus aquí eres tú.", "¿Escaneando? Tu personalidad es la amenaza.", "Limpia tu cuarto, no solo tu PC."],
    
    # ENTRETENIMIENTO
    "youtube": ["¿Tutoriales? Igual no vas a aprender.", "Ese youtuber te odia en secreto.", "Das vergüenza ajena viendo eso.", "Cierra eso y ten dignidad."],
    "netflix": ["¿Tu vida es tan gris que ves la de otros?", "Otro capítulo, otro fracaso.", "Productividad: -1000%. Bravo.", "Te vas a pudrir en ese sofá."],
    
    # GENERICOS
    "game": ["¿Jugando en modo fácil? Manco.", "Vas a perder. Como en la vida.", "Reflejos de tortuga muerta.", "Desinstala el juego."],
    "default": ["Te odio.", "¿Por qué sigues aquí?", "Qué decepción de ser humano.", "Me das asco.", "¿No te cansas de fracasar?", "Mírate... patético.", "Tus iconos están desordenados.", "¿Ese fondo de pantalla? En serio?"]
}

class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANS_COLOR)
        self.root.config(bg=TRANS_COLOR)
        
        self.frames = self.load_sprites()
        if not self.frames:
            print("❌ No encontré dino1.png, dino2.png, dino3.png")
            sys.exit()

        self.current_frame = 0
        self.direction = 1 
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        # Posicionar
        vh = self.frames[0].height()
        self.x = 100
        self.y = self.screen_h - vh - 45 
        
        self.root.geometry(f"+{self.x}+{self.y}")
        
        self.lbl_dino = tk.Label(self.root, bg=TRANS_COLOR)
        self.lbl_dino.pack()
        
        self.setup_bubble()

        self.walking = True
        self.animate()
        self.walk()
        
        threading.Thread(target=self.judge_user, daemon=True).start()
        # Eventos ratón
        self.lbl_dino.bind("<Double-Button-1>", lambda e: sys.exit())
        self.lbl_dino.bind("<Button-3>", self.show_menu) # Click Derecho

        # Menu Contextual
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Cerrar Mascota", command=sys.exit)
        self.menu.add_command(label="Insultame ahora", command=lambda: self.judge_user(force=True))

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def setup_bubble(self):
        self.bubble = tk.Toplevel(self.root)
        self.bubble.overrideredirect(True)
        self.bubble.attributes("-topmost", True)
        self.lbl_text = tk.Label(self.bubble, text="", bg="#ffffe0", fg="black", font=("Comic Sans MS", 9), borderwidth=1, relief="solid", padx=5, pady=2)
        self.lbl_text.pack()
        self.bubble.withdraw()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_image(self, path):
        # Usar ruta absoluta gestionada
        abs_path = self.resource_path(path)
        if not os.path.exists(abs_path):
            return None
        return Image.open(abs_path).convert("RGBA")

    def process_frame(self, img):
        # 1. Redimensionar preservando aspecto
        aspect = img.width / img.height
        new_w = int(TARGET_HEIGHT * aspect)
        # USAR NEAREST PARA PIXEL ART (Evita bordes borrosos/magentas)
        img = img.resize((new_w, TARGET_HEIGHT), Image.Resampling.NEAREST)
        
        # 2. Crear fondo MAGENTA y pegar la imagen encima
        bg = Image.new("RGBA", img.size, (255, 0, 255, 255))
        bg.paste(img, (0, 0), img) 
        
        return bg.convert("RGB")

    def load_sprites(self):
        files = ["dino1.png", "dino2.png", "dino3.png"]
        images = []
        for f in files:
            img = self.load_image(f)
            if img:
                img = self.process_frame(img)
                images.append(ImageTk.PhotoImage(img))
        
        if not images: return []

        # Crear espejos (Mirando a la izquierda)
        self.frames_R = images
        self.frames_L = []
        
        for f in files:
            img = self.load_image(f)
            if img:
                img = self.process_frame(img) # Re-procesar desde original para calidad
                # Espejo manual no soportado facil en PhotoImage, mejor re-abrir y flipear PIL
                img_pil = self.load_image(f)
                img_pil = img_pil.transpose(Image.FLIP_LEFT_RIGHT)
                img_pil = self.process_frame(img_pil)
                self.frames_L.append(ImageTk.PhotoImage(img_pil))
                
        return images

    def animate(self):
        if self.walking:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            frs = self.frames_R if self.direction == 1 else self.frames_L
            self.lbl_dino.config(image=frs[self.current_frame])
        self.root.after(150, self.animate)

    def walk(self):
        if self.walking:
            self.x += WALK_SPEED * self.direction
            if self.x > self.screen_w - 80:
                self.direction = -1
            elif self.x < 0:
                self.direction = 1
            self.root.geometry(f"+{self.x}+{self.y}")
            self.bubble.geometry(f"+{self.x}+{self.y - 40}")
        if random.random() < 0.05:
            self.walking = not self.walking
        self.root.after(100, self.walk)

    def show_bubble(self, text):
        self.lbl_text.config(text=text)
        self.bubble.deiconify()
        self.bubble.geometry(f"+{self.x}+{self.y - 40}")
        self.root.after(4000, self.bubble.withdraw)

    def judge_user(self, force=False):
        while True:
            if not force:
                time.sleep(ROAST_INTERVAL)
            else:
                 # Si es forzado, saltamos la espera pero reseteamos el loop
                 pass

            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    title = active_window.title.lower()
                    found_key = "default"
                    for key in ROASTS:
                        if key in title:
                            found_key = key
                            break
                    msg = random.choice(ROASTS[found_key])
                    self.root.after(0, lambda m=msg: self.show_bubble(m))
            except:
                pass
            
            if force: break # Solo una vez si es forzado

if __name__ == "__main__":
    app = DesktopPet()
    app.root.mainloop()
