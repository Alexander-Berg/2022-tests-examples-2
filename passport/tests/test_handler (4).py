# -*- coding: utf-8 -*-
import json

import mock
from passport.backend.core.builders.avatars_mds_api import (
    AvatarsMdsApiInvalidFileSizeError,
    AvatarsMdsApiInvalidImageSizeError,
    AvatarsMdsApiTemporaryError,
)
from passport.backend.core.builders.avatars_mds_api.faker import (
    avatars_mds_api_upload_ok_response,
    FakeAvatarsMdsApi,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
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
from passport.backend.logbroker_client.avatars.handler import (
    AvatarsHandler,
    AvatarsHandlerException,
)
from passport.backend.logbroker_client.core.tests.test_events.base import get_headers_event_file
from passport.backend.utils.logging_mock import LoggingMock
import pytest


TEST_UID = 123456789
TEST_UNIXTIME = 1548688928
TEST_USER_IP = '127.0.0.1'

TEST_URL = 'http://smth'

NO_APPROPRIATE_EVENTS_DATA = 'tskv\tmode=hack_password\tstatus=error\n'
GOOD_EVENTS_DATA = 'tskv\tmode=upload_by_url\tunixtime=%s\tuid=%s\tavatar_to_upload=%s\tuser_ip=%s\n' % (
    TEST_UNIXTIME,
    TEST_UID,
    TEST_URL,
    TEST_USER_IP,
)
GOOD_EVENTS_DATA_SKIP_IF_SET = GOOD_EVENTS_DATA.replace('\n', '\tskip_if_set=1\n')

TEST_HEADER = get_headers_event_file(mode='passport_avatars')

TEST_AVATAR_KEY = '6vh7Xyxc6wM8pK7XOthOjJrvw8-1'
TEST_GROUP_ID = '123'


class TestAvatarsHandler(object):
    def setup_method(self, method):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'passport',
                        'ticket': TEST_TICKET,
                    }
                }
            )
        )

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                default_avatar_key='0/0-0',
                is_avatar_empty=True,
            ),
        )

        self.fake_passport = FakePassport()
        self.fake_passport.set_response_value('set_default_avatar', passport_ok_response())

        self.fake_avatars_api = FakeAvatarsMdsApi()
        self.fake_avatars_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response(TEST_GROUP_ID))

        patch_get_key = mock.patch(
            'passport.backend.core.avatars.avatars.get_avatar_mds_key',
            mock.Mock(return_value=TEST_AVATAR_KEY),
        )

        self.patches = [
            self.fake_tvm_credentials_manager,
            self.fake_blackbox,
            self.fake_passport,
            self.fake_avatars_api,
            patch_get_key,
        ]
        for patch in self.patches:
            patch.start()

        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'avatars/base.yaml',
                'avatars/testing.yaml',
                'logging.yaml',
                'avatars/export.yaml',
            ]
        )
        self.config.set_as_passport_settings()
        self.handler = AvatarsHandler(self.config)

    def teardown_method(self, method):
        for patch in reversed(self.patches):
            patch.stop()

    def assert_blackbox_called(self):
        assert len(self.fake_blackbox.requests) == 1

    def assert_passport_called(self):
        assert len(self.fake_passport.requests) == 1
        self.fake_passport.requests[0].assert_properties_equal(
            method='POST',
            url='https://passport-test-internal.yandex.ru/1/account/avatars/default/?consumer=logbroker-client',
            post_args=dict(
                uid=TEST_UID,
                key='{}/{}'.format(TEST_GROUP_ID, TEST_AVATAR_KEY),
            ),
            headers={
                'Ya-Consumer-Client-Ip': TEST_USER_IP,
                'X-Ya-Service-Ticket': TEST_TICKET,
            },
        )

    def assert_avatars_api_called(self):
        assert len(self.fake_avatars_api.requests) == 1
        self.fake_avatars_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://avatars-int.mdst.yandex.net:13000/put-yapic/{}?url={}'.format(TEST_AVATAR_KEY, TEST_URL),
        )

    def assert_blackbox_not_called(self):
        assert len(self.fake_blackbox.requests) == 0

    def assert_passport_not_called(self):
        assert len(self.fake_passport.requests) == 0

    def assert_avatars_api_not_called(self):
        assert len(self.fake_avatars_api.requests) == 0

    def test_log_and_push_metrics(self):
        config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'avatars/base.yaml',
                'avatars/testing.yaml',
                'logging.yaml',
                'avatars/export.yaml',
            ]
        )
        config.set_as_passport_settings()
        handler = AvatarsHandler(
            config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(TEST_HEADER, GOOD_EVENTS_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10301/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'avatars.entries._.var/log/yandex/passport-api/statbox/avatars.log_dmmm': {
                        'value': 1,
                    },
                    'avatars.entries.total.var/log/yandex/passport-api/statbox/avatars.log_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '/var/log/yandex/passport-api/statbox/avatars.log',
                    'handler_name': 'avatars',
                    'metric:avatars.entries._.var/log/yandex/passport-api/statbox/avatars.log': 1,
                    'metric:avatars.entries.total.var/log/yandex/passport-api/statbox/avatars.log': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_ok(self):
        self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_avatars_api_called()
        self.assert_passport_called()

    def test_no_events(self):
        self.handler.process(TEST_HEADER, NO_APPROPRIATE_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_passport_not_called()
        self.assert_avatars_api_not_called()

    def test_temporary_passport_error(self):
        self.fake_passport.set_response_side_effect('set_default_avatar', PassportTemporaryError())
        with settings_context(**dict(self.config, PASSPORT_RETRIES=1)):
            with pytest.raises(AvatarsHandlerException):
                self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_avatars_api_called()
        self.assert_passport_called()

    def test_temporary_avatars_api_error(self):
        self.fake_avatars_api.set_response_side_effect('upload_from_url', AvatarsMdsApiTemporaryError())
        with pytest.raises(AvatarsHandlerException):
            self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_avatars_api_called()
        self.assert_passport_not_called()

    def test_too_big_image(self):
        self.fake_avatars_api.set_response_side_effect('upload_from_url', AvatarsMdsApiInvalidFileSizeError())
        self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_avatars_api_called()
        self.assert_passport_not_called()

    def test_too_small_image(self):
        self.fake_avatars_api.set_response_side_effect('upload_from_url', AvatarsMdsApiInvalidImageSizeError())
        self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA)
        self.assert_blackbox_not_called()
        self.assert_avatars_api_called()
        self.assert_passport_not_called()

    def test_skip_if_set__avatar_missing(self):
        self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA_SKIP_IF_SET)
        self.assert_blackbox_called()
        self.assert_avatars_api_called()
        self.assert_passport_called()

    def test_skip_if_set__avatar_present(self):
        self.fake_blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                default_avatar_key='some-avatar-key',
                is_avatar_empty=False,
            ),
        )
        self.handler.process(TEST_HEADER, GOOD_EVENTS_DATA_SKIP_IF_SET)
        self.assert_blackbox_called()
        self.assert_avatars_api_not_called()
        self.assert_passport_not_called()
