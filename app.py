import streamlit as st

st.set_page_config(page_title="Pañol de Mecatrónica", page_icon="⚙️", layout="wide")

# ==============================================================================
# 1. CAPA DE DATOS (ADAPTADA AL ESQUEMA EXACTO DE SUPABASE)
# ==============================================================================

conn = st.connection("sql", type="sql")

def obtener_inventario():
    """Consulta componentes uniendo la tabla de categorías"""
    try:
        sql = """
            SELECT 
                c.id, 
                c.nombre, 
                COALESCE(cat.nombre, 'Sin Categoría') AS categoria, 
                c.cantidad, 
                c.stock_minimo AS minimo 
            FROM public.componentes c 
            LEFT JOIN public.categorias cat ON c.categoria_id = cat.id 
            ORDER BY c.id ASC;
        """
        df = conn.query(sql, ttl=0)
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Error al obtener el inventario: {e}")
        return []

def obtener_pedidos():
    """Consulta pedidos uniendo alumnos, usuarios, detalles, componentes y estados"""
    try:
        sql = """
            SELECT 
                p.id AS pedido_id, 
                CONCAT(u.nombre, ' ', u.apellido) AS alumno, 
                comp.nombre AS producto, 
                pd.cantidad, 
                e.nombre AS estado,
                pd.componente_id
            FROM public.pedidos p
            JOIN public.alumnos a ON p.alumno_id = a.id
            JOIN public.usuarios u ON a.usuario_id = u.id
            JOIN public.pedido_detalle pd ON pd.pedido_id = p.id
            JOIN public.componentes comp ON pd.componente_id = comp.id
            JOIN public.estado e ON p.estado_id = e.id
            ORDER BY p.id DESC;
        """
        df = conn.query(sql, ttl=0)
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Error al obtener pedidos: {e}")
        return []

def crear_pedido(nombre_completo, componente_id, cantidad):
    """Crea el alumno/usuario temporal si no existe, luego el pedido y su detalle"""
    with conn.session as session:
        # 1. Obtener ID del estado 'Pendiente'
        res_estado = session.execute("SELECT id FROM public.estado WHERE nombre = 'Pendiente';").fetchone()
        if not res_estado:
            st.error("No se encontró el estado 'Pendiente' en la base de datos.")
            return
        estado_id = res_estado[0]

        # 2. Separar nombre y apellido
        partes = nombre_completo.strip().split(" ", 1)
        nombre = partes[0]
        apellido = partes[1] if len(partes) > 1 else ""
        email_fake = f"{nombre.lower()}.{apellido.lower()}@escuela.edu"

        # 3. Buscar o crear Usuario y Alumno
        res_user = session.execute(
            "SELECT a.id FROM public.alumnos a JOIN public.usuarios u ON a.usuario_id = u.id WHERE u.nombre = :nom AND u.apellido = :ape;",
            {"nom": nombre, "ape": apellido}
        ).fetchone()

        if res_user:
            alumno_id = res_user[0]
        else:
            # Crear usuario
            res_ins_u = session.execute(
                "INSERT INTO public.usuarios (nombre, apellido, email) VALUES (:nom, :ape, :email) RETURNING id;",
                {"nom": nombre, "ape": apellido, "email": email_fake}
            ).fetchone()
            usuario_id = res_ins_u[0]

            # Crear alumno
            res_ins_a = session.execute(
                "INSERT INTO public.alumnos (usuario_id, curso) VALUES (:uid, 'Mecatrónica') RETURNING id;",
                {"uid": usuario_id}
            ).fetchone()
            alumno_id = res_ins_a[0]

        # 4. Insertar la cabecera del Pedido
        res_ped = session.execute(
            "INSERT INTO public.pedidos (alumno_id, estado_id) VALUES (:aid, :eid) RETURNING id;",
            {"aid": alumno_id, "eid": estado_id}
        ).fetchone()
        pedido_id = res_ped[0]

        # 5. Insertar el Detalle del Pedido
        session.execute(
            "INSERT INTO public.pedido_detalle (pedido_id, componente_id, cantidad) VALUES (:pid, :cid, :cant);",
            {"pid": pedido_id, "cid": componente_id, "cant": cantidad}
        )
        session.commit()

