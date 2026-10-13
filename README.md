<h1 align="center">Hi there, this is a <a href="https://daniilshat.ru/" target="_blank">DASHA</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>
<h3 align="center">Personal computer assistant,</h3>

A computer-based voice or text assistant.
It is designed to automate everyday processes and control a personal computer using voice commands.
The built-in neural network allows you to communicate, ask questions, and receive instant responses via speech or text in the terminal (for now).

Communication with the neural network and PC control can be done via the terminal using text and voice, as well as via a Telegram bot from your phone.

All three input methods only accept your request and send it to the core.

Features:
🎙️ Voice input — speech recognition via Google STT
🔊 Voice output — speech synthesis via pyttsx3 / edge-tts
⌨️ Text input — via the console (DASHA — T)
📱 Telegram bot — control from a phone
🧠 Neural network — Groq (openai/gpt-oss-120b)

💾 Memory — remembers facts about you.

📚 Context — remembers the history of the conversation.

⚡ Cache — saves tokens and speeds up responses.

🖥️ PC control — opens applications, searches for files, turns off the computer.

Architecture

voice.py (DASHA — Voice)     console.py (DASHA — Text)     bot.py (Telegram)
        ↓                        ↓                        ↓
                        gilimzan.py (мозг)
                                ↓
                    Groq + JSON-файлы (memory, caches, context)

//TODO
Create a graphical interface.
Add even more commands to control computer processes.
The ability to easily add personalized commands and settings without editing the code.

Installation
Clone the repository:

bash
git clone https://github.com/yourname/DASHA.git
Install the dependencies:

bash
pip install -r requirements.txt
Get the Groq API key: console.groq.com

Create an API file and paste the key in one line.

Launch:

python voice.py — Voice mode

python console.py — text mode

python bot.py — Telegram bot

License
MIT License..

👤 Author
Gilimzan
GitHub: @gilimzan4ik