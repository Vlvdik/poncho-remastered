import asyncio
import vk_api
import methods
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *

authorize = vk_api.VkApi(token = main_token)
upload = vk_api.VkUpload(authorize)
longpoll = VkBotLongPoll(authorize, group_id)
log = methods.event_logs

### Методы для общения с ВК
async def write_msg(sender, message):
    authorize.method('messages.send', {'chat_id': sender, 'message': message, 'random_id': 0})

async def send_picture(sender, message, attachment):
    authorize.method('messages.send', {'chat_id': sender, 'message': message, 'attachment': attachment, 'random_id': 0})

### Вхождение в луп
async def main():
    for event in longpoll.listen():
        try:
            await event_handle(event)
        except:
            methods.event_logs('Server_error', '5XX')

### Основная логика тут, в том числе обработка ивентов
async def event_handle(event):
    try:

        ### Часто использующиеся параметры
        msg = event.message.get('text').lower()
        words = event.message.get('text').lower().split()
        chat = event.chat_id
        user_id = event.message.get('from_id')    

        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":
            
            await log('New_message', msg, user_id)

            if msg == '/help':
                await write_msg(chat, helper)

            if msg == '/гороскоп':
                await write_msg(chat, 'Укажите знак зодиака 👺')
            elif words[0] == '/гороскоп':
                if words[1] in zodiac_signs:
                    photo = upload.photo_messages('uploads/Кот_' + words[1] + '.png')
                    attachment = "photo" + str(photo[0]['owner_id']) + "_" + str(photo[0]['id']) + "_" + str(photo[0]['access_key'])
                    await send_picture(chat, methods.parse_horoscope(words[1]), attachment)
                else:
                    await write_msg(chat, 'Моими лапами невозможно найти подобный знак зодиака 😿') 

            if words[0] == '/расписание':
                if msg == words[0] or len(words) == 2:
                    await write_msg(chat, 'Укажите КУРС и ГРУППУ!')
                elif len(words) > 3:
                    await write_msg(chat, methods.parse_schedule(words[1], words[2], words[3]))
                else:
                    await write_msg(chat, methods.parse_schedule(words[1], words[2]))
    
        elif event.type == VkBotEventType.MESSAGE_NEW and (event.message.action.get('type') == 'chat_invite_user' or event.message.action.get('type') == 'chat_invite_user_by_link'):
            member_id = event.message.action.get('member_id')

            await log('New_user', member_id)
            await write_msg(event.chat_id, f"@id{member_id} (Странник), привет, какими судьбами?")
    
        elif event.type == VkBotEventType.MESSAGE_NEW and event.message.action.get('type') == 'chat_kick_user':
            member_id = event.message.action.get('member_id')

            await log('Kick_user', member_id)
            await write_msg(event.chat_id, f"@id{user_id} (Человек) отправил в далекое плавание @id{member_id} (человека)\nPress F")
    except:
        await methods.event_logs('Handle_error', 'undefiend event')

asyncio.run(main())
