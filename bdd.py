import psycopg2

# Parámetros de conexión a la base de datos
dbname = 'monumentos'
user = 'postgres'
password = 'postgres'
host = 'localhost'  # Por ejemplo, 'localhost' si está en tu máquina local
port = '25432'  # Por defecto, el puerto de PostgreSQL es 5432

# Crear la cadena de conexión
connection_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

# Establecer la conexión
conn = psycopg2.connect(connection_string)

# Crear un objeto cursor para ejecutar consultas SQL
cursor = conn.cursor()

def Dijsktra(coordenada_inicio, coordenada_destino):
    query = f"""-- find he nearest vertex to the start longitude/latitude
        WITH start AS (
        SELECT topo.source --could also be topo.target
        FROM calles_2po_4pgr as topo
        ORDER BY topo.geom_way <-> ST_SetSRID(
        ST_GeomFromText('POINT ({' '.join(coordenada_inicio)})'),
        4326)
        LIMIT 1
        ),
        -- find the nearest vertex to the destination longitude/latitude
        destination AS (
        SELECT topo.source --could also be topo.target
        FROM calles_2po_4pgr as topo
        ORDER BY topo.geom_way <-> ST_SetSRID(
        ST_GeomFromText('POINT ({' '.join(coordenada_destino)})'),
        4326)
        LIMIT 1
        )
        -- use Dijsktra and join with the geometries
        SELECT ST_AsText(ST_Union(geom_way))
        FROM pgr_dijkstra('
        SELECT id,false,
        source,
        target,
        ST_Length(ST_Transform(geom_way, 3857)) AS cost
        FROM calles_2po_4pgr',
        array(SELECT source FROM start),
        array(SELECT source FROM destination),
        directed := true) AS di
        JOIN calles_2po_4pgr AS pt
        ON di.edge = pt.id;
        """
    return query

def Dijsktraa(coordenada_inicio, coordenada_destino):

    query = f"""WITH start AS (
                SELECT topo.source --could also be topo.target
                FROM calles_2po_4pgr as topo where kmh > 15
                ORDER BY topo.geom_way <-> ST_SetSRID(
                    ST_GeomFromText('POINT ({' '.join(coordenada_inicio)})'),
                4326)
                LIMIT 1
                ),
                -- find the nearest vertex to the destination longitude/latitude
                destination AS (
                SELECT topo.source --could also be topo.target
                FROM calles_2po_4pgr as topo where kmh > 15
                ORDER BY topo.geom_way <-> ST_SetSRID(
                    ST_GeomFromText('POINT ({' '.join(coordenada_destino)})'),
                4326)
                LIMIT 1
                )
                -- use Dijsktra and join with the geometries
                SELECT ST_AsText(ST_Union(geom_way))
                FROM pgr_dijkstra('
                    SELECT id,
                        source,
                        target,
                        ST_Length(ST_Transform(geom_way, 3857)) AS cost
                        FROM calles_2po_4pgr where kmh > 15',
                    array(SELECT source FROM start),
                    array(SELECT source FROM destination),
                    directed := true) AS di
                JOIN   calles_2po_4pgr AS pt
                ON   di.edge = pt.id;"""
    return query

def Astar(coordenada_inicio, coordenada_destino):
    query = f"""-- find he nearest vertex to the start longitude/latitude
                WITH start AS (
                SELECT topo.source --could also be topo.target
                FROM calles_2po_4pgr as topo where kmh > 15
                ORDER BY topo.geom_way <-> ST_SetSRID(
                ST_GeomFromText('POINT ({' '.join(coordenada_inicio)})'),
                4326)
                LIMIT 1
                ),
                -- find the nearest vertex to the destination longitude/latitude
                destination AS (
                SELECT topo.source --could also be topo.target
                FROM calles_2po_4pgr as topo where kmh > 15
                ORDER BY topo.geom_way <-> ST_SetSRID(
                ST_GeomFromText('POINT ({' '.join(coordenada_destino)})'),
                4326)
                LIMIT 1
                )
                SELECT ST_AsText(ST_Union(geom_way))
                FROM pgr_aStar('
                SELECT id, source, target, ST_Length(ST_Transform(geom_way, 3857)) AS cost,
                reverse_cost,x1, y1, x2, y2
                FROM calles_2po_4pgr where kmh > 15',
                array(SELECT source FROM start),
                array(SELECT source FROM destination),
                directed := true, heuristic := 2) AS di
                JOIN calles_2po_4pgr AS pt
                ON di.edge = pt.id;"""
    return query
def get_costo(coordenada_inicio, coordenada_fin):
    query = f"""WITH start AS (
    SELECT topo.source
    FROM calles_2po_4pgr as topo
    WHERE kmh > 15
    ORDER BY topo.geom_way <-> ST_SetSRID(
        ST_GeomFromText('POINT ({' '.join(coordenada_inicio)})'), 4326
    )
    LIMIT 1
),
destination AS (
    SELECT topo.source
    FROM calles_2po_4pgr as topo
    WHERE kmh > 15
    ORDER BY topo.geom_way <-> ST_SetSRID(
        ST_GeomFromText('POINT ({' '.join(coordenada_fin)})'), 4326
    )
    LIMIT 1
)
SELECT
    ST_AsText(ST_Union(geom_way)),
    SUM(pt.cost) AS total_cost
FROM pgr_dijkstra(
    'SELECT id,
        source,
        target,
        ST_Length(ST_Transform(geom_way, 3857)) AS cost
        FROM calles_2po_4pgr WHERE kmh > 15',
    ARRAY(SELECT source FROM start),
    ARRAY(SELECT source FROM destination),
    directed := true
) AS di
JOIN calles_2po_4pgr AS pt
ON di.edge = pt.id;"""
    return query