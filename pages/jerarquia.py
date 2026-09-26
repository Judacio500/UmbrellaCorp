import streamlit as st 
from funciones import init_connection_pool
from funciones import renderizar_jerarquias

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

if "current_view_jerarquia" not in st.session_state:
    st.session_state.current_view_jerarquia = 0
    st.warning("Acceso no autorizado. Por favor, inicie sesión.")
    st.switch_page("login.py")   

with st.sidebar:
    st.markdown("<h3 style='color: #cc0000;'>Menú de Estructura</h3>", unsafe_allow_html=True)
    st.write("")

    button1 = st.button("CONSULTA SUBORDINADOS", type="primary", use_container_width=True)
    button2 = st.button("CONSULTA JEFES", type="primary", use_container_width=True)

    if button1:
        st.session_state.current_view_jerarquia = 0
    elif button2:
        st.session_state.current_view_jerarquia = 1

st.markdown("<h1 style='text-align: center; color: #cc0000; font-family: Arial, sans-serif;'>UMBRELLA CORPORATION</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555555; font-family: Arial, sans-serif;'>Directorio Jerárquico Central</h3>", unsafe_allow_html=True)
st.divider()

conn = db_pool.getconn()
try:
    cur = conn.cursor()

    cur.execute("SELECT id_emp, nombre || ' ' || apellido AS nombre_completo FROM cientificos")
    cientificos = {fila[1] : fila[0] for fila in cur.fetchall()}

    col_controls, col_graph = st.columns([1, 4])
    match st.session_state.current_view_jerarquia:
        case 0:
            with col_controls:
                st.markdown("<h4 style='color: #333333;'>Árbol de Subordinados</h4>", unsafe_allow_html=True)
                if(st.session_state.user[5] == 10):
                    id_emp = st.selectbox(
                            label = "NOMBRE",
                            options = cientificos.keys()
                        )
                else:
                    user = f"{st.session_state.user[3]} {st.session_state.user[4]}"
                    st.text_input(label = "Usuario:", value = user, disabled = True)
                    id_emp = st.session_state.user[0]
            
            query = "SELECT * FROM linea_de_subordinados(%s)"
            cur.execute(query,(cientificos[id_emp],))
            subordinados = cur.fetchall()
            
            with col_graph:
                with st.container(height=700, border=True):
                    grafo_sub = renderizar_jerarquias(subordinados, 1)
                
        case 1:
            st.markdown("<h4 style='color: #333333;'>Superiores Directos</h4>", unsafe_allow_html=True)
            with col_controls:
                st.markdown("<h4 style='color: #333333;'>Lista de Superiores</h4>", unsafe_allow_html=True)
                if(st.session_state.user[5] == 10):
                    id_emp = st.selectbox(
                            label = "NOMBRE",
                            options = cientificos.keys()
                        )
                else:
                    user = f"{st.session_state.user[3]} {st.session_state.user[4]}"
                    st.text_input(label = "Usuario:", value = user, disabled = True)
                    id_emp = st.session_state.user[0]
            
            query = "SELECT * FROM linea_de_mando(%s)"
            cur.execute(query,(cientificos[id_emp],))
            jefes = cur.fetchall()
            
            with col_graph:
                with st.container(height=700, border=True):
                    grafo_sub = renderizar_jerarquias(jefes, 0)
    cur.close()
finally:
    db_pool.putconn(conn)