import re

from bs4 import BeautifulSoup
from selenium import webdriver

from database.mongo_db import Database
from utils.url import url_changer


def parse_and_save(user_id: str, item_name: str):
    
    changed_url = url_changer(item_name)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Инициализация WebDriver
    driver = webdriver.Chrome(options=options)

    url = f'https://tap.az/elanlar?order=&q%5Buser_id%5D=&q%5Bcontact_id%5D=&q%5Bprice%5D%5B%5D=&q%5Bprice%5D%5B%5D=&q%5Bregion_id%5D=&q%5Bkeywords%5D={changed_url}'

    # Запрос к странице
    driver.get(url)

    # Получение HTML содержимого страницы
    soup = BeautifulSoup(driver.page_source, 'html.parser')

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

        items.append({"_id": int(''.join(id)), "name": name, "price": price, "created": created_at, "link": link, 'image_url': f'https:{image_url}', 'user_id': user_id})

    db = Database()
    db.insert_items(user_id, items)
    driver.quit()
