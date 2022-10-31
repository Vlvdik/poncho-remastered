import aiofiles.os
import docx
import urllib.request
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from config import *

async def toxicity_handler(msg):
    payload = {"inputs": msg}
    
    async with ClientSession() as session:
        async with session.post(API_URL, headers=headers_for_model, json=payload) as response:
            try:
                labels = await response.json()
                
                if labels[0][0]['label'] == 'LABEL_1':
                    return round(labels[0][0]['score'] - labels[0][1]['score'], 3)
                else:
                    return round(labels[0][1]['score'] - labels[0][0]['score'], 3)
            except:
                return 0.0

async def refresh_chats_info(chat_id, user_id, msg):
    score = await toxicity_handler(msg)

    if chat_id in chats_info:
        if user_id in chats_info[chat_id]:
            chats_info[chat_id][user_id] += score
        else:
            chats_info[chat_id][user_id] = score
    else:
        chats_info[chat_id] = {user_id : score}

async def get_horoscope(msg):       
    async with ClientSession() as session:
        async with session.get(zodiac_sign_urls[msg], headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.findAll('div', class_='article__item article__item_alignment_left article__item_html')
            comps = []

            for item in items:
                comps.append({
                'data': item.findAll('p')
                })

            string = comps[0]['data'][0].get_text(strip=True) + "\n" + comps[0]['data'][1].get_text(strip=True)
            result = f"🌟 Гороскоп на сегодня: {msg} {zodiac_signs[msg]} \n\n🟠 {string}"

            return result

async def get_schedule(words):
    try:
        if int(words[1]) not in range(1,8):
            return "Курс не найден/не соответствует реальности😿"
    except:
        return "Курс это не буквы☝"

    ###Тянем ссылку на расписание группы
    async with ClientSession() as session:
        async with session.get(schedule_link + "_groups?i=0&f=0&k=" + words[1], headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.find('td', string=words[2].upper())
    
            if items == None:
                return 'Группа не найдена/не существует 😢'
            else:
                file_link = schedule_link + '_word_blank?' + items.find_next('a').get('href')[22:]
                filename = 'Schedule_' + words[2].upper() + '.docx'

                if len(words) > 3:
                    return await parse_schedule(filename, file_link, words[3])
                else:
                    return await parse_schedule(filename, file_link)

    ###Тянем само расписание 

async def parse_schedule(filename, file_link, value="неделя"):
    urllib.request.urlretrieve(file_link, filename)
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

    await aiofiles.os.remove(filename)

    if result.lower()[2:-1] == value:
        result = result[:-1] + '❌'
    return result + '\n\n💾Ссылка на файл с расписанием на неделю: ' + file_link
