import streamlit as st
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os
import math
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Se unifican las configuraciones, manteniendo el layout "wide" para dar espacio al banner
st.set_page_config(
    page_title="Generador de Ofertas Pro",
    page_icon="🛒",
    layout="wide",
)

# --- FUNCIONES DE UTILIDAD (Banner) ---
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
    
    draw.polygon(poly, fill=fill)
    poly.append(poly[0]) 
    draw.line(poly, fill=outline, width=width, joint="curve")

def draw_torn_ribbon(draw, x, y, width, height, fill, outline_color, outline_width=0, zigzags=6, tilt=0):
    """Dibuja un listón con bordes rasgados"""
    points = []
    points.append((x, y))
    points.append((x + width, y - 50)) 
    
    y_step = height / zigzags
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-15, 15) if i < zigzags else 0
        points.append((x + width + x_offset, y - 50 + (i * y_step)))
        
    points.append((x, y + height))
    
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-15, 15)
        points.append((x + x_offset, y + (i * y_step)))

    if outline_width > 0:
        draw.polygon(points, fill=outline_color)
        inner_points = [(px, py + outline_width) if i in [0, 1] else (px, py - outline_width) for i, (px, py) in enumerate(points)]
        draw.polygon(points, fill=fill) 
    else:
        draw.polygon(points, fill=fill)

def create_sale_tag():
    """Crea una etiqueta de 'sale' como una imagen rotada"""
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
st.title("🛒 Herramientas de Ofertas Pro")
st.write("Genera textos persuasivos y banners llamativos para tus productos.")

# Creación de pestañas para dividir las dos herramientas
tab1, tab2 = st.tabs(["💬 Texto para WhatsApp", "🖼️ Generador de Banner"])

