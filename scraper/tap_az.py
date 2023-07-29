import json
import re

import requests
from bs4 import BeautifulSoup

from database.mongo_db import Database


def parse():
    url = 'https://tap.az/elanlar?log=true&q%5Bkeywords%5D=piano&q%5Bregion_id%5D='
    req = requests.get(url=url)
    soup = BeautifulSoup(req.text, 'html.parser')
    pianos = soup.find_all('div', class_='products-i rounded')

    items = []

    for piano in pianos:
        image_url = piano.find('img')['src']
        price = piano.find(class_='price-val').text.strip()
        name = piano.find(class_='products-name').text.strip()
        created_at = piano.find(class_='products-created').text.strip()
        link = piano.find(class_='products-link')['href']
        link = f'https://tap.az{link}'
        id = re.findall(r'\d+', link)
            
        items.append({"_id": int(''.join(id)), "name": name, "price": price, "created": created_at, "link": link, 'image_url': f'https:{image_url}'})
    
    db = Database()
    db.insert_pianos(items)
