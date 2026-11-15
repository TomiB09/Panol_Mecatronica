# Librería externa que permite a Python usar los certificados de seguridad de Windows.
# En redes escolares evita errores de certificado SSL al conectar con Supabase.
import truststore
truststore.inject_into_ssl()


#interactuar con el sistema operativo
import os


#manejar fechas y horas
from datetime import datetime


# Herramienta para manejar rutas de archivos de forma segura en Windows, Mac o Linux.
from pathlib import Path


# Framework principal que convierte este script de Python en una aplicación web interactiva.
import streamlit as st


# Función para cargar variables desde un archivo .env
from dotenv import load_dotenv


#Supabase para consultar la base de datos y gestionar usuarios.
from supabase import create_client


# Intenta cargar variables de entorno desde un archivo .env si existiera en la carpeta.
load_dotenv()


# Configura los metadatos de la pestaña del navegador y el diseño general de la página.
# IMPORTANTE: En Streamlit, st.set_page_config() siempre debe ser la primera instrucción visual ejecutada.
st.set_page_config(
    page_title="Pañol de Mecatrónica | ORT",  # Título que aparece en la pestaña del navegador.
    page_icon="⚙️",                           # Ícono (favicon) de la pestaña.
    layout="wide",                            # Usa todo el ancho disponible de la pantalla en lugar de centrar angosto.
    initial_sidebar_state="expanded",         # Muestra el panel lateral izquierdo abierto por defecto.
)


# Lee las credenciales desde .streamlit/secrets.toml o desde variables de entorno (.env) sin lanzar error si falta el archivo.
def obtener_secreto(clave):
    try:
        valor = st.secrets.get(clave)
        if valor:
            return valor
    except Exception:
        pass
    return os.getenv(clave)


SUPABASE_URL = obtener_secreto("SUPABASE_URL")
SUPABASE_KEY = obtener_secreto("SUPABASE_PUBLISHABLE_KEY")
SUPABASE_SECRET_KEY = obtener_secreto("SUPABASE_SECRET_KEY")
CLAVE_MAESTRA_ADMIN = obtener_secreto("CLAVE_MAESTRA_ADMIN")


# Crea un cliente estándar de Supabase usando la clave pública.
# Este cliente respeta las reglas de seguridad (RLS) de la base de datos según el usuario que inicie sesión.
def crear_cliente():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# Crea un cliente con privilegios de administrador usando la clave secreta.
# Permite crear cuentas directamente en Supabase Auth sin límites de envío de correos.
def crear_cliente_admin():
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


# st.session_state es una memoria privada que Streamlit crea por cada pestaña/usuario conectado.
# Guardamos el cliente de Supabase allí para que la sesión de un alumno no se mezcle con la de otro usuario.
if "supabase_client" not in st.session_state:
    st.session_state["supabase_client"] = crear_cliente()
supabase = st.session_state["supabase_client"]


# Inyecta código CSS directamente en la página web mediante st.markdown
# para personalizar tipografía, colores de fondo, tarjetas, botones y el banner principal.
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
 
# Dibuja el encabezado superior con el logo institucional (si existe) y el banner azul.
def mostrar_encabezado(subtitulo="Gestión inteligente de materiales y componentes"):
    # Construye la ruta al archivo logo_ort.png ubicado en la misma carpeta que este script (__file__).
    logo = Path(__file__).parent / "logo_ort.png"
    # Divide el ancho de pantalla en 2 columnas: la primera ocupa 1 parte y la segunda 5 partes.
    c1, c2 = st.columns([1, 5], vertical_alignment="center")
    with c1:
        if logo.exists():
            st.image(str(logo), width=130)  # Si la imagen existe en la carpeta, la muestra.
        else:
            st.markdown("## ⚙️ ORT")         # Si no existe, muestra un texto alternativo para no dar error.
    with c2:
        # Dibuja la tarjeta degradada azul usando las clases CSS definidas arriba (.hero).
        st.markdown(
            f"""<div class="hero">
            <div class="hero-kicker">Escuela ORT · Mecatrónica</div>
            <h1>Pañol de materiales</h1>
            <p>{subtitulo}</p>
            </div>""",
            unsafe_allow_html=True,
        )


