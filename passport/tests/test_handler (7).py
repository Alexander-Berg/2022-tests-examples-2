# -*- coding: utf-8 -*-
from functools import partial
import itertools
import json
import unittest

import mock
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.sender_api.exceptions import SenderApiTemporaryError
from passport.backend.core.builders.sender_api.faker.sender_api import (
    FakeSenderApi,
    sender_api_reply_ok,
)
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.test.consts import (
    TEST_EMAIL1,
    TEST_EMAIL2,
    TEST_UID,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.mail_unsubscriptions.events import (
    EmailConfirmedAddEvent,
    Sid2ChangeEvent,
    UnsubscribedFromMaillistsAttributeChangeEvent,
)
from passport.backend.logbroker_client.mail_unsubscriptions.handler import (
    MailUnsubscriptionsHandler,
    ServiceHandlerException,
)
from passport.backend.utils.logging_mock import (
    LoggingMock,
    LogMock,
)


HEADER = {
    'sourceid': 'base64:tTOfUD6sTFy9l4a_mIq8WQ',
    'seqno': '509549082',
    'topic': 'rt3.iva--historydb--raw',
    'path': '/var/log/yandex/passport-api/statbox/statbox.log',
    'servier': 'pass-dd-i84.sezam.yandex.net',
    'partition': '7',
    'offset': '535729'
}

TEST_UNIXTIME = 139883646

GOOD_EVENTS_DATA = (
    'tskv\tentity=account.emails\tunixtime={unixtime}\tuid=123\toperation=added\tconfirmed_at=2020-01-04\temail_id=2\tsome_data=aaa\n'
    'tskv\tentity=subscriptions\tunixtime={unixtime}\tuid=456\toperation=removed\tsid=2\tsome_data=кириллицааааа\n'
    'tskv\tentity=account.unsubscribed_from_maillists\tunixtime={unixtime}\tuid=789\toperation=updated\tsome_data=ccc\n'
).format(unixtime=TEST_UNIXTIME).encode()

WRONG_EVENTS_DATA = 'tskv\tentity=other\tunixtime={}\tuid=123\toperation=added\tsome_data=ффф\n'.format(TEST_UNIXTIME).encode()

TEST_ALIAS = 'alias1'
TEST_NATIVE_ALIAS_EMAIL1 = 'alias1@yandex.ru'
TEST_NATIVE_ALIAS_EMAIL2 = 'alias1@ya.ru'
TEST_NATIVE_OTHER_EMAIL1 = TEST_EMAIL1
TEST_NATIVE_OTHER_EMAIL2 = TEST_EMAIL2
TEST_NATIVE_OTHER_EMAIL3 = 'benny@jihad.net'
TEST_EXT_EMAIL_ID1 = 333
TEST_EXT_EMAIL1 = 'test3@test.com'
TEST_EXT_EMAIL_ID2 = 444
TEST_EXT_EMAIL2 = 'test4@test.com'
TEST_EXT_EMAIL_ID3 = 555
TEST_EXT_EMAIL3 = 'test5@test2.com'

TEST_SUBSCRIPTION_SERVICES = [
    # Почта
    dict(
        id=1,
        origin_prefixes=['mail_origin1', 'mail_origin2'],
        app_ids=['ru.yandex.mail', 'ru.yandex.mail2'],
        slug='mail',
        external_list_ids=[10, 11],
    ),
    # Карты
    dict(
        id=2,
        origin_prefixes=['maps_origin1', 'maps_origin2'],
        app_ids=['ru.yandex.maps', 'ru.yandex.maps2'],
        slug='maps',
        external_list_ids=[20, 21],
    ),
    # Маркет
    dict(
        id=3,
        origin_prefixes=['market_origin1', 'market_origin2'],
        app_ids=['ru.yandex.market', 'ru.yandex.market2'],
        slug='market',
        external_list_ids=[30, 31],
    ),
]


DEFAULT_SETTINGS = dict(
    SENDER_MAIL_SUBSCRIPTION_SERVICES=TEST_SUBSCRIPTION_SERVICES,
    BLACKBOX_URL='http://test',
    SENDER_API_TIMEOUT=1,
    SENDER_API_RETRIES=2,
    SENDER_API_URL='http://test',
    SENDER_API_UNSUBSCRIBE_EXT_ACCOUNT='test',
    NATIVE_EMAIL_DOMAINS=['yandex.ru', 'ya.ru'],
)

NON_PORTAL_ALIASES = ['lite', 'pdd', 'neophonish', 'phonish']


def merge_parameters(*parameter_iter):
    return list(itertools.product(*parameter_iter))


class _BaseTestMailUnsubscriptionsHandler(unittest.TestCase):
    maxDiff = 2000

    def setUp(self):
        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                'mail_unsubscriptions/base.yaml',
                'mail_unsubscriptions/testing.yaml',
                'logging.yaml',
                'mail_unsubscriptions/export.yaml',
            ],
        )
        self.config.set_as_passport_settings()
        self.handler = MailUnsubscriptionsHandler(self.config)
        self._patches = []
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {'alias': 'blackbox', 'ticket': TEST_TICKET},
                    '2': {'alias': 'sender_api', 'ticket': TEST_TICKET},
                },
            ),
        )
        self._patches.append(self.fake_tvm_credentials_manager)

        self.blackbox = FakeBlackbox()
        self._patches.append(self.blackbox)

        self.sender = FakeSenderApi()
        self._patches.append(self.sender)

        self.handler_logger = LogMock()
        self._patches.append(
            mock.patch(
                'passport.backend.logbroker_client.mail_unsubscriptions.handler.log',
                self.handler_logger,
            ),
        )

        for patch in self._patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()

    def setup_blackbox_account_response(
        self, uid=TEST_UID, portal_alias=TEST_ALIAS, unsubscribed_attr='1,2',
        emails=None, native_emails=None, alias_type='portal', subscribed_to_sid2=True,
        **kwargs
    ):
        if native_emails is None:
            native_emails = [
                dict(email=TEST_NATIVE_OTHER_EMAIL1, confirmed=True),
                dict(email=TEST_NATIVE_OTHER_EMAIL2, confirmed=True),
                dict(email=TEST_NATIVE_OTHER_EMAIL3, confirmed=True),
            ]
        if emails is None:
            emails = [
                dict(id=TEST_EXT_EMAIL_ID1, email=TEST_EXT_EMAIL1, confirmed=True),
                dict(id=TEST_EXT_EMAIL_ID2, email=TEST_EXT_EMAIL2, confirmed=True),
                dict(id=TEST_EXT_EMAIL_ID3, email=TEST_EXT_EMAIL3, confirmed=False),
            ]
        blackbox_emails = [
            dict(
                address=email['email'],
                native=True,
                validated=email['confirmed'],
            )
            for email in native_emails
        ]
        blackbox_email_attributes = [
            dict(
                id=email['id'],
                attributes={
                    1: email['email'],
                    3: email['confirmed'],
                },
            )
            for email in emails
        ]
        aliases = {alias_type: portal_alias}
        attributes = {
            'account.unsubscribed_from_maillists': unsubscribed_attr,
        }
        subscribed_to = []
        if subscribed_to_sid2:
            subscribed_to.append(2)
        self.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                emails=blackbox_emails,
                email_attributes=blackbox_email_attributes,
                aliases=aliases,
                attributes=attributes,
                subscribed_to=subscribed_to,
                **kwargs
            ),
        )

    def setup_sender_set_effects(self, *responses):
        if responses:
            self.sender.set_response_side_effect('set_unsubscriptions', responses)
        else:
            self.sender.set_response_value('set_unsubscriptions', sender_api_reply_ok())

    def setup_sender_copy_effects(self, *responses):
        if responses:
            self.sender.set_response_side_effect('copy_unsubscriptions', responses)
        else:
            self.sender.set_response_value('copy_unsubscriptions', sender_api_reply_ok())

    def get_event(self, entity, operation='added', uid=TEST_UID, **kwargs):
        data = dict(
            entity=entity,
            operation=operation,
            uid=uid,
            unixtime=TEST_UNIXTIME,
            **kwargs
        )
        body = '\t'.join('{}={}'.format(k, v) for k, v in data.items())
        return 'tskv\t{}\n'.format(body).encode()

    def assert_sender_not_called(self):
        self.assertEqual(len(self.sender.requests), 0)

    def assert_sender_copy_not_called(self):
        self.assertEqual(len(self.sender.get_requests_by_method('copy_unsubscriptions')), 0)

    def assert_sender_set_not_called(self):
        self.assertEqual(len(self.sender.get_requests_by_method('set_unsubscriptions')), 0)

    def assert_blackbox_not_called(self):
        self.assertEqual(len(self.blackbox.requests), 0)

    def assert_blackbox_userinfo_called(self, uid=TEST_UID, attributes=None, with_sid2=False, dbfields=None, **args):
        if attributes is None:
            attributes = ['account.unsubscribed_from_maillists']
        requests = self.blackbox.get_requests_by_method('userinfo')
        self.assertEqual(len(requests), 1)
        expected_args = {}
        if dbfields is None:
            dbfields = []
        if with_sid2:
            dbfields.extend([
                'subscription.suid.2',
                'subscription.login_rule.2',
                'subscription.login.2',
                'subscription.host_id.2',
            ])
        if dbfields:
            expected_args['dbfields'] = ','.join(dbfields)
        expected_args.update(args)
        requests[0].assert_post_data_contains(
            dict(
                method='userinfo',
                uid=uid,
                emails='getall',
                **expected_args
            ),
        )
        requests[0].assert_contains_attributes(attributes)

    def sender_set_call(self, email, subscribe_list, unsubscribe_list):
        state = [
            {'list_id': list_id, 'unsubscribed': True} for
            list_id in unsubscribe_list
        ] + [
            {'list_id': list_id, 'unsubscribed': False} for
            list_id in subscribe_list
        ]
        return dict(state=state, email=email)

    @staticmethod
    def _dict_friendly_sort(value):
        return json.dumps(value) if isinstance(value, dict) else value

    def assert_calls_equal(self, real_calls, expected_calls, formatter):
        self.assertEqual(
            sorted(real_calls, key=self._dict_friendly_sort),
            sorted(expected_calls, key=self._dict_friendly_sort),
            '\nReal:\n{}\n\nExpected:\n{}'.format(
                '\n'.join(formatter(call) for call in real_calls),
                '\n'.join(formatter(call) for call in expected_calls),
            ),
        )

    @staticmethod
    def _format_set_call(call):
        return '{}: s: {}; u: {}'.format(
            call['email'],
            ', '.join(str(l['list_id']) for l in call['state'] if not l['unsubscribed']),
            ', '.join(str(l['list_id']) for l in call['state'] if l['unsubscribed']),
        )

    def assert_sender_set_called(self, expected_calls):
        real_calls = []
        for request in self.sender.get_requests_by_method('set_unsubscriptions'):
            email = request.get_query_params()['email'][0]
            state = json.loads(request.post_args['state'])
            subscribe_list = []
            unsubscribe_list = []
            for rec in state:
                if rec['unsubscribed']:
                    unsubscribe_list.append(rec['list_id'])
                else:
                    subscribe_list.append(rec['list_id'])
            real_calls.append(
                self.sender_set_call(
                    email=email,
                    subscribe_list=subscribe_list,
                    unsubscribe_list=unsubscribe_list,
                ),
            )
        self.assert_calls_equal(real_calls, expected_calls, self._format_set_call)

    @staticmethod
    def _format_copy_call(call):
        return 'src: {} dst: {}'.format(call['email_src'], call['email_dst'])

    def sender_copy_call(self, email_src, email_dst):
        return dict(email_src=email_src, email_dst=email_dst)

    def assert_sender_copy_called(self, expected_calls):
        real_calls = []
        for request in self.sender.get_requests_by_method('copy_unsubscriptions'):
            query = request.get_query_params()
            real_calls.append(
                self.sender_copy_call(
                    email_src=query['src'][0],
                    email_dst=query['dst'][0],
                ),
            )
        self.assert_calls_equal(real_calls, expected_calls, self._format_copy_call)

    def assert_last_log_re(self, pattern):
        entry = self.handler_logger.entries[-1]
        record = entry[0]
        self.assertRegexpMatches(record, pattern)


