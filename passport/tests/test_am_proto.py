import json
import random
import time
from typing import Optional

from nose_parameterized import parameterized
from passport.backend.api.settings.am_pushes.classes import (
    AllowRule,
    ForbidRule,
    PLATFORM_ANDROID,
    PLATFORM_IOS,
)
from passport.backend.core.am_pushes.common import Platforms
from passport.backend.core.am_pushes.push_request import SubscriptionSources
from passport.backend.core.am_pushes.test.constants import (
    TEST_APP1,
    TEST_APP2,
    TEST_APP3,
    TEST_APP4,
    TEST_DEVICE_ID1,
    TEST_DEVICE_ID2,
    TEST_DEVICE_ID3,
    TEST_EVENT_NAME,
    TEST_LOGIN_ID1,
    TEST_LOGIN_ID2,
    TEST_LOGIN_ID3,
    TEST_PUSH_SERVICE,
    TEST_TIMESTAMP1,
    TEST_TIMESTAMP2,
    TEST_TIMESTAMP3,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_oauth_tokens_response
from passport.backend.core.test.consts import (
    TEST_UID,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
    TEST_UID4,
)
from passport.backend.utils.common import noneless_dict

from .base import (
    _BaseTestChallengePushesHandler,
    IgnoreOrderListMatcher,
)
from .constants import (
    TEST_BODY1,
    TEST_PUSH_ID,
    TEST_SUBTITLE1,
    TEST_TITLE1,
    TEST_WEBVIEW_URL,
)


TEXT_FIELDS = ['body']
TEXT_FIELDS_ALL = ['body', 'subtitle']
WEBVIEW_FIELDS = ['webview_url', 'require_web_auth']

TEST_APS_DICT = {'content-available': 1}
TEST_REPACK_APNS_BASIC = IgnoreOrderListMatcher([
    {'e': 'event_name'}, 'passp_am_proto', 'push_service', 'event_name',
    'push_id', 'is_silent', 'uid', 'title',
])
TEST_REPACK_APNS_MIN_VERSION = [{'min_am_version': 'min_am_version_ios'}]
TEST_REPACK_APNS_WITH_TEXT = TEST_REPACK_APNS_BASIC + TEXT_FIELDS
TEST_REPACK_APNS_ALL_TEXT = TEST_REPACK_APNS_BASIC + TEXT_FIELDS_ALL
TEST_REPACK_APNS_WEBVIEW = TEST_REPACK_APNS_BASIC + WEBVIEW_FIELDS

TEST_REPACK_FCM_BASIC = IgnoreOrderListMatcher([
    'passp_am_proto', 'push_service', 'event_name', 'push_id', 'is_silent', 'uid', 'title',
])
TEST_REPACK_FCM_MIN_VERSION = [{'min_am_version': 'min_am_version_android'}]
TEST_REPACK_FCM_WITH_TEXT = TEST_REPACK_FCM_BASIC + TEXT_FIELDS
TEST_REPACK_FCM_ALL_TEXT = TEST_REPACK_FCM_BASIC + TEXT_FIELDS_ALL
TEST_REPACK_FCM_WEBVIEW = TEST_REPACK_FCM_BASIC + WEBVIEW_FIELDS

TEST_APNS_ALERT_BASIC = {'title': TEST_TITLE1}
TEST_APNS_ALERT_TEXT = {'title': TEST_TITLE1, 'body': TEST_BODY1}
TEST_APNS_ALERT_FULL = {'title': TEST_TITLE1, 'body': TEST_BODY1, 'subtitle': TEST_SUBTITLE1}
TEST_BLACKLISTED_PUSH_SERVICE = 'forbid_push_service'
TEST_BLACKLISTED_EVENT = 'forbid_event'


def send_details_body_ok(message_id, sub_id):
    return str(dict(code=200, body=dict(message_id=message_id), id=sub_id))


def send_details_body_fail(message_id, sub_id, code=205):
    return str(dict(code=code, body=dict(error='MismatchSenderID'), id=sub_id))


class _BaseTestChallengePushesProtocolHandler(_BaseTestChallengePushesHandler):
    EXTRA_EXPORTED_CONFIGS = dict(
        AM_CAPABILITIES_BY_VERSION_ANDROID={
            (1, 1): {'cap1', 'push:passport_protocol'},
            (1, 2): {'cap2'},
        },
        AM_CAPABILITIES_BY_VERSION_IOS={
            (1, 3): {'cap1', 'push:passport_protocol'},
            (1, 4): {'cap2'},
        },
        AM_SUBSCRIPTION_APP_RULES=[
            ForbidRule(platform='ios', app=TEST_APP2),
            ForbidRule(
                platform='ios',
                app=TEST_APP1,
                push_service=TEST_BLACKLISTED_PUSH_SERVICE,
                event=TEST_BLACKLISTED_EVENT,
            ),
        ],
        YAKEY_SUBSCRIPTION_APP_RULES=[
            AllowRule(platform=PLATFORM_ANDROID, app='ru.yandex.key'),
            AllowRule(platform=PLATFORM_IOS, app='ru.yandex.mobile.kluch'),
            # Всё, что не разрешено - запрещено
            ForbidRule(),
        ]
    )

    def setup_blackbox(self, has_trusted_xtokens=True):
        self.fake_blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(
                self.make_xtokens_bundle(has_trusted_xtokens),
            ),
        )

    def _build_sent_push(
        self, silent=False, uid=TEST_UID, min_am_version_android=None,
        min_am_version_ios=None, title=TEST_TITLE1, body=None, subtitle=None,
        webview_url=None, require_web_auth=None,
        repack_apns: list = TEST_REPACK_APNS_BASIC,
        apns_alert: Optional[dict] = TEST_APNS_ALERT_BASIC,
        repack_fcm: list = TEST_REPACK_FCM_BASIC,
        push_service=TEST_PUSH_SERVICE,
        event_name=TEST_EVENT_NAME,
        subsciption_ids=None,
        extra_data=None,
    ):
        payload = noneless_dict(
            passp_am_proto='1.0',
            push_id=TEST_PUSH_ID,
            is_silent=silent,
            uid=uid,
            min_am_version_android=min_am_version_android,
            min_am_version_ios=min_am_version_ios,
            title=title,
            body=body,
            subtitle=subtitle,
            webview_url=webview_url,
            require_web_auth=require_web_auth,
            push_service=push_service,
            event_name=event_name,
            **(extra_data or {})
        )
        aps = dict(TEST_APS_DICT)
        if apns_alert:
            aps.update(alert=apns_alert)
        push_data = dict(
            payload=payload,
            repack=dict(
                apns=noneless_dict(
                    aps=aps,
                    repack_payload=repack_apns,
                ),
                fcm=noneless_dict(
                    repack_payload=repack_fcm,
                ),
            ),
        )
        return dict(data=push_data, uid=uid, subscription_ids=subsciption_ids)

    def _build_subscription_log_args(self, subs, sub_id, message_id, error_code=None, **kwargs):
        subs_by_id = {sub['id']: sub for sub in subs}
        if error_code:
            details = send_details_body_fail(message_id, sub_id, code=error_code)
        else:
            details = send_details_body_ok(message_id, sub_id)
        res = dict(
            subscription_id=sub_id,
            device_id=subs_by_id[sub_id].get('device'),
            app_id=subs_by_id[sub_id].get('app'),
            details=details,
        )
        if error_code:
            res.update(status='error')
        res.update(kwargs)
        return res


