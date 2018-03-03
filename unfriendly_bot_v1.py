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
should_add_task = False
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
def list_cammand_handler(message):
    show_list()

@bot.message_handler(commands=['add'])
def add_command_handler(message):
    text = message.text.strip()
    text = text.split("/add")
    if (text[1] == ""):
        prepare_to_add_a_task()
    else:
        add_task(text[1])


@bot.message_handler(commands=['swap'])
def swap_command_handler(message):
    mes_text = message.text.strip()
    mes_text = mes_text.split("/swap")
    if (mes_text[1] == ""):
        text = "Ничонипонял >< Введите два числа - номера задач."
        # bot.send_message(my_chat_id, "Ничонипонял >< Введите два числа - номера задач.")
    else:
        find_numbers = mes_text.split(" ")
        numbers = []
        for num in find_numbers:
            if string_is_number(num):
                numbers.append(num)
        if len(numbers) != 2:
            text = "Ничонипонял >< Введите два числа - номера задач."
        else:
            if numbers[0] > 0 and numbers[0] <= len(tasks) and numbers[1] > 0 and numbers[1] <= len(tasks):
                swap_two_tasks(numbers[0], numbers[1])
                text = "Поменял местами " + str(numbers[0]) + " и " + str(numbers[1])
            else:
                text = "Некорректные номера"
        bot.send_message(my_chat_id, text)


@bot.message_handler(func=lambda m: True) # reply to every phrase
def echo_all(message):
    global should_add_task, is_previous_message_greet_question

    if should_add_task:
        add_task(message.text, should_show_list=True)

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
        show_list() # show task list


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
    prepare_to_add_a_task()


@bot.callback_query_handler(func=lambda call: call.data == "-2") # If delete button was pressed
def remove_callback(call):
    global tasks

    text = "Удалил " + tasks[delete_task_id]
    tasks.remove(tasks[delete_task_id])
    show_list(should_edit_message=True, text=text, call=call)

    pickle.dump(tasks, open("./secure/tasks", "wb"))


@bot.callback_query_handler(func=lambda call: call.data == "-3") # If done button was pressed
def done_callback(call):
    if len(tasks) > 1:
        bot.edit_message_text(random.choice(did_well_reply),
                              chat_id=my_chat_id,
                              message_id=call.message.message_id,
                              inline_message_id=call.inline_message_id) # Say sth nice
        tasks.remove(tasks[delete_task_id]) # Delete the task
        show_list()
    else:
        tasks.remove(tasks[delete_task_id]) # Same
        show_list(should_edit_message=True, call=call)

    pickle.dump(tasks, open("./secure/tasks", "wb"))


@bot.callback_query_handler(func=lambda call: call.data == "-4") # If occas button was pressed
def test_callback(call):    
    show_list(should_edit_message=True, call=call)


def show_list(should_edit_message=False, text="", call=None):
    markup = types.InlineKeyboardMarkup(row_width=1)  # Building keyboard with tasks
    for i in range(len(tasks)):
        markup.add(types.InlineKeyboardButton(str(i + 1) + ". " + tasks[i], callback_data=str(i)))
    markup.add(types.InlineKeyboardButton("Добавить задачу", callback_data="-1"))

    if text == "":
        if len(tasks) == 0:  # Choosing text
            text = "Упс, ты молодец, у тебя нет задач :)"
        else:
            text = "Лови список задач!"

    if should_edit_message:
        bot.edit_message_text(text, chat_id=my_chat_id, message_id=call.message.message_id,
                                      inline_message_id=call.inline_message_id, reply_markup=markup)
    else:
        bot.send_message(my_chat_id, text, reply_markup=markup)


def prepare_to_add_a_task(task=""):
    global should_add_task

    if (task == ""):
        bot.send_message(my_chat_id, "Какая задача?")
        should_add_task = True
    else:
        add_task(task)


def add_task(task, should_show_list=False):
    global should_add_task

    if len(task) <= 10000 and len(tasks) <= 10000:  # In case not to store big files
        tasks.append(task)
        bot.send_message(my_chat_id, "Добавил " + task)

        if should_show_list:
            show_list()

        should_add_task = 0
        pickle.dump(tasks, open("./secure/tasks", "wb"))
    else:
        bot.send_message(my_chat_id, "Хорош меня дудосить :(")


def swap_two_tasks(num1, num2):
    pass


def string_is_number(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def main():
    bot.polling()



if __name__ == '__main__':
    main()