# Muestra un mensaje de error amigable en pantalla y oculta el error técnico real dentro de un desplegable.
def error_db(exc, accion="realizar la operación"):
    st.error(f"No se pudo {accion}.")
    with st.expander("Ver detalle técnico"):
        st.code(str(exc))


# Función genérica para buscar un único registro en cualquier tabla de Supabase.
# Equivale en SQL a: SELECT columnas FROM tabla WHERE columna = valor LIMIT 1;
def consultar_uno(tabla, columnas, columna, valor):
    respuesta = supabase.table(tabla).select(columnas).eq(columna, valor).limit(1).execute()
    # Devuelve el primer diccionario encontrado, o None si la lista está vacía.
    return respuesta.data[0] if respuesta.data else None


# Dado el UUID de un usuario autenticado, busca sus datos personales y determina si es profesor o alumno.
def obtener_perfil(user_id):
    usuario = consultar_uno("usuarios", "id,nombre,apellido,email", "id", user_id)
    alumno = consultar_uno("alumnos", "id,curso", "usuario_id", user_id)
    profesor = consultar_uno("profesores", "id,materia", "usuario_id", user_id)
    if profesor:
        return {"rol": "profesor", "usuario": usuario or {}, "perfil": profesor}
    if alumno:
        return {"rol": "alumno", "usuario": usuario or {}, "perfil": alumno}
    return None


#En esta versión con interfaz, un Trigger configurado dentro de PostgreSQL en Supabase
# escucha el alta en Auth y crea automáticamente las filas en 'usuarios' y 'alumnos'/'profesores'.
def registrar_usuario(rol, nombre, apellido, email, password, dato_extra):
    email = email.strip().lower()
    # Se usa el cliente administrador con "email_confirm": True (igual que en main_2.py)
    # para crear cuentas ilimitadas sin enviar correos y evitar el error "email rate limit exceeded".
    cliente_admin = crear_cliente_admin()
    if cliente_admin is None:
        raise Exception(
            "Falta configurar SUPABASE_SECRET_KEY en el archivo .streamlit/secrets.toml."
        )


    if rol == "alumno":
        resultado = cliente_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "rol": "alumno",
                "nombre": nombre.strip(),
                "apellido": apellido.strip(),
                "curso": dato_extra.strip(),
            }
        })
    elif rol == "profesor":
        # Se envía 'rol' tanto en user_metadata como en app_metadata.
        resultado = cliente_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "rol": "profesor",
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


    # Garantiza que el usuario quede en 'profesores' o 'alumnos' según el rol elegido,
    # corrigiendo si el Trigger SQL de Supabase lo insertó por defecto en 'alumnos'.
    user_id = resultado.user.id if resultado and resultado.user else None
    if user_id:
        existe_usuario = cliente_admin.table("usuarios").select("id").eq("id", user_id).execute().data
        if not existe_usuario:
            cliente_admin.table("usuarios").insert({
                "id": user_id,
                "nombre": nombre.strip(),
                "apellido": apellido.strip(),
                "email": email,
            }).execute()


        if rol == "profesor":
            cliente_admin.table("alumnos").delete().eq("usuario_id", user_id).execute()
            existe_prof = cliente_admin.table("profesores").select("id").eq("usuario_id", user_id).execute().data
            if not existe_prof:
                cliente_admin.table("profesores").insert({
                    "usuario_id": user_id,
                    "materia": dato_extra.strip(),
                }).execute()
        else:
            existe_alum = cliente_admin.table("alumnos").select("id").eq("usuario_id", user_id).execute().data
            if not existe_alum:
                cliente_admin.table("alumnos").insert({
                    "usuario_id": user_id,
                    "curso": dato_extra.strip(),
                }).execute()


    return resultado


