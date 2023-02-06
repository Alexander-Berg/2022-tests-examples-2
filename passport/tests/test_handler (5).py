# -*- coding: utf-8 -*-
import json

from passport.backend.core.builders.push_api.faker import (
    FakePushApi,
    push_api_app_subscription_info,
)
from passport.backend.core.protobuf.challenge_pushes.challenge_pushes_pb2 import ChallengePushRequest
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.logbroker_client.challenge_pushes.handler import ChallengePushesHandler
from passport.backend.logbroker_client.core.test.native_client.protobuf_handler import BaseProtobufHandlerTestCase


TEST_APP1 = 'ru.yandex.test1'
TEST_APP2 = 'ru.yandex.test2'
TEST_APP3 = 'ru.yandex.test3'
TEST_BROWSER = 'ChromeMobile 48.0.2564 (Android Marshmallow)'
TEST_CLIENT_IP = '3.3.3.3'
TEST_DEVICE1 = 'ab123'
TEST_DEVICE2 = 'cd456'
TEST_EVENT_NAME = 'security'
TEST_LOCATION = u'Кривой Рог'
TEST_MAP_URL = 'https://static-maps.yandex.ru/1.x/?ll=-73.261810,41.147500&size=450,450&z=13&l=map&lang=ru_RU&pt=-73.261810,41.147500,pm2rdm'
TEST_MESSAGE_KEY = 'passport_push_security_message_key'
TEST_PUSH_TEXT = 'Посмотрите, когда и откуда. Если это не вы — срочно смените пароль, иначе ваши данные на Яндексе могут похитить.'
TEST_PUSH_TITLE = 'Кто-то вошёл в ваш аккаунт!'
TEST_SUBSCRIPTIONS_RATING = {
    'app': [TEST_APP1, TEST_APP2],
}
TEST_TIMESTAMP1 = 1606300318
TEST_TIMESTAMP2 = TEST_TIMESTAMP1 + 3600 * 24
TEST_TIMESTAMP3 = TEST_TIMESTAMP2 + 3600 * 24
TEST_TITLE_KEY = 'passport_push_security_title_key'


class _BaseTestChallengePushesHandler(BaseProtobufHandlerTestCase):
    HANDLER_CLASS = ChallengePushesHandler
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

    def setUp(self):
        super(_BaseTestChallengePushesHandler, self).setUp()
        self.fake_push_api = FakePushApi()
        self.fake_push_api.start()
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'push_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.fake_tvm.start()

    def tearDown(self):
        self.fake_tvm.stop()
        self.fake_push_api.stop()
        super(_BaseTestChallengePushesHandler, self).tearDown()

    def _make_handler(self, subscriptions_rating=None, **kwargs):
        if subscriptions_rating is None:
            subscriptions_rating = TEST_SUBSCRIPTIONS_RATING
        return ChallengePushesHandler(
            subscription_rating=subscriptions_rating,
            config=self.config,
            message_class=self.MESSAGE_CLASS,
            **kwargs
        )

    def _make_data(
        self, uid=TEST_UID, event_timestamp=TEST_TIMESTAMP1, event_name=TEST_EVENT_NAME,
        location=TEST_LOCATION, client_ip=TEST_CLIENT_IP, browser=TEST_BROWSER,
        map_url=TEST_MAP_URL, message_key=TEST_MESSAGE_KEY, title_key=TEST_TITLE_KEY,
        push_title=TEST_PUSH_TITLE, push_text=TEST_PUSH_TEXT,
    ):
        return ChallengePushRequest(
            push_message=ChallengePushRequest.PushMessage(
                uid=uid,
                event_timestamp=event_timestamp,
                event_name=event_name,
                location=location,
                client_ip=client_ip,
                browser=browser,
                map_url=map_url,
                message_key=message_key,
                title_key=title_key,
                push_title=push_title,
                push_text=push_text,
            ),
        ).SerializeToString()

    @staticmethod
    def _sub_info(id_, device, app, init_time):
        return push_api_app_subscription_info(
            id_=id_,
            device=device,
            app=app,
            init_time=init_time,
            last_sent=1607613458,
            uuid='aabbccddeeff112233445566',
            platform='fcm',
        )

    def _set_basic_sub_info(self):
        subscriptions = [
            self._sub_info('s1', TEST_DEVICE1, TEST_APP1, TEST_TIMESTAMP1),
        ]
        self.fake_push_api.set_response_value('list', json.dumps(subscriptions))

    def assert_push_sent(self, data, subscription_ids=None):
        requests = self.fake_push_api.get_requests_by_method('send')
        self.assertEqual(len(requests), 1)
        request = requests[0]
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
        request.assert_query_equals({
            'event': TEST_EVENT_NAME,
            'user': str(TEST_UID),
            'service': 'passport-push',
        })

    def assert_push_not_sent(self):
        self.assertEqual(len(self.fake_push_api.get_requests_by_method('send')), 0)
