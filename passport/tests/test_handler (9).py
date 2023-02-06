# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.clean_web_api import CleanWebTemporaryError
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import (
    clean_web_api_simple_response,
    FakeCleanWebAPI,
)
from passport.backend.core.builders.passport.exceptions import PassportTemporaryError
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
from passport.backend.logbroker_client.passport_clean_web.handler import (
    PassportCleanWebHandler,
    PassportCleanWebHandlerException,
)
from passport.backend.utils.logging_mock import LoggingMock
import pytest


TEST_UID = 123456789
TEST_UNIXTIME = 1548688928
TEST_AVATAR_KEY = '123/enc-456'
TEST_NAME = 'test name'


def make_test_data(entity, value):
    return 'tskv\tevent=account_modification\tentity=%s\told=-\tnew=%s\tunixtime=%s\tuid=%s\n' % (
        entity,
        value,
        TEST_UNIXTIME,
        TEST_UID,
    )


TEST_NO_APPROPRIATE_EVENTS_DATA = 'tskv\tmode=hack_password\tstatus=error\n'
TEST_AVATAR_SET_DATA = make_test_data('person.default_avatar', TEST_AVATAR_KEY)
TEST_EMPTY_NEW_DATA = make_test_data('person.default_avatar', '-') + make_test_data('person.display_name', '-') + make_test_data('person.fullname', '-')

TEST_HEADER = get_headers_event_file(mode='passport_statbox')


