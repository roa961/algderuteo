import json
import psycopg2

with open('metadata_rating.json') as json_file1:
    rating = json.load(json_file1)
with open('metadata_description.json') as json_file2:
    description = json.load(json_file2)
with open('metadata_images.json') as json_file3:
    images = json.load(json_file3)

conn = psycopg2.connect(
    dbname="monumentos",
    user="postgres",
    password="postgres",
    host="172.18.0.2",
    port="5432"
)
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        id TEXT,
        nombre TEXT,
        descripcion TEXT,
        rating varchar(5),
        imagenes TEXT
    )
''')

for rat in rating:
    cursor.execute('''
        INSERT INTO metadata (id, nombre, rating )
        VALUES (%s, %s, %s)
    ''', (rat['id'], rat['name'], rat['rating']))

for desc in description:
    cursor.execute('''
        UPDATE metadata SET descripcion = %s
        where id = %s
    ''', (desc['description'], desc['id']) )

for img in images:
    cursor.execute('''
        UPDATE metadata SET imagenes = %s
        where id = %s
    ''', (img['img'], img['id']) )


conn.commit()
conn.close()
