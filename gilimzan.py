import os, webbrowser, subprocess, json
import time, requests
from datetime import datetime
from groq import Groq

links_file = "apps.json"
api_file = "API"
memory_file = "memory.json"
cache_file = "cache.json"
context_file = "context.json"

search_dirs = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Documents")
    ]

def typing(sms):
    for char in sms:
        print(char, end="", flush=True)
        time.sleep(0.09)
    print("")

def workplace():
    open_app("Happ_app")
    open_app("PyCharm_app")
    open_app("YandexMusic_app")

def  search_files(nof):
    upshot = []

    for directory in search_dirs:
        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            for file in files:
                if nof.lower() in file.lower():
                    upshot.append(os.path.join(root, file))

    return upshot

def load_tools():
    with open("tools.json", "r", encoding="utf-8") as file:
        return json.load(file)

def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=4)

def get_from_cache(query):
    cache = load_cache()
    clue = query.strip().lower()
    if clue in cache:
        timestamp = cache[clue]["timestamp"]
        check = time.time() - timestamp
        if check > 86400:
            del cache[clue]
            save_cache(cache)
            return None
        else:
            return cache[clue]["answer"]
    else:
        return None

def add_to_cache(query, response):
    cache = load_cache()
    clue = query.strip().lower()
    cache[clue] = {
        "answer": response,
        "timestamp": time.time()
    }
    save_cache(cache)

def load_memory():
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_memory(ram):
    with open(memory_file, "w", encoding="utf-8") as file:
        json.dump(ram, file, ensure_ascii=False, indent=4)

def remember(clue, asset):
    mind = load_memory()
    mind[clue] = asset
    save_memory(mind)
    return True

