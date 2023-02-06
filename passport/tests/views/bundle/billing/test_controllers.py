# -*- coding: utf-8 -*-

from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    EmailTestMixin,
)
from passport.backend.core.builders.billing.faker.billing import (
    billing_check_binding_response,
    billing_create_binding_response,
    billing_do_binding_response,
    billing_list_payment_methods_response,
    billing_unbind_card_response,
    TEST_PURCHASE_TOKEN,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from six.moves import xmlrpc_client

from .base import (
    BaseBillingTestCase,
    CommonBillingBundleTests,
    TEST_CARD_ID,
    TEST_HOST,
    TEST_IP,
    TEST_SESSIONID_VALUE,
    TEST_TOKEN,
    TEST_UID,
)


class ListPaymentMethodsTestCase(BaseBillingTestCase, CommonBillingBundleTests):
    billing_method = 'list_payment_methods'
    default_url = '/1/bundle/billing/list_payment_methods/?consumer=dev'
    parsed_billing_response = billing_list_payment_methods_response(serialize=False)

    def setUp(self):
        super(ListPaymentMethodsTestCase, self).setUp()
        self.fake_billing.set_response_value('list_payment_methods', billing_list_payment_methods_response())

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.ListPaymentMethods',
            (TEST_TOKEN, {'uid': str(TEST_UID), 'user_ip': TEST_IP}),
        )
        self.assert_statbox_log(with_check_cookies=True)

    def test_ok_with_full_params(self):
        self.http_query_args['ym_schema'] = 100500

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.ListPaymentMethods',
            (TEST_TOKEN, {'uid': str(TEST_UID), 'ym_schema': '100500', 'user_ip': TEST_IP}),
        )


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'card_add'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'card_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:card_add': 5,
            'push:card_change': 5,
        },
    )
)
class CreateBindingTestCase(
    BaseBillingTestCase,
    CommonBillingBundleTests,
):
    billing_method = 'create_binding'
    default_url = '/1/bundle/billing/create_binding/?consumer=dev'
    parsed_billing_response = billing_create_binding_response(serialize=False)

    def setUp(self):
        super(CreateBindingTestCase, self).setUp()
        self.fake_billing.set_response_value('create_binding', billing_create_binding_response())

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CreateBinding',
            (TEST_TOKEN, {'uid': str(TEST_UID)}),
        )
        self.assert_statbox_log(with_check_cookies=True)

    def test_ok_with_full_params(self):
        self.http_query_args.update(
            return_path='http://blabla',
            back_url='http://car',
            timeout=xmlrpc_client.MAXINT,
            currency='rur',
            region_id=xmlrpc_client.MININT,
            lang='ru',
            template_tag='mobile',
            domain_sfx='com.tr',
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CreateBinding',
            (
                TEST_TOKEN,
                {
                    'uid': str(TEST_UID),
                    'return_path': 'http://blabla',
                    'back_url': 'http://car',
                    'timeout': xmlrpc_client.MAXINT,
                    'currency': 'rur',
                    'region_id': xmlrpc_client.MININT,
                    'lang': 'ru',
                    'template_tag': 'mobile',
                    'domain_sfx': 'com.tr',
                },
            ),
        )


class DoBindingTestCase(BaseBillingTestCase, CommonBillingBundleTests):
    billing_method = 'do_binding'
    default_url = '/1/bundle/billing/do_binding/?consumer=dev'
    parsed_billing_response = billing_do_binding_response(serialize=False)

    def setUp(self):
        super(DoBindingTestCase, self).setUp()
        self.fake_billing.set_response_value('do_binding', billing_do_binding_response())
        self.http_query_args['purchase_token'] = TEST_PURCHASE_TOKEN

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.DoBinding',
            (TEST_TOKEN, {'purchase_token': TEST_PURCHASE_TOKEN}),
        )
        self.assert_statbox_log(with_check_cookies=True)


class CheckBindingTestCase(BaseBillingTestCase, CommonBillingBundleTests):
    billing_method = 'check_binding'
    default_url = '/1/bundle/billing/check_binding/?consumer=dev'
    parsed_billing_response = billing_check_binding_response(serialize=False)

    def setUp(self):
        super(CheckBindingTestCase, self).setUp()
        self.fake_billing.set_response_value('check_binding', billing_check_binding_response())
        self.http_query_args['purchase_token'] = TEST_PURCHASE_TOKEN

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CheckBinding',
            (TEST_TOKEN, {'purchase_token': TEST_PURCHASE_TOKEN}),
        )
        self.assert_statbox_log(with_check_cookies=True)


@with_settings_hosts(
    ACCOUNT_MODIFICATION_MAIL_ENABLE={'card_delete'},
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'card_change'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'email:card_delete': 5,
            'push:card_change': 5,
        },
    )
)
class UnbindCardTestCase(
    EmailTestMixin,
    BaseBillingTestCase,
    CommonBillingBundleTests,
    AccountModificationNotifyTestMixin,
):
    billing_method = 'unbind_card'
    default_url = '/1/bundle/billing/unbind_card/?consumer=dev'
    parsed_billing_response = billing_unbind_card_response(serialize=False)

    def setUp(self):
        super(UnbindCardTestCase, self).setUp()
        self.fake_billing.set_response_value('unbind_card', billing_unbind_card_response())
        self.fake_billing.set_response_value('list_payment_methods', billing_list_payment_methods_response())
        self.http_query_args['card'] = TEST_CARD_ID
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(UnbindCardTestCase, self).tearDown()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ] * 2,
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'] * 2)

    def test_ok(self):
        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
        self.fake_billing.requests[1].assert_xmlrpc_method_called(
            'BalanceSimple.UnbindCard',
            (
                TEST_TOKEN,
                {
                    'session_id': TEST_SESSIONID_VALUE,
                    'user_ip': TEST_IP,
                    'host': TEST_HOST,
                    'card': TEST_CARD_ID,
                },
            ),
        )
        self.assert_statbox_log(with_check_cookies=True)
        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='card_change',
            uid=TEST_UID,
            title='Новые данные о карте в аккаунте %s' % self.userinfo['login'],
            body='Если это изменение внесли вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
            context='{"track_id": "%s"}' % self.track_id,
        )

    def test_send_mail_when_card_change(self):
        email = self.create_native_email(self.userinfo['login'], 'yandex.ru')
        self.userinfo.update(emails=[email])
        self.setup_blackbox()

        card_id = 'card-3600'
        card_info = billing_list_payment_methods_response(serialize=False)['payment_methods'][card_id]

        rv = self.make_request(query_args=dict(card=card_id))

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )

        r = self.env.blackbox.get_requests_by_method('sessionid')[0]
        r.assert_query_contains(dict(emails='getall'))
        self.assert_emails_sent([
            self.create_account_modification_mail(
                'card_delete',
                email['address'],
                dict(
                    login=self.userinfo['login'],
                    NUMBER=card_info['number'],
                    USER_IP=TEST_IP,
                ),
            ),
        ])

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.ListPaymentMethods',
            (TEST_TOKEN, {'uid': str(TEST_UID), 'user_ip': TEST_IP}),
        )
