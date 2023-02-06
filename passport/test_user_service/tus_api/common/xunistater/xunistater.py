# coding=utf-8
from datetime import datetime
from functools import wraps
import logging

from flask import request
from passport.backend.qa.test_user_service.tus_api.utils import retry_decorator
import requests
from requests import ConnectionError


log = logging.getLogger(__name__)


@retry_decorator(exception=(ConnectionError,))
def push_to_xunistater(signals, values):
    data = {}
    for (signal, value) in zip(signals, values):
        data[signal] = {
            'value': value
        }
    return requests.post(
        'http://localhost:10280/stats/metrics',
        json=data,
    )


def request_time(signal_name=None, suffix='avvx'):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            result = f(*args, **kwargs)
            end_time = datetime.now()
            job_time = (end_time - start_time).total_seconds()
            endpoint = request.path.strip('/').replace('/', '_')
            # Костыль, но по-другому не получилось прокинуть endpoint  декоратор
            signal = endpoint if signal_name is None else signal_name
            signal_with_suffix = 'request_time.{name}_{suffix}'.format(name=signal, suffix=suffix)
            push_to_xunistater([signal_with_suffix], [job_time])
            return result

        return wrapper

    return decorator
