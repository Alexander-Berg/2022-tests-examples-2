# -*- coding: utf-8 -*-
import json

from nose.tools import raises
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidResponseError
from passport.backend.core.test.test_utils import with_settings

from .test_blackbox import BaseBlackboxRequestTestCase


TEST_IP = '127.0.0.1'
TEST_LOGIN = 'lensvol.test'
TEST_UID = 4000433902
TEST_ADDRESS = '%s@yandex.ru' % TEST_LOGIN


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestGetSingleEmail(BaseBlackboxRequestTestCase):
    def setUp(self):
        super(TestBlackboxRequestGetSingleEmail, self).setUp()
        self.base_reply = {
            'users': [
                {
                    'address-list': [
                        {
                            'address': TEST_ADDRESS,
                            'born-date': '2014-12-26 16:11:15',
                            'default': True,
                            'native': True,
                            'prohibit-restore': False,
                            'rpop': False,
                            'silent': False,
                            'unsafe': False,
                            'validated': True,
                        },
                    ],
                    'have_hint': False,
                    'have_password': True,
                    'id': str(TEST_UID),
                    'karma': {
                        'value': 0,
                    },
                    'karma_status': {
                        'value': 0,
                    },
                    'login': TEST_LOGIN,
                    'uid': {
                        'hosted': False,
                        'lite': False,
                        'value': str(TEST_UID),
                    },
                },
            ],
        }
        self.reset_reply()

    def reset_reply(self):
        self.set_blackbox_response_value(json.dumps(self.base_reply))

    def test_uid_user_exists_and_has_specified_email(self):
        uid, email_address = self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)

        assert uid == TEST_UID
        assert email_address is not None

        assert email_address == self.base_reply['users'][0]['address-list'][0]

    def test_uid_by_login_user_exists_and_has_specified_email(self):
        uid, email_address = self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, login=TEST_LOGIN)

        assert uid == TEST_UID
        assert email_address is not None

        assert email_address == self.base_reply['users'][0]['address-list'][0]

    def test_user_exists_email_not_found(self):
        self.base_reply['users'][0]['address-list'] = ''
        self.reset_reply()

        uid, email_address = self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)

        assert uid == TEST_UID
        assert email_address is None

    def test_user_does_not_exist(self):
        self.base_reply['users'][0] = {
            'id': '40004339022222',
            'karma': {
                'value': 0,
            },
            'karma_status': {
                'value': 0,
            },
            'uid': {},
        }
        self.reset_reply()

        uid, email_address = self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)

        assert uid is None
        assert email_address is None

    @raises(ValueError)
    def test_error_no_uid_or_login_in_params(self):
        self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS)

    @raises(BlackboxInvalidResponseError)
    def test_error_bad_reply(self):
        '''
        Случай, когда парсеру была передана что-то иное,
        нежели ответ от userinfo.
        '''
        self.base_reply = {
            'hello': 'world',
        }
        self.reset_reply()

        self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)

    @raises(BlackboxInvalidResponseError)
    def test_error_too_many_users(self):
        '''Слишком много пользователей в ответе от ЧЯ'''
        self.base_reply['users'] *= 2
        self.reset_reply()

        self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)

    @raises(BlackboxInvalidResponseError)
    def test_error_too_many_emails(self):
        '''Слишком много адресов в ответе от ЧЯ'''
        self.base_reply['users'][0]['address-list'] *= 2
        self.reset_reply()

        self.blackbox.get_single_email(TEST_IP, TEST_ADDRESS, uid=TEST_UID)
