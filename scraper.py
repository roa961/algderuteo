import os
import requests
import json
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = 'https://www.monumentos.gob.cl'
url = 'https://www.monumentos.gob.cl/monumentos/monumentos-monumentos?f[0]=localizacion:28'

mismatching_data = {
    'iglesia quinta bella, ubicada en terrenos de la escuela perú (e-n°126)': 'Iglesia Quinta Bella',
    'estadio víctor jara (estadio chile)': 'Estadio Víctor Jara',
    'club de septiembre': 'Club de Septiembre (Casa Edwards)',
    'iglesia y convento del buen pastor': 'Iglesia y Convento Buen Pastor',
    'mural pintado por pedro lira': 'Mural de Pedro Lira',
    'actual casa de la cultura de ñuñoa, incluido el parque que lo rodea': 'Casa de la Cultura de Ñuñoa (Palacio Ossa)',
    'intendencia de santiago': 'Intendencia de Santiago (Ex edificio del Diario Ilustrado)',
    'casa de lo matta y los terrenos adyacentes': 'Casa de Lo Matta',
    'patio nº 29, actual nº 162, del cementerio general': 'Patio N°29, actual N° 162, del Cementerio General',
    'casa de asturias nº 400': 'Casa de Asturias N°400',
    'edificio del congreso nacional y los jardines que le rodean': 'Edificio del Congreso Nacional',
    "iglesia del santísimo sacramento de santiago": 'Iglesia del Santísimo Sacramento',
    'inmueble conocido como casa de los diez': 'Casa de Los Diez',
    'sitio de memoria centro de detención denominado "venda sexy - discoteque"': 'Sitio de memoria centro de detención denominado Venda Sexy - Discoteque',
    'las casas y parque de peñalolén': 'Casas y Parque de Peñalolén (Parque Arrieta)',
    'pabellón valentín errazuriz y otros pabellones del hospital san borja arriarán': 'Pabellón Valentín Errázuriz y otros pabellones del Hospital San Borja Arriarán',
    'teatro huemul': 'Teatro Huemúl',
    'edificio de la antigua cervecería de andrés ebner': 'Cervecería de Andrés Ebner',
    'ex caja de crédito hipotecario': 'Edificio de la ex Caja de Crédito Hipotecario',
    'estación mapocho': 'Estacion Mapocho (CCEM)',
    'palacio de la ex nunciatura apostólica': 'Palacio de la Ex-Nunciatura Apostólica',
    'iglesia las agustinas y la construcción anexa que es parte del antiguo convento': 'Iglesia de Las Agustinas',
    'museo nacional de bellas artes comprendiento también la parte ocupada actualmente por el museo de arte contemporáneo': 'Museo Nacional de Bellas Artes, comprendiendo también la parte ocupada actualmente por el Museo de Arte Contemporáneo',
    'edificio denominado ex casa rivas y casa montero': 'Ex Casa Rivas, conocida también como la antigua Ferretería Montero',
    'las casas de san ignacio de quilicura': 'Casas de San Ignacio de Quilicura',
    'iglesia santa ana, con su plazoleta': 'Iglesia Santa Ana',
    'consultorio externo del hospital san juan de dios (ex facultad de agricultura de la universidad de chile en la quinta normal)': 'Consultorio Externo del Hospital San Juan de Dios',
    'inmueble del museo benjamín vicuña mackenna': 'Museo Benjamín Vicuña Mackenna',
    'iglesia de la merced y la parte que queda del convento de la merced': 'Iglesia de La Merced y parte del Convento',
    'casa de administración del ex recinto de detención tres y cuatro álamos': 'Campo de Prisioneros Políticos Tres y Cuatro Álamos',
    'casas de la chacra manquehue': 'Casas de La Chacra Manquehue (Lo Gallo)',
    'palacio cousiño y sus jardines': 'Palacio Cousiño y Jardines',
    'edificio de la ex escuela de artes y oficios': 'Escuela de Artes y Oficios',
    'municipalidad de santiago': 'Municipalidad de Santiago (Edificio Consistorial Santiago)',
    'edificio y parque del instituto cultural de las condes': 'Casa y Parque del Instituto Cultural de las Condes, ex Chacra el Rosario',
    'cerro santa lucía de santiago': 'Cerro Santa Lucía',
    'edificio del palacio de los tribunales de justicia': 'Palacio de los Tribunales de Justicia',
    'iglesia nuestra señora de la divina providencia': 'Iglesia Parroquial Nuestra Señora de La Divina Providencia con su casa parroquial y construcciones adyacentes',
    'edificio del ex teatro carrera': 'Teatro Carrera',
    'sede de los trabajadores de la construcción, excavadores y alcantarilleros': 'Sede Social y Espacio de Memoria de los trabajadores de la construcción, excavadores y alcantarilleros de la Región Metropolitana',
    'iglesia de la viñita': 'Iglesia La Viñita',
    'edificio ex arsenales de guerra': 'Ex Arsenales de Guerra',
    'edificio de la ex escuela militar, actual escuela de suboficiales del ejército': 'Antigua Escuela Militar',
    'edificio de la casa central de la universidad de chile': 'Casa Central de la Universidad de Chile',
    'inmueble ubicado en calle londres nº 40 (ex londres nº 38)': 'Londres 38. Espacio de Memorias. Ex centro clandestino de detención, tortura, ejecución y desaparición forzada',
    'iglesia de san vicente ferrer': 'Iglesia de San Vicente Ferrer de Los Dominicos',
    'inmueble denominado casona de las condes y su entorno': 'Casona de Las Condes',
    'las casas patronales, bodegas y parque del antiguo fundo el salto': 'Casas patronales, bodegas y parque del ex Fundo El Salto o Palacio Riesco',
    'edificio del mercado central de santiago': 'Mercado Central',
    'monasterio benedictino': 'Iglesia y conjunto de edificios del Monasterio Benedictino',
    'casa patronal ex chacra ochagavía': 'Casa patronal ex chacra Ochagavía',
    'mural obra de maría martner y de juan o´gorman del balneario tupahue': 'Mural obra de María Martner y de Juan O\'Gorman del Balneario Tupahue',
    'consultorio nº1 doctor ramón corbalán melgarejo': 'Consultorio N°1 Doctor Ramón Corbalán Melgarejo',
    'inmueble ubicado en avenida francia nº 1442': 'Casa de Av. Francia N° 1442',
    'iglesia y convento de santo domingo': 'Iglesia de Santo Domingo',
    'las bodegas de la viña santa carolina': 'Bodegas de la Viña Santa Carolina',
    'mural "el primer gol del pueblo chileno" de roberto matta': 'Mural El primer Gol del Pueblo Chileno de Roberto Matta',
    'casa llamada "lo contador"': 'Casa lo Contador',
    'todos los restos del puente de cal y canto de santiago': 'Restos del Puente Cal y Canto',
    'palacio de la moneda - antigua "real casa de moneda"': 'Palacio de La Moneda - Antigua Real casa de Moneda',
    'inmueble denominado ex pabellón de la exposición parís de santiago': 'Ex Pabellón de la Exposición de París',
    'ex palacio de la real audiencia y cajas reales': 'Palacio de la Real Audiencia y Cajas Reales',
    'casa y parque de la quinta las rosas de maipú': 'Casa y Parque de la Quinta de Las Rosas de Maipú'
}