class TestSendMessagesGlobalTarget(_BaseTestChallengePushesProtocolHandler):
    def test_send__simple__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(),
        )
        self.assert_push_sent(**self._build_sent_push())
        self.assert_list_not_called()
        self.assert_pushes_logged([self.build_logged_push(subscription_id='GLOBAL')])

    def test_send__with_context__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(context='{"CONTEXT": "TEST"}'),
        )
        self.assert_push_sent(**self._build_sent_push())
        self.assert_list_not_called()
        self.assert_pushes_logged([self.build_logged_push(
            subscription_id='GLOBAL',
            context='{"CONTEXT": "TEST"}',
        )])

    def test_send__expired_ttl__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(expire_time=int(time.time() - 1)),
        )
        self.assert_push_not_sent()
        self.assert_list_not_called()
        self.assert_pushes_logged([])

    def test_send__notification_text__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(
                body=TEST_BODY1,
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            body=TEST_BODY1,
            repack_apns=TEST_REPACK_APNS_WITH_TEXT,
            repack_fcm=TEST_REPACK_FCM_WITH_TEXT,
            apns_alert=TEST_APNS_ALERT_TEXT,
        ))
        self.assert_list_not_called()
        self.assert_pushes_logged([self.build_logged_push(subscription_id='GLOBAL')])

    def test_send__all_text_fields__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            body=TEST_BODY1,
            subtitle=TEST_SUBTITLE1,
            repack_apns=TEST_REPACK_APNS_ALL_TEXT,
            repack_fcm=TEST_REPACK_FCM_ALL_TEXT,
            apns_alert=TEST_APNS_ALERT_FULL,
        ))
        self.assert_list_not_called()
        self.assert_pushes_logged([self.build_logged_push(subscription_id='GLOBAL')])

    def test_send__webview__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(
                webview_url=TEST_WEBVIEW_URL,
                require_web_auth=False,
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            webview_url=TEST_WEBVIEW_URL,
            require_web_auth=False,
            repack_apns=TEST_REPACK_APNS_WEBVIEW,
            repack_fcm=TEST_REPACK_FCM_WEBVIEW,
        ))
        self.assert_list_not_called()
        self.assert_pushes_logged([self.build_logged_push(subscription_id='GLOBAL')])

    def test_send__multiple_recipients__ok(self):
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(),
                    self._make_recipient(uid=TEST_UID1),
                ],
            ),
        )
        self.assert_pushes_sent([
            self._build_sent_push(),
            self._build_sent_push(uid=TEST_UID1),
        ])
        self.assert_list_not_called()
        self.assert_pushes_logged([
            self.build_logged_push(subscription_id='GLOBAL'),
            self.build_logged_push(subscription_id='GLOBAL', uid=str(TEST_UID1)),
        ])


