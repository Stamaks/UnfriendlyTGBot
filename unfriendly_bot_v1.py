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

is_previous_message_greet_question = 0
add_task = 0


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
    is_previous_message_greet_question = 1


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
        is_previous_message_greet_question = 0
    else:
        bot.send_message(my_chat_id, "Ничонипонял")
        show_keyboard()


@bot.callback_query_handler(func=lambda call: call.data == "1")
def test_callback(call):
   pass



@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    # Process all chosen_inline_result.
    pass


@bot.inline_handler(lambda query: query.query == 1)
def query_text(inline_query):
    # try:
    #     r = types.InlineQueryResultArticle('1', 'Result', types.InputTextMessageContent('Result message.'))
    #     r2 = types.InlineQueryResultArticle('2', 'Result2', types.InputTextMessageContent('Result message2.'))
    #     bot.answer_inline_query(inline_query.id, [r, r2])
    # except Exception as e:
    #     print(e)
    print("aaaa")


def show_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    but1 = types.InlineKeyboardButton("1dgdgjdkjhkg", callback_data=1)
    but2 = types.InlineKeyboardButton("1sfdsdsd", callback_data=2)
    markup.add(but1, but2)
    bot.send_message(my_chat_id, "text", reply_markup=markup)


def main():
    bot.polling()



if __name__ == '__main__':
    main()