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
# ENCABEZADO CON LOGO DE ORT
# ---------------------------------------------------------
col_header, col_logo = st.columns([3, 1])

with col_header:
    st.markdown("<h1 class='main-title'>⚙️ Materiales Mecatrónica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Pañol de Mecatrónica • Escuela ORT</p>", unsafe_allow_html=True)

with col_logo:
    try:
        st.image("logo_ort.png", width=220)
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

# Información de perfil activo
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
# SECCIÓN: ALUMNO
# ---------------------------------------------------------
if st.session_state["rol"] == "Alumno":
    tab1, tab2, tab3 = st.tabs(["🔍 Materiales", "📋 Pedir Material", "📜 Mis Pedidos"])

    df_inventario = pd.DataFrame(st.session_state["inventario"])

    # TAB 1: CONSULTAR MATERIALES
    with tab1:
        st.subheader("Buscador de Componentes")
        col_search, col_cat = st.columns([3, 2])
        
        with col_search:
            busqueda = st.text_input("Buscar componente por nombre:", placeholder="Ej. Arduino, Sensor, Servo...")
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
            st.warning("No se encontraron componentes con ese criterio.")
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

    # TAB 2: PEDIR MATERIAL
    with tab2:
        st.subheader("Solicitud de Material para Clases / Proyectos")
        with st.form("form_pedido_alumno"):
            alumno_nombre = st.text_input("Nombre y Apellido del Alumno:")
            alumno_curso = st.text_input("Curso / División / Especialidad:")
            
            materiales_con_stock = df_inventario[df_inventario["stock"] > 0]["nombre"].tolist()
            
            if materiales_con_stock:
                material_sel = st.selectbox("¿Qué material pedís?:", materiales_con_stock)
            else:
                material_sel = None
                st.warning("No hay materiales con stock disponible en este momento.")

            cantidad = st.number_input("Cantidad requerida:", min_value=1, max_value=10, value=1)
            observaciones = st.text_area("Motivo del pedido / Proyecto:")
            
            btn_enviar_pedido = st.form_submit_button("📩 Enviar Solicitud")

            if btn_enviar_pedido:
                if not alumno_nombre.strip() or not alumno_curso.strip():
                    st.error("Por favor completá tu Nombre y Apellido y tu Curso.")
                elif not material_sel:
                    st.error("Seleccioná un material válido para realizar la solicitud.")
                else:
                    nuevo_pedido = {
                        "id": len(st.session_state["pedidos"]) + 1,
                        "alumno": alumno_nombre,
                        "curso": alumno_curso,
                        "material": material_sel,
                        "cantidad": cantidad,
                        "observaciones": observaciones,
                        "estado": "Pendiente"
                    }
                    st.session_state["pedidos"].append(nuevo_pedido)
                    st.success("¡Solicitud enviada con éxito! Queda pendiente de aprobación por el Profesor.")

    # TAB 3: MIS PEDIDOS
    with tab3:
        st.subheader("Estado de tus Solicitudes")
        if not st.session_state["pedidos"]:
            st.info("Aún no realizaste ningún pedido.")
        else:
            for p in reversed(st.session_state["pedidos"]):
                with st.container():
                    c_det, c_est = st.columns([3, 1])
                    with c_det:
                        st.markdown(f"### Pedido #{p['id']}: {p['material']} (x{p['cantidad']})")
                        st.write(f"👤 **Alumno:** {p['alumno']} | **Curso:** {p['curso']}")
                        if p["observaciones"]:
                            st.caption(f"💬 Motivo: {p['observaciones']}")
                    with c_est:
                        if p["estado"] == "Pendiente":
                            st.warning("⏳ Pendiente")
                        elif p["estado"] == "Aceptado":
                            st.success("✅ Aceptado")
                        else:
                            st.error("❌ Rechazado")
                    st.divider()

