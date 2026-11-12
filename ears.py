import difflib
import json
import os
import time
import urllib.error
import urllib.request
import zipfile

import speech_recognition as sr


LANGUAGE = "ru-RU"
WAKE_WORDS = ("даша", "даш", "аша", "дашуля", "джарвис", "джарвис", "jarvis", "жарвис", "джарвиз", "джервис")
VOSK_MODEL_NAME = "vosk-model-small-ru-0.22"
VOSK_URL = f"https://alphacephei.com/vosk/models/{VOSK_MODEL_NAME}.zip"
VOSK_MODEL = None


recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.4
recognizer.non_speaking_duration = 0.25
recognizer.dynamic_energy_threshold = False
recognizer.operation_timeout = 10



def init_vosk():
    global VOSK_MODEL
    try:
        from vosk import Model, SetLogLevel
    except ImportError:
        print("Пакет vosk не установлен (pip install vosk).")
        return False
    try:
        SetLogLevel(-1)
        base = "C:/VoskModel/vosk-model-small-ru-0.22"
        path = "C:/VoskModel/vosk-model-small-ru-0.22"
        if not os.path.isdir(path):
            print("Скачиваю модель распознавания речи (~45 МБ), это один раз...")
            zip_path = path + ".zip"
            urllib.request.urlretrieve(VOSK_URL, zip_path)
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(base)
            os.remove(zip_path)
        VOSK_MODEL = Model(path)
        return True
    except Exception as e:
        print(f"[Vosk не запустился: {e}]")
        return False


def listen_vosk(timeout, phrase_limit):
    from vosk import KaldiRecognizer
    rec = KaldiRecognizer(VOSK_MODEL, 16000)
    time.sleep(0.2)
    start, speech_start = time.time(), None
    with sr.Microphone(sample_rate=16000, chunk_size=2000) as source:
        while True:
            data = source.stream.read(2000)
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "")
                if text:
                    return text
                speech_start = None
            elif speech_start is None and json.loads(rec.PartialResult()).get("partial"):
                speech_start = time.time()

            now = time.time()
            if speech_start is None:
                if timeout and now - start > timeout:
                    return ""
                if not timeout and now - start > 60:
                    rec, start = KaldiRecognizer(VOSK_MODEL, 16000), now
            elif now - speech_start > phrase_limit:
                return json.loads(rec.FinalResult()).get("text", "")


def listen_google(timeout, phrase_limit):
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return ""
    try:
        return recognizer.recognize_google(audio, language=LANGUAGE)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[распознавание речи недоступно: {e}]")
        return ""


def listen(timeout=None, phrase_limit=15):
    try:
        text = (listen_vosk if VOSK_MODEL is not None else listen_google)(timeout, phrase_limit)
    except OSError as e:
        print(f"[ошибка микрофона: {e}]")
        time.sleep(1)
        return ""
    text = text.lower().replace("ё", "е").strip()
    if text:
        print(f"Вы: {text}")
    return text

def split_wake(text):
    words = text.split()
    for i, w in enumerate(words):
        w = w.strip(",.!?:;")
        if w in WAKE_WORDS or difflib.get_close_matches(w, WAKE_WORDS, n=1, cutoff=0.75):
            return True, " ".join(words[:i] + words[i + 1:]).strip(" ,.")
    return False, text