import hashlib
import math
import os
import random
import re
from io import BytesIO
from pathlib import Path
from typing import Optional

import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Generador de Ofertas para Móvil",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hace que la interfaz se adapte a teléfonos, tabletas y computadoras.
st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 1.3rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stImage"] img {
            max-height: 78vh;
            object-fit: contain;
        }

        .stDownloadButton button,
        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 3rem;
            font-weight: 700;
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 0.8rem 0.75rem 1.5rem;
            }

            h1 {
                font-size: 1.75rem !important;
                line-height: 1.15 !important;
            }

            h2, h3 {
                line-height: 1.2 !important;
            }

            div[data-testid="stHorizontalBlock"] {
                display: block;
            }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 0.35rem;
            }

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            textarea {
                min-height: 2.8rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_WIDTH = 1080
BASE_HEIGHT = 1920

FORMATOS = {
    "Historia / Reel vertical (9:16)": (1080, 1920),
    "Publicación vertical (4:5)": (1080, 1350),
    "Publicación cuadrada (1:1)": (1080, 1080),
    "Horizontal (16:9)": (1920, 1080),
}

PALETAS = {
    "Salud y belleza": {
        "fondo": (128, 186, 230, 255),
        "brillo": (190, 230, 255),
        "sello": (148, 230, 255, 255),
        "sello_texto": (72, 155, 230),
    },
    "Tecnología": {
        "fondo": (52, 76, 115, 255),
        "brillo": (94, 155, 225),
        "sello": (108, 180, 255, 255),
        "sello_texto": (30, 85, 150),
    },
    "Moda": {
        "fondo": (225, 151, 185, 255),
        "brillo": (255, 205, 227),
        "sello": (255, 190, 220, 255),
        "sello_texto": (185, 65, 120),
    },
    "Alimentos": {
        "fondo": (244, 166, 76, 255),
        "brillo": (255, 221, 145),
        "sello": (255, 213, 114, 255),
        "sello_texto": (190, 100, 25),
    },
    "General": {
        "fondo": (128, 186, 230, 255),
        "brillo": (190, 230, 255),
        "sello": (148, 230, 255, 255),
        "sello_texto": (72, 155, 230),
    },
}


# =========================================================
# FUENTES Y TEXTO
# =========================================================
def _rutas_fuentes(candidatos: list[str]) -> Optional[str]:
    for ruta in candidatos:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


@st.cache_resource
def cargar_rutas_fuentes() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Busca fuentes compatibles con Windows, Linux, macOS y Streamlit Cloud."""
    carpeta = Path(__file__).resolve().parent

    regular = _rutas_fuentes(
        [
            str(carpeta / "arial.ttf"),
            "arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    )
    bold = _rutas_fuentes(
        [
            str(carpeta / "arialbd.ttf"),
            "arialbd.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    )
    display = _rutas_fuentes(
        [
            str(carpeta / "fuente_oferta.ttf"),
            str(carpeta / "arialbd.ttf"),
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
    )
    return regular, bold, display


def obtener_fuente(tamano: int, tipo: str = "regular") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    regular, bold, display = cargar_rutas_fuentes()
    ruta = {"regular": regular, "bold": bold, "display": display}.get(tipo, regular)
    if ruta:
        try:
            return ImageFont.truetype(ruta, max(10, int(tamano)))
        except OSError:
            pass
    return ImageFont.load_default()


def ajustar_fuente(
    draw: ImageDraw.ImageDraw,
    texto: str,
    ancho_maximo: int,
    tamano_inicial: int,
    tamano_minimo: int,
    tipo: str = "bold",
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Reduce el tamaño de fuente hasta que el texto quepa en el ancho disponible."""
    for tamano in range(tamano_inicial, tamano_minimo - 1, -2):
        fuente = obtener_fuente(tamano, tipo)
        caja = draw.textbbox((0, 0), texto, font=fuente, stroke_width=2)
        if caja[2] - caja[0] <= ancho_maximo:
            return fuente
    return obtener_fuente(tamano_minimo, tipo)


def texto_seguro(valor: str, predeterminado: str, limite: int = 55) -> str:
    limpio = " ".join((valor or "").strip().split())
    return (limpio or predeterminado)[:limite]


def nombre_archivo_seguro(nombre: str) -> str:
    nombre = re.sub(r"[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ_-]+", "_", nombre.strip())
    return nombre.strip("_") or "producto"


# =========================================================
# ELEMENTOS GRÁFICOS
# =========================================================
def draw_scalloped_badge(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    r_outer: int,
    r_inner: int,
    points: int,
    fill: tuple,
    outline: tuple,
    width: int,
) -> None:
    poly = []
    for i in range(points * 2):
        angle = i * math.pi / points
        radius = r_outer if i % 2 == 0 else r_inner
        poly.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))

    draw.polygon(poly, fill=fill)
    if width > 0:
        draw.line(poly + [poly[0]], fill=outline, width=width, joint="curve")


