import telebot
from gilimzan import jarvis_process

token_file = "token.txt"

def read_token():
    with open(token_file, "r", encoding="utf-8") as f:
        return f.readline()

token = read_token()
bot = telebot.TeleBot(token)

@bot.message_handler(commands=["start"])
def start_message(message):
    chat_id = str(message.chat.id)
    bot.send_message(
        message.chat.id,
        f"Привет, я твой персональный помошник Джарвис для ПК. Отсюда ты можешь управлять своим компьтером удаленно, а также общаться с нейросетью, которая знает тебя.",
    )


@bot.message_handler(func=lambda message: True)
def message(message):
    answer = jarvis_process(message.text)
    bot.send_message(
        message.chat.id, answer,
    )













bot.infinity_polling()