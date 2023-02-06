# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import ConfirmView
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.yasms.faker import yasms_confirm_response
from passport.backend.core.mailer.faker.mail_utils import create_native_email
from passport.backend.core.models.phones.faker import (
    assert_phone_unbound,
    assert_secure_phone_bound,
    build_account,
    build_phone_bound,
    build_secure_phone_being_bound,
    event_lines_mark_operation_created,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.xml.test_utils import assert_xml_response_equals

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
)


UID = 4814
UID_EXTRA = 5015
LOGIN = u'test1'
LOGIN_EXTRA = u'test2'
PHONE_NUMBER = PhoneNumber.parse(u'+79000000001')
PHONE_ID = 9944
PHONE_ID_EXTRA = 7722
CONFIRMATION_CODE = u'1234'
CONFIRMATION_CODE_EXTRA = u'4321'
OPERATION_ID = 2000
TEST_DATE = datetime(2014, 1, 2, 3, 4, 5)
TEST_CODE_CHECKS_LIMIT = 5
USER_IP = u'127.0.0.1'
ALIAS_SID = 65
CONSUMER = u'dev'
TEST_OPERATION_TTL = timedelta(hours=1)
TEST_USER_AGENT = u'curl'


@nottest
class _BaseConfirmTestCase(BaseTestCase):
    default_headers = {
        u'Ya-Client-User-Agent': TEST_USER_AGENT,
        u'Ya-Client-Host': 'yandex.ru',
    }

    def test_no_phone_id_error_when_phone_id_and_phone_number_are_empty(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        response = self.make_request(id=None, number=None)

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Phone ID not specified', u'NOPHONEID')

    def test_no_phone_id_error_when_phone_id_is_invalid(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        response = self.make_request(id=u'invalid')

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Phone ID not specified', u'NOPHONEID')

    def test_no_phone_error_when_phone_number_is_invalid(self):
        # Для номера не вызывалась register
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        response = self.make_request(number=u'invalid')

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Impossible to confirm the phone number', u'NOPHONE')

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(ConfirmView)

    def test_args_in_post_data(self):
        """
        Ручка может воспользоваться POST параметрами.
        """
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        self.response = self.env.client.post(
            u'/yasms/confirm',
            data={
                u'sender': u'dev',
                u'uid': UID,
                u'code': CONFIRMATION_CODE,
                u'number': PHONE_NUMBER.e164,
            },
            headers={
                u'Ya-Client-User-Agent': TEST_USER_AGENT,
            }
        )

        self.assert_response_is_good_response()

    def make_request(self, sender=CONSUMER, uid=UID, code=CONFIRMATION_CODE,
                     number=PHONE_NUMBER.e164, id=None, headers=None):
        self.response = self.env.client.get(
            u'/yasms/confirm',
            query_string={
                u'sender': sender,
                u'uid': uid,
                u'code': code,
                u'number': number,
                u'phoneid': id,
            },
            headers=headers or self.default_headers,
        )
        return self.response

    def assert_response_is_good_response(self):
        self._assert_response_is_phone_bound(self.response)

    def _assert_response_is_phone_bound(self, response):
        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_confirm_response(
                PHONE_ID,
                PHONE_NUMBER.e164,
                UID,
                is_valid=True,
                is_current=True,
                code_checks_left=None,
            ),
        )

    def _assert_response_is_wrong_code(self, response, code_checks_left):
        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_confirm_response(
                PHONE_ID,
                PHONE_NUMBER.e164,
                UID,
                is_valid=False,
                is_current=False,
                code_checks_left=code_checks_left,
            ),
        )

    def _statbox_line_code_confirmed(self, **kwargs):
        return self.env.statbox.entry(
            u'base',
            action=u'confirm.confirm.phone_confirmed',
            phone_id=str(PHONE_ID),
            number=PHONE_NUMBER.masked_format_for_statbox,
            confirmation_time=DatetimeNow(convert_to_datetime=True),
            operation_id=str(OPERATION_ID),
            ip=USER_IP,
            consumer=CONSUMER,
            uid=str(UID),
            **kwargs
        )

    def _statbox_line_secure_phone_bound(self, **kwargs):
        return self.env.statbox.entry(
            u'base',
            action=u'confirm.confirm.secure_phone_bound',
            phone_id=str(PHONE_ID),
            number=PHONE_NUMBER.masked_format_for_statbox,
            operation_id=str(OPERATION_ID),
            ip=USER_IP,
            consumer=CONSUMER,
            uid=str(UID),
            **kwargs
        )

    def _statbox_line_karma_changed(self, **kwargs):
        return self.env.statbox.entry(
            u'frodo_karma',
            action=u'confirm',
            uid=str(UID),
            login=LOGIN,
            old=u'0',
            new=u'6000',
            registration_datetime=u'-',
            ip=USER_IP,
            consumer=CONSUMER,
            user_agent=TEST_USER_AGENT,
            **kwargs
        )

    def _statbox_line_phone_alias_subscription(self, **kwargs):
        return self.env.statbox.entry(
            u'subscriptions',
            ip=USER_IP,
            sid=str(ALIAS_SID),
            consumer=CONSUMER,
            operation=u'added',
            uid=str(UID),
            user_agent=TEST_USER_AGENT,
            **kwargs
        )

    def _statbox_line_phonenumber_alias_created(self, **kwargs):
        return self.env.statbox.entry(
            'phonenumber_alias_added',
            uid=str(UID),
            consumer=CONSUMER,
            user_agent=TEST_USER_AGENT,
            **kwargs
        )

    def _statbox_line_phone_unbound(self, **kwargs):
        return self.env.statbox.entry(
            u'base',
            action=u'confirm.phone_unbound',
            number=PHONE_NUMBER.masked_format_for_statbox,
            phone_id=str(PHONE_ID_EXTRA),
            ip=USER_IP,
            consumer=CONSUMER,
            uid=str(UID_EXTRA),
            **kwargs
        )

    def _event_lines_alias_created(self):
        return (
            {u'uid': str(UID), u'name': u'alias.phonenumber.add', u'value': PHONE_NUMBER.international},
            {u'uid': str(UID), u'name': u'info.phonenumber_alias_search_enabled', u'value': '1'},
        )

    def _event_lines_secure_phone_bound(self):
        fmt = (PHONE_ID, OPERATION_ID)
        return (
            {u'uid': str(UID), u'name': u'phone.%d.action' % PHONE_ID, u'value': u'changed'},
            {u'uid': str(UID), u'name': u'phone.%d.number' % PHONE_ID, u'value': PHONE_NUMBER.e164},
            {u'uid': str(UID), u'name': u'phone.%d.bound' % PHONE_ID, u'value': TimeNow()},
            {u'uid': str(UID), u'name': u'phone.%d.secured' % PHONE_ID, u'value': TimeNow()},
            {u'uid': str(UID), u'name': u'phone.%d.confirmed' % PHONE_ID, u'value': TimeNow()},
            {u'uid': str(UID), u'name': u'phone.%d.operation.%d.action' % fmt, u'value': u'deleted'},
            {u'uid': str(UID), u'name': u'phone.%d.operation.%d.security_identity' % fmt, u'value': u'1'},
            {u'uid': str(UID), u'name': u'phone.%d.operation.%d.type' % fmt, u'value': u'bind'},
            {u'uid': str(UID), u'name': u'phones.secure', u'value': str(PHONE_ID)},
        )

    def _event_lines_karma_full_changed(self):
        return (
            {u'uid': str(UID), u'name': u'info.karma_full', u'value': u'6000'},
        )

    def _event_lines_karma_changed(self):
        return (
            {u'uid': str(UID), u'name': u'info.karma_prefix', u'value': u'6'},
        )

    def _event_lines_action_consumer(self, uid):
        return (
            {u'uid': str(uid), u'name': u'action', u'value': u'confirm'},
            {u'uid': str(uid), u'name': u'consumer', u'value': CONSUMER},
            {u'uid': str(UID), u'name': u'user_agent', u'value': TEST_USER_AGENT},
        )

    def _event_lines_phone_marked(self):
        return event_lines_mark_operation_created(
            uid=UID_EXTRA,
            phone_id=PHONE_ID_EXTRA,
            phone_number=PHONE_NUMBER,
            operation_id=2001,
            operation_ttl=TEST_OPERATION_TTL,
            user_agent=None,
        )

    def _event_lines_phone_unbound(self):
        return (
            {u'uid': str(UID_EXTRA), u'name': u'action', u'value': u'unbind_phone_from_account'},
            {u'uid': str(UID_EXTRA), u'name': u'consumer', u'value': CONSUMER},
            {u'uid': str(UID_EXTRA), u'name': u'reason_uid', u'value': str(UID)},

            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.action' % PHONE_ID_EXTRA, u'value': u'changed'},
            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.number' % PHONE_ID_EXTRA, u'value': PHONE_NUMBER.e164},
            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.bound' % PHONE_ID_EXTRA, u'value': u'0'},
            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.operation.2001.action' % PHONE_ID_EXTRA, u'value': u'deleted'},
            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.operation.2001.type' % PHONE_ID_EXTRA, u'value': u'mark'},
            {u'uid': str(UID_EXTRA), u'name': u'phone.%d.operation.2001.security_identity' % PHONE_ID_EXTRA, u'value': PHONE_NUMBER.digital},

            {u'uid': str(UID), u'name': u'unbind_phone_from_account.%d' % UID_EXTRA, u'value': PHONE_NUMBER.e164},
        )


