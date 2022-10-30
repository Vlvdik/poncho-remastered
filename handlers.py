import methods
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from config import *

authorize = vk_api.VkApi(token = main_token)
upload = vk_api.VkUpload(authorize)
longpoll = VkBotLongPoll(authorize, group_id)

### Методы для общения с ВК
async def write_msg(chat_id, message):
    authorize.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id': 0})

async def send_picture(chat_id, message, attachment):
    authorize.method('messages.send', {'chat_id': chat_id, 'message': message, 'attachment': attachment, 'random_id': 0})

async def kick_user(chat_id, member_id):
    authorize.method('messages.removeChatUser', {'chat_id' : chat_id, 'user_id' : member_id})

### Обработчики конкретных событий
async def help(chat_id):
    await write_msg(chat_id, helper)

async def chat_greeting(chat_id):
    await write_msg(chat_id, f"Приветствую кожанные\nЯ Пончо, буду вашим помошником. Но для этого, дайте мне права админа :3")

async def user_greeting(chat_id, member_id):
    await write_msg(chat_id, f"@id{member_id} (Кожанный), приветствую, какими судьбами?\nДа и вообще, расскажи о себе")

async def leave_user(chat_id, member_id):
    await write_msg(chat_id, f"@id{member_id} (Чел) не выдержал и свалил")

async def kick_user(chat_id, user_id, member_id):
    await write_msg(chat_id, f"@id{user_id} (Человек) отправил в далекое плавание @id{member_id} (человека)\nPress F")

async def bibametr(chat_id, user_id):
    res = random.randint(-100,100)
    smile = ''

    if res >= 30:
        smile = '🙀'
    else:
        smile = '😿'

    await write_msg(chat_id, f'@id{user_id} (Чел), биба {res} см {smile}')

async def bydlo(chat_id):
    if chats_info:
        await write_msg(chat_id, methods.get_chat_info(chat_id))
    else:
        await write_msg(chat_id, 'Инфы о чате еще нет или она отсутствует')

async def set_limit(chat_id, words):
    if len(words) > 1:
        await write_msg(chat_id, methods.set_chat_limit(chat_id, words[1]))
    else:
        await write_msg(chat_id, 'Укажите значение лимита')

async def roulette(chat_id, user_id):
    try:
        if random.randint(0,5):
            await write_msg(chat_id, 'ВСЕ ХОРОШО👍')
        else:
            await write_msg(chat_id, 'АХАХАХАХАХА, КЛАССИК🔫')
            await kick_user(chat_id, user_id)
    except:
        await write_msg(chat_id, f'@id{user_id} (Админ), это шутка, я никогда бы не выстрелил в кормильца :3')

async def horoscope(chat_id, words):
    try:
        if words[1] in zodiac_signs:
            photo = upload.photo_messages('Ваш путь к картинкам')
            attachment = "photo" + str(photo[0]['owner_id']) + "_" + str(photo[0]['id']) + "_" + str(photo[0]['access_key'])

            await send_picture(chat_id, await methods.get_horoscope(words[1]), attachment)
        else:
            await write_msg(chat_id, 'Моими лапами невозможно найти подобный знак зодиака 😿') 
    except:
        await write_msg(chat_id, 'Укажите знак зодиака 👺')


async def schedule(chat_id, words):
    try:
        await write_msg(chat_id, await methods.get_schedule(words))
    except:
        await write_msg(chat_id, 'Укажите КУРС и ГРУППУ!')

async def check_chat_limit(chat_id, user_id):           
    if chats_info[chat_id][user_id] > chats_limit[chat_id]:
        chats_info[chat_id][user_id] = 0.0
        
        await kick_user(chat_id, user_id)
        await write_msg(chat_id, 'ОСУЖДАЮ БЫДЛО')
