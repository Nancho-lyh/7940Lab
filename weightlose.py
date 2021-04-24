
from telegram import Update
from telegram.ext import CallbackContext
import configparser
import redis
import time

global redis1
config = configparser.ConfigParser()
config.read('config.ini')
redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']),
                     port=(config['REDIS']['REDISPORT']))

sport_cal = {"running":13,"swimming":14,"jumping":15}

def start_sport(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    sport_type = context.args[0]
    sport_list = ["running", "swimming", "jumping"]
    if sport_type not in sport_list:
        update.message.reply_text("we do not support this sport to lose weight!")
        return
    counter = str(chat_id) + sport_type
    start_time = int(time.time())
    redis1.set(counter, start_time)
    update.message.reply_text("you are "+sport_type +" now!")


def end_sport(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    sport_type = context.args[0]
    counter = str(chat_id) + sport_type
    end_time = redis1.get(counter)
    if end_time is None:
        update.message.reply_text("please start "+sport_type+" firstly")
        return
    res = int(time.time()) - int(end_time)
    update.message.reply_text("you have "+sport_type+" for "+str(res//60)+" minutes!")
    redis1.hincrby(chat_id, sport_type, res)
    redis1.delete(counter)


def count_cal(update: Update, context: CallbackContext):
    try:
        chat_id = update.message.chat_id
        sum = 0
        for k, v in redis1.hgetall(chat_id).items():
            cal_min = sport_cal.get(k.decode("utf-8"))
        sum += cal_min*(int(v)//60)
        context.bot.send_message(chat_id, "totally burn " +str(sum)+ " calories")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /count')