# Callback que se ejecuta inmediatamente al presionar "Eliminar componente" (antes de redibujar la interfaz).
# Verifica la confirmación, revisa que no pertenezca a ningún pedido y lo elimina definitivamente de Supabase.
def eliminar_componente_callback(comp_id, comp_nombre):
    if not st.session_state.get(f"confirmar_eliminar_{comp_id}", False):
        st.session_state["feedback_inv"] = (
            "warning",
            f"Marcá la casilla de confirmación antes de eliminar «{comp_nombre}»."
        )
        return


    try:
        # Usa el cliente administrador para evitar que políticas RLS bloqueen consultas o borrados.
        cliente_db = crear_cliente_admin() or supabase


        # Revisa que el componente no esté en un pedido para que no quede fantasma y cause error.
        en_pedidos = (
            cliente_db.table("pedido_detalle")
            .select("id,pedido_id")
            .eq("componente_id", comp_id)
            .execute()
            .data
        )
        if en_pedidos:
            st.session_state["feedback_inv"] = (
                "error",
                f"No se puede eliminar «{comp_nombre}» porque pertenece a {len(en_pedidos)} pedido(s) registrado(s)."
            )
            return


        # Ejecuta DELETE en la tabla 'componentes' filtrando por el id del ítem.
        respuesta = cliente_db.table("componentes").delete().eq("id", comp_id).execute()


        # Verifica que Supabase realmente haya eliminado la fila.
        if not respuesta.data:
            st.session_state["feedback_inv"] = (
                "error",
                f"Supabase no eliminó «{comp_nombre}». Verificá SUPABASE_SECRET_KEY en secrets.toml."
            )
            return


        st.session_state.pop(f"confirmar_eliminar_{comp_id}", None)
        st.session_state["feedback_inv"] = (
            "success",
            f"Componente «{comp_nombre}» eliminado correctamente de Supabase."
        )
    except Exception as exc:
        st.session_state["feedback_inv"] = (
            "error",
            f"No se pudo eliminar «{comp_nombre}»: {exc}"
        )


# Cierra la sesión en Supabase, borra los datos del usuario de la memoria de Streamlit y recarga la página.
def cerrar_sesion():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    # Elimina 'user' y 'perfil' de st.session_state sin dar error si ya no existían.
    for key in ("user", "perfil"):
        st.session_state.pop(key, None)
    # Fuerza a Streamlit a volver a ejecutar el script desde arriba (mostrará la pantalla de login).
    st.rerun()


# Renderiza la pantalla completa de acceso con dos pestañas: "Iniciar sesión" y "Crear cuenta".
def iniciar_sesion():
    mostrar_encabezado(
        "Ingresá o creá tu cuenta para consultar y administrar el pañol."
    )
    # Crea 3 columnas para centrar la caja de login en el medio de la pantalla.
    _, centro, _ = st.columns([1, 1.4, 1])
    with centro:
        tab_login, tab_registro = st.tabs([
            "Iniciar sesión",
            "Crear cuenta"
        ])


        with tab_login:
            st.markdown(
                '<div class="section-title">Bienvenido</div>',
                unsafe_allow_html=True
            )
            st.write("Usá tu correo y contraseña para continuar.")
            # st.form() agrupa los campos para que la página no se recargue cada vez que escribes una letra.
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


            # Este bloque solo se ejecuta cuando el usuario presiona el botón "Iniciar sesión".
            if entrar:
                if not email.strip() or not password:
                    st.warning("Completá el correo y la contraseña.")
                else:
                    try:
                        # Valida email y contraseña contra Supabase Auth.
                        result = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })
                        user = result.user
                        # Busca el perfil asociado en las tablas 'usuarios', 'alumnos' o 'profesores'.
                        perfil = obtener_perfil(user.id)
                        if not perfil:
                            # Si existe en Auth pero no tiene fila en alumnos/profesores, cierra sesión por seguridad.
                            supabase.auth.sign_out()
                            st.error(
                                "La cuenta inició sesión, pero no está "
                                "vinculada a un alumno o profesor."
                            )
                        else:
                            # Guarda usuario y perfil en la memoria de sesión y recarga la web para entrar al panel.
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


        with tab_registro:
            st.markdown(
                '<div class="section-title">Crear una cuenta</div>',
                unsafe_allow_html=True
            )
            st.write("Completá tus datos para registrarte.")
            # El selector de rol va FUERA del st.form() para que al cambiar entre Alumno y Profesor
            # la pantalla se actualice al instante mostrando "Curso" o "Materia + Clave maestra".
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


            # Validaciones de formulario al presionar "Crear cuenta".
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
                    except Exception as exc:
                        st.error(
                            "No se pudo crear la cuenta. "
                            "Revisá los datos o consultá el detalle técnico."
                        )
                        with st.expander("Detalle técnico"):
                            st.code(str(exc))


