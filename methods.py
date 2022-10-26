import json
import os
import random
import requests
import docx
import urllib.request
from bs4 import BeautifulSoup
from config import *

async def event_logs(name, value, user_id=''):
    if user_id:
        print(f'\n[{name}]: {value} \n[From_user]: {user_id}')
    else:
        print(f'\n[{name}]: {value}')

def get_chat_info(chat_id):
    result = '❗РЕЙТИНГ ТОКСИЧНОСТИ В ЭТОМ ЧАТЕ❗\n'

    for user in chats_info[chat_id]:
        score = chats_info[chat_id][user]
        result += f'@id{str(user)}, значение токсичности: {str(score)}\n'
    return result

def toxicity_handler(msg):
    payload = {"inputs": msg}
    response = requests.post(API_URL, headers=headers_for_model, json=payload).json()

    try:
        labels = response[0]
        
        if labels[0]['label'] == 'LABEL_1':
            return labels[0]['score'] - labels[1]['score']
        else:
            return labels[1]['score'] - labels[0]['score']
    except:
        print('Нейронка грузится')
        return 0.0

def refresh_chats_info(chat_id, user_id, msg):
    score = toxicity_handler(msg)

    if chat_id in chats_info:
        if user_id in chats_info[chat_id]:
            chats_info[chat_id][user_id] += score
        else:
            chats_info[chat_id][user_id] = score
    else:
        chats_info[chat_id] = {user_id : score}
        
def bibametr(user_id):
    res = random.randint(-100,100)
    smile = ''

    if res >= 30:
        smile = '🙀'
    else:
        smile = '😿'

    return f"@id{user_id} (Чел), биба {res} см {smile}"

def parse_horoscope(msg):   
    URL = zodiac_sign_urls[msg]

    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.findAll('div', class_='article__item article__item_alignment_left article__item_html')
    comps = []

    for item in items:
        comps.append({
            'data': item.findAll('p')
        })

    string = comps[0]['data'][0].get_text(strip=True) + "\n" + comps[0]['data'][1].get_text(strip=True)
    result = f"🌟 Гороскоп на сегодня: {msg} {zodiac_signs[msg]} \n\n🟠 {string}"
    return result

def parse_schedule(course, group, value="неделя"):
    try:
        if int(course) not in range(1,8):
            return "Курс не найден/не соответствует реальности😿"
    except:
        return "Курс это не буквы☝"

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

    if value in day_of_weeks:
        marker = False
        
        for row in table.rows:
            string = ''

            if row.cells[0].text.lower() == value:
                marker = True   
            elif row.cells[0].text.lower() in day_of_weeks:
                marker = False

            for cell in row.cells:
                if ' ' + cell.text == string:
                    string += '✅'
                    break
                elif cell.text.isnumeric():
                    string = cell.text + ')'
                    continue
                string += ' ' + cell.text

            if marker:
                result += '\n' + string
            else:
                continue
   
    else:
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

    if result.lower()[2:-1] == value:
        result = result[:-1] + '❌'

    return result + '\n\n💾Ссылка на файл с расписанием на неделю: ' + schedule_link + '_word_blank?' + url_id
