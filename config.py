import os
import json

config_path = os.environ.get('GRETEL_CONFIG_FILE')

if config_path is not None and os.path.exists(config_path):
    with open(config_path) as file:
        data = json.load(file)
        mongo_db_url = data['mongo_db']
        token = data['token']
        bot_id = int(token.split(":")[0])
else:
    config_path = 'config.json'
