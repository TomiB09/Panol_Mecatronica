import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Materiales Mecatrónica - ORT",
    page_icon="⚙️",
    layout="wide"
)

# 2. CSS Personalizado
st.markdown("""
    <style>
    .main-title {
        font-size: 2.6rem;
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
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INICIALIZACIÓN DE DATOS Y ESTADO DE LA APP
# ---------------------------------------------------------
if "inventario" not in st.session_state:
    st.session_state["inventario"] = [
        {"id": 1, "nombre": "Arduino UNO Rev3", "categoria": "Microcontroladores", "stock": 15, "ubicacion": "Caja A1", "descripcion": "Placa de desarrollo ATmega328P"},
        {"id": 2, "nombre": "ESP32 NodeMCU", "categoria": "Microcontroladores", "stock": 8, "ubicacion": "Caja A2", "descripcion": "Módulo Wi-Fi y Bluetooth dual core"},
        {"id": 3, "nombre": "Servomotor SG90 9g", "categoria": "Actuadores y Motores", "stock": 2, "ubicacion": "Caja B1", "descripcion": "Servomotor de torque 1.8 kg/cm"},
        {"id": 4, "nombre": "Motor Paso a Paso NEMA 17", "categoria": "Actuadores y Motores", "stock": 6, "ubicacion": "Caja B3", "descripcion": "Motor stepper para impresión 3D / CNC"},
        {"id": 5, "nombre": "Sensor Ultrasónico HC-SR04", "categoria": "Sensores", "stock": 20, "ubicacion": "Caja C1", "descripcion": "Medidor de distancia por ultrasonido"},
        {"id": 6, "nombre": "Sensor de Temperatura DHT11", "categoria": "Sensores", "stock": 0, "ubicacion": "Caja C2", "descripcion": "Sensor digital de humedad y temperatura"},
    ]

if "pedidos" not in st.session_state:
    st.session_state["pedidos"] = []

if "rol" not in st.session_state:
    st.session_state["rol"] = "Alumno"

if "profesor_autenticado" not in st.session_state:
    st.session_state["profesor_autenticado"] = False

# ---------------------------------------------------------
# ENCABEZADO CON LOGO DE ORT MÁS GRANDE
# ---------------------------------------------------------
col_header, col_logo = st.columns([3, 1])

with col_header:
    st.markdown("<h1 class='main-title'>⚙️ Materiales Mecatrónica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Pañol de Mecatrónica • Escuela ORT</p>", unsafe_allow_html=True)

with col_logo:
    try:
        st.image("logo_ort.png", width=220)  # Logo más grande
    except:
        st.write("📷 *(Logo ORT)*")

st.divider()

# ---------------------------------------------------------
# SELECCIÓN DE ROL (Botones Grandes)
# ---------------------------------------------------------
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

# VALIDACIÓN DE CONTRASEÑA DE PROFESOR
if st.session_state["rol"] == "Profesor" and not st.session_state["profesor_autenticado"]:
    st.warning("🔒 Acceso restringido para Profesores.")
    with st.form("form_login_profesor"):
        clave = st.text_input("Ingresá la contraseña:", type="password")
        btn_ingresar = st.form_submit_button("Ingresar")
        if btn_ingresar:
            if clave == "admin123":
                st.session_state["profesor_autenticado"] = True
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Intentalo de nuevo.")
    st.stop()

# Info de sesión activa
col_status, col_logout = st.columns([4, 1])
with col_status:
    st.caption(f"Perfil activo: **{st.session_state['rol']}**")
with col_logout:
    if st.session_state["rol"] == "Profesor" and st.session_state["profesor_autenticado"]:
        if st.button("🔒 Cerrar Sesión", type="secondary"):
            st.session_state["profesor_autenticado"] = False
            st.session_state["rol"] = "Alumno"
            st.rerun()

st.divider()

# ---------------------------------------------------------
# VISTA: ALUMNO
# ---------------------------------------------------------
if st.session_state["rol"] == "Alumno":
    tab1, tab2, tab3 = st.tabs(["🔍 Consultar Stock", "📋 Pedir Materiales", "📜 Mis Pedidos"])

    df_inventario = pd.DataFrame(st.session_state["inventario"])

    # TAB 1: CONSULTAR STOCK
    with tab1:
        st.subheader("Buscador de Componentes")
        col_search, col_cat = st.columns([3, 2])
        
        with col_search:
            busqueda = st.text_input("Buscar componente:", placeholder="Ej. Arduino, Sensor, Servo...")
        with col_cat:
            cat_options = ["Todas"] + list(df_inventario["categoria"].unique())
            categoria_sel = st.selectbox("Filtrar por categoría:", cat_options)

        df_filtrado = df_inventario.copy()

        if categoria_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado["categoria"] == categoria_sel]
        if busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["nombre"].str.contains(busqueda, case=False) | 
                df_filtrado["descripcion"].str.contains(busqueda, case=False)
            ]

        if df_filtrado.empty:
            st.warning("No se encontraron componentes.")
        else:
            for cat in df_filtrado["categoria"].unique():
                with st.expander(f"📁 **{cat}**", expanded=True):
                    items = df_filtrado[df_filtrado["categoria"] == cat]
                    for _, item in items.iterrows():
                        c_info, c_stock = st.columns([3, 1])
                        with c_info:
                            st.markdown(f"### {item['nombre']}")
                            st.write(f"📝 {item['descripcion']}")
                            st.caption(f"📍 Ubicación: **{item['ubicacion']}**")
                        with c_stock:
                            if item['stock'] > 3:
                                st.metric("Stock Disponible", f"{item['stock']} un.")
                            elif item['stock'] > 0:
                                st.metric("⚠️ Poco Stock", f"{item['stock']} un.")
                            else:
                                st.metric("❌ Sin Stock", "0 un.")
                        st.divider()

    # TAB 2: PEDIR MATERIALES
    with tab2:
        st.subheader("Solicitud de Material para Clases / Proyectos")
        with st.form("form_pedido_alumno"):
            alumno_nombre = st.text_input("Nombre completo del Alumno / Grupo:")
            curso_proyecto = st.text_
