# Домашний Ассистент Широкой Автоматизации - T
from gilimzan import jarvis_process, typing

typing("Доброе утро, сэр")

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