# ---------------------------------------------------------
# SECCIÓN: PROFESOR
# ---------------------------------------------------------
elif st.session_state["rol"] == "Profesor":
    tab_pedidos, tab_modificar, tab_nuevo = st.tabs(["📬 Pedidos de Alumnos", "⚙️ Modificar Materiales y Stock", "➕ Agregar Material"])

    # TAB 1: PEDIDOS DE ALUMNOS (ACEPTAR / RECHAZAR)
    with tab_pedidos:
        st.subheader("Solicitudes de Materiales Recibidas")
        pedidos_pendientes = [p for p in st.session_state["pedidos"] if p["estado"] == "Pendiente"]
        
        if not pedidos_pendientes:
            st.info("No hay pedidos pendientes de revisión.")
        else:
            for p in pedidos_pendientes:
                with st.container():
                    st.markdown(f"### Solicitud #{p['id']}: {p['material']} (x{p['cantidad']})")
                    st.write(f"👤 **Alumno:** {p['alumno']} | 🏫 **Curso:** {p['curso']}")
                    if p["observaciones"]:
                        st.write(f"💬 **Motivo:** {p['observaciones']}")
                    
                    c_aprobar, c_rechazar = st.columns(2)
                    
                    with c_aprobar:
                        if st.button(f"✅ Aceptar Pedido #{p['id']}", key=f"btn_ok_{p['id']}", type="primary"):
                            p["estado"] = "Aceptado"
                            # Descontar stock del material
                            for item in st.session_state["inventario"]:
                                if item["nombre"] == p["material"]:
                                    item["stock"] = max(0, item["stock"] - p["cantidad"])
                            st.success(f"Pedido #{p['id']} ACEPTADO. Se descontaron {p['cantidad']} unidades del stock.")
                            st.rerun()

                    with c_rechazar:
                        if st.button(f"❌ Rechazar Pedido #{p['id']}", key=f"btn_no_{p['id']}"):
                            p["estado"] = "Rechazado"
                            st.error(f"Pedido #{p['id']} RECHAZADO.")
                            st.rerun()
                    st.divider()

    # TAB 2: MODIFICAR MATERIALES Y STOCK
    with tab_modificar:
        st.subheader("Modificar Inventario y Ajustar Stock")
        
        for idx, item in enumerate(st.session_state["inventario"]):
            with st.expander(f"🛠️ {item['nombre']} — Stock actual: {item['stock']} un."):
                col_e1, col_e2 = st.columns(2)
                
                with col_e1:
                    nuevo_nombre = st.text_input("Nombre del Componente:", value=item["nombre"], key=f"p_nom_{item['id']}")
                    nueva_cat = st.text_input("Categoría:", value=item["categoria"], key=f"p_cat_{item['id']}")
                    nueva_ubicacion = st.text_input("Ubicación en Pañol:", value=item["ubicacion"], key=f"p_ubic_{item['id']}")
                
                with col_e2:
                    nuevo_stock = st.number_input("Stock (Unidades):", min_value=0, value=int(item["stock"]), key=f"p_stk_{item['id']}")
                    nueva_desc = st.text_area("Descripción:", value=item["descripcion"], key=f"p_desc_{item['id']}")

                if st.button(f"💾 Guardar Cambios", key=f"p_save_{item['id']}"):
                    st.session_state["inventario"][idx]["nombre"] = nuevo_nombre
                    st.session_state["inventario"][idx]["categoria"] = nueva_cat
                    st.session_state["inventario"][idx]["ubicacion"] = nueva_ubicacion
                    st.session_state["inventario"][idx]["stock"] = nuevo_stock
                    st.session_state["inventario"][idx]["descripcion"] = nueva_desc
                    st.success(f"¡Cambios guardados en {nuevo_nombre}!")
                    st.rerun()

    # TAB 3: AGREGAR NUEVO MATERIAL
    with tab_nuevo:
        st.subheader("Agregar Nuevo Componente al Pañol")
        with st.form("form_nuevo_componente"):
            item_nom = st.text_input("Nombre del Componente:")
            item_cat = st.text_input("Categoría (ej. Sensores, Microcontroladores, Herramientas):")
            item_stk = st.number_input("Stock Inicial:", min_value=0, value=1)
            item_ubic = st.text_input("Ubicación en Pañol (ej. Caja D3, Estante 2):")
            item_desc = st.text_area("Descripción breve:")
            
            btn_crear = st.form_submit_button("➕ Crear Componente")
            
            if btn_crear:
                if not item_nom.strip() or not item_cat.strip():
                    st.error("Por favor ingresá al menos el nombre y la categoría.")
                else:
                    nuevo_item = {
                        "id": len(st.session_state["inventario"]) + 1,
                        "nombre": item_nom,
                        "categoria": item_cat,
                        "stock": item_stk,
                        "ubicacion": item_ubic,
                        "descripcion": item_desc
                    }
                    st.session_state["inventario"].append(nuevo_item)
                    st.success(f"¡Componente '{item_nom}' agregado al inventario!")
                    st.rerun()
