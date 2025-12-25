from PIL import Image
import os

def fix_fake_transparency():
    files = ["dino1.png", "dino2.png", "dino3.png"]
    
    for f in files:
        if not os.path.exists(f):
            print(f"Saltando {f} (no existe)")
            continue
            
        print(f"Arreglando {f}...")
        img = Image.open(f).convert("RGBA")
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            r, g, b, a = item
            
            # CRITERIO DE SATURACIÓN
            # Los colores grises/blancos tienen R, G y B muy parecidos.
            # Los colores vivos (verde, amarillo) tienen mucha diferencia.
            
            saturation = max(r, g, b) - min(r, g, b)
            
            # Si el pixel tiene poca 'vida' (es grisáceo o blanco), borrarlo.
            # Umbral de 20 suele ser seguro para pixel art colorido.
            if saturation < 20: 
                new_data.append((0, 0, 0, 0)) # Transparente Total
            else:
                new_data.append(item) # Mantener pixel
        
        img.putdata(new_data)
        img.save(f) # Sobreescribir
        print(f" -> {f} arreglado.")

if __name__ == "__main__":
    fix_fake_transparency()
    print("¡Listo! Ejecuta start_pet.bat de nuevo.")
