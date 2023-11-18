import requests
import json

url = 'https://www.waze.com/live-map/api/georss'

params = dict(
    top='-32.916667',
    bottom='-34.316667',
    left='-71.716667',
    right='-69.783333',
    env='row',
    types='alerts,traffic'
)

resulting_geojson = {
    "type": "FeatureCollection",
    "features": []
}

resp = requests.get(url=url, params=params)

res = resp.json()

alerts = res['alerts']

for i, alert in enumerate(alerts):
    alert_type = alert['type']
    alert_subtype = alert['subtype']
    alert_reliability = alert['reliability']
    alert_confidence = alert['confidence']
    alert_location = alert['location']

    x, y = alert_location['x'], alert_location['y']

    resulting_geojson['features'].append({
        "type": "Feature",
        "id": f"alert_{i:04d}",
        "geometry": {
            "type": "Point",
            "coordinates": [
                x,
                y
            ]
        },
        "properties": {
            "type": alert_type,
            "subtype": alert_subtype,
            "reliability": alert_reliability,
            "confidence": alert_confidence
        }
    })

with open('./threats.geojson', 'w') as f:
    f.write(json.dumps(resulting_geojson, indent=4))