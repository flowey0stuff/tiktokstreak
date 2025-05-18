# Данные! Проверьте readme.md (Страницу на гитхабе) для информации что к чему.

SESSION_ID = "" # необязательно
MS_TOKEN = "" # необязательно
TARGET_USERNAME = ""
TARGET_USER_ID = "" # необязательно
MESSAGE = "Привет! Это запланированное сообщение, отправляемое в 12:00 по МСК!"
ONRUNMESSAGE = "Привет! Это автоматическое сообщение, отправляемое при запуске кода."
LOGINGUI = True

# если не написаны все данные, то код этого не скажет. так что убедитесь, что написаны как минимум TARGET_USERNAME, MESSAGE, ONRUNMESSAGE, LOGINGUI. Остальное - в случае если хотите вход в аккаунт без браузера

# импорты внизу лоооол чоооо ваще невозможно (игнорируйте плиз импорты, марафон в 3 часа ночи)

import time, json, os
from datetime import datetime, timedelta, timezone
from TikTokApi import TikTokApi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import logging
from selenium.webdriver.chrome.options import Options
import re

# самый худший код за всё время, зато работает 👍

logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
MSK = timezone(timedelta(hours=3))
COOKIE_FILE = "tiktok_tokens.json"

# Запуск шедевро браузера для входа. (в случае LOGINGUI=True и если нет токенов.)
def login_gui():
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--disable-extensions")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    driver.get("https://www.tiktok.com")
    print("Запуск сайта...")

    try:
        print("Войдите через аккаунт Tiktok. Внимание! Будут собраны SESSION_ID и MS_TOKEN и будут помещены в tiktok_tokens.json...")
        print("Поиск токенов каждые 5 секунд... (игнорируйте спам MS_TOKEN в консоле, так и должно быть)")
        session_id = None
        ms_token = None
        max_wait_time = 300
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            cookies = driver.get_cookies()
            for c in cookies:
                if c["name"] == "sessionid": 
                    session_id = c["value"]
            
            logs = driver.get_log("performance")
            for log in logs:
                try:
                    network_log = json.loads(log["message"])["message"]
                    if "Network.requestWillBeSent" in network_log["method"]:
                        request_url = network_log["params"]["request"]["url"]
                        if "msToken=" in request_url:
                            match = re.search(r'msToken=([^&]+)', request_url)
                            if match:
                                ms_token = match.group(1)
                                print(f"msToken найден в URL! (игнорируйте)")
                except:
                    continue
            if session_id and ms_token:
                print("Вход выполнен успешно!")
                break
            time.sleep(5)
            print(".", end="", flush=True)
        if not session_id or not ms_token:
            print("\nВремя ожидания истекло.")
        else:
            print()
    except Exception as e:
        print(f"Ошибка при входе: {e}")
    if not session_id:
        cookies = driver.get_cookies()
        for c in cookies:
            if c["name"] == "sessionid": 
                session_id = c["value"]
    driver.quit()
    if not session_id:
        print("Не удалось получить sessionid. Проверьте, что вы вошли в аккаунт.")
    else:
        # print(f"SessionID: {session_id}")
        # Уберите комментарий сверху, если хотите получить session_id
        print(f"SessionID успешно получен: {'*'*(len(session_id)-4) + session_id[-4:] if session_id else 'None'}")
    
    if not ms_token:
        print("Не удалось получить msToken. Попробуйте снова или укажите его вручную.")
    else:
        # print(f"msToken: {ms_token}")
        # Уберите комментарий сверху, если хотите получить ms_token
        print(f"msToken успешно получен: {'*'*(len(ms_token)-4) + ms_token[-4:] if ms_token else 'None'}") 
    data = {"session_id": session_id, "ms_token": ms_token}
    with open(COOKIE_FILE, "w") as f:
        json.dump(data, f)
    return session_id, ms_token
