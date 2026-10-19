import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Pañol de Mecatrónica", page_icon="⚙️", layout="wide")

# ==============================================================================
# 1. CAPA DE DATOS (FUNCIONALIDAD TEMPORAL / CONTRATO DE INTEGRACIÓN)
# Cuando conecten Supabase, tu compañero solo reemplazará estas 6 funciones.
# ==============================================================================

if 'inventario' not in st.session_state:
    st.session_state.inventario = [
        {"id": 1, "nombre": "Arduino Uno", "categoria": "Microcontroladores", "cantidad": 5, "minimo": 2},
        {"id": 2, "nombre": "Sensor Ultrasónico HC-SR04", "categoria": "Sensores", "cantidad": 2, "minimo": 3},
        {"id": 3, "nombre": "Servomotor SG90", "categoria": "Actuadores", "cantidad": 0, "minimo": 2},
    ]

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

def obtener_inventario():
    return st.session_state.inventario

def obtener_pedidos():
    return st.session_state.pedidos

def crear_pedido(nombre_alumno, producto_nombre, cantidad):
    nuevo_id = len(st.session_state.pedidos) + 1
    st.session_state.pedidos.append({
        "id": nuevo_id,
        "alumno": nombre_alumno,
        "producto": producto_nombre,
        "cantidad": cantidad,
        "estado": "Pendiente"
    })

def aprobar_pedido(pedido_id):
    for p in st.session_state.pedidos:
        if p["id"] == pedido_id and p["estado"] == "Pendiente":
            for prod in st.session_state.inventario:
                if prod["nombre"] == p["producto"]:
                    if prod["cantidad"] >= p["cantidad"]:
                        prod["cantidad"] -= p["cantidad"]
                        p["estado"] = "Aceptado"
                        return True
            break
    return False

def rechazar_pedido(pedido_id):
    for p in st.session_state.pedidos:
        if p["id"] == pedido_id:
            p["estado"] = "Rechazado"
            break

def modificar_stock(producto_nombre, nueva_cantidad):
    for prod in st.session_state.inventario:
        if prod["nombre"] == producto_nombre:
            prod["cantidad"] = nueva_cantidad
            break

def crear_material(nombre, categoria, cantidad, minimo):
    nuevo_id = len(st.session_state.inventario) + 1
    st.session_state.inventario.append({
        "id": nuevo_id,
        "nombre": nombre,
        "categoria": categoria,
        "cantidad": cantidad,
        "minimo": minimo
    })


# ==============================================================================
# 2. CONTROL DE ACCESO Y ROLES (BARRA LATERAL)
# ==============================================================================
if 'rol' not in st.session_state:
    st.session_state.rol = "Alumno"

st.sidebar.title("⚙️ Pañol Mecatrónica")
st.sidebar.write(f"Rol actual: **{st.session_state.rol}**")

modo_seleccionado = st.sidebar.radio("Vista de usuario:", ["Alumno", "Profesor"])

if modo_seleccionado == "Profesor" and st.session_state.rol != "Profesor":
    clave = st.sidebar.text_input("Contraseña de docente:", type="password")
    if st.sidebar.button("Ingresar como Profesor"):
        if clave == "admin123":
            st.session_state.rol = "Profesor"
            st.rerun()
        else:
            st.sidebar.error("Contraseña incorrecta")

elif modo_seleccionado == "Alumno" and st.session_state.rol != "Alumno":
    st.session_state.rol = "Alumno"
    st.rerun()

if st.session_state.rol == "Profesor":
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.rol = "Alumno"
        st.rerun()


# ==============================================================================
# 3. INTERFAZ PRINCIPAL - VISTA DE ALUMNO
# ==============================================================================
st.title("Sistema de Gestión de Inventario")

inventario_actual = obtener_inventario()

if not inventario_actual:
    st.info("El catálogo del pañol está vacío actualmente.")
