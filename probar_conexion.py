
import streamlit as st
from database import conectar_supabase

st.title("Prueba de conexión con Supabase")

st.write("Ingresá los datos de un usuario de prueba.")

email = st.text_input("Email")
password = st.text_input("Contraseña", type="password")

if st.button("Probar conexión"):

    if not email or not password:
        st.warning("Completá el email y la contraseña.")

    else:
        try:
            supabase = conectar_supabase()

            supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.success("¡Inicio de sesión correcto!")

            respuesta = supabase.table("categorias").select("*").limit(5).execute()

            st.success("¡Consulta a Supabase realizada correctamente!")

            if respuesta.data:
                st.dataframe(respuesta.data)
            else:
                st.info("La conexión funciona, pero todavía no hay categorías registradas.")

        except Exception as error:
            st.error("Ocurrió un error:")
            st.code(str(error))
