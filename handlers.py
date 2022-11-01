import methods
import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime
from config import *

authorize = vk_api.VkApi(token = main_token)
longpoll = VkBotLongPoll(authorize, group_id)
upload = vk_api.VkUpload(authorize)

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
    authorize.method('messages.removeChatUser', {'chat_id' : chat_id, 'user_id' : member_id})

### Обработчики конкретных событий
async def start(user_id):
    
    keyboard = VkKeyboard(one_time=False, inline=True)
    keyboard.add_button('ОЧНАЯ', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('ОЧНО-ЗАОЧНАЯ', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('ЗАОЧНАЯ', color=VkKeyboardColor.NEGATIVE)

    await write_msg(user_id, starter, keyboard)
    

async def set_form(user_id, form):
    if user_id in users_group:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('НАЗАД', color=VkKeyboardColor.NEGATIVE)

        await write_msg(user_id, 'Ты уже выбрал форму обучения, пришли мне свою группу', keyboard)
    else:    
        users_group[user_id] = {'Форма обучения': form}
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('НАЗАД', color=VkKeyboardColor.NEGATIVE)

        await write_msg(user_id, 'Теперь, пришли мне пожалуйста свою группу', keyboard)

async def set_group(user_id, group):
    if await methods.is_group(user_id, group):
        users_group[user_id]['Группа'] = group
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('СМЕНИТЬ ГРУППУ', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('НЕДЕЛЯ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ДЕНЬ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('СЕГОДНЯ', color=VkKeyboardColor.PRIMARY)

        await write_msg(user_id, 'Класс, теперь ты можешь выбирать расписание!', keyboard)
    else:
        await write_msg(user_id, 'Группа не найдена, проверьте правильность данных')

async def back(user_id):
    users_group.pop(user_id)
    await write_msg(user_id, 'OK')     
    await start(user_id)

async def push_button(user_id, msg):
    if msg in day_of_weeks:
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('ПОНЕДЕЛЬНИК', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ВТОРНИК', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('СРЕДА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('ЧЕТВЕРГ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ПЯТНИЦА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('СУББОТА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('ВОСКРЕСЕНЬЕ', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('ВЫБОР РАСПИСАНИЯ', color=VkKeyboardColor.NEGATIVE)

        await write_msg(user_id, await methods.parse_schedule(users_group[user_id]['Группа'], users_group[user_id]['Ссылка'], msg), keyboard)
    elif msg  == 'сменить группу':
        await back(user_id)
    elif msg  == 'неделя':
        await write_msg(user_id, await methods.parse_schedule(users_group[user_id]['Группа'], users_group[user_id]['Ссылка']))
    elif msg  == 'день':
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('ПОНЕДЕЛЬНИК', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ВТОРНИК', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('СРЕДА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('ЧЕТВЕРГ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ПЯТНИЦА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('СУББОТА', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('ВОСКРЕСЕНЬЕ', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('ВЫБОР РАСПИСАНИЯ', color=VkKeyboardColor.NEGATIVE)
        
        await write_msg(user_id, 'Напиши мне день недели', keyboard) 
    elif msg == 'выбор расписания':
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('СМЕНИТЬ ГРУППУ', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_button('НЕДЕЛЯ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('ДЕНЬ', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('СЕГОДНЯ', color=VkKeyboardColor.PRIMARY)

        await write_msg(user_id, 'Вернулись к расписанию', keyboard)
    elif msg  == 'сегодня':
        await write_msg(user_id, await methods.parse_schedule(users_group[user_id]['Группа'], users_group[user_id]['Ссылка'], day_of_weeks[datetime.now().day]))
    else:
        await write_msg(user_id, 'Я не знаю такой команды (квак плак)')

async def help(chat_id):
    await write_chat_msg(chat_id, helper)

async def chat_greeting(chat_id):
    await write_chat_msg(chat_id, f"Приветствую кожанные\nЯ Пончо, буду вашим помошником. Но для этого, дайте мне права админа :3")

async def user_greeting(chat_id, member_id):
    await write_chat_msg(chat_id, f"@id{member_id} (Кожанный), приветствую, какими судьбами?\nДа и вообще, расскажи о себе")

async def leave_user(chat_id, member_id):
    await write_chat_msg(chat_id, f"@id{member_id} (Чел) не выдержал и свалил")

async def kick_user(chat_id, user_id, member_id):
    await write_chat_msg(chat_id, f"@id{user_id} (Человек) отправил в далекое плавание @id{member_id} (человека)\nPress F")



async def bibametr(chat_id, user_id):
    res = random.randint(-100,100)
    smile = ''

    if res >= 30:
        smile = '🙀'
    else:
        smile = '😿'

    await write_chat_msg(chat_id, f'@id{user_id} (Чел), биба {res} см {smile}')

async def set_chat_limit(chat_id, words):
    if len(words) > 1:
        try:
            chats_limit[chat_id] = float(words[1])
        
            if float(words[1]) == 0.0:
                chats_limit.pop(chat_id, None)

            await write_chat_msg(chat_id, 'Задано')
        except:
            await write_chat_msg(chat_id, 'Задан неккоректный лимит')
    else:
        await write_chat_msg(chat_id, 'Укажите значение лимита')


async def get_chat_info(chat_id):
    if chats_info:
        result = '❗РЕЙТИНГ ТОКСИЧНОСТИ В ЭТОМ ЧАТЕ❗\n\nБыдло #1: '
        chats_info[chat_id] = dict(sorted(chats_info[chat_id].items(), key=lambda x: x[1], reverse=True))

        for user in chats_info[chat_id]:
            score = chats_info[chat_id][user]
            result += f'@id{str(user)}, значение токсичности: {str(round(score, 3))}\n'
        
        await write_chat_msg(chat_id, result)
    else:
        await write_chat_msg(chat_id, 'Инфы о чате еще нет или она отсутствует')

async def roulette(chat_id, user_id):
    try:
        if random.randint(0,5):
            await write_chat_msg(chat_id, 'ВСЕ ХОРОШО👍')
        else:
            await write_chat_msg(chat_id, 'АХАХАХАХАХА, КЛАССИК🔫')
            await kick_user(chat_id, user_id)
    except:
        await write_chat_msg(chat_id, f'@id{user_id} (Админ), это шутка, я никогда бы не выстрелил в кормильца :3')

async def horoscope(chat_id, words):
    try:
        if words[1] in zodiac_signs:
            photo = upload.photo_messages('Ваш путь к картинке')
            attachment = "photo" + str(photo[0]['owner_id']) + "_" + str(photo[0]['id']) + "_" + str(photo[0]['access_key'])

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

async def check_chat_limit(chat_id, user_id):           
    if chats_info[chat_id][user_id] > chats_limit[chat_id]:
        chats_info[chat_id][user_id] = 0.0
        
        await kick_user(chat_id, user_id)
        await write_chat_msg(chat_id, 'ОСУЖДАЮ БЫДЛО')