class TestSendMessagesGlobalWithCapsTarget(_BaseTestChallengePushesProtocolHandler):
    def test_send__simple__ok(self):
        self._set_basic_sub_info()
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(app_targeting_type='GLOBAL_WITH_CAPS'),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(subsciption_ids=['s1']))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()
        self.assert_pushes_logged([self.build_logged_push(
            subscription_id='s1',
            app_id=TEST_APP1,
            device_id=TEST_DEVICE_ID1,
        )])

    def test_send__disabled_test_subscriptions__ok(self):
        self._set_basic_sub_info(with_test_subscription=True)
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(app_targeting_type='GLOBAL_WITH_CAPS'),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(subsciption_ids=['s1']))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()
        self.assert_pushes_logged([self.build_logged_push(
            subscription_id='s1',
            device_id=TEST_DEVICE_ID1,
            app_id=TEST_APP1,
        )])

    def test_send__enabled_test_subscriptions__ok(self):
        self._set_basic_sub_info(with_test_subscription=True)
        self.process(
            self._make_handler(with_test_subscriptions=True),
            self._make_data(
                recipients=[
                    self._make_recipient(app_targeting_type='GLOBAL_WITH_CAPS'),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(subsciption_ids=['s1', 'test1']))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()
        self.assert_pushes_logged([
            self.build_logged_push(
                subscription_id='s1',
                device_id=TEST_DEVICE_ID1,
                app_id=TEST_APP1,
            ),
            self.build_test_logged_push(),
        ])

    def test_send__am_caps_filter__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        uid=TEST_UID,
                        app_targeting_type='GLOBAL_WITH_CAPS',
                        required_am_capabilities=['cap1'],
                    ),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            uid=TEST_UID,
            repack_apns=TEST_REPACK_APNS_BASIC + TEST_REPACK_APNS_MIN_VERSION,
            repack_fcm=TEST_REPACK_FCM_BASIC + TEST_REPACK_FCM_MIN_VERSION,
            min_am_version_android='1.1',
            min_am_version_ios='1.3',
            subsciption_ids=['s3', 's4', 's5', 's10', 's11'],
        ))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()

    def test_send__unknown_platform__not_send(self):
        subs = [self._sub_info(id_='s1', platform='unknown')]
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        uid=TEST_UID,
                        app_targeting_type='GLOBAL_WITH_CAPS',
                        required_am_capabilities=['cap1'],
                    ),
                ],
            ),
        )
        self.assert_push_not_sent()
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()
        self.assert_not_sent_push_logged()

    def test_send__platform_filter__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        uid=TEST_UID1,
                        app_targeting_type='GLOBAL_WITH_CAPS',
                        required_platforms=[Platforms.android.value],
                    ),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            uid=TEST_UID1,
            subsciption_ids=['s3', 's4', 's5'],
        ))
        self.assert_list_called([TEST_UID1])
        self.assert_blackbox_not_called()
        self.assert_pushes_logged([
            self.build_logged_push(
                subscription_id='s3',
                uid=str(TEST_UID1),
                device_id=TEST_DEVICE_ID1,
                app_id=TEST_APP2,
            ),
            self.build_logged_push(
                subscription_id='s4',
                uid=str(TEST_UID1),
                device_id=TEST_DEVICE_ID1,
                app_id=TEST_APP2,
            ),
            self.build_logged_push(
                subscription_id='s5',
                uid=str(TEST_UID1),
                device_id=TEST_DEVICE_ID2,
                app_id=TEST_APP1,
            ),
        ])

    def test_send__trusted_devices_filter__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox()
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        uid=TEST_UID1,
                        app_targeting_type='GLOBAL_WITH_CAPS',
                        require_trusted_device=True,
                    ),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            uid=TEST_UID1,
            subsciption_ids=['s5'],
        ))
        self.assert_list_called([TEST_UID1])
        self.assert_blackbox_called([TEST_UID1])
        self.assert_pushes_logged([self.build_logged_push(
            subscription_id='s5',
            uid=str(TEST_UID1),
            app_id=TEST_APP1,
            device_id=TEST_DEVICE_ID2,
        )])

    def test_send__no_trusted_devices_filter__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox(has_trusted_xtokens=False)
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        uid=TEST_UID1,
                        app_targeting_type='GLOBAL_WITH_CAPS',
                        require_trusted_device=True,
                    ),
                ],
            ),
        )
        self.assert_push_not_sent()
        self.assert_list_not_called()
        self.assert_blackbox_called([TEST_UID1])
        self.assert_not_sent_push_logged()

    def test_send__all_filters__ok(self):
        subs = self.make_subs_bundle()
        recipients = [
            self._make_recipient(
                uid=TEST_UID1,
                app_targeting_type='GLOBAL_WITH_CAPS',
                required_am_capabilities=['cap1'],
            ),
            self._make_recipient(
                uid=TEST_UID2,
                app_targeting_type='GLOBAL_WITH_CAPS',
                required_platforms=[Platforms.android.value],
            ),
            self._make_recipient(
                uid=TEST_UID3,
                app_targeting_type='GLOBAL_WITH_CAPS',
                require_trusted_device=True,
            ),
            self._make_recipient(
                uid=TEST_UID4,
                app_targeting_type='GLOBAL_WITH_CAPS',
                required_platforms=[Platforms.android.value],
                required_am_capabilities=['cap1', 'cap2'],
                require_trusted_device=True,
            )
        ]
        self.fake_push_api.set_response_side_effect(
            'list',
            [json.dumps(subs)] * len(recipients),
        )
        self.fake_blackbox.set_response_side_effect(
            'get_oauth_tokens',
            [
                blackbox_get_oauth_tokens_response(
                    self.make_xtokens_bundle(has_trusted_xtokens=True),
                ),
            ] * 2,
        )
        self.process(
            self._make_handler(),
            self._make_data(recipients=recipients),
        )
        self.assert_pushes_sent([
            self._build_sent_push(
                uid=TEST_UID1,
                min_am_version_android='1.1',
                min_am_version_ios='1.3',
                repack_apns=TEST_REPACK_APNS_BASIC + TEST_REPACK_APNS_MIN_VERSION,
                repack_fcm=TEST_REPACK_FCM_BASIC + TEST_REPACK_FCM_MIN_VERSION,
                subsciption_ids=['s3', 's4', 's5', 's10', 's11'],
            ),
            self._build_sent_push(
                uid=TEST_UID2,
                subsciption_ids=['s3', 's4', 's5'],
            ),
            self._build_sent_push(
                uid=TEST_UID3,
                subsciption_ids=['s5'],
            ),
            self._build_sent_push(
                uid=TEST_UID4,
                min_am_version_android='1.2',
                min_am_version_ios='1.4',
                repack_apns=TEST_REPACK_APNS_BASIC + TEST_REPACK_APNS_MIN_VERSION,
                repack_fcm=TEST_REPACK_FCM_BASIC + TEST_REPACK_FCM_MIN_VERSION,
                subsciption_ids=['s5'],
            ),
        ])
        self.assert_list_called([TEST_UID, TEST_UID2, TEST_UID3, TEST_UID4])
        self.assert_blackbox_called([TEST_UID3, TEST_UID4])


