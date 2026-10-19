import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Materiales Meca - ORT",
    page_icon="⚙️",
    layout="wide"
)

# 2. CSS Personalizado para un diseño más elaborado y moderno
st.markdown("""
    <style>
    /* Estilos del encabezado */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #002B66;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #666;
        margin-top: -5px;
        margin-bottom: 20px;
    }
    
    /* Tarjetas de materiales */
    .material-card {
        background-color: #f8f9fa;
        border-left: 5px solid #002B66;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stock-badge-high {
        color: #1b5e20;
        background-color: #c8e6c9;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .stock-badge-low {
        color: #b71c1c;
        background-color: #ffcdd2;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ENCABEZADO CON LOGO DE ORT
# ---------------------------------------------------------
col_header, col_logo = st.columns([4, 1])

with col_header:
    st.markdown("<h1 class='main-title'>⚙️ Materiales Meca</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Pañol de Mecatrónica • Escuela ORT</p>", unsafe_allow_html=True)

with col_logo:
    # Carga la imagen del logo que guardaste localmente
    try:
        st.image("logo_ort.png", width=140)
    except:
        st.write("📷 *(Logo ORT)*")

st.divider()

# ---------------------------------------------------------
# SELECCIÓN DE ROL (Botones Grandes)
# ---------------------------------------------------------
if "rol" not in st.session_state:
    st.session_state["rol"] = "Alumno"

st.subheader("👤 Seleccioná tu perfil")

col_alumno, col_profesor = st.columns(2)

with col_alumno:
    btn_alumno = st.button(
        "🎓 ALUMNO",
        use_container_width=True,
        type="primary" if st.session_state["rol"] == "Alumno" else "secondary"
    )
    if btn_alumno:
        st.session_state["rol"] = "Alumno"
        st.rerun()

with col_profesor:
    btn_profesor = st.button(
        "👨‍🏫 PROFESOR",
        use_container_width=True,
        type="primary" if st.session_state["rol"] == "Profesor" else "secondary"
    )
    if btn_profesor:
        st.session_state["rol"] = "Profesor"
        st.rerun()

st.caption(f"Perfil seleccionado actualmente: **{st.session_state['rol']}**")
st.write("")

# ---------------------------------------------------------
# DATOS DE EJEMPLO (Se reemplaza por las consultas SQL a Supabase)
# ---------------------------------------------------------
datos_inventario = [
    {"id": 1, "nombre": "Arduino UNO Rev3", "categoria": "Microcontroladores", "stock": 15, "ubicacion": "Caja A1", "descripcion": "Placa de desarrollo ATmega328P"},
    {"id": 2, "nombre": "ESP32 NodeMCU", "categoria": "Microcontroladores", "stock": 8, "ubicacion": "Caja A2", "descripcion": "Módulo Wi-Fi y Bluetooth dual core"},
    {"id": 3, "nombre": "Servomotor SG90 9g", "categoria": "Actuadores y Motores", "stock": 2, "ubicacion": "Caja B1", "descripcion": "Servomotor de torque 1.8 kg/cm"},
    {"id": 4, "nombre": "Motor Pasó a Paso NEMA 17", "categoria": "Actuadores y Motores", "stock": 6, "ubicacion": "Caja B3", "descripcion": "Motor stepper para impresión 3D / CNC"},
    {"id": 5, "nombre": "Sensor Ultrasónico HC-SR04", "categoria": "Sensores", "stock": 20, "ubicacion": "Caja C1", "descripcion": "Medidor de distancia por ultrasonido"},
    {"id": 6, "nombre": "Sensor de Temperatura DHT11", "categoria": "Sensores", "stock": 0, "ubicacion": "Caja C2", "descripcion": "Sensor digital de humedad y temperatura"},
]

df_inventario = pd.DataFrame(datos_inventario)

# ---------------------------------------------------------
# BÚSQUEDA Y CATEGORÍAS DE MATERIALES
# ---------------------------------------------------------
st.subheader("🔍 Buscador de Componentes")

col_search, col_cat = st.columns([3, 2])

with col_search:
    busqueda = st.text_input("Buscar por nombre o descripción:", placeholder="Ej. Arduino, Sensor, Servo...")

with col_cat:
    categorias_disponibles = ["Todas"] + list(df_inventario["categoria"].unique())
    categoria_sel = st.selectbox("Filtrar por categoría:", categorias_disponibles)

# Filtrar DataFrame según búsqueda y categoría
df_filtrado = df_inventario.copy()

if categoria_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria_sel]

if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado["nombre"].str.contains(busqueda, case=False) | 
        df_filtrado["descripcion"].str.contains(busqueda, case=False)
    ]

# ---------------------------------------------------------
# VISUALIZACIÓN POR CATEGORÍA Y DETALLE DE STOCK
# ---------------------------------------------------------
st.write("")

if df_filtrado.empty:
    st.warning("No se encontraron componentes con los criterios ingresados.")
else:
    # Agrupar componentes por categorías
    categorias_presentes = df_filtrado["categoria"].unique()
    
    for cat in categorias_presentes:
        with st.expander(f"📁 **{cat}**", expanded=True):
            items_cat = df_filtrado[df_filtrado["categoria"] == cat]
            
            for _, item in items_cat.iterrows():
                col_info, col_stock_metric = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"### {item['nombre']}")
                    st.write(f"📝 {item['descripcion']}")
                    st.caption(f"📍 **Ubicación en Pañol:** {item['ubicacion']}")
                
                with col_stock_metric:
                    # Formato de stock visual según cantidad
                    if item['stock'] > 3:
                        st.metric(label="Stock Disponible", value=f"{item['stock']} unidades")
                    elif item['stock'] > 0:
                        st.metric(label="⚠️ Poco Stock", value=f"{item['stock']} unidades")
                    else:
                        st.metric(label="❌ Sin Stock", value="0 unidades")
                
                # Acciones exclusivas para profesores
                if st.session_state["rol"] == "Profesor":
                    c1, c2 = st.columns(2)
                    with c1:
                        st.button(f"✏️ Editar {item['nombre']}", key=f"edit_{item['id']}")
                    with c2:
                        st.button(f"➕ Modificar Stock", key=f"stock_{item['id']}")
                
                st.divider()
