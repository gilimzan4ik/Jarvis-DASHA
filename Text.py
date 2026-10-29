# Домашний Ассистент Широкой Автоматизации - T
from gilimzan import jarvis_process, typing, open_app

typing("Доброе утро, сэр")
open_app("Happ_app")
def listen():
    text = input("Ты: ")
    return text

while True:
        question = listen()

        if question == "привет":
            typing("приветствую вас, сэр")

        elif question == "":
            typing("Ничего не распознано")

        else:
            answer = jarvis_process(question)
            typing(answer)
