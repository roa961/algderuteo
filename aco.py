import geopandas as gpd
import networkx as nx
import folium
import random
import bdd
import geojson
from geojson import MultiLineString

def aco_restringido_exacto(grafo, nodos_deseados, iteraciones=100, alfa=1.0, beta=2.0, rho=0.5, q=1.0, num_rutas_mostrar=10):
    feromonas = {(i, j): 1.0 for i, j in grafo.edges()}
    todas_las_rutas = set()

    for _ in range(iteraciones):
        # Inicializar hormigas en nodos permitidos diferentes
        hormigas = random.sample(nodos_deseados, len(nodos_deseados))
        soluciones = []

        for hormiga in hormigas:
            solucion = construir_solucion_exacta(grafo, hormiga, nodos_deseados, feromonas, alfa, beta)
            soluciones.append(tuple(solucion))

        costos = [calcular_costo(solucion, grafo) for solucion in soluciones]
        actualizar_feromonas(feromonas, soluciones, costos, rho, q)
        todas_las_rutas.update(zip(soluciones, costos))

    todas_las_rutas = list(todas_las_rutas)
    todas_las_rutas.sort(key=lambda x: x[1])
    mejores_rutas = todas_las_rutas[:num_rutas_mostrar]

    return mejores_rutas

def construir_solucion_exacta(grafo, nodo_inicial, nodos_deseados, feromonas, alfa, beta):
    solucion = [nodo_inicial]
    nodos_no_visitados = set(nodos_deseados)
    nodos_no_visitados.remove(nodo_inicial)

    while nodos_no_visitados:
        siguiente_nodo = elegir_siguiente_nodo_exacto(grafo, solucion[-1], nodos_no_visitados, feromonas, alfa, beta)
        solucion.append(siguiente_nodo)
        nodos_no_visitados.remove(siguiente_nodo)

    return solucion

def elegir_siguiente_nodo_exacto(grafo, nodo_actual, nodos_no_visitados, feromonas, alfa, beta):
    probabilidades = []

    for vecino in nodos_no_visitados:
        feromona = feromonas.get((nodo_actual, vecino), 0.0)
        probabilidad = (feromona ** alfa) * ((1.0 / grafo[nodo_actual][vecino]['weight']) ** beta)
        probabilidades.append((vecino, probabilidad))

    total_probabilidades = sum(prob[1] for prob in probabilidades)

    if total_probabilidades == 0:
        siguiente_nodo = random.choice(list(nodos_no_visitados))
    else:
        probabilidades = [(nodo, prob / total_probabilidades) for nodo, prob in probabilidades]
        siguiente_nodo = random.choices(probabilidades, weights=[prob[1] for prob in probabilidades])[0][0]

    return siguiente_nodo

def actualizar_feromonas(feromonas, soluciones, costos, rho, q):
    for arista in feromonas:
        feromonas[arista] *= (1.0 - rho)

    # Encuentra el índice de la mejor solución (costo mínimo)
    indice_mejor_solucion = costos.index(min(costos))
    mejor_solucion = soluciones[indice_mejor_solucion]

    for i in range(len(mejor_solucion) - 1):
        arista = (mejor_solucion[i], mejor_solucion[i + 1])
        feromonas[arista] += q / costos[indice_mejor_solucion]

def calcular_costo(solucion, grafo):
    costo_total = 0
    for i in range(len(solucion) - 1):
        costo_total += grafo[solucion[i]][solucion[i + 1]]['weight']
    return costo_total

# Cargar el archivo GeoJSON usando GeoPandas
archivo_geojson = "./file_replaced.geojson"
gdf = gpd.read_file(archivo_geojson)

# Crear un grafo completo usando NetworkX
grafo = nx.complete_graph(len(gdf))
grafo = nx.DiGraph(grafo)

# Agregar un valor de 'id' a los nodos
for nodo, row in gdf.iterrows():
    grafo.nodes[nodo]['id'] = row['id']  # 'ID' debe ser el nombre de la columna en tu GeoJSON

