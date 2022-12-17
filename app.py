import logging
import asyncio
import db_methods
import handlers
from vk_api.bot_longpoll import VkBotEventType
from config import bot_id, forms, commands

logging.basicConfig(level=logging.INFO, filename='logs\server.log')
log = logging.getLogger('SERVER.PY')

async def main():
    tasks = []
    for event in handlers.longpoll.listen():
        try:
            tasks.append(asyncio.create_task(event_handle(event)))
            await asyncio.gather(*tasks)
        except Exception as ex:
            logging.critical(f'SERVER ERROR: {ex}')

async def event_handle(event):
    try:
        if event.type == VkBotEventType.MESSAGE_NEW:

            ### Часто использующиеся параметры
            msg = event.message.get('text').lower()
            words = msg.split()
            user_id = event.message.get('from_id')  
            if event.from_user and event.message.get('text') != "":

                log.info(f'\nNEW DIRECT MESSAGE: {msg} FROM USER: {user_id}\n')

                if msg == 'начать' and not await db_methods.is_existing_user(user_id):
                    await handlers.start(user_id)
                elif msg == 'назад' and await db_methods.is_existing_user(user_id):
                    await handlers.back(user_id)
                elif await db_methods.is_existing_user(user_id) and await db_methods.is_user_have_form(user_id):
                    if await db_methods.is_user_have_group(user_id):
                        await handlers.push_button(user_id, msg)
                    else:
                        await handlers.set_group(user_id, msg)
                elif msg in forms:
                    await handlers.set_form(user_id, msg)
                else:
                    await handlers.undefiend_command(user_id)

            elif event.from_chat and event.message.get('text') != "":
                chat_id = event.chat_id

                log.info(f'\nNEW MESSAGE: {msg} \nFROM CHAT: {chat_id} \nFROM USER: {user_id}\n')

                if msg == '/help':
                    await handlers.help(chat_id)

                if msg == '/быдло':
                    await handlers.get_chat_info(chat_id)

                if msg == '/рулетка':
                    await handlers.roulette(chat_id, user_id)

                if words[0] == '/лимит':
                    await handlers.set_chat_limit(chat_id, user_id, words)

                if words[0] == '/гороскоп':
                    await handlers.horoscope(chat_id, words)

                if words[0] == '/расписание':
                    await handlers.schedule(chat_id, words)

                ### Обновлеям токсичность чата
                if words[0] not in commands:
                    await handlers.refresh_chats_info(chat_id, user_id, msg)

                if await db_methods.is_chat_have_limit(chat_id):
                    try:
                        await handlers.check_chat_limit(chat_id, user_id)
                    except:
                        log.warning(f'\nRIGHTS ERROR: attempt to kick administrator (CHAT: {chat_id})\n')
    
            elif event.message.action.get('type') == 'chat_invite_user' or event.message.action.get('type') == 'chat_invite_user_by_link':
                member_id = event.message.action.get('member_id')
                chat_id = event.chat_id

            
                if member_id == bot_id:
                    log.info(f'\nNEW CHAT: {chat_id}\n')
                    await handlers.chat_greeting(chat_id)
                else:
                    log.info(f'\nNEW USER: {member_id} (CHAT: {chat_id})\n')
                    await handlers.user_greeting(chat_id, member_id)
    
            elif event.message.action.get('type') == 'chat_kick_user':
                member_id = event.message.action.get('member_id')
                chat_id = event.chat_id

                if user_id == member_id:
                    log.info(f'\nLEAVE USER: {member_id} (CHAT: {chat_id})\n')
                    await handlers.leave_user(chat_id, member_id)                
                else:    
                    log.info(f'\nKICK USER: {member_id} (CHAT: {chat_id})\n')
                    await handlers.kick(chat_id, user_id, member_id)
    except Exception as ex:
        log.warning(f'\nHANDLE ERROR: {ex}\n')
        
if __name__ == "__main__":
    asyncio.run(main())