def aprobar_pedido(pedido_id, componente_id, cantidad):
    """Descuenta stock del componente y pasa el pedido a estado 'Aceptado'"""
    with conn.session as session:
        res_estado = session.execute("SELECT id FROM public.estado WHERE nombre = 'Aceptado';").fetchone()
        if res_estado:
            estado_id = res_estado[0]
            # Restar stock
            session.execute(
                "UPDATE public.componentes SET cantidad = cantidad - :cant WHERE id = :cid AND cantidad >= :cant;",
                {"cant": cantidad, "cid": componente_id}
            )
            # Cambiar estado
            session.execute(
                "UPDATE public.pedidos SET estado_id = :eid WHERE id = :pid;",
                {"eid": estado_id, "pid": pedido_id}
            )
            session.commit()

def rechazar_pedido(pedido_id):
    """Pasa el pedido a estado 'Rechazado'"""
    with conn.session as session:
        res_estado = session.execute("SELECT id FROM public.estado WHERE nombre = 'Rechazado';").fetchone()
        if res_estado:
            estado_id = res_estado[0]
            session.execute(
                "UPDATE public.pedidos SET estado_id = :eid WHERE id = :pid;",
                {"eid": estado_id, "pid": pedido_id}
            )
            session.commit()

def modificar_stock(componente_id, nueva_cantidad):
    """Actualiza la cantidad en la tabla componentes"""
    with conn.session as session:
        session.execute(
            "UPDATE public.componentes SET cantidad = :cant WHERE id = :cid;",
            {"cant": nueva_cantidad, "cid": componente_id}
        )
        session.commit()

def crear_material(nombre, categoria_nombre, cantidad, stock_minimo):
    """Crea la categoría si no existe y luego el componente"""
    with conn.session as session:
        # Buscar o crear categoría
        res_cat = session.execute(
            "SELECT id FROM public.categorias WHERE LOWER(nombre) = LOWER(:cat);",
            {"cat": categoria_nombre}
        ).fetchone()

        if res_cat:
            categoria_id = res_cat[0]
        else:
            res_ins_cat = session.execute(
                "INSERT INTO public.categorias (nombre) VALUES (:cat) RETURNING id;",
                {"cat": categoria_nombre}
            ).fetchone()
            categoria_id = res_ins_cat[0]

        # Insertar componente
        session.execute(
            "INSERT INTO public.componentes (nombre, categoria_id, cantidad, stock_minimo) VALUES (:nom, :cat_id, :cant, :min);",
            {"nom": nombre, "cat_id": categoria_id, "cant": cantidad, "min": stock_minimo}
        )
        session.commit()


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
    st.info("No se encontraron materiales cargados en la base de datos.")
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

    prod_obj = next((p for p in productos_filtrados if p["nombre"] == prod_sel), productos_filtrados[0] if productos_filtrados else None)

    if prod_obj:
        st.subheader("Estado de Disponibilidad:")
        if prod_obj["cantidad"] == 0:
            st.error(f"❌ AGOTADO - No hay {prod_obj['nombre']} disponible en este momento.")
        elif prod_obj["cantidad"] <= prod_obj["minimo"]:
            st.warning(f"⚠️ POCO STOCK - Quedan solo {prod_obj['cantidad']} unidad(es) de {prod_obj['nombre']}.")
        else:
            st.success(f"✅ DISPONIBLE - Hay {prod_obj['cantidad']} unidad(es) de {prod_obj['nombre']}.")

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
                        crear_pedido(nombre_alumno.strip(), prod_obj["id"], cant_solicitada)
                        st.success("¡Solicitud enviada con éxito! Revisa en el mostrador del pañol.")
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

                if c_ok.button("✅ Aceptar", key=f"ok_{pedido['pedido_id']}"):
                    aprobar_pedido(pedido['pedido_id'], pedido['componente_id'], pedido['cantidad'])
                    st.success(f"Pedido de {pedido['alumno']} aprobado.")
                    st.rerun()

                if c_cancel.button("❌ Rechazar", key=f"cancel_{pedido['pedido_id']}"):
                    rechazar_pedido(pedido['pedido_id'])
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
            nueva_cant_stock = st.number_input("Nueva cantidad total en pañol:", min_value=0, value=prod_editar_obj["cantidad"])

            if st.button("Guardar Cambios de Stock"):
                modificar_stock(prod_editar_obj["id"], nueva_cant_stock)
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

            btn_crear_mat = st.form_submit_button("Guardar Componente en Supabase")

            if btn_crear_mat:
                if nuevo_nombre.strip() and nueva_categoria.strip():
                    crear_material(
                        nuevo_nombre.strip(), 
                        nueva_categoria.strip().capitalize(), 
                        cant_inicial, 
                        min_alerta
                    )
                    st.success(f"¡Componente '{nuevo_nombre}' guardado en Supabase con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor completa el nombre y la categoría.")
