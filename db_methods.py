from config import *


###### METHODS FOR SHEDULES TABLE
### CREATE/UPDATE

async def insert_user(user_id):
    cursor.execute('INSERT INTO schedules VALUES (?,?,?,?);', (user_id, 'not set', 'not set', 'not set'))
    db.commit()

async def insert_form(user_id, form):
    cursor.execute('UPDATE schedules SET users_form=? WHERE user_id=?;', (form, user_id))
    db.commit()

async def insert_group(user_id, group):
    cursor.execute('UPDATE schedules SET users_group=? WHERE user_id=?;', (group, user_id))
    db.commit()

async def insert_link(user_id, link):
    cursor.execute('UPDATE schedules SET users_link=? WHERE user_id=?;', (link, user_id))
    db.commit()

### READ

async def get_user_form(user_id):
    return cursor.execute('SELECT users_form FROM schedules WHERE user_id=?;', (user_id, )).fetchone()[0]

async def get_user_group(user_id):
    return cursor.execute('SELECT users_group FROM schedules WHERE user_id=?;', (user_id, )).fetchone()[0]

async def get_user_link(user_id):
    return cursor.execute('SELECT users_link FROM schedules WHERE user_id=?;', (user_id, )).fetchone()[0]

async def is_existing_user(user_id):
    if cursor.execute('SELECT user_id FROM schedules WHERE user_id=?;', (user_id, )).fetchone() != None:
        return True
    else:
        return False

async def is_user_have_form(user_id):
    if cursor.execute('SELECT users_form FROM schedules WHERE user_id=?;', (user_id, )).fetchone()[0] != 'not set':
        return True
    else:
        return False

async def is_user_have_group(user_id):
    if cursor.execute('SELECT users_group FROM schedules WHERE user_id=?;', (user_id, )).fetchone()[0] != 'not set':
        return True
    else:
        return False

### DELETE

async def delete_user(user_id):
    cursor.execute('DELETE FROM schedules WHERE user_id=?', (user_id, ))
    db.commit()

###### METHODS FOR CHATS TABLE
### CREATE/UPDATE

async def insert_chats_limit(chat_id, value):
    cursor.execute('INSERT INTO chats VALUES(?,?)', (chat_id, value))
    db.commit()

async def update_chats_limit(chat_id, value):
    cursor.execute('UPDATE chats SET chats_limit=? WHERE user_id=?;', (value, chat_id))
    db.commit()

### READ

async def is_chat_have_limit(chat_id):
    if cursor.execute('SELECT chat_id FROM chats WHERE chat_id=?;', (chat_id, )).fetchone() != None:
        return True
    else:
        return False

### DELETE

async def delete_chats_limit(chat_id):
    cursor.execute('DELETE FROM chats WHERE chat_id=?', (chat_id, ))
    db.commit()

###### METHODS FOR USERS TABLE
### CREATE/UPDATE

async def insert_chat_user_score(user_id, chat_id, score):
    cursor.execute('INSERT INTO users VALUES(?,?,?)', (user_id, chat_id, score))
    db.commit()

async def update_chat_user_score(user_id, chat_id, score):
    cursor.execute('UPDATE users SET score=score+? WHERE user_id=? AND users_chat=?', (score, user_id, chat_id))
    db.commit()

### READ

async def get_score_info(chat_id):
    return cursor.execute('SELECT user_id, score FROM users WHERE users_chat=? AND score>0 ORDER BY score DESC;', (chat_id, )).fetchall()

async def is_existed_chat(chat_id):
    if cursor.execute('SELECT users_chat FROM users WHERE users_chat=?;', (chat_id, )).fetchone() != None:
        return True
    else:
        return False

async def is_user_exist_in_current_chat(user_id, chat_id):
    if cursor.execute('SELECT user_id FROM users WHERE user_id=? AND users_chat=?;', (user_id, chat_id)).fetchone() != None:
        return True
    else:
        return False

### DELETE

async def delete_user_from_chat(user_id, chat_id):
    cursor.execute('DELETE FROM users WHERE user_id=? AND users_chat=?', (user_id, chat_id))
    db.commit()
