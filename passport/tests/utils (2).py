# -*- coding: utf-8 -*-


def get_headers_event_file(mode='event'):
    logname = ''

    if mode == 'event':
        logname = 'event.log'
    elif mode == 'auth':
        logname = 'auth.log'
    elif mode == 'oauth':
        logname = 'oauth.event.log'

    return {
        'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
        'seqno': '509549082',
        'topic': 'rt3.iva--historydb--raw',
        'path': '/var/log/yandex/passport-api/historydb/%s' % logname,
        'servier': 'pass-dd-i84.sezam.yandex.net',
        'partition': '7',
        'offset': '535729'
    }
