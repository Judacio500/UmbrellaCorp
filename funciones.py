import streamlit as st
import psycopg2 as psql
from psycopg2 import pool
import base64
from streamlit_agraph import agraph, Node, Edge, Config 

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

def cargar_catalogo():
    db_pool = init_connection_pool()
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

def renderizar_jerarquias(list_jerarquia, sentido):
    nodos = []
    aristas = []
    
    for emp in list_jerarquia:
        ruta = emp[2]

        with open(ruta, "rb") as foto:
            foto_bytes = foto.read()

        bytes_base64 = base64.b64encode(foto_bytes)

        string_imagen = bytes_base64.decode('utf-8')
        imagen_url = "data:image/jpeg;base64," + string_imagen
        
        nodos.append(Node(
            id=emp[0], 
            label=emp[1], 
            shape="circularImage", 
            image=imagen_url, 
            size=45,
            borderWidth=3,
            color={"border": "#cc0000", "background": "#1e1e1e"},
            font={"color": "#ffffff", "size": 15, "face": "Arial"}
        ))
        if emp[3] != None:
            if sentido == 1:
                aristas.append(Edge(source=emp[3],target=emp[0],color="#cc0000",width=2))
            else:
                aristas.append(Edge(source=emp[0],target=emp[3],color="#cc0000",width=2))

    configuracion = Config(
        width="100%",
        height=650,
        directed=True,       
        physics=False,         
        hierarchical=True,    
        layout={"hierarchical": {"enabled": True, "direction": "UD", "sortMethod": "directed", "nodeSpacing": 180}},
        interaction={"dragNodes": False, "zoomView": True, "dragView": True, "selectable": False}
    )

    return agraph(nodes = nodos, edges = aristas, config = configuracion)