class TestMailUnsubscriptionsHandlerMain(_BaseTestMailUnsubscriptionsHandler):
    def test_log_and_push_metrics(self):
        handler = MailUnsubscriptionsHandler(
            self.config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )
        handler._process_event = lambda *_, **__: None

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                handler.process(HEADER, GOOD_EVENTS_DATA)

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:10306/xpush',
            method='POST',
            post_args=json.dumps(
                {
                    'mail_unsubscriptions.entries._.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 3,
                    },
                    'mail_unsubscriptions.entries.total.var/log/yandex/passport-api/statbox/statbox.log_dmmm': {
                        'value': 3,
                    },
                },
                sort_keys=True,
            ),
        )

        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '/var/log/yandex/passport-api/statbox/statbox.log',
                    'handler_name': 'mail_unsubscriptions',
                    'metric:mail_unsubscriptions.entries._.var/log/yandex/passport-api/statbox/statbox.log': 3,
                    'metric:mail_unsubscriptions.entries.total.var/log/yandex/passport-api/statbox/statbox.log': 3,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_no_events(self):
        self.handler.process(HEADER, WRONG_EVENTS_DATA)
        self.assert_sender_not_called()
        self.assert_blackbox_not_called()


@with_settings_hosts(**DEFAULT_SETTINGS)
class TestAttrUnsubscribedFromMaillistsChange(_BaseTestMailUnsubscriptionsHandler):
    ENTITY = 'account.unsubscribed_from_maillists'
    OPERATIONS = ['added', 'updated', 'created']

    OPERATION_PARAMETERS = merge_parameters(OPERATIONS)
    OPERATION_AND_NON_PORTAL_ALIAS_PARAMETERS = merge_parameters(
        OPERATIONS,
        NON_PORTAL_ALIASES,
    )

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_account_not_found__no_actions(self, operation):
        self.setup_blackbox_account_response(uid=None)
        event = self.get_event(self.ENTITY, operation=operation)
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Uid .+ not found')

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_usual_account__ok(self, operation):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_called([
            self.sender_set_call(email, [30, 31], [10, 11, 20, 21])
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3, TEST_NATIVE_ALIAS_EMAIL1]
        ])
        self.assert_sender_copy_called([
            self.sender_copy_call(TEST_NATIVE_ALIAS_EMAIL1, TEST_EXT_EMAIL1),
            self.sender_copy_call(TEST_NATIVE_ALIAS_EMAIL1, TEST_EXT_EMAIL2),
        ])

    def test_usual_account__dry_run__ok(self):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation='added')

        self.handler.dry_run = True
        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_not_called()
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_usual_account__unsubscribe_only__ok(self, operation):
        self.setup_blackbox_account_response(unsubscribed_attr='all')
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_called([
            self.sender_set_call(email, [], [10, 11, 20, 21, 30, 31])
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3, TEST_NATIVE_ALIAS_EMAIL1]
        ])
        self.assert_sender_copy_called([
            self.sender_copy_call(TEST_NATIVE_ALIAS_EMAIL1, TEST_EXT_EMAIL1),
            self.sender_copy_call(TEST_NATIVE_ALIAS_EMAIL1, TEST_EXT_EMAIL2),
        ])

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_usual_account__subscribe_only__ok(self, operation):
        self.setup_blackbox_account_response(unsubscribed_attr='')
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_called([
            self.sender_set_call(email, [10, 11, 20, 21, 30, 31], [])
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3, TEST_NATIVE_ALIAS_EMAIL1]
        ])
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_AND_NON_PORTAL_ALIAS_PARAMETERS)
    def test_non_portal_account__ok(self, operation, alias_type):
        self.setup_blackbox_account_response(alias_type=alias_type)
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_called([
            self.sender_set_call(email, [30, 31], [10, 11, 20, 21])
            for email in
            [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3]
        ])
        self.assert_sender_copy_called([
            self.sender_copy_call(TEST_NATIVE_OTHER_EMAIL3, TEST_EXT_EMAIL1),
            self.sender_copy_call(TEST_NATIVE_OTHER_EMAIL3, TEST_EXT_EMAIL2),
        ])

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_no_native_emails__no_actions(self, operation):
        self.setup_blackbox_account_response(alias_type='pdd', native_emails=[])
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_not_called()
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_no_emails__no_actions(self, operation):
        self.setup_blackbox_account_response(alias_type='pdd', native_emails=[], emails=[])
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_set_not_called()
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_blackbox_error__handler_exception(self, operation):
        self.blackbox.set_response_side_effect('userinfo', BlackboxTemporaryError('err123'))
        event = self.get_event(self.ENTITY, operation=operation)
        with self.assertRaisesRegexp(ServiceHandlerException, 'err123'):
            self.handler.process(HEADER, event)

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_sender_set_error__handler_exception(self, operation):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects(
            *([SenderApiTemporaryError('err456')] * 10)
        )
        self.setup_sender_copy_effects()
        event = self.get_event(self.ENTITY, operation=operation)
        with self.assertRaisesRegexp(ServiceHandlerException, 'err456'):
            self.handler.process(HEADER, event)

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_sender_copy_error__handler_exception(self, operation):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects()
        self.setup_sender_copy_effects(
            *([SenderApiTemporaryError('err789')] * 10)
        )
        event = self.get_event(self.ENTITY, operation=operation)
        with self.assertRaisesRegexp(ServiceHandlerException, 'err789'):
            self.handler.process(HEADER, event)


