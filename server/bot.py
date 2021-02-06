# создаем телеграм бота
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.utils.request import Request

import config

req = Request(proxy_url=config.proxy)
bot = Bot(config.token, request=req)
upd = Updater(bot=bot, use_context=True)
dp = upd.dispatcher

# логирование
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
    

# приветственное сообщение
def hello(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Это Гретель! В случае неприятной ситуации она удалит вас из всех чатов, где она админ. Используйте команду /scan в чате чтобы запомнить/обновить список учатников чата, команду /sos чтобы удалиться из всех чатов и команду /kick @username чтобы удалить друг_ую учатни_цу чата")


dp.add_handler(CommandHandler('start', hello))

def main():
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()
