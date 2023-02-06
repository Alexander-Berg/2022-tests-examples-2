# -*- coding: utf-8 -*-
import json

from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.builders.historydb_api import (
    HistoryDBApiInvalidResponseError,
    HistoryDBApiTemporaryError,
)
from passport.backend.core.builders.historydb_api.faker import last_letter_response
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import remove_none_values


TEST_COOKIE = 'Session_id=foo'
TEST_HOST = 'yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_CONSUMER_IP = '127.0.0.1'
TEST_UID = 1


SENDER_SERVICE_1 = dict(
    id=1,
    origin_prefixes=[],
    app_ids=[],
    slug='s1',
    external_list_ids=[10, 11],
)
SENDER_SERVICE_2 = dict(
    id=2,
    origin_prefixes=[],
    app_ids=[],
    slug='s2',
    external_list_ids=[20, 21],
)
SENDER_SERVICE_3 = dict(
    id=3,
    origin_prefixes=[],
    app_ids=[],
    slug='s3',
    external_list_ids=[30, 31],
)


class BaseMailSubscriptionsTestCase(BaseBundleTestViews):
    def setup_grants(self, suffix):
        self.env.grants.set_grants_return_value(
            {
                'dev': dict(
                    networks=[TEST_CONSUMER_IP],
                    grants={
                        'mail_subscriptions': [suffix],
                    },
                ),
            },
        )

    def setup_blackbox_response(self, mail_subscriptions=None):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                attributes=remove_none_values({
                    str(AT['account.unsubscribed_from_maillists']): mail_subscriptions,
                }),
            ),
        )


@with_settings_hosts(
    SENDER_MAIL_SUBSCRIPTION_SERVICES=[
        SENDER_SERVICE_1,
        SENDER_SERVICE_2,
        SENDER_SERVICE_3,
    ],
)
class TestGetMailSubscriptions(BaseMailSubscriptionsTestCase):
    default_url = '/1/bundle/account/mail_subscriptions/'
    http_method = 'GET'
    consumer = 'dev'
    http_headers = {
        'cookie': TEST_COOKIE,
        'host': TEST_HOST,
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        super(TestGetMailSubscriptions, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_grants('get')
        self.env.historydb_api.set_response_value(
            'last_letter',
            last_letter_response(
                uid=TEST_UID,
                list_id_to_ts={
                    10: 100500,
                    11: 100501,
                    20: 100502,
                },
            ),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestGetMailSubscriptions, self).tearDown()

    @parameterized.expand([
        (None, [True] * 3),
        ('all', [False] * 3),
        ('1,3', [False, True, False]),
        ('1,2,3', [False] * 3),
    ])
    def test_ok(self, attribute_value, is_subscribed_values):
        self.setup_blackbox_response(attribute_value)
        resp = self.make_request()

        expected_response = {
            'services': {
                '1': {
                    'is_subscribed': None,
                    'slug': 's1',
                    'email_sent_ts': 100501,
                },
                '2': {
                    'is_subscribed': None,
                    'slug': 's2',
                    'email_sent_ts': 100502,
                },
                '3': {
                    'is_subscribed': None,
                    'slug': 's3',
                    'email_sent_ts': 0,
                },
            },
        }
        for i, is_subscribed in enumerate(is_subscribed_values, start=1):
            expected_response['services'][str(i)]['is_subscribed'] = is_subscribed

        self.assert_ok_response(resp, **expected_response)

    @parameterized.expand([
        (HistoryDBApiTemporaryError, ),
        (HistoryDBApiInvalidResponseError, )
    ])
    def test_historydb_api_failed(self, error):
        self.env.historydb_api.set_response_side_effect('last_letter', error)
        self.setup_blackbox_response('all')
        resp = self.make_request()

        expected_response = {
            'services': {
                '1': {
                    'is_subscribed': False,
                    'slug': 's1',
                    'email_sent_ts': None,
                },
                '2': {
                    'is_subscribed': False,
                    'slug': 's2',
                    'email_sent_ts': None,
                },
                '3': {
                    'is_subscribed': False,
                    'slug': 's3',
                    'email_sent_ts': None,
                },
            },
        }
        self.assert_ok_response(resp, **expected_response)


@with_settings_hosts(
    SENDER_MAIL_SUBSCRIPTION_SERVICES=[
        SENDER_SERVICE_1,
        SENDER_SERVICE_2,
        SENDER_SERVICE_3,
    ],
)
class TestSetMailSubscriptions(BaseMailSubscriptionsTestCase):
    default_url = '/1/bundle/account/mail_subscriptions/'
    http_method = 'POST'
    consumer = 'dev'
    http_headers = {
        'cookie': TEST_COOKIE,
        'host': TEST_HOST,
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        super(TestSetMailSubscriptions, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_grants('set')

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestSetMailSubscriptions, self).tearDown()

    @parameterized.expand([
        (None, [True] * 3, None),
        (None, [False] * 3, 'all'),
        ('1,2', [False] * 3, 'all'),
        ('1,3', [True, False, True], '2'),
        ('1,2,3,4', [False] * 4, 'all'),
        ('1,4', [False] * 2, '1,2'),
        ('all', [True] * 3, None),
        ('1,2', [True] * 3, None),
        ('all', [True, False, True], '2'),
        ('all', [False] * 3, 'all'),
        (None, [True, False, True], '2'),
    ])
    def test_ok(self, attribute_value, input_data, expected_db_value):
        self.setup_blackbox_response(attribute_value)
        resp = self.make_request(
            query_args={
                'subscriptions_json': json.dumps(
                    {str(i): is_subscribed for i, is_subscribed in enumerate(input_data, start=1)},
                ),
            },
        )
        self.assert_ok_response(resp)

        if expected_db_value is None:
            # атрибут удаляется
            self.env.db.check_db_attr_missing(TEST_UID, 'account.unsubscribed_from_maillists')
        elif attribute_value == expected_db_value:
            # атрибут не меняется, поэтому в бд запись не происходит
            self.env.db.check_db_attr_missing(TEST_UID, 'account.unsubscribed_from_maillists')
        else:
            # атрибут меняется
            self.env.db.check_db_attr(TEST_UID, 'account.unsubscribed_from_maillists', expected_db_value)
