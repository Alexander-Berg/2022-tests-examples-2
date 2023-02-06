# -*- coding: utf-8 -*-
import mock
from nose_parameterized import parameterized
from passport.backend.core.am_pushes.common import Platforms
from passport.backend.core.am_pushes.push_request import (
    AppTargetingTypes,
    PushRequest,
    PushRequestRecipient,
)
from passport.backend.core.protobuf.am_push_protocol.am_push_protocol_pb2 import PushMessageRequest
from passport.backend.core.test.consts import (
    TEST_UID,
    TEST_UID1,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.utils.string import smart_bytes


TEST_PUSH_SERVICE = 'bug_notifications'
TEST_EVENT_NAME = 'new_bug_notification'
TEST_APP_ID1 = 'ru.yandex.mail'
TEST_APP_ID2 = 'ru.yandex.maps'
TEST_PUSH_TITLE = u'Вы выиграли приз'
TEST_PUSH_TITLE_BIN = smart_bytes(TEST_PUSH_TITLE)
TEST_PUSH_BODY = u'Ваш приз - прекрасный огромный кусок НИЧЕГО'
TEST_PUSH_BODY_BIN = smart_bytes(TEST_PUSH_BODY)
TEST_PUSH_SUBTITLE = u'Приходите и забирайте'
TEST_PUSH_SUBTITLE_BIN = smart_bytes(TEST_PUSH_SUBTITLE)
TEST_WEBVIEW_URL = 'https://yandex.ru/404'
TEST_WEBVIEW_URL_BIN = smart_bytes(TEST_WEBVIEW_URL)
TEST_PUSH_ID1 = '063e16fd-8670-49ac-87ad-0d157184b746'
TEST_PUSH_ID2 = 'a374610f-7a4e-4e5b-9281-50150919c61c'
TEST_CONTEXT = '{"TEST_CONTEXT": "TEST"}'


@with_settings_hosts(
    AM_CAPABILITIES_BY_VERSION_ANDROID={
        (1, 1): {'cap1'},
        (1, 2): {'cap2'},
    },
    AM_CAPABILITIES_BY_VERSION_IOS={
        (1, 3): {'cap1'},
        (1, 4): {'cap2'},
    },
)
class TestCreatePushRequestRecipient(PassportTestCase):
    def test_simple__ok(self):
        r = PushRequestRecipient(uid=TEST_UID)
        self.assertEqual(
            r.to_proto(),
            PushMessageRequest.PushMessageRecipient(
                uid=TEST_UID,
                app_targeting_type=AppTargetingTypes.GLOBAL,
                custom_app_priority=[],
            ),
        )

    def test_extended__ok(self):
        r = PushRequestRecipient(
            uid=TEST_UID,
            app_targeting_type=AppTargetingTypes.ONE_APP_PER_DEVICE,
            custom_app_priority=[TEST_APP_ID1, TEST_APP_ID2],
            required_am_capabilities=['cap1', 'cap2'],
            required_platforms=[Platforms.ios],
            require_trusted_device=True,
            context=TEST_CONTEXT,
        )
        self.assertEqual(
            r.to_proto(),
            PushMessageRequest.PushMessageRecipient(
                uid=TEST_UID,
                app_targeting_type=AppTargetingTypes.ONE_APP_PER_DEVICE,
                custom_app_priority=[TEST_APP_ID1, TEST_APP_ID2],
                required_am_capabilities=['cap1', 'cap2'],
                required_platforms=[Platforms.ios.value],
                require_trusted_device=True,
                context=TEST_CONTEXT,
            ),
        )

    @parameterized.expand([
        (
            dict(custom_app_priority=[TEST_APP_ID1]),
            r'other than ONE_APP_PER_DEVICE',
        ),
        (
            dict(required_am_capabilities=['cap1']),
            r'Cannot set required_am_capabilities',
        ),
        (
            dict(required_platforms=[Platforms.ios]),
            r'Cannot set required_platforms',
        ),
        (
            dict(
                app_targeting_type=AppTargetingTypes.ONE_APP_PER_DEVICE,
                required_am_capabilities=['cap1', 'cap3'],
            ),
            r'Capabilities not found: \[\'cap3\'\]',
        ),
        (
            dict(
                app_targeting_type=AppTargetingTypes.GLOBAL,
                require_trusted_device=True,
            ),
            r'Cannot set require_trusted_device',
        ),
    ])
    def test_invalid_args__exception(self, obj_args, exc_re):
        with self.assertRaisesRegexp(ValueError, exc_re):
            PushRequestRecipient(uid=TEST_UID, **obj_args)


class TestCreatePushRequest(PassportTestCase):
    def setUp(self):
        self._uuid_patch = mock.patch('uuid.uuid4', lambda: TEST_PUSH_ID1)
        self._uuid_patch.start()

    def tearDown(self):
        self._uuid_patch.stop()

    def _build_recipient(self, uid=TEST_UID, **kwargs):
        return PushRequestRecipient(uid=uid, **kwargs)

    def test_simple__ok(self):
        r = PushRequest(
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            recipients=self._build_recipient(),
            title=TEST_PUSH_TITLE,
        )
        proto = r.to_proto()
        self.assertEqual(
            proto,
            PushMessageRequest(
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT_NAME,
                recipients=[self._build_recipient().to_proto()],
                text_body=PushMessageRequest.PushMessageTextBody(
                    title=TEST_PUSH_TITLE_BIN,
                ),
                push_id=TEST_PUSH_ID1,
            )
        )
        self.assertFalse(proto.HasField('webview_body'))

    def test_extended__ok(self):
        r = PushRequest(
            push_service=TEST_PUSH_SERVICE,
            event_name=TEST_EVENT_NAME,
            recipients=[
                self._build_recipient(),
                self._build_recipient(TEST_UID1),
            ],
            title=TEST_PUSH_TITLE,
            body=TEST_PUSH_BODY,
            subtitle=TEST_PUSH_SUBTITLE,
            webview_url=TEST_WEBVIEW_URL,
            require_web_auth=False,
            push_id=TEST_PUSH_ID2,
            expire_time=123,
        )
        r.extra_data = {'a': 'b'}
        self.assertEqual(
            r.to_proto(),
            PushMessageRequest(
                push_service=TEST_PUSH_SERVICE,
                event_name=TEST_EVENT_NAME,
                recipients=[
                    self._build_recipient().to_proto(),
                    self._build_recipient(TEST_UID1).to_proto(),
                ],
                text_body=PushMessageRequest.PushMessageTextBody(
                    title=TEST_PUSH_TITLE_BIN,
                    body=TEST_PUSH_BODY_BIN,
                    subtitle=TEST_PUSH_SUBTITLE_BIN,
                ),
                webview_body=PushMessageRequest.PushMessageWebviewBody(
                    webview_url=TEST_WEBVIEW_URL,
                    require_web_auth=False,
                ),
                extra_json=b'{"a": "b"}',
                push_id=TEST_PUSH_ID2,
                expire_time=123,
            ),
        )


class TestParseProtobuf(PassportTestCase):
    @parameterized.expand([
        (
            {
                'push_service': TEST_PUSH_SERVICE,
                'event_name': TEST_EVENT_NAME,
                'title': TEST_PUSH_TITLE_BIN,
                'push_id': TEST_PUSH_ID1,
                'recipients': [
                    {
                        'uid': TEST_UID,
                        'app_targeting_type': AppTargetingTypes.ONE_APP_PER_DEVICE,
                    },
                    {
                        'uid': TEST_UID1,
                        'app_targeting_type': AppTargetingTypes.GLOBAL_WITH_CAPS,
                    },
                ],
            },
            {
                'push_service': TEST_PUSH_SERVICE,
                'event_name': TEST_EVENT_NAME,
                'title': TEST_PUSH_TITLE,
                'push_id': TEST_PUSH_ID1,
                'recipients': [
                    {
                        'uid': TEST_UID,
                        'app_targeting_type': AppTargetingTypes.ONE_APP_PER_DEVICE,
                    },
                    {
                        'uid': TEST_UID1,
                        'app_targeting_type': AppTargetingTypes.GLOBAL_WITH_CAPS,
                    },
                ],
            },
        ),
        (
            {
                'push_service': TEST_PUSH_SERVICE,
                'event_name': TEST_EVENT_NAME,
                'title': TEST_PUSH_TITLE_BIN,
                'body': TEST_PUSH_BODY_BIN,
                'subtitle': TEST_PUSH_SUBTITLE_BIN,
                'webview_url': TEST_WEBVIEW_URL_BIN,
                'require_web_auth': True,
                'extra_data': b'{"a": "b"}',
                'push_id': TEST_PUSH_ID2,
                'expire_time': 123,
                'recipients': [
                    {
                        'uid': TEST_UID,
                        'app_targeting_type': AppTargetingTypes.ONE_APP_PER_DEVICE,
                        'custom_app_priority': [TEST_APP_ID1, TEST_APP_ID2],
                    },
                    {
                        'uid': TEST_UID1,
                        'app_targeting_type': AppTargetingTypes.GLOBAL_WITH_CAPS,
                        'required_am_capabilities': ['cap1', 'cap2'],
                        'required_platforms': [Platforms.ios.value],
                    },
                ],
            },
            {
                'push_service': TEST_PUSH_SERVICE,
                'event_name': TEST_EVENT_NAME,
                'title': TEST_PUSH_TITLE,
                'body': TEST_PUSH_BODY,
                'subtitle': TEST_PUSH_SUBTITLE,
                'webview_url': TEST_WEBVIEW_URL,
                'require_web_auth': True,
                'extra_json': {'a': 'b'},
                'push_id': TEST_PUSH_ID2,
                'expire_time': 123,
                'recipients': [
                    {
                        'uid': TEST_UID,
                        'app_targeting_type': AppTargetingTypes.ONE_APP_PER_DEVICE,
                        'custom_app_priority': [TEST_APP_ID1, TEST_APP_ID2],
                        'context': TEST_CONTEXT,
                    },
                    {
                        'uid': TEST_UID1,
                        'app_targeting_type': AppTargetingTypes.GLOBAL_WITH_CAPS,
                        'required_am_capabilities': ['cap1', 'cap2'],
                        'required_platforms': [Platforms.ios],
                        'context': TEST_CONTEXT,
                    },
                ],
            },
        ),
    ])
    def test_ok(self, initial_data, expected_data):
        recipients_proto = [
            PushMessageRequest.PushMessageRecipient(
                uid=r['uid'],
                app_targeting_type=r['app_targeting_type'],
                custom_app_priority=r.get('custom_app_priority'),
                required_am_capabilities=r.get('required_am_capabilities'),
                required_platforms=r.get('required_platforms'),
            )
            for r in initial_data['recipients']
        ]

        kwargs = {}
        if 'webview_url' in initial_data:
            kwargs['webview_body'] = dict(
                webview_url=initial_data['webview_url'],
                require_web_auth=initial_data['require_web_auth'],
            )
        request_proto = PushMessageRequest(
            push_service=initial_data['push_service'],
            recipients=recipients_proto,
            text_body=PushMessageRequest.PushMessageTextBody(
                title=initial_data['title'],
                body=initial_data.get('body'),
                subtitle=initial_data.get('subtitle'),
            ),
            **kwargs
        )
        request = PushRequest.from_proto(request_proto)

        plain_attributes = [
            'push_service', 'title', 'body', 'subtitle', 'webview_url',
            'require_web_auth', 'extra_data',
        ]
        self.assertEqual(
            {attr: getattr(request, attr) for attr in plain_attributes},
            {key: expected_data.get(key) for key in plain_attributes},
        )

        plain_recipient_attributes = [
            'uid', 'app_targeting_type', 'custom_app_priority',
            'required_am_capabilities', 'required_platforms',
        ]
        self.assertEqual(
            [
                {attr: getattr(r, attr) for attr in plain_recipient_attributes}
                for r in request.recipients
            ],
            [
                {key: r.get(key) for key in plain_recipient_attributes}
                for r in expected_data['recipients']
            ],
        )
