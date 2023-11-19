import json
from os import makedirs
import re

regex = re.compile(r'Provincia</td>\n\n<td>(.*?)</td>')

with open('./file.geojson', 'r') as f:
    text = f.read()

data = json.loads(text)

makedirs('./views', exist_ok=True)

exported_features = []

for feature in data['features']:
    id_feature = feature['id']
    filename = f'./views/{id_feature}.html'
    description = feature['properties']['description'].replace(r'\n\n', '\n').replace(r'\t\t', '')
    feature['properties']['description'] = filename
    provincia = regex.search(description).group(1).strip()
    if provincia != 'Santiago' or feature['properties']['icon'] != "files/Layer0_Symbol_84674c30_0.png":
        continue
    exported_features.append(feature)
    with open(filename, 'w') as f:
        f.write(description)

data['features'] = exported_features

with open('./file_replaced.geojson', 'w') as f:
    f.write(json.dumps(data, indent=4))
