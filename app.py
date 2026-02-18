import streamlit as st
import pandas as pd
import qrcode

from io import BytesIO


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
    URL_SHEET = "https://docs.google.com/spreadsheets/d/TU_ID/pub?output=csv"  # noqa: F841

def cargar_datos():
    # Lee los datos directamente de la nube
    return pd.read_csv("URL_SHEET")

def generar_qr(url):
    qr = qrcode.make(url)
    buf = BytesIO()
    qr.save(buf, format="JPG")
    return buf.getvalue()

st.title("🛍️ Mi Catálogo desde la Nube")

try:
    df = cargar_datos()
    params = st.query_params
    prod_id = params.get("id")

    if prod_id:
        # Mostrar solo el producto escaneado
        producto = df[df['id'] == prod_id].iloc[0]
        if st.button("⬅️ Volver"): st.query_params.clear()  # noqa: E701
        
        col1, col2 = st.columns(2)
        with col1: st.image(producto['imagen'])  # noqa: E701
        with col2:
            st.header(producto['nombre'])
            st.subheader(f"Precio: {producto['precio']}")
    else:
        # Mostrar catálogo completo con sus QRs
        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 2, 1])
                c1.image(row['imagen'], width=100)
                c2.write(f"**{row['nombre']}**\n\n{row['precio']}")
                
                # Generar el link para el móvil
                link = f"https://tu-app.streamlit.app/?id={row['id']}"
                c3.image(generar_qr(link), caption="Escanea para ver", width=100)

except Exception as e:  # noqa: F841
    st.error("Asegúrate de que el enlace de Google Sheets sea público y correcto.")

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
            st.link_button("🚀 Enviar a WhatsApp", f"https://wa.me/123456789?text={mensaje}")
        
        if st.button("Vaciar carrito"):
            st.session_state.carrito = []
            st.rerun()