class TestCleanWebHandler(object):
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
        self.fake_blackbox = FakeBlackbox()
        self.fake_cleanweb_api = FakeCleanWebAPI()
        self.fake_passport = FakePassport()

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.fake_blackbox,
            self.fake_cleanweb_api,
            self.fake_passport,
        ]
        for patch in self.patches:
            patch.start()

        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        self.fake_cleanweb_api.set_response_value('', clean_web_api_simple_response(False))
        self.fake_passport.set_response_value('reset_avatar', passport_ok_response())

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'passport-clean-web/base.yaml',
                'passport-clean-web/testing.yaml',
                'logging.yaml',
                'passport-clean-web/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()
        self.handler = PassportCleanWebHandler(self.config)

    def teardown_method(self, method):
        for patch in reversed(self.patches):
            patch.stop()

    def assert_passport_reset_avatar_called(self, index=-1):
        assert len(self.fake_passport.requests) == 1
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='https://passport-test-internal.yandex.ru/1/bundle/account/reset/avatar/?consumer=logbroker-client',
            post_args=dict(
                uid=TEST_UID,
                avatar_key=TEST_AVATAR_KEY,
            ),
        )

    def assert_passport_not_called(self):
        assert len(self.fake_passport.requests) == 0

    def assert_cleanweb_called(self, uid, type, key, auto_only, **kwargs):
        assert len(self.fake_cleanweb_api.requests) == 1
        self.fake_cleanweb_api.requests[0].assert_properties_equal(
            method='POST',
            url='https://cw-router-dev.common.yandex.net/',
            headers={'Content-Type': 'application/json'},
            json_data=dict(
                jsonrpc='2.0',
                method='process',
                id=1234,
                params=dict(
                    service='passport',
                    type=type,
                    key=key,
                    puid=str(uid),
                    body=dict(
                        auto_only=auto_only,
                        **kwargs
                    ),
                ),
            ),
        )

    def assert_cleanweb_called_avatar(self, uid, event_timestamp, avatar_key, auto_only=False):
        self.assert_cleanweb_called(
            uid,
            'image',
            'avatar_cl_check_%s_%s' % (uid, event_timestamp),
            auto_only,
            image_url='https://avatars.mdst.yandex.net/get-yapic/%s/orig' % avatar_key,
            verdict_data=json.dumps(dict(
                uid=uid,
                avatar_key=avatar_key,
            )),
        )

    def assert_cleanweb_called_name(self, field, uid, event_timestamp, name, auto_only=False):
        self.assert_cleanweb_called(
            uid,
            'user_data',
            '%s_cl_check_%s_%s' % (field, uid, event_timestamp),
            auto_only,
            verdict_data=json.dumps(dict(
                uid=uid,
                value=name,
            )),
            **{
                field: name,
            }
        )

    def assert_cleanweb_not_called(self):
        assert len(self.fake_cleanweb_api.requests) == 0

    def test_log_and_push_metrics(self):
        config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'passport-clean-web/base.yaml',
                'passport-clean-web/testing.yaml',
                'logging.yaml',
                'passport-clean-web/export.yaml',
            ]
        )
        config.set_as_passport_settings()
        handler = PassportCleanWebHandler(
            config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )
        self.fake_cleanweb_api.set_response_value('', clean_web_api_simple_response(True))

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10299/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'passport_clean_web.entries._.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 1,
                    },
                    'passport_clean_web.entries.total.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '/var/log/yandex/passport-api/statbox/statbox.log',
                    'handler_name': 'passport_clean_web',
                    'metric:passport_clean_web.entries._.var/log/yandex/passport-api/statbox/statbox.log': 1,
                    'metric:passport_clean_web.entries.total.var/log/yandex/passport-api/statbox/statbox.log': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_no_events(self):
        self.handler.process(TEST_HEADER, TEST_NO_APPROPRIATE_EVENTS_DATA)
        self.assert_cleanweb_not_called()
        self.assert_passport_not_called()

    def test_temporary_cleanweb_error(self):
        self.fake_cleanweb_api.set_response_side_effect('', CleanWebTemporaryError())
        with pytest.raises(PassportCleanWebHandlerException):
            self.handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)

    def test_temporary_passport_error(self):
        self.fake_passport.set_response_side_effect('reset_avatar', PassportTemporaryError())
        with pytest.raises(PassportCleanWebHandlerException):
            self.handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)

    def test_ok_avatar(self):
        self.handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)
        self.assert_cleanweb_called_avatar(TEST_UID, TEST_UNIXTIME, TEST_AVATAR_KEY)
        self.assert_passport_reset_avatar_called()

    def test_ok_fullname(self):
        self.handler.process(TEST_HEADER, make_test_data('person.fullname', TEST_NAME))
        self.assert_cleanweb_called_name('full_name', TEST_UID, TEST_UNIXTIME, TEST_NAME)
        self.assert_passport_not_called()

    def test_ok_displayname(self):
        self.handler.process(TEST_HEADER, make_test_data('person.display_name', 'p:{}'.format(TEST_NAME)))
        self.assert_cleanweb_called_name('display_name', TEST_UID, TEST_UNIXTIME, TEST_NAME)
        self.assert_passport_not_called()

    def test_ok_wo_using_auto_verdict(self):
        with settings_context(**dict(self.config, CLEAN_WEB_USE_AUTO_VERDICTS=False)):
            self.handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)
        self.assert_cleanweb_called_avatar(TEST_UID, TEST_UNIXTIME, TEST_AVATAR_KEY)
        self.assert_passport_not_called()

    def test_new_value_is_empty_event(self):
        self.handler.process(
            TEST_HEADER,
            TEST_EMPTY_NEW_DATA,
        )
        self.assert_cleanweb_not_called()
        self.assert_passport_not_called()

    def test_avatars_auto_only(self):
        with settings_context(**dict(self.config, CLEAN_WEB_AVATARS_AUTO_ONLY=True)):
            self.handler.process(TEST_HEADER, TEST_AVATAR_SET_DATA)
        self.assert_cleanweb_called_avatar(TEST_UID, TEST_UNIXTIME, TEST_AVATAR_KEY, auto_only=True)
        self.assert_passport_reset_avatar_called()

    def test_names_auto_only(self):
        with settings_context(**dict(self.config, CLEAN_WEB_NAMES_AUTO_ONLY=True)):
            self.handler.process(TEST_HEADER, make_test_data('person.full_name', TEST_NAME))
            self.assert_cleanweb_not_called()
