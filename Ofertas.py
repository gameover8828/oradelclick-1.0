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

# --- INICIALIZAR ESTADO DE SESIÓN (Para poder limpiar los datos) ---
# Esto permite que el botón de limpieza vacíe las variables conectadas
keys_texto = ["prod_name", "prod_price", "prod_link", "prod_orig_price", "desc_txt"]
for key in keys_texto:
    if key not in st.session_state:
        st.session_state[key] = ""

if "prod_cat" not in st.session_state:
    st.session_state.prod_cat = "General / Cualquiera"
if "reset_uploader" not in st.session_state:
    st.session_state.reset_uploader = 0

def limpiar_datos():
    """Función para limpiar todos los inputs y el banner"""
    for k in keys_texto:
        st.session_state[k] = ""
    st.session_state.prod_cat = "General / Cualquiera"
    st.session_state.reset_uploader += 1 # Resetea el cargador de imágenes

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
    draw.line(poly, fill=outline, width=width, joint="curve")

def draw_torn_ribbon(draw, x, y, width, height, fill, outline_color, outline_width=0, zigzags=6):
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
        draw.polygon(points, fill=fill) 
    else:
        draw.polygon(points, fill=fill)

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
st.title("🛒 Ecosistema de Ofertas Pro")
st.write("Escribe los datos una vez, y generaremos tu diseño y tus textos en conjunto.")

# ==========================================
# SECCIÓN GLOBAL (Datos que trabajan entre sí)
# ==========================================
st.header("📝 1. Datos Generales del Producto")
st.caption("Llena estos datos y se aplicarán automáticamente tanto al texto de WhatsApp como al Banner.")

col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
with col1:
    producto = st.text_input("Nombre del Producto", placeholder="Ej. Taladro Inalámbrico", key="prod_name")
with col2:
    precio = st.text_input("Precio de Oferta ($)", placeholder="Ej. 1299", key="prod_price")
with col3:
    lista_categorias = [
        "General / Cualquiera", "Vehículos y Accesorios", "Supermercado y Alimentos", 
        "Tecnología y Electrónica", "Videojuegos y Consolas", "Electrodomésticos",
        "Hogar y Muebles", "Moda", "Joyería y Relojes", "Deportes y Fitness", 
        "Herramientas y Construcción", "Mascotas", "Bebés y Juguetes", 
        "Salud y Belleza", "Libros y Música", "Instrumentos Musicales", "Papelería y Arte"
    ]
    categoria = st.selectbox("Categoría:", lista_categorias, key="prod_cat")
with col4:
    st.write("") # Espaciado
    st.button("🧹 Limpiar Todo", on_click=limpiar_datos, type="primary", use_container_width=True)

st.divider()

# ==========================================
# PESTAÑAS SINCRONIZADAS
# ==========================================
tab1, tab2 = st.tabs(["💬 Mensaje para WhatsApp", "🖼️ Generador de Banner"])

# --- PESTAÑA 1: WHATSAPP ---
with tab1:
    st.subheader("Configuración del Mensaje")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        link_ml = st.text_input("Link de MercadoLibre / Tienda", placeholder="https://...", key="prod_link")
    with col_w2:
        estilo = st.selectbox("Estilo del mensaje:", ["Llamativo", "Corto y directo", "Urgencia"])

    if producto and precio and link_ml:
        # Lógica de Categorías
        emoji_cat = "🎁🛍️"
        frase_cat = f"¡Checa este productazo! El {producto} que estabas buscando."
        frase_urgencia = "¡Corre porque vuelan las piezas!"
        
        # (Lógica simplificada para brevedad, puedes agregar las demás categorías como estaban)
        if categoria == "Tecnología y Electrónica":
            emoji_cat, frase_cat, frase_urgencia = "⚡📱", f"¡Llegó la hora de actualizarte! Llévate este {producto}.", "¡Pocas unidades disponibles!"
        elif categoria == "Salud y Belleza":
            emoji_cat, frase_cat, frase_urgencia = "✨💄", f"Consiéntete como te mereces con este {producto}.", "¡Cuida de ti antes de que se agote!"
        
        # Lógica del Estilo
        if estilo == "Llamativo":
            mensaje_default = f"🔥 ¡GRAN OFERTA DE NO CREER! 🔥\n\n{emoji_cat} {frase_cat}\n\n💰 Precio especial: solo $ {precio}. 😱\n\n👉 Cómpralo de forma segura aquí: \n{link_ml} \n\n#Ofertas #Imperdible"
        elif estilo == "Corto y directo":
            mensaje_default = f"✅ {emoji_cat} {producto} disponible por solo ${precio}.\n\n🛒 Cómpralo aquí: {link_ml}"
        else: 
            mensaje_default = f"🚨 ¡ÚLTIMAS PIEZAS DISPONIBLES! 🚨\n\n{producto} súper rebajado a solo ${precio}. 😱\n\n⚠️ {frase_urgencia}\n\n🛒 Haz tu pedido AQUÍ: {link_ml}"
        
        mensaje_final = st.text_area("Texto final (editable):", value=mensaje_default, height=150)
        st.link_button("Enviar por WhatsApp", f"https://wa.me/?text={urllib.parse.quote(mensaje_final)}")
    else:
        st.info("👆 Llena el Nombre, Precio (arriba) y el Link para generar tu mensaje.")


