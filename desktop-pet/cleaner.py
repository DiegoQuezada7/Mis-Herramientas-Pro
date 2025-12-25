from PIL import Image, ImageChops
import os

def clean_and_split():
    if not os.path.exists("dino.png"):
        print("No encuentro dino.png")
        return

    img = Image.open("dino.png").convert("RGBA")
    
    # 1. ESTRATEGIA DE COLOR: 
    # Solo queremos lo que sea "Verde" o "Amarillo" (el cuerpo del dino).
    # Todo lo que sea Blanco (Fondo) o Negro/Gris (Bordes del cuadro) lo haremos transparente.
    
    datas = img.getdata()
    new_data = []
    
    for item in datas:
        r, g, b, a = item
        
        # Criterio: ¿Es un pixel de color vivo?
        # El dino es verde/amarillo. Tienen mucha saturación.
        # Blanco/Gris/Negro tienen R,G,B muy parecidos (baja saturación).
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        saturation = max_val - min_val
        
        # Si la saturación es baja (< 30), es gris/blanco/negro -> BORRAR
        if saturation < 30:
            new_data.append((0, 0, 0, 0)) # Transparente
        else:
            # Es color (el dino) -> MANTENER
            new_data.append(item)
            
    img.putdata(new_data)
    
    # 2. SEPARAR EN 3 IMAGENES
    # Primero recortamos los espacios vacíos generales
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    w, h = img.size
    # Asumimos que están distribuidos en 3 tercios
    part_w = w // 3
    
    frames = []
    for i in range(3):
        # Cortar cada tercio
        part = img.crop((i*part_w, 0, (i+1)*part_w, h))
        
        # Recortar espacios vacios DENTRO del tercio (ajuste fino)
        part_bbox = part.getbbox()
        if part_bbox:
            part = part.crop(part_bbox)
            
        # Guardar limpio
        filename = f"dino_{i}.png"
        part.save(filename)
        frames.append(filename)
        print(f"Generado: {filename}")

if __name__ == "__main__":
    clean_and_split()
