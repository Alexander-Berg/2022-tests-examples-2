# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from urllib import urlencode
from urlparse import urlparse

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.social.broker.communicators.communicator import (
    AuthorizeOptions,
    OAuth2Communicator,
)
from passport.backend.social.broker.communicators.FacebookCommunicator import FacebookCommunicator
from passport.backend.social.broker.exceptions import (
    CommunicationFailedError,
    DisplayInvalidError,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.broker.tests.communicators import TestCommunicator
from passport.backend.social.common.application import Application
from passport.backend.social.common.test.consts import (
    EXTERNAL_APPLICATION_ID1,
    TASK_ID1,
)
from passport.backend.social.common.useragent import Url


def minus_separated_task_id(task_id):
    """
    Разделяет строку с task_id литерой "-"
    """
    # Первый блок произвольной длины, длина остальных блоков:
    lens = [4, 4, 4, 12]

    bits = list()
    head = str(task_id)
    for ln in reversed(lens):
        bits.insert(0, head[-ln:])
        head = head[:len(head) - ln]
    bits.insert(0, head)
    return '-'.join(bits)


class TestCommunicatorsBasic(TestCase):
    def build_settings(self):
        settings = super(TestCommunicatorsBasic, self).build_settings()
        settings['social_config'].update(
            domain_to_redirect_url={
                '.yandex.ru': 'https://social.yandex.ru/broker/redirect',
                'social.yandex.ru': 'https://social.yandex.ru/broker/redirect',

                '.yandex.com.tr': 'https://social.yandex.com.tr/broker/redirect',
                'social.yandex.com.tr': 'https://social.yandex.com.tr/broker/redirect',

                '.kinopoisk.ru': 'https://www.kinopoisk.ru/social_redirect',
                'www.kinopoisk.ru': 'https://www.kinopoisk.ru/social_redirect',
            },
        )
        return settings

    def test_process_redirector(self):
        app = TestCommunicator.get_application('fb')

        def check_output(redirect_uri_domain, app_domain, redirect_to, url_param):
            app.domain = app_domain
            communicator = OAuth2Communicator(app=app)
            redirect_uri = 'https://%s/taskid/callback' % redirect_uri_domain
            result = communicator._build_redirect_args(app, redirect_uri)
            result = result['redirect_uri']
            redirect = urlparse(result)
            eq_(redirect.netloc, redirect_to)
            if url_param:
                assert redirect.query == urlencode({'url': redirect_uri})
            else:
                assert redirect.query == ''

        check_output('www.kinopoisk.ru',       'www.kinopoisk.ru',   'www.kinopoisk.ru',       False)
        check_output('social.yandex.ru',       'www.kinopoisk.ru',   'www.kinopoisk.ru',       True)
        check_output('social.yandex.ru',       '.kinopoisk.ru',      'www.kinopoisk.ru',       True)

        check_output('social.yandex.ru',       'social.yandex.ru',  'social.yandex.ru',       False)
        check_output('social.yandex.com',      'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('social.yandex.com.tr',   'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('social-test.yandex.ru',  'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('social-test.yandex.com', 'social.yandex.ru',  'social.yandex.ru',       True)

        check_output('social.yandex.ru',       '.yandex.ru',        'social.yandex.ru',       False)
        check_output('social.yandex.com',      '.yandex.ru',        'social.yandex.ru',       True)
        check_output('social.yandex.com.tr',   '.yandex.ru',        'social.yandex.ru',       True)
        check_output('social-test.yandex.ru',  '.yandex.ru',        'social-test.yandex.ru',  False)
        check_output('social-test.yandex.com', '.yandex.ru',        'social-test.yandex.ru',  True)

        check_output('social.yandex.com.tr', 'social.yandex.com.tr', 'social.yandex.com.tr',  False)
        check_output('yandex.com.tr',            'yandex.com.tr',    'yandex.com.tr',         False)

        check_output('1.social.yandex.ru',       'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('1.social.yandex.com',      'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('1.social-test.yandex.ru',  'social.yandex.ru',  'social.yandex.ru',       True)
        check_output('1.social-test.yandex.com', 'social.yandex.ru',  'social.yandex.ru',       True)

        check_output('1.social.yandex.ru',       '.yandex.ru',        '1.social.yandex.ru',       False)
        check_output('1.social.yandex.com',      '.yandex.ru',        'social.yandex.ru',       True)
        check_output('1.social-test.yandex.ru',  '.yandex.ru',        '1.social-test.yandex.ru',  False)
        check_output('1.social-test.yandex.com', '.yandex.ru',        'social.yandex.ru',  True)


class TestMisc(TestCase):
    @raises(DisplayInvalidError)
    def test_invalid_display(self):
        FacebookCommunicator(TestCommunicator.get_application('fb'), display='qwerty')

    def test_get_scope(self):
        com = OAuth2Communicator(app=Application())
        com.default_scopes = ['foo', 'bar']

        assert com.get_scope() == 'bar,foo'
        assert com.get_scope(['qwerty']) == 'bar,foo,qwerty'

        com.app.allowed_scope = 'qwerty foo'
        com.default_scopes = ['foo', 'bar']

        assert com.get_scope() == 'bar,foo'
        assert com.get_scope(['qwerty', 'spam']) == 'bar,foo,qwerty'

    def test_get_exchange_value_from_callback_ok(self):
        communicator = FacebookCommunicator(TestCommunicator.get_application('fb'))
        eq_(communicator.get_exchange_value_from_callback({'code': '123'}), '123')

    @raises(CommunicationFailedError)
    def test_get_exchange_value_from_callback_error(self):
        communicator = FacebookCommunicator(TestCommunicator.get_application('fb'))
        communicator.get_exchange_value_from_callback({})


class TestOpaqueState(TestCase):
    def setUp(self):
        super(TestOpaqueState, self).setUp()
        domain = 'social.yandex.net'
        self.provider_client_id = EXTERNAL_APPLICATION_ID1
        self.comm = OAuth2Communicator(
            app=Application(
                domain=domain,
                id=self.provider_client_id,
            ),
        )
        self.comm.IS_OPAQUE_STATE = True
        self.comm.OAUTH_AUTHORIZE_URL = 'https://vk.com/auth'
        self.redirect_uri = 'https://%s/broker/redirect' % domain

    def test(self):
        authorize_url = self.comm.get_authorize_url(AuthorizeOptions(
            callback_url='https://social.yandex.ru/broker2/%s/callback' % TASK_ID1,
        ))

        check_url_equals(
            authorize_url,
            str(
                Url(
                    self.comm.OAUTH_AUTHORIZE_URL,
                    dict(
                        client_id=self.provider_client_id,
                        redirect_uri=self.redirect_uri,
                        response_type='code',
                        state=minus_separated_task_id(TASK_ID1),
                    ),
                ),
            ),
        )
