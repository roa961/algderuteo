import requests
import json

def check_weight(type_name, subtype):
    weight = 0

    if type_name == "POLICE":
        weight += 1
        if subtype == "POLICE_VISIBLE":
            weight += 1
        elif subtype == "POLICE_HIDING":
            weight += 1

    elif type_name == "HAZARD":
        weight += 3
        if subtype == "HAZARD_ON_ROAD_TRAFFIC_LIGHT_FAULT":
            weight += 5
        elif subtype == "HAZARD_ON_ROAD_POT_HOLE":
            weight += 4
        elif subtype == "HAZARD_ON_ROAD":
            weight += 3
        elif subtype == "HAZARD_ON_SHOULDER_CAR_STOPPED":
            weight += 3
        elif subtype == "HAZARD_ON_ROAD_CONSTRUCTION":
            weight += 4
        elif subtype == "HAZARD_ON_SHOULDER_MISSING_SIGN":
            weight += 2
        elif subtype == "HAZARD_ON_SHOULDER":
            weight += 2
        elif subtype == "HAZARD_ON_SHOULDER":
            weight += 4


    elif type_name == "JAM":
        weight +=5
        if subtype == "JAM_HEAVY_TRAFFIC":
            weight += 5
        elif subtype == "JAM_MODERATE_TRAFFIC":
            weight += 4
        elif subtype == "JAM_STAND_STILL_TRAFFIC":
            weight += 6

    elif type_name == "ACCIDENT":
        weight +=7
        if subtype == "ACCIDENT_MAJOR":
            weight += 6
        elif subtype == "ACCIDENT_MINOR":
            weight += 3

    elif type_name == "ROAD_CLOSED":
        weight +=10
        if subtype == "ROAD_CLOSED_EVENT":
            weight += 8

    elif type_name == "CHIT_CHAT":
        weight +=1

    return weight

url = 'https://www.waze.com/live-map/api/georss'

params = dict(
    top='-33.348488',
    bottom='-33.605715',
    left='-70.792061',
    right='-70.514611',
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
    weight = 0
    alert_type = alert['type']
    alert_subtype = alert['subtype']
    alert_reliability = alert['reliability']
    alert_confidence = alert['confidence']
    alert_location = alert['location']
    weight = check_weight(alert_type, alert_subtype)
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
            "confidence": alert_confidence,
            "weight": weight
        }
    })

with open('./threats.geojson', 'w') as f:
    f.write(json.dumps(resulting_geojson, indent=4))