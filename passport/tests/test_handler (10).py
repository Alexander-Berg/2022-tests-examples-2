# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.passport.exceptions import (
    PassportAccountNotFoundError,
    PassportTemporaryError,
)
from passport.backend.core.builders.passport.faker.fake_passport import (
    FakePassport,
    passport_ok_response,
)
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.test.test_utils import settings_context
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.core.tests.test_events.base import get_headers_event_file
from passport.backend.logbroker_client.passport_toloka.handler import (
    PassportTolokaHandler,
    PassportTolokaHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


TEST_UID = 123456789
TEST_UNIXTIME = 1548688928
TEST_AVATAR_KEY = '123/enc-456'
TEST_NAME = 'Elon M'


def make_data(entity, value=True, data=None, name='media_toloka_porno'):
    _data = dict(
        name=name,
        subsource='custom-toloka',
        value=value,
        entity=entity,
        source='clean-web',
        key='comment-gotthit-4',
    )
    if data:
        _data['data'] = data
    return '{}\n'.format(json.dumps(_data))


TEST_HEADER = dict(
    get_headers_event_file(),
    path='unknown',
)


class TestTolokaHandler(object):
    def setup_method(self, method):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'passport',
                        'ticket': TEST_TICKET,
                    },
                }
            )
        )
        self.fake_passport = FakePassport()

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.fake_passport,
        ]
        for patch in self.patches:
            patch.start()

        self.fake_passport.set_response_value('reset_avatar', passport_ok_response())
        self.fake_passport.set_response_value('reset_display_name', passport_ok_response())

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'passport-toloka/base.yaml',
                'passport-toloka/testing.yaml',
                'logging.yaml',
                'passport-toloka/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()
        self.handler = PassportTolokaHandler(self.config)

    def teardown_method(self, method):
        for patch in reversed(self.patches):
            patch.stop()

    def assert_passport_called(self, handle='avatar', **kwargs):
        assert len(self.fake_passport.requests) == 1
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='https://passport-test-internal.yandex.ru/1/bundle/account/reset/{}/?consumer=logbroker-client'.format(handle),
            post_args=dict(
                uid=TEST_UID,
                **kwargs
            ),
        )

    def assert_passport_not_called(self):
        assert len(self.fake_passport.requests) == 0

    def test_log_and_push_metrics(self):
        config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'passport-toloka/base.yaml',
                'passport-toloka/testing.yaml',
                'logging.yaml',
                'passport-toloka/export.yaml',
            ]
        )
        config.set_as_passport_settings()
        handler = PassportTolokaHandler(
            config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID))))

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10302/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'passport_toloka.entries._.unknown_dmmm': {
                        'value': 1,
                    },
                    'passport_toloka.entries.total.unknown_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': 'unknown',
                    'handler_name': 'passport_toloka',
                    'metric:passport_toloka.entries._.unknown': 1,
                    'metric:passport_toloka.entries.total.unknown': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_no_events(self):
        self.handler.process(TEST_HEADER, '\n')
        self.assert_passport_not_called()

    def test_temporary_passport_error(self):
        self.fake_passport.set_response_side_effect('reset_avatar', PassportTemporaryError())
        with pytest.raises(PassportTolokaHandlerException):
            self.handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID))))

    def test_ok_avatar(self):
        self.handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID)), name='media_toloka_porno'))
        self.assert_passport_called(avatar_key=TEST_AVATAR_KEY)

    def test_avatar_incorrect_resolution(self):
        self.handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID)), name='text_passport_toloka_gov'))
        self.assert_passport_not_called()

    def test_ok_full_name(self):
        self.handler.process(TEST_HEADER, make_data('full_name', data=json.dumps(dict(value=TEST_NAME, uid=TEST_UID)), name='text_passport_toloka_porno'))
        self.assert_passport_called(handle='display_name', full_name=TEST_NAME)

    def test_ok_display_name(self):
        self.handler.process(TEST_HEADER, make_data('display_name', data=json.dumps(dict(value=TEST_NAME, uid=TEST_UID)), name='text_passport_toloka_porno'))
        self.assert_passport_called(handle='display_name', public_name=TEST_NAME)

    def test_no_data(self):
        self.handler.process(TEST_HEADER, make_data('image'))
        self.assert_passport_not_called()

    def test_value_is_false(self):
        self.handler.process(TEST_HEADER, make_data('image', value=False, data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID))))
        self.assert_passport_not_called()

    def test_unknown_name(self):
        self.handler.process(TEST_HEADER, make_data('image', name='WTF', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID))))
        self.assert_passport_not_called()

    def test_unexpected_entity(self):
        self.handler.process(TEST_HEADER, make_data('unexpected_entity', data='{"uid": 2345}'))
        self.assert_passport_not_called()

    def test_ok_dry_run_avatars(self):
        with settings_context(**dict(self.config, DRY_RUN_AVATARS=True)):
            self.handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID))))
        self.assert_passport_not_called()

    def test_ok_dry_run_display_name(self):
        with settings_context(**dict(self.config, DRY_RUN_DISPLAY_NAME=True)):
            self.handler.process(TEST_HEADER, make_data('display_name', data=json.dumps(dict(value=TEST_NAME, uid=TEST_UID))))
        self.assert_passport_not_called()

    def test_ok_account_not_found_display_name(self):
        self.fake_passport.set_response_side_effect('reset_display_name', PassportAccountNotFoundError(''))
        self.handler.process(TEST_HEADER, make_data('display_name', data=json.dumps(dict(value=TEST_NAME, uid=TEST_UID)), name='text_passport_toloka_porno'))
        self.assert_passport_called(handle='display_name', public_name=TEST_NAME)

    def test_ok_account_not_found_avatar(self):
        self.fake_passport.set_response_side_effect('reset_avatar', PassportAccountNotFoundError(''))
        self.handler.process(TEST_HEADER, make_data('image', data=json.dumps(dict(avatar_key=TEST_AVATAR_KEY, uid=TEST_UID)), name='media_toloka_porno'))
        self.assert_passport_called(avatar_key=TEST_AVATAR_KEY)
