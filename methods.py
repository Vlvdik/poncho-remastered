import aiofiles.os
import docx
import db_methods
import random
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
                    return labels[0][0]['score'] - labels[0][1]['score'] * random.random()
                else:
                    return labels[0][1]['score'] - labels[0][0]['score'] * random.random()
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
                group = items.find_next('a').get('href')[22:]
                url = schedule_link + '_groups?' + group
                file_link = schedule_link + '_word_blank?' + group
                
                if len(words) > 3:
                    return await parse_schedule(url, file_link, words[3])
                else:
                    return await parse_schedule(url, file_link)

async def parse_schedule(url, file_link, value='Неделя'):
    async with ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            tables = soup.find_all('tbody')
            days = soup.find_all('h2')[2:]
            result = ''
            day = 0

            if value in day_of_weeks:
                for i in tables:
                    try:      
                        string = '' 
                        
                        if days[day].text.split()[0].lower() == value:
                            string += days[day].text + '✅' 

                            for j in i.find_all('tr'):
                                    if len(list(filter(None, ''.join(str(j).split('\n<td>')[1:]).split('</td>')))) > 3:
                                        for res in j:
                                            if res.text.isnumeric():
                                                if int(res.text) in range (1,9):
                                                    continue
                                                else:
                                                    pass
                                            if len(str(res).split('<hr/>')) > 1:
                                                if res.hr.previous_sibling.name == 'strong':
                                                    string += res.hr.previous_sibling.previous_sibling.text + ' / ' + res.hr.next_sibling.text
                                                else:
                                                    if res.hr.previous_sibling.name == 'a':
                                                        string += res.hr.previous_sibling.text + ' / ' + res.hr.next_sibling.next_sibling.text
                                                    else:
                                                        string += res.hr.previous_sibling.text + ' / ' + res.hr.next_sibling.text  
                                            else:
                                                string += res.text  
                                        if j.find('a'):
                                            string = string[:-1] + '📲 Место проведения: ' + ''.join(str(j.find('a').get('href')).split(' ')) + '\n'
                            if string[:-1] == days[day].text:
                                string = string[:-1] + '❌'  
                        else:
                            continue
                    except:
                        continue
                    finally:              
                        result += '\n' + string
                        day += 1
            else:
                for i in tables:
                    try:      
                        string = '' 
                        string += days[day].text + '✅' 

                        for j in i.find_all('tr'):
                                if len(list(filter(None, ''.join(str(j).split('\n<td>')[1:]).split('</td>')))) > 3:
                                    for res in j:
                                        if res.text.isnumeric():
                                            if int(res.text) in range (1,9):
                                                continue
                                            else:
                                                pass
                                        if len(str(res).split('<hr/>')) > 1:
                                            if res.hr.previous_sibling.name == 'strong':
                                                string += res.hr.previous_sibling.previous_sibling.text + ' / ' + res.hr.next_sibling.text
                                            else:
                                                if res.hr.previous_sibling.name == 'a':
                                                    string += res.hr.previous_sibling.text + ' / ' + res.hr.next_sibling.next_sibling.text
                                                else:
                                                    string += res.hr.previous_sibling.text + ' / ' + res.hr.next_sibling.text  
                                        else:
                                            string += res.text  
                                    if j.find('a'):
                                        string = string[:-1] + '📲 Место проведения: ' + ''.join(str(j.find('a').get('href')).split(' ')) + '\n'
                    except:
                        continue
                    finally:
                        if string[:-1] == days[day].text:
                            string = string[:-1] + '❌'
                    
                        result += '\n' + string
                        day += 1
            
    return result + '\n\n💾 Ссылка на файл с расписанием недели: ' + file_link
