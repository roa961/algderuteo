#! /bin/bash

# This script downloads the kmz file from monumentos.gob.cl and transforms it to geojson
if [ ! -f "consejo_de_monumentos_nacionales-1_0.kmz" ]; then
    wget https://www.monumentos.gob.cl/sites/default/files/consejo_de_monumentos_nacionales-1_0.kmz
fi

if [ ! -f "doc.kml" ]; then
    unzip consejo_de_monumentos_nacionales-1_0.kmz
fi

if [ ! -f "file.geojson" ]; then
    npx @mapbox/togeojson doc.kml > file.geojson
fi

python3 replace_description.py

if [ $? -eq 0 ]; then
    echo "Success getting geojson"
else
    echo "Error"
fi
