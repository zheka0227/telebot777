import os 
PORT = int(os.environ.get('PORT', 5000))
from datetime import datetime
import telebot
from telebot import types
TOKEN = '5224678135:AAFwehLAgijGzT3l7Zy60nSjTuc7xIKr1O0'
bot = telebot.TeleBot('5224678135:AAFwehLAgijGzT3l7Zy60nSjTuc7xIKr1O0')
import psycopg2
dbname='telegram'
password='321'
host='localhost'
user='postgres'


# Команда start
@bot.message_handler(commands=["start"])
def start(message, res=False):
    # Добавляем две кнопки
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Профиль")
    item2=types.KeyboardButton("Статистика")
    markup.add(item1)
    markup.add(item2)

    userId = message.from_user.id
    first_name = isNone(message.from_user.first_name)
    last_name = isNone(message.from_user.last_name)
    username = isNone(message.from_user.username)

    #aboutMan = '{0}\n{1}\n{2}\n{3}'.format(userId, first_name, last_name, username)

    bot.send_message(message.chat.id, 'бот запущен', reply_markup=markup)

    updateActions(userId, message.text)

    conn = psycopg2.connect(dbname=dbname, password=password, host=host, user=user)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE userid={0}".format(userId))
    records = cursor.fetchall()
    if len(records)==0:
        cursor.execute("INSERT INTO users (userid, firstname, lastname, username) VALUES ({0}, '{1}', '{2}', '{3}')".format(userId, first_name, last_name, username))
    else:
        cursor.execute("UPDATE users SET firstname='{1}', lastname='{2}', username='{3}' WHERE userid={0}".format(userId, first_name, last_name, username))
    conn.commit()
    cursor.close()
    conn.close()


def isNone(text, replace=''):
    if text==None:
        return replace
    else:
        return text

def updateActions(userId, message_text):
    conn = psycopg2.connect(dbname=dbname, password=password, host=host, user=user)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO actions (userid, command, date) VALUES ({0}, '{1}', '{2}')".format(userId, message_text, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    userId = message.from_user.id
    updateActions(userId, message.text)
    if message.text == "Профиль":
        first_name = isNone(message.from_user.first_name)
        last_name = isNone(message.from_user.last_name)
        username = isNone(message.from_user.username)
        aboutMan = 'userId: {0}\nfirstName: {1}\nlastName: {2}\nuserName: {3}'.format(userId, first_name, last_name, username)
        bot.send_message(message.chat.id, aboutMan)
    elif message.text == "Статистика":
        conn = psycopg2.connect(dbname=dbname, password=password, host=host, user=user)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM actions WHERE command='{0}'".format('/start'))
        records = cursor.fetchall()
        bot.send_message(message.chat.id, "Количество запусков бота: {0}".format(records[0][0]))
    else:
        firstWord = message.text.split(' ')[0]
        conn = psycopg2.connect(dbname=dbname, password=password, host=host, user=user)
        cursor = conn.cursor()
        cursor.execute("select command from actions as a1 inner join (select max(id-1) id, userid from actions group by userid) as a2 on a1.id=a2.id and a1.userid=a2.userid order by random() limit 1")
        records = cursor.fetchall()
        lastWord = records[0][0].split(' ')[-1]
        bot.send_message(message.chat.id, "{0}\n{1}".format(firstWord, lastWord))

#bot.polling(none_stop=True, interval=0)
#bot.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN) 
bot.set_webhook(' https://telbot777.herokuapp.com/' + TOKEN)