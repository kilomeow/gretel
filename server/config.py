with open('bot_config') as cfg:
    name, proxy, token = map(lambda s: s.rstrip(' \n'),
                       cfg.readlines()[:3])

