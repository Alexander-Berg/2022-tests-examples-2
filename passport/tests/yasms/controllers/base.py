# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import AccountHistoryTestMixin
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.yasms import grants
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    BlackboxYasmsConfigurator,
)
from passport.backend.core.conf import settings
from passport.backend.core.models.phones.faker import PhoneIdGeneratorFaker
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)
from passport.backend.core.xml.test_utils import assert_xml_response_equals


__all__ = (
    u'BaseTestCase',
    u'BlackboxCommonTestCase',
    u'OptionalSenderWhenGrantsAreRequiredTestMixin',
    u'OptionalSenderWhenGrantsAreOptionalTestMixin',
    u'RequiredSenderWhenGrantsAreRequiredTestMixin',
    u'RequiredUidWhenGrantsAreRequiredTestMixin',
    u'RequiredUidWhenGrantsAreOptionalTestMixin',
    u'BlackboxYasmsConfigurator',
    u'TEST_PROXY_IP',
)

TEST_NON_NUMBER_UID = u'test_non_number_uid'
TEST_INVALID_PHONE_NUMBERS = [u'261234567', u'01', u'abcdef', u'0953111111']
TEST_USER_AGENT = u'curl'
TEST_PROXY_IP = '127.0.0.255'


class BaseTestCase(BaseTestViews, AccountHistoryTestMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.assign_no_grants()
        self._phone_id_generator_faker = PhoneIdGeneratorFaker()
        self._phone_id_generator_faker.start()

    def tearDown(self):
        self._phone_id_generator_faker.stop()
        self.env.stop()
        del self.env
        del self._phone_id_generator_faker

    def assert_response_is_error(self, message, code, encoding=u'utf-8'):
        return self.assert_response_is_xml_error(message, code, encoding)

    def assert_response_is_xml_error(self, message, code, encoding=u'utf-8'):
        assert_xml_response_equals(
            self.response,
            u'''
            <?xml version="1.0" encoding="{encoding}"?>
            <doc>
            <error>{message}</error>
            <errorcode>{code}</errorcode>
            </doc>
            '''.format(message=message, code=code, encoding=encoding),
        )

    def assert_response_is_json_error(self, code):
        eq_(self.response.status_code, 200)
        eq_(json.loads(self.response.data), {u'error': code})

    def assign_all_grants(self, networks=[u'127.0.0.1'], tvm_client_id=None):
        self.assign_grants(
            [
                grants.CHECK_PHONE,
                grants.DELETE_PHONE,
                grants.DROP_PHONE,
                grants.HAVE_USER_ONCE_VALIDATED_PHONE,
                grants.PROLONG_VALID,
                grants.REGISTRATOR,
                grants.REMOVE_USER_PHONES,
                grants.RETURN_FULL_PHONE,
                grants.USER_PHONES,
                grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            ],
            networks=networks,
            tvm_client_id=tvm_client_id,
        )

    def assign_no_grants(self):
        self.assign_grants([])

    def assign_grants(self, grant_list, consumer=u'old_yasms_grants_dev',
                      networks=[u'127.0.0.1'], tvm_client_id=None):
        splitted_grants = {}
        for composite_grant_name in grant_list:
            grant, op = composite_grant_name.split(u'.')
            splitted_grants[grant] = [op]

        config = dict(
            grants=splitted_grants,
            networks=networks,
        )
        if tvm_client_id:
            config.update(dict(client=dict(client_id=tvm_client_id)))

        grants_to_assign = {
            consumer: config,
            settings.SUBSTITUTE_CONSUMER_IP_CONSUMER: dict(networks=[TEST_PROXY_IP]),
        }
        self.env.grants.set_grants_return_value(grants_to_assign)

    def assert_unhandled_exception_is_processed(self, view_class):
        self.assign_all_grants()
        with mock.patch.object(
            view_class,
            u'process_request',
            side_effect=Exception(u'Test exception'),
        ):
            r = self.make_request()
            eq_(r.status_code, 200)
            self.assert_response_is_error(u'Internal error', u'INTERROR')

    def assert_no_rights_error_when_sender_misses_rights_and_invalid_phone(self, phone_arg_name=u'phone'):
        """
        Показать сообщение о том, что у потребителя не хватает разрешений,
        даже когда, есть ошибка в phone.
        """
        self.assign_no_grants()
        self.setup_blackbox_to_serve_good_response()

        for phone_number in TEST_INVALID_PHONE_NUMBERS:
            kwargs = {phone_arg_name: phone_number}
            r = self.make_request(**kwargs)
            eq_(r.status_code, 200)
            self.assert_response_is_error(u'Not enough rights', u'NORIGHTS')

    def assert_dont_know_you_error_when_invalid_sender_and_invalid_phone(self, phone_arg_name=u'phone'):
        """
        Показать сообщение о том, что потребитель не знаком, даже когда,
        есть ошибка в phone.
        """
        self.env.grants.set_grants_return_value({})
        self.setup_blackbox_to_serve_good_response()

        for phone_number in TEST_INVALID_PHONE_NUMBERS:
            kwargs = {u'sender': u'unknown', phone_arg_name: phone_number}
            r = self.make_request(**kwargs)
            eq_(r.status_code, 200)
            self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def assert_sender_is_not_granted_when_invalid_uid(self):
        """
        Показать сообщение о том, что у потребителя не хватает разрешений,
        даже когда, есть ошибка в uid.
        """
        self.assign_no_grants()
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request(uid=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"Not enough rights", u'NORIGHTS')

    def assert_sender_is_unknown_when_invalid_uid(self):
        """
        Показать сообщение о том, что потребитель не знаком, даже когда,
        есть ошибка в uid.
        """
        self.assign_grants([], u'known_sender')
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request(sender=u'unknown', uid=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def assert_no_uid_error_when_empty_uid(self):
        "Показать ошибку NOUID, когда uid пустой."
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        # нет uid
        r = self.make_request(uid=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u'User ID not specified', u'NOUID')

        # пустой uid
        r = self.make_request(uid=u'')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u'User ID not specified', u'NOUID')

    def assert_no_uid_error_when_invalid_uid(self):
        "Показать ошибку NOUID, когда uid имеет неверную форму."
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request(uid=TEST_NON_NUMBER_UID)

        eq_(r.status_code, 200)
        self.assert_response_is_error(
            u'User ID not specified',
            u'NOUID',
        )

        r = self.make_request(uid=u'-1')

        eq_(r.status_code, 200)
        self.assert_response_is_error(
            u'User ID not specified',
            u'NOUID',
        )

    def assert_response_is_ok_when_empty_sender_and_ip_is_granted(self):
        """
        Запрос будет обработан, если sender пуст, но для данного интернет
        адреса выделены все необходимые разрешения.
        """
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        # нет sender, у адреса есть все разрешения
        self.make_request(sender=None)

        self.assert_response_is_good_response()

        # пустой sender, у адреса есть все разрешения
        self.make_request(sender=u'')

        self.assert_response_is_good_response()

    def assert_uses_consumer_real_ip(self):
        """
        Адрес потребителя берётся из заголовка Ya-Consumer-Real-Ip, если X-Real_IP доверенный.
        """
        self.assign_all_grants(networks=[u'127.0.0.2'])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(headers=[
            (u'X-Real-IP', TEST_PROXY_IP),
            (u'Ya-Consumer-Real-Ip', u'127.0.0.2'),
            (u'Ya-Client-User-Agent', TEST_USER_AGENT),
        ])
        self.assert_response_is_good_response()

    def assert_uses_x_real_ip(self):
        """
        Адрес потребителя берётся из заголовка X-Real-Ip.
        """
        self.assign_all_grants(networks=[u'127.0.0.2'])
        self.setup_blackbox_to_serve_good_response()

        self.make_request(headers=[
            (u'X-Real-IP', u'127.0.0.2'),
            (u'Ya-Client-User-Agent', TEST_USER_AGENT),
        ])
        self.assert_response_is_good_response()

    def assert_no_rights_error_when_empty_sender_and_ip_is_granted_but_not_enough_rights(self):
        """
        Показать ошибку NORIGHTS, если sender пуст, а интернет адрес известен
        грантушке, но ему не выделено необходимых разрешений.
        """
        self.assign_no_grants()
        self.setup_blackbox_to_serve_good_response()

        # нет sender, не достаточно разрешений
        r = self.make_request(sender=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u'Not enough rights', u'NORIGHTS')

        # пустой sender, не достаточно разрешений
        r = self.make_request(sender=u'')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u'Not enough rights', u'NORIGHTS')

    def assert_dont_know_you_error_when_empty_sender_and_ip_is_not_granted(self):
        """
        Показать ошибку DONTKNOWYOU, если sender пуст, а интернет адрес
        неизвестен грантушке.
        """
        self.assign_grants([], u'known_sender', [])
        self.setup_blackbox_to_serve_good_response()

        # нет sender
        r = self.make_request(sender=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

        # пустой sender
        r = self.make_request(sender=u'')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def assert_dont_know_you_error_when_invalid_sender(self):
        """
        Показать ошибку DONTKNOWYOU, если sender имеет неверную форму или
        неизвестен Грантушке.
        """
        # Выставляем потребителя с местным интернет адресом, чтобы
        # гарантировать, что система не воспользуется адресом, когда задан
        # потребитель.
        self.assign_grants([], u'some_known_sender', [u'127.0.0.1'])
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request(sender=u'\u0000')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

        r = self.make_request(sender=u'unknown')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def assert_no_rights_error_when_sender_misses_required_grants(self):
        """
        Показать ошибку NORIGHTS, если у sender нет необходимых
        разрешений.
        """
        self.assign_no_grants()
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request()

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"Not enough rights", u'NORIGHTS')

    def assert_json_responses_equal(self, actual, expected):
        if hasattr(actual, u'data'):
            actual = actual.data
        if hasattr(expected, u'data'):
            expected = expected.data
        eq_(json.loads(actual), json.loads(expected))

    def init_blackbox_yasms_configurator(self):
        return BlackboxYasmsConfigurator(self.env.blackbox)

    def make_request(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def setup_blackbox_to_serve_good_response(self):
        """
        Метод настраивает Чёрный ящик, так что тот может отдать корректный
        ответ.
        """

    def assert_response_is_good_response(self):
        """
        Метод утверждает, что ручка обработала корректный ответ старого Я.Смса
        и вернула свой корректный ответ.
        """
        raise NotImplementedError()  # pragma: no cover


class BlackboxCommonTestCase(object):
    def test_internal_error_when_getting_account_results_in_invalid_blackbox_response(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(u'userinfo', u'invalid response')

        self.make_request()

        self.assert_response_is_error(
            u'Blackbox replied with invalid response',
            u'INTERROR',
        )

    def test_internal_error_when_getting_account_results_in_db_fetch_failed_error_blackbox_response(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_json_error_response(u'DB_FETCHFAILED'),
        )

        self.make_request()

        self.assert_response_is_error(
            u'Blackbox internal error occured',
            u'INTERROR',
        )

    def test_internal_error_when_getting_account_results_in_db_exception_error_blackbox_response(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_json_error_response(u'DB_EXCEPTION'),
        )

        self.make_request()

        self.assert_response_is_error(
            u'Blackbox internal error occured',
            u'INTERROR',
        )

    def test_internal_error_when_getting_account_results_in_unknown_error_blackbox_response(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_json_error_response(u'UNKNOWN'),
        )

        self.make_request()

        self.assert_response_is_error(
            u'Blackbox internal error occured',
            u'INTERROR',
        )

    def test_uses_consumer_real_ip(self):
        self.assert_uses_consumer_real_ip()

    def test_uses_x_real_ip(self):
        self.assert_uses_x_real_ip()


class OptionalSenderWhenGrantsAreRequiredTestMixin(object):
    """
    Набор тестов гарантирующих ожидаемую проверку разрешений для ручек
    с необходимыми разрешениями и необязательным sender.
    """
    def test_empty_sender_when_ip_is_granted(self):
        self.assert_response_is_ok_when_empty_sender_and_ip_is_granted()

    def test_empty_sender_when_ip_is_granted_but_not_enough_rights(self):
        self.assert_no_rights_error_when_empty_sender_and_ip_is_granted_but_not_enough_rights()

    def test_empty_sender_when_ip_is_not_granted(self):
        self.assert_dont_know_you_error_when_empty_sender_and_ip_is_not_granted()

    def test_dont_know_you_error_when_invalid_sender(self):
        self.assert_dont_know_you_error_when_invalid_sender()

    def test_not_enough_rights_error_when_sender_misses_required_grants(self):
        self.assert_no_rights_error_when_sender_misses_required_grants()

    def test_dont_know_you_error_when_sender_should_have_tvm_ticket(self):
        self.assign_all_grants(tvm_client_id=123)
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request(sender=None)

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

        r = self.make_request(sender=u'')

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def test_valid_tvm_ticket(self):
        self.assign_all_grants(tvm_client_id=TEST_CLIENT_ID_2)
        self.setup_blackbox_to_serve_good_response()

        self.make_request(
            sender=None,
            headers=[(u'X-Ya-Service-Ticket', TEST_TICKET)],
        )

        self.assert_response_is_good_response()


class OptionalSenderWhenGrantsAreOptionalTestMixin(object):
    """
    Набор тестов гарантирующих ожидаемую проверку разрешений для ручек
    без обязательного sender и грантов.
    """
    def test_empty_sender_when_ip_is_granted(self):
        self.assert_response_is_ok_when_empty_sender_and_ip_is_granted()

    def test_empty_sender_when_ip_is_not_granted(self):
        self.assert_dont_know_you_error_when_empty_sender_and_ip_is_not_granted()

    def test_dont_know_you_error_when_invalid_sender(self):
        self.assert_dont_know_you_error_when_invalid_sender()


class RequiredSenderWhenGrantsAreRequiredTestMixin(object):
    """
    Набор тестов гарантирующих ожидаемую проверку разрешений для ручек
    с обязательным sender и необходимыми разрешениями.
    """
    def test_dont_know_you_error_when_invalid_sender(self):
        self.assert_dont_know_you_error_when_invalid_sender()

    def test_no_rights_error_when_sender_misses_required_grants(self):
        self.assert_no_rights_error_when_sender_misses_required_grants()

    def test_no_sender_error_when_empty_sender(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        self.make_request(sender=None)
        self.assert_response_is_error(u'No sender defined', u'NOSENDER')

        self.make_request(sender=u'')
        self.assert_response_is_error(u'No sender defined', u'NOSENDER')

    def test_dont_know_you_error_when_sender_should_have_tvm_ticket(self):
        self.assign_all_grants(tvm_client_id=123)
        self.setup_blackbox_to_serve_good_response()

        r = self.make_request()

        eq_(r.status_code, 200)
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def test_valid_tvm_ticket(self):
        self.assign_all_grants(tvm_client_id=TEST_CLIENT_ID_2)
        self.setup_blackbox_to_serve_good_response()

        self.make_request(headers=[
            (u'X-Ya-Service-Ticket', TEST_TICKET),
            (u'Ya-Client-User-Agent', TEST_USER_AGENT),
        ])

        self.assert_response_is_good_response()


class RequiredUidWhenGrantsAreRequiredTestMixin(object):
    """Набор тестов для ручек в которые передаётся uid и требуются гранты."""
    def test_sender_is_not_granted_when_invalid_uid(self):
        self.assert_sender_is_not_granted_when_invalid_uid()

    def test_sender_is_unknown_when_invlaid_uid(self):
        self.assert_sender_is_unknown_when_invalid_uid()

    def test_no_uid_error_when_empty_uid(self):
        self.assert_no_uid_error_when_empty_uid()

    def test_no_uid_error_when_invalid_uid(self):
        self.assert_no_uid_error_when_invalid_uid()


class RequiredUidWhenGrantsAreOptionalTestMixin(object):
    """
    Набор тестов для ручек в которые передаётся uid и нет обязятельных грантов.
    """
    def test_sender_is_unknown_when_invlaid_uid(self):
        self.assert_sender_is_unknown_when_invalid_uid()

    def test_no_uid_error_when_empty_uid(self):
        self.assert_no_uid_error_when_empty_uid()

    def test_no_uid_error_when_invalid_uid(self):
        self.assert_no_uid_error_when_invalid_uid()
