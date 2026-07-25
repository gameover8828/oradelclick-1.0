import streamlit as st
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os
import math
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Ofertas Pro",
    page_icon="🛒",
    layout="wide",
)

# --- INICIALIZAR ESTADO DE SESIÓN ---
keys_texto = ["prod_name", "prod_price", "prod_link", "prod_orig_price", "desc_txt"]
for key in keys_texto:
    if key not in st.session_state:
        st.session_state[key] = ""

if "prod_cat" not in st.session_state:
    st.session_state.prod_cat = "General / Cualquiera"
if "reset_uploader" not in st.session_state:
    st.session_state.reset_uploader = 0

def limpiar_datos():
    for k in keys_texto:
        st.session_state[k] = ""
    st.session_state.prod_cat = "General / Cualquiera"
    st.session_state.reset_uploader += 1 

# --- FUNCIONES DE UTILIDAD ---
@st.cache_resource  
def cargar_fuentes():
    try:
        font_principal = ImageFont.truetype("arialbd.ttf", 90) # Tamaño controlado para el listón
        font_general = ImageFont.truetype("arial.ttf", 50)   
        font_precios = ImageFont.truetype("arialbd.ttf", 100) 
        font_tachado = ImageFont.truetype("arialbd.ttf", 50)
        font_titulo = ImageFont.truetype("arialbd.ttf", 75)
        return font_principal, font_general, font_precios, font_tachado, font_titulo
    except:
        font_defecto = ImageFont.load_default()
        return font_defecto, font_defecto, font_defecto, font_defecto, font_defecto

def draw_scalloped_badge(draw, cx, cy, r_outer, r_inner, points, fill, outline, width):
    poly = []
    for i in range(points * 2):
        angle = i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        poly.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(poly, fill=fill)
    poly.append(poly[0])
    if width > 0:
        draw.line(poly, fill=outline, width=width, joint="curve")

