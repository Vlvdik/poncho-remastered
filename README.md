# New **async** bot for vk's conversations ![License](https://img.shields.io/github/license/Vlvdik/poncho-remastered)

##### *The old project was **lost** 😢*
##### *The source code of this furry friend was left on the old operating system, which I safely **demolished***
#  
#  **Installation**

### 1) Clone this repository
```bash
git clone https://github.com/Vlvdik/poncho-remastered 
```
### 2) Create your config file (get API token, parse the necessary links etc)
```bash
touch config.py
```
##### * ***Or like this this method is more welcome, guess why***  :smiley_cat:

```bash
cat config.py
```

### 3) Configurate your config file

```python
import sqlite3

# You can use another one, but then maybe you need to change the queries and methods of working with the DB

db = sqlite3.connect('name_db.db')
cursor = db.cursor()
# ...............................|
# Some execute for create tables |
#................................|

group_id = 'Your group ID, integer'
bot_id = 'Your bot ID, integer'

main_token = 'Your API token from VK group'

HEADERS = {'User_agent': 'Your user agent'}

# .....................................
# In the same way we add the rest of the parameters to support the functionality
```
### 4) Run your bot by pulling up all dependencies using the **makefile**

```bash
make run
```
---
# **Done!**
##### **P.S. Well, if you do not want to bother with setting up your own bot, you can try its functionality by writing in direct or by inviting to the ![conversation VK](https://vk.com/ponchomeowbot)**
