import streamlit as st
import pandas as pd
import plotly.express as px
from funciones import init_connection_pool

# Configuración inicial y CSS para ocultar el login
st.set_page_config(page_title="Umbrella Corp - Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
        ul[data-testid="stSidebarNavItems"] li:nth-child(1) {
            display: none;
        }
        .badge-container {
            border: 1px solid #cc0000; 
            border-radius: 8px; 
            background-color: #121212; 
            padding: 20px; 
            box-shadow: 0 4px 8px rgba(204, 0, 0, 0.2);
        }
        .section-title {
            color: #cc0000; 
            font-family: Arial, sans-serif; 
            border-bottom: 1px solid #333; 
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inicializar pool de conexiones
db_pool = init_connection_pool()

if "user" not in st.session_state:
    st.warning("Acceso no autorizado. Por favor, inicie sesión.")
    st.switch_page("login.py")    

nivel_acceso = st.session_state.user[5]
id_empleado = st.session_state.user[0]

conn = db_pool.getconn()

try:
    col_foto, col_info, col_logo = st.columns([1, 4, 1])
    cur = conn.cursor()

    with col_foto:
        query_foto = "SELECT file_path FROM foto_personal WHERE id_emp = %s"
        cur.execute(query_foto, (st.session_state.user[0],))
        fot = cur.fetchone()
        fot_path = fot[0] if fot else 'Characters/default.jpg'
        st.image(fot_path, width=120)    

    with col_info:
        query_jefe = "SELECT nombre || ' ' || apellido from cientificos WHERE id_emp = %s"
        cur.execute(query_jefe, (st.session_state.user[6],))
        jefe_cons = cur.fetchone()

        jefe = jefe_cons[0] if jefe_cons else "USTEDE ES EL JEFE SUPREMO DE UMBRELLA"

        st.markdown(f"<h2 style='color: white; margin-bottom: 0px;'>{st.session_state.user[3]} {st.session_state.user[4]}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color: #888; margin-top: 0px;'>ID de Empleado: {id_empleado:04d} | Autorización: Nivel {nivel_acceso}</h4>", unsafe_allow_html=True)
        st.markdown(f"**SUPERIOR:** {jefe}")
        
        if nivel_acceso >= 7:
            st.markdown("<span style='color: #00ff00; font-weight: bold;'>[ESTADO: AUTORIZACIÓN ALPHA CONCEDIDA]</span> - Acceso total a zonas de cuarentena y reportes de mortalidad.", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #ffaa00; font-weight: bold;'>[ESTADO: AUTORIZACIÓN LIMITADA]</span>", unsafe_allow_html=True)

    with col_logo:
        st.markdown("<h1 style='color: #cc0000; text-align: right;'>☂</h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown("<h3 class='section-title'>Monitor Global de Brotes (B.O.W. Deployments)</h3>", unsafe_allow_html=True)

    query_mapa = "SELECT * FROM zonas_activas(%s)"
    cur.execute(query_mapa, (10,))
    registros = cur.fetchall()
    df_mapa = pd.DataFrame(registros, columns=["zona", "lat", "lon", "especimenes"])
    
    fig_map = px.scatter_geo(
        df_mapa, lat='lat', lon='lon', size='especimenes', hover_name='zona',
        projection="natural earth", template="plotly_dark",
        color_discrete_sequence=["#cc0000"]
    )
    fig_map.update_geos(showcountries=True, countrycolor ="#333333", showland=True, landcolor="#1e1e1e", showocean=True, oceancolor="#0e1117")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400)
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("<h3 class='section-title'>Telemetría y Registro Operativo</h3>", unsafe_allow_html=True)

    query_ba = "SELECT SUM(cantidad_especimenes) FROM despliegue"
    query_cuarentena = "SELECT COUNT(id_zona) FROM zona_de_brote WHERE estado_de_cuarentena = '4' OR estado_de_cuarentena = '3'"
    query_concentracion = "SELECT MAX(cantidad_especimenes) FROM despliegue"
    query_incidentes = "SELECT COUNT(id_despliegue_detonante) FROM accidentes"

    cur.execute(query_ba)
    bows_activas = cur.fetchone()[0]

    cur.execute(query_cuarentena)
    zonas_en_cuarentena = cur.fetchone()[0]

    cur.execute(query_concentracion)
    concentracion_bows = cur.fetchone()[0]

    cur.execute(query_incidentes)
    Incidentes_registrados = cur.fetchone()[0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="B.O.W.s Activas en Campo", value=bows_activas)
    m2.metric(label="Zonas en Cuarentena Crítica", value=zonas_en_cuarentena if nivel_acceso >= 7 else "CLASIFICADO")
    m3.metric(label="Mayor Concentración", value=concentracion_bows)
    m4.metric(label="Incidentes de Brecha", value=Incidentes_registrados if nivel_acceso >= 7 else "CLASIFICADO")

    st.write("")

    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.markdown("##### Despliegue Temporal por Tipo de Mutágeno")

        query_agregacion = "SELECT DATE_TRUNC('month', fecha_despliegue) as mes, armas_bio_organicas.nombre_clave as nombre, SUM(cantidad_especimenes) as especimenes FROM despliegue JOIN armas_bio_organicas ON despliegue.id_bow = armas_bio_organicas.id_bow GROUP BY DATE_TRUNC('month', despliegue.fecha_despliegue), armas_bio_organicas.nombre_clave ORDER BY mes ASC;"

        cur.execute(query_agregacion)
        fechas = cur.fetchall()
        df_fechas = pd.DataFrame(fechas, columns=["mes","nombre","cantidad de especimenes"])
        st.plotly_chart(px.line(df_fechas, x='mes', y='cantidad de especimenes', color='nombre', template='plotly_dark'))
                
        st.write("")
        
        st.markdown("##### Últimos Despliegues Registrados")
        query_last_10 = "SELECT id_despliegue AS Identificador, zona_de_brote.nombre AS Lugar, cientificos.nombre || ' ' || cientificos.apellido AS Empleado, armas_bio_organicas.nombre_clave AS BOW, equipo_de_control.nombre as Asignado, fecha_despliegue as Fecha, cantidad_especimenes as Especimenes FROM despliegue JOIN zona_de_brote ON zona_de_brote.id_zona = despliegue.id_zona JOIN cientificos ON cientificos.id_emp = despliegue.id_emp JOIN armas_bio_organicas ON armas_bio_organicas.id_bow = despliegue.id_bow JOIN equipo_de_control ON equipo_de_control.id_equipo = despliegue.id_equipo ORDER BY fecha_despliegue DESC LIMIT 10"
        cur.execute(query_last_10)
        last_10 = cur.fetchall()
        df_ul_10 = pd.DataFrame(last_10, columns=["ID", "ZONA", "AUTORIZA", "B.O.W.", "ESCUADRÓN", "FECHA", "ESPECIMENES LIBERADOS"])
        st.dataframe(df_ul_10, use_container_width=True, hide_index=True)

    with col_der:   
        st.markdown("##### Directivas Activas")
        st.info("**Prioridad Alpha:** Monitorear niveles de mutación en sector 4.")
        st.warning("**Aviso de Seguridad:** Escuadrón HUNK reporta bajas operativas.")
        if nivel_acceso >= 7:
            st.error("**ALERTA CRÍTICA:** Proyecto Tyrant requiere evaluación de contención inmediata.")
        
        st.markdown("##### Científico Destacado")

        query_mejor = "SELECT nombre || ' ' || apellido, SUM(despliegue.cantidad_especimenes) AS total_desplegados, foto_personal.file_path FROM cientificos JOIN despliegue ON cientificos.id_emp = despliegue.id_emp JOIN foto_personal ON foto_personal.id_emp = cientificos.id_emp GROUP BY nombre, apellido, foto_personal.file_path ORDER BY total_desplegados DESC LIMIT 1"
        cur.execute(query_mejor)
        mejor = cur.fetchone()
        st.metric(label="Nombre", value = mejor[0])
        st.metric(label="BOWS. DESPLEGADAS", value = mejor[1])
        st.image(mejor[2], width=120)

finally:
    db_pool.putconn(conn)