def download_image(url, name):
    response = requests.get(url)
    with open(f'img/{name}.jpg', 'wb') as f:
        f.write(response.content)

def scrape_monuments(page):
    response = requests.get(page)
    soup = BeautifulSoup(response.content, 'lxml')
    monumentos = soup.find_all('h2', class_='field-content')
    return [(monumento.text, monumento.find('a')['href']) for monumento in monumentos]

def scrape_images(monument):
    name, url = monument
    name = name.replace(' ', '_')

    response = requests.get(f'{base_url}{url}')

    soup = BeautifulSoup(response.content, 'lxml')

    slides = soup.find_all('ul', class_='slides', recursive=True)

    if len(slides) == 0:
        print(f'{name} has no slides')
        return None
    
    slides = slides[0].find_all('li')

    if len(slides) == 0:
        print(f'{name} has no images')
        return None

    print(f'{name} has {len(slides)} images')

    os.makedirs(f'img/{name}', exist_ok=True)

    return [(slide.find('img')['src'], f'{name}/{i}') for i, slide in enumerate(slides) if slide.find('img') is not None]

def add_differing_names(monument_info):
    new_monument_info = []
    for monument in monument_info:
        name, url = monument
        if name.lower() in mismatching_data:
            new_monument_info.append((mismatching_data[name.lower()], url))

    return new_monument_info

parser = argparse.ArgumentParser(description='Scrape monumentos.gob.cl')
parser.add_argument('file', metavar='file', type=str, help='geojson file to scrape', default=None)
args = parser.parse_args()

os.makedirs('img', exist_ok=True)

with open(args.file if args.file is not None else './file_replaced.geojson', 'r', encoding='utf-8') as f:
    data = json.loads(f.read())

names = set([feat['properties']['name'] for feat in data['features']])

print('Requesting landing page...')

response = requests.get(url)

monument_info = []

soup = BeautifulSoup(response.content, 'lxml')

monumentos = soup.find_all('h2', class_='field-content')

for monumento in monumentos:
    monument_info.append((monumento.text, monumento.find('a')['href']))

num_pages = int(soup.find('li', class_='pager-last last').find('a')['href'].split('page=')[1])

print('Requesting other pages...')

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(scrape_monuments, f'{url}&page={i}') for i in range(1, num_pages+1)]

    for future in as_completed(futures):
        monument_info.extend(future.result())

names_lower = set(map(lambda x: x.lower(), names))
page_names_lower = set(map(lambda x: " ".join(x[0].split()).lower(), monument_info))
missing_file = names_lower - page_names_lower
missing_page = page_names_lower - names_lower

print('Scraping images...')

modified_monument_info = add_differing_names(monument_info)

momuments_inter = set([mon[0].lower() for mon in monument_info]).intersection(names_lower)

monument_info = [mon for mon in monument_info if mon[0].lower() in momuments_inter]

monument_info.extend(modified_monument_info)

images = []

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(scrape_images, monument) for monument in monument_info]

    for future in as_completed(futures):
        if future.result() is not None:
            images.extend(future.result())

print('Downloading images...')

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_image, image[0], image[1]) for image in images]

    for future in as_completed(futures):
        future.result()

id_to_image_path= {}

for feature in data['features']:
    names = [mon[0] for mon in monument_info]

    if feature['properties']['name'] not in names:
        continue

    idx = names.index(feature['properties']['name'])

    name, _ = monument_info[idx]

    id_mon = feature['id']

    id_to_image_path[id_mon] = f"img/{name.replace(' ', '_')}"

with open('metadata_images.json', 'w') as f:
    json.dump(id_to_image_path, f, indent=4)

print('Done!')
