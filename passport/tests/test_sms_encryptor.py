# -*- coding: utf-8 -*-
from json import dump
import mock
from os import remove
from unittest import TestCase

from passport.backend.core.lazy_loader import LazyLoader
from passport.infra.daemons.yasmsapi.api.sms_encryptor import (
    get_sms_encryptor,
)

from passport.backend.library.configurator.test import FakeConfig

KEYS_FILE = './keys.json'


class SmsEncryptorTestCase(TestCase):
    def setUp(self):
        with open(KEYS_FILE, 'wt') as f:
            dump(
                [
                    {
                        'id': 1,
                        'body': 'abcdef',
                        'create_ts': 500,
                    },
                    {
                        'id': 2,
                        'body': 'f011fe8926e0fcfff727b6dd0cc483a2d7daaa006af9fb1796173294bfc87578',
                        'create_ts': 100,
                    },
                    {'id': 3, 'body': '123456', 'create_ts': 200},
                ],
                f,
            )

        try:
            LazyLoader.flush("SmsEncryptor")
        except Exception:
            pass

        with FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'sms_encryptor': {
                    'keys_path': KEYS_FILE,
                    'reload_period': 600,
                    'key_depth': 3,
                    'encrypt_sms': False,
                }
            },
        ):
            self.enc = get_sms_encryptor()

    def tearDown(self):
        remove(KEYS_FILE)

    def test_encryptor_off(self):

        assert self.enc.key_id == 2
        assert self.enc.encryption_key == 'f011fe8926e0fcfff727b6dd0cc483a2d7daaa006af9fb1796173294bfc87578'.decode(
            'hex'
        )
        assert self.enc.encryption_on is False

        assert 'hello' == self.enc.encrypt_sms('hello', '+74951112233')
        assert 'hello' == self.enc.encrypt_sms('hello', '+79161111111')
        assert 'hello' == self.enc.encrypt_sms('hello', '')
        assert '1:2:3' == self.enc.encrypt_sms('1:2:3', '+74951112233')
        assert '1:2:3' == self.enc.encrypt_sms('1:2:3', '')

    def test_encryptor_on(self):

        self.enc.encryption_on = True

        assert self.enc.key_id == 2
        assert self.enc.encryption_key == 'f011fe8926e0fcfff727b6dd0cc483a2d7daaa006af9fb1796173294bfc87578'.decode(
            'hex'
        )
        assert self.enc.encryption_on is True

        with mock.patch(
            'passport.infra.daemons.yasmsapi.api.sms_encryptor.urandom',
            return_value='1234567890ab1234567890ab'.decode('hex'),
        ):
            assert '1:2:1234567890ab1234567890ab:f3d2178ae9:b8a2de7b9e805352eba559e24a802652' == self.enc.encrypt_sms(
                'hello', ''
            )
            assert '1:2:1234567890ab1234567890ab:f3d2178ae9:381065ee48ed91cdfe3b8a96db6d2ad0' == self.enc.encrypt_sms(
                'hello', '12345'
            )
            assert '1:2:1234567890ab1234567890ab:f3d2178ae9:bb2f7220491482a6383581b0c9a7a483' == self.enc.encrypt_sms(
                'hello', '+79160001122'
            )
            assert (
                '1:2:1234567890ab1234567890ab:4b2dab5656d4f0f3ac0b7d6e8e7af0b55810f2028df'
                'b2d226926c6403283b744ac42f19d781e49290ca3c5abcb227846ba3b482fadd5cbca786f21'
                'b8f68b9b0b458702:c60c0e6b28509de0af5ae4eacf370a45'
                == self.enc.encrypt_sms(u'Какая гадость эта ваша заливная рыба', '')
            )
            assert (
                '1:2:1234567890ab1234567890ab:4b2dab5656d4f0f3ac0b7d6e8e7af0b55810f2028df'
                'b2d226926c6403283b744ac42f19d781e49290ca3c5abcb227846ba3b482fadd5cbca786f21'
                'b8f68b9b0b458702:155514a65dd4c7c814cc7b2919ea1ed9'
                == self.enc.encrypt_sms(u'Какая гадость эта ваша заливная рыба', '+74951112233')
            )