# Trae todos los componentes ordenados alfabéticamente junto con el nombre de su categoría (JOIN).
def cargar_inventario():
    return (
        supabase.table("componentes")
        .select("id,nombre,descripcion,categoria_id,cantidad,stock_minimo,ubicacion,categorias(nombre)")
        .order("nombre")
        .execute()
        .data
    )


# Trae el listado de todas las categorías disponibles ordenadas por nombre.
def cargar_categorias():
    return supabase.table("categorias").select("id,nombre").order("nombre").execute().data


# Extrae de forma segura el nombre de la categoría desde el diccionario devuelto por Supabase.
def nombre_categoria(item):
    relacion = item.get("categorias")
    if isinstance(relacion, dict):
        return relacion.get("nombre", "Sin categoría")
    if isinstance(relacion, list) and relacion:
        return relacion[0].get("nombre", "Sin categoría")
    return "Sin categoría"


# Trae el historial de pedidos de un alumno puntual haciendo JOIN con 'estado', 'pedido_detalle' y 'componentes'.
def cargar_pedidos_alumno(alumno_id):
    return (
        supabase.table("pedidos")
        .select("id,fecha,estado_id,estado(nombre),pedido_detalle(cantidad,componentes(nombre))")
        .eq("alumno_id", alumno_id)
        .order("fecha", desc=True)  # Ordena del pedido más reciente al más antiguo.
        .execute()
        .data
    )


# Trae TODOS los pedidos del sistema para el profesor, incluyendo datos del alumno y usuario solicitante.
def cargar_pedidos_profesor():
    return (
        supabase.table("pedidos")
        .select("id,fecha,estado_id,alumno_id,profesor_id,estado(nombre),alumnos(curso,usuarios(nombre,apellido,email)),pedido_detalle(cantidad,componentes(nombre))")
        .order("fecha", desc=True)
        .execute()
        .data
    )


# Convierte la lista de detalles de un pedido en un texto
def texto_detalle(pedido):
    partes = []
    for detalle in pedido.get("pedido_detalle", []) or []:
        comp = detalle.get("componentes") or {}
        if isinstance(comp, list):
            comp = comp[0] if comp else {}
        partes.append(f"{comp.get('nombre', 'Componente')} × {detalle.get('cantidad', 0)}")
    return ", ".join(partes) or "Sin detalle"


# Extrae el nombre del estado del pedido (ej. "pendiente")
def estado_nombre(pedido):
    estado = pedido.get("estado") or {}
    if isinstance(estado, list):
        estado = estado[0] if estado else {}
    return estado.get("nombre", "sin estado").capitalize()