# ==========================================
# PESTAÑA 1: TEXTO PARA WHATSAPP
# ==========================================
with tab1:
    st.header("1. Ingresa los datos del producto")

    col1_txt, col2_txt = st.columns(2)
    with col1_txt:
        producto = st.text_input("Nombre del Producto", placeholder="Ej. Taladro Inalámbrico", key="prod_txt")
        precio = st.text_input("Precio de Oferta", placeholder="Ej. 1299", key="precio_txt")
    with col2_txt:
        link_ml = st.text_input("Link de MercadoLibre", placeholder="https://articulo.mercadolibre.com.mx/...")
        
        lista_categorias = [
            "General / Cualquiera", "Vehículos y Accesorios", "Supermercado y Alimentos", 
            "Tecnología y Electrónica", "Videojuegos y Consolas", "Electrodomésticos",
            "Hogar y Muebles", "Moda", "Joyería y Relojes", "Deportes y Fitness", 
            "Herramientas y Construcción", "Mascotas", "Bebés y Juguetes", 
            "Salud y Belleza", "Libros y Música", "Instrumentos Musicales", "Papelería y Arte"
        ]
        categoria_txt = st.selectbox("Categoría del producto:", lista_categorias)

    st.header("2. Personaliza tu mensaje")
    estilo = st.selectbox("Elige el estilo del mensaje:", ["Llamativo", "Corto y directo", "Urgencia"])

    if producto and precio and link_ml:
        if categoria_txt == "Vehículos y Accesorios":
            emoji_cat, frase_cat, frase_urgencia = "🚗🔧", f"¡Equipa tu vehículo con este excelente {producto}!", "¡No dejes pasar esta oportunidad para tu auto o moto!"
        elif categoria_txt == "Supermercado y Alimentos":
            emoji_cat, frase_cat, frase_urgencia = "🛒🍎", f"¡Aprovecha y llévate {producto} al mejor precio!", "¡Llena tu despensa antes de que se agote!"
        elif categoria_txt == "Tecnología y Electrónica":
            emoji_cat, frase_cat, frase_urgencia = "⚡📱", f"¡Llegó la hora de actualizarte! Llévate este {producto}.", "¡Pocas unidades disponibles de esta joya tecnológica!"
        elif categoria_txt == "Videojuegos y Consolas":
            emoji_cat, frase_cat, frase_urgencia = "🎮🕹️", f"¡Lleva tu entretenimiento al siguiente nivel con este {producto}!", "¡Sube de nivel antes de que se agoten las unidades!"
        elif categoria_txt == "Electrodomésticos":
            emoji_cat, frase_cat, frase_urgencia = "🧊🍳", f"¡Facilita tu día a día con este increíble {producto}!", "¡Equipa tu casa al mejor precio ahora mismo!"
        elif categoria_txt == "Hogar y Muebles":
            emoji_cat, frase_cat, frase_urgencia = "🏡🛋️", f"Dale un toque especial a tu casa con este {producto}.", "¡Mejora tu hogar hoy mismo antes de que se acaben!"
        elif categoria_txt == "Moda":
            emoji_cat, frase_cat, frase_urgencia = "👟👗", f"¡Renueva tu outfit con este increíble {producto}! Luce espectacular.", "¡Últimas tallas y modelos en inventario!"
        elif categoria_txt == "Joyería y Relojes":
            emoji_cat, frase_cat, frase_urgencia = "💍⌚", f"¡Luce increíble y a la moda con este hermoso {producto}!", "¡Un detalle perfecto que se está agotando muy rápido!"
        elif categoria_txt == "Deportes y Fitness":
            emoji_cat, frase_cat, frase_urgencia = "🏋️‍♂️⚽", f"¡Ponte en forma y da tu máximo con este {producto}!", "¡Equípate antes de que suba de precio!"
        elif categoria_txt == "Herramientas y Construcción":
            emoji_cat, frase_cat, frase_urgencia = "🛠️🏗️", f"¡Haz tus proyectos realidad con la mejor calidad! Increíble {producto}.", "¡Herramientas indispensables a un precio irrepetible!"
        elif categoria_txt == "Mascotas":
            emoji_cat, frase_cat, frase_urgencia = "🐶🐱", f"¡Consiente a tu mejor amigo peludo con este {producto}!", "¡Lo mejor para tu mascota a un clic, últimas piezas!"
        elif categoria_txt == "Bebés y Juguetes":
            emoji_cat, frase_cat, frase_urgencia = "👶🧸", f"¡Diversión y cuidado garantizado con este {producto}!", "¡Consíguelo antes de que vuele!"
        elif categoria_txt == "Salud y Belleza":
            emoji_cat, frase_cat, frase_urgencia = "✨💄", f"Consiéntete como te mereces. Este {producto} es justo lo que necesitas.", "¡Cuida de ti al mejor precio antes de que se agote!"
        elif categoria_txt == "Libros y Música":
            emoji_cat, frase_cat, frase_urgencia = "📚🎶", f"¡Sumérgete en una gran historia o melodía con {producto}!", "¡Añádelo a tu colección hoy mismo!"
        elif categoria_txt == "Instrumentos Musicales":
            emoji_cat, frase_cat, frase_urgencia = "🎸🎹", f"¡Saca el artista que llevas dentro con este {producto}!", "¡No dejes que la música pare, últimas piezas!"
        elif categoria_txt == "Papelería y Arte":
            emoji_cat, frase_cat, frase_urgencia = "✏️🎨", f"¡Despierta tu creatividad con este {producto}!", "¡Materiales increíbles a un precio que no volverá!"
        else: 
            emoji_cat, frase_cat, frase_urgencia = "🎁🛍️", f"¡Checa este productazo! El {producto} que estabas buscando.", "¡Corre porque vuelan las piezas!"

        if estilo == "Llamativo":
            mensaje_default = f"🔥 ¡GRAN OFERTA DE NO CREER! 🔥\n\n{emoji_cat} {frase_cat}\n\n💰 Precio especial: solo $ {precio}. 😱\n\n👉 Cómpralo de forma segura en MercadoLibre aquí: \n{link_ml} \n\n#Ofertas #MercadoLibre #Imperdible"
        elif estilo == "Corto y directo":
            mensaje_default = f"✅ {emoji_cat} {producto} disponible por solo ${precio}.\n\n🛒 Cómpralo aquí directo en MercadoLibre: {link_ml}"
        else: 
            mensaje_default = f"🚨 ¡ÚLTIMAS PIEZAS DISPONIBLES! 🚨\n\n{producto} súper rebajado a solo ${precio}. 😱\n\n⚠️ {frase_urgencia}\n\n🛒 Haz tu pedido AQUÍ antes de que se acabe: {link_ml}"
        
        mensaje_final = st.text_area("Edita el texto final si deseas agregar o quitar algo:", value=mensaje_default, height=200)
        
        mensaje_codificado = urllib.parse.quote(mensaje_final)
        url_whatsapp = f"https://wa.me/?text={mensaje_codificado}"
        
        st.link_button("Enviar por WhatsApp", url_whatsapp, type="primary")
    else:
        st.info("Por favor, introduce el nombre del producto, precio y link arriba para generar los textos personalizados.")