def draw_torn_ribbon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    fill: tuple,
    rng: random.Random,
    zigzags: int = 6,
) -> None:
    points: list[tuple[float, float]] = [(x, y), (x + width, y - 50)]
    y_step = height / zigzags

    for i in range(1, zigzags + 1):
        x_offset = rng.randint(-15, 15) if i < zigzags else 0
        points.append((x + width + x_offset, y - 50 + i * y_step))

    points.append((x, y + height))

    for i in range(zigzags - 1, 0, -1):
        points.append((x + rng.randint(-15, 15), y + i * y_step))

    draw.polygon(points, fill=fill)


def create_sale_tag() -> Image.Image:
    tag = Image.new("RGBA", (200, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tag)
    draw.polygon(
        [(40, 10), (190, 10), (190, 70), (40, 70), (10, 40)],
        fill=(255, 85, 50, 255),
    )
    draw.ellipse([(20, 35), (30, 45)], fill=(255, 255, 255, 255))
    fuente = obtener_fuente(40, "bold")
    draw.text((115, 40), "sale", fill=(255, 255, 255, 255), font=fuente, anchor="mm")
    return tag


def preparar_producto(archivo) -> Image.Image:
    imagen = Image.open(archivo)
    imagen = ImageOps.exif_transpose(imagen)
    return imagen.convert("RGBA")


def adaptar_formato(imagen_vertical: Image.Image, tamano_objetivo: tuple[int, int]) -> Image.Image:
    """
    Conserva todo el diseño vertical. En formatos distintos de 9:16 crea un fondo
    desenfocado para evitar recortar texto, precios o producto.
    """
    target_w, target_h = tamano_objetivo
    if imagen_vertical.size == tamano_objetivo:
        return imagen_vertical

    fondo = ImageOps.fit(
        imagen_vertical.convert("RGB"),
        (target_w, target_h),
        method=Image.Resampling.LANCZOS,
    ).filter(ImageFilter.GaussianBlur(max(16, target_w // 45)))
    fondo = fondo.convert("RGBA")

    escala = min(target_w / imagen_vertical.width, target_h / imagen_vertical.height)
    nuevo_w = max(1, int(imagen_vertical.width * escala))
    nuevo_h = max(1, int(imagen_vertical.height * escala))
    frente = imagen_vertical.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)

    x = (target_w - nuevo_w) // 2
    y = (target_h - nuevo_h) // 2

    # Panel translúcido para que la pieza principal se distinga del fondo.
    panel = Image.new("RGBA", (nuevo_w, nuevo_h), (255, 255, 255, 18))
    fondo.alpha_composite(panel, (x, y))
    fondo.alpha_composite(frente, (x, y))
    return fondo


def generar_banner(
    imagen_producto: Image.Image,
    nombre_producto: str,
    precio_oferta: str,
    precio_original: str,
    descuento: str,
    moneda: str,
    categoria: str,
    mostrar_sello: bool,
) -> Image.Image:
    """Genera el diseño maestro en 1080 × 1920 usando posiciones seguras."""
    paleta = PALETAS.get(categoria, PALETAS["General"])
    semilla = hashlib.sha256(
        f"{nombre_producto}|{precio_oferta}|{precio_original}|{descuento}".encode("utf-8")
    ).hexdigest()
    rng = random.Random(int(semilla[:16], 16))

    banner = Image.new("RGBA", (BASE_WIDTH, BASE_HEIGHT), paleta["fondo"])
    draw = ImageDraw.Draw(banner, "RGBA")

    # Brillo radial.
    for alpha in range(45, 0, -2):
        radio = 570 + (45 - alpha) * 17
        color = (*paleta["brillo"], alpha)
        draw.ellipse(
            [
                (BASE_WIDTH // 2 - radio, BASE_HEIGHT // 2 - radio - 190),
                (BASE_WIDTH // 2 + radio, BASE_HEIGHT // 2 + radio - 190),
            ],
            fill=color,
        )

    # Confeti reproducible.
    colores_confeti = [
        (255, 70, 70, 235),
        (255, 215, 0, 235),
        (70, 150, 255, 235),
        (255, 255, 255, 225),
    ]
    for _ in range(110):
        x = rng.randint(0, BASE_WIDTH)
        y = rng.randint(0, BASE_HEIGHT)
        tam = rng.randint(9, 24)
        color = rng.choice(colores_confeti)
        angle = rng.uniform(0, math.pi)
        p1 = (x, y)
        p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
        p3 = (
            x + tam * math.cos(angle) - (tam / 2) * math.sin(angle),
            y + tam * math.sin(angle) + (tam / 2) * math.cos(angle),
        )
        p4 = (x - (tam / 2) * math.sin(angle), y + (tam / 2) * math.cos(angle))
        draw.polygon([p1, p2, p3, p4], fill=color)

    # Encabezado.
    encabezado = "OFERTA RELÁMPAGO"
    fuente_titulo = ajustar_fuente(draw, encabezado, 940, 86, 48, "bold")
    draw.text(
        (BASE_WIDTH // 2 + 5, 151),
        encabezado,
        fill=(0, 0, 0, 95),
        font=fuente_titulo,
        anchor="mm",
    )
    draw.text(
        (BASE_WIDTH // 2, 145),
        encabezado,
        fill=(255, 255, 255, 255),
        font=fuente_titulo,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(255, 255, 255, 255),
    )

    # Nombre del producto.
    nombre = texto_seguro(nombre_producto, "Producto en oferta", 45)
    fuente_nombre = ajustar_fuente(draw, nombre, 900, 58, 32, "bold")
    draw.rounded_rectangle(
        [(85, 225), (995, 330)],
        radius=30,
        fill=(0, 0, 0, 70),
    )
    draw.text(
        (BASE_WIDTH // 2, 277),
        nombre,
        fill=(255, 255, 255, 255),
        font=fuente_nombre,
        anchor="mm",
    )

    # Sello de más vendido.
    if mostrar_sello:
        pos_x, pos_y = 820, 490
        draw_scalloped_badge(
            draw,
            pos_x + 10,
            pos_y + 10,
            158,
            140,
            16,
            (0, 0, 0, 55),
            (0, 0, 0, 0),
            0,
        )
        draw_scalloped_badge(
            draw,
            pos_x,
            pos_y,
            158,
            140,
            16,
            paleta["sello"],
            (255, 255, 255, 255),
            10,
        )
        draw.ellipse(
            [(pos_x - 112, pos_y - 112), (pos_x + 112, pos_y + 112)],
            outline=(255, 255, 255, 255),
            width=5,
        )
        fuente_sello = obtener_fuente(52, "bold")
        draw.text(
            (pos_x, pos_y - 32),
            "MÁS",
            fill=paleta["sello_texto"],
            font=fuente_sello,
            anchor="mm",
        )
        draw.text(
            (pos_x, pos_y + 32),
            "VENDIDO",
            fill=paleta["sello_texto"],
            font=obtener_fuente(43, "bold"),
            anchor="mm",
        )

    # Etiquetas decorativas.
    tag = create_sale_tag()
    tag_1 = tag.rotate(25, expand=True, resample=Image.Resampling.BICUBIC)
    tag_2 = tag.rotate(-20, expand=True, resample=Image.Resampling.BICUBIC)
    banner.alpha_composite(tag_1, (235, 360))
    banner.alpha_composite(tag_2, (760, 1240))

    # Imagen del producto: usa un área máxima, sin deformarla.
    producto = imagen_producto.copy()
    producto.thumbnail((900, 760), Image.Resampling.LANCZOS)
    prod_w, prod_h = producto.size
    prod_x = (BASE_WIDTH - prod_w) // 2
    prod_y = 555 + max(0, (760 - prod_h) // 2)

    sombra = Image.new("RGBA", (prod_w + 120, 130), (0, 0, 0, 0))
    sombra_draw = ImageDraw.Draw(sombra, "RGBA")
    sombra_draw.ellipse(
        [(30, 30), (prod_w + 90, 105)],
        fill=(0, 0, 0, 115),
    )
    sombra = sombra.filter(ImageFilter.GaussianBlur(20))
    banner.alpha_composite(sombra, (prod_x - 60, prod_y + prod_h - 75))
    banner.alpha_composite(producto, (prod_x, prod_y))

    # Listón de descuento.
    cinta_x, cinta_y, cinta_w, cinta_h = 95, 1370, 890, 245
    draw_torn_ribbon(
        draw,
        cinta_x - 10,
        cinta_y + 12,
        cinta_w + 40,
        cinta_h,
        (255, 215, 0, 255),
        rng,
    )
    draw_torn_ribbon(
        draw,
        cinta_x,
        cinta_y,
        cinta_w,
        cinta_h,
        (255, 60, 0, 255),
        rng,
    )

    descuento_limpio = texto_seguro(descuento, "¡OFERTA!", 24)
    fuente_descuento = ajustar_fuente(draw, descuento_limpio, 790, 150, 68, "display")
    draw.text(
        (BASE_WIDTH // 2 + 8, cinta_y + 116),
        descuento_limpio,
        fill=(145, 0, 0, 210),
        font=fuente_descuento,
        anchor="mm",
    )
    draw.text(
        (BASE_WIDTH // 2, cinta_y + 108),
        descuento_limpio,
        fill=(255, 235, 0, 255),
        font=fuente_descuento,
        anchor="mm",
    )

    # Precios con ajuste automático de tamaño.
    original = f"{moneda}{texto_seguro(precio_original, '0', 18)}"
    oferta = f"{moneda}{texto_seguro(precio_oferta, '0', 18)}"

    fuente_original = ajustar_fuente(draw, original, 800, 66, 36, "bold")
    fuente_oferta = ajustar_fuente(draw, oferta, 920, 116, 54, "bold")

    original_y = 1715
    draw.text(
        (BASE_WIDTH // 2, original_y),
        original,
        fill=(255, 255, 255, 255),
        font=fuente_original,
        anchor="mm",
    )
    caja_original = draw.textbbox(
        (BASE_WIDTH // 2, original_y),
        original,
        font=fuente_original,
        anchor="mm",
    )
    draw.line(
        [(caja_original[0] - 12, original_y), (caja_original[2] + 12, original_y)],
        fill=(220, 20, 20, 255),
        width=8,
    )

    oferta_y = 1830
    draw.text(
        (BASE_WIDTH // 2 + 6, oferta_y + 6),
        oferta,
        fill=(0, 50, 0, 155),
        font=fuente_oferta,
        anchor="mm",
    )
    draw.text(
        (BASE_WIDTH // 2, oferta_y),
        oferta,
        fill=(100, 255, 0, 255),
        font=fuente_oferta,
        anchor="mm",
        stroke_width=3,
        stroke_fill=(20, 100, 0, 255),
    )

    return banner


# =========================================================
# INTERFAZ
# =========================================================
st.title("🛒 Generador de ofertas para teléfono")
st.caption(
    "Funciona desde el navegador de Android, iPhone, tablet o computadora. "
    "El resultado se descarga como imagen PNG."
)

with st.form("formulario_oferta", clear_on_submit=False):
    col_1, col_2 = st.columns(2)

    with col_1:
        producto_nombre = st.text_input(
            "Nombre del producto",
            value="Kit La Roche-Posay",
            max_chars=55,
        )
        precio_oferta_txt = st.text_input(
            "Precio de oferta",
            value="1,125",
            max_chars=18,
        )
        porcentaje_desc_txt = st.text_input(
            "Texto del descuento",
            value="¡25% OFF!",
            max_chars=24,
        )
        moneda = st.selectbox(
            "Símbolo o moneda",
            ["$", "$ MXN ", "$ USD ", "€", "£"],
            index=0,
        )

    with col_2:
        precio_original_txt = st.text_input(
            "Precio original",
            value="1,500",
            max_chars=18,
        )
        categoria = st.selectbox(
            "Categoría",
            list(PALETAS.keys()),
            index=0,
        )
        formato_nombre = st.selectbox(
            "Formato de salida",
            list(FORMATOS.keys()),
            index=0,
        )
        mostrar_sello = st.checkbox("Mostrar sello “MÁS VENDIDO”", value=True)

    st.markdown("#### Imagen del producto")
    metodo = st.radio(
        "Selecciona cómo agregarla",
        ["Subir archivo", "Tomar foto con la cámara"],
        horizontal=True,
    )

    if metodo == "Subir archivo":
        archivo_imagen = st.file_uploader(
            "PNG transparente recomendado; también acepta JPG, JPEG y WEBP",
            type=["png", "jpg", "jpeg", "webp"],
        )
    else:
        archivo_imagen = st.camera_input("Toma una foto del producto")

    generar = st.form_submit_button("✨ Generar diseño")


if generar:
    if archivo_imagen is None:
        st.error("Agrega una imagen del producto antes de generar el diseño.")
    elif not precio_oferta_txt.strip() or not precio_original_txt.strip():
        st.error("Escribe el precio de oferta y el precio original.")
    else:
        try:
            with st.spinner("Generando diseño…"):
                imagen_producto = preparar_producto(archivo_imagen)
                maestro = generar_banner(
                    imagen_producto=imagen_producto,
                    nombre_producto=producto_nombre,
                    precio_oferta=precio_oferta_txt,
                    precio_original=precio_original_txt,
                    descuento=porcentaje_desc_txt,
                    moneda=moneda,
                    categoria=categoria,
                    mostrar_sello=mostrar_sello,
                )
                resultado = adaptar_formato(maestro, FORMATOS[formato_nombre])

                buffer = BytesIO()
                resultado.convert("RGB").save(buffer, format="PNG", optimize=True)
                datos_png = buffer.getvalue()

            st.success("Diseño generado correctamente.")
            st.image(
                datos_png,
                caption=f"{formato_nombre} · {resultado.width} × {resultado.height} px",
                use_container_width=True,
            )
            st.download_button(
                label="📥 Descargar imagen PNG",
                data=datos_png,
                file_name=f"oferta_{nombre_archivo_seguro(producto_nombre)}.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"No fue posible procesar la imagen: {exc}")
            st.info(
                "Prueba con una imagen PNG, JPG o WEBP diferente. "
                "Algunos formatos especiales de cámara, como HEIC, necesitan convertirse primero."
            )
else:
    st.info("Completa los datos, agrega la foto y presiona “Generar diseño”.")
