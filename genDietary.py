
from telegram import Update
from telegram.ext import CallbackContext
import configparser
import redis


global redis1
config = configparser.ConfigParser()
config.read('config.ini')
redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']),
                     port=(config['REDIS']['REDISPORT']))

def gen_dietary(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    diet = context.args[1]
    ret = redis1.get(diet)
    context.bot.send_message(chat_id, ret.decode('utf-8'))