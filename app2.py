import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
from io import BytesIO
import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Mi Catálogo Inteligente",
    page_icon="🛍️",
    layout="centered"
)

# --- 2. ESTILO PERSONALIZADO (CSS) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; }
    .producto-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATOS (Simulados - Aquí conectarás tu Google Sheet después) ---
@st.cache_data
def load_data():
    data = {
        'id': ['p1', 'p2', 'p3'],
        'nombre': ['Humor envove', 'Crema care frutos rojos', 'Crema ekos maracuya'],
        'precio': [250.00, 120.00, 450.00],
        'stock': [15, 3, 5],
        'imagen': [
            'https://www.bing.com/images/search?view=detailV2&ccid=nK7uvgHG&id=061E04D9A13753EC27A79EB59CF2D81D136C9A76&thid=OIP.nK7uvgHG7BjsV0WDx8RVqwHaHa&mediaurl=https%3a%2f%2ffimgs.net%2fmdimg%2fsecundar%2fo.132246.jpg&cdnurl=https%3a%2f%2fth.bing.com%2fth%2fid%2fR.9caeeebe01c6ec18ec574583c7c455ab%3frik%3ddppsEx3Y8py1ng%26pid%3dImgRaw%26r%3d0&exph=1200&expw=1200&q=humor+envolve+natura&FORM=IRPRST&ck=23C67B4B07FF60CDA5D4D4E01D32263A&selectedIndex=0&itb=0&ajaxhist=0&ajaxserp=0',
            'https://production.na01.natura.com/on/demandware.static/-/Sites-avon-ar-storefront-catalog/default/dw703667e5/AVNARG-711408_1.jpg',
            'https://stockings.cl/wp-content/uploads/2024/03/Pulma-Hidratante-para-manos-Ekos-Maracuya_Webp.webp'
        ]
    }
    return pd.DataFrame(data)

df = load_data()

# --- 4. INICIALIZAR CARRITO ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- 5. LÓGICA DE NAVEGACIÓN (QR vs Catálogo) ---
params = st.query_params

# A. VISTA DE DETALLE (Cuando escanean un QR)
if "id" in params:
    prod_id = params["id"]
    producto = df[df['id'] == prod_id]

    if not producto.empty:
        p = producto.iloc[0]
        if st.button("⬅️ Volver al catálogo"):
            st.query_params.clear()
            st.rerun()
        
        st.image(p['imagen'], use_container_width=True)
        st.title(p['nombre'])
        st.subheader(f"Precio: ${p['precio']:,.2f}")
        
        if p['stock'] > 0:
            st.success(f"✅ Stock disponible: {p['stock']} unidades")
            if st.button("🛒 Añadir al carrito"):
                st.session_state.carrito.append(p.to_dict())
                st.toast(f"{p['nombre']} añadido!")
        else:
            st.error("❌ Agotado temporalmente")
            st.button("Agotado", disabled=True)
        
        # Sección de Reseñas (Simulada)
        st.divider()
        st.subheader("💬 Reseñas")
        st.write("⭐ 4.5/5 - '¡Excelente calidad!'")
        with st.expander("Escribir una reseña"):
            st.text_input("Tu nombre")
            st.text_area("Tu comentario")
            st.button("Enviar reseña")

# B. VISTA PRINCIPAL (Página de Bienvenida)
else:
    st.image("https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1000", use_container_width=True)
    st.title("✨ Bienvenidos a Nuestra Tienda")
    
    # Banner de Instalación PWA
    with st.container(border=True):
        st.markdown("📱 **¡Instala nuestra App!** Toca los 3 puntos (Android) o Compartir (iOS) y selecciona 'Añadir a pantalla de inicio'.")

    st.divider()
    st.subheader("Nuestros Productos")
    
    # Grid de productos
    for i, row in df.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            c1.image(row['imagen'])
            c2.subheader(row['nombre'])
            c2.write(f"Precio: **${row['precio']:,.2f}**")
            if c2.button(f"Ver más de {row['nombre']}", key=f"view_{row['id']}"):
                st.query_params["id"] = row['id']
                st.rerun()

# --- 6. BARRA LATERAL (CARRITO & WHATSAPP) ---
with st.sidebar:
    st.header("🛒 Mi Carrito")
    if not st.session_state.carrito:
        st.write("Está vacío.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrito):
            st.write(f"**{item['nombre']}** - ${item['precio']}")
            total += item['precio']
        
        st.divider()
        st.subheader(f"Total: ${total:,.2f}")
        
        if st.button("Finalizar por WhatsApp", type="primary"):
            mensaje = "Hola! Quiero pedir:%0A" + "%0A".join([f"- {p['nombre']}" for p in st.session_state.carrito])
            # Cambia el número abajo por el tuyo
            st.link_button("🚀 Enviar a WhatsApp", f"https://wa.me/+5492634303887?text={mensaje}")
        
        if st.button("Vaciar carrito"):
            st.session_state.carrito = []
            st.rerun()