@with_settings_hosts(**DEFAULT_SETTINGS)
class TestSid2Change(_BaseTestMailUnsubscriptionsHandler):
    ENTITY = 'subscriptions'
    OPERATIONS = ['added', 'removed']

    OPERATION_PARAMETERS = merge_parameters(OPERATIONS)
    OPERATION_AND_SUBSCRIBED_PARAMETERS = merge_parameters(
        OPERATIONS,
        (True, False),
    )
    OPERATION_SUBSCRIBED_AND_NON_PORTAL_ALIAS_PARAMETERS = merge_parameters(
        OPERATIONS,
        (True, False),
        NON_PORTAL_ALIASES,
    )

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_account_not_found__no_actions(self, operation):
        self.setup_blackbox_account_response(uid=None)
        event = self.get_event(self.ENTITY, operation=operation, sid='2')
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called(with_sid2=True)
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Uid .+ not found')

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_account_unsubscribed_from_maillists_empty__no_actions(self, operation):
        self.setup_blackbox_account_response(unsubscribed_attr='')
        event = self.get_event(self.ENTITY, operation=operation, sid='2')
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called(with_sid2=True)
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Attr unsubscribed_from_maillists is empty. Skipping')

    @parameterized.expand(OPERATION_AND_SUBSCRIBED_PARAMETERS)
    def test_usual_account__ok(self, operation, subscribed):
        self.setup_blackbox_account_response(subscribed_to_sid2=subscribed)
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=operation, sid='2')

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(with_sid2=True)
        if subscribed:
            expected_unsubscribe = [10, 11, 20, 21]
            expected_subscribe = []
        else:
            expected_subscribe = [10, 11, 20, 21]
            expected_unsubscribe = []
        self.assert_sender_set_called([
            self.sender_set_call(email, expected_subscribe, expected_unsubscribe)
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3, TEST_NATIVE_ALIAS_EMAIL1]
        ])
        self.assert_sender_copy_not_called()

    def test_usual_account__dry_run__ok(self):
        self.setup_blackbox_account_response(subscribed_to_sid2=True)
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation='added', sid='2')

        self.handler.dry_run = True
        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(with_sid2=True)

        self.assert_sender_set_not_called()
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_SUBSCRIBED_AND_NON_PORTAL_ALIAS_PARAMETERS)
    def test_non_portal_account__ok(self, operation, subscribed, alias_type):
        self.setup_blackbox_account_response(alias_type=alias_type, subscribed_to_sid2=subscribed)
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=operation, sid='2')

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called(with_sid2=True)
        if subscribed:
            expected_unsubscribe = [10, 11, 20, 21]
            expected_subscribe = []
        else:
            expected_subscribe = [10, 11, 20, 21]
            expected_unsubscribe = []
        self.assert_sender_set_called([
            self.sender_set_call(email, expected_subscribe, expected_unsubscribe)
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3]
        ])
        self.assert_sender_copy_not_called()

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_blackbox_error__handler_exception(self, operation):
        self.blackbox.set_response_side_effect('userinfo', BlackboxTemporaryError('err123'))
        event = self.get_event(self.ENTITY, operation=operation, sid='2')
        with self.assertRaisesRegexp(ServiceHandlerException, 'err123'):
            self.handler.process(HEADER, event)

    @parameterized.expand(OPERATION_PARAMETERS)
    def test_sender_set_error__handler_exception(self, operation):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects(
            *([SenderApiTemporaryError('err456')] * 10)
        )
        event = self.get_event(self.ENTITY, operation=operation, sid='2')
        with self.assertRaisesRegexp(ServiceHandlerException, 'err456'):
            self.handler.process(HEADER, event)