@with_settings_hosts(
    YASMS_SENDER=u'passport',
    YASMS_VALIDATION_LIMIT=1,
    YASMS_PHONE_BINDING_LIMIT=1,
    SMS_VALIDATION_MAX_CHECKS_COUNT=TEST_CODE_CHECKS_LIMIT,
    YASMS_MARK_OPERATION_TTL=TEST_OPERATION_TTL.total_seconds(),
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'phone_change'},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:phone_change': 5,
        },
    )
)
@istest
class TestConfirmView(_BaseConfirmTestCase,
                      BlackboxCommonTestCase,
                      RequiredSenderWhenGrantsAreRequiredTestMixin,
                      RequiredUidWhenGrantsAreRequiredTestMixin,
                      AccountModificationNotifyTestMixin):
    def setUp(self):
        super(TestConfirmView, self).setUp()
        self.env.statbox.bind_entry(
            u'account_phones_secure',
            _inherit_from=[u'account_modification'],
            uid=str(UID),
            entity=u'phones.secure',
            operation=u'created',
            new=PHONE_NUMBER.masked_format_for_statbox,
            new_entity_id=str(PHONE_ID),
            old=u'-',
            old_entity_id=u'-',
            consumer=CONSUMER,
            user_agent=TEST_USER_AGENT,
        )

        # Запись о блокировке телефона перед отвязкой
        self.env.statbox.bind_entry(
            u'mark_operation_created',
            _inherit_from=[u'mark_operation_created'],
            uid=str(UID_EXTRA),
            operation_id=str(OPERATION_ID + 1),
            phone_id=str(PHONE_ID_EXTRA),
            number=PHONE_NUMBER.masked_format_for_statbox,
            user_agent=TEST_USER_AGENT,
            consumer=CONSUMER,
            ip=USER_IP,
        )

        self.env.statbox.bind_entry(
            u'phonenumber_alias_search_enabled',
            uid=str(UID),
            user_agent=TEST_USER_AGENT,
        )
        self.start_account_modification_notify_mocks(ip='127.0.0.1')
        self.setup_kolmogor()

    def tearDown(self):
        self.stop_account_modification_notify_mocks()

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def test_bind__aliasify__wash(self):
        # Привязывается защищённый номер
        # Номер нужно сделать алиасом
        # Число привязок номера в истории позволяет обелить учётную запись

        self.assign_grants([grants.REGISTRATOR])

        flags = PhoneOperationFlags()
        flags.aliasify = True
        user_info = blackbox_userinfo_response(
            uid=UID,
            login=LOGIN,
            emails=[create_native_email(LOGIN, 'yandex.ru')],
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                password_verified=datetime.now(),
                flags=flags,
            )
        )

        self.env.db.serialize(user_info)

        self.env.blackbox.set_response_side_effect(
            u'userinfo',
            [
                # Данная учётная запись
                user_info,

                # Учётная запись с алиасом
                blackbox_userinfo_response(uid=None),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                # История для обеления
                blackbox_phone_bindings_response([]),

                # Нынешние привязки для отвязки по лимиту
                blackbox_phone_bindings_response([
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER.e164,
                        u'phone_id': PHONE_ID,
                        u'uid': UID,
                        u'bound': datetime.now(),
                    },
                ]),
            ],
        )

        response = self.make_request()

        self._assert_response_is_phone_bound(response)
        assert_secure_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER.e164},
        )
        self.env.db.check_missing(u'phone_operations', id=OPERATION_ID, uid=UID, db=u'passportdbshard1')
        self.env.db.check(u'aliases', u'phonenumber', PHONE_NUMBER.digital, uid=UID, db='passportdbcentral')
        self.env.db.check(u'attributes', u'karma.value', u'6000', uid=UID, db=u'passportdbshard1')

        self.env.statbox.assert_has_written([
            self._statbox_line_code_confirmed(code_checks_count=u'1'),
            self._statbox_line_secure_phone_bound(),
            self.env.statbox.entry(u'account_phones_secure'),
            self._statbox_line_karma_changed(),
            self._statbox_line_phonenumber_alias_created(),
            self._statbox_line_phone_alias_subscription(),
            self.env.statbox.entry(u'phonenumber_alias_search_enabled'),
        ])
        self.env.event_logger.assert_events_are_logged(
            self._event_lines_action_consumer(UID) +
            self._event_lines_secure_phone_bound() +
            self._event_lines_karma_changed() +
            self._event_lines_karma_full_changed() +

            self._event_lines_action_consumer(UID) +
            self._event_lines_alias_created(),
        )
        self.assert_account_history_parses_secure_phone_set(PHONE_NUMBER)
        self.check_account_modification_push_sent(
            ip='127.0.0.1',
            event_name='phone_change',
            uid=UID,
            title='В аккаунте {} изменён номер телефона'.format(LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
        )

    def test_bind__dont_wash__unbind_olds(self):
        # Учётная запись заблокирована
        # Привязывается защищённый номер
        # Число привязок номера в истории не позволяет обелить учётную запись
        # Число учётных записей к которым привязан номер достигло лимита

        self.assign_grants([grants.REGISTRATOR])

        user_info = blackbox_userinfo_response(
            uid=UID,
            login=LOGIN,
            enabled=False,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                password_verified=datetime.now(),
            )
        )

        # Другая учётная запись
        extra_user = dict(
            uid=UID_EXTRA,
            login=LOGIN_EXTRA,
            **build_phone_bound(
                PHONE_ID_EXTRA,
                PHONE_NUMBER.e164,
                phone_created=TEST_DATE,
                phone_bound=TEST_DATE,
                phone_confirmed=TEST_DATE,
            )
        )

        self.env.db.serialize(user_info)
        self.env.db.serialize(blackbox_userinfo_response(**extra_user))

        self.env.blackbox.set_response_side_effect(
            u'userinfo',
            [
                # Данная учётная запись
                user_info,

                # Учётные записи для отвязки
                blackbox_userinfo_response_multiple([extra_user]),
            ],
        )

        self.env.blackbox.set_response_side_effect(
            u'phone_bindings',
            [
                # История для обеления
                blackbox_phone_bindings_response([
                    {
                        u'type': u'history',
                        u'number': PHONE_NUMBER.e164,
                        u'phone_id': PHONE_ID_EXTRA,
                        u'uid': UID_EXTRA,
                        u'bound': TEST_DATE,
                    },
                ]),

                # Нынешние привязки для отвязки по лимиту
                blackbox_phone_bindings_response([
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER.e164,
                        u'phone_id': PHONE_ID,
                        u'uid': UID,
                        u'bound': datetime.now(),
                    },
                    {
                        u'type': u'current',
                        u'number': PHONE_NUMBER.e164,
                        u'phone_id': PHONE_ID_EXTRA,
                        u'uid': UID_EXTRA,
                        u'bound': TEST_DATE,
                    },
                ]),
            ],
        )

        response = self.make_request()

        self._assert_response_is_phone_bound(response)
        assert_secure_phone_bound.check_db(
            self.env.db,
            UID,
            {u'id': PHONE_ID, u'number': PHONE_NUMBER.e164},
        )
        self.env.db.check_missing(u'phone_operations', id=OPERATION_ID, uid=UID, db=u'passportdbshard1')
        self.env.db.check_missing(u'aliases', u'phonenumber', uid=UID, db='passportdbcentral')
        self.env.db.check_missing(u'attributes', u'karma.value', uid=UID, db=u'passportdbshard1')
        assert_phone_unbound.check_db(
            self.env.db,
            UID_EXTRA,
            {u'id': PHONE_ID_EXTRA, u'number': PHONE_NUMBER.e164},
        )

        self.env.statbox.assert_has_written([
            self._statbox_line_code_confirmed(code_checks_count=u'1'),
            self._statbox_line_secure_phone_bound(),
            self.env.statbox.entry(u'account_phones_secure'),
            self.env.statbox.entry(u'mark_operation_created'),
            self._statbox_line_phone_unbound(),
        ])
        self.env.event_logger.assert_events_are_logged(
            self._event_lines_action_consumer(UID) +
            self._event_lines_secure_phone_bound() +

            self._event_lines_phone_marked() +
            self._event_lines_phone_unbound(),
        )

    def test_wrong_code(self):
        self.assign_grants([grants.REGISTRATOR])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                login=LOGIN,
                **build_secure_phone_being_bound(
                    PHONE_ID,
                    PHONE_NUMBER.e164,
                    OPERATION_ID,
                    code_value=CONFIRMATION_CODE,
                    code_checks_count=1,
                )
            ),
        )

        response = self.make_request(code=CONFIRMATION_CODE_EXTRA)

        self._assert_response_is_wrong_code(
            response,
            code_checks_left=TEST_CODE_CHECKS_LIMIT - 2,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                u'base',
                action=u'confirm.confirm.confirm_phone',
                error=u'code.invalid',
                operation_id=str(OPERATION_ID),
                code_checks_count=u'2',
                number=PHONE_NUMBER.masked_format_for_statbox,
                phone_id=str(PHONE_ID),
                uid=str(UID),
                ip=USER_IP,
                consumer=CONSUMER,
            ),
        ])
        self.env.event_logger.assert_events_are_logged([])

    def test_hit_code_checks_limit(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                login=LOGIN,
                **build_secure_phone_being_bound(
                    PHONE_ID,
                    PHONE_NUMBER.e164,
                    OPERATION_ID,
                    code_checks_count=TEST_CODE_CHECKS_LIMIT,
                )
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Max validations exeeded', u'VALEXEEDED')

        self.env.statbox.assert_has_written([])
        self.env.event_logger.assert_events_are_logged([])

    def test_account_not_found(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(u'userinfo', blackbox_userinfo_response(uid=None))

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Impossible to confirm the phone number', u'NOPHONE')

    def test_operation_confirmed(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                login=LOGIN,
                **build_secure_phone_being_bound(
                    PHONE_ID,
                    PHONE_NUMBER.e164,
                    OPERATION_ID,
                    code_value=CONFIRMATION_CODE,
                    code_confirmed=datetime.now(),
                )
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Impossible to confirm the phone number', u'NOPHONE')

    def test_operation_expired(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                login=LOGIN,
                **build_secure_phone_being_bound(
                    PHONE_ID,
                    PHONE_NUMBER.e164,
                    OPERATION_ID,
                    operation_started=datetime.now(),
                    operation_finished=datetime.now(),
                )
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_response_is_error(u'Operation is expired', u'INTERROR')

    def setup_blackbox_to_serve_good_response(self):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            uid=UID,
            **build_secure_phone_being_bound(
                PHONE_ID,
                PHONE_NUMBER.e164,
                OPERATION_ID,
                code_value=CONFIRMATION_CODE,
                password_verified=datetime.now(),
            )
        )
        self.env.blackbox.set_response_value(u'phone_bindings', blackbox_phone_bindings_response([]))
