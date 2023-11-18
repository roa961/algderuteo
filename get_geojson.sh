#! /bin/bash

# This script downloads the kmz file from monumentos.gob.cl and transforms it to geojson
if [ ! -f "monumentos.kmz" ]; then
    wget https://www.monumentos.gob.cl/sites/default/files/consejo_de_monumentos_nacionales-1_0.kmz
fi

if [ ! -f "monumentos.kml" ]; then
    unzip consejo_de_monumentos_nacionales-1_0.kmz
fi

if [ ! -f "monumentos.geojson" ]; then
    npx @mapbox/togeojson monumentos.kml > monumentos.geojson
fi

python3 replace_description.py

if [ $? -eq 0 ]; then
    echo "Success getting geojson"
else
    echo "Error"
fi