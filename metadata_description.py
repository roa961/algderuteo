import json


with open('file_replaced.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

desc_list = []

for feature in geojson_data['features']:

    
    feature_id = feature.get('id', None)  
    desc = feature['properties']['description']
    desc_list.append({'id': feature_id, 'description': desc})


with open('metadata_description.json', 'w') as descript:
    json.dump(desc_list, descript, indent=2)