# ==========================================
# PESTAÑA 2: GENERADOR DE BANNER
# ==========================================
with tab2:
    st.write("Personaliza tu banner para redes sociales basado en el diseño profesional de ejemplo.")

    col1_img, col2_img = st.columns(2)

    with col1_img:
        producto_nombre = st.text_input("Nombre del Producto", value="Kit La Roche-Posay", key="prod_img")
        precio_oferta_img = st.text_input("Precio de Oferta", value="1,125", key="precio_oferta_img")
        porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡25% OFF!")

    with col2_img:
        precio_original_txt = st.text_input("Precio Original Tachado", value="1,500")
        categoria_img = st.selectbox("Categoría:", ["Salud y Belleza", "Tecnología", "Moda"], key="cat_img")
        imagen_subida = st.file_uploader("Sube la foto de tu producto (PNG transparente recomendado)", type=["png", "jpg", "jpeg"])

    st.divider()

    if imagen_subida and precio_oferta_img and precio_original_txt:
        st.subheader("🖼️ Vista Previa del Banner Generado")

        ancho, alto = 1080, 1920 
        
        banner_base = Image.new("RGBA", (ancho, alto), (128, 186, 230, 255))
        draw = ImageDraw.Draw(banner_base)
        
        for i in range(255, 0, -5):
            radio = 800 + (255 - i) * 2
            color_borde = (190, 230, 255, int(i * 0.15))
            draw.ellipse([(ancho//2 - radio, alto//2 - radio - 200), (ancho//2 + radio, alto//2 + radio - 200)], fill=color_borde)
        
        colores_confeti = [(255, 70, 70), (255, 215, 0), (70, 150, 255), (255, 255, 255)]
        for _ in range(120):
            x = random.randint(0, ancho)
            y = random.randint(0, alto)
            tam = random.randint(10, 25)
            color = random.choice(colores_confeti)
            
            angle = random.uniform(0, math.pi)
            p1 = (x, y)
            p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
            p3 = (x + tam * math.cos(angle) - (tam/2) * math.sin(angle), y + tam * math.sin(angle) + (tam/2) * math.cos(angle))
            p4 = (x - (tam/2) * math.sin(angle), y + (tam/2) * math.cos(angle))
            draw.polygon([p1, p2, p3, p4], fill=color)

        fuente_script, fuente_sec, fuente_precios, fuente_tachado, font_titulo = cargar_fuentes()
        
        texto_oferta = " OFERTA RELÁMPAGO "
        draw.text((ancho//2 + 5, 155), texto_oferta, fill=(0, 0, 0, 80), font=font_titulo, anchor="mm") 
        draw.text((ancho//2, 150), texto_oferta, fill=(255, 255, 255), font=font_titulo, anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))

        pos_sello_x, pos_sello_y = 820, 480
        draw_scalloped_badge(draw, pos_sello_x+10, pos_sello_y+10, 170, 150, 16, (0,0,0,50), (0,0,0,0), 0)
        draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 170, 150, 16, (148, 230, 255, 255), (255, 255, 255, 255), 12)
        draw.ellipse([(pos_sello_x - 120, pos_sello_y - 120), (pos_sello_x + 120, pos_sello_y + 120)], outline=(255, 255, 255, 255), width=5)
        
        try:
            font_sello = ImageFont.truetype("arialbd.ttf", 60)
        except:
            font_sello = fuente_sec
        draw.text((pos_sello_x, pos_sello_y - 35), "MÁS", fill=(72, 155, 230), font=font_sello, anchor="mm")
        draw.text((pos_sello_x, pos_sello_y + 35), "VENDIDO", fill=(72, 155, 230), font=font_sello, anchor="mm")

        tag_img = create_sale_tag()
        banner_base.paste(tag_img.rotate(25, expand=True), (250, 320), tag_img.rotate(25, expand=True))
        banner_base.paste(tag_img.rotate(-20, expand=True), (750, 1250), tag_img.rotate(-20, expand=True))

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
        
        sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
        sombra_draw = ImageDraw.Draw(sombra_prod)
        sombra_draw.ellipse([(50, nuevo_alto-80), (nuevo_ancho-50, nuevo_alto+20)], fill=(0,0,0,100))
        sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(15))
        banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
        
        banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

        cinta_x, cinta_y_base, cinta_w, cinta_h = 100, 1380, 880, 250
        
        draw_torn_ribbon(draw, cinta_x - 10, cinta_y_base + 10, cinta_w + 40, cinta_h, fill=(255, 215, 0, 255), outline_color=(0,0,0,0))
        draw_torn_ribbon(draw, cinta_x, cinta_y_base, cinta_w, cinta_h, fill=(255, 60, 0, 255), outline_color=(0,0,0,0))

        draw.text((ancho//2 + 8, cinta_y_base + 118), porcentaje_desc_txt, fill=(180, 0, 0), font=fuente_script, anchor="mm")
        draw.text((ancho//2, cinta_y_base + 110), porcentaje_desc_txt, fill=(255, 235, 0), font=fuente_script, anchor="mm")

        precio_orig_y = 1720
        precio_final_y = 1820
        
        texto_original_str = f"${precio_original_txt}"
        w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
        draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(255, 255, 255), font=fuente_tachado, anchor="mm")
        draw.line([(ancho//2 - w_tachado//2 - 10, precio_orig_y), (ancho//2 + w_tachado//2 + 10, precio_orig_y)], fill=(220, 20, 20), width=8)
        
        texto_oferta_str = f"${precio_oferta_img} MXN"
        draw.text((ancho//2 + 5, precio_final_y + 5), texto_oferta_str, fill=(0, 50, 0, 150), font=fuente_precios, anchor="mm")
        draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 255, 0), font=fuente_precios, anchor="mm", stroke_width=2, stroke_fill=(20, 100, 0))

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
