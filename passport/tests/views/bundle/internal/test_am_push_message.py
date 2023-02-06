# -*- coding: utf-8 -*-

import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.am_pushes.push_request import (
    AppTargetingTypes,
    Platforms,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_UID = 12345
TEST_PUSH_SERVICE = 'push_service'
TEST_EVENT_NAME = 'event_name'
TEST_TITLE = u'Тайтл'
TEST_BODY = u'Сообщение'
TEST_SUBTITLE = u'Ещё тайтл'
TEST_WEBVIEW_URL = u'https://test.ru/404?not_found=1&found=0'


@with_settings_hosts(
    AM_VERSION_CAPABILITIES_INFO=[dict(version=(1, 0, 0), caps=['cap1', 'cap2'])]
)
class TestAmPushMessage(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'internal': ['am_push_message_test']}))

        self.base_request_patch = mock.patch(
            'passport.backend.api.views.bundle.internal.controllers.ChallengePushRequest',
            mock.Mock(),
        )
        self.base_request_patch.start()

        self.fake_request = mock.Mock()
        self.request_patch = mock.patch(
            'passport.backend.api.views.bundle.internal.controllers.PushRequest',
            self.fake_request,
        )
        self.request_patch.start()

        self.fake_recipient = mock.Mock()
        self.recipient_patch = mock.patch(
            'passport.backend.api.views.bundle.internal.controllers.PushRequestRecipient',
            self.fake_recipient,
        )
        self.recipient_patch.start()

    def tearDown(self):
        self.env.stop()
        self.recipient_patch.stop()
        self.request_patch.stop()
        self.base_request_patch.stop()

    def make_request(self, **data):
        return self.env.client.post(
            '/1/bundle/test/am_push_message/',
            query_string={'consumer': 'dev'},
            data=data,
        )

    def test_no_grants_error(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={}))

        resp = self.make_request()

        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_basic_fields__ok(self):
        resp = self.make_request(
            uid=TEST_UID,
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            title=TEST_TITLE,
        )
        self.assert_ok_response(resp)
        self.fake_request.assert_called_once_with(
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            title=TEST_TITLE,
            subtitle=None,
            body=None,
            recipients=mock.ANY,
            webview_url=None,
            require_web_auth=True,
            push_id=None,
        )
        self.fake_recipient.assert_called_once_with(
            uid=TEST_UID,
            required_am_capabilities=None,
            app_targeting_type=AppTargetingTypes.GLOBAL,
            custom_app_priority=None,
            required_platforms=None,
            device_ids=None,
        )

    def test_all_fields__ok(self):
        resp = self.make_request(
            uid=TEST_UID,
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            app_targeting_type='ONE_APP_PER_DEVICE',
            custom_app_priority='app1,app2',
            am_capabilities='cap1,cap2',
            required_platforms='android,ios',
            title=TEST_TITLE,
            body=TEST_BODY,
            subtitle=TEST_SUBTITLE,
            webview_url=TEST_WEBVIEW_URL,
            require_web_auth='0',
            push_id='some_push_id',
            device_ids='d1,d2',
        )
        self.assert_ok_response(resp)
        self.fake_request.assert_called_once_with(
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            title=TEST_TITLE,
            subtitle=TEST_SUBTITLE,
            body=TEST_BODY,
            recipients=mock.ANY,
            webview_url=TEST_WEBVIEW_URL,
            require_web_auth=False,
            push_id='some_push_id',
        )
        self.fake_recipient.assert_called_once_with(
            uid=TEST_UID,
            required_am_capabilities=['cap1', 'cap2'],
            app_targeting_type=AppTargetingTypes.ONE_APP_PER_DEVICE,
            custom_app_priority=['app1', 'app2'],
            required_platforms=[Platforms.android, Platforms.ios],
            device_ids=['d1', 'd2'],
        )
