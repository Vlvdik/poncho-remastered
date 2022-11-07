import aiofiles.os
import docx
import db_methods
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
                    return labels[0][0]['score'] - labels[0][1]['score']
                else:
                    return labels[0][1]['score'] - labels[0][0]['score']
            except:
                return 0.0

async def get_horoscope(sign, period='сегодня'):    
    if period not in zodiac_sign_route:
        period = 'сегодня'
    async with ClientSession() as session:
        async with session.get(zodiac_sign_urls[sign] + zodiac_sign_route[period], headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.findAll('div', class_='article__item article__item_alignment_left article__item_html')
            comps = []

            for item in items:
                comps.append({
                'data': item.findAll('p')
                })

            string = comps[0]['data'][0].get_text(strip=True) + "\n" + comps[0]['data'][1].get_text(strip=True)
            result = f"🌟 Гороскоп на {period}: {sign} {zodiac_signs[sign]} \n\n🟠 {string}"

            return result

async def is_group(user_id, group):
    async with ClientSession() as session:
        form = await db_methods.get_user_form(user_id)
        async with session.get(schedule_link + '_groups?i=0&f=' + forms[form] + '&k=0', headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.find('td', string=group.upper())

            if items == None:
                return False
            else:
                await db_methods.insert_link(user_id, schedule_link + '_word_blank?' + items.find_next('a').get('href')[22:])
                return True

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
    remote_marker = False
    result = ''
    last_string = ''

    if value in day_of_weeks:
        day_marker = False
        
        for row in table.rows[5:]:
            string = ''
            if len(row.cells[0].text.split()) > 0:
                if row.cells[0].text.split()[0].lower() == value:
                    day_marker = True   
                elif row.cells[0].text.split()[0].lower() in day_of_weeks:
                    day_marker = False

            for cell in row.cells:
                if ' ' + cell.text == string:
                    string += '✅'
                    break
                if len(cell.text.split()) > 0 and cell.text.split()[0] == 'Дистанционная' and day_marker:
                    remote_marker = True
                elif cell.text.isnumeric():
                    string = cell.text + ')'
                    continue
                string += ' ' + cell.text
            
            if day_marker:
                result += '\n' + string
            else:
                continue
   
    else:
        for row in table.rows[5:]:
            string = ''

            for cell in row.cells:
                if len(cell.text.split()) > 0 and cell.text.split()[0] == 'Дистанционная':
                    remote_marker = True
                elif ' ' + cell.text == string:
                    break
                elif cell.text.isnumeric():
                    string = cell.text + ')'
                    continue
                string += ' ' + cell.text

            if string.split()[0].lower() in day_of_weeks:
                
                result += '\n'
                
                try:
                    string += '✅'

                    if last_string[:-1] in day_of_weeks or last_string in day_of_weeks:
                        result = result[:-2]
                        result += '❌\n'
                    if string.split()[0].lower()[:-1] == "воскресенье":
                        string = string[:-1]
                        string += '❌'
                except:
                    continue

            if string != '':
                last_string = string.split()[0].lower()
            result += '\n' + string 

    await aiofiles.os.remove(filename)
    
    if result.lower()[2:-1] == value or result[-2] == ')':
        result = result[:-1] + '❌'
    
    if remote_marker:
        result += '\n\n🌐Ссылка для просмотра удаленки: ' + remote_link
    
    return result + '\n\n💾Ссылка на файл с расписанием на неделю: ' + file_link