# Seleccionar nodos permitidos
nodos_permitidos = []
monumentos_a_recorrer = ['ID_00460', 'ID_00838', 'ID_00462', 'ID_00463', 'ID_00467', "ID_00837","ID_01074"]# Aquí debes poner los IDs de los monumentos que quieres recorrer
for nodo, row in gdf.iterrows():
    if grafo.nodes[nodo]['id'] in monumentos_a_recorrer: # 'ID' debe ser el nombre de la columna en tu GeoJSON
        nodos_permitidos.append(nodo)

# Crear grafo restringido
grafo_restringido = grafo.subgraph(nodos_permitidos)
nodos_coordenadas = {nodo: (str(row['geometry'].x), str(row['geometry'].y)) for nodo, row in gdf.iterrows()}

# Asignar pesos a las aristas
for edge in grafo_restringido.edges():
    nodo_inicio, nodo_fin = edge
    coordenadas_inicio = nodos_coordenadas[nodo_inicio]
    coordenadas_fin = nodos_coordenadas[nodo_fin]
    peso = bdd.get_costo(coordenadas_inicio, coordenadas_fin)
    bdd.cursor.execute(peso)
    query = bdd.cursor.fetchone()
    costo = float(query[1])
    grafo[edge[0]][edge[1]]['weight'] = costo
    grafo[edge[0]][edge[1]]['camino'] = query[0]

# Ejecutar ACO restringido
mejores_rutas = aco_restringido_exacto(grafo_restringido, nodos_permitidos)

for i, (ruta, costo) in enumerate(mejores_rutas, 1):
    print(f"Ruta {i}: {ruta}, Costo: {costo}")

mapa = folium.Map(location=list(nodos_coordenadas.values())[0][::-1], zoom_start=14)

for i in range(len(mejores_rutas[0][0])-1):
    camino_nodos = grafo[mejores_rutas[0][0][i]][mejores_rutas[0][0][i+1]]['camino']
    camino_nodos = camino_nodos.replace('MULTILINESTRING((', '')
    camino_nodos = camino_nodos.replace('))', '')
    camino_nodos = camino_nodos.split('),(')
    for i in range(len(camino_nodos)):
        camino_nodos[i] = camino_nodos[i].split(',')
    for i in range(len(camino_nodos)):
        for j in range(len(camino_nodos[i])):
            camino_nodos[i][j] = camino_nodos[i][j].split(' ')
            camino_nodos[i][j] = [float(coor) for coor in camino_nodos[i][j]]
    archivo = MultiLineString(camino_nodos)
    dump = geojson.dumps(archivo)
    archivo = open('ruta.geojson', 'w')
    archivo.write(dump)
    archivo.close()
    gdf = gpd.read_file(dump)
    folium.GeoJson(gdf).add_to(mapa)
    
# Agregar nodos al mapa
for nodo, coordenadas in nodos_coordenadas.items():
    id_nodo = grafo.nodes[nodo].get('id', '')  # Obtener el 'id' del nodo, o una cadena vacía si no existe
    primer_nodo = mejores_rutas[0][0][0]
    ultimo_nodo = mejores_rutas[0][0][-1]
    if id_nodo in monumentos_a_recorrer:
        coordenadas = coordenadas[::-1]
        if primer_nodo == nodo:
            folium.Marker(location=coordenadas, popup=f"ID: {id_nodo}", icon=folium.Icon(color='red')).add_to(mapa)
        elif ultimo_nodo == nodo:
            folium.Marker(location=coordenadas, popup=f"ID: {id_nodo}", icon=folium.Icon(color='green')).add_to(mapa)
        else:
            folium.Marker(location=coordenadas, popup=f"ID: {id_nodo}", icon=folium.Icon(color='blue')).add_to(mapa)

mapa.save("grafo_mapa_con_id.html")