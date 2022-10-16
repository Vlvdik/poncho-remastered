from bs4 import BeautifulSoup
import requests
from config import *

def parse_horo(msg):
    URL = zz[msg]

    HEADERS = {
        'User_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }

    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('div', class_='article__item article__item_alignment_left article__item_html')
    comps = []

    for item in items:
        comps.append({
            'data': item.findAll('p')

        })

    result = "Гороскоп на сегодня: " + msg + "\n\n" + comps[0]['data'][0].get_text(strip=True) + "\n" + comps[0]['data'][1].get_text(strip=True)
    return result
