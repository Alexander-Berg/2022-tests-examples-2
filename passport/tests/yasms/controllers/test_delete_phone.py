# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    istest,
)
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import DeletePhoneView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import (
    yasms_delete_phone_response,
    yasms_send_sms_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.models.phones.faker import (
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_phone_has_been_bound,
    assert_secure_phone_being_removed,
    build_account,
    build_phone_bound,
    build_phone_secured,
    build_remove_operation,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
    TEST_PROXY_IP,
)


UID = 4814
PHONE_NUMBER1 = PhoneNumber.parse(u'+79259164525')
PHONE_ID1 = 19
PHONE_NUMBER2 = PhoneNumber.parse(u'+79025411724')
PHONE_ID2 = 23
OPERATION_ID = 661
TEST_DATE = datetime(2001, 2, 3, 4, 5, 6)
VALIDATION_CODE = u'1111'
PHONISH_LOGIN = 'phne-login'
TEST_USER_AGENT = u'curl'
LOGIN = u'andrey1931'


@with_settings_hosts(
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestDeletePhoneView(
    BaseTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
    BlackboxCommonTestCase,
    AccountModificationNotifyTestMixin,
):
    default_headers = {
        u'Ya-Client-User-Agent': TEST_USER_AGENT,
        u'Ya-Client-Host': 'yandex.ru',
    }

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(DeletePhoneView)

    def test_not_secure__ok__history_db(self):
        """
        Проверим, что пишется в history_db.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account(
            phone_number=PHONE_NUMBER1.e164,
            phone_id=17,
        )

        self.make_request(number=PHONE_NUMBER1.e164, sender=u'dev')

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': 'delete_phone',
                u'consumer': u'dev',
                u'phone.17.action': u'deleted',
                u'phone.17.number': PHONE_NUMBER1.e164,
                u'phones.default': u'0',
                u'user_agent': TEST_USER_AGENT,
            },
        )

    def test_not_secure__ok__db(self):
        """
        Проверим, что номер удаляется из хранилища.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account(
            uid=UID,
            phone_number=PHONE_NUMBER1.e164,
            phone_id=PHONE_ID1,
        )

        self.make_request(uid=UID, number=PHONE_NUMBER1.e164)

        assert_no_phone_in_db(self.env.db, UID, PHONE_ID1, PHONE_NUMBER1.e164)
        assert_no_default_phone_chosen(self.env.db, UID)
        assert_phone_has_been_bound(self.env.db, UID, PHONE_NUMBER1.e164, times=1)

    def test_not_secure__ok__statbox(self):
        """
        Проверим, что пишется в статбокс.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        self.make_request()

        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_not_secure__ok__send_sms(self):
        """
        Проверим, куда уходят СМСки.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        self.make_request()

        eq_(len(self.env.yasms.get_requests_by_method(u'send_sms')), 0)

    def test_not_secure__ok__send_email(self):
        """
        Проверим, куда уходит электронная почта.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        self.make_request()

        eq_(len(self.env.mailer.messages), 0)

    def test_not_secure__ok(self):
        """
        Прверим, ответ ручки.
        Номер не защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'OK'),
        )

    def _put_secure_phone_to_account(self,
                                     uid=UID,
                                     phone_number=PHONE_NUMBER1.e164,
                                     phone_id=PHONE_ID1,
                                     created=TEST_DATE,
                                     bound=TEST_DATE,
                                     confirmed=TEST_DATE,
                                     secured=TEST_DATE,
                                     admitted=None,
                                     language=u'ru',
                                     emails=None,
                                     firstname=u'Андрей'):
        self._build_account(
            uid=UID,
            firstname=firstname,
            language=language,
            emails=emails,
            **build_phone_secured(
                phone_id,
                phone_number,
                created,
                bound,
                confirmed,
                secured,
                admitted,
                is_default=True,
                is_alias=True,
            )
        )
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            [
                # Сообщение с кодом для подтверждения
                yasms_send_sms_response(sms_id=1),
                # Сообщение с уведомлением
                yasms_send_sms_response(sms_id=2),
            ],
        )

    def test_secure__ok__history_db(self):
        """
        Проверим, что пишется в history_db.
        Номер защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_secure_phone_to_account(
            phone_number=PHONE_NUMBER1.e164,
            phone_id=17,
        )

        self.make_request(sender=u'dev', number=PHONE_NUMBER1.e164)

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': u'delete_phone',
                u'consumer': u'dev',
                u'phone.17.number': PHONE_NUMBER1.e164,
                u'phone.17.operation.1.action': u'created',
                u'phone.17.operation.1.type': u'remove',
                u'phone.17.operation.1.security_identity': u'1',
                u'phone.17.operation.1.started': TimeNow(),
                u'phone.17.operation.1.finished': TimeNow(offset=settings.PHONE_QUARANTINE_SECONDS),
                u'user_agent': TEST_USER_AGENT,
            },
        )

    def test_secure__ok__db(self):
        """
        Проверим, что номер удаляется из хранилища.
        Номер защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_secure_phone_to_account(
            uid=PHONE_ID1,
            phone_number=PHONE_NUMBER1.e164,
            phone_id=PHONE_ID1,
            created=TEST_DATE,
            bound=TEST_DATE,
            confirmed=TEST_DATE,
            secured=TEST_DATE,
            admitted=TEST_DATE,
        )

        self.make_request(number=PHONE_NUMBER1.e164, uid=UID)

        assert_secure_phone_being_removed.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID1, u'number': PHONE_NUMBER1.e164},
            {
                u'id': 1,
                u'started': DatetimeNow(),
                u'finished': DatetimeNow() + timedelta(seconds=settings.PHONE_QUARANTINE_SECONDS),
                u'code_value': VALIDATION_CODE,
                u'code_checks_count': 0,
                u'code_send_count': 1,
                u'code_last_sent': DatetimeNow(),
                u'code_confirmed': None,
                u'password_verified': None,
            },
        )

    def test_secure__ok__statbox(self):
        """
        Проверим, что пишется в статбокс.
        Номер защищён.
        """
        self.assign_grants([grants.DELETE_PHONE], networks=[u'1.2.3.4'])
        self._put_secure_phone_to_account(
            uid=UID,
            phone_number=u'+79010000001',
        )

        self.make_request(
            uid=UID,
            number=u'+79010000001',
            sender=u'dev',
            headers={
                u'X-Real-IP': TEST_PROXY_IP,
                u'Ya-Consumer-Real-Ip': u'1.2.3.4',
                u'Ya-Client-User-Agent': TEST_USER_AGENT,
            },
        )

        self.env.statbox.assert_equals([
            self.env.statbox.entry(
                'yasms',
                uid=str(UID),
                number=u'+79010******',
                action=u'delete_phone.delete_phone.notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
                consumer=u'dev',
                ip=u'1.2.3.4',
                sms_id='2',
            ),
            self.env.statbox.entry(
                'remove_secure_operation_created',
                uid=str(UID),
                number=u'+79010******',
                phone_id=str(PHONE_ID1),
                ip=u'1.2.3.4',
                consumer=u'dev',
                user_agent=TEST_USER_AGENT,
            ),
            self.env.statbox.entry(
                'yasms',
                uid=str(UID),
                number=u'+79010******',
                ip=u'1.2.3.4',
                action=u'delete_phone.delete_phone.send_confirmation_code.code_sent',
                consumer=u'dev',
                operation_id=u'1',
                sms_count=u'1',
                sms_id=u'1',
            ),
        ])

    def test_secure__ok__send_sms(self):
        """
        Проверим, куда уходят СМСки.
        Номер защищён.
        """
        self.assign_grants(
            [grants.DELETE_PHONE],
            consumer=u'old_yasms_grants_stix',
        )
        self._put_secure_phone_to_account(
            uid=UID,
            language=u'ru',
        )

        self.make_request(
            sender=u'stix',
            uid=UID,
        )

        send_sms_requests = self.env.yasms.get_requests_by_method(u'send_sms')
        eq_(len(send_sms_requests), 2)
        send_sms_requests[0].assert_query_contains({
            u'text': u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
            u'from_uid': str(UID),
            u'identity': u'delete_phone.delete_phone.send_confirmation_code',
            u'caller': u'stix',
        })
        send_sms_requests[0].assert_post_data_contains({
            u'text_template_params': u'{"code": "%s"}' % VALIDATION_CODE,
        })
        send_sms_requests[1].assert_query_contains({
            u'text': u'Начато удаление телефона на Яндексе: https://ya.cc/sms-help-ru',
            u'from_uid': str(UID),
            u'identity': u'notify_user_by_sms_that_secure_phone_removal_started.notify',
            u'caller': u'stix',
        })

    def test_secure__ok__no_email(self):
        """
        Уведомления по электронной почте не высылаются, т.к. мы не наничаем
        карантин.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_secure_phone_to_account(
            emails=[
                self.env.email_toolkit.create_native_email(
                    login=u'andrey1931',
                    domain=u'yandex-team.ru',
                ),
            ],
            firstname=u'Андрей',
        )

        self.make_request()

        messages = self.env.mailer.messages
        eq_(len(messages), 0)

    def test_secure__ok(self):
        """
        Проверим ответ ручки.
        Номер защищён.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_secure_phone_to_account()

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'STARTED'),
        )
        self.check_account_modification_push_not_sent()

    def test_invalid_phone_number(self):
        """
        Ручке даётся номер в неправильной форме.
        У пользователя есть телефоны в ЧЯ.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        response = self.make_request(number=u'02')

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'NOTFOUND'),
        )

    def test_account_not_found(self):
        self.assign_grants([grants.DELETE_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request(uid=UID)

        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'NOTFOUND'),
        )

    def test_secure__has_operation__internal_error(self):
        """
        Защищённый номер с операцией.
        """
        self.assign_grants([grants.DELETE_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **deep_merge(
                    build_phone_secured(
                        PHONE_ID1,
                        PHONE_NUMBER1.e164,
                        is_default=True,
                    ),
                    build_remove_operation(OPERATION_ID, PHONE_ID1),
                )
            ),
        )

        response = self.make_request(uid=UID, number=PHONE_NUMBER1.e164)

        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'INTERROR'),
        )

    def test_phone_number_not_found(self):
        self.assign_grants([grants.DELETE_PHONE])
        self._put_not_secure_phone_to_account()

        response = self.make_request(number=PHONE_NUMBER2.e164)

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'NOTFOUND'),
        )

    def test_many_not_secure__ok(self):
        self.assign_grants([grants.DELETE_PHONE])
        self._build_account(
            **deep_merge(
                build_phone_bound(PHONE_ID1, PHONE_NUMBER1.e164),
                build_phone_bound(PHONE_ID2, PHONE_NUMBER2.e164),
            )
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'OK'),
        )

    def test_phonish(self):
        # Удаление номера у фониша запрещено
        self.assign_grants([grants.DELETE_PHONE])

        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                **deep_merge(
                    {
                        'uid': UID,
                        'login': PHONISH_LOGIN,
                        'aliases': {
                            'phonish': PHONISH_LOGIN,
                        },
                    },
                    build_phone_bound(
                        PHONE_ID1,
                        PHONE_NUMBER1.e164,
                        binding_flags=flags,
                    ),
                )
            ),
        )

        response = self.make_request(uid=UID, number=PHONE_NUMBER1.e164)

        self.assert_json_responses_equal(
            response,
            yasms_delete_phone_response(uid=UID, status=u'INTERROR'),
        )

    def make_request(self, sender=u'dev', uid=UID, number=PHONE_NUMBER1.e164,
                     headers=None):
        self.response = self.env.client.get(
            u'/yasms/api/deletephone',
            query_string={u'sender': sender, u'uid': uid, u'number': number},
            headers=headers or self.default_headers,
        )
        return self.response

    def assert_response_is_error(self, message, code, encoding=u'utf-8'):
        self.assert_response_is_json_error(code)

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        self.assert_json_responses_equal(
            self.response,
            yasms_delete_phone_response(uid=UID, status=u'OK'),
        )

    def setUp(self):
        super(TestDeletePhoneView, self).setUp()
        self.start_account_modification_notify_mocks(ip='127.0.0.1')
        self.setup_kolmogor()
        self.env.code_generator.set_return_value(VALIDATION_CODE)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        super(TestDeletePhoneView, self).tearDown()

    def _build_account(self, uid=UID, language=u'ru', emails=None,
                       firstname=u'Андрей', **kwargs):
        kwargs = deep_merge(
            {
                u'uid': uid,
                u'login': LOGIN,
                u'aliases': {u'portal': u'andrey1931'},
                u'firstname': firstname,
                u'language': language,
                u'emails': emails or [],
            },
            kwargs,
        )
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **kwargs
        )

    def _put_not_secure_phone_to_account(self, phone_number=PHONE_NUMBER1.e164,
                                         phone_id=PHONE_ID1, uid=UID):
        self._build_account(
            uid=uid,
            **build_phone_bound(
                phone_id,
                phone_number,
                phone_created=TEST_DATE,
                phone_bound=TEST_DATE,
                phone_confirmed=TEST_DATE,
                is_default=True,
            )
        )

    def setup_blackbox_to_serve_good_response(self):
        self._put_not_secure_phone_to_account()
