import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os
import math
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Ora del Click - Generador de Ofertas Pro",
    page_icon="🛒",
    layout="wide",
)

# --- FUNCIONES DE UTILIDAD ---
@st.cache_resource  
def cargar_fuentes():
    try:
        font_path = "fuente_oferta.ttf"
        font_principal = ImageFont.truetype(font_path, 180) if os.path.exists(font_path) else ImageFont.truetype("arialbd.ttf", 150)
        font_general = ImageFont.truetype("arial.ttf", 50)   
        font_precios = ImageFont.truetype("arialbd.ttf", 100)
        font_precios_tachado = ImageFont.truetype("arialbd.ttf", 60)
        font_titulo = ImageFont.truetype("arialbd.ttf", 85)
        return font_principal, font_general, font_precios, font_precios_tachado, font_titulo
    except:
        st.warning("⚠️ Fuentes no encontradas. Usando fuentes por defecto. Te recomendamos tener arial.ttf y arialbd.ttf en tu sistema.")
        font_defecto = ImageFont.load_default()
        return font_defecto, font_defecto, font_defecto, font_defecto, font_defecto

def draw_scalloped_badge(draw, cx, cy, r_outer, r_inner, points, fill, outline, width):
    """Dibuja un sello con bordes ondulados (scalloped)"""
    poly = []
    for i in range(points * 2):
        angle = i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        poly.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    
    # Truco para borde grueso en polígonos: dibujar varias veces o usar una línea sobre el borde
    draw.polygon(poly, fill=fill)
    poly.append(poly[0]) # Cerrar el trazo
    draw.line(poly, fill=outline, width=width, joint="curve")

def draw_torn_ribbon(draw, x, y, width, height, fill, outline_color, outline_width=0, zigzags=6, tilt=0):
    """Dibuja un listón con bordes rasgados"""
    # Puntos base
    points = []
    
    # Borde superior
    points.append((x, y))
    points.append((x + width, y - 50)) # Inclinación ligera
    
    # Borde derecho rasgado (zig-zag)
    y_step = height / zigzags
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-15, 15) if i < zigzags else 0
        points.append((x + width + x_offset, y - 50 + (i * y_step)))
        
    # Borde inferior
    points.append((x, y + height))
    
    # Borde izquierdo rasgado (zig-zag)
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-15, 15)
        points.append((x + x_offset, y + (i * y_step)))

    if outline_width > 0:
        # Dibujar borde "sombra/resalte" desplazado o como contorno
        draw.polygon(points, fill=outline_color)
        
        # Reducir un poco el tamaño para el polígono interior
        inner_points = [(px, py + outline_width) if i in [0, 1] else (px, py - outline_width) for i, (px, py) in enumerate(points)]
        draw.polygon(points, fill=fill) # Simplificado para evitar cálculos complejos de contracción
    else:
        draw.polygon(points, fill=fill)

def create_sale_tag():
    """Crea una etiqueta de 'sale' como una imagen rotada"""
    tag = Image.new("RGBA", (200, 80), (0,0,0,0))
    d = ImageDraw.Draw(tag)
    # Fondo naranja de la etiqueta
    d.polygon([(40, 10), (190, 10), (190, 70), (40, 70), (10, 40)], fill=(255, 85, 50, 255))
    # Agujero de la etiqueta
    d.ellipse([(20, 35), (30, 45)], fill=(255, 255, 255, 255))
    # Texto
    try:
        f = ImageFont.truetype("arialbd.ttf", 40)
    except:
        f = ImageFont.load_default()
    d.text((115, 40), "sale", fill=(255, 255, 255, 255), font=f, anchor="mm")
    return tag

# --- SECCIÓN 1: DATOS DEL BANNER ---
st.title("🛒 Generador Profesional de Ofertas y Diseños")
st.write("Personaliza tu banner para redes sociales basado en el diseño profesional de ejemplo.")

col1, col2 = st.columns(2)

with col1:
    producto_nombre = st.text_input("Nombre del Producto", value="Kit La Roche-Posay")
    precio_oferta_txt = st.text_input("Precio de Oferta", value="1,125")
    porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡25% OFF!")

with col2:
    precio_original_txt = st.text_input("Precio Original Tachado", value="1,500")
    categoria = st.selectbox("Categoría:", ["Salud y Belleza", "Tecnología", "Moda"])
    imagen_subida = st.file_uploader(
        "Sube la foto de tu producto (PNG transparente recomendado)",
        type=["png", "jpg", "jpeg"],
    )

st.divider()

