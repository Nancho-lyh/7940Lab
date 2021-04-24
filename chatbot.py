from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import weightlose
import genDietary
import logging
import configparser
import redis

global redis1
global gif_server

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']),
                         port=(config['REDIS']['REDISPORT']))
    global gif_server
    gif_server = config['GIFSERVER']['HOST']

    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    # dispatcher = updater.dispatcher
    # global redis1
    # redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']),
    #                      port=(os.environ['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    dispatcher.add_handler(CommandHandler("show", sendImage))
    dispatcher.add_handler(CommandHandler("start", weightlose.start_sport))
    dispatcher.add_handler(CommandHandler("end", weightlose.end_sport))
    dispatcher.add_handler(CommandHandler("count", weightlose.count_cal))
    dispatcher.add_handler(CommandHandler("diet", genDietary.gen_dietary))
    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('''CREATE DIETARY
                              /diet for muscleGain ---we will offer you a healthy menu
                              WEIGHT LOSE
                              /start xxx ---we will start a timer for you
                              /start running or /start swimming or /start jumping
                              /end xxx   ---stop your sport,end up timer
                              /count ---I will count the calories you have been burned
                              EXERCISE SHOW
                              /show <keywords>  ---send you a gif for guiding exercise
                              <keywords>includes pectorales、biceps、backmuscle、abdominal;
                              such as /show biceps
                              ''')


def hello_command(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(context.args[0])
        name = context.args[0]
        update.message.reply_text('Good day,' + name + '!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def sendImage(update: Update, context: CallbackContext) -> None:
    try:
        name = context.args[0]
        gif_url = redis1.get(name)
        if gif_url is None:
            update.message.reply_text("no guide for this exercise")
        dataval = gif_server+gif_url.decode('utf-8')+".gif"
        context.bot.sendDocument(chat_id=update.message.chat_id, document=dataval)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /show <keyword>')


if __name__ == '__main__':
    main()
