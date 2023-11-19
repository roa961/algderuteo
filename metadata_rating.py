import json
import requests
import os

api_key = 'AIzaSyCKrq10m3W__m0ug4s5Vf9MKLBDudQNLcU'
url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

with open('file_replaced.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)

id_rating_list = []

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
        feature['properties']['rating'] = rating
        print(data["candidates"][0]["photos"])

        id_rating_list.append((feature_id, rating))
    except:
        rating = 0
        feature['properties']['rating'] = rating
        feature_id = feature.get('id', None)  

        id_rating_list.append((feature_id, rating))

with open('rating_metadata.json', 'w') as id_rating_file:
    json.dump(id_rating_list, id_rating_file, indent=2)

print("rating añadido ")