# --- SECCIÓN 2: RENDERIZADO VISUAL DEL BANNER ---
if imagen_subida and precio_oferta_txt and precio_original_txt:
    st.subheader("🖼️ Vista Previa del Banner Generado")

    ancho, alto = 1080, 1920 
    
    # 1. Fondo Base Degradado más suave
    banner_base = Image.new("RGBA", (ancho, alto), (128, 186, 230, 255))
    draw = ImageDraw.Draw(banner_base)
    
    # Brillo central (Radial)
    for i in range(255, 0, -5):
        radio = 800 + (255 - i) * 2
        color_borde = (190, 230, 255, int(i * 0.15))
        draw.ellipse([(ancho//2 - radio, alto//2 - radio - 200), (ancho//2 + radio, alto//2 + radio - 200)], fill=color_borde)
    
    # 2. Confeti Mejorado (Polígonos rotados en lugar de rectángulos fijos)
    colores_confeti = [(255, 70, 70), (255, 215, 0), (70, 150, 255), (255, 255, 255)]
    for _ in range(120):
        x = random.randint(0, ancho)
        y = random.randint(0, alto)
        tam = random.randint(10, 25)
        color = random.choice(colores_confeti)
        
        # Generar rectángulo rotado simulando confeti
        angle = random.uniform(0, math.pi)
        p1 = (x, y)
        p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
        p3 = (x + tam * math.cos(angle) - (tam/2) * math.sin(angle), y + tam * math.sin(angle) + (tam/2) * math.cos(angle))
        p4 = (x - (tam/2) * math.sin(angle), y + (tam/2) * math.cos(angle))
        draw.polygon([p1, p2, p3, p4], fill=color)

    # 3. Rayos Eléctricos y Texto Superior
    fuente_script, fuente_sec, fuente_precios, fuente_tachado, font_titulo = cargar_fuentes()
    
    # Sombras y Texto "OFERTA RELÁMPAGO"
    texto_oferta = " OFERTA RELÁMPAGO "
    draw.text((ancho//2 + 5, 155), texto_oferta, fill=(0, 0, 0, 80), font=font_titulo, anchor="mm") # Sombra
    draw.text((ancho//2, 150), texto_oferta, fill=(255, 255, 255), font=font_titulo, anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))

    # 4. Sello "MÁS VENDIDO" (Ondulado / Scalloped)
    pos_sello_x, pos_sello_y = 820, 480
    # Sombra
    draw_scalloped_badge(draw, pos_sello_x+10, pos_sello_y+10, 170, 150, 16, (0,0,0,50), (0,0,0,0), 0)
    # Fondo Sello
    draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 170, 150, 16, (148, 230, 255, 255), (255, 255, 255, 255), 12)
    # Círculo interior
    draw.ellipse([(pos_sello_x - 120, pos_sello_y - 120), (pos_sello_x + 120, pos_sello_y + 120)], outline=(255, 255, 255, 255), width=5)
    
    try:
        font_sello = ImageFont.truetype("arialbd.ttf", 60)
    except:
        font_sello = fuente_sec
    draw.text((pos_sello_x, pos_sello_y - 35), "MÁS", fill=(72, 155, 230), font=font_sello, anchor="mm")
    draw.text((pos_sello_x, pos_sello_y + 35), "VENDIDO", fill=(72, 155, 230), font=font_sello, anchor="mm")

    # 5. Etiquetas de 'Sale'
    tag_img = create_sale_tag()
    banner_base.paste(tag_img.rotate(25, expand=True), (250, 320), tag_img.rotate(25, expand=True))
    banner_base.paste(tag_img.rotate(-20, expand=True), (750, 1250), tag_img.rotate(-20, expand=True))

    # 6. Imagen del producto
    img_prod = Image.open(imagen_subida).convert("RGBA")
    w_orig, h_orig = img_prod.size
    nuevo_alto = 750
    nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
    if nuevo_ancho > ancho * 0.85:
        nuevo_ancho = int(ancho * 0.85)
        nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
        
    img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    pos_prod_x = (ancho - nuevo_ancho) // 2
    pos_prod_y = 600 
    
    # Sombra del producto
    sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
    sombra_draw = ImageDraw.Draw(sombra_prod)
    sombra_draw.ellipse([(50, nuevo_alto-80), (nuevo_ancho-50, nuevo_alto+20)], fill=(0,0,0,100))
    sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(15))
    banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
    
    # Pegar Producto
    banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

    # 7. Listón de Descuento (Estilo Papel Rasgado)
    cinta_x, cinta_y_base, cinta_w, cinta_h = 100, 1380, 880, 250
    
    # Fondo Amarillo del listón
    draw_torn_ribbon(draw, cinta_x - 10, cinta_y_base + 10, cinta_w + 40, cinta_h, fill=(255, 215, 0, 255), outline_color=(0,0,0,0))
    # Frente Rojo del listón
    draw_torn_ribbon(draw, cinta_x, cinta_y_base, cinta_w, cinta_h, fill=(255, 60, 0, 255), outline_color=(0,0,0,0))

    # Texto del Descuento
    # Sombra del texto
    draw.text((ancho//2 + 8, cinta_y_base + 118), porcentaje_desc_txt, fill=(180, 0, 0), font=fuente_script, anchor="mm")
    # Texto principal
    draw.text((ancho//2, cinta_y_base + 110), porcentaje_desc_txt, fill=(255, 235, 0), font=fuente_script, anchor="mm")

    # 8. Precios
    precio_orig_y = 1720
    precio_final_y = 1820
    
    # Precio Tachado
    texto_original_str = f"${precio_original_txt}"
    w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
    draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(255, 255, 255), font=fuente_tachado, anchor="mm")
    draw.line([(ancho//2 - w_tachado//2 - 10, precio_orig_y), (ancho//2 + w_tachado//2 + 10, precio_orig_y)], fill=(220, 20, 20), width=8)
    
    # Precio Oferta (Con sombra oscura)
    texto_oferta_str = f"${precio_oferta_txt} MXN"
    # Sombra
    draw.text((ancho//2 + 5, precio_final_y + 5), texto_oferta_str, fill=(0, 50, 0, 150), font=fuente_precios, anchor="mm")
    # Texto
    draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 255, 0), font=fuente_precios, anchor="mm", stroke_width=2, stroke_fill=(20, 100, 0))

    # Guardar y mostrar
    buffered = BytesIO()
    banner_base.save(buffered, format="PNG")
    
    st.image(buffered.getvalue(), caption="Diseño Profesional Generado", use_container_width=True)

    st.download_button(
        label="📥 Descargar Imagen Publicitaria Completa",
        data=buffered.getvalue(),
        file_name=f"banner_pro_{producto_nombre.replace(' ', '_')}.png",
        mime="image/png",
    )

else:
    st.info("👆 Sube la imagen de tu producto y define los precios para generar el diseño.")
