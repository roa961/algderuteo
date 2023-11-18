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

resp = requests.get(url=url, params=params)

res = resp.json()

with open('./threats.json', 'w') as f:
    f.write(json.dumps(res, indent=4))