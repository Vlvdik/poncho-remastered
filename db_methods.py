from config import *

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
