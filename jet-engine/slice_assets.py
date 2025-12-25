from PIL import Image, ImageDraw, ImageOps
import os

# Ruta de la imagen generada (Asegúrate de que esta ruta sea correcta o haya sido inyectada)
SOURCE_IMG = r"C:/Users/diego/.gemini/antigravity/brain/bc3e8cd5-009b-416e-981e-9dfe0b00f4c2/jet_engine_ui_assets_1766431697028.png"
OUTPUT_DIR = r"c:/Users/diego/Desktop/Pruebas/jet-engine/assets"

def make_circle(img):
    # Crear mascara circular
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    
    # Aplicar mascara al alpha
    output = img.copy()
    output.putalpha(mask)
    return output

def slice_assets():
    if not os.path.exists(SOURCE_IMG):
        print("Error: No encuentro la imagen fuente.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    img = Image.open(SOURCE_IMG).convert("RGBA")
    
    # --- 1. Background (Panel) ---
    # Ajustamos recorte para quitar bordes feos si los hay
    # Coordenadas aproximadas del panel superior
    bg_crop = img.crop((60, 60, 940, 490)) 
    bg_crop = bg_crop.resize((400, 300))
    bg_crop.save(os.path.join(OUTPUT_DIR, "hud_bg.png"))
    
    # --- 2. Boton OFF (Circular) ---
    # Coordenadas aproximadas del boton azul (Izquierda Abajo)
    # Ajustando para centrar mejor el circulo
    btn_off_crop = img.crop((70, 560, 430, 920)) 
    btn_off_crop = btn_off_crop.resize((140, 140)) # Un poco mas grande
    btn_off_crop = make_circle(btn_off_crop)
    btn_off_crop.save(os.path.join(OUTPUT_DIR, "btn_off.png"))

    # --- 3. Boton ON (Circular) ---
    # Coordenadas aproximadas del boton fuego (Derecha Abajo)
    btn_on_crop = img.crop((570, 560, 930, 920))
    btn_on_crop = btn_on_crop.resize((140, 140))
    btn_on_crop = make_circle(btn_on_crop)
    btn_on_crop.save(os.path.join(OUTPUT_DIR, "btn_on.png"))
    
    print("Assets reparados (Círculos Transparentes) en:", OUTPUT_DIR)

if __name__ == "__main__":
    slice_assets()
