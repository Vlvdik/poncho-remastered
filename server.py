import logging
import asyncio
import methods
import handlers
from vk_api.bot_longpoll import VkBotEventType
from config import chats_limit, bot_id

### Вхождение в луп
async def main():
    for event in handlers.longpoll.listen():
        try:
            await asyncio.gather(event_handle(event))
        except:
            pass

### Основная логика тут, в том числе обработка ивентов
async def event_handle(event):
    try:

        ### Часто использующиеся параметры
        msg = event.message.get('text').lower()
        words = msg.split()
        chat_id = event.chat_id
        user_id = event.message.get('from_id')    

        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":

            if msg == '/help':
                await handlers.help(chat_id)

            if msg == '/bibametr':
                await handlers.bibametr(chat_id, user_id)

            if msg == '/быдло':
                await handlers.bydlo(chat_id)

            if msg == '/рулетка':
                await handlers.roulette(chat_id, user_id)

            if words[0] == '/лимит':
                await handlers.set_limit(chat_id, words)

            if words[0] == '/гороскоп':
                await handlers.horoscope(chat_id, words)

            if words[0] == '/расписание':
                await handlers.schedule(chat_id, words)

            ### Обновлеям токсичность чата
            await methods.refresh_chats_info(chat_id, user_id, msg)
            
            if chat_id in chats_limit:
                try:
                    await handlers.check_chat_limit(chat_id, user_id)
                except:
                    pass
    
        elif event.type == VkBotEventType.MESSAGE_NEW and (event.message.action.get('type') == 'chat_invite_user' or event.message.action.get('type') == 'chat_invite_user_by_link'):
            member_id = event.message.action.get('member_id')
            
            if member_id == bot_id:
                await handlers.chat_greeting(chat_id)
            else:
                await handlers.user_greeting(chat_id, member_id)
    
        elif event.type == VkBotEventType.MESSAGE_NEW and event.message.action.get('type') == 'chat_kick_user':
            member_id = event.message.action.get('member_id')
        
            if user_id == member_id:
                await handlers.leave_user(chat_id, member_id)                
            else:    
                await handlers.kick_user(chat_id, user_id, member_id)
    except:
        pass

asyncio.run(main())