def load_tokens():
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r") as f:
                d = json.load(f)
                if "timestamp" in d:
                    last_login_time = d.get("timestamp", 0)
                    current_time = time.time()
                    if current_time - last_login_time < 300:
                        return d.get("session_id"), d.get("ms_token")
            return d.get("session_id"), d.get("ms_token")
        except Exception as e:
            print(f"Ошибка при загрузке токенов: {e}. Попробуйте удалить tiktok_tokens.json")
    return None, None
def validate_tokens(session_id, ms_token):
    if not session_id or not ms_token:
        return False
    try:
        test_api = TikTokApi()
        test_api.sessionid = session_id
        test_api.ms_token = ms_token
        try:
            test_api.trending.hashtag()
            print("Прошлые данные действительны.") # plot twist: это невозможно достичь в коде
            return True
        except Exception as specific_e:
            print(f"Не удалось проверить данные: {specific_e} (можно игнорировать)")
            if session_id and ms_token:
                print("Используются прошлые данные. (можно игнорировать)")
                return True
            return False
    except Exception as e:
        print(f"Токены недействительны или истекли: {e} (можно игнорировать)")
        return False
s, m = load_tokens()
tokens_valid = False
if s and m:
    print("Проверка прошлых данных...")
    tokens_valid = validate_tokens(s, m)
if not tokens_valid:
    if LOGINGUI:
        print("Открытие сайта с входом...")
        s, m = login_gui()
        if s and m:
            data = {"session_id": s, "ms_token": m, "timestamp": time.time()}
            with open(COOKIE_FILE, "w") as f:
                json.dump(data, f)
    
    if not s and os.path.exists(COOKIE_FILE):
        s, m = load_tokens()




SESSION_ID = SESSION_ID or s
MS_TOKEN = MS_TOKEN or m
if not SESSION_ID:
    print("Нету SESSION_ID. Включите LOGINGUI если это не-хостинг. В другом случае - чекните readme.md")
    exit()

