import time
from datetime import datetime
from zoneinfo import ZoneInfo
from TikTokApi import TikTokApi
# Пропишите в терминале -> pip install TikTokApi 

USERNAME = ""
PASSWORD = ""
TARGET_USERNAME = ""
MESSAGE = "Привет! Огонек."
ONRUNMESSAGE = "Привет! Это автоматическое сообщение."

MOSCOW = ZoneInfo("Europe/Moscow") # Берётся часовой пояс Москвы.
api = TikTokApi()
api.login(username=USERNAME, password=PASSWORD) # Логин в Аккаунт.
user_info = api.user(username=TARGET_USERNAME)
TARGET_USER_ID = user_info.id # Берётся айди нужного пользователя.
api.direct_messages.send(to_user_id=TARGET_USER_ID, text=ONRUNMESSAGE) # Пишет автоматическое сообщение при запуске.

while True:
    now = datetime.now(MOSCOW)
    if now.hour == 12 and now.minute == 0: # Оптимальное время для России.
        api.direct_messages.send(to_user_id=TARGET_USER_ID, text=MESSAGE)
        time.sleep(60)
    time.sleep(30)