class TestSendMessagesOneAppPerDeviceTarget(_BaseTestChallengePushesProtocolHandler):
    def test_send__different_apps__best_app(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
        ]
        self._set_send_sync_result(['s2'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s2'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    @parameterized.expand([(False,), (True,)])
    def test_send__blacklisted_by_event_and_push_service(self, blacklisted):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP3, platform='apns'),
        ]
        expected_sub = ['s1']
        if not blacklisted:
            expected_sub.append('s2')
        self._set_send_sync_result(expected_sub)
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        data_kwargs = {}
        log_event_name=TEST_EVENT_NAME
        log_push_service=TEST_PUSH_SERVICE
        if blacklisted:
            data_kwargs.update(
                push_service=TEST_BLACKLISTED_PUSH_SERVICE,
                event_name=TEST_BLACKLISTED_EVENT,
            )
            log_event_name=TEST_BLACKLISTED_EVENT
            log_push_service=TEST_BLACKLISTED_PUSH_SERVICE
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        app_targeting_type='ONE_APP_PER_DEVICE',
                    ),
                ],
                **data_kwargs
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=expected_sub,
            **data_kwargs
        ))
        self.assert_pushes_logged([
            self.build_logged_push(
                push_event=log_event_name,
                push_service=log_push_service,
                **self._build_subscription_log_args(subs, sub_id, 'message-{}'.format(i)),
            ) for i, sub_id in enumerate(expected_sub, 1)
        ])
        self.assert_blackbox_not_called()

    def test_send__different_apps__custom_priority__best_app(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
        ]
        self._set_send_sync_result(['s3'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                    custom_app_priority=[TEST_APP3, TEST_APP1, TEST_APP2],
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s3'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    def test_send__similar_apps__best_ts(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP2),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
        ]
        self._set_send_sync_result(['s3'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s3'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    def test_send__similar_everything__first_element(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
        ]
        self._set_send_sync_result(['s1'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    def test_send__none_everything__first_element(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, None, None),
            _s('s2', TEST_DEVICE_ID1, None, None),
            _s('s3', TEST_DEVICE_ID1, None, None),
        ]
        self._set_send_sync_result(['s1'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    def test_send__unknown_apps__best_ts(self):
        _s = self._sub_info
        subs = [
            _s('s1', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP2),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP3),
        ]
        self._set_send_sync_result(['s3'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s3'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    @parameterized.expand((seed,) for seed in range(5))
    def test_send__multiple__determined_rating__ok(self, seed):
        _s = self._sub_info
        subs = [
            # Устройство 1: в приоритете TEST_APP1
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
            # Устройство 2: в приоритете TEST_TIMESTAMP3
            _s('s4', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP2),
            _s('s5', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP3),
            _s('s6', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1),
            # Устройство 3: в приоритете TEST_TIMESTAMP3
            _s('s7', TEST_DEVICE_ID3, TEST_APP3, TEST_TIMESTAMP2),
            _s('s8', TEST_DEVICE_ID3, TEST_APP4, TEST_TIMESTAMP3),
            _s('s9', TEST_DEVICE_ID3, TEST_APP3, TEST_TIMESTAMP1),
        ]
        random.Random(seed).shuffle(subs)
        self._set_send_sync_result(['s2', 's5', 's8'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s2', 's5', 's8'],
        ))
        self.assert_blackbox_not_called()

    def test_send__multiple__undetermined_rating__ok(self):
        _s = self._sub_info
        subs = [
            # Рейтинг одинаковый, выбирается первый элемент
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
        ]
        self._set_send_sync_result(['s1'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1', 'message-1'),
            ),
        )
        self.assert_blackbox_not_called()

    def test_send__multiple__require_trusted_devices__ok(self):
        _s = self._sub_info
        subs = [
            # Устройство 1
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP1, am_version='1.3'),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID1, am_version='1.3'),
            # Устройство 2
            _s('s3', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID2, am_version='1.3'),
            _s('s4', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID3, am_version='1.3'),
        ]
        self._set_send_sync_result(['s3'])
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox()

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                    require_trusted_device=True,
                ),
            ]),
        )
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s3'],
        ))
        self.assert_pushes_logged(
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3', 'message-1'),
            ),
        )
        self.assert_list_called([TEST_UID1])
        self.assert_blackbox_called([TEST_UID1])

    def test_send__multiple__no_trusted_devices__ok(self):
        _s = self._sub_info
        subs = [
            # Устройство 1
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID1),
            # Устройство 2
            _s('s3', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID2),
            _s('s4', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1, login_id=TEST_LOGIN_ID3),
        ]
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox(has_trusted_xtokens=False)

        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                    require_trusted_device=True
                ),
            ]),
        )
        self.assert_push_not_sent()
        self.assert_list_not_called()
        self.assert_not_sent_push_logged()
        self.assert_blackbox_called([TEST_UID1])


