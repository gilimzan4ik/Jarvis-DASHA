# Домашний Ассистент Широкой Автоматизации - Г
import difflib
from voice_engine import Voice, prewarm_voice
from ears import listen, init_vosk, split_wake
from gilimzan import jarvis_process
import threading


jarvis_voice = Voice()
init_vosk()
tbr = ('скажи', 'произнеси', 'озвучь', 'сколько', 'расскажи')

threading.Thread(target=prewarm_voice, args=(jarvis_voice,), daemon=True).start()

jarvis_voice.say("Системы запущены, слушаю")
jarvis_voice.wait()

def is_echo(text):
    words = text.split()
    if len(words) < 2:
        return False
    return any(difflib.SequenceMatcher(None, text, r).ratio() > 0.7 for r in jarvis_voice.recent)

sleeping = False

try:
    while True:
        heard = listen().lower()
        if not heard or is_echo(heard):
            continue

        woke, clean_question = split_wake(heard)

        # Логика сна
        if sleeping:
            if not woke:
                continue
            sleeping = False

        # Если разбудили, но команду не сказали
        if woke and not clean_question:
            jarvis_voice.say("Да, сэр?")
            jarvis_voice.wait()
            clean_question = listen(timeout=8)
            if not clean_question or is_echo(clean_question):
                continue

        # Выход
        if "отбой" in clean_question or "выход" in clean_question:
            jarvis_voice.say("Хорошего дня, сэр.")
            jarvis_voice.wait()
            break

        # Режим сна
        if "помолчи" in clean_question or "усни" in clean_question or "режим ожидания" in clean_question:
            sleeping = True
            jarvis_voice.say("Перехожу в режим ожидания. Назовите моё имя, когда понадоблюсь, сэр.")
            jarvis_voice.wait()
            continue

        # Очистка слов-триггеров
        for w in tbr:
            clean_question = clean_question.replace(w, "").strip()

        # Отправка в мозг
        answer = jarvis_process(clean_question).lower()

        # Озвучка ответа
        jarvis_voice.say(answer)
        jarvis_voice.wait()

except KeyboardInterrupt:
    print("\n[Программа завершена пользователем]")