@with_settings_hosts(**DEFAULT_SETTINGS)
class TestEmailChange(_BaseTestMailUnsubscriptionsHandler):
    ENTITY = 'account.emails'
    OPERATION = 'added'

    def _get_email_event(self, email_id=TEST_EXT_EMAIL_ID1):
        return self.get_event(
            self.ENTITY,
            operation=self.OPERATION,
            email_id=str(email_id),
            confirmed_at='2020-01-01',
        )

    def test_account_not_found__no_actions(self):
        self.setup_blackbox_account_response(uid=None)
        self.handler.process(HEADER, self._get_email_event())

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Uid .+ not found')

    def test_account_unsubscribed_from_maillists_empty__no_actions(self):
        self.setup_blackbox_account_response(unsubscribed_attr='')
        self.handler.process(HEADER, self._get_email_event())

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Attr unsubscribed_from_maillists is empty. Skipping')

    def test_email_id_not_found__no_actions(self):
        self.setup_blackbox_account_response()
        self.handler.process(HEADER, self._get_email_event(email_id=77712345))

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Email .+ not found')

    def test_email_not_confimed__no_actions(self):
        self.setup_blackbox_account_response()
        self.handler.process(HEADER, self._get_email_event(email_id=TEST_EXT_EMAIL_ID3))

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Email .+ is not confirmed')

    def test_no_native_emails__no_action(self):
        self.setup_blackbox_account_response(native_emails=[])
        self.handler.process(HEADER, self._get_email_event())

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_not_called()
        self.assert_last_log_re(r'Account has no native emails to copy unsubscriptions')

    def test_non_native_email__ok(self):
        self.setup_blackbox_account_response()
        self.setup_sender_copy_effects()
        self.handler.process(HEADER, self._get_email_event())

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_copy_called([
            self.sender_copy_call(TEST_NATIVE_OTHER_EMAIL3, TEST_EXT_EMAIL1),
        ])
        self.assert_sender_set_not_called()

    def test_non_native_email__dry_run__ok(self):
        self.setup_blackbox_account_response()
        self.setup_sender_copy_effects()

        self.handler.dry_run = True
        self.handler.process(HEADER, self._get_email_event())

        self.assert_blackbox_userinfo_called(email_attributes='all')
        self.assert_sender_copy_not_called()
        self.assert_sender_set_not_called()

    def test_blackbox_error__handler_exception(self):
        self.blackbox.set_response_side_effect('userinfo', BlackboxTemporaryError('err123'))
        event = self._get_email_event()
        with self.assertRaisesRegexp(ServiceHandlerException, 'err123'):
            self.handler.process(HEADER, event)

    def test_sender_set_error__handler_exception(self):
        self.setup_blackbox_account_response()
        self.setup_sender_copy_effects(
            *([SenderApiTemporaryError('err456')] * 10)
        )
        event = self._get_email_event()
        with self.assertRaisesRegexp(ServiceHandlerException, 'err456'):
            self.handler.process(HEADER, event)


