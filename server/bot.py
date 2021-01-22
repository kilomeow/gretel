# создаем телеграм бота
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.utils.request import Request

import config, db

req = Request(proxy_url=config.proxy) if config.proxy else Request()
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
                             text="Привет! Это Гретель! В случае неприятной ситуации я удалю вас из всех чатов, где вы отметились. Используйте команду /checkin в чате чтобы вас запомнили, команду /sos чтобы удалиться из всех чатов и команду /kick @username чтобы удалить друг_ую учатни_цу чата")
    db.meet_user(update.message.from_user)


def is_admin(chat):
    botadmin = next(filter(lambda d: d.user.id == config.bot_id, chat.get_administrators()), None)
    return botadmin and botadmin.can_restrict_members
    

def check_in(update, context):
    user = update.message.from_user
    hide(user, update)
    if not is_admin(update.effective_chat):
        bot.send_message(chat_id=update.effective_chat.id,
        text="Но для этого мне нужны *права администратора*",
        parse_mode="Markdown")


def new_users(update, context):
    for user in update.message.new_chat_members:
        hide(user, update)
    if not is_admin(update.effective_chat):
        bot.send_message(chat_id=update.effective_chat.id,
        text="Но для этого мне нужны *права администратора*",
        parse_mode="Markdown")


def hide(user, update):
    db.add_user_group(user, update.effective_chat.id)
    update.message.reply_text(f"В случае опасности я спрячу *{user.username}*!",
    parse_mode="Markdown")


def sos_message(update, context):
    update.message.reply_text("Поняла! Не переживай")
    remove_user(update.message.from_user.id)
    update.message.reply_text("Вы надежно спрятаны!")


def kick(update, context):
    usernames = list()
    for mention in filter(lambda e: e["type"] == "mention",
                          update.message.entities):
        usernames.append( update.message.text[mention.offset+1:mention.offset+mention.length])
    users = list()
    not_found_usernames = list()
    for un in usernames:
        print(db.get_user_id(un))
        try:
            uid = db.get_user_id(un)
        except:
            not_found_usernames.append(un)
        else:
            users.append(uid)
    if not_found_usernames:
        update.message.reply_text(f"Я не знаю {', '.join(map(lambda n: '@'+n, not_found_usernames))} :C")
    for uid in users: remove_user(uid)
    

def remove_user(user_id):
    for group_id in db.get_user_groups(user_id):
        try:
            user = bot.get_chat_member(group_id, user_id).user
        except:
            # no such user in chat
            pass
        else:
            try:
                bot.unban_chat_member(group_id, user_id)
            except:
                bot.send_message(chat_id=group_id, 
                                 text=f"Не могу удалить @{user.username} :C")
            else:
                bot.send_message(chat_id=group_id,
                                 text=f"@{user.username} в домике!")


dp.add_handler(CommandHandler('start', hello))
dp.add_handler(CommandHandler('checkin', check_in))
dp.add_handler(CommandHandler('sos', sos_message))
dp.add_handler(CommandHandler('kick', kick))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_users))

def main():
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()
