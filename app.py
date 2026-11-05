import os
from datetime import datetime
from pathlib import Path


import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


# ------------------------------------------------------------
# CONFIGURACION Y CONEXION
# ------------------------------------------------------------
load_dotenv()


st.set_page_config(
    page_title="Pañol de Mecatrónica | ORT",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
CLAVE_MAESTRA_ADMIN = os.getenv("CLAVE_MAESTRA_ADMIN")


def crear_cliente():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def crear_cliente_admin():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return None


    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


# Un cliente por sesión de Streamlit: evita compartir la sesión Auth
# de un alumno/profesor con otro usuario.
if "supabase_client" not in st.session_state:
    st.session_state["supabase_client"] = crear_cliente()
supabase = st.session_state["supabase_client"]


# ------------------------------------------------------------
# ESTILO VISUAL - inspirado en interfaces limpias tipo Apple
# ------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp { background: #f5f5f7; color: #1d1d1f; }
[data-testid="stHeader"] { background: rgba(245,245,247,.82); }
.block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 4rem; }
section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8e8ed; }
.hero {
    background: linear-gradient(125deg, #111827 0%, #172554 55%, #2563eb 100%);
    padding: 2.2rem 2.4rem; border-radius: 25px; color: white;
    box-shadow: 0 16px 40px rgba(20,40,90,.14); margin-bottom: 1.5rem;
}
.hero-kicker { color: #bfdbfe; font-size: .78rem; letter-spacing: .14em; font-weight: 700; text-transform: uppercase; }
.hero h1 { color: white; font-size: clamp(2rem, 4vw, 3rem); line-height: 1.08; margin: .5rem 0; font-weight: 800; }
.hero p { color: #dbeafe; font-size: 1rem; margin: .4rem 0 0 0; }
.eyebrow { color: #6e6e73; font-size: .76rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; }
.section-title { color: #1d1d1f; font-size: 1.55rem; font-weight: 750; margin: .1rem 0 .2rem 0; }
.muted { color: #6e6e73; }
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e8e8ed; border-radius: 18px;
    padding: 1rem 1.1rem; box-shadow: 0 4px 16px rgba(0,0,0,.025);
}
div[data-testid="stMetricLabel"] { color: #6e6e73; }
div[data-testid="stMetricValue"] { color: #1d1d1f; font-weight: 750; }
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    border-radius: 12px; font-weight: 650; min-height: 2.7rem;
}
div[data-testid="stTabs"] button { font-weight: 650; }
div[data-testid="stExpander"] { background: white; border: 1px solid #e8e8ed; border-radius: 16px; }
div[data-testid="stForm"] { background: white; border: 1px solid #e8e8ed; border-radius: 18px; padding: 1.2rem; }
div[data-testid="stAlert"] { border-radius: 14px; }
.small-note { color: #86868b; font-size: .82rem; }
hr { border-color: #e8e8ed; }
</style>
""", unsafe_allow_html=True)




def mostrar_encabezado(subtitulo="Gestión inteligente de materiales y componentes"):
    logo = Path(__file__).parent / "logo_ort.png"
    c1, c2 = st.columns([1, 5], vertical_alignment="center")
    with c1:
        if logo.exists():
            st.image(str(logo), width=130)
        else:
            st.markdown("## ⚙️ ORT")
    with c2:
        st.markdown(
            f"""<div class="hero">
            <div class="hero-kicker">Escuela ORT · Mecatrónica</div>
            <h1>Pañol de materiales</h1>
            <p>{subtitulo}</p>
            </div>""",
            unsafe_allow_html=True,
        )




def error_db(exc, accion="realizar la operación"):
    st.error(f"No se pudo {accion}.")
    with st.expander("Ver detalle técnico"):
        st.code(str(exc))




def consultar_uno(tabla, columnas, columna, valor):
    respuesta = supabase.table(tabla).select(columnas).eq(columna, valor).limit(1).execute()
    return respuesta.data[0] if respuesta.data else None




def obtener_perfil(user_id):
    usuario = consultar_uno("usuarios", "id,nombre,apellido,email", "id", user_id)
    alumno = consultar_uno("alumnos", "id,curso", "usuario_id", user_id)
    profesor = consultar_uno("profesores", "id,materia", "usuario_id", user_id)
    if profesor:
        return {"rol": "profesor", "usuario": usuario or {}, "perfil": profesor}
    if alumno:
        return {"rol": "alumno", "usuario": usuario or {}, "perfil": alumno}
    return None


def registrar_usuario(rol, nombre, apellido, email, password, dato_extra):
    email = email.strip().lower()


    if rol == "alumno":
        # Registro público normal: Supabase crea la cuenta.
        # El trigger SQL crea automáticamente usuarios y alumnos.
        resultado = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "nombre": nombre.strip(),
                    "apellido": apellido.strip(),
                    "curso": dato_extra.strip(),
                }
            }
        })


    elif rol == "profesor":
        # Registro administrativo: requiere la clave secreta del servidor.
        cliente_admin = crear_cliente_admin()


        if cliente_admin is None:
            raise Exception(
                "Falta configurar SUPABASE_SECRET_KEY en el archivo .env."
            )


        resultado = cliente_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "user_metadata": {
                "nombre": nombre.strip(),
                "apellido": apellido.strip(),
                "materia": dato_extra.strip(),
            },
            "app_metadata": {
                "rol": "profesor"
            }
        })


    else:
        raise Exception("Rol de usuario no válido.")


    return resultado


def cerrar_sesion():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for key in ("user", "perfil"):
        st.session_state.pop(key, None)
    st.rerun()




def iniciar_sesion():
    mostrar_encabezado(
        "Ingresá o creá tu cuenta para consultar y administrar el pañol."
    )


    _, centro, _ = st.columns([1, 1.4, 1])


    with centro:
        tab_login, tab_registro = st.tabs([
            "Iniciar sesión",
            "Crear cuenta"
        ])


        # ------------------------------------------------
        # INICIAR SESIÓN
        # ------------------------------------------------
        with tab_login:
            st.markdown(
                '<div class="section-title">Bienvenido</div>',
                unsafe_allow_html=True
            )
            st.write("Usá tu correo y contraseña para continuar.")


            with st.form("login_form"):
                email = st.text_input(
                    "Correo electrónico",
                    placeholder="nombre@ort.edu.ar"
                )
                password = st.text_input(
                    "Contraseña",
                    type="password"
                )


                entrar = st.form_submit_button(
                    "Iniciar sesión",
                    type="primary",
                    use_container_width=True
                )


            if entrar:
                if not email.strip() or not password:
                    st.warning("Completá el correo y la contraseña.")
                else:
                    try:
                        result = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })


                        user = result.user
                        perfil = obtener_perfil(user.id)


                        if not perfil:
                            supabase.auth.sign_out()
                            st.error(
                                "La cuenta inició sesión, pero no está "
                                "vinculada a un alumno o profesor."
                            )
                        else:
                            st.session_state["user"] = {
                                "id": user.id,
                                "email": user.email
                            }
                            st.session_state["perfil"] = perfil
                            st.rerun()


                    except Exception as exc:
                        st.error(
                            "No se pudo iniciar sesión. "
                            "Revisá el correo y la contraseña."
                        )
                        with st.expander("Detalle técnico"):
                            st.code(str(exc))


        # ------------------------------------------------
        # REGISTRARSE
        # ------------------------------------------------
        with tab_registro:
            st.markdown(
                '<div class="section-title">Crear una cuenta</div>',
                unsafe_allow_html=True
            )
            st.write("Completá tus datos para registrarte.")


            rol = st.radio(
                "Tipo de cuenta",
                ["Alumno", "Profesor"],
                horizontal=True,
                key="tipo_registro"
            )


            es_profesor = rol == "Profesor"


            with st.form("registro_form"):
                nombre = st.text_input("Nombre")
                apellido = st.text_input("Apellido")


                email_registro = st.text_input(
                    "Correo electrónico",
                    placeholder="nombre@ort.edu.ar"
                )


                if es_profesor:
                    dato_extra = st.text_input(
                        "Materia o área"
                    )
                    clave_admin = st.text_input(
                        "Clave de registro de profesor",
                        type="password"
                    )
                else:
                    dato_extra = st.text_input(
                        "Curso",
                        placeholder="Ej. 6° Informática"
                    )
                    clave_admin = ""


                password_registro = st.text_input(
                    "Contraseña",
                    type="password"
                )


                confirmar_password = st.text_input(
                    "Confirmar contraseña",
                    type="password"
                )


                registrar = st.form_submit_button(
                    "Crear cuenta",
                    type="primary",
                    use_container_width=True
                )


            if registrar:
                if not all([
                    nombre.strip(),
                    apellido.strip(),
                    email_registro.strip(),
                    dato_extra.strip(),
                    password_registro,
                    confirmar_password
                ]):
                    st.warning("Completá todos los campos.")


                elif "@" not in email_registro:
                    st.warning("Ingresá un correo electrónico válido.")


                elif len(password_registro) < 8:
                    st.warning(
                        "La contraseña debe tener al menos 8 caracteres."
                    )


                elif password_registro != confirmar_password:
                    st.error("Las contraseñas no coinciden.")


                elif es_profesor and not CLAVE_MAESTRA_ADMIN:
                    st.error(
                        "No está configurada la clave administrativa "
                        "en el servidor."
                    )


                elif es_profesor and clave_admin != CLAVE_MAESTRA_ADMIN:
                    st.error("La clave de registro de profesor es incorrecta.")


                else:
                    try:
                        registrar_usuario(
                            rol="profesor" if es_profesor else "alumno",
                            nombre=nombre,
                            apellido=apellido,
                            email=email_registro,
                            password=password_registro,
                            dato_extra=dato_extra
                        )


                        st.success(
                            "¡Cuenta creada correctamente! "
                            "Ahora podés iniciar sesión."
                        )


                        st.info(
                            "Si Supabase tiene habilitada la confirmación "
                            "por correo, primero revisá tu bandeja de entrada "
                            "y confirmá tu dirección."
                        )


                    except Exception as exc:
                        st.error(
                            "No se pudo crear la cuenta. "
                            "Revisá los datos o consultá el detalle técnico."
                        )
                        with st.expander("Detalle técnico"):
                            st.code(str(exc))


def cargar_inventario():
    return (
        supabase.table("componentes")
        .select("id,nombre,descripcion,categoria_id,cantidad,stock_minimo,ubicacion,categorias(nombre)")
        .order("nombre")
        .execute()
        .data
    )




def cargar_categorias():
    return supabase.table("categorias").select("id,nombre").order("nombre").execute().data




def nombre_categoria(item):
    relacion = item.get("categorias")
    if isinstance(relacion, dict):
        return relacion.get("nombre", "Sin categoría")
    if isinstance(relacion, list) and relacion:
        return relacion[0].get("nombre", "Sin categoría")
    return "Sin categoría"




def cargar_pedidos_alumno(alumno_id):
    return (
        supabase.table("pedidos")
        .select("id,fecha,estado_id,estados(nombre),pedido_detalle(cantidad,componentes(nombre))")
        .eq("alumno_id", alumno_id)
        .order("fecha", desc=True)
        .execute()
        .data
    )




def cargar_pedidos_profesor():
    return (
        supabase.table("pedidos")
        .select("id,fecha,estado_id,alumno_id,profesor_id,estados(nombre),alumnos(curso,usuarios(nombre,apellido,email)),pedido_detalle(cantidad,componentes(nombre))")
        .order("fecha", desc=True)
        .execute()
        .data
    )




def texto_detalle(pedido):
    partes = []
    for detalle in pedido.get("pedido_detalle", []) or []:
        comp = detalle.get("componentes") or {}
        if isinstance(comp, list):
            comp = comp[0] if comp else {}
        partes.append(f"{comp.get('nombre', 'Componente')} × {detalle.get('cantidad', 0)}")
    return ", ".join(partes) or "Sin detalle"




def estado_nombre(pedido):
    estado = pedido.get("estados") or {}
    if isinstance(estado, list):
        estado = estado[0] if estado else {}
    return estado.get("nombre", "sin estado").capitalize()




def panel_alumno(perfil):
    st.markdown('<div class="eyebrow">Área del alumno</div><div class="section-title">Tu espacio de materiales</div>', unsafe_allow_html=True)
    nombre = f"{perfil['usuario'].get('nombre', '')} {perfil['usuario'].get('apellido', '')}".strip() or st.session_state["user"]["email"]
    st.caption(f"{nombre} · Curso {perfil['perfil'].get('curso', 'No indicado')}")
    try:
        inventario = cargar_inventario()
        categorias = cargar_categorias()
        pedidos = cargar_pedidos_alumno(perfil["perfil"]["id"])
    except Exception as exc:
        error_db(exc, "cargar los datos desde Supabase")
        return


    total = len(inventario)
    disponibles = sum(1 for x in inventario if (x.get("cantidad") or 0) > 0)
    bajo_stock = sum(1 for x in inventario if (x.get("cantidad") or 0) <= (x.get("stock_minimo") or 0))
    m1, m2, m3 = st.columns(3)
    m1.metric("Componentes registrados", total)
    m2.metric("Con disponibilidad", disponibles)
    m3.metric("En nivel mínimo", bajo_stock)


    tab_inv, tab_pedir, tab_mios = st.tabs(["  Inventario  ", "  Solicitar material  ", "  Mis solicitudes  "])


    with tab_inv:
        st.markdown("#### Explorar inventario")
        c1, c2 = st.columns([2, 1])
        busqueda = c1.text_input("Buscar", placeholder="Ej. Arduino, motor, sensor...")
        opciones = ["Todas"] + [c["nombre"] for c in categorias]
        cat = c2.selectbox("Categoría", opciones)
        filtrados = inventario
        if cat != "Todas":
            categoria_id = next((c["id"] for c in categorias if c["nombre"] == cat), None)
            filtrados = [x for x in filtrados if x.get("categoria_id") == categoria_id]
        if busqueda:
            filtrados = [x for x in filtrados if busqueda.casefold() in (x.get("nombre") or "").casefold() or busqueda.casefold() in (x.get("descripcion") or "").casefold()]
        if not filtrados:
            st.info("No hay componentes que coincidan con la búsqueda.")
        else:
            for item in filtrados:
                cantidad = item.get("cantidad") or 0
                minimo = item.get("stock_minimo") or 0
                with st.container(border=True):
                    a, b, c = st.columns([3, 1.3, 1.2], vertical_alignment="center")
                    a.markdown(f"**{item['nombre']}**")
                    a.caption(f"{item.get('descripcion') or 'Sin descripción'} · {nombre_categoria(item)}")
                    a.caption(f"Ubicación: {item.get('ubicacion') or 'No asignada'}")
                    b.metric("Disponibles", cantidad)
                    if cantidad == 0:
                        c.error("Sin stock")
                    elif cantidad <= minimo:
                        c.warning("Stock bajo")
                    else:
                        c.success("Disponible")


    with tab_pedir:
        st.markdown("#### Nueva solicitud")
        disponibles_items = [x for x in inventario if (x.get("cantidad") or 0) > 0]
        if not disponibles_items:
            st.info("En este momento no hay materiales con stock.")
        else:
            opciones_material = {f"{x['nombre']} · {x.get('cantidad', 0)} disponibles": x for x in disponibles_items}
            with st.form("crear_pedido_form"):
                elegido = st.selectbox("Material", list(opciones_material.keys()))
                material = opciones_material[elegido]
                st.caption(f"Categoría: {nombre_categoria(material)} · Ubicación: {material.get('ubicacion') or 'No asignada'}")
                cantidad = st.number_input("Cantidad solicitada", min_value=1, max_value=max(1, int(material.get("cantidad") or 1)), value=1, step=1)
                motivo = st.text_area("¿Para qué clase o proyecto lo necesitás?", placeholder="Contanos brevemente el uso...")
                enviar = st.form_submit_button("Enviar solicitud", type="primary", use_container_width=True)
            if enviar:
                try:
                    supabase.rpc("crear_pedido", {
                        "p_componente_id": material["id"],
                        "p_cantidad": int(cantidad),
                        "p_observaciones": motivo.strip() or None,
                    }).execute()
                    st.success("Solicitud registrada. Podés seguir su estado en «Mis solicitudes».")
                    st.rerun()
                except Exception as exc:
                    error_db(exc, "crear la solicitud")
                    st.caption("La función crear_pedido usa el usuario autenticado para identificar al alumno.")


    with tab_mios:
        st.markdown("#### Seguimiento")
        if not pedidos:
            st.info("Todavía no tenés solicitudes registradas.")
        for pedido in pedidos:
            estado = estado_nombre(pedido)
            with st.container(border=True):
                a, b = st.columns([3, 1])
                a.markdown(f"**Solicitud #{pedido['id']}**")
                a.write(texto_detalle(pedido))
                a.caption(f"Fecha: {pedido.get('fecha', 'No disponible')}")
                if estado == "Pendiente":
                    b.warning(estado)
                elif estado == "Rechazado":
                    b.error(estado)
                elif estado == "Entregado":
                    b.success(estado)
                else:
                    b.info(estado)




def panel_profesor(perfil):
    st.markdown('<div class="eyebrow">Administración</div><div class="section-title">Panel del pañol</div>', unsafe_allow_html=True)
    nombre = f"{perfil['usuario'].get('nombre', '')} {perfil['usuario'].get('apellido', '')}".strip()
    st.caption(f"{nombre or st.session_state['user']['email']} · Profesor")
    try:
        inventario = cargar_inventario()
        categorias = cargar_categorias()
        pedidos = cargar_pedidos_profesor()
        estados = supabase.table("estados").select("id,nombre").execute().data
    except Exception as exc:
        error_db(exc, "cargar los datos administrativos")
        return


    pendientes = sum(1 for p in pedidos if estado_nombre(p).lower() == "pendiente")
    bajo_stock = sum(1 for x in inventario if (x.get("cantidad") or 0) <= (x.get("stock_minimo") or 0))
    m1, m2, m3 = st.columns(3)
    m1.metric("Componentes", len(inventario))
    m2.metric("Solicitudes pendientes", pendientes)
    m3.metric("Alertas de stock", bajo_stock)


    tab_ped, tab_inv, tab_nuevo, tab_cat = st.tabs(["  Solicitudes  ", "  Inventario  ", "  Agregar componente  ", "  Categorías  "])


    with tab_ped:
        st.markdown("#### Solicitudes de alumnos")
        if not pedidos:
            st.info("Todavía no hay solicitudes.")
        for pedido in pedidos:
            estado = estado_nombre(pedido)
            alumno = pedido.get("alumnos") or {}
            if isinstance(alumno, list):
                alumno = alumno[0] if alumno else {}
            usuario = alumno.get("usuarios") or {}
            if isinstance(usuario, list):
                usuario = usuario[0] if usuario else {}
            alumno_nombre = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or usuario.get("email", "Alumno")
            with st.container(border=True):
                top, status = st.columns([4, 1])
                top.markdown(f"**Solicitud #{pedido['id']} · {texto_detalle(pedido)}**")
                top.caption(f"{alumno_nombre} · Curso {alumno.get('curso', 'No indicado')} · {pedido.get('fecha', '')}")
                if estado == "Pendiente":
                    status.warning(estado)
                elif estado == "Rechazado":
                    status.error(estado)
                elif estado == "Entregado":
                    status.success(estado)
                else:
                    status.info(estado)
                if estado.lower() in ("pendiente", "en proceso", "aprobado"):
                    disponibles_estados = [e for e in estados if e["nombre"] in ("en proceso", "aprobado", "rechazado", "entregado")]
                    etiquetas = {e["nombre"].capitalize(): e["nombre"] for e in disponibles_estados}
                    c1, c2 = st.columns([2, 1])
                    nuevo_estado = c1.selectbox("Actualizar estado", list(etiquetas.keys()), key=f"estado_{pedido['id']}")
                    if c2.button("Guardar estado", key=f"guardar_estado_{pedido['id']}", type="primary", use_container_width=True):
                        try:
                            supabase.rpc("actualizar_estado_pedido", {
                                "p_pedido_id": pedido["id"],
                                "p_nuevo_estado": etiquetas[nuevo_estado].lower(),
                            }).execute()
                            st.success(f"Solicitud #{pedido['id']} actualizada.")
                            st.rerun()
                        except Exception as exc:
                            error_db(exc, "actualizar el estado")
                            st.caption("La entrega descuenta el stock desde Supabase. No se descuenta al crear ni al aprobar el pedido.")


    with tab_inv:
        st.markdown("#### Editar inventario")
        for item in inventario:
            with st.expander(f"{item['nombre']} · {item.get('cantidad', 0)} unidades"):
                with st.form(f"editar_{item['id']}"):
                    c1, c2 = st.columns(2)
                    nombre = c1.text_input("Nombre", value=item["nombre"])
                    categoria_actual = next((c["id"] for c in categorias if c["id"] == item.get("categoria_id")), categorias[0]["id"] if categorias else None)
                    categoria_nombres = {c["nombre"]: c["id"] for c in categorias}
                    categoria_nombre_actual = next((n for n, cid in categoria_nombres.items() if cid == categoria_actual), None)
                    cat_opciones = list(categoria_nombres.keys())
                    cat_idx = cat_opciones.index(categoria_nombre_actual) if categoria_nombre_actual in cat_opciones else 0
                    cat_nombre = c1.selectbox("Categoría", cat_opciones, index=cat_idx) if cat_opciones else None
                    cantidad = c2.number_input("Cantidad actual", min_value=0, value=int(item.get("cantidad") or 0), step=1)
                    minimo = c2.number_input("Stock mínimo", min_value=0, value=int(item.get("stock_minimo") or 0), step=1)
                    ubicacion = c1.text_input("Ubicación", value=item.get("ubicacion") or "")
                    descripcion = c2.text_area("Descripción", value=item.get("descripcion") or "")
                    guardar = st.form_submit_button("Guardar cambios", type="primary")
                if guardar:
                    if not nombre.strip():
                        st.error("El nombre no puede estar vacío.")
                    elif cantidad < 0 or minimo < 0:
                        st.error("Las cantidades no pueden ser negativas.")
                    else:
                        try:
                            supabase.table("componentes").update({
                                "nombre": nombre.strip(),
                                "categoria_id": categoria_nombres.get(cat_nombre) if cat_nombre else None,
                                "cantidad": int(cantidad),
                                "stock_minimo": int(minimo),
                                "ubicacion": ubicacion.strip() or None,
                                "descripcion": descripcion.strip() or None,
                            }).eq("id", item["id"]).execute()
                            st.success("Componente actualizado en Supabase.")
                            st.rerun()
                        except Exception as exc:
                            error_db(exc, "guardar los cambios")


    with tab_nuevo:
        st.markdown("#### Incorporar un componente")
        if not categorias:
            st.warning("Primero creá una categoría.")
        else:
            with st.form("nuevo_componente"):
                nombre = st.text_input("Nombre del componente")
                cat = st.selectbox("Categoría", {c["nombre"]: c["id"] for c in categorias}.keys())
                c1, c2 = st.columns(2)
                cantidad = c1.number_input("Cantidad inicial", min_value=0, value=1, step=1)
                minimo = c2.number_input("Stock mínimo", min_value=0, value=1, step=1)
                ubicacion = st.text_input("Ubicación", placeholder="Ej. Cajón A1")
                descripcion = st.text_area("Descripción")
                crear = st.form_submit_button("Agregar al inventario", type="primary", use_container_width=True)
            if crear:
                if not nombre.strip():
                    st.error("Ingresá el nombre del componente.")
                else:
                    try:
                        cat_id = next(c["id"] for c in categorias if c["nombre"] == cat)
                        supabase.table("componentes").insert({
                            "nombre": nombre.strip(),
                            "descripcion": descripcion.strip() or None,
                            "categoria_id": cat_id,
                            "cantidad": int(cantidad),
                            "stock_minimo": int(minimo),
                            "ubicacion": ubicacion.strip() or None,
                        }).execute()
                        st.success("Componente agregado correctamente.")
                        st.rerun()
                    except Exception as exc:
                        error_db(exc, "agregar el componente")


    with tab_cat:
        st.markdown("#### Administrar categorías")
        for categoria in categorias:
            st.write(f"• {categoria['nombre']}")
        with st.form("nueva_categoria"):
            nueva = st.text_input("Nombre de la nueva categoría")
            descripcion_cat = st.text_input("Descripción (opcional)")
            agregar = st.form_submit_button("Crear categoría", type="primary")
        if agregar:
            if not nueva.strip():
                st.warning("Escribí un nombre para la categoría.")
            else:
                try:
                    supabase.table("categorias").insert({
                        "nombre": nueva.strip(),
                        "descripcion": descripcion_cat.strip() or None,
                    }).execute()
                    st.success("Categoría creada.")
                    st.rerun()
                except Exception as exc:
                    error_db(exc, "crear la categoría")




# ------------------------------------------------------------
# INICIO
# ------------------------------------------------------------
if supabase is None:
    mostrar_encabezado()
    st.error("Falta configurar la conexión con Supabase.")
    st.markdown("Creá un archivo **.env** en la carpeta del proyecto con estas variables:")
    st.code("SUPABASE_URL=https://TU-PROYECTO.supabase.co\nSUPABASE_PUBLISHABLE_KEY=TU_CLAVE_PUBLICABLE")
    st.stop()


if "user" not in st.session_state:
    iniciar_sesion()
    st.stop()


# Confirmar que el perfil todavía corresponde al usuario autenticado.
if "perfil" not in st.session_state:
    try:
        st.session_state["perfil"] = obtener_perfil(st.session_state["user"]["id"])
    except Exception:
        st.session_state["perfil"] = None


if not st.session_state.get("perfil"):
    st.warning("Tu usuario no está asociado a un registro de alumno o profesor.")
    if st.button("Cerrar sesión"):
        cerrar_sesion()
    st.stop()


perfil = st.session_state["perfil"]
with st.sidebar:
    st.markdown("## ⚙️ Pañol ORT")
    st.caption("Mecatrónica")
    st.divider()
    st.markdown(f"**{perfil['usuario'].get('nombre', '')} {perfil['usuario'].get('apellido', '')}**")
    st.caption(st.session_state["user"]["email"])
    st.info("Perfil de profesor" if perfil["rol"] == "profesor" else f"Alumno · {perfil['perfil'].get('curso', '')}")
    if st.button("Cerrar sesión", use_container_width=True):
        cerrar_sesion()
    st.markdown("---")
    st.caption("Inventario centralizado en Supabase")


mostrar_encabezado("Un espacio simple y ordenado para consultar, solicitar y administrar materiales.")
try:
    if perfil["rol"] == "alumno":
        panel_alumno(perfil)
    else:
        panel_profesor(perfil)
except Exception as exc:
    error_db(exc, "mostrar la aplicación")





