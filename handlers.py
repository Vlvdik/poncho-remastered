import methods
import db_methods
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime
from config import *

### Налаживаем общение с ВК

authorize = vk_api.VkApi(token = main_token)
longpoll = VkBotLongPoll(authorize, group_id)
upload = vk_api.VkUpload(authorize)
start_keyboard = VkKeyboard(one_time=False)
form_keyboard = VkKeyboard(one_time=False)
back_keyboard = VkKeyboard(one_time=False)
schedule_keyboard = VkKeyboard(one_time=False)
days_keyboard = VkKeyboard(one_time=False)

### Кастомим клавы

start_keyboard.add_button('НАЧАТЬ', color=VkKeyboardColor.PRIMARY)

form_keyboard.add_button('ОЧНАЯ', color=VkKeyboardColor.POSITIVE)
form_keyboard.add_line()
form_keyboard.add_button('ОЧНО-ЗАОЧНАЯ', color=VkKeyboardColor.PRIMARY)
form_keyboard.add_line()
form_keyboard.add_button('ЗАОЧНАЯ', color=VkKeyboardColor.NEGATIVE)

back_keyboard.add_button('НАЗАД', color=VkKeyboardColor.NEGATIVE)

schedule_keyboard.add_button('СМЕНИТЬ ГРУППУ', color=VkKeyboardColor.NEGATIVE)
schedule_keyboard.add_button('НЕДЕЛЯ', color=VkKeyboardColor.POSITIVE)
schedule_keyboard.add_button('ДЕНЬ', color=VkKeyboardColor.POSITIVE)
schedule_keyboard.add_line()
schedule_keyboard.add_button('СЕГОДНЯ', color=VkKeyboardColor.PRIMARY)

