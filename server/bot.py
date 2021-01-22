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
                             text="Привет! Это Гретель! В случае неприятной ситуации я удалю вас из всех чатов, где вы отметились. Используйте команду /checkin в чате чтобы вас запомнили, команду /sos чтобы удалиться из всех чатов и команду /hide @username чтобы скрыть друг_ую учатни_цу")

def start(update, context):
    hello(update, context)
    db.meet_user(update.message.from_user)


def is_admin(chat):
    botadmin = next(filter(lambda d: d.user.id == config.bot_id, chat.get_administrators()), None)
    return botadmin and botadmin.can_restrict_members
    
def is_supergroup(chat):
    return chat.type == "supergroup"

def check_functionality(chat):
    msg = []
    if not is_admin(chat):
        msg.append("Для функционирования я должна быть *администратором* с правом *бана*.")
    if not is_supergroup(chat):
        msg.append("Чтобы я могла удалять пользователей, это должна быть *супергруппа*.")
    if msg:
        bot.send_message(chat_id=chat.id, text=" ".join(msg), parse_mode="Markdown")

def check_in(update, context):
    user = update.message.from_user
    hide(user, update)
    check_functionality(update.effective_chat)


def new_users(update, context):
    for user in update.message.new_chat_members:
        if user.id == config.bot_id:
            hello(update, context)
        else:
            hide(user, update)
    check_functionality(update.effective_chat)


def hide(user, update):
    db.add_user_group(user, update.effective_chat.id)
    update.message.reply_text(f"В случае опасности я спрячу *{user.username}*!",
    parse_mode="Markdown")


def sos_message(update, context):
    update.message.reply_text("Поняла! Не переживай")
    remove_user(update.message.from_user.id)
    try:
        bot.send_message(chat_id=update.message.from_user.id,
                         text="Вы в домике!")
    except:
        pass

def hide(update, context):
    usernames = list()
    for mention in filter(lambda e: e["type"] == "mention",
                          update.message.entities):
        usernames.append( update.message.text[mention.offset+1:mention.offset+mention.length])
    users = list()
    not_found_usernames = list()
    for un in usernames:
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
            cm = bot.get_chat_member(group_id, user_id)
            user = cm.user
            chat = bot.get_chat(group_id)
        except:
            # no such user in chat, could not access chat etc...
            pass
        else:
            if not cm["status"] == "left":
                try:
                    bot.unban_chat_member(group_id, user_id)
                except Exception as e:
                    try:
                        bot.send_message(chat_id=group_id, 
                                     text=f"От @{user.username} поступил сигнал тревоги, но я не могу удалить! :C Сделайте это вручную")
                    except:
                        # ?? could not send message to this chat
                        db.remove_user_group(user, group_id)
                    else:
                        check_functionality(chat)
                else:
                    bot.send_message(chat_id=group_id,
                                     text=f"@{user.username} в домике!")


dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('checkin', check_in))
dp.add_handler(CommandHandler('sos', sos_message))
dp.add_handler(CommandHandler('hide', hide))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_users))

def main():
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()