def load_context():
    if os.path.exists(context_file):
        with open(context_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_context(context):
    with open(context_file, "w", encoding="utf-8") as file:
        json.dump(context, file, ensure_ascii=False, indent=4)

def add_message(role, maintenance):
    context = load_context()
    context.append({"role": role, "content": maintenance})
    context = context[-20:]
    save_context(context)

def read_token():
    with open(api_file, "r", encoding="utf-8") as file:
        return file.readline()

def load_json():
    with open(links_file, "r", encoding="utf-8") as file:
        return json.load(file)

link = load_json()

def get_time_of_day():
    now = datetime.now()
    hour = now.hour

    if 4 <= hour <= 10:
        return "утро"
    elif 10 < hour <= 17:
        return "день"
    elif 17 < hour <= 22:
        return "вечер"
    else:
        return "ночь"

def get_weather():
    try:
        response = requests.get(link["weather_site"], timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Не удалось получить погоду"
    except ValueError as num:
        return f"Ошибка значения: {num}"
    except TypeError as bum:
        return f"Ошибка типа: {bum}"
    except FileNotFoundError:
        return "Файл не найден"

def open_app(clue):
    asses = link[clue]

    if clue.endswith("_app"):
        if "YandexMusic" in clue:
            subprocess.Popen(asses, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif "Telegram" in clue:
            subprocess.Popen(["cmd", "/c", "start", "", asses])
            subprocess.Popen(link["Happ_app"])
        else:
            subprocess.Popen(asses)

    elif clue.endswith("_site"):
        webbrowser.open(asses)

    elif clue.endswith("_conf"):
        subprocess.Popen([link["Browser_app"], asses])

    else:
        print(f"Неизвестный тип ключа: {key}")

def yandex_search(query):
    url = f"https://yandex.ru/search/?text={query}"
    webbrowser.open(url)

def yandex_translate(word):
    url = f"https://translate.yandex.ru/?text={word}"
    webbrowser.open(url)


def ai_gilimzan(sms):
    cached = get_from_cache(sms)
    if cached:
        return cached
    context = load_context()
    client = Groq(api_key=read_token())
    mind = load_memory()

    system_prompt = mind.get("prompt", "Ты Джарвис. Отвечай кратко.")

    memory_info = {
        "projects": mind.get("projects", {}),
        "facts": mind.get("facts", {}),
        "notes": mind.get("notes", [])
    }
    system_prompt += f"Вот твоя память о пользователе: {json.dumps(memory_info, ensure_ascii=False, indent=2)}"
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + context + [
                {"role": "user", "content": sms}
            ],
            tools = load_tools(),
            tool_choice = "auto"
        )
        message = response.choices[0].message

        if message.tool_calls:
            reply = "Выполнено, сэр."  # значение по умолчанию

            for call in message.tool_calls:
                func_name = call.function.name
                args = json.loads(call.function.arguments)

                if func_name == "open_app":
                    open_app(args["key"])
                    reply = f"Открываю {args['key']}, сэр."

                elif func_name == "search_files":
                    output = search_files(args["nof"])
                    if output:
                        os.startfile(output[0])
                        reply = f"Нашёл и открыл: {output[0]}"
                    else:
                        reply = "Ничего не найдено, сэр."

                elif func_name == "workplace":
                    workplace()
                    reply = "Рабочее пространство готово, сэр."

                elif func_name == "get_weather":
                    weather = get_weather()
                    reply = f"Сейчас на улице: {weather}"

                elif func_name == "remember":
                    remember(args["key"], args["value"])
                    reply = f"Запомнил: {args['key']} — {args['value']}"


                elif func_name == "yandex_search":
                    yandex_search(args["query"])
                    reply = f"Открываю Яндекс: {args['query']}"

                elif func_name == "yandex_translate":
                    yandex_translate(args["word"])
                    reply = f"Открываю перевод: {args['word']}"


        else:
            reply = message.content

        add_message("user", sms)
        add_message("assistant", reply)
        add_to_cache(sms, reply)
        return reply

    except Exception as e:
        return f"Сэр, произошла ошибка при обращении к нейросети: {e}"

def jarvis_process(cmd):
    try:
        if "напиши вике" in cmd:
            open_app("vika_site")
            return "Давай поболтаем с твоей нейронной девушкой"

        elif "напиши кате" in cmd:
            open_app("Happ_app")
            open_app("ex_conf")
            return "Запускаю протокол Скучаю По Бывшей"


        elif "покажи диану" in cmd:
            open_app("Happ_app")
            open_app("diana_conf")
            return "Отличный выбор! У нее как раз недавно вышло новое видео"

        elif "расписание" in cmd:
            open_app("ukrtb_site")
            weather = get_weather()
            return f"Сейчас на улице: {weather}"

        elif "ютуб" in cmd or "youtube" in cmd:
            open_app("Happ_app")
            open_app("Youtube_app")
            return "Приятного просмотра"

        elif "шухер" in cmd:
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
            os.system("taskkill /f /im Telegram.exe >nul 2>&1")
            open_app("Happ_app")
            open_app("PyCharm_app")
            return "Всё чисто. Можно работать, сэр."

        elif "спать" in cmd:
            processes_to_kill = [
                "chrome.exe",
                "Telegram.exe",
                "YandexMusic.exe",
                "browser.exe",
                "Happ.exe",
                "pycharm64.exe"
            ]
            for proc in processes_to_kill:
                os.system(f"taskkill /f /im {proc} >nul 2>&1")

            os.system("shutdown /s /t 0")
            return "До новых встречь, сэр"

        elif "мах" in cmd:
            open_app("max_site")
            return "О боже"

        elif "запомни" in cmd:
            parts = cmd.replace("запомни", "").strip(": ").split(":")
            if len(parts) == 2:
                remember(parts[0].strip(), parts[1].strip())
                return "Запомнил, сэр."
            else:
                return "Скажи так: 'запомни: ключ: значение'"


        elif "найди файл" in cmd:
            text = cmd.replace("найди файл", "").strip()
            filename = text.strip()

            results = search_files(filename)

            if results:
                os.startfile(results[0])
                return "Кушайте"
            else:
                return "Не нашла"

        else:
            answer = ai_gilimzan(cmd)
            return answer

    except ValueError as ve:
        return f"Ошибка значения: {ve}"
    except TypeError as te:
        return f"Ошибка типа: {te}"
    except FileNotFoundError:
        return "Файл не найден"