@with_settings_hosts(**DEFAULT_SETTINGS)
class TestPortalAliasAdded(_BaseTestMailUnsubscriptionsHandler):
    ENTITY = 'aliases'
    OPERATION = 'added'

    def test_account_not_found__no_actions(self):
        self.setup_blackbox_account_response(uid=None)
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called()
        self.assert_sender_not_called()

    def test_account_unsubscribed_from_maillists_empty__no_actions(self):
        self.setup_blackbox_account_response(uid=None, unsubscribed_attr='')
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called()
        self.assert_sender_not_called()

    def test_usual_account__ok(self):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called()
        self.assert_sender_set_called([
            self.sender_set_call(email, [30, 31], [10, 11, 20, 21])
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3, TEST_NATIVE_ALIAS_EMAIL1]
        ])
        self.assert_sender_copy_not_called()

    def test_usual_account__dry_run__ok(self):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')

        self.handler.dry_run = True
        self.handler.process(HEADER, event)

        self.assert_blackbox_userinfo_called()
        self.assert_sender_set_not_called()
        self.assert_sender_copy_not_called()

    @parameterized.expand(NON_PORTAL_ALIASES)
    def test_non_portal_account__ok(self, alias_type):
        self.setup_blackbox_account_response(alias_type=alias_type)
        self.setup_sender_set_effects()
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')

        self.handler.process(HEADER, event)
        self.assert_blackbox_userinfo_called()
        self.assert_sender_set_called([
            self.sender_set_call(email, [30, 31], [10, 11, 20, 21])
            for email in [TEST_NATIVE_OTHER_EMAIL1, TEST_NATIVE_OTHER_EMAIL2, TEST_NATIVE_OTHER_EMAIL3]
        ])
        self.assert_sender_copy_not_called()

    def test_blackbox_error__handler_exception(self):
        self.blackbox.set_response_side_effect('userinfo', BlackboxTemporaryError('err123'))
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')
        with self.assertRaisesRegexp(ServiceHandlerException, 'err123'):
            self.handler.process(HEADER, event)

    def test_sender_set_error__handler_exception(self):
        self.setup_blackbox_account_response()
        self.setup_sender_set_effects(
            *([SenderApiTemporaryError('err456')] * 10)
        )
        event = self.get_event(self.ENTITY, operation=self.OPERATION, type='1')
        with self.assertRaisesRegexp(ServiceHandlerException, 'err456'):
            self.handler.process(HEADER, event)


