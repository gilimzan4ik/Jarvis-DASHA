import asyncio
import collections
import hashlib
import os
import platform
import queue
import re
import sys
import threading
import time
import numpy as np

import edge_tts
import pygame

WAKE_WORDS = ("даша", "даш", "аша", "дашуля", "джарвис", "джарвис", "jarvis", "жарвис", "джарвиз", "джервис")
LANGUAGE = "ru-RU"
WAKE_WORD_REQUIRED = False
STT_ENGINE = "vosk"
VOSK_MODEL_NAME = "vosk-model-small-ru-0.22"
VOSK_URL = f"https://alphacephei.com/vosk/models/{VOSK_MODEL_NAME}.zip"

VOICE = "ru-RU-SvetlanaNeural"
VOICE_RATE = "+20%"
VOICE_PITCH = "+10Hz"
VOICE_FX = True
TYPE_SYNC = True
_net_lock = threading.Lock()

OS = platform.system()
VOICE_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_cache")

pygame.mixer.init()
pygame.mixer.set_num_channels(4)


async def _synthesize(text, path, rate, pitch):
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(path)

def synth(text, quick=False):
    os.makedirs(VOICE_CACHE, exist_ok=True)
    key = hashlib.md5(f"{text}|{VOICE}|{VOICE_RATE}|{VOICE_PITCH}".encode()).hexdigest()
    mp3 = os.path.join(VOICE_CACHE, key + ".mp3")
    if os.path.exists(mp3):
        return mp3

    attempts = [(VOICE_RATE, VOICE_PITCH), (VOICE_RATE, "+0Hz"), ("+0%", "+0Hz")]
    if quick:
        attempts = attempts[:1]
    tmp = f"{mp3}.{threading.get_ident()}.part"
    error = None
    with _net_lock:
        for rate, pitch in attempts:
            try:
                asyncio.run(_synthesize(text, tmp, rate, pitch))
                if os.path.getsize(tmp) > 0:
                    os.replace(tmp, mp3)
                    return mp3
            except Exception as e:
                error = e
                time.sleep(0.15)
    raise RuntimeError(f"не удалось озвучить: {error}")

def load_sound(path):
    sound = pygame.mixer.Sound(path)
    if not (VOICE_FX and np is not None):
        return sound
    try:
        freq, fmt, channels = pygame.mixer.get_init()
        if fmt != -16:
            return sound
        x = np.frombuffer(sound.get_raw(), dtype=np.int16).astype(np.float32).reshape(-1, channels)
        n = x.shape[0]
        spec = np.fft.rfft(x, axis=0)
        hz = np.fft.rfftfreq(n, 1.0 / freq)
        spec[(hz < 110) | (hz > 8500)] = 0
        y = np.fft.irfft(spec, n=n, axis=0)
        y = np.vstack([y, np.zeros((int(freq * 0.12), channels), dtype=np.float32)])
        dry = y.copy()
        for ms, gain in ((40, 0.18), (95, 0.08)):
            d = int(freq * ms / 1000)
            if d < len(y):
                y[d:] += gain * dry[:-d]
        peak = float(np.abs(y).max()) or 1.0
        y = np.clip(y * (0.9 * 32767 / peak), -32768, 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=y.tobytes())
    except Exception:
        return sound

def split_sentences(text):
    text = re.sub(r"[*_`#>]", "", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if re.search(r"\w", s)]

def _play_synced(text, path):
    if path is None:
        print(f"JARVIS: {text}")
        return
    try:
        sound = load_sound(path)
        length = sound.get_length()
        channel = sound.play()
        busy = channel.get_busy if channel else (lambda: False)
    except pygame.error:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        length = len(text) * 0.06
        busy = pygame.mixer.music.get_busy

    sys.stdout.write("JARVIS: ")
    sys.stdout.flush()
    if TYPE_SYNC and length > 0:
        delay = length * 0.92 / max(len(text), 1)
        start = time.time()
        for i, ch in enumerate(text):
            sys.stdout.write(ch)
            sys.stdout.flush()
            pause = start + (i + 1) * delay - time.time()
            if pause > 0:
                time.sleep(pause)
    else:
        sys.stdout.write(text)
    sys.stdout.write("\n")
    sys.stdout.flush()
    while busy():
        time.sleep(0.02)



class Voice:
    def __init__(self):
        self.synth_q = queue.Queue()
        self.play_q = queue.Queue()
        self.pending = 0
        self.last_activity = time.time()
        self.recent = collections.deque(maxlen=5)
        self.cv = threading.Condition()
        threading.Thread(target=self._synth_loop, daemon=True).start()
        threading.Thread(target=self._play_loop, daemon=True).start()

    def idle(self):
        return self.pending == 0 and time.time() - self.last_activity > 2.5

    def say(self, text):
        self.last_activity = time.time()
        for sentence in split_sentences(text):
            self.recent.append(re.sub(r"[^\w\s]", "", sentence.lower()))
            with self.cv:
                self.pending += 1
            self.synth_q.put(sentence)

    def wait(self):
        with self.cv:
            self.cv.wait_for(lambda: self.pending == 0)

    def _synth_loop(self):
        while True:
            text = self.synth_q.get()
            try:
                path = synth(text)
            except Exception as e:
                print(f"[голос недоступен: {e}]")
                path = None
            self.play_q.put((text, path))

    def _play_loop(self):
        while True:
            text, path = self.play_q.get()
            try:
                _play_synced(text, path)
            except Exception as e:
                print(f"[ошибка воспроизведения: {e}]")
            finally:
                self.last_activity = time.time()
                with self.cv:
                    self.pending -= 1
                    self.cv.notify_all()

PHRASES = [
    "Системы запущены. Слушаю вас, сэр.", "Да, сэр?", "Открываю.", "Выполняю, сэр.", "Выполняю.",
    "Ищу, сэр.", "Ищу в интернете, сэр.", "Печатаю.", "Делаю снимок.", "Блокирую.", "Громче.",
    "Тише.", "Звук отключён.", "Следующий трек.", "Предыдущий трек.", "Отменено, сэр.",
    "Приветствую, сэр. Чем могу быть полезен?", "Все системы в норме, сэр.",
    "Всегда к вашим услугам, сэр.", "Произошла ошибка, сэр.", "Хорошего дня, сэр.",
    "Не понял команду, сэр.", "Закрываю.", "Обновляю.", "Копирую.", "Вставляю.", "Выделяю.",
    "Сохраняю.", "Отменяю.", "Переключаю.", "Слушаю, сэр.", "Нет окна для закрытия, сэр.",
    "Перехожу в режим ожидания. Назовите моё имя, когда понадоблюсь, сэр.",
]

def prewarm_voice(jarvis_voice):
    for phrase in PHRASES:
        for sentence in split_sentences(phrase):
            while not jarvis_voice.idle():
                time.sleep(0.5)
            try:
                synth(sentence, quick=True)
            except Exception:
                time.sleep(2)