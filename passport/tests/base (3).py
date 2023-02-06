from functools import cmp_to_key
import json

from passport.backend.core.am_pushes.test.constants import (
    TEST_EVENT_NAME,
    TEST_PUSH_SERVICE,
    TEST_SUBSCRIPTIONS_RATING,
)
from passport.backend.core.am_pushes.test.mixin import AmPushesTestMixin
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.push_api.faker import FakePushApi
from passport.backend.core.logging_utils.faker.fake_tskv_logger import PushLoggerFaker
from passport.backend.core.protobuf.am_push_protocol.am_push_protocol_pb2 import PushMessageRequest
from passport.backend.core.protobuf.challenge_pushes.challenge_pushes_pb2 import ChallengePushRequest
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.logbroker_client.challenge_pushes.handler import ChallengePushesHandler
from passport.backend.logbroker_client.core.test.native_client.protobuf_handler import BaseProtobufHandlerTestCase
from passport.backend.utils.common import noneless_dict

from .constants import (
    TEST_PUSH_ID,
    TEST_TITLE1,
)


AppTargetingTypes = PushMessageRequest.PushMessageRecipient.AppTargetingType


class _BaseTestChallengePushesHandler(BaseProtobufHandlerTestCase, AmPushesTestMixin):
    MESSAGE_CLASS = 'passport.backend.core.protobuf.challenge_pushes.challenge_pushes_pb2.ChallengePushRequest'
    TOPIC = 'challenge-pushes'
    CONFIGS = [
        'base.yaml',
        'challenge-pushes/base.yaml',
        'challenge-pushes/testing.yaml',
        'logging.yaml',
        'export.yaml',
        'challenge-pushes/export.yaml',
    ]

    def build_patches(self):
        self.fake_push_api = FakePushApi()
        self.fake_push_api.set_response_value('send', 'OK')
        self._patches.append(self.fake_push_api)

        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
                '2': {
                    'alias': 'push_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._patches.append(self.fake_tvm)

        self.fake_blackbox = FakeBlackbox()
        self._patches.append(self.fake_blackbox)

        self.fake_push_log = PushLoggerFaker()
        self._patches.append(self.fake_push_log)
        self.setup_push_log_templates()

    def setup_push_log_templates(self):
        self.fake_push_log.bind_entry(
            'push',
            uid=str(TEST_UID),
            push_id=TEST_PUSH_ID,
            push_service=TEST_PUSH_SERVICE,
            push_event=TEST_EVENT_NAME,
            status='ok',
        )

    def _build_send_sync_result(self, subscription_ids, errors=None):
        errors = errors or {}
        return [
            {
                'code': errors.get(s, 200),
                'body': {
                    'error': 'MismatchSenderID',
                } if s in errors else {
                    'message_id': 'message-{}'.format(i),
                },
                'id': s,
            }
            for i, s in enumerate(subscription_ids, 1)
        ]

    def _set_send_sync_multiple_results(self, results):
        self.fake_push_api.set_response_side_effect('send', [
            json.dumps(data) for data in results
        ])

    def _set_send_sync_result(self, subscription_ids):
        self.fake_push_api.set_response_value('send', json.dumps(
            self._build_send_sync_result(subscription_ids),
        ))

    def _make_handler(self, **kwargs):
        return ChallengePushesHandler(
            subscription_rating=TEST_SUBSCRIPTIONS_RATING,
            config=self.config,
            message_class=self.MESSAGE_CLASS,
            **kwargs
        )

    def _make_recipient(
        self, uid=TEST_UID, app_targeting_type='GLOBAL',
        custom_app_priority=None, required_am_capabilities=None,
        required_platforms=None, require_trusted_device=False,
        device_ids=None, subscription_source=None, context=None,
    ):
        return PushMessageRequest.PushMessageRecipient(**noneless_dict(
            uid=uid,
            app_targeting_type=getattr(AppTargetingTypes, app_targeting_type),
            custom_app_priority=custom_app_priority,
            required_am_capabilities=required_am_capabilities,
            required_platforms=required_platforms,
            require_trusted_device=require_trusted_device,
            device_ids=device_ids,
            subscription_source=subscription_source,
            context=context,
        ))

    def _make_data(
        self, push_service=TEST_PUSH_SERVICE, event_name=TEST_EVENT_NAME,
        push_id=TEST_PUSH_ID, recipients=None, title=TEST_TITLE1, body=None, subtitle=None,
        webview_url=None, width_percents=None, height_percents=None, require_web_auth=None,
        context=None, expire_time=None, extra_data=None,
    ):
        if recipients is None:
            recipients = [self._make_recipient(context=context)]
        request = PushMessageRequest(
            push_service=push_service,
            event_name=event_name,
            push_id=push_id,
            recipients=recipients,
            text_body=PushMessageRequest.PushMessageTextBody(**noneless_dict(
                title=title,
                body=body,
                subtitle=subtitle,
            )),
            expire_time=expire_time,
            extra_json=json.dumps(extra_data) if extra_data else '',
        )
        webview_body = noneless_dict(
            webview_url=webview_url,
            width_percents=width_percents,
            height_percents=height_percents,
            require_web_auth=require_web_auth,
        )
        if webview_body:
            for k, v in webview_body.items():
                setattr(request.webview_body, k, v)
        return ChallengePushRequest(
            push_message_request=request,
        ).SerializeToString()

    def assert_push_sent(self, data, subscription_ids=None, offset=None, uid=TEST_UID):
        requests = self.fake_push_api.get_requests_by_method('send')
        if offset is None:
            self.assertEqual(len(requests), 1)
            offset = 0
        request = requests[offset]
        post_dict = json.loads(request.post_args)
        sub_info = post_dict.pop('subscriptions', None)
        if subscription_ids is not None:
            self.assertIsNotNone(sub_info)
            self.assertEqual(len(sub_info), 1)
            self.assertEqual(sorted(sub_info[0]['subscription_id']), sorted(subscription_ids))
        else:
            self.assertIsNone(sub_info)
        self.assertEqual(post_dict, data)
        request.assert_url_starts_with('https://push-sandbox.yandex.ru/v2/send')
        request.assert_query_equals(dict(
            event=data['payload']['event_name'],
            user=str(uid),
            service='passport-push',
        ))

    def assert_pushes_sent(self, pushes):
        requests = self.fake_push_api.get_requests_by_method('send')
        self.assertEqual(len(requests), len(pushes))
        for i, push in enumerate(pushes):
            self.assert_push_sent(**push, offset=i)

    def assert_push_not_sent(self):
        self.assertEqual(len(self.fake_push_api.get_requests_by_method('send')), 0)

    def build_logged_push(
        self,
        subscription_id=None,
        device_id=None,
        app_id=None,
        **kwargs,
    ):
        return self.fake_push_log.entry(
            'push',
            **noneless_dict(
                subscription_id=subscription_id,
                device_id=device_id,
                app_id=app_id,
                **kwargs
            ),
        )

    def build_test_logged_push(self):
        return self.build_logged_push(
            subscription_id='test1',
            app_id='',
        )

    def assert_pushes_logged(self, entries):
        self.fake_push_log.assert_has_written(entries)

    def assert_push_not_logged(self):
        self.assert_pushes_logged([])

    def assert_not_sent_push_logged(self, **kwargs):
        self.assert_pushes_logged([self.build_logged_push(
            subscription_id='n/a',
            status='not_sent',
            details='No subscriptions filtered',
            **kwargs
        )])

    def _set_basic_sub_info(self, with_test_subscription=False):
        subscriptions = [
            self._sub_info('s1'),
        ]
        if with_test_subscription:
            subscriptions.append(self._autotests_subscription_info('test1'))
        self.fake_push_api.set_response_value('list', json.dumps(subscriptions))


class IgnoreOrderListMatcher(list):
    def __add__(self, other):
        return IgnoreOrderListMatcher(list(self) + other)

    @staticmethod
    def _cmp(a, b):
        try:
            return (a > b) - (a < b)
        except TypeError as err:
            raise TypeError('{}: {} {}'.format(err, a, b))

    def _dict_friendly_cmp(self, a, b):
        if isinstance(a, dict) != isinstance(b, dict):
            return self._cmp(isinstance(a, dict), isinstance(b, dict))
        if isinstance(a, dict) and isinstance(b, dict):
            return self._cmp(sorted(a.items()), sorted(b.items()))
        return self._cmp(a, b)

    def _sort(self, list_value):
        return sorted(list_value, key=cmp_to_key(self._dict_friendly_cmp))

    def __eq__(self, other):
        if not isinstance(other, list):
            return False
        return self._sort(self) == self._sort(other)