def crear_liston_inclinado(ancho, alto, texto, fuente):
    """Crea un listón con proporciones exactas y limpias"""
    img_liston = Image.new("RGBA", (ancho, alto), (0,0,0,0))
    d = ImageDraw.Draw(img_liston)
    
    x, y, w, h = 20, 20, ancho - 40, alto - 40
    zigzags = 6
    
    # Capa Sombra (Amarillo)
    puntos_sombra = [(x-5, y+10), (x+w+5, y-10)]
    y_step = h / zigzags
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-8, 8) if i < zigzags else 0
        puntos_sombra.append((x+w+5 + x_offset, y-10 + (i * y_step)))
    puntos_sombra.append((x-5, y+h+10))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-8, 8)
        puntos_sombra.append((x-5 + x_offset, y+10 + (i * y_step)))
    d.polygon(puntos_sombra, fill=(255, 200, 0, 255)) 

    # Capa Principal (Rojo)
    puntos = [(x, y), (x+w, y-25)]
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-8, 8) if i < zigzags else 0
        puntos.append((x+w + x_offset, y-25 + (i * y_step)))
    puntos.append((x, y+h))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-8, 8)
        puntos.append((x + x_offset, y + (i * y_step)))
    d.polygon(puntos, fill=(255, 50, 0, 255)) 
    
    texto_mostrar = texto if texto else "¡OFERTA!"
    d.text((ancho//2, alto//2 - 5), texto_mostrar, fill=(255, 235, 0), font=fuente, anchor="mm", stroke_width=3, stroke_fill=(180, 0, 0))
    return img_liston

def create_sale_tag():
    tag = Image.new("RGBA", (160, 70), (0,0,0,0))
    d = ImageDraw.Draw(tag)
    d.polygon([(30, 10), (150, 10), (150, 60), (30, 60), (10, 35)], fill=(255, 85, 50, 255))
    d.ellipse([(15, 30), (23, 40)], fill=(255, 255, 255, 255))
    try:
        f = ImageFont.truetype("arialbd.ttf", 35)
    except:
        f = ImageFont.load_default()
    d.text((90, 35), "sale", fill=(255, 255, 255, 255), font=f, anchor="mm")
    return tag

# --- INTERFAZ PRINCIPAL ---
st.title("🛒 Generador de Ofertas Pro")

st.header("1. Datos Generales del Producto")
col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
with col1:
    producto = st.text_input("Nombre del Producto", placeholder="Ej. Smart TV 55", key="prod_name")
with col2:
    precio = st.text_input("Precio de Oferta", placeholder="Ej. 1125", key="prod_price")
with col3:
    lista_categorias = ["General / Cualquiera", "Tecnología y Electrónica", "Hogar y Muebles", "Moda"]
    categoria = st.selectbox("Categoría:", lista_categorias, key="prod_cat")
with col4:
    st.write("") 
    st.button("🧹 Limpiar Todo", on_click=limpiar_datos, type="primary", use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(["💬 Mensaje para WhatsApp", "🖼️ Generador de Banner"])

with tab1:
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        link_ml = st.text_input("Link", placeholder="https://...", key="prod_link")
    with col_w2:
        estilo = st.selectbox("Estilo del mensaje:", ["Llamativo", "Corto y directo", "Urgencia"])

    if producto and precio and link_ml:
        mensaje_default = f"🔥 ¡OFERTA RELÁMPAGO! 🔥\n\n¡No dejes pasar esta oportunidad! El {producto} que buscabas.\n\n💰 Llevátelo por solo $ {precio} MXN. 😱\n\n👉 Cómpralo de forma segura aquí: \n{link_ml}"
        mensaje_final = st.text_area("Edita tu texto:", value=mensaje_default, height=200)
        st.link_button("Enviar por WhatsApp", f"https://wa.me/?text={urllib.parse.quote(mensaje_final)}", type="primary")
    else:
        st.info("Introduce Nombre, Precio y Link para generar el texto.")

with tab2:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡25% OFF!", key="desc_txt")
        precio_original_txt = st.text_input("Precio Original Tachado", placeholder="Ej. 1500", key="prod_orig_price")
    with col_b2:
        imagen_subida = st.file_uploader("Sube la foto de tu producto", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_uploader}")

    if imagen_subida and precio and precio_original_txt:
        st.subheader("🖼️ Banner Generado")

        ancho, alto = 1080, 1920 
        
        # 1. FONDO BLANCO LIMPIO
        banner_base = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
        draw = ImageDraw.Draw(banner_base)
        
        # 2. Confeti controlado
        colores_confeti = [(255, 70, 70), (255, 215, 0), (70, 150, 255)]
        for _ in range(100):
            x = random.randint(50, ancho-50)
            y = random.randint(50, alto-50)
            tam = random.randint(12, 22)
            color = random.choice(colores_confeti)
            angle = random.uniform(0, math.pi)
            p1 = (x, y)
            p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
            p3 = (x + tam * math.cos(angle) - (tam/2) * math.sin(angle), y + tam * math.sin(angle) + (tam/2) * math.cos(angle))
            p4 = (x - (tam/2) * math.sin(angle), y + (tam/2) * math.cos(angle))
            draw.polygon([p1, p2, p3, p4], fill=color)

        fuente_script, fuente_sec, fuente_precios, fuente_tachado, font_titulo = cargar_fuentes()
        
        # 3. Título Superior
        texto_oferta = "OFERTA RELÁMPAGO"
        draw.text((ancho//2 + 3, 103), texto_oferta, fill=(210, 210, 210, 255), font=font_titulo, anchor="mm")
        draw.text((ancho//2, 100), texto_oferta, fill=(50, 50, 50), font=font_titulo, anchor="mm", stroke_width=2, stroke_fill=(200, 200, 200))

        # 4. Imagen del producto (Centrada y bien proporcionada)
        img_prod = Image.open(imagen_subida).convert("RGBA")
        w_orig, h_orig = img_prod.size
        nuevo_alto = 700
        nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
        if nuevo_ancho > ancho * 0.75:
            nuevo_ancho = int(ancho * 0.75)
            nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
            
        img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        pos_prod_x = (ancho - nuevo_ancho) // 2
        pos_prod_y = 350 
        
        # Sombra suave para el producto
        sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
        sombra_draw = ImageDraw.Draw(sombra_prod)
        sombra_draw.ellipse([(40, nuevo_alto-50), (nuevo_ancho-40, nuevo_alto+15)], fill=(0,0,0,70))
        sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(15))
        banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
        banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

        # 5. Sello "MÁS VENDIDO"
        pos_sello_x, pos_sello_y = 780, 260
        draw_scalloped_badge(draw, pos_sello_x+6, pos_sello_y+6, 140, 125, 16, (230, 230, 230, 255), (0,0,0,0), 0) 
        draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 140, 125, 16, (148, 230, 255, 255), (255, 255, 255, 255), 8)
        draw.ellipse([(pos_sello_x - 100, pos_sello_y - 100), (pos_sello_x + 100, pos_sello_y + 100)], outline=(255, 255, 255, 255), width=4)
        
        try:
            font_s = ImageFont.truetype("arialbd.ttf", 45)
            font_sp = ImageFont.truetype("arialbd.ttf", 30)
        except:
            font_s, font_sp = fuente_sec, fuente_sec
            
        draw.text((pos_sello_x, pos_sello_y - 20), "MÁS", fill=(72, 155, 230), font=font_s, anchor="mm")
        draw.text((pos_sello_x, pos_sello_y + 25), "VENDIDO", fill=(72, 155, 230), font=font_sp, anchor="mm")

        # 6. Etiqueta 'sale'
        tag_img = create_sale_tag()
        banner_base.paste(tag_img.rotate(25, expand=True), (220, 220), tag_img.rotate(25, expand=True))

        # 7. Listón Inclinado (Tamaño y ángulo correctos)
        liston = crear_liston_inclinado(800, 200, porcentaje_desc_txt, fuente_script)
        liston_rotado = liston.rotate(6, expand=True) 
        pos_liston_x = (ancho - liston_rotado.width) // 2
        pos_liston_y = 1050
        banner_base.paste(liston_rotado, (pos_liston_x, pos_liston_y), liston_rotado)

        # 8. PRECIOS (Ubicados ordenadamente abajo)
        precio_orig_y = 1380
        precio_final_y = 1520
        
        # Precio Tachado
        texto_original_str = f"${precio_original_txt}"
        w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
        draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(120, 120, 120), font=fuente_tachado, anchor="mm")
        draw.line([(ancho//2 - w_tachado//2 - 10, precio_orig_y), (ancho//2 + w_tachado//2 + 10, precio_orig_y)], fill=(255, 0, 0), width=6)
        
        # Precio Oferta (Verde brillante)
        texto_oferta_str = f"${precio} MXN"
        draw.text((ancho//2 + 3, precio_final_y + 3), texto_oferta_str, fill=(0, 80, 0, 120), font=fuente_precios, anchor="mm")
        draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 230, 0), font=fuente_precios, anchor="mm", stroke_width=2, stroke_fill=(30, 130, 30))

        buffered = BytesIO()
        banner_base.save(buffered, format="PNG")
        
        st.image(buffered.getvalue(), caption="Diseño Correcto Generado", use_container_width=True)
        st.download_button(label="📥 Descargar Imagen Completa", data=buffered.getvalue(), file_name=f"banner_pro_{producto.replace(' ', '_')}.png", mime="image/png")

    else:
        st.info("👆 Sube la imagen y define los precios para generar el diseño.")

    else:
        st.info("👆 Sube la imagen y define los precios para generar el diseño.")
