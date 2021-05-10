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
                             text="Привет! Это Гретель! В случае неприятной ситуации я удалю вас из всех чатов, где вы отметились. Используйте команду /checkin в чате чтобы вас запомнили, команду /sos чтобы удалиться из всех чатов и команду /hide @username чтобы скрыть друг_ую учатни_цу. Используйте команду /invite @username чтобы выслать приглашение обратно в чат")

def start(update, context):
    hello(update, context)
    db.meet_user(update.message.from_user)


def is_admin(uid, chat):
   return bool(next(filter(lambda d: d.user.id == uid, chat.get_administrators()), None))


def check_admin_rights(chat):
    botadmin = next(filter(lambda d: d.user.id == config.bot_id, chat.get_administrators()), None)
    return botadmin and botadmin.can_restrict_members


def check_functionality(chat):
    res = {}
    try:
        res["is_admin"] = check_admin_rights(chat)
    except:
        res["is_admin"] = None
    res["is_group"] = "group" in chat.type
    res["is_supergroup"] = chat.type == "supergroup"
    return res

def compose_functionality_message(functions, chat):
    msg = []
    if not functions["is_admin"]:
        msg.append("Для функционирования я должна быть *администратором* с правом *бана*.")
    if not functions["is_supergroup"]:
        msg.append("Чтобы я могла удалять пользователей, это должна быть *супергруппа*.")
    if msg:
        bot.send_message(chat_id=chat.id, text=" ".join(msg), parse_mode="Markdown")


def can_hide_user(user, chat):
    return (not user.is_bot) and (not is_admin(user.id, chat))


def check_in(update, context):
    user = update.message.from_user
    chat = update.effective_chat
    functions = check_functionality(chat)
    if not functions["is_group"]:
        update.message.reply_text("Это не группа, так что здесь не нужен чекин!")
    else:
        if user.is_bot:
            update.message.reply_text("Я могу спрятать бота!")
        elif not can_hide_user(user, chat):
            update.message.reply_text("Я не смогу тебя спрятать, пока ты админ :C")
        elif functions["is_supergroup"]:
            remember(user, update)
        compose_functionality_message(functions, chat)


def new_users(update, context):
    for user in update.message.new_chat_members:
        if user.id == config.bot_id:
            hello(update, context)
        elif not user.is_bot:
            remember(user, update)
    compose_functionality_message(
        check_functionality(update.effective_chat), 
        update.effective_chat)


def remember(user, update):
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


def parse_mentions(message):
    usernames = list()
    for mention in filter(lambda e: e["type"] == "mention",
                          message.entities):
        usernames.append( message.text[mention.offset+1:mention.offset+mention.length])
    users = dict()
    not_found_usernames = list()
    for un in usernames:
        try:
            uid = db.get_user_id(un)
        except:
            not_found_usernames.append(un)
        else:
            users[un] = uid
    return {"id": users, 
            "not_found": not_found_usernames}


def hide(update, context):
    users = parse_mentions(update.message)
    if users["not_found"]:
        update.message.reply_text(f"Я не знаю {', '.join(map(lambda n: '@'+n, users['not_found']))} :C")
    for un, uid in users['id'].items(): remove_user(uid)    


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


def return_to_chat(chat, un, uid):
    link = chat.invite_link
    if not link:
        bot.send_message(chat_id=chat.id,
                         text=f"В вашем чате нет пригласительной ссылки, верните @{un} вручную!")
    else:
        try:
            bot.send_message(chat_id=uid,
                             text=f"Возвращайся обратно! {link}")
        except:
            bot.send_message(chat_id=chat.id,
                             text=f"Не удалось отправить приглашение @{un}, пришлите вручную ссылку: f{link}")


def invite(update, context):
    compose_functionality_message(
        check_functionality(update.effective_chat), 
        update.effective_chat)
    users = parse_mentions(update.message)
    if users["not_found"]:
        update.message.reply_text(f"Я не знаю {', '.join(map(lambda n: '@'+n, users['not_found']))} :C")
    for un, uid in users['id'].items(): return_to_chat(bot.get_chat(update.effective_chat.id), un, uid)


def echo(update, context):
    text = update.message.text
    if text.split(" ")[1] == config.token:
        groups = set()
        for d in db.users.find():
            if d.get("groups"): groups.update(d["groups"])
        for gid in groups:
            try:
                bot.send_message(chat_id = gid,
                                 text = " ".join(text.split(" ")[2:]))
            except:
                pass


dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('checkin', check_in))
dp.add_handler(CommandHandler('sos', sos_message))
dp.add_handler(CommandHandler('hide', hide))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_users))
dp.add_handler(CommandHandler('invite', invite))
dp.add_handler(CommandHandler('echo', echo))

def main():
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()