# Это не работает. (сделайте tiktok api нормальным 🙏🙏🙏)
api = TikTokApi()
api.sessionid = SESSION_ID
api.ms_token = MS_TOKEN
def get_tiktok_user_id(username: str) -> tuple:
    try:
        import requests, re, json # импортил ли я до этого? да ваще пофиг. работает же
        url = f"https://www.tiktok.com/@{username.lstrip('@')}"
        headers = {"User-Agent":"Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', resp.text)
        if not m:
            print(f"Не удалось найти данные пользователя на странице {username} (можно игнорировать)")
            return None, None
        data = json.loads(m.group(1))
        user = data["props"]["pageProps"]["userInfo"]["user"]
        return user["id"], user.get("secUid")
    except Exception as e:
        print(f"Не найден ID пользователя через веб-запрос: {e} (можно игнорировать)")
        return None, None
def send_message(api, username, text, direct_user_id=None):
    try:
        user_id = direct_user_id
        sec_uid = None
        if not user_id:
            try:
                user = api.user(username=username)
                print(f"{type(user)} (можно игнорировать)")
                if hasattr(user, 'id'):
                    user_id = user.id
                    print(f"{user_id} (можно игнорировать)")
                elif hasattr(user, 'user_id'):
                    user_id = user.user_id
                    print(f"{user_id} (можно игнорировать)")
                elif hasattr(user, 'uniqueId'):
                    print(f"{user.uniqueId} (можно игнорировать)")
                if hasattr(user, 'sec_uid'):
                    sec_uid = user.sec_uid
                    print(f"{sec_uid} (можно игнорировать)")
            except Exception as e:
                print(f"TikTokAPI не сработал. {e} (можно игнорировать)")
            if not user_id:
                print("Другой способ получить ID пользователя (можно игнорировать)")
                user_id, sec_uid = get_tiktok_user_id(username)
                if user_id:
                    print(f"Получен ID из веб реквеста: {user_id} (можно игнорировать)")
                if sec_uid:
                    print(f"Получен sec_uid из веб рекаеста: {sec_uid} (можно игнорировать)")
        if not user_id:
            print(f"Не удалось использовать TikTokAPI для получения ID. {username}. Проверьте, вдруг проблема в нике (можно игнорировать)")
            return None
            
        print(f"Получен ID пользователя: {user_id} (можно игнорировать)")
        try:
            import requests
            import time
            conversation_id = get_or_create_conversation(user_id)
            if not conversation_id:
                print("Не получен ID чата. (можно игнорировать?)")
                return False
                
            print(f"Используется ID чата: {conversation_id}")
            url = "https://www.tiktok.com/api/im/send_message/"
            headers = {
                "authority": "www.tiktok.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "cookie": f"sessionid={SESSION_ID}",
                "origin": "https://www.tiktok.com",
                "referer": f"https://www.tiktok.com/messages",
                "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            }
            data = {
                "conversation_id": conversation_id,
                "conversation_short_id": conversation_id,
                "content": text,
                "text": text,
                "type": 0,
                "msToken": MS_TOKEN,
                "X-Bogus": generate_x_bogus(),
                "_signature": generate_signature()
            }
            url += f"?_t={int(time.time() * 1000)}"
            response = requests.post(url, headers=headers, data=data)
            print(f": {response.status_code}")
            print(f": {response.headers}")
            try:
                print(f": {response.json()}")
            except:
                print(f": {response.text}")
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if resp_json.get("status_code") == 0:
                        print(f"Сообщение отправлено {username}: {text}")
                        return True
                    else:
                        print(f"TikTok API вернул ошибку: {resp_json.get('status_msg', 'Unknown error')}")
                        return False
                except:
                    print(f"Сообщение отправлено {username}: {text}")
                    return True
            else:
                print(f"Ошибка при отправке сообщения: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            return None
            
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return None

def get_or_create_conversation(user_id):
    try:
        import requests
        url = "https://www.tiktok.com/api/im/conversation/list/"
        headers = {
            "Cookie": f"sessionid={SESSION_ID}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                conversations = data.get("conversations", [])
                for conv in conversations:
                    participants = conv.get("participants", [])
                    for participant in participants:
                        if str(participant.get("user_id")) == str(user_id):
                            return conv.get("conversation_id")
            except:
                pass
        create_url = "https://www.tiktok.com/api/im/create_conversation/"
        create_data = {
            "recipient_id": user_id,
            "msToken": MS_TOKEN
        }
        create_response = requests.post(create_url, headers=headers, data=create_data)
        if create_response.status_code == 200:
            try:
                data = create_response.json()
                return data.get("conversation_id")
            except:
                pass
                
        return None
    except Exception as e:
        print(f"Ошибка при получении чата: {e} (можно игнорировать)")
        return None

def generate_x_bogus():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_signature():
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def send_message_via_browser(username, text):
    print(f"Отправка сообщения пользователю {username} через СКРЫТЫЙ браузер.")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("https://www.tiktok.com")
        driver.add_cookie({
            "name": "sessionid",
            "value": SESSION_ID,
            "domain": ".tiktok.com"
        })
        driver.get("https://www.tiktok.com/messages")
        print("Открыта страница сообщений (можно игнорировать)")
        driver.execute_script("window.focus();")
        time.sleep(10)
        user_found = False
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'DivConversationListContainer')]"))
            )
            print("Поиск ника через PInfoNickname в HTML... (можно игнорировать)")
            nickname_elements = driver.find_elements(By.XPATH, "//p[contains(@class, 'PInfoNickname')]")
            print(f"Найдено {len(nickname_elements)} PInfoNickname (можно игнорировать)")
            for i, elem in enumerate(nickname_elements):
                try:
                    print(f"Ник {i+1}: {elem.text} (можно игнорировать)")
                    if username.lower() in elem.text.lower():
                        print(f"Найден пользователь: {elem.text} (можно игнорировать)")
                        try:
                            elem.click()
                            print("Нажато (можно игнорировать)")
                            user_found = True
                        except Exception as click_error:
                            print(f"Не удалось нажать: {click_error} (можно игнорировать)")
                            
                            try:
                                driver.execute_script("arguments[0].click();", elem)
                                print("Нажатие через JavaScript (можно игнорировать)")
                                user_found = True
                            except Exception as js_error:
                                print(f"Нажатие через JavaScript неудачное: {js_error} (можно игнорировать)")
                                
                                try:
                                    parent = driver.execute_script("""
                                        var element = arguments[0];
                                        var parent = element;
                                        for (var i = 0; i < 3 && parent; i++) {
                                            parent = parent.parentElement;
                                        }
                                        return parent;
                                    """, elem)
                                    if parent:
                                        driver.execute_script("arguments[0].click();", parent)
                                        print("Нажато через элемент (можно игнорировать)")
                                        user_found = True
                                except Exception as parent_error:
                                    print(f"Нажатие через элемент неудалось: {parent_error} (можно игнорировать)")
                        if user_found:
                            time.sleep(5)
                            break
                except Exception as e:
                    print(f"Ошибка при получении ника. {i+1}: {e} (можно игнорировать)")
            if user_found:
                try:
                    message_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='message-input-area']"))
                    )
                    print("Успешно открыт чат с пользователем (можно игнорировать)")
                except:
                    user_found = False
                    print("Не удалось открыть чат. (можно игнорировать)")
        except Exception as e:
            print(f"Ошибка при получении ника через XPath: {e} (можно игнорировать)")
        if not user_found:
            try:
                print(f"Не найден пользователь. Попытка начать чат.")
                new_chat_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'ButtonNewChat') or contains(@aria-label, 'New') or contains(@aria-label, 'Add')]")
                if new_chat_buttons:
                    new_chat_buttons[0].click()
                    time.sleep(2)
                    search_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Search') or contains(@placeholder, 'Find')]"))
                    )
                    search_input.clear()
                    search_input.send_keys(username)
                    time.sleep(5)
                    search_results = driver.find_elements(By.XPATH, "//div[contains(@class, 'SearchResultItem') or contains(@class, 'UserItem')]")
                    if search_results:
                        search_results[0].click()
                        time.sleep(2)
                        start_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Chat') or contains(text(), 'Message') or contains(@class, 'ButtonSend')]")
                        if start_buttons:
                            start_buttons[0].click()
                            time.sleep(2)
                            user_found = True
            except Exception as e:
                print(f"Ошибка при создании чата: {e}. Неправильный ник?")
        if not user_found:
            print(f"!!!!!!!!!!!!!!! (Перепроверьте данные, может что-то неправильно ввели? Или удалите tiktok_tokens.json, и войдите заново.):\nНе удалось найти пользователя {username} в списке сообщений")
            return False
        try:
            message_input_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='message-input-area']"))
            )
            print("Найден ввод текста через data-e2e атрибут (можно игнорировать)")
            editable_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='message-input-area']//div[contains(@class, 'public-DraftEditor-content')]"))
            )
            print("Найден div для ввода текста. (можно игнорировать)")
            driver.execute_script("arguments[0].focus();", editable_div)
            editable_div.click()
            time.sleep(1)
            driver.execute_script("arguments[0].innerHTML = '';", editable_div)
            for char in text:
                driver.execute_script("if(document.activeElement !== arguments[0]) arguments[0].focus();", editable_div)
                driver.switch_to.active_element.send_keys(char)
                time.sleep(0.05)
            
            print(f"Текст '{text}' успешно введен (можно игнорировать)")
            time.sleep(1)
            editable_div.send_keys(Keys.RETURN)
            print("Нажат ENTER для отправки сообщения (можно игнорировать)")
            time.sleep(3)
            try:
                message_elements = driver.find_elements(By.XPATH, f"//div[contains(text(), '{text}')]")
                if message_elements:
                    print("Сообщение успешно отображается в чате (можно игнорировать)")
                else:
                    print("Сообщение не найдено в чате, но попытка отправить была сделана. (можно игнорировать)")
            except:
                print("Не удалось проверить наличие сообщения в чате (можно игнорировать)")
            print(f"Сообщение отправлено пользователю {username}: {text}")
            return True
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e} (можно игнорировать)")
            try:
                print("Пробуем другой метод отправки сообщения...")
                editable_divs = driver.find_elements(By.XPATH, "//div[@role='textbox' or contains(@class, 'public-DraftEditor-content')]")
                if editable_divs:
                    print(f"Найдено {len(editable_divs)} потенциальных полей ввода")
                    for i, div in enumerate(editable_divs):
                        try:
                            print(f"Пробуем поле ввода #{i+1}")
                            driver.execute_script("arguments[0].focus();", div)
                            div.click()
                            time.sleep(1)
                            driver.execute_script("arguments[0].innerHTML = '';", div)
                            div.send_keys(text)
                            time.sleep(1)
                            div.send_keys(Keys.RETURN)
                            time.sleep(3)
                            message_elements = driver.find_elements(By.XPATH, f"//div[contains(text(), '{text}')]")
                            if message_elements:
                                print(f"Сообщение успешно отправлено через поле ввода #{i+1}")
                                return True
                        except Exception as div_error:
                            print(f"Ошибка при использовании поля ввода #{i+1}: {div_error}")
                print("Все попытки отправки сообщения не удались. Плохой интернет?")
                return False
            except Exception as fallback_error:
                print(f"Ошибка при использовании другого метода: {fallback_error}")
                return False
    except Exception as e:
        print(f"Ошибка при отправке сообщения через браузер: {e}")
        return False
    finally:
        if driver:
            time.sleep(10)
            driver.quit()
