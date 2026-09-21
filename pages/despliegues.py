import streamlit as st
import pandas as pd
from login import init_connection_pool

st.set_page_config(layout="wide")

db_pool = init_connection_pool()

def cargar_catalogo():
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        
        cur.execute("SELECT id_zona, nombre FROM zona_de_brote")
        cat_zona = {fila[1] : fila[0] for fila in cur.fetchall()}

        cur.execute("SELECT nombre || ' ' || apellido AS nombre_completo FROM cientificos WHERE id_emp = %s", (st.session_state.user[0],))
        emp = cur.fetchone()

        cur.execute("SELECT id_bow, nombre_clave FROM armas_bio_organicas")
        cat_bow = {fila[1] : fila[0] for fila in cur.fetchall()}

        cur.execute("SELECT id_equipo, nombre FROM equipo_de_control")
        cat_equipo = {fila[1] : fila[0] for fila in cur.fetchall()}

        cur.close()
    finally:
        db_pool.putconn(conn)
    return emp, cat_zona, cat_bow, cat_equipo

if "current_view" not in st.session_state:
    st.session_state.current_view = 0

with st.sidebar:
    st.header("Opciones")

    button1 = st.button("Registro de Eventos", type="primary")
    button2 = st.button("Consultar despliegues", type="primary")

    if button1:
        st.session_state.current_view = 0
    elif button2:
        st.session_state.current_view = 1

col_form, col_regist = st.columns([1,2])

match st.session_state.current_view:
    case 0:
        with col_form:
            with st.form("Registro de Despligue de BOWs"):
                usuario,zonas,bows,equipos = cargar_catalogo()
                st.text_input(
                    label = "Cientifico al mando",
                    value = usuario[0],
                    disabled = True
                )
                s_zona = st.selectbox(
                    label = "Zona",
                    options = zonas.keys()
                )
                s_bows = st.selectbox(
                    label = "Arma a Desplegar",
                    options = bows.keys()
                )
                s_equipos = st.selectbox(
                    label = "Equipo de Contencion",
                    options = equipos.keys()
                )
                fecha = st.date_input("Fecha de Despliegue")
                n_especimenes = st.number_input("Cantidad a Desplegar", min_value=1, step=1)
                id_zona = zonas[s_zona]
                id_bows = bows[s_bows]
                id_equipo = equipos[s_equipos]

                submit_form = st.form_submit_button("AUTORIZAR DESPLIEGUE", type="primary")

                if submit_form:
                    conn = db_pool.getconn()
                    try:
                        cur = conn.cursor()
                        cur.execute("CALL insertar_despliegue(%s, %s, %s, %s, %s, %s)", (id_zona,st.session_state.user[0],id_bows,id_equipo,fecha,n_especimenes))

                        conn.commit()
                        st.success("DESPLIGUE AUTORIZADO")

                    except Exception as error_db:
                        conn.rollback()
                        st.error(f"{error_db}")
                    finally:
                        cur.close()
                        db_pool.putconn(conn)

        with col_regist:
                st.title("THIS IS A PLACEHOLDER")                
    case 1:
        with st.form("Consulta de despliegues de BOWs"):
            conn = db_pool.getconn()
            try:
                cur = conn.cursor()
                query = "SELECT id_despliegue AS Identificador, zona_de_brote.nombre AS Lugar, cientificos.nombre || ' ' || cientificos.apellido AS Empleado, armas_bio_organicas.nombre_clave AS BOW, equipo_de_control.nombre as Asignado, fecha_despliegue as Fecha, cantidad_especimenes as Especimenes FROM despliegue JOIN zona_de_brote ON zona_de_brote.id_zona = despliegue.id_zona JOIN cientificos ON cientificos.id_emp = despliegue.id_emp JOIN armas_bio_organicas ON armas_bio_organicas.id_bow = despliegue.id_bow JOIN equipo_de_control ON equipo_de_control.id_equipo = despliegue.id_equipo"
                cur.execute(query)
                registros = cur.fetchall()

                nombre_columnas = [desc[0] for desc in cur.description]
                df_despliegues = pd.DataFrame(registros, columns=nombre_columnas)
                st.dataframe(df_despliegues, hide_index = True)

                cur.close()
            finally:
                db_pool.putconn(conn)
