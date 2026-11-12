# Домашний Ассистент Широкой Автоматизации - T
from gilimzan import jarvis_process, typing, open_app
from ears import split_wake

typing("Доброе утро, сэр")
open_app("Happ_app")

tbr = ('скажи', 'произнеси', 'озвучь', 'сколько', 'расскажи')

def listen():
    text = input("Ты: ")
    return text.lower()

while True:
    text = listen()
    if text == "":
        typing("ничего не распознано")
    else:
        woke, clean_question = split_wake(text)

        for w in tbr:
            clean_question = clean_question.replace(w, "").strip()

        answer = jarvis_process(clean_question)
        typing(answer)