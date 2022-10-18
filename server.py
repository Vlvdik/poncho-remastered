import asyncio
import re
import vk_api
import methods
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *

authorize = vk_api.VkApi(token = main_token)
longpoll = VkBotLongPoll(authorize, group_id)

### Методы для общения с ВК
async def write_msg(sender, message):
    authorize.method('messages.send', {'chat_id': sender, 'message': message, 'random_id': 0})

### Вхождение в луп
async def main():
    for event in longpoll.listen():
        try:
            await event_handle(event)
        except:
            print("Error_log: [Handle error]")

### Основная логика тут, в том числе обработка ивентов
async def event_handle(event):    
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":
        
        msg = event.message.get('text').lower()
        words = event.message.get('text').lower().split()
        chat = event.chat_id
        user_id = event.message.get('from_id')

        ### Логи
        print('Chat_id: [' + str(chat) + ']\nUser_id: [' + str(user_id) + ']\nMessage: [' + msg + ']')

        if msg == '/гороскоп':
            await write_msg(chat, 'Укажите знак зодиака 👺')
        elif words[0] == '/гороскоп':
            if words[1] in zodiac_signs:
                await write_msg(chat, methods.parse_horoscope(words[1]))
            else:
                await write_msg(chat, 'Моими лапами невозможно найти подобный знак зодиака 😿') 
    
        if words[0] == '/расписание':
            if msg == words[0] or len(words) == 2:
                await write_msg(chat, 'Укажите КУРС и ГРУППУ!')
            else:
                await write_msg(chat, methods.parse_schedule(words[1], words[2]))

asyncio.run(main())
