import streamlit as st
import pandas as pd
from funciones import init_connection_pool

st.set_page_config(
    page_title="Umbrella Corp - Access",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 style='text-align: center; color: #cc0000; font-family: Arial, sans-serif;'>UMBRELLA CORPORATION</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555555; font-family: Arial, sans-serif;'>Terminal de Autenticación Central</h4>", unsafe_allow_html=True)
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login"):
            nombre_usuario = st.text_input(label = "Usuario: ", value = "")
            contrasena = st.text_input(label = "Contraseña: ", value = "", type = "password")
            
            query = "SELECT cientificos.id_emp, nombre_usuario, contrasena, cientificos.nombre, cientificos.apellido, cientificos.nivel as nivel, cientificos.id_jefe FROM credenciales_estandar JOIN cientificos ON cientificos.id_emp = credenciales_estandar.id_emp WHERE nombre_usuario = %s AND contrasena = %s" 
            
            st.write("")
            
            if st.form_submit_button("Login", use_container_width=True):
                db_pool = init_connection_pool()
                conn = db_pool.getconn()
                try:
                    cur = conn.cursor()
                    cur.execute(query,(nombre_usuario,contrasena))
                    user = cur.fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                    else:
                        st.error("Credenciales Incorrectas")
                    cur.close()
                finally:
                    db_pool.putconn(conn)
                st.rerun()
else:
    st.switch_page("pages/despliegues.py")