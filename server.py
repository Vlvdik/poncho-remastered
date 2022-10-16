import vk_api
import methods
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *

authorize = vk_api.VkApi(token = main_token)
longpoll = VkBotLongPoll(authorize, group_id)

### Методы для общения с ВК

def write_msg(sender, message):
    authorize.method('messages.send', {'chat_id': sender, 'message': message, "random_id": 0})

### Основная логика тут, в том числе обработка ивентов

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":
        
        msg = event.message.get('text')
        words = event.message.get('text').lower().split()
        chat = event.chat_id
        user_id = event.message.get('from_id')

        ### Логи
        print('Chat_id: [' + str(chat) + ']\nUser_id: [' + str(user_id) + ']\nMessage: [' + msg + ']')

        if msg == '/гороскоп':
            write_msg(chat, 'Укажите знак зодиака 👺')
            continue
        if words[0] == '/гороскоп':
            if words[1].lower() in zz:
                write_msg(chat, methods.parse_horo(words[1].lower()))
            else:
                write_msg(chat, 'Моими лапами невозможно найти подобный знак зодиака 😿') 
