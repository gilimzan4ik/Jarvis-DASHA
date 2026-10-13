# Домашний Ассистент Широкой Автоматизации - Г
import pyttsx3
import speech_recognition as sr
from gilimzan import jarvis_process

opts = {
    "alias": ('даша', 'даш', 'дарья', 'дора', 'дар', 'дашенька', 'дашуля', "джарвис"),
    "tbr": ('скажи', 'произнеси',  'озвучь',  'сколько',  'расскажи'),
}

def is_called(text):
    for alias in opts["alias"]:
        if alias in text:
            return True
    return False

def speak(for_speak):
    engine = pyttsx3.init()
    engine.say(for_speak)
    engine.runAndWait()

speak("Доброе утро, сэр")

def listen():
    r = sr.Recognizer()
    text = ""
    with sr.Microphone() as source:
        print("Говори: ")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="ru-RU").lower()
        print(f"[log] Распознано: {text}")
        if is_called(text):
            for x in opts['alias']:
                text = text.replace(x, "").strip()
            for x in opts['tbr']:
                text = text.replace(x, "").strip()

    except sr.UnknownValueError:
        print("Не удалось распознать речь")
    except sr.RequestError:
        print("Ошибка сервиса распознавания")

    return text

while True:
        question = listen()

        if question == "привет":
            speak("приветствую вас, сэр")

        elif question == "":
            speak("Ничего не распознано")

        else:
            answer = jarvis_process(question)
            speak(answer)