days_keyboard.add_button('ПОНЕДЕЛЬНИК', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_button('ВТОРНИК', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_button('СРЕДА', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_line()
days_keyboard.add_button('ЧЕТВЕРГ', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_button('ПЯТНИЦА', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_button('СУББОТА', color=VkKeyboardColor.POSITIVE)
days_keyboard.add_line()
days_keyboard.add_button('ВОСКРЕСЕНЬЕ', color=VkKeyboardColor.SECONDARY)
days_keyboard.add_button('ВЫБОР РАСПИСАНИЯ', color=VkKeyboardColor.NEGATIVE)

### Методы для общения с ВК
async def write_msg(user_id, message, keyboard=None):
    msg = {'user_id': user_id, 'message': message, 'random_id': 0}

    if keyboard != None:
        msg['keyboard'] = keyboard.get_keyboard()

    authorize.method('messages.send', msg)

async def write_chat_msg(chat_id, message):
    authorize.method('messages.send', {'chat_id': chat_id, 'message': message, 'random_id': 0})

async def send_picture(chat_id, message, attachment):
    authorize.method('messages.send', {'chat_id': chat_id, 'message': message, 'attachment': attachment, 'random_id': 0})

async def kick_user(chat_id, member_id):
    authorize.method('messages.removeChatUser', {'chat_id' : chat_id, 'member_id' : member_id})

async def get_conversation_info(chat_id):
    return authorize.method('messages.getConversationMembers', {'peer_id': 2000000000 + chat_id, 'group_id': group_id})['items']

### Обработчики событий из лички
async def start(user_id, value='Привет, Я Пончо, твой пушистый помошник, своими лапами ищу расписания групп🐈'):
    await db_methods.insert_user(user_id)
    await write_msg(user_id, value + '\nДля начала, давай определимся с твоей формой обучения:', form_keyboard)
    
async def undefiend_command(user_id):
    if await db_methods.is_existing_user(user_id):
        await db_methods.delete_user(user_id)
    await start(user_id, 'Если это команда, то я ее не понял😿')

async def set_form(user_id, form):  
    await db_methods.insert_form(user_id, form)
    await write_msg(user_id, 'Отлично, теперь напиши мне свою группу \nЖелательно существующую😸', back_keyboard)

async def set_group(user_id, group):
    if await methods.is_group(user_id, group):
        await db_methods.insert_group(user_id, group)
        await write_msg(user_id, 'Группа установлена, супер! \n💥 Теперь ты можешь запрашивать расписание заданной группы, мрр', schedule_keyboard)
    else:
        await write_msg(user_id, 'СУЩЕСТВУЮЩУЮ группу 👺')

async def back(user_id):
    await db_methods.delete_user(user_id)   
    await start(user_id, 'Окей, давай по новой 👌🏻\n')

async def push_button(user_id, msg):
    if msg in day_of_weeks:
        group = await db_methods.get_user_link(user_id)

        await write_msg(user_id, await methods.parse_schedule('https://ies.unitech-mo.ru/schedule_list_groups?' + group[51:], await db_methods.get_user_link(user_id), msg), days_keyboard)
    elif msg  == 'сменить группу':
        await back(user_id)
    elif msg  == 'неделя':
        group = await db_methods.get_user_link(user_id)

        await write_msg(user_id, await methods.parse_schedule('https://ies.unitech-mo.ru/schedule_list_groups?' + group[51:], await db_methods.get_user_link(user_id)))
    elif msg  == 'день':
        await write_msg(user_id, 'Хорошо, теперь ты можешь выбрать конкретный день. \nP.S. Обрати внимание, что расписание выдается на ТЕКУЩУЮ неделю ❗', days_keyboard) 
    elif msg == 'выбор расписания':
        await write_msg(user_id, '👌🏻', schedule_keyboard)
    elif msg  == 'сегодня':
        group = await db_methods.get_user_link(user_id)

        await write_msg(user_id, await methods.parse_schedule('https://ies.unitech-mo.ru/schedule_list_groups?' + group[51:], await db_methods.get_user_link(user_id), day_of_weeks[datetime.now().weekday()]))
    else:
        await write_msg(user_id, 'Если это команда, то я ее не понял😿')

###Обработчики сообщений из чата

async def help(chat_id):
    await write_chat_msg(chat_id, helper)

async def chat_greeting(chat_id):
    await write_chat_msg(chat_id, "Приветствую кожанные\n🐈🐈🐈🐈🐈🐈\nЯ Пончо, буду вашим помошником, но для этого, дайте мне права админа :3\n\n Чтобы узнать, что я умею, напиши /help")

async def user_greeting(chat_id, member_id):
    await write_chat_msg(chat_id, f"@id{member_id} (Кожанный), приветствую, какими судьбами?\nДа и вообще, расскажи о себе")

async def leave_user(chat_id, member_id):
    await write_chat_msg(chat_id, f"@id{member_id} (Кожанный) не выдержал и свалил")

async def kick(chat_id, user_id, member_id):
    await write_chat_msg(chat_id, f"@id{user_id} (Кэп) отправил в далекое плавание @id{member_id} (этого морячка)\nPress F😿")

async def bibametr(chat_id, user_id):
    res = random.randint(-100,100)
    smile = ''

    if res >= 30:
        smile = '🙀'
    else:
        smile = '😿'

    await write_chat_msg(chat_id, f'@id{user_id} (Чел), биба {res} см {smile}')

async def roulette(chat_id, user_id):
    try:
        if random.randint(0,5):
            await write_chat_msg(chat_id, 'ВСЕ ХОРОШО 👍')
        else:
            await write_chat_msg(chat_id, 'АХАХАХАХАХА, КЛАССИК 🔫')
            await kick_user(chat_id, user_id)
    except:
        await write_chat_msg(chat_id, f'@id{user_id} (Админ), это шутка, я никогда бы не выстрелил в кормильца :3')

### Работа с инфой чата

async def refresh_chats_info(chat_id, user_id, msg):
    score = await methods.toxicity_handler(msg)

    if await db_methods.is_user_exist_in_current_chat(user_id, chat_id):
        if await db_methods.get_user_chat_score_info(user_id, chat_id) < CHAT_LOW_HYPER_PARAMETER:
            pass
        else:
            await db_methods.update_chat_user_score(user_id, chat_id, score)
    else:
        await db_methods.insert_chat_user_score(user_id, chat_id, score)

async def set_chat_limit(chat_id, user_id, words):
    if len(words) > 1:
        try:
            conversation_info = await get_conversation_info(chat_id)

            for user in conversation_info:
                if user['member_id'] == user_id:
                    try:
                        if user['is_admin']: 
                            try:
                                if float(words[1]) == 0.0:
                                    await db_methods.delete_chats_limit(chat_id)
                                    await write_chat_msg(chat_id, 'Лимит убран 👌🏻')
                                    break
                                else:
                                    if await db_methods.is_chat_have_limit(chat_id):
                                        await db_methods.update_chats_limit(chat_id, float(words[1]))
                                    else:
                                        await db_methods.insert_chats_limit(chat_id, float(words[1])) 
                                    await write_chat_msg(chat_id, 'Задано 👌🏻')
                                    break
                            except:
                                await write_chat_msg(chat_id, 'Задан неккоректный лимит 👺')

                    except:
                        await write_chat_msg(chat_id, 'Лимит могут задавать только администраторы беседы 👺')
        except:
            await write_chat_msg(chat_id, 'Некорректная работа операции...')
    else:
        await write_chat_msg(chat_id, 'Укажите значение лимита 👺')

async def get_chat_info(chat_id):
    if await db_methods.is_existed_chat(chat_id):
        result = ''
        number = 1
        current_chat = await db_methods.get_score_info(chat_id)

        for user in current_chat:
            user_id = str(user[0])
            result += f'👲🏽 @id{user_id} (Быдло №{number})\n'
            number += 1
        if result != '':
            await write_chat_msg(chat_id, '❗РЕЙТИНГ ТОКСИЧНОСТИ В ЭТОМ ЧАТЕ❗\n\n' + result)
        else:
            await write_chat_msg(chat_id,  'В чате нет токсиков 👍')
    else:
        await write_chat_msg(chat_id, 'Инфы о чате еще нет или она отсутствует 😿')

async def check_chat_limit(chat_id, user_id):   
    if await db_methods.is_existed_chat(chat_id):
        if await db_methods.get_user_chat_score_info(user_id, chat_id) > await db_methods.get_chat_limit(chat_id):        
            await db_methods.delete_user_from_chat(user_id, chat_id)
            await kick_user(chat_id, user_id)
            await write_chat_msg(chat_id, 'ОСУЖДАЮ')

### Работа с парсерами

async def horoscope(chat_id, words):
    try:
        if words[1] in zodiac_signs:
            photo = upload.photo_messages('Your path to img')
            attachment = "photo" + str(photo[0]['owner_id']) + "_" + str(photo[0]['id']) + "_" + str(photo[0]['access_key'])
            if len(words) > 2:
                await send_picture(chat_id, await methods.get_horoscope(words[1], words[2]), attachment)
            else:
                await send_picture(chat_id, await methods.get_horoscope(words[1]), attachment)
        else:
            await write_chat_msg(chat_id, 'Моими лапами невозможно найти подобный знак зодиака 😿') 
    except:
        await write_chat_msg(chat_id, 'Укажите знак зодиака 👺')

async def schedule(chat_id, words):
    try:
        await write_chat_msg(chat_id, await methods.get_schedule(words))
    except:
        await write_chat_msg(chat_id, 'Укажите КУРС и ГРУППУ!')
