from pymongo import MongoClient


client = MongoClient('mongodb://gretel_db:27017/')

users = client.gretel_bot.users


def meet_user(user):
    users.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username}}, upsert=True)


def add_user_group(user, group_id):
    users.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username},
         "$addToSet": {"groups": group_id}}, upsert=True)

def remove_user_group(user, group_id):
    users.update_one(
        {"user_id": user.id},
        {"$pull": {"groups": group_id}})


def get_user_groups(user_id):
    try:
        return users.find_one({"user_id": user_id})["groups"]
    except:
        return list()


def get_user_id(username):
    return users.find_one({"username": username})["user_id"]
