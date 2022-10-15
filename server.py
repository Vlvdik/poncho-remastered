import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *

authorize = vk_api.VkApi(token = main_token)
longpoll = VkBotLongPoll(authorize, group_id)

def write_msg(sender, message):
    authorize.method('messages.send', {'chat_id': sender, 'message': message, "random_id": 0})

def send_picture(sender):
    authorize.method('messages.send', {'chat_id': sender, 'attachment': 'photo-201338515_457239018', 'random_id': 0})

def pin_message(user_id, msg_ID):
    authorize.method('messages.pin', {'peer_id': 2000000000 + user_id, 'conversation_message_id': msg_ID})

def unpin_message(user_id):
    authorize.method('messages.unpin', {'peer_id': 2000000000 + user_id})

def search_msg(msg_context, user_id):
    return authorize.method('messages.search', {'q': msg_context, 'peer_id': user_id, 'preview_length': 0, 'group_id': 201338515})

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":
        msg = event.message.get('text')
        
        print('Log_msg: [' + msg + ']')

        if msg == 'hello':
            write_msg(event.chat_id, msg)
        