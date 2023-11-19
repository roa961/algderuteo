import os
import requests
import json
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = 'https://www.monumentos.gob.cl'
url = 'https://www.monumentos.gob.cl/monumentos/monumentos-monumentos?f[0]=localizacion:28'

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

with open('./monumentos.json', 'w') as f:
    f.write(json.dumps(monument_info, indent=4))

names_lower = set(map(lambda x: x.lower(), names))
subs = names_lower - set([mon[0].lower() for mon in monument_info])
subs2 = set([mon[0].lower() for mon in monument_info]) - names_lower

with open('./missing_page.json', 'w') as f:
    f.write(json.dumps(list(subs), indent=4))

with open('./missing_monumento.json', 'w') as f:
    f.write(json.dumps(list(subs2), indent=4))

print(f'{len(subs) = }')
print(f'{len(subs2) = }')
print(f'{len(names_lower.intersection(set([mon[0].lower() for mon in monument_info]))) = }')
print(f'{len(monument_info) = }')
print(f'{len(names) = }')

print('Scraping images...')

momuments_inter = set([mon[0].lower() for mon in monument_info]).intersection(names_lower)

monument_info = [mon for mon in monument_info if mon[0].lower() in momuments_inter]

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

print('Done!')
