# -*- coding: utf-8 -*-

import datetime

from nose.tools import eq_
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.app_passwords.switch import GRANT
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


TEST_HOST = 'passport-test.yandex.ru'
TEST_SESSIONID = '2:session'
TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_USER_COOKIES = 'Session_id=%s; yandexuid=%s' % (
    TEST_SESSIONID,
    TEST_YANDEXUID_COOKIE,
)
TEST_USER_IP = '127.0.0.2'
TEST_ORIGIN = 'test-origin'

TEST_UID = 42
TEST_LOGIN = 'test_user'
TEST_PASSWORD_HASH = '1:hash'
TEST_COOKIE_AGE = 123
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=datetime.datetime.fromtimestamp(1),
)


@with_settings_hosts
class SwitchBaseTestCase(BaseBundleTestViews, EmailTestMixin):
    """
    Базовый класс для тестирования активации/деактивации паролей приложений
    (здесь и далее называется просто "переключателем"). Содержит набор
    необходимых хелперов и параметризуемых тестов, которые уже должны вызываться
    в классах-потомках с нужными параметрами.
    """

    uid = TEST_UID
    ip = TEST_USER_IP
    # Имя переключателя, должно задаваться в классе-потомке.
    switch_name = None

    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        cookie=TEST_USER_COOKIES,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list([GRANT])

        self.unixtime_mock = TimeNow()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args = dict(track_id=self.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = self.uid
            track.origin = TEST_ORIGIN

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            unixtime=self.unixtime_mock,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'account_modification_enable_app_passwords',
            uid=str(self.uid),
            event='account_modification',
            entity='account.enable_app_password',
            user_agent='-',
            ip=self.ip,
        )
        self.env.statbox.bind_entry(
            'account_revoke_app_passwords',
            uid=str(self.uid),
            event='account_modification',
            entity='account.revoker.app_passwords',
            operation='updated',
            user_agent='-',
            ip=self.ip,
            new=DatetimeNow(convert_to_datetime=True),
            old=TEST_GLOBAL_LOGOUT_DATETIME,
        )
        self.env.statbox.bind_entry(
            'app_passwords',
            uid=str(self.uid),
            mode='app_passwords',
            action=self.switch_name,
            track_id=self.track_id,
            ip=self.ip,
            origin=TEST_ORIGIN,
            yandexuid=TEST_YANDEXUID_COOKIE,
        )

    def set_blackbox_response(
        self,
        password_is_set=True,
        totp_is_set=False,
        app_passwords_is_activated=None,
        password_verification_age=TEST_COOKIE_AGE,
        is_federal=False,
    ):
        bb_response = blackbox_sessionid_multi_response(
            uid=self.uid,
            attributes={
                'account.enable_app_password': app_passwords_is_activated,
                'account.2fa_on': totp_is_set,
            },
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            crypt_password=TEST_PASSWORD_HASH if password_is_set else None,
            age=password_verification_age,
            aliases={'federal': 'some_federal_alias'} if is_federal else None,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_response,
        )

        self.env.db.serialize(bb_response)

    # db
    def assert_db_shard_query_count(self, shard=0):
        self.env.db.check_query_counts(central=0, shard=shard)

    def assert_app_passwords_position(self, position):
        if position:
            self.env.db.check_db_attr(self.uid, 'account.enable_app_password', '1')
        else:
            self.env.db.check_db_attr_missing(self.uid, 'account.enable_app_password')

    def assert_app_passwords_revocation(self, is_revoked):
        if is_revoked:
            self.env.db.check_db_attr(self.uid, 'revoker.app_passwords', TimeNow())
        else:
            self.env.db.check_db_attr_missing(self.uid, 'revoker.app_passwords')

    # history
    def assert_events_are_logged_to_history(self, events):
        self.assert_events_are_logged(self.env.handle_mock, events)

    def assert_no_events_are_logged_to_history(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_history_ok(self, position):
        events = {
            'action': 'app_passwords.' + self.switch_name,
            'consumer': 'dev',
            'info.enable_app_password': str(int(position)),
        }
        if not position:
            events['info.app_passwords_revoked'] = TimeNow()
        self.assert_events_are_logged_to_history(events)

        # Проверим, что записанные в лог события парсятся для ручки /account/events
        parsed_events = [e._asdict() for e in self.env.event_logger.parse_events()]
        eq_(len(parsed_events), 1)

        expected_key = 'app_passwords_enabled' if position else 'app_passwords_disabled'

        eq_(parsed_events[0].get('event_type'), expected_key)
        expected_actions = [{'type': expected_key}]
        if not position:
            expected_actions.append({'type': 'app_passwords_revoked'})
        eq_(
            sorted(expected_actions, key=lambda d: d['type']),
            sorted(parsed_events[0].get('actions'), key=lambda d: d['type']),
        )

    # statbox
    def assert_check_cookies_logged_to_statbox(self):
        self.env.statbox_logger.assert_has_written([self.env.statbox.entry('check_cookies')])

    def assert_statbox_ok(self, expected_position, current_position):
        """
        Проверяет правильность записей в statbox-лог после успешного переключения учитывая
        текущее (старое) положение переключателя.
        :param expected_position: Ожидаемое (новое) положение переключателя после успешного переключения.
        :param current_position: Текущее (старое) положение переключателя до переключения.
        """
        entries = [
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'account_modification_enable_app_passwords',
                old='-' if current_position is None else str(int(current_position)),
                new=str(int(expected_position)),
                operation='created' if current_position is None else 'updated',
            ),
        ]
        if not expected_position:
            entries.append(self.env.statbox.entry('account_revoke_app_passwords'))
        entries.append(self.env.statbox.entry('app_passwords'))

        self.env.statbox_logger.assert_has_written(entries)

    # emails
    def check_emails_not_sent(self):
        self.assert_emails_sent([])

    def build_email(self, address, is_native):
        raise NotImplementedError()  # pragma: no cover

    def check_emails_sent(self):
        self.assert_emails_sent([
            self.build_email(address='%s@%s' % (TEST_LOGIN, 'gmail.com'), is_native=False),
            self.build_email(address='%s@%s' % (TEST_LOGIN, 'yandex.ru'), is_native=True),
        ])

    # high-level
    def assert_work_was_not_performed(self, position):
        """
        Проверяет отстутствие признаков выполнения какой-либо реальной работы при неуспешной проверке
        требуемых условий срабатывания переключателя: не должно быть никаких записей в историю, в статистику,
        запросов в базу, и положение переключателя должно остаться неизменным.
        """
        self.assert_db_shard_query_count(0)
        self.assert_app_passwords_position(position)
        self.assert_app_passwords_revocation(is_revoked=False)
        self.assert_no_events_are_logged_to_history()
        self.assert_check_cookies_logged_to_statbox()
        self.check_emails_not_sent()

    def assert_work_was_performed(self, expected_position, current_position):
        """
        Проверяет правильность выполнения всей реальной работы в случае успешного ответа: запись событий в историю,
        запись в статистику, выполненные запросы в базу, установленное положение переключателя.
        """
        # При включении два INSERT-запроса склеиваются. При выключении Insert и Delete не склеиваются.
        shard_query_count = 1 if expected_position else 2
        self.assert_db_shard_query_count(shard_query_count)
        self.assert_app_passwords_position(expected_position)
        if not expected_position:
            self.assert_app_passwords_revocation(is_revoked=True)
        self.assert_history_ok(expected_position)
        self.assert_statbox_ok(expected_position, current_position)
        self.check_emails_sent()

    # private tests
    def _test_fail_if_account_without_password(self, position):
        """
        Тестирует ошибочный ответ, если на аккаунте нет пароля.
        """
        self.set_blackbox_response(password_is_set=False, app_passwords_is_activated=position)

        rv = self.make_request()

        self.assert_error_response(rv, ['account.without_password'])
        self.assert_work_was_not_performed(position)

    def _test_fail_if_password_not_entered_recently(self, current_position):
        """
        Тестирует ошибочный ответ, если пароль не вводился.
        """
        self.set_blackbox_response(app_passwords_is_activated=current_position, password_verification_age=-1)

        rv = self.make_request()

        self.assert_error_response(rv, ['password.required'])
        self.assert_work_was_not_performed(current_position)

    def _test_fail_if_at_same_position(self, position):
        """
        Тестирует ошибочный ответ, если переключатель уже находится в желаемом положении.
        """
        self.set_blackbox_response(password_is_set=True, app_passwords_is_activated=position)

        rv = self.make_request()

        self.assert_error_response(rv, ['action.not_required'])
        self.assert_work_was_not_performed(position)

    def _test_switch_position(self, expected_position, current_position):
        """
        Тестирует успешный ответ, если всё требуемые условия соблюдены.
        :param expected_position: Ожидаемое (новое) положение переключателя после успешного переключения.
        :param current_position: Текущее (старое) положение переключателя до переключения. Требуется для
        проверки правильности записи в statbox-лог.
        """
        self.set_blackbox_response(password_is_set=True, app_passwords_is_activated=current_position)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_work_was_performed(expected_position, current_position)

    def _test_switch_position_federal(
        self,
        expected_position,
        current_position,
    ):
        """
        Тестирует успешный ответ, для аккаунта федерала.
        :param expected_position: Ожидаемое (новое) положение переключателя после успешного переключения.
        :param current_position: Текущее (старое) положение переключателя до переключения. Требуется для
        проверки правильности записи в statbox-лог.
        """
        self.set_blackbox_response(
            password_is_set=False,
            app_passwords_is_activated=current_position,
            password_verification_age=-1,
            is_federal=True,
        )

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_work_was_performed(expected_position, current_position)


