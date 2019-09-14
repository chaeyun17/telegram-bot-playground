import logging
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Init Status
INPUT, END = range(2)

# Inline Keyboard Buttons
keyboard = [[InlineKeyboardButton("참가", callback_data='1'),
            InlineKeyboardButton("불참", callback_data='2')]]
reply_markup = InlineKeyboardMarkup(keyboard)

# data
MyDataList = set()

class MyData():
    def __init__(self, chat_id, update):
        self.chat_id = chat_id
        self.chat_instance_id = 0
        self.update = update
        self.attendee = set()
        self.absentee = set()
        self.eventMsg = ""

    def __eq__(self, other):
        if not isinstance(other, MyData):
            return NotImplemented
        
        return self.chat_id == other.chat_id

    def __hash__(self):
        return hash((self.chat_id))

def start(update, message):
    update.message.reply_text("행사 내용을 알려주세요.\n이 메시지에 답장하기로 보내주세요.")
    return INPUT

def input(update, message):
    logger.info("[START Chat] chat_id: %s", str(update.message.chat.id))
    myData = MyData(update.message.chat.id, update)
    myData.eventMsg = update.message.text

    update.message.reply_text(text=update.message.text, reply_markup=reply_markup)
    global MyDataList
    MyDataList.add(myData)

def button(update, message):
    query = update.callback_query
    logger.info("[Activity] chat_id: %s", str(query.message.chat.id))
    username = getFullUserName(update)

    mydata = getMyData(query.message.chat.id)

    if query.data == '1':
        mydata.attendee.add(username)
        if username in mydata.absentee:
            mydata.absentee.remove(username)
    elif query.data == '2':
        mydata.absentee.add(username)
        if username in mydata.attendee:
            mydata.attendee.remove(username)
    mydata.update.message.reply_text(text=getText(mydata), reply_markup=reply_markup, quote=False)
    query.answer();

def getMyData(chat_id):
    for ele in MyDataList:
        if ele.chat_id == chat_id:
            return ele

def getFullUserName(update):
    fromUser = update.callback_query.from_user
    if fromUser.last_name == None and fromUser.first_name == None:
        return fromUser.username
    elif fromUser.last_name == None:
        return fromUser.first_name
    elif fromUser.first_name == None:
        return fromUser.last_name
    else:
        return fromUser.last_name + fromUser.first_name

def getText(mydata):
    attendtext = "\n참여: " + ", ".join(mydata.attendee)
    absentText = "\n불참: " + ", ".join(mydata.absentee)
    text = mydata.eventMsg + "\n" + attendtext + absentText;
    return text

def end(update, message):
    mydata = getMyData(update.message.chat.id)
    mydata.update.message.reply_text(text=getEndText(mydata))
    MyDataList.remove(mydata)
    print("[Close]: chat_id: "+ str(update.message.chat.id))
    return ConversationHandler.END

def getEndText(mydata):
    endText = "\n\n--- 마감되었습니다 ---"
    return getText(mydata) + endText;

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def help(update, message):
    helpStr = """행사 참석자 여부를 조사하는 봇입니다. 버튼을 통해 참석 여부를 조사하며, 실시간 메시지로 진행 상황을 확인할 수 있습니다.
/start: 메시지를 통해 행사 내용을 등록할 수 있습니다. 참석자 조사 메시지가 뜹니다.
/end: 참석자 조사를 마칩니다. 결과 메시지가 나타납니다.
/help: 도움말. 이 설명을 다시 볼 수 있습니다."""
    update.message.reply_text(text=helpStr)

def main():
    updater = Updater(sys.argv[1], use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                    CommandHandler('end', end)],

        states={
            INPUT: [MessageHandler(Filters.text, input),
                    CommandHandler('end', end)]
        },

        fallbacks=[CommandHandler('end', end)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_error_handler(error)
    dp.add_handler(CommandHandler('help', help))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