from selenium.webdriver.common.keys import Keys
if TARGET_USERNAME and ONRUNMESSAGE:
    api_result = send_message(api, TARGET_USERNAME, ONRUNMESSAGE, direct_user_id=TARGET_USER_ID if TARGET_USER_ID else None)
    if not api_result:
        print("API метод не сработал, пробуем отправить через браузер...")
        send_message_via_browser(TARGET_USERNAME, ONRUNMESSAGE)
else:
    print("Не введены данные: TARGET_USERNAME , ONRUNMESSAGE")
def send_scheduled_message():
    if TARGET_USERNAME and MESSAGE:
        print(f"Отправка временного сообщения пользователю {TARGET_USERNAME} в {datetime.now(MSK).strftime('%H:%M:%S')}")
        api_result = send_message(api, TARGET_USERNAME, MESSAGE, direct_user_id=TARGET_USER_ID if TARGET_USER_ID else None)
        if not api_result:
            print("API метод не сработал, пробуем отправить через браузер...")
            send_message_via_browser(TARGET_USERNAME, MESSAGE)
        print(f"Сообщение по времени отправлено. Следующая отправка будет в 12:00 МСК")
        return True
    else:
        print("Не введены данные: TARGET_USERNAME, MESSAGE")
        return False
if TARGET_USERNAME and ONRUNMESSAGE:
    api_result = send_message(api, TARGET_USERNAME, ONRUNMESSAGE, direct_user_id=TARGET_USER_ID if TARGET_USER_ID else None)
    if not api_result:
        print("API метод не сработал, пробуем отправить через браузер...")
        send_message_via_browser(TARGET_USERNAME, ONRUNMESSAGE)
else:
    print("Не введены данные: TARGET_USERNAME, ONRUNMESSAGE")
print(f"Код ждёт. Сообщение по времени будет отправлено в 12:00 MSK каждый день.")
last_run_day = -1
while True:
    now = datetime.now(MSK)
    if now.hour == 12 and now.minute == 0 and now.day != last_run_day:
        send_scheduled_message()
        last_run_day = now.day
        seconds_to_next_minute = 60 - now.second
        time.sleep(seconds_to_next_minute)
    if now.hour == 11 and now.minute >= 58:
        time.sleep(10)
    elif now.hour == 12 and now.minute == 0:
        time.sleep(1)
    else:
        time.sleep(30)
# 555 строк!
