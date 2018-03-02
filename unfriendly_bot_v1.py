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
delete_task_id = 0

# TODO: command swap to swap tasks

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

    markup = types.InlineKeyboardMarkup(row_width=1) # Building keyboard with tasks
    for i in range(len(tasks)):
        markup.add(types.InlineKeyboardButton(str(i+1) + ". " + tasks[i], callback_data=str(i)))
    markup.add(types.InlineKeyboardButton("Добавить задачу", callback_data="-1"))

    if len(tasks) == 0: # Choosing text
        text = "Упс, ты молодец, у тебя нет задач :)"
    else:
        text = "Лови список задач!"
    bot.send_message(my_chat_id, text, reply_markup=markup)


@bot.message_handler(func=lambda m: True) # reply to every phrase
def echo_all(message):
    global add_task, is_previous_message_greet_question

    if add_task:

        # add the task
        if len(message.text) <= 10000 and len(tasks) <= 10000: # In case not to store big files
            tasks.append(message.text)
            bot.send_message(my_chat_id, "Добавил " + message.text)
            show_list(message)

            add_task = 0
            pickle.dump(tasks, open("./secure/tasks", "wb"))
        else:
            bot.send_message(my_chat_id, "Хорош меня дудосить :(")

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


@bot.callback_query_handler(func=lambda call: int(call.data) >= 0) # If task button was presses
def task_callback(call):
    global delete_task_id

    markup = types.InlineKeyboardMarkup(row_width=3)
    button1 = types.InlineKeyboardButton("Сделала!", callback_data="-3")
    button2 = types.InlineKeyboardButton("Я случайно", callback_data="-4")
    button3 = types.InlineKeyboardButton("Удали!", callback_data="-2")
    markup.add(button1, button2, button3)
    bot.edit_message_text("Задача №" + str(int(call.data) + 1),
                          chat_id=my_chat_id, message_id=call.message.message_id, reply_markup=markup)
    delete_task_id = int(call.data) # In case user presses "delete" the next step


@bot.callback_query_handler(func=lambda call: call.data == "-1") # If add button was pressed
def add_callback(call):
    global add_task

    bot.send_message(my_chat_id, "Какая задача?")
    add_task = True


@bot.callback_query_handler(func=lambda call: call.data == "-2") # If delete button was pressed
def remove_callback(call):
    global tasks

    bot.send_message(my_chat_id, "Удалил " + tasks[delete_task_id])
    tasks.remove(tasks[delete_task_id])
    show_list(call.message)

    pickle.dump(tasks, open("./secure/tasks", "wb"))


@bot.callback_query_handler(func=lambda call: call.data == "-3") # If done button was pressed
def done_callback(call):
    bot.send_message(my_chat_id, random.choice(did_well_reply)) # Say sth nice

    remove_callback(call) # Delete the task


@bot.callback_query_handler(func=lambda call: call.data == "-4") # If occas button was pressed
def test_callback(call):
    show_list(call.message)

def main():
    bot.polling()



if __name__ == '__main__':
    main()