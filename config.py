import os
import json

config_path = os.environ('GRETEL_CONFIG_FILE')
if config_path is None: config_path = '/run/secrets/gretel_config'

with json.load(config_path) as data:
    data = json.load(cfg)
    mongo_db_url, token = map(lambda s: s.rstrip(' \n'),
                       cfg.readlines()[:2])
    bot_id = int(token.split(":")[0])