class MockFuture(mock.Mock):
    def __init__(self, exc=None, *args, **kwargs):
        super().__init__(
            result=mock.Mock(side_effect=self._result),
            done=mock.Mock(side_effect=lambda: self._is_done),
            *args,
            **kwargs,
        )
        self._is_done = False
        self._exc = exc

    def _result(self):
        self._is_done = True
        if self._exc:
            raise self._exc


class TestAsyncMethod(_BaseTestMailUnsubscriptionsHandler):
    def setUp(self):
        super().setUp()
        self.executor_pool_submit = mock.Mock()
        self.executor_pool = mock.Mock(
            name='executor_pool',
            submit=self.executor_pool_submit,
        )
        self.executor_class = mock.Mock(
            name='ThreadPoolExecutor',
            return_value=self.executor_pool,
        )
        self.executor_patch = mock.patch(
            'passport.backend.logbroker_client.mail_unsubscriptions.handler.ThreadPoolExecutor',
            self.executor_class,
        )
        self.executor_patch.start()
        del self.handler

    def tearDown(self):
        self.executor_patch.stop()
        super().tearDown()

    def make_handler(self, thread_count=5):
        return MailUnsubscriptionsHandler(self.config, thread_count)

    def test_iteration(self):
        mock_futures = [MockFuture(), MockFuture(), MockFuture()]
        self.executor_pool_submit.side_effect = mock_futures

        handler = self.make_handler()
        handler.process(HEADER, GOOD_EVENTS_DATA)

        self.executor_class.assert_called_once_with(max_workers=5)
        calls = self.executor_pool_submit.call_args_list
        self.assertEqual(len(calls), 3)
        for call in calls:
            self.assertIsInstance(call[0][0], partial)
            self.assertEqual(call[0][0].func, handler.process_event)

        self.assertEqual(
            [call[0][1].__class__ for call in calls],
            [EmailConfirmedAddEvent, Sid2ChangeEvent, UnsubscribedFromMaillistsAttributeChangeEvent],
        )

        for i, future in enumerate(mock_futures):
            try:
                future.result.assert_called_once_with()
            except AssertionError as err:
                raise AssertionError('{}: {}'.format(i, err))

    def test_complete_on_exception(self):
        mock_futures = [MockFuture(), MockFuture(exc=RuntimeError('Blah blah')), MockFuture()]
        self.executor_pool_submit.side_effect = mock_futures

        handler = self.make_handler()
        with self.assertRaisesRegexp(RuntimeError, r'Blah blah'):
            handler.process(HEADER, GOOD_EVENTS_DATA)

        for i, future in enumerate(mock_futures):
            try:
                future.result.assert_called_once_with()
            except AssertionError as err:
                raise AssertionError('{}: {}'.format(i, err))

    def test_complete_on_two_exceptions(self):
        mock_futures = [
            MockFuture(),
            MockFuture(exc=RuntimeError('Blah blah')),
            MockFuture(exc=RuntimeError('Oh wow')),
            MockFuture(),
        ]
        self.executor_pool_submit.side_effect = mock_futures

        handler = self.make_handler()
        events = GOOD_EVENTS_DATA + self.get_event('account.unsubscribed_from_maillists')
        with self.assertRaisesRegexp(RuntimeError, r'Blah blah'):
            handler.process(HEADER, events)

        for i, future in enumerate(mock_futures):
            try:
                future.result.assert_called_once_with()
            except AssertionError as err:
                raise AssertionError('{}: {}'.format(i, err))
