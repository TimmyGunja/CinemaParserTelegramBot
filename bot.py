import config
import os
import telebot
from flask import Flask, request
from telebot import types
import parser


bot = telebot.TeleBot(config.TOKEN)

kinoseti_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
kinoseti_menu_keyboard.add(types.KeyboardButton(text='КИНОМАКС'))
kinoseti_menu_keyboard.add(types.KeyboardButton(text='КАРО'))
kinoseti_menu_keyboard.add(types.KeyboardButton(text='ЛЮКСОР'))


@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id, "Добро пожаловать \nВыберите киносеть, используя кнопки", parse_mode='markdown')
    bot.send_message(message.chat.id, 'КИНОМАКС\nКАРО\nЛЮКСОР', reply_markup=kinoseti_menu_keyboard)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_kinoset(message):
    cinema_list_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    msg = ''
    if message.text == 'КИНОМАКС':
        bot.send_message(message.chat.id, 'Секундочку...')
        cinema_data = parser.kinomax_theaters()

        cinema_list_keyboard = types.ReplyKeyboardMarkup()

        for cinema in cinema_data:
            cinema_list_keyboard.add(types.KeyboardButton(text=cinema))

        bot.send_message(chat_id=message.chat.id, text="Введите кинотеатр", reply_markup=cinema_list_keyboard)
        bot.register_next_step_handler(message, process_kinomax_cinema_select)

    elif message.text == 'КАРО':
        bot.send_message(message.chat.id, 'Секундочку...')
        cinema_data = parser.karo_theaters()

        cinema_list_keyboard = types.ReplyKeyboardMarkup()

        for cinema in cinema_data:
            cinema_list_keyboard.add(types.KeyboardButton(text=cinema))

        bot.send_message(chat_id=message.chat.id, text="Введите кинотеатр", reply_markup=cinema_list_keyboard)
        bot.register_next_step_handler(message, process_karo_cinema_select)

    elif message.text == 'ЛЮКСОР':
        bot.send_message(message.chat.id, 'Секундочку...')
        cinema_data = parser.luxor_theaters()

        cinema_list_keyboard = types.ReplyKeyboardMarkup()

        for cinema in cinema_data:
            cinema_list_keyboard.add(types.KeyboardButton(text=cinema))

        bot.send_message(chat_id=message.chat.id, text="Введите кинотеатр", reply_markup=cinema_list_keyboard)
        bot.register_next_step_handler(message, process_luxor_cinema_select)


def process_luxor_cinema_select(message):
    bot.send_message(message.chat.id, 'Высылаю полный список кинотеатров, фильмов и расписаний...')
    bot.send_message(message.chat.id, parser.luxor_theaters())

    try:
        if message.text.lower() == 'назад':
            bot.send_message(message.chat.id, 'Выберите киносеть\nКИНОМАКС\nКАРО\nЛЮКСОР', reply_markup=kinoseti_menu_keyboard)
            return
        else:
            print("CHECKPOINT 1")
            data = parser.luxor_theaters()
            print("CHECKPOINT 2")
            if message.text in data:
                print("CHECKPOINT 3")
                if message.text == data[0]:
                    print("le")
                elif message.text == data[1]:
                    print('asdsad')
                else:
                    print("ни то ни сё")
                cin_list_keyboard = types.ReplyKeyboardMarkup()
                for cinema in data:
                    for i in cinema['cinema schedule']:
                        cin_list_keyboard.add(types.KeyboardButton(text=i))

                bot.send_message(message.chat.id, 'Выберите фильм', parse_mode='markdown', reply_markup=cin_list_keyboard)
                #bot.register_next_step_handler(message, process_, link)
            else:
                msg = bot.reply_to(message, 'Кинотеатра с таким номером не существует. Введите номер заново')
                bot.register_next_step_handler(msg, process_kinomax_cinema_select)
                return

    except Exception as e:
        bot.reply_to(message, e)



def process_karo_cinema_select(message):
    bot.send_message(message.chat.id, 'CHECKPOINT')
    try:
        if message.text.lower() == 'назад':
            bot.send_message(message.chat.id, 'Выберите киносеть\nКИНОМАКС\nКАРО\nЛЮКСОР', reply_markup=kinoseti_menu_keyboard)
            return
        else:
            bot.send_message(message.chat.id, 'CHECKPOINT')
            data = parser.karo_theaters()
            cinemas_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            current = message.text
            for cinema in data:
                if data[cinema] == current:
                    for film in data[cinema][current]:
                        cinemas_keyboard.add(types.KeyboardButton(text=film))

            bot.send_message(message.chat.id, 'Выберите фильм', parse_mode='markdown', reply_markup=cinemas_keyboard)

    except Exception as e:
        bot.reply_to(message, e)


def process_kinomax_cinema_select(message):
    try:
        if message.text.lower() == 'назад':
            bot.send_message(message.chat.id, 'Выберите киносеть\nКИНОМАКС\nКАРО\nЛЮКСОР', reply_markup=kinoseti_menu_keyboard)
            return
        else:
            data = parser.get_kinomax_cinema_list()
            if message.text in data:
                link = data[message.text][1]
                data = parser.get_kinomax_date(link)
                date_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for date in data:
                    date_keyboard.add(types.KeyboardButton(text=date))

                bot.send_message(message.chat.id, 'Выберите дату', parse_mode='markdown', reply_markup=date_keyboard)
                bot.register_next_step_handler(message, process_kinomax_date_select, link)
            else:
                msg = bot.reply_to(message, 'Кинотеатра с таким номером не существует. Введите номер заново')
                bot.register_next_step_handler(msg, process_kinomax_cinema_select)
                return

    except Exception as e:
        bot.reply_to(message, e)


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
