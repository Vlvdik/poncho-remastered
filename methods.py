import os
import requests
import docx
import urllib.request
from bs4 import BeautifulSoup
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

def parse_schedule(course, group):
    
    HEADERS = {
        'User_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }

    ###Тянем ссылку на расписание группы
    response = requests.get(schedule_link + "_groups?i=0&f=0&k=" + course, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find('td', string=group.upper())
    
    if items == None:
        return 'Группа не найдена/не существует 😢'
    else:
        url_id = items.find_next('a').get('href')[22:]

    ###Тянем само расписание 
    
    filename = 'Schedule_' + group.upper() + '.docx'
    urllib.request.urlretrieve(schedule_link + '_word_blank?' + url_id, filename)
    doc = docx.Document(filename)
    table = doc.tables[0]
    result = ''
    last_string = ''
    for row in table.rows:
        string = ''
        for cell in row.cells:
            if cell.text.lower() == 'пара':
                break
            elif ' ' + cell.text == string:
                break
            elif cell.text.isnumeric():
                string = cell.text + ')'
                continue
            string += ' ' + cell.text
        
        if string.lower()[1:] in day_of_weeks:
            try:
                string += '✅'
                if string[1:-1].lower() == "воскресенье":
                    string = string[:-1]
                    string += '❌'

                if last_string[1:-1].lower() in day_of_weeks:
                    result = result[:-1]
                    result += '❌'
            except:
                continue
        if string != '':
            last_string = string
        result += '\n' + string
    
    os.remove(filename)

    return result + '\n\n💾Ссылка на файл с расписанием: ' + schedule_link + '_word_blank?' + url_id
