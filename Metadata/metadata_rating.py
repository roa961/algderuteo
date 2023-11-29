import json
import requests

api_key = '' #Se debe agregar API key de Google maps

url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

with open('file_replaced.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

id_name_rating_list = []

for feature in geojson_data['features']:
    params = {
        'fields': 'formatted_address,name,rating,opening_hours,geometry,photos',
        'input': feature['properties']['name'],
        'inputtype': 'textquery',
        'key': api_key
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        rating = data["candidates"][0]["rating"]
        feature_id = feature.get('id', None)  
        feature_name = feature['properties'].get('name', None) 
        feature['properties']['rating'] = rating
        print(data["candidates"][0]["photos"])

        id_name_rating_list.append({'id': feature_id, 'name': feature_name, 'rating': rating})
    except:
        rating = 0
        feature['properties']['rating'] = rating
        feature_id = feature.get('id', None)  
        feature_name = feature['properties'].get('name', None)  

        id_name_rating_list.append({'id': feature_id, 'name': feature_name, 'rating': rating})

with open('metadata_rating.json', 'w') as id_name_rating_file:
    json.dump(id_name_rating_list, id_name_rating_file, indent=2)

