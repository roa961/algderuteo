import json
import requests


with open('file_replaced.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

description_list_loc = []

for feature in geojson_data['features']:

    feature_id = feature.get('id', None)  
    desc = feature['properties']['description'] 
    description_list_loc.append((feature_id, desc))


with open('desc_metadata.json', 'w') as id_desc:
    json.dump(description_list_loc, id_desc, indent=2)

print("localizacion desc añadido ")
