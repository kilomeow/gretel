import os
import json

config_path = os.environ('GRETEL_CONFIG_FILE')
if config_path is None: config_path = '/run/secrets/gretel_config'

with json.load(config_path) as data:
    mongo_db_url = data['mongo_db']
    token = data['token']
    bot_id = int(token.split(":")[0])

