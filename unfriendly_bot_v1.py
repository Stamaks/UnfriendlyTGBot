import telebot
from telebot import types
import pickle
import random
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs debug messages to console.

bot = telebot.TeleBot(pickle.load(open("./secure/token", "rb")))

my_chat_id = pickle.load(open("./secure/my_chat_id", "rb"))
tasks = pickle.load(open("./secure/tasks", "rb"))
greet_phrases = pickle.load(open("./data/greet_phrases", "rb"))
greet_questions = pickle.load(open("./data/greet_question", "rb"))
nothing_was_done_reply = pickle.load(open("./data/nothing_was_done", "rb"))
sth_was_done_reply = pickle.load(open("./data/sth_was_done", "rb"))
did_well_reply = pickle.load(open("./data/did_well", "rb"))

is_previous_message_greet_question = False
add_task = False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global is_previous_message_greet_question

    # generate greeting phrase
    greet = random.choice(greet_phrases)
    bot.send_message(my_chat_id, greet)

    # generate question
    greet_question = random.choice(greet_questions)
    bot.send_message(my_chat_id, greet_question)

    # the question was asked
    is_previous_message_greet_question = True


@bot.message_handler(commands=['list'])
def show_list(message):
    # Building keyboard with tasks
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(len(tasks)):
        markup.add(types.InlineKeyboardButton(str(i+1) + ". " + tasks[i], callback_data=str(i)))
    markup.add(types.InlineKeyboardButton("Добавить задачу", callback_data="add_button_pressed"))

    if len(tasks) == 0:
        text = "Упс, ты молодец, у тебя нет задач :)"
    else:
        text = "Лови список задач!"
    bot.send_message(my_chat_id, text, reply_markup=markup)



# reply to every phrase
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global add_task, is_previous_message_greet_question

    if add_task == 1:
        # add the task
        tasks.append(message.text)
        bot.send_message(my_chat_id, "Добавил " + message.text)

        # TODO: add task keyboard open

        add_task = 0
    elif is_previous_message_greet_question:

        # if it was a question, choose the answer
        if "ничего" or "нифига" or "нихуя" in message.text.lower():
            text = random.choice(nothing_was_done_reply)
        elif len(message.text.split()) < 10:
            text = random.choice(sth_was_done_reply)
        elif len(message.text.split()) >= 10:
            text = random.choice(did_well_reply)

        # send the answer
        bot.send_message(my_chat_id, text)
        is_previous_message_greet_question = False
    else:
        bot.send_message(my_chat_id, "Ничонипонял")
        show_list(message) # show task list


@bot.callback_query_handler(func=lambda call: int(call.data) >= 0)
def test_callback(call):
    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("Сделала!", callback_data="task_done_button_pressed")
    button2 = types.InlineKeyboardButton("Я случайно", callback_data="occas_button_pressed")
    button3 = types.InlineKeyboardButton("Удали!", callback_data="delete_task_button_pressed")
    markup.add(button1, button2, button3)
    bot.edit_message_text("Задача №" + str(int(call.data) + 1),
                          chat_id=my_chat_id, message_id=call.message.message_id, reply_markup=markup)


def main():
    bot.polling()



if __name__ == '__main__':
    main()