class ActivatorTestCase(SwitchBaseTestCase):
    """
    Тестирует ручку активации паролей приложений.
    """

    default_url = '/1/account/app_passwords/activate/?consumer=dev'
    switch_name = 'activate'

    def build_email(self, address, is_native):
        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'app_passwords_enabled.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'app_passwords_enabled.notice': {
                    'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                    'ACCESS_CONTROL_URL_END': '</a>',
                },
                'app_passwords_enabled.disable': {
                    'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                    'ACCESS_CONTROL_URL_END': '</a>',
                },
                'signature.secure': {},
            },
        }

    def test_fail_if_account_without_password(self):
        self._test_fail_if_account_without_password(True)

    def test_fail_if_already_activated(self):
        self._test_fail_if_at_same_position(True)

    def test_activate_if_current_position_is_false(self):
        self._test_switch_position(expected_position=True, current_position=False)

    def test_activate_if_current_position_is_none(self):
        self._test_switch_position(expected_position=True, current_position=None)

    def test_fail_if_password_not_entered_recently(self):
        self._test_fail_if_password_not_entered_recently(current_position=False)

    def test_activate_federal(self):
        self._test_switch_position_federal(
            expected_position=True, current_position=False,
        )


class DeactivatorTestCase(SwitchBaseTestCase):
    """
    Тестирует ручку деактивации паролей приложений.
    """

    default_url = '/1/account/app_passwords/deactivate/?consumer=dev'
    switch_name = 'deactivate'

    def build_email(self, address, is_native):
        return {
            'language': 'ru',
            'addresses': [address],
            'subject': 'app_passwords_disabled.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'app_passwords_disabled.notice': {},
                'app_passwords_disabled.enable': {
                    'ACCESS_CONTROL_URL_BEGIN': '<a href=\'https://passport.yandex.ru/profile/access\'>',
                    'ACCESS_CONTROL_URL_END': '</a>',
                },
                'app_passwords_disabled.2fa': {},
                'signature.secure': {},
            },
        }

    def test_fail_if_account_without_password(self):
        self._test_fail_if_account_without_password(False)

    def test_fail_if_already_deactivated(self):
        self._test_fail_if_at_same_position(False)

    def test_deactivate(self):
        self._test_switch_position(expected_position=False, current_position=True)

    def test_fail_if_password_not_entered_recently(self):
        self._test_fail_if_password_not_entered_recently(current_position=True)

    def test_fail_if_2fa_is_on(self):
        self.set_blackbox_response(password_is_set=False, totp_is_set=True, app_passwords_is_activated=True)
        rv = self.make_request()

        self.assert_error_response(rv, ['action.impossible'])
        self.assert_work_was_not_performed(position=True)

    def test_deactivate_federal(self):
        self._test_switch_position_federal(
            expected_position=False, current_position=True,
        )