else:
    categorias_disponibles = sorted(list(set(item["categoria"] for item in inventario_actual)))

    st.header("📦 Consulta y Solicitud de Materiales")
    col_cat, col_prod = st.columns(2)

    with col_cat:
        cat_sel = st.selectbox("1. Selecciona Categoría:", categorias_disponibles)

    productos_filtrados = [p for p in inventario_actual if p["categoria"] == cat_sel]
    nombres_productos = [p["nombre"] for p in productos_filtrados]

    with col_prod:
        prod_sel = st.selectbox("2. Selecciona Componente:", nombres_productos)

    # Búsqueda del objeto seleccionado
    prod_obj = next((p for p in productos_filtrados if p["nombre"] == prod_sel), productos_filtrados[0] if productos_filtrados else None)

    if prod_obj:
        st.subheader("Estado de Disponibilidad:")
        if prod_obj["cantidad"] == 0:
            st.error(f"❌ AGOTADO - No hay {prod_obj['nombre']} disponible.")
        elif prod_obj["cantidad"] <= prod_obj["minimo"]:
            st.warning(f"⚠️ POCO STOCK - Quedan solo {prod_obj['cantidad']} unidad(es).")
        else:
            st.success(f"✅ DISPONIBLE - Hay {prod_obj['cantidad']} unidad(es).")

        # Formulario para pedidos
        if st.session_state.rol == "Alumno" and prod_obj["cantidad"] > 0:
            st.write("---")
            st.subheader("Solicitar Material al Pañol")
            with st.form("form_solicitud_alumno", clear_on_submit=True):
                nombre_alumno = st.text_input("Nombre y Apellido del Alumno:")
                cant_solicitada = st.number_input("Cantidad requerida:", min_value=1, max_value=prod_obj["cantidad"], value=1)
                btn_enviar = st.form_submit_button("Enviar Solicitud")

                if btn_enviar:
                    if not nombre_alumno.strip():
                        st.error("Por favor ingresa tu nombre antes de enviar.")
                    else:
                        crear_pedido(nombre_alumno.strip(), prod_obj["nombre"], cant_solicitada)
                        st.success("¡Solicitud enviada con éxito! Espera la llamada del pañolero.")
                        st.rerun()


# ==============================================================================
# 4. INTERFAZ PRINCIPAL - PANEL DE PROFESOR
# ==============================================================================
if st.session_state.rol == "Profesor":
    st.write("---")
    st.header("🛠️ Panel de Control Docente")

    tab_pedidos, tab_stock, tab_nuevo = st.tabs([
        "📋 Solicitudes Pendientes", 
        "📊 Gestionar Stock", 
        "➕ Agregar Nuevo Material"
    ])

    # --- PESTAÑA 1: SOLICITUDES ---
    with tab_pedidos:
        st.subheader("Solicitudes de Alumnos")
        pedidos_totales = obtener_pedidos()
        pedidos_pendientes = [p for p in pedidos_totales if p["estado"] == "Pendiente"]

        if not pedidos_pendientes:
            st.info("No hay solicitudes pendientes en este momento.")
        else:
            for pedido in pedidos_pendientes:
                c_info, c_ok, c_cancel = st.columns([3, 1, 1])
                c_info.write(f"👤 **{pedido['alumno']}** solicita: **{pedido['cantidad']}x {pedido['producto']}**")

                if c_ok.button("✅ Aceptar", key=f"ok_{pedido['id']}"):
                    if aprobar_pedido(pedido['id']):
                        st.success(f"Pedido de {pedido['alumno']} aprobado y stock actualizado.")
                    else:
                        st.error("No se pudo aprobar (stock insuficiente).")
                    st.rerun()

                if c_cancel.button("❌ Rechazar", key=f"cancel_{pedido['id']}"):
                    rechazar_pedido(pedido['id'])
                    st.warning(f"Pedido de {pedido['alumno']} rechazado.")
                    st.rerun()

    # --- PESTAÑA 2: GESTIÓN DE STOCK ---
    with tab_stock:
        st.subheader("Inventario General")
        if inventario_actual:
            st.dataframe(inventario_actual, use_container_width=True)

            st.write("### Actualizar Cantidad en Pañol")
            todos_los_nombres = [p["nombre"] for p in inventario_actual]
            prod_a_editar = st.selectbox("Seleccionar componente a modificar:", todos_los_nombres)
            
            prod_editar_obj = next(p for p in inventario_actual if p["nombre"] == prod_a_editar)
            nueva_cant_stock = st.number_input("Nueva cantidad total:", min_value=0, value=prod_editar_obj["cantidad"])

            if st.button("Guardar Cambios de Stock"):
                modificar_stock(prod_a_editar, nueva_cant_stock)
                st.success(f"Stock de '{prod_a_editar}' modificado correctamente.")
                st.rerun()

    # --- PESTAÑA 3: ALTA DE MATERIAL ---
    with tab_nuevo:
        st.subheader("Dar de Alta un Componente Nuevo")
        with st.form("form_alta_material", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre del Componente:")
            nueva_categoria = st.text_input("Categoría:")
            cant_inicial = st.number_input("Cantidad Inicial:", min_value=1, value=5)
            min_alerta = st.number_input("Stock Mínimo para Alerta:", min_value=1, value=2)

            btn_crear_mat = st.form_submit_button("Guardar Componente")

            if btn_crear_mat:
                if nuevo_nombre.strip() and nueva_categoria.strip():
                    crear_material(
                        nuevo_nombre.strip(), 
                        nueva_categoria.strip().capitalize(), 
                        cant_inicial, 
                        min_alerta
                    )
                    st.success(f"¡Componente '{nuevo_nombre}' agregado al catálogo con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor completa el nombre y la categoría.")