import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, message):
    update.message.reply_text("Hello! Send me a message. I will append your name to the message.")

def help(update, message):
    example = """ 
* Example Input Message: 
    [Invitation 000 Events] 
    if you wanna attend, leave your name. 

    - Attendee: John

* Output Message:
    [Invitation 000 Events] 
    if you wanna attend, leave your name. 

    - Attendee: John YourName
    """
    update.message.reply_text(example)

def appendName(update, message):
    user = update.message.from_user
    text = update.message.text;
    text = text + " " + user.last_name + user.first_name;

    update.message.reply_text(text=text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():

    updater = Updater("token here", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(filters=Filters.text, callback=appendName))
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
