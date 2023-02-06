# -*- coding: utf-8 -*-

from flask import make_response


def ping():
    """
    Ручка для тестирования того, что все это вообще работоспособно
    """
    return make_response('Pong', 200, {'Content-Type': 'text/plain'})


__all__ = (
    'ping',
)
