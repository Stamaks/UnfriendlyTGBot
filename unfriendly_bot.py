import logging
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram import *
from telegram.ext import CallbackQueryHandler
import pickle
import random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token=pickle.load(open("./secure/token", "rb")))

my_chat_id = pickle.load(open("./secure/my_chat_id", "rb"))
tasks = pickle.load(open("./secure/tasks", "rb"))
greet_phrases = pickle.load(open("./data/greet_phrases", "rb"))
greet_questions = pickle.load(open("./data/greet_question", "rb"))
nothing_was_done_reply = pickle.load(open("./data/nothing_was_done", "rb"))
sth_was_done_reply = pickle.load(open("./data/sth_was_done", "rb"))
did_well_reply = pickle.load(open("./data/did_well", "rb"))

is_previous_message_greet_question = 0
add_task = 0

    
def start(bot, update):
    global is_previous_message_greet_question

    greet = random.choice(greet_phrases)
    bot.send_message(chat_id=update.message.chat_id, text=greet)
    greet_question = random.choice(greet_questions)
    bot.send_message(chat_id=update.message.chat_id, text=greet_question)
    is_previous_message_greet_question = 1


def echo(bot, update):
    global add_task, is_previous_message_greet_question

    if add_task == 1:
        add_task = 0
        tasks.append(update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text="Добавил \"" + update.message.text + "\"")

    elif is_previous_message_greet_question:
        if "ничего" or "нифига" or "нихуя" in update.message.text.lower():
            text = random.choice(nothing_was_done_reply)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        elif len(update.message.text.split()) < 10:
            text = random.choice(sth_was_done_reply)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        elif len(update.message.text.split()) >= 10:
            text = random.choice(did_well_reply)
            bot.send_message(chat_id=update.message.chat_id, text=text)

        is_previous_message_greet_question = 0

    else:
        bot.send_message(chat_id=update.message.chat_id, text="Ничонипонял")


def show_keyboard(bot, update):
    if len(tasks) == 0:
        key_buttons = [InlineKeyboardButton(text="Добавить", callback_data=str(-1))]
        keyboard = InlineKeyboardMarkup([key_buttons])
        bot.send_message(chat_id=update.message.chat_id, text="Упс, ты молодец, у тебя нет задач :)", reply_markup=keyboard)
    else:
        key_buttons = []
        for i in range(len(tasks)):
            key_buttons.append(InlineKeyboardButton(text=str(i+1) + ". " + tasks[i], callback_data=str(i)))
        keyboard = InlineKeyboardMarkup([key_buttons])
        bot.send_message(chat_id=update.message.chat_id, text="Лови список задач!", reply_markup=keyboard)


def callback_query(bot, update):
    global add_task

    if int(update.callback_query.data) >= 0:
        key_buttons = [InlineKeyboardButton(text="Случайно тыкнула!", callback_data=str(-2)),
                       InlineKeyboardButton(text="Сделала :)", callback_data=str(-3)),
                       InlineKeyboardButton(text="Просто удали", callback_data=str(-4))]
        keyboard = InlineKeyboardMarkup([key_buttons])
        bot.send_message(chat_id=update.message.chat_id, text="ere", reply_markup=keyboard)        
    elif int(update.callback_query.data) == -1:
        add_task = 1
    bot.send_message(chat_id=my_chat_id, text=update.callback_query.data)
    bot.edit_message_text(text="JKJKJK", chat_id=update.callback_query.message.chat_id, 
                             message_id=update.callback_query.message.message_id)


def main():
    start_handler = CommandHandler('start', start)
    show_keyboard_handler = CommandHandler('list', show_keyboard)
    callback_query_handler = CallbackQueryHandler(callback_query)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(show_keyboard_handler)
    dispatcher.add_handler(callback_query_handler)
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()