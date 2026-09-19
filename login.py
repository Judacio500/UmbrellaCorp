import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
import psycopg2 as psql

dbname = st.secrets["umbrellaConn"]["dbname"]
user = st.secrets["umbrellaConn"]["user"]
password = st.secrets["umbrellaConn"]["password"]
host = st.secrets["umbrellaConn"]["host"]
port = st.secrets["umbrellaConn"]["port"]

conn = psql.connect(
    dbname = dbname,
    user = user,
    password = password,
    host = host,
    port = port
)
cur = conn.cursor()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    with st.form("login"):
        nombre_usuario = st.text_input(label = "Usuario: ", value = "")
        contrasena = st.text_input(label = "Contraseña: ", value = "", type = "password")
        
        query = "SELECT id_emp, nombre_usuario, contrasena FROM credenciales_estandar WHERE nombre_usuario = %s AND contrasena = %s" 
        if st.form_submit_button("Login"):
            cur.execute(query,(nombre_usuario,contrasena))
            user = cur.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
            else:
                st.error("Credenciales Incorrectas")
            st.rerun()
else:
    st.markdown(f"Bienvenido, {st.session_state.user[1]}")