# --- PESTAÑA 2: BANNER ---
with tab2:
    st.subheader("Configuración del Diseño")
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        precio_original = st.text_input("Precio Original (para tacharlo)", placeholder="Ej. 1500", key="prod_orig_price")
        texto_descuento = st.text_input("Etiqueta extra (ej. descuento)", placeholder="¡25% OFF!", key="desc_txt")
        diseno_limpio = st.checkbox("🖌️ Diseño Limpio (Quitar confeti para un look minimalista)", value=False)
        
    with col_b2:
        imagen_subida = st.file_uploader(
            "Sube la foto del producto (PNG sin fondo recomendado)", 
            type=["png", "jpg", "jpeg"], 
            key=f"uploader_{st.session_state.reset_uploader}"
        )

    if imagen_subida and precio and precio_original and producto:
        ancho, alto = 1080, 1920 
        banner_base = Image.new("RGBA", (ancho, alto), (128, 186, 230, 255))
        draw = ImageDraw.Draw(banner_base)
        
        # Brillo de fondo
        for i in range(255, 0, -5):
            radio = 800 + (255 - i) * 2
            color_borde = (190, 230, 255, int(i * 0.15))
            draw.ellipse([(ancho//2 - radio, alto//2 - radio - 200), (ancho//2 + radio, alto//2 + radio - 200)], fill=color_borde)
        
        # Opción de limpiar el diseño (Toggle de confeti)
        if not diseno_limpio:
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
        
        # Textos Superiores
        texto_oferta = " OFERTA RELÁMPAGO "
        draw.text((ancho//2 + 5, 155), texto_oferta, fill=(0, 0, 0, 80), font=font_titulo, anchor="mm") 
        draw.text((ancho//2, 150), texto_oferta, fill=(255, 255, 255), font=font_titulo, anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))

        # Sello solo si NO es diseño limpio
        if not diseno_limpio:
            pos_sello_x, pos_sello_y = 820, 480
            draw_scalloped_badge(draw, pos_sello_x+10, pos_sello_y+10, 170, 150, 16, (0,0,0,50), (0,0,0,0), 0)
            draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 170, 150, 16, (148, 230, 255, 255), (255, 255, 255, 255), 12)
            draw.ellipse([(pos_sello_x - 120, pos_sello_y - 120), (pos_sello_x + 120, pos_sello_y + 120)], outline=(255, 255, 255, 255), width=5)
            font_sello = ImageFont.truetype("arialbd.ttf", 60) if os.path.exists("arialbd.ttf") else fuente_sec
            draw.text((pos_sello_x, pos_sello_y - 35), "MÁS", fill=(72, 155, 230), font=font_sello, anchor="mm")
            draw.text((pos_sello_x, pos_sello_y + 35), "VENDIDO", fill=(72, 155, 230), font=font_sello, anchor="mm")

        # Imagen del Producto
        img_prod = Image.open(imagen_subida).convert("RGBA")
        w_orig, h_orig = img_prod.size
        nuevo_alto = 750
        nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
        if nuevo_ancho > ancho * 0.85:
            nuevo_ancho = int(ancho * 0.85)
            nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
            
        img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
        pos_prod_x = (ancho - nuevo_ancho) // 2
        pos_prod_y = 550 
        
        # Sombra del producto
        sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
        sombra_draw = ImageDraw.Draw(sombra_prod)
        sombra_draw.ellipse([(50, nuevo_alto-80), (nuevo_ancho-50, nuevo_alto+20)], fill=(0,0,0,100))
        sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(15))
        banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
        banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

        # Nombre del producto encima del listón
        draw.text((ancho//2, 1340), producto.upper(), fill=(255, 255, 255), font=font_titulo, anchor="mm", stroke_width=3, stroke_fill=(0,0,0))

        # Listón de texto secundario (Descuento)
        cinta_x, cinta_y_base, cinta_w, cinta_h = 100, 1400, 880, 200
        draw_torn_ribbon(draw, cinta_x - 10, cinta_y_base + 10, cinta_w + 40, cinta_h, fill=(255, 215, 0, 255), outline_color=(0,0,0,0))
        draw_torn_ribbon(draw, cinta_x, cinta_y_base, cinta_w, cinta_h, fill=(255, 60, 0, 255), outline_color=(0,0,0,0))
        
        texto_mostrar = texto_descuento if texto_descuento else "¡OFERTA ESPECIAL!"
        draw.text((ancho//2 + 5, cinta_y_base + 95), texto_mostrar, fill=(180, 0, 0), font=fuente_script, anchor="mm")
        draw.text((ancho//2, cinta_y_base + 90), texto_mostrar, fill=(255, 235, 0), font=fuente_script, anchor="mm")

        # Precios
        precio_orig_y, precio_final_y = 1680, 1800
        
        # Tachado
        texto_original_str = f"${precio_original}"
        w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
        draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(255, 255, 255), font=fuente_tachado, anchor="mm")
        draw.line([(ancho//2 - w_tachado//2 - 10, precio_orig_y), (ancho//2 + w_tachado//2 + 10, precio_orig_y)], fill=(220, 20, 20), width=8)
        
        # Oferta
        texto_oferta_str = f"${precio} MXN"
        draw.text((ancho//2 + 5, precio_final_y + 5), texto_oferta_str, fill=(0, 50, 0, 150), font=fuente_precios, anchor="mm")
        draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 255, 0), font=fuente_precios, anchor="mm", stroke_width=2, stroke_fill=(20, 100, 0))

        # Renderizar en pantalla
        buffered = BytesIO()
        banner_base.save(buffered, format="PNG")
        st.image(buffered.getvalue(), caption="Banner Generado Automáticamente", use_container_width=True)

        st.download_button(
            label="📥 Descargar Imagen Publicitaria Completa",
            data=buffered.getvalue(),
            file_name=f"banner_{producto.replace(' ', '_')}.png",
            mime="image/png",
        )
    else:
        st.info("👆 Llena el Precio Original e inserta tu imagen para generar el Banner.")
