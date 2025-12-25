from PIL import Image, ImageDraw
import os
import sys

# Píxeles de diferencia para considerar algo "mismo color"
TOLERANCE = 30 

def is_background(pixel):
    # Detectar si es gris/blanco (cuadros de ajedrez falsos)
    r, g, b, a = pixel
    # Si la saturación es baja (gris/blanco) Y es brillante (>200) o gris medio (>100)
    saturation = max(r, g, b) - min(r, g, b)
    if saturation < 30 and r > 100:
        return True
    return False

def smart_clean():
    files = ["dino1.png", "dino2.png", "dino3.png"]
    
    for f in files:
        if not os.path.exists(f):
            continue
            
        print(f"Operando {f}...")
        img = Image.open(f).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        # Algoritmo Flood Fill (Inundación) desde las 4 esquinas
        # Solo borramos si logramos conectar con el borde.
        # Los ojos estan aislados dentro, asi que no se tocarán.
        
        stack = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited:
                continue
            
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
                
            visited.add((x, y))
            
            # Chequear si este pixel parece fondo
            if is_background(pixels[x, y]):
                # BORRARLO
                pixels[x, y] = (0, 0, 0, 0)
                
                # Expandir a vecinos
                stack.append((x+1, y))
                stack.append((x-1, y))
                stack.append((x, y+1))
                stack.append((x, y-1))

        img.save(f)
        print(f" -> {f} limpiado (Ojos protegidos).")

if __name__ == "__main__":
    smart_clean()