def panel_alumno(perfil):
    st.markdown('<div class="eyebrow">Área del alumno</div><div class="section-title">Tu espacio de materiales</div>', unsafe_allow_html=True)
    nombre = f"{perfil['usuario'].get('nombre', '')} {perfil['usuario'].get('apellido', '')}".strip() or st.session_state["user"]["email"]
    st.caption(f"{nombre} · Curso {perfil['perfil'].get('curso', 'No indicado')}")


    # Descarga inicial de datos desde Supabase para poblar las 3 pestañas del alumno.
    try:
        inventario = cargar_inventario()
        categorias = cargar_categorias()
        pedidos = cargar_pedidos_alumno(perfil["perfil"]["id"])
    except Exception as exc:
        error_db(exc, "cargar los datos desde Supabase")
        return


    # Calcula indicadores rápidos en memoria y los muestra en 3 tarjetas superiores.
    total = len(inventario)
    disponibles = sum(1 for x in inventario if (x.get("cantidad") or 0) > 0)
    bajo_stock = sum(1 for x in inventario if (x.get("cantidad") or 0) <= (x.get("stock_minimo") or 0))
    m1, m2, m3 = st.columns(3)
    m1.metric("Componentes registrados", total)
    m2.metric("Con disponibilidad", disponibles)
    m3.metric("En nivel mínimo", bajo_stock)


    # Divide el panel del alumno en 3 pestañas navegables.
    tab_inv, tab_pedir, tab_mios = st.tabs(["  Inventario  ", "  Solicitar material  ", "  Mis solicitudes  "])


    # --- PESTAÑA 1: EXPLORAR INVENTARIO ---
    with tab_inv:
        st.markdown("#### Explorar inventario")
        c1, c2 = st.columns([2, 1])
        busqueda = c1.text_input("Buscar", placeholder="Ej. Arduino, motor, sensor...")
        opciones = ["Todas"] + [c["nombre"] for c in categorias]
        cat = c2.selectbox("Categoría", opciones)


        # Filtra la lista descargada en memoria según la categoría elegida y el texto buscado.
        filtrados = inventario
        if cat != "Todas":
            categoria_id = next((c["id"] for c in categorias if c["nombre"] == cat), None)
            filtrados = [x for x in filtrados if x.get("categoria_id") == categoria_id]
        if busqueda:
            # .casefold() compara texto ignorando mayúsculas y tildes mejor que .lower().
            filtrados = [x for x in filtrados if busqueda.casefold() in (x.get("nombre") or "").casefold() or busqueda.casefold() in (x.get("descripcion") or "").casefold()]


        if not filtrados:
            st.info("No hay componentes que coincidan con la búsqueda.")
        else:
            # Dibuja una tarjeta con borde por cada componente filtrado.
            for item in filtrados:
                cantidad = item.get("cantidad") or 0
                minimo = item.get("stock_minimo") or 0
                with st.container(border=True):
                    a, b, c = st.columns([3, 1.3, 1.2], vertical_alignment="center")
                    a.markdown(f"**{item['nombre']}**")
                    a.caption(f"{item.get('descripcion') or 'Sin descripción'} · {nombre_categoria(item)}")
                    a.caption(f"Ubicación: {item.get('ubicacion') or 'No asignada'}")
                    b.metric("Disponibles", cantidad)
                    # Muestra una etiqueta de color según el nivel de stock.
                    if cantidad == 0:
                        c.error("Sin stock")
                    elif cantidad <= minimo:
                        c.warning("Stock bajo")
                    else:
                        c.success("Disponible")


    # --- PESTAÑA 2: SOLICITAR MATERIAL ---
    with tab_pedir:
        st.markdown("#### Nueva solicitud")
        # Filtra solo los componentes que tienen al menos 1 unidad disponible.
        disponibles_items = [x for x in inventario if (x.get("cantidad") or 0) > 0]
        if not disponibles_items:
            st.info("En este momento no hay materiales con stock.")
        else:
          # Crea un diccionario donde la clave es el texto visible en el desplegable y el valor es el objeto componente.
            opciones_material = {f"{x['nombre']} · {x.get('cantidad', 0)} disponibles": x for x in disponibles_items}
            # El selector de material va FUERA del st.form() para que al cambiar de componente
            # se actualice al instante el stock máximo disponible en el campo numérico.
            elegido = st.selectbox("Material", list(opciones_material.keys()))
            material = opciones_material[elegido]
            st.caption(f"Categoría: {nombre_categoria(material)} · Ubicación: {material.get('ubicacion') or 'No asignada'}")
            with st.form("crear_pedido_form"):
                # Limita el selector numérico para que nunca se pueda pedir más del stock disponible.
                cantidad = st.number_input("Cantidad solicitada", min_value=1, max_value=max(1, int(material.get("cantidad") or 1)), value=1, step=1)
                motivo = st.text_area("¿Para qué clase o proyecto lo necesitás?", placeholder="Contanos brevemente el uso...")
                enviar = st.form_submit_button("Enviar solicitud", type="primary", use_container_width=True)
            if enviar:
                try:
                    # Llama a una función almacenada (RPC) dentro de PostgreSQL llamada 'crear_pedido'.
                    # Esa función identifica automáticamente al alumno mediante su sesión en Supabase Auth
                    # e inserta el pedido y su detalle en una sola transacción segura.
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


    # --- PESTAÑA 3: MIS SOLICITUDES ---
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
                # Colorea la insignia del estado según corresponda.
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


    # Descarga inventario, categorías, todos los pedidos y el catálogo de estados posibles.
    try:
        inventario = cargar_inventario()
        categorias = cargar_categorias()
        pedidos = cargar_pedidos_profesor()
        lista_estados = supabase.table("estado").select("id,nombre").execute().data
    except Exception as exc:
        error_db(exc, "cargar los datos administrativos")
        return


    # Calcula métricas generales para el tablero del profesor.
    pendientes = sum(1 for p in pedidos if estado_nombre(p).lower() == "pendiente")
    bajo_stock = sum(1 for x in inventario if (x.get("cantidad") or 0) <= (x.get("stock_minimo") or 0))
    m1, m2, m3 = st.columns(3)
    m1.metric("Componentes", len(inventario))
    m2.metric("Solicitudes pendientes", pendientes)
    m3.metric("Alertas de stock", bajo_stock)


    # Crea las 4 pestañas de administración.
    tab_ped, tab_inv, tab_nuevo, tab_cat = st.tabs(["  Solicitudes  ", "  Inventario  ", "  Agregar componente  ", "  Categorías  "])


    # --- PESTAÑA 1: GESTIONAR SOLICITUDES ---
    with tab_ped:
        st.markdown("#### Solicitudes de alumnos")
        if not pedidos:
            st.info("Todavía no hay solicitudes.")
        for pedido in pedidos:
            estado = estado_nombre(pedido)
            # Desempaqueta los datos anidados del alumno y su usuario de forma segura.
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


                # Solo permite cambiar el estado si el pedido sigue activo (no rechazado ni ya entregado).
                if estado.lower() in ("pendiente", "en proceso", "aprobado"):
                    disponibles_estado = [e for e in lista_estados if e["nombre"] in ("en proceso", "aprobado", "rechazado", "entregado")]
                    etiquetas = {e["nombre"].capitalize(): e["nombre"] for e in disponibles_estado}
                    c1, c2 = st.columns([2, 1])
                    # Cada widget dentro de un bucle for necesita un 'key' único para que Streamlit no los confunda.
                    nuevo_estado = c1.selectbox("Actualizar estado", list(etiquetas.keys()), key=f"estado_{pedido['id']}")
                    if c2.button("Guardar estado", key=f"guardar_estado_{pedido['id']}", type="primary", use_container_width=True):
                        try:
                            # Llama a la función SQL 'actualizar_estado_pedido' en Supabase.
                            # Cuando pasa a 'entregado', esa función en la base de datos descuenta el stock automáticamente.
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
        # Muestra el resultado de la última operación de borrado (éxito, advertencia o error).
        if "feedback_inv" in st.session_state:
            tipo_msg, texto_msg = st.session_state.pop("feedback_inv")
            if tipo_msg == "success":
                st.success(texto_msg)
            elif tipo_msg == "warning":
                st.warning(texto_msg)
            else:
                st.error(texto_msg)


        for item in inventario:
            # Crea un acordeón desplegable por cada componente para no saturar la pantalla.
            with st.expander(f"{item['nombre']} · {item.get('cantidad', 0)} unidades"):
                with st.form(f"editar_{item['id']}"):
                    c1, c2 = st.columns(2)
                    nombre = c1.text_input("Nombre", value=item["nombre"])
                    # Busca qué categoría tiene actualmente el componente para preseleccionarla en el desplegable.
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
                            # Ejecuta UPDATE en la tabla 'componentes' filtrando por el id del ítem (.eq).
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


                # --- ELIMINAR COMPONENTE (misma lógica que eliminar_componente() de main_2.py) ---
                st.divider()
                col_del1, col_del2 = st.columns([2, 1], vertical_alignment="center")
                # Casilla de confirmación manual para no borrar componentes por accidente.
                col_del1.checkbox(
                    f"Confirmar eliminación de «{item['nombre']}»",
                    key=f"confirmar_eliminar_{item['id']}"
                )
                # Ejecuta el borrado mediante on_click para que Streamlit lo procese antes de recargar.
                col_del2.button(
                    "Eliminar componente",
                    key=f"eliminar_{item['id']}",
                    use_container_width=True,
                    on_click=eliminar_componente_callback,
                    args=(item["id"], item["nombre"])
                )


    # --- PESTAÑA 3: AGREGAR NUEVO COMPONENTE ---
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
                        # Obtiene el ID numérico de la categoría elegida por su nombre.
                        cat_id = next(c["id"] for c in categorias if c["nombre"] == cat)
                        # Ejecuta INSERT en la tabla 'componentes'.
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


    # --- PESTAÑA 4: ADMINISTRAR CATEGORÍAS ---
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
                    # Ejecuta INSERT en la tabla 'categorias'.
                    supabase.table("categorias").insert({
                        "nombre": nueva.strip(),
                        "descripcion": descripcion_cat.strip() or None,
                    }).execute()
                    st.success("Categoría creada.")
                    st.rerun()
                except Exception as exc:
                    error_db(exc, "crear la categoría")