class TestSendMessagesOneAppPerDeviceTargetRetries(_BaseTestChallengePushesProtocolHandler):
    def _build_subs(self):
        _s = self._sub_info
        subs = [
            _s('s1-1', TEST_DEVICE_ID1, TEST_APP1),
            _s('s1-2', TEST_DEVICE_ID1, TEST_APP2),
            _s('s1-3', TEST_DEVICE_ID1, TEST_APP3),
            _s('s2-1', TEST_DEVICE_ID2, TEST_APP1),
            _s('s2-2', TEST_DEVICE_ID2, TEST_APP2),
            _s('s2-3', TEST_DEVICE_ID2, TEST_APP3),
            _s('s3-1', TEST_DEVICE_ID3, TEST_APP1),
            _s('s3-2', TEST_DEVICE_ID3, TEST_APP2),
            _s('s3-3', TEST_DEVICE_ID3, TEST_APP3),
        ]
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        return subs

    def _process(self):
        self.process(
            self._make_handler(),
            self._make_data(recipients=[
                self._make_recipient(
                    app_targeting_type='ONE_APP_PER_DEVICE',
                ),
            ]),
        )

    def test_all_success__ok(self):
        subs = self._build_subs()
        expected_subs = ['s1-1', 's2-1', 's3-1']
        self._set_send_sync_result(expected_subs)

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=expected_subs,
        ))
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, sub, 'message-{}'.format(i)),
            ) for i, sub in enumerate(expected_subs, 1)
        ])
        self.assert_blackbox_not_called()

    def test_single_constant_error__next_sub(self):
        subs = self._build_subs()
        self._set_send_sync_multiple_results([
            self._build_send_sync_result(['s1-1', 's2-1', 's3-1'], errors={'s1-1': 205}),
            self._build_send_sync_result(['s1-2']),
        ])

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1', 's2-1', 's3-1'],
        ), offset=0)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-2']
        ), offset=1)
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-1', 'message-2'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-1', 'message-3'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-2', 'message-1'),
            ),
        ])

    def test_single_temporary_error__retry(self):
        subs = self._build_subs()
        self._set_send_sync_multiple_results([
            self._build_send_sync_result(['s1-1', 's2-1', 's3-1'], errors={'s1-1': 500}),
            self._build_send_sync_result(['s1-1']),
        ])

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1', 's2-1', 's3-1'],
        ), offset=0)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1']
        ), offset=1)
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=500),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-1', 'message-2'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-1', 'message-3'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1'),
            ),
        ])

    def test_all_device_subscriptions_failed(self):
        subs = self._build_subs()
        self._set_send_sync_multiple_results([
            self._build_send_sync_result(['s1-1', 's2-1', 's3-1'], errors={'s1-1': 205}),
            self._build_send_sync_result(['s1-2'], errors={'s1-2': 205}),
            self._build_send_sync_result(['s1-3'], errors={'s1-3': 205}),
        ])

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1', 's2-1', 's3-1'],
        ), offset=0)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-2']
        ), offset=1)
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-1', 'message-2'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-1', 'message-3'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-2', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-3', 'message-1', error_code=205),
            ),
        ])

    def test_all_subscriptions_failed(self):
        subs = self._build_subs()
        self._set_send_sync_multiple_results([
            self._build_send_sync_result(['s1-1', 's2-1', 's3-1'], errors={'s1-1': 205, 's2-1': 205, 's3-1': 205}),
            self._build_send_sync_result(['s1-2', 's2-2', 's3-2'], errors={'s1-2': 205, 's2-2': 205, 's3-2': 205}),
            self._build_send_sync_result(['s1-3', 's2-3', 's3-3'], errors={'s1-3': 205, 's2-3': 205, 's3-3': 205}),
        ])

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1', 's2-1', 's3-1'],
        ), offset=0)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-2', 's2-2', 's3-2']
        ), offset=1)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-3', 's2-3', 's3-3']
        ), offset=2)
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-1', 'message-2', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-1', 'message-3', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-2', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-2', 'message-2', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-2', 'message-3', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-3', 'message-1', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-3', 'message-2', error_code=205),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-3', 'message-3', error_code=205),
            ),
        ])

    def test_multiple_temporary_errors__retries_limit_reached(self):

        subs = self._build_subs()
        self._set_send_sync_multiple_results([
            self._build_send_sync_result(['s1-1', 's2-1', 's3-1'], errors={'s1-1': 500}),
            self._build_send_sync_result(['s1-1'], errors={'s1-1': 500}),
            self._build_send_sync_result(['s1-1'], errors={'s1-1': 500}),
            self._build_send_sync_result(['s1-2']),
        ])

        self._process()
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1', 's2-1', 's3-1'],
        ), offset=0)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1']
        ), offset=1)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-1']
        ), offset=2)
        self.assert_push_sent(**self._build_sent_push(
            subsciption_ids=['s1-2']
        ), offset=3)
        self.assert_pushes_logged([
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=500),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's2-1', 'message-2'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's3-1', 'message-3'),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=500),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-1', 'message-1', error_code=500),
            ),
            self.build_logged_push(
                **self._build_subscription_log_args(subs, 's1-2', 'message-1'),
            ),
        ])


