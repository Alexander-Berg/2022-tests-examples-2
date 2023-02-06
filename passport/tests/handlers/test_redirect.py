# -*- coding: utf-8 -*-

from copy import copy
import json
import uuid

from furl import furl
from mock import Mock
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker.exceptions import RetpathInvalidError
from passport.backend.social.broker.handlers.redirect import RedirectHandler
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.task import (
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig


class TestRedirect(TestCase):
    def setUp(self):
        super(TestRedirect, self).setUp()

        self._fake_grants_config = FakeGrantsConfig().start()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['redirect'])

        self.request = Mock(
            consumer_ip=CONSUMER_IP1,
            header_consumer=CONSUMER1,
            ticket_body=None,
        )
        self.rh = RedirectHandler(self.request)

    def tearDown(self):
        self._fake_grants_config.stop()
        super(TestRedirect, self).tearDown()

    def build_settings(self):
        settings = super(TestRedirect, self).build_settings()
        settings['social_config'].update(
            dict(
                environment_from_id={
                    0: 'production',
                    1: 'hogwarts',
                },
                social_broker_redirect_url_from_enviroment={
                    'production': 'https://social.yandex.net/broker/redirect',
                    'hogwarts': 'https://www.hogwarts.uk/potter/harry',
                },
            ),
        )
        return settings

    def _single_redirect_test(self, url, url_args, request_args, expected_url):
        url_ = furl(url)
        url_.query = url_args

        for param_name in ['url', 'state']:
            args = copy(request_args)
            args[param_name] = url_.url
            self.request.args = args
            try:
                response = self.rh.get()
            except:
                if expected_url:
                    raise
                return
            response = json.loads(response.data)
            check_url_equals(response['location'], expected_url)

    def test_redirect_basic(self):
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback', {}, {},
            'https://social.yandex.ru/broker2/taskid/callback',
        )

        # Параметры
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback', {}, {'a': 'b'},
            'https://social.yandex.ru/broker2/taskid/callback?a=b',
        )
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback', {'a': 'b&%#c'}, {},
            'https://social.yandex.ru/broker2/taskid/callback?a=b%26%25%23c',
        )
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback#data', {'url': 'url', 'a': 'b'}, {'c': 'd'},
            'https://social.yandex.ru/broker2/taskid/callback?url=url&a=b&c=d#data',
        )

        # Схема
        self._single_redirect_test(
            'http://social.yandex.ru/broker2/taskid/callback', {}, {},
            'http://social.yandex.ru/broker2/taskid/callback',
        )
        self._single_redirect_test('htt://social.yandex.ru/broker2/taskid/callback', {}, {}, None)

        # Путевая часть
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback/', {}, {},
            'https://social.yandex.ru/broker2/taskid/callback/',
        )
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/authz_in_app/taskid/callback/', {}, {},
            'https://social.yandex.ru/broker2/authz_in_app/taskid/callback/',
        )
        self._single_redirect_test(
            'https://social.yandex.ru/broker2/taskid/callback/hello', {}, {},
            None,
        )

        # Доменное имя
        self._single_redirect_test(
            'https://social-test.yandex.ru/broker2/taskid/callback', {}, {},
            'https://social-test.yandex.ru/broker2/taskid/callback',
        )
        self._single_redirect_test(
            'https://social-rc.yandex.ru/broker2/taskid/callback', {}, {},
            'https://social-rc.yandex.ru/broker2/taskid/callback',
        )
        self._single_redirect_test(
            'https://0.social-dev.yandex.ru/broker2/taskid/callback', {}, {},
            'https://0.social-dev.yandex.ru/broker2/taskid/callback',
        )
        self._single_redirect_test(
            'https://8080.social-dev.yandex.ru/broker2/taskid/callback', {}, {},
            'https://8080.social-dev.yandex.ru/broker2/taskid/callback',
        )
        self._single_redirect_test(
            'https://social.yandex.ua/broker2/taskid/callback', {}, {},
            'https://social.yandex.ua/broker2/taskid/callback',
        )
        self._single_redirect_test('https://social.google.ru/broker2/taskid/callback', {}, {}, None)
        self._single_redirect_test('https://social.yandex.ru.google.ru/broker2/taskid/callback', {}, {}, None)
        self._single_redirect_test('https://exploit.yandex.ru/broker2/taskid/callback', {}, {}, None)

    def test_load_callback_url_from_redis(self):
        task = Task()
        task.callback_url = 'https://spam/hello?a=%D1%8F'
        task_id = self._fake_generate_task_id.build_fake_task_id()
        save_task_to_redis(self._fake_redis, task_id, task)

        self.request.args = dict(foo='bar', state=str(uuid.UUID(task_id)))
        rv = self.rh.get()

        rv = json.loads(rv.data)
        check_url_equals(rv.get('location'), 'https://spam/hello?a=%D1%8F&foo=bar')

    def test_state_from_other_environment(self):
        task_id = self._fake_generate_task_id.build_fake_task_id(environment_id=1)
        state = str(uuid.UUID(task_id))

        self.request.args = dict(foo='bar', state=state)
        rv = self.rh.get()

        rv = json.loads(rv.data)
        check_url_equals(rv.get('location'), 'https://www.hogwarts.uk/potter/harry?state=%s&foo=bar' % state)

    def test_invalid_state(self):
        self.request.args = dict(state='invalid')

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.rh.get()

        assert str(assertion.exception) == 'Invalid scheme: "invalid"'

    def test_no_state(self):
        self.request.args = dict()

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.rh.get()

        assert str(assertion.exception) == 'Empty retpath'
