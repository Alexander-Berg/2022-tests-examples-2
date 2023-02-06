# -*- coding: utf-8 -*-
# цельнотянуто из passport_core
import threading


class RequestIdManager(object):
    thread_data = threading.local()

    @classmethod
    def _make_request_id(cls):
        request_ids = cls.thread_data.__dict__.get('request_ids')
        if request_ids:
            cls.thread_data.cached_request_id = '@%s' % ','.join(cls.thread_data.request_ids)
        else:
            cls.thread_data.cached_request_id = ''

    @classmethod
    def get_request_id(cls):
        if cls.thread_data.__dict__.get('cached_request_id'):
            request_id = cls.thread_data.cached_request_id
        else:
            request_id = ''
        return request_id

    @classmethod
    def push_request_id(cls, *args):
        if 'request_ids' not in cls.thread_data.__dict__:
            cls.thread_data.request_ids = []

        cls.thread_data.request_ids.extend(str(request_id) for request_id in args)
        cls._make_request_id()

    @classmethod
    def pop_request_id(cls):
        if cls.thread_data.__dict__.get('request_ids'):
            cls.thread_data.request_ids.pop()
            cls._make_request_id()

    @classmethod
    def clear_request_id(cls):
        cls.thread_data.request_ids = []
        cls._make_request_id()


def get_request_id():
    return RequestIdManager.get_request_id()