class TestSendMessagesClientDecidesTarget(_BaseTestChallengePushesProtocolHandler):
    def test_send__simple__ok(self):
        self._set_basic_sub_info()
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(app_targeting_type='CLIENT_DECIDES'),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            silent=True,
            apns_alert=None,
            subsciption_ids=['s1'],
        ))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()

    def test_send__trusted_devices__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox()
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        app_targeting_type='CLIENT_DECIDES',
                        require_trusted_device=True,
                    ),
                ],
            ),
        )
        self.assert_push_sent(**self._build_sent_push(
            silent=True,
            apns_alert=None,
            subsciption_ids=['s5'],
        ))
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_called([TEST_UID])

    def test_send__no_trusted_devices__ok(self):
        subs = self.make_subs_bundle()
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.setup_blackbox(has_trusted_xtokens=False)
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=[
                    self._make_recipient(
                        app_targeting_type='CLIENT_DECIDES',
                        require_trusted_device=True,
                    ),
                ],
            ),
        )
        self.assert_push_not_sent()
        self.assert_list_not_called()
        self.assert_blackbox_called([TEST_UID])

    def test_send__filtered_complex__ok(self):
        recipients = [
            self._make_recipient(
                uid=TEST_UID1,
                app_targeting_type='CLIENT_DECIDES',
                required_am_capabilities=['cap1'],
            ),
            self._make_recipient(
                uid=TEST_UID2,
                app_targeting_type='CLIENT_DECIDES',
                required_platforms=[Platforms.android.value],
            ),
            self._make_recipient(
                uid=TEST_UID3,
                app_targeting_type='CLIENT_DECIDES',
                require_trusted_device=True,
            ),
            self._make_recipient(
                uid=TEST_UID4,
                app_targeting_type='CLIENT_DECIDES',
                required_platforms=[Platforms.android.value],
                required_am_capabilities=['cap1', 'cap2'],
                require_trusted_device=True,
            ),
        ]
        _s = self._sub_info
        subs = [
            _s('s1', am_version=None, platform='fcm'),
            _s('s2', am_version='1.0', platform='fcm', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s3', am_version='1.1', platform='fcm', login_id=TEST_LOGIN_ID2, device=TEST_DEVICE_ID2),
            _s('s4', am_version='1.2', platform='fcm', login_id=TEST_LOGIN_ID3, device=TEST_DEVICE_ID3),
            _s('s5', am_version='1.3', platform='fcm', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s6', am_version=None, platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s7', am_version='1.0', platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s8', am_version='1.1', platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s9', am_version='1.2', platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s10', am_version='1.3', platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
            _s('s11', am_version='1.4', platform='apns', login_id=TEST_LOGIN_ID1, device=TEST_DEVICE_ID1),
        ]
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.fake_blackbox.set_response_side_effect(
            'get_oauth_tokens',
            [
                blackbox_get_oauth_tokens_response(
                    self.make_xtokens_bundle(has_trusted_xtokens=True),
                ),
            ] * 2,
        )
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=recipients, body=TEST_BODY1, subtitle=TEST_SUBTITLE1,
            ),
        )
        self.assert_pushes_sent([
            self._build_sent_push(
                uid=TEST_UID1,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                min_am_version_android='1.1',
                min_am_version_ios='1.3',
                repack_apns=TEST_REPACK_APNS_ALL_TEXT + TEST_REPACK_APNS_MIN_VERSION,
                repack_fcm=TEST_REPACK_FCM_ALL_TEXT + TEST_REPACK_FCM_MIN_VERSION,
                silent=True,
                apns_alert=None,
                subsciption_ids=['s3', 's4', 's5', 's10', 's11'],
            ),
            self._build_sent_push(
                uid=TEST_UID2,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                repack_apns=TEST_REPACK_APNS_ALL_TEXT,
                repack_fcm=TEST_REPACK_FCM_ALL_TEXT,
                silent=True,
                apns_alert=None,
                subsciption_ids=['s3', 's4', 's5'],
            ),
            self._build_sent_push(
                uid=TEST_UID3,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                repack_apns=TEST_REPACK_APNS_ALL_TEXT,
                repack_fcm=TEST_REPACK_FCM_ALL_TEXT,
                silent=True,
                apns_alert=None,
                subsciption_ids=['s3', 's4'],
            ),
            self._build_sent_push(
                uid=TEST_UID4,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                min_am_version_android='1.2',
                min_am_version_ios='1.4',
                repack_apns=TEST_REPACK_APNS_ALL_TEXT + TEST_REPACK_APNS_MIN_VERSION,
                repack_fcm=TEST_REPACK_FCM_ALL_TEXT + TEST_REPACK_FCM_MIN_VERSION,
                silent=True,
                apns_alert=None,
                subsciption_ids=['s4'],
            ),
        ])
        self.assert_list_called([TEST_UID, TEST_UID2, TEST_UID3, TEST_UID4])
        self.assert_blackbox_called([TEST_UID3, TEST_UID4])

    def test_send__yakey__ok(self):
        recipients = [
            self._make_recipient(
                uid=TEST_UID1,
                app_targeting_type='CLIENT_DECIDES',
                device_ids=[TEST_DEVICE_ID1, TEST_DEVICE_ID2],
                subscription_source=SubscriptionSources.YAKEY,
            ),
        ]
        _s = self._sub_info
        subs = [
            _s('s1', app='ru.yandex.key', platform='fcm', device=TEST_DEVICE_ID1),
            _s('s2', app='ru.yandex.mobile.kluch', platform='apns', device=TEST_DEVICE_ID2),
            _s('s3', app='ru.yandex.key', platform='fcm', device=TEST_DEVICE_ID3),  # не тот device
            _s('s4', app='smth', platform='apns', device=TEST_DEVICE_ID1),  # не тот app
            _s('s5', app='ru.yandex.key', platform='apns', device=TEST_DEVICE_ID1),  # неверное сочетание app и platform
        ]
        self.fake_push_api.set_response_value('list', json.dumps(subs))
        self.process(
            self._make_handler(),
            self._make_data(
                recipients=recipients,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                extra_data={'track_id': 'track-id'},
            ),
        )
        self.assert_pushes_sent([
            self._build_sent_push(
                uid=TEST_UID1,
                body=TEST_BODY1,
                subtitle=TEST_SUBTITLE1,
                repack_apns=TEST_REPACK_APNS_ALL_TEXT + ['track_id'],
                repack_fcm=TEST_REPACK_FCM_ALL_TEXT + ['track_id'],
                silent=True,
                apns_alert=None,
                subsciption_ids=['s1', 's2'],
                extra_data={'track_id': 'track-id'},
            ),
        ])
        self.assert_list_called([TEST_UID1])
        self.assert_blackbox_not_called()
