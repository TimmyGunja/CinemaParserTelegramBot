import config
import os
import telebot
from flask import Flask, request


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id, "Добро пожаловать")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def process_message(message):
    bot.send_message(message.chat.id, message.text)


if "HEROKU" in list(os.environ.keys()):
    server = Flask(__name__)

    @server.route('/' + config.TOKEN, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=config.HEROKU_URL + config.TOKEN)
        return "!", 200

    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

else:
    bot.remove_webhook()
    bot.polling(none_stop=True)
