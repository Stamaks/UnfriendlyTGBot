import telebot
import pickle
import random

bot = telebot.TeleBot(pickle.load(open("./secure/token", "rb")))

my_chat_id = pickle.load(open("./secure/my_chat_id", "rb"))
tasks = pickle.load(open("./secure/tasks", "rb"))
greet_phrases = pickle.load(open("./data/greet_phrases", "rb"))
greet_questions = pickle.load(open("./data/greet_question", "rb"))
nothing_was_done_reply = pickle.load(open("./data/nothing_was_done", "rb"))
sth_was_done_reply = pickle.load(open("./data/sth_was_done", "rb"))
did_well_reply = pickle.load(open("./data/did_well", "rb"))

is_previous_message_greet_question = 0
add_task = 0


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global is_previous_message_greet_question

    # generate greeting phrase
    greet = random.choice(greet_phrases)
    bot.reply_to(message, greet)

    # generate question
    greet_question = random.choice(greet_questions)
    bot.reply_to(message, greet_question)

    # the question was asked
    is_previous_message_greet_question = 1


# reply to every phrase
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global add_task, is_previous_message_greet_question

    if add_task == 1:
        add_task = 0
        tasks.append(message.text)
        bot.reply_to(message, "Добавил " + message.text)
        