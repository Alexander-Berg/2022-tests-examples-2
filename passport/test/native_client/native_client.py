# -*- coding: utf-8 -*-


def native_client_header(
    message_class, topic, server='server1', partition=1, offset=1, path=None,
    ident=None, logtype=None,
):
    message_class = message_class.split('.')[-1]
    header = {
        'topic': topic,
        'partition': partition,
        'offset': offset,
    }
    extras = {
        'path': path,
        'server': server,
        'ident': ident,
        'logtype': logtype,
        'message_class': message_class,
    }
    extras = {k: v for k, v in extras.items() if v is not None}
    header['extra_fields'] = extras
    header.update(extras)

    return header
