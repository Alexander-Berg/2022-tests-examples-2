def get_headers_event_file(mode='event'):
    logname = ''

    if mode == 'event':
        logname = 'passport-api/historydb/event.log'
    elif mode == 'auth':
        logname = 'passport-api/historydb/auth.log'
    elif mode == 'oauth':
        logname = 'oauth-server/historydb/oauth.event.log'
    elif mode == 'auth_challenge':
        logname = 'passport-api/historydb/auth_challenge.log'
    elif mode == 'passport_messages':
        logname = 'passport-api/statbox/passport-messages.log'
    elif mode == 'passport_avatars':
        logname = 'passport-api/statbox/avatars.log'
    elif mode == 'passport_statbox':
        logname = 'passport-api/statbox/statbox.log'
    elif mode == 'social-bindings':
        logname = 'socialism/social-bindings.statbox.log'

    return {
        'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
        'seqno': '509549082',
        'topic': 'rt3.iva--historydb--raw',
        'path': '/var/log/yandex/%s' % logname,
        'servier': 'pass-dd-i84.sezam.yandex.net',
        'partition': '7',
        'offset': '535729'
    }
