import streamlit as st
import pandas as pd
import plotly.express as px
from funciones import init_connection_pool
from funciones import cargar_catalogo
from PIL import Image

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        ul[data-testid="stSidebarNavItems"] li:nth-child(1) {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

db_pool = init_connection_pool()

if "current_view_despliegue" not in st.session_state:
    st.session_state.current_view_despliegue = 0
    st.warning("Acceso no autorizado. Por favor, inicie sesión.")
    st.switch_page("login.py") 

with st.sidebar:
    st.markdown("<h3 style='color: #cc0000;'>Menú Táctico</h3>", unsafe_allow_html=True)
    st.write("")
    
    button1 = st.button("Registro de Eventos", type="primary", use_container_width=True)
    button2 = st.button("Consultar despliegues", type="primary", use_container_width=True)

    if button1:
        st.session_state.current_view_despliegue = 0
    elif button2:
        st.session_state.current_view_despliegue = 1

st.markdown("<h1 style='text-align: center; color: #cc0000; font-family: Arial, sans-serif;'>UMBRELLA CORPORATION</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555555; font-family: Arial, sans-serif;'>Panel de Operaciones: Despliegue B.O.W.</h3>", unsafe_allow_html=True)
st.divider()

col_form, col_regist = st.columns([1,2])

match st.session_state.current_view_despliegue:
    case 0:
        conn = db_pool.getconn()
        try:
            cur = conn.cursor()
            
            with col_form:
                st.markdown("<h4 style='color: #333333;'>Autorización de Campo</h4>", unsafe_allow_html=True)
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

                st.write("")
                submit_form = st.button("AUTORIZAR DESPLIEGUE", type="primary", use_container_width=True)

                if submit_form:
                    try:
                        cur.execute("CALL insertar_despliegue(%s, %s, %s, %s, %s, %s)", (id_zona,st.session_state.user[0],id_bows,id_equipo,fecha,n_especimenes))
                        conn.commit()
                        st.success("DESPLIGUE AUTORIZADO")
                    except Exception as error_db:
                        conn.rollback()
                        st.error(f"{error_db}")

            with col_regist:
                st.markdown("<h4 style='color: #333333; text-align: center;'>Visualización Táctica</h4>", unsafe_allow_html=True)
                
                cur.execute("SELECT file_path FROM foto_personal WHERE id_emp = %s", (st.session_state.user[0],))
                fot_user = cur.fetchone()
                foto_cientifico = fot_user[0] if fot_user else 'Characters/default.jpg'

                cur.execute("SELECT file_path FROM foto_bow WHERE id_bow = %s", (id_bows,))
                fot_bow = cur.fetchone()
                foto_arma = fot_bow[0] if fot_bow else 'BOWs/default.jpg'

                img_col1, img_col2 = st.columns(2)
                with img_col1:
                    img_arma = Image.open(foto_arma).resize((500, 550))
                    st.image(img_arma, use_container_width=True)
                with img_col2:
                    img_cientifico = Image.open(foto_cientifico).resize((500, 550))
                    st.image(img_cientifico, use_container_width=True)
                
                st.write("")
                
                cur.execute("SELECT z.id_zona, z.nombre, u.latitud, u.longitud FROM zona_de_brote z JOIN ubicacion_zona u ON z.id_zona = u.id_zona")
                map_data = cur.fetchall()
                df_mapa = pd.DataFrame(map_data, columns=["id_zona", "zona", "lat", "lon"])
                
                df_mapa['color'] = df_mapa['id_zona'].apply(lambda x: '#ff0000' if x == id_zona else '#550000')
                df_mapa['size'] = df_mapa['id_zona'].apply(lambda x: 15 if x == id_zona else 5)
                
                fig_map = px.scatter_geo(
                    df_mapa, lat='lat', lon='lon', size='size', hover_name='zona',
                    projection="natural earth", template="plotly_dark",
                    color='color', color_discrete_map="identity"
                )
                fig_map.update_geos(showcountries=True, countrycolor="#333333", showland=True, landcolor="#1e1e1e", showocean=True, oceancolor="#0e1117")
                fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=250)
                st.plotly_chart(fig_map, use_container_width=True)

        finally:
            cur.close()
            db_pool.putconn(conn)
                
    case 1:
        st.markdown("<h4 style='color: #333333;'>Bitácora Global de Despliegues</h4>", unsafe_allow_html=True)
        with st.form("Consulta de despliegues de BOWs"):
            conn = db_pool.getconn()
            try:
                cur = conn.cursor()
                query = "SELECT id_despliegue AS Identificador, zona_de_brote.nombre AS Lugar, cientificos.nombre || ' ' || cientificos.apellido AS Empleado, armas_bio_organicas.nombre_clave AS BOW, equipo_de_control.nombre as Asignado, fecha_despliegue as Fecha, cantidad_especimenes as Especimenes FROM despliegue JOIN zona_de_brote ON zona_de_brote.id_zona = despliegue.id_zona JOIN cientificos ON cientificos.id_emp = despliegue.id_emp JOIN armas_bio_organicas ON armas_bio_organicas.id_bow = despliegue.id_bow JOIN equipo_de_control ON equipo_de_control.id_equipo = despliegue.id_equipo"
                cur.execute(query)
                registros = cur.fetchall()

                nombre_columnas = [desc[0] for desc in cur.description]
                df_despliegues = pd.DataFrame(registros, columns=nombre_columnas)
                
                st.dataframe(df_despliegues, hide_index=True, use_container_width=True)

                cur.close()
            finally:
                db_pool.putconn(conn)
            
            st.write("")
            st.form_submit_button("ACTUALIZAR BITÁCORA", use_container_width=True)