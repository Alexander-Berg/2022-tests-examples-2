import mock
from passport.backend.core.builders.push_api.faker import push_api_subscription_info
from passport.backend.core.test.test_utils import PassportTestCase


class TestFakePushApiResponses(PassportTestCase):
    def test_push_api_subscription_info__main_args(self):
        self.assertEqual(
            push_api_subscription_info(id_='mob:aabbccddeeff'),
            {
                'id': 'mob:aabbccddeeff',
                'app': '',
                'client': mock.ANY,
                'session': mock.ANY,
                'ttl': mock.ANY,
                'device': '',
                'platform': '',
                'filter': '',
                'uuid': '',
                'extra': '',
            },
        )

    def test_push_api_subscription_info__optional_args(self):
        self.assertEqual(
            push_api_subscription_info(
                id_='mob:aabbccddeeff',
                app='some_app',
                device='device_1234567',
                platform='fcm',
                uuid='f8be6dc6-1425-4cf8-9e72-4913d48f93de',
                extra='abcdef',
                some_field='some_value',
            ),
            {
                'id': 'mob:aabbccddeeff',
                'app': 'some_app',
                'client': mock.ANY,
                'session': mock.ANY,
                'ttl': mock.ANY,
                'device': 'device_1234567',
                'platform': 'fcm',
                'filter': '',
                'uuid': 'f8be6dc6-1425-4cf8-9e72-4913d48f93de',
                'extra': 'abcdef',
                'some_field': 'some_value',
            },
        )
