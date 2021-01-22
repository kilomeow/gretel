with open('bot_config') as cfg:
    proxy, token = map(lambda s: s.rstrip(' \n'),
                       cfg.readlines()[:2])
    bot_id = int(token.split(":")[0])

