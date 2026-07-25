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
        font_principal = ImageFont.truetype("arialbd.ttf", 220) 
        font_general = ImageFont.truetype("arial.ttf", 50)   
        font_precios = ImageFont.truetype("arialbd.ttf", 160) 
        font_tachado = ImageFont.truetype("arialbd.ttf", 80)
        font_titulo = ImageFont.truetype("arialbd.ttf", 90)
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
    img_liston = Image.new("RGBA", (ancho + 200, alto + 100), (0,0,0,0))
    d = ImageDraw.Draw(img_liston)
    
    x, y, w, h = 50, 50, ancho, alto
    zigzags = 6
    
    # Capa Sombra (Amarillo Oscuro/Naranja)
    puntos_sombra = [(x-10, y+20), (x+w+10, y-30)]
    y_step = h / zigzags
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-15, 15) if i < zigzags else 0
        puntos_sombra.append((x+w+10 + x_offset, y-30 + (i * y_step)))
    puntos_sombra.append((x-10, y+h+20))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-15, 15)
        puntos_sombra.append((x-10 + x_offset, y+20 + (i * y_step)))
    d.polygon(puntos_sombra, fill=(255, 200, 0, 255)) 

    # Capa Principal (Rojo)
    puntos = [(x, y), (x+w, y-50)]
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-15, 15) if i < zigzags else 0
        puntos.append((x+w + x_offset, y-50 + (i * y_step)))
    puntos.append((x, y+h))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-15, 15)
        puntos.append((x + x_offset, y + (i * y_step)))
    d.polygon(puntos, fill=(255, 50, 0, 255)) 
    
    texto_mostrar = texto if texto else "¡OFERTA!"
    d.text((x + w//2, y + h//2 - 20), texto_mostrar, fill=(255, 235, 0), font=fuente, anchor="mm", stroke_width=4, stroke_fill=(180, 0, 0))
    return img_liston

def create_sale_tag():
    tag = Image.new("RGBA", (200, 80), (0,0,0,0))
    d = ImageDraw.Draw(tag)
    d.polygon([(40, 10), (190, 10), (190, 70), (40, 70), (10, 40)], fill=(255, 85, 50, 255))
    d.ellipse([(20, 35), (30, 45)], fill=(255, 255, 255, 255))
    try:
        f = ImageFont.truetype("arialbd.ttf", 40)
    except:
        f = ImageFont.load_default()
    d.text((115, 40), "sale", fill=(255, 255, 255, 255), font=f, anchor="mm")
    return tag

# --- INTERFAZ PRINCIPAL ---
st.title("🛒 Generador de Ofertas Pro (Fondo Blanco)")

st.header("1. Datos Generales del Producto")
col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
with col1:
    producto = st.text_input("Nombre del Producto", placeholder="Ej. Smart TV 55", key="prod_name")
with col2:
    precio = st.text_input("Precio de Oferta", placeholder="Ej. 10999", key="prod_price")
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
        precio_original_txt = st.text_input("Precio Original Tachado", placeholder="Ej. 15599", key="prod_orig_price")
    with col_b2:
        imagen_subida = st.file_uploader("Sube la foto de tu producto", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_uploader}")

    if imagen_subida and precio and precio_original_txt:
        st.subheader("🖼️ Banner Generado")

        ancho, alto = 1080, 1920 
        
        # 1. FONDO BLANCO PURO
        banner_base = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
        draw = ImageDraw.Draw(banner_base)
        
        # 2. Confeti
        colores_confeti = [(255, 70, 70), (255, 215, 0), (70, 150, 255)]
        for _ in range(150):
            x = random.randint(0, ancho)
            y = random.randint(0, alto)
            tam = random.randint(15, 30)
            color = random.choice(colores_confeti)
            angle = random.uniform(0, math.pi)
            p1 = (x, y)
            p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
            p3 = (x + tam * math.cos(angle) - (tam/2) * math.sin(angle), y + tam * math.sin(angle) + (tam/2) * math.cos(angle))
            p4 = (x - (tam/2) * math.sin(angle), y + (tam/2) * math.cos(angle))
            draw.polygon([p1, p2, p3, p4], fill=color)

        fuente_script, fuente_sec, fuente_precios, fuente_tachado, font_titulo = cargar_fuentes()
        
        # 3. Texto Superior (Blanco con borde Gris)
        texto_oferta = "⚡ OFERTA RELÁMPAGO ⚡"
        draw.text((ancho//2 + 5, 155), texto_oferta, fill=(220, 220, 220, 255), font=font_titulo, anchor="mm") # Sombra leve
        draw.text((ancho//2, 150), texto_oferta, fill=(255, 255, 255), font=font_titulo, anchor="mm", stroke_width=3, stroke_fill=(200, 200, 200))

        # 4. Imagen del producto 
        img_prod = Image.open(imagen_subida).convert("RGBA")
        w_orig, h_orig = img_prod.size
        nuevo_alto = 800
        nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
        if nuevo_ancho > ancho * 0.90:
            nuevo_ancho = int(ancho * 0.90)
            nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
            
        img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        pos_prod_x = (ancho - nuevo_ancho) // 2
        pos_prod_y = 450 
        
        # Sombra del producto
        sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
        sombra_draw = ImageDraw.Draw(sombra_prod)
        sombra_draw.ellipse([(50, nuevo_alto-100), (nuevo_ancho-50, nuevo_alto+30)], fill=(0,0,0,100))
        sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(25))
        banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
        banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

        # 5. Sello "MÁS VENDIDO" (Azul claro sobre blanco)
        pos_sello_x, pos_sello_y = 800, 300
        # Sombra offset gris
        draw_scalloped_badge(draw, pos_sello_x+10, pos_sello_y+10, 170, 150, 16, (220, 220, 220, 255), (0,0,0,0), 0) 
        # Fondo Azul Claro
        draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 170, 150, 16, (148, 230, 255, 255), (255, 255, 255, 255), 10)
        draw.ellipse([(pos_sello_x - 125, pos_sello_y - 125), (pos_sello_x + 125, pos_sello_y + 125)], outline=(255, 255, 255, 255), width=6)
        
        try:
            font_sello = ImageFont.truetype("arialbd.ttf", 60)
            font_sello_peq = ImageFont.truetype("arialbd.ttf", 40)
        except:
            font_sello = fuente_sec
            font_sello_peq = fuente_sec
            
        draw.text((pos_sello_x, pos_sello_y - 25), "MÁS", fill=(72, 155, 230), font=font_sello, anchor="mm")
        draw.text((pos_sello_x, pos_sello_y + 35), "VENDIDO", fill=(72, 155, 230), font=font_sello_peq, anchor="mm")

        # 6. Etiquetas 'sale'
        tag_img = create_sale_tag()
        banner_base.paste(tag_img.rotate(35, expand=True), (250, 250), tag_img.rotate(35, expand=True))

        # 7. Listón Inclinado
        liston = crear_liston_inclinado(950, 320, porcentaje_desc_txt, fuente_script)
        liston_rotado = liston.rotate(8, expand=True) 
        pos_liston_x = (ancho - liston_rotado.width) // 2
        pos_liston_y = 1100
        banner_base.paste(liston_rotado, (pos_liston_x, pos_liston_y), liston_rotado)

        # 8. PRECIOS 
        precio_orig_y = 1550
        precio_final_y = 1750
        
        # Precio Tachado (Texto GRIS para que se vea en fondo blanco)
        texto_original_str = f"${precio_original_txt}"
        w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
        draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(150, 150, 150), font=fuente_tachado, anchor="mm") # GRIS CLARO
        draw.line([(ancho//2 - w_tachado//2 - 15, precio_orig_y), (ancho//2 + w_tachado//2 + 15, precio_orig_y)], fill=(255, 0, 0), width=10) # LINEA ROJA
        
        # Precio Oferta (Verde Neón)
        texto_oferta_str = f"${precio} MXN"
        draw.text((ancho//2 + 5, precio_final_y + 5), texto_oferta_str, fill=(0, 100, 0, 150), font=fuente_precios, anchor="mm")
        draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(128, 255, 0), font=fuente_precios, anchor="mm", stroke_width=4, stroke_fill=(30, 150, 30))

        buffered = BytesIO()
        banner_base.save(buffered, format="PNG")
        
        st.image(buffered.getvalue(), caption="Diseño Fondo Blanco Generado", use_container_width=True)
        st.download_button(label="📥 Descargar Imagen Completa", data=buffered.getvalue(), file_name=f"banner_blanco_{producto.replace(' ', '_')}.png", mime="image/png")

    else:
        st.info("👆 Sube la imagen y define los precios para generar el diseño.")
