# Arquitectura de Vistas: Umbrella Corp

## 1. `dashboard.py` (Panel Táctico Principal)
* Enmascarar u omitir las zonas de brote activas y los detalles de patógenos letales si la vista corresponde a un usuario con nivel de seguridad menor a 7[cite: 1].
* Mostrar métricas clave usando `st.metric` para contabilizar las B.O.W. activas en campo, las zonas en cuarentena crítica y los especímenes dispersados[cite: 1].
* Generar gráficos interactivos de agregación temporal que clasifiquen a los especímenes liberados por mes/semana y por tipo de mutágeno[cite: 1].
* Visualizar un mapa o diagrama de las zonas geográficas afectadas[cite: 1].

## 2. `jerarquia.py` (Cadena de Mando Científica)
* Implementar un selector interactivo diseñado para buscar a un jefe de división científica[cite: 1].
* **[Requisito Extra]** Ejecutar desde Streamlit la consulta de la CTE recursiva (`WITH RECURSIVE`) para calcular toda la cadena de mando del científico seleccionado[cite: 1].
* **[Requisito Extra]** Proyectar esta jerarquía, indicando la profundidad y el personal bajo su mando directo e indirecto, utilizando una tabla interactiva o un grafo visual de dependencias[cite: 1].

## 3. `despliegues.py` (Control y Autorización de Operaciones)
* Construir un formulario interactivo mediante `st.form` para registrar nuevos despliegues, capturando: científico emisor, B.O.W., zona, escuadrón y cantidad de especímenes[cite: 1].
* **[Requisito Extra]** Procesar la inserción de datos llamando directamente al Procedimiento Almacenado transaccional a través del pool de conexiones[cite: 1].
* **[Requisito Extra]** Capturar y desplegar visualmente en la pantalla las excepciones emitidas por la base de datos si el trigger o las restricciones de autorización rechazan la orden de despliegue[cite: 1].