import json
import requests
import os

url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

api_key = os.getenv('API_KEY')

with open('file_rating_updated.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)


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
        feature['properties']['rating'] = data["candidates"][0]["rating"]

        print(data["candidates"][0]["photos"])
    except:
        feature['properties']['rating'] = 0


with open('output_geojson_file.geojson', 'w') as output_file:
    json.dump(geojson_data, output_file)

print("Rating agregado a geojson")
