# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import numbers
from urllib import urlencode

from mock import Mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.common.context import request_ctx
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
)

from .base_broker_test_data import (
    TEST_CONSUMER,
    TEST_FRONTEND_URL,
    TEST_REQUEST_ID,
    TEST_RETPATH,
    TEST_SESSION_ID,
    TEST_USER_IP,
    TEST_YANDEX_UID,
)


class TimeSpan(object):
    def __init__(self, value=0, delta=5, convert_from_string=False):
        self.delta = delta
        self.time = value
        self.convert_from_string = convert_from_string

    def __eq__(self, other):
        if self.convert_from_string:
            other = float(other)
        if not isinstance(other, numbers.Number):
            return False

        return abs(self.time - other) < self.delta

    def __repr__(self):
        return '<%s: %s +- %ds>' % (self.__class__.__name__, self.time, self.delta)


class TimeNow(TimeSpan):
    def __init__(self, delta=5, **kwargs):
        super(TimeNow, self).__init__(now.f(), delta, **kwargs)


def uniq(src, filter_):
    return [i for i in src if i not in filter_]


def iterdiff(f):
    def wrapper(a, b, *args, **kwargs):
        try:
            f(a, b, *args, **kwargs)
        except AssertionError as e:
            if isinstance(a, dict) and isinstance(b, dict):
                a_items = a.items()
                b_items = b.items()
                in_a = uniq(a_items, b_items)
                in_b = uniq(b_items, a_items)
            elif isinstance(a, (list, set, tuple)) and isinstance(b, (list, set, tuple)):
                in_a = uniq(a, b)
                in_b = uniq(b, a)
            else:
                raise e
            e.args = tuple(["\nIn first: %s\nIn second: %s" % (
                in_a,
                in_b
            )] + list(e.args[1:]))
            raise e
    return wrapper


def get_start_request(provider_code, with_session_id=False, require_auth=False):
    request = Mock()
    args = {
        'consumer': TEST_CONSUMER,
        'provider': provider_code,
        'retpath': TEST_RETPATH,
    }
    if require_auth:
        args['require_auth'] = '1'

    form = {
        'user_ip': TEST_USER_IP,
        'yandexuid': TEST_YANDEX_UID,
        'frontend_url': TEST_FRONTEND_URL,
    }
    if with_session_id:
        form['Session_id'] = TEST_SESSION_ID

    args_encoded = urlencode(args)
    request.url = 'http://socialdev-1.yandex.ru/brokerback/start?' + args_encoded
    request.host = 'socialdev-1.yandex.ru'
    request.args = args
    request.values = args
    request.scheme = 'https'
    request.headers = {}
    request.header_consumer = CONSUMER1
    request.remote_addr = request.consumer_ip = CONSUMER_IP1
    request.ticket_body = None
    request.id = TEST_REQUEST_ID
    request.form = form
    return request


def _parse_cookie(data):
    if data:
        return data.split('; ')[0][6:]


def get_callback_request(task_id, code=None, track=None, args=None, with_session_id=False, allow_bind=False):
    request = Mock()
    if not args:
        args = {'code': code}

    form = {
        'track': _parse_cookie(track),
        'user_ip': TEST_USER_IP,
        'yandexuid': TEST_YANDEX_UID,
        'frontend_url': TEST_FRONTEND_URL,
    }
    if with_session_id:
        form['Session_id'] = TEST_SESSION_ID

    if allow_bind:
        form['allow'] = '1'

    args_encoded = urlencode(args)
    request.url = 'http://socialdev-1.yandex.ru/brokerback/callback/%s?%s' % (task_id, args_encoded)
    request.host = 'socialdev-1.yandex.ru'
    request.path = '/brokerback/callback/%s' % task_id
    request.args = args
    request.values = args
    request.scheme = 'https'
    request.remote_addr = request.consumer_ip = CONSUMER_IP1
    request.headers = {}
    request.header_consumer = CONSUMER1
    request.ticket_body = None
    request.id = TEST_REQUEST_ID
    request_ctx.request_id = TEST_REQUEST_ID
    request.form = form

    if track in args and args['track']:
        request.form['track'] = _parse_cookie(args['track'])
    return request


def get_callback_request_oauth1(task_id, oauth_verifier=None, oauth_token=None, track=None, args=None):
    request = Mock()
    if not args:
        args = {
            'oauth_verifier': oauth_verifier,
            'oauth_token': oauth_token,
        }

    args_encoded = urlencode(args)
    request.url = 'http://socialdev-1.yandex.ru/brokerback/%s/callback?%s' % (task_id, args_encoded)
    request.host = 'socialdev-1.yandex.ru'
    request.path = '/brokerback/callback/%s' % task_id
    request.args = args
    request.values = args
    request.scheme = 'https'
    request.headers = {}
    request.header_consumer = CONSUMER1
    request.remote_addr = request.consumer_ip = CONSUMER_IP1
    request.ticket_body = None
    request.form = {
        'track': _parse_cookie(track),
        'user_ip': TEST_USER_IP,
        'Session_id': TEST_SESSION_ID,
        'yandexuid': TEST_YANDEX_UID,
        'frontend_url': TEST_FRONTEND_URL,
    }
    request.id = TEST_REQUEST_ID
    return request


def check_final_response(result, task):
    data = json.loads(result.data)

    ok_('cookies' in data)
    eq_(len(data['cookies']), 1)

    location = data['location']
    ok_('status=ok' in location, location)
    ok_('task_id=' in location, location)
    ok_(location.startswith(TEST_RETPATH), [location, TEST_RETPATH])

    session = task.dump_session_data()
    session = json.loads(session)
    eq_(session['tid'], task.task_id)
    for key in ['code', 'ts', 'args']:
        ok_(key in session)
