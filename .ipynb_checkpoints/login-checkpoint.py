import streamlit as st
import pandas as pd
import psycopg2 as psql
from psycopg2 import pool

dbname = st.secrets["umbrellaConn"]["dbname"]
user = st.secrets["umbrellaConn"]["user"]
password = st.secrets["umbrellaConn"]["password"]
host = st.secrets["umbrellaConn"]["host"]
port = st.secrets["umbrellaConn"]["port"]

@st.cache_resource
def init_connection_pool():
    return pool.ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    with st.form("login"):
        nombre_usuario = st.text_input(label = "Usuario: ", value = "")
        contrasena = st.text_input(label = "Contraseña: ", value = "", type = "password")
        
        query = "SELECT id_emp, nombre_usuario, contrasena FROM credenciales_estandar WHERE nombre_usuario = %s AND contrasena = %s" 
        if st.form_submit_button("Login"):
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
    st.markdown(f"Bienvenido, {st.session_state.user[1]}")