# 1. Verifica que las claves de Supabase estén configuradas en secrets.toml; si faltan, detiene la app.
if supabase is None:
    mostrar_encabezado()
    st.error("Falta configurar la conexión con Supabase.")
    st.markdown("Creá un archivo **.streamlit/secrets.toml** en la carpeta del proyecto con estas variables:")
    st.code('SUPABASE_URL="https://TU-PROYECTO.supabase.co"\nSUPABASE_PUBLISHABLE_KEY="TU_CLAVE_PUBLICABLE"\nSUPABASE_SECRET_KEY="TU_CLAVE_SECRETA"')
    st.stop()  # Detiene la ejecución del script aquí para no renderizar nada más.


# 2. Si no hay un usuario guardado en la sesión actual, muestra la pantalla de Login/Registro y frena el script.
if "user" not in st.session_state:
    iniciar_sesion()
    st.stop()


# 3. Si existe 'user' en sesión pero falta 'perfil', intenta recuperarlo desde la base de datos.
if "perfil" not in st.session_state:
    try:
        st.session_state["perfil"] = obtener_perfil(st.session_state["user"]["id"])
    except Exception:
        st.session_state["perfil"] = None


# 4. Si el usuario autenticado no tiene perfil válido en 'alumnos' o 'profesores', bloquea el acceso.
if not st.session_state.get("perfil"):
    st.warning("Tu usuario no está asociado a un registro de alumno o profesor.")
    if st.button("Cerrar sesión"):
        cerrar_sesion()
    st.stop()


# 5. Si pasó todas las validaciones anteriores, dibuja la barra lateral izquierda con los datos del usuario.
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


# 6. Renderiza el encabezado principal y abre el panel correspondiente según el rol del usuario.
mostrar_encabezado("Un espacio simple y ordenado para consultar, solicitar y administrar materiales.")
try:
    if perfil["rol"] == "alumno":
        panel_alumno(perfil)
    else:
        panel_profesor(perfil)
except Exception as exc:
    error_db(exc, "mostrar la aplicación")  


