# -*- coding: utf-8 -*-

from collections import OrderedDict
from contextlib import contextmanager
from datetime import (
    datetime,
    timedelta,
)
from unittest import TestCase

from hamcrest import (
    assert_that,
    contains_inanyorder,
)
import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    FakeBlackbox,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.dbmanager.manager import (
    get_dbm,
    safe_execute,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.env import Environment
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    AccountModificationInfosecLoggerFaker,
    AccountModificationLoggerFaker,
    CryptastatLoggerFaker,
    FamilyLoggerFaker,
    PharmaLoggerFaker,
    StatboxLoggerFaker,
)
from passport.backend.core.models.account import (
    Account,
    ACCOUNT_DISABLED_ON_DELETION,
    MAIL_STATUS_ACTIVE,
    MAIL_STATUS_FROZEN,
)
from passport.backend.core.models.alias import (
    AltDomainAlias,
    KiddishAlias,
    KinopoiskAlias,
    KolonkishAlias,
    LiteAlias,
    MailishAlias,
    NeophonishAlias,
    PddAlias,
    PhonenumberAlias,
    PhonishAlias,
    PublicIdAlias,
    ScholarAlias,
    UberAlias,
    YambotAlias,
    YandexoidAlias,
)
from passport.backend.core.models.domain import (
    Domain,
    PartialPddDomain,
)
from passport.backend.core.models.email import Email
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.models.family import (
    AccountFamilyInfo,
    FamilyInfo,
    FamilyMember,
)
from passport.backend.core.models.password import (
    Password,
    PASSWORD_CHANGING_REASON_PWNED,
    ScholarPassword,
)
from passport.backend.core.models.person import DisplayName
from passport.backend.core.models.phones.phones import (
    ReplaceSecurePhoneWithBoundPhoneOperation,
    ReplaceSecurePhoneWithNonboundPhoneOperation,
)
from passport.backend.core.models.subscription import (
    subscribe,
    Subscription,
    unsubscribe,
)
from passport.backend.core.processor import (
    fix_passport_login_rule,
    run,
    run_cryptastat,
    run_historydb,
    run_pharma,
    run_statbox,
)
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.test.consts import (
    TEST_KIDDISH_LOGIN1,
    TEST_PHONE_NUMBER1,
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_SCHOLAR_LOGIN1,
)
from passport.backend.core.test.events import (
    EventLoggerFaker,
    EventLoggerTskvFaker,
)
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    unixtime,
    unixtime_to_statbox_datetime,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.core.types.birthday import Birthday
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.mail_subscriptions import UnsubscriptionList
from passport.backend.core.types.phone import PhoneNumber
from passport.backend.core.undefined import Undefined
from passport.backend.utils.time import (
    datetime_to_integer_unixtime,
    unixtime_to_datetime,
)


HOST_ID = 10
TEST_ENVIRONMENT = Environment(user_ip='127.0.0.1')
TEST_EVENTS = {'action': 'test-action'}
TEST_TIME = datetime(2001, 1, 2, 1, 2, 1)
UID = 13
LOGIN = u'bucky'
EXTRA_UID = 17

TEST_USER_DEFINED_LOGIN = 'test.test'
TEST_USER_DEFINED_PUBLIC_ID = 'test_test'
TEST_ALIAS = 'test-test'
TEST_CYRILLIC_EMAIL = u'админ@окна.рф'
TEST_EMAIL = 'admin@okna.ru'
TEST_EMAIL2 = 'admin.2@okna.ru'

TEST_EMAIL_ID = 1

TEST_UID = UID
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_PHONE_NUMBER = PhoneNumber.parse('+79030915478')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79259164525')
TEST_PHONE_NUMBER3 = PhoneNumber.parse('+79026411724')

OLD_LOGOUT_DATETIME = DatetimeNow(convert_to_datetime=True, timestamp=datetime(1970, 1, 1, 3, 0, 0))
NEW_LOGOUT_DATETIME = DatetimeNow(convert_to_datetime=True, timestamp=datetime(1980, 1, 1, 3, 0, 0))

TEST_PHONE = '+79030915478'
TEST_PHONE_ID = 10
TEST_PHONE_ID2 = 13
TEST_PHONE_ID3 = 17

TEST_PHONE_ATTR_CREATED = 1234567892
TEST_PHONE_ATTR_BOUND = 1234567893
TEST_PHONE_ATTR_CONFIRMED = 1234567894
TEST_PHONE_ATTR_ADMITTED = 1234567895
TEST_PHONE_ATTR_SECURED = 1234567896
TEST_PHONE_ATTR_BOUND_DT = unixtime_to_datetime(TEST_PHONE_ATTR_BOUND)

TEST_PHONE_OPERATION = {
    'id': 1,
    'type': 'bind',
    'password_verified': unixtime(2000, 1, 23, 12, 34, 56),
    'started': unixtime(2000, 1, 22, 12, 34, 56),
    'finished': unixtime(2000, 1, 22, 12, 34, 57),
    'security_identity': 1,
}

TEST_PHONE_DICT = {
    'id': TEST_PHONE_ID,
    'valid': 'valid',
    'secure': 1,
    'attributes': {
        'number': TEST_PHONE_NUMBER.e164,
        'created': TEST_PHONE_ATTR_CREATED,
        'bound': TEST_PHONE_ATTR_BOUND,
        'confirmed': TEST_PHONE_ATTR_CONFIRMED,
        'admitted': TEST_PHONE_ATTR_ADMITTED,
        'secured': TEST_PHONE_ATTR_SECURED,
    },
    'operation': TEST_PHONE_OPERATION,
}

TEST_CONFIRMATION_CODE1 = '123456'
TEST_CONFIRMATION_CODE2 = '234561'

TEST_FAMILY_ID = 71


class TestRunHistoryDB(TestCase):
    def setUp(self):
        self._faker = EventLoggerFaker()
        self._faker_tskv = EventLoggerTskvFaker()
        self._faker.start()
        self._faker_tskv.start()
        self.event_log = self._faker._logger
        self.tskv_event_log = self._faker_tskv._logger

    def tearDown(self):
        self._faker.stop()
        self._faker_tskv.stop()
        del self._faker
        del self._faker_tskv
        del self.event_log
        del self.tskv_event_log

    def test_same_timestamp(self):
        """
        Все записи в одном вызове имеют одинаковую временную метку.
        """
        account = default_account(uid=UID, alias=LOGIN)

        run_historydb(
            None,
            account,
            diff({}, {}),
            TEST_ENVIRONMENT,
            {'action': 'value1', 'name2': 'value2'},
            10,
            force_external_events=True,
        )
        eq_(self._faker.events[0].time, self._faker.events[1].time)
        # В tskv это будет одна строка
        eq_(len(self._faker_tskv.events), 1)

    def test_comment_at_action_line(self):
        """
        Комментарий из переданного словаря событий записывается в той же
        строчке что и 'action'.
        """
        account = default_account(uid=UID, alias=LOGIN)

        run_historydb(
            None,
            account,
            diff({}, {}),
            TEST_ENVIRONMENT,
            {'action': 'value1', 'name2': 'value2', 'comment': 'the_comment'},
            10,
            force_external_events=True,
        )

        eq_(len(self._faker.events), 3)
        eq_(self._faker.events[-2].comment, 'the_comment')
        eq_(self._faker.events[-1].comment, '-')
        # В tskv в той же строчке, важно наличие
        eq_(self._faker_tskv.events[0].data.get('comment'), 'the_comment')

    def test_user_agent(self):
        """User_agent записывается в отдельной строке"""
        account = default_account(uid=UID, alias=LOGIN)

        run_historydb(
            None,
            account,
            diff({}, {}),
            Environment(user_ip='127.0.0.1', user_agent='firefox'),
            {'action': 'value1', 'name2': 'value2', 'comment': 'the_comment'},
            10,
            force_external_events=True,
        )

        eq_(len(self._faker.events), 4)
        event = self._faker.events[-1]
        eq_(event.name, 'user_agent')
        eq_(event.value, 'firefox')
        # В tskv это одна строка с кv user_agent=firefox
        eq_(len(self._faker_tskv.events), 1)
        eq_(self._faker_tskv.events[0].data.get('user_agent'), 'firefox')

    def test_long_user_agent(self):
        """
        User_agent обрезается до 200 символов.
        """
        account = default_account(uid=UID, alias=LOGIN)

        run_historydb(
            None,
            account,
            diff({}, {}),
            Environment(user_ip='127.0.0.1', user_agent='a' * 201),
            {'action': 'value1', 'name2': 'value2', 'comment': 'the_comment'},
            10,
            force_external_events=True,
        )

        eq_(len(self._faker.events), 4)
        event = self._faker.events[-1]
        eq_(event.name, 'user_agent')
        eq_(event.value, 'a' * 200)
        # В tskv это одна строка с кv user_agent='a' * 201
        eq_(len(self._faker_tskv.events), 1)
        eq_(self._faker_tskv.events[0].data.get('user_agent'), 'a' * 200)

    def test_yandexuid_in_action(self):
        """
        yandexuid записывается только в событие action.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff({}, {}),
            Environment(user_ip='127.0.0.1', cookies={'yandexuid': 'test_yandexuid'}),
            {'action': 'value1', 'name2': 'value2', 'comment': 'the_comment'},
            10,
            force_external_events=True,
        )
        eq_(len(self._faker.events), 3)
        eq_(self._faker.events[-2].name, 'action')
        eq_(self._faker.events[-2].yandexuid, 'test_yandexuid')
        eq_(self._faker.events[-1].yandexuid, '-')
        eq_(len(self._faker_tskv.events), 1)
        eq_(self._faker_tskv.events[0].data.get('yandexuid'), 'test_yandexuid')

    def test_internal_events__log_internal_and_external_events(self):
        """
        Если обнаружены внутренние события, то в журнал пишутся и внешние, и
        внутренние события.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff(None, account),
            Environment(),
            {u'action': u'action'},
            HOST_ID,
        )

        eq_(len(self._faker.events), 3)
        eq_(len(self._faker_tskv.events), 1)

    def test_no_internal_events__dont_log_external_events(self):
        """
        Если внутренних событий нет, то и внешние события не пишутся в журнал.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            account,
            account,
            diff(account, account),
            Environment(),
            {u'action': u'action'},
            HOST_ID,
        )

        eq_(self._faker.events, [])
        eq_(self._faker_tskv.events, [])

    def test_no_internal_events__log_external_events(self):
        """
        Если внутренних событий нет, но передан параметр force_external_events,
        то внешние события пишутся в журнал.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            account,
            account,
            diff(account, account),
            Environment(),
            {u'action': u'action'},
            HOST_ID,
            force_external_events=True,
        )

        eq_(len(self._faker.events), 1)
        eq_(len(self._faker_tskv.events), 1)

    def test_initiator_uid_equals_to_account_uid(self):
        """
        Если initiator_uid совпадает с uid'ом учётной записи, то пишутся сведения
        о запросе.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff(None, account),
            Environment(
                user_ip=u'127.0.0.1',
                cookies={u'yandexuid': u'test_yandexuid'},
                user_agent=u'test_user_agent',
            ),
            {u'action': u'action', u'user_agent': u'test_user_agent'},
            HOST_ID,
            initiator_uid=UID,
        )

        event = self._faker.events[2]
        eq_(event.name, u'action')
        eq_(event.user_ip, u'127.0.0.1')
        eq_(event.yandexuid, u'test_yandexuid')

        event = self._faker.events[3]
        eq_(event.name, u'user_agent')
        eq_(event.value, u'test_user_agent')

        eq_(len(self._faker_tskv.events), 1)
        eq_(self._faker_tskv.events[0].data.get('user_agent'), 'test_user_agent')
        eq_(self._faker_tskv.events[0].data.get('yandexuid'), 'test_yandexuid')
        eq_(self._faker_tskv.events[0].data.get('ip_from'), '127.0.0.1')
        eq_(self._faker_tskv.events[0].events.get('action'), 'action')

    def test_no_initiator_uid(self):
        """
        Если initiator_uid не указан, то пишем сведения о запросе.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff(None, account),
            Environment(
                user_ip=u'127.0.0.1',
                cookies={u'yandexuid': u'test_yandexuid'},
                user_agent=u'test_user_agent',
            ),
            {u'action': u'action'},
            HOST_ID,
        )

        event = self._faker.events[2]
        eq_(event.name, u'action')
        eq_(event.user_ip, u'127.0.0.1')
        eq_(event.yandexuid, u'test_yandexuid')

        event = self._faker.events[3]
        eq_(event.name, u'user_agent')
        eq_(event.value, u'test_user_agent')

        eq_(len(self._faker_tskv.events), 1)
        eq_(self._faker_tskv.events[0].data.get('user_agent'), 'test_user_agent')
        eq_(self._faker_tskv.events[0].data.get('yandexuid'), 'test_yandexuid')
        eq_(self._faker_tskv.events[0].data.get('ip_from'), '127.0.0.1')
        eq_(self._faker_tskv.events[0].events.get('action'), 'action')

    def test_initiator_uid_does_not_equal_to_account_uid(self):
        """
        Если initiator_uid не совпадает с uid'ом учётной записи, то сведения о
        запросе не пишутся.
        """
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff(None, account),
            Environment(
                user_ip=u'127.0.0.1',
                cookies={u'yandexuid': u'test_yandexuid'},
                user_agent=u'test_user_agent',
            ),
            {u'action': u'action'},
            HOST_ID,
            initiator_uid=EXTRA_UID,
        )

        event = self._faker.events[2]
        eq_(event.name, u'action')
        eq_(event.user_ip, u'-')
        eq_(event.yandexuid, u'-')

        eq_(self._faker_tskv.events[0].events.get('action'), 'action')
        eq_(self._faker_tskv.events[0].data.get('ip_from'), None)
        eq_(self._faker_tskv.events[0].data.get('yandexuid'), None)

    def test_defaults(self):
        account = default_account(uid=UID, alias=LOGIN)
        run_historydb(
            None,
            account,
            diff(None, account),
            Environment(),
            {},
            HOST_ID,
            initiator_uid=EXTRA_UID,
        )

        event = self._faker.events[0]
        eq_(event.admin, u'-')
        eq_(event.comment, u'-')
        eq_(self._faker_tskv.events[0].data.get('admin'), None)
        eq_(self._faker_tskv.events[0].data.get('comment'), None)

    def test_delete_account_with_aliases(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
        })
        acc.lite_alias = LiteAlias(acc, email=acc.login + '@kinopoisk.ru')
        acc.pdd_alias = PddAlias(acc, email='test@okna.ru')
        acc.phonish_alias = PhonishAlias(acc, login='phne-test')
        acc.neophonish_alias = NeophonishAlias(acc, alias='nphne-test')
        acc.mailish_alias = MailishAlias(acc, mailish_id='some-string')
        acc.kinopoisk_alias = KinopoiskAlias(acc, alias='100500')
        acc.uber_alias = UberAlias(acc, uber_id='1')
        acc.yambot_alias = YambotAlias(acc, alias='yambot-bot')
        acc.kolonkish_alias = KolonkishAlias(acc, alias='kolonkish-123')
        acc.public_id_alias = PublicIdAlias(acc, alias='public_id')
        acc.domain = PartialPddDomain().parse({
            'domid': 42,
            'domain': 'okna.ru',
        })
        run_historydb(
            acc,
            None,
            diff(acc, None),
            Environment(),
            {},
            HOST_ID,
            initiator_uid=EXTRA_UID,
        )

        historydb_records = [
            ('info.login', TEST_ALIAS),
            ('info.domain_name', '-'),
            ('info.domain_id', '-'),
            ('info.password', '-'),
            ('info.password_quality', '-'),
            ('info.password_update_time', '-'),
            ('info.totp', 'disabled'),
            ('info.totp_update_time', '-'),
            ('info.rfc_totp', 'disabled'),
            ('alias.public_id.rm', 'public_id'),
            ('sid.rm', '8|%s' % TEST_ALIAS),
        ]

        expected_value = []
        for v in historydb_records:
            name, value = v
            expected_value.append(
                {
                    'uid': str(TEST_UID),
                    'name': name,
                    'value': value,
                }
            )
        self._faker.assert_events_are_logged_with_order(expected_value)
        # Для tskv порядок не важен, только то что под одним uid
        self._faker_tskv.assert_events_are_logged(expected_value)


class TestPreprocessDiff(TestCase):
    def test_login_rule_8_on_add_account(self):
        acc = default_account()
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        eq_(modified_diff.added['subscriptions'][8]['login_rule'], 1)

    def test_no_login_rule_8_on_add_pdd_account(self):
        domain = Domain()
        domain.id = 1
        acc = default_account(alias_type='pdd').parse({'domain': domain})
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        ok_('subscriptions' not in modified_diff.added)

    def test_no_login_rule_8_on_add_kinopoisk_account(self):
        acc = default_account(alias_type='kinopoisk')
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        ok_('subscriptions' not in modified_diff.added)

    def test_no_login_rule_8_on_add_uber_account(self):
        acc = default_account(alias_type='uber')
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        ok_('subscriptions' not in modified_diff.added)

    def test_no_login_rule_8_on_add_yambot_account(self):
        acc = default_account(alias_type='yambot')
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        ok_('subscriptions' not in modified_diff.added)

    def test_no_login_rule_8_on_add_kolonkish_account(self):
        acc = default_account(alias_type='kolonkish')
        difference = diff(None, acc)
        modified_diff = fix_passport_login_rule(None, acc, difference)
        ok_('subscriptions' not in modified_diff.added)

    def test_login_rule_8_on_change_account(self):
        acc = default_account()
        s1 = acc.snapshot()
        acc.password.setup_password_changing_requirement()
        difference = fix_passport_login_rule(s1, acc, diff(s1, acc))

        eq_(difference.changed['subscriptions'][8]['login_rule'], 5)

    def test_login_rule_8_on_change_account_with_different_changing_reason(self):
        acc = default_account()
        s1 = acc.snapshot()
        acc.password.setup_password_changing_requirement(changing_reason='1234')
        difference = fix_passport_login_rule(s1, acc, diff(s1, acc))

        eq_(difference.changed['subscriptions'][8]['login_rule'], 5)

    def test_login_rule_8_no_changes(self):
        acc = default_account()
        difference = fix_passport_login_rule(acc, acc, diff(acc, acc))
        ok_('subscriptions' not in difference.changed)

    def test_login_rule_8_no_changes_with_forced_changing_reason(self):
        acc = default_account()
        acc.password.setup_password_changing_requirement(changing_reason='2')
        difference = fix_passport_login_rule(acc, acc, diff(acc, acc))
        ok_('subscriptions' not in difference.changed)

    def test_login_rule_8_cleared_on_change_account(self):
        acc = default_account()
        acc.password.setup_password_changing_requirement()
        s1 = acc.snapshot()
        acc.password.setup_password_changing_requirement(is_required=False)
        difference = fix_passport_login_rule(s1, acc, diff(s1, acc))

        eq_(difference.changed['subscriptions'][8]['login_rule'], 1)

    def test_without_subscription_login_rule_8(self):
        acc = default_account(uid=TEST_UID).parse({})
        s1 = acc.snapshot()
        acc.parse({'person.firstname': 'firstname'})
        difference = fix_passport_login_rule(s1, acc, diff(s1, acc))
        eq_(acc.person.firstname, 'firstname')
        ok_('subscriptions' not in difference.changed)

    def test_with_delete_password(self):
        acc = default_account(uid=TEST_UID).parse({'forced_changing_reason': '1'})
        s1 = acc.snapshot()
        acc.password = None
        difference = fix_passport_login_rule(s1, acc, diff(s1, acc))
        ok_('subscriptions' not in difference.changed)


class TestRunStatbox(TestCase):
    def setUp(self):
        self.statbox_handle_mock = mock.Mock()
        self.statbox = StatboxLoggerFaker()
        self.statbox.start()
        self.family_statbox = FamilyLoggerFaker()
        self.family_statbox.start()
        self.account_modification_log = AccountModificationLoggerFaker()
        self.account_modification_log.start()
        self.account_modification_infosec_log = AccountModificationInfosecLoggerFaker()
        self.account_modification_infosec_log.start()
        self.setup_statbox_templates()

    def tearDown(self):
        self.account_modification_infosec_log.stop()
        self.account_modification_log.stop()
        self.family_statbox.stop()
        self.statbox.stop()

    def _assert_family_statbox(self, entries):
        entries_basic = []
        entries_family = []
        for entry in entries:
            entries_basic.append(
                self.statbox.entry(
                    entry[0],
                    **entry[1]
                ),
            )
            entries_family.append(
                self.family_statbox.entry(
                    entry[0],
                    **entry[1]
                ),
            )
        self.statbox.assert_equals(entries_basic)
        self.family_statbox.assert_equals(entries_family)

    def _assert_statbox_has_written(self, entries, with_account_modification=True):
        self.statbox.assert_has_written(entries)
        if with_account_modification:
            self.account_modification_log.assert_has_written(entries)

    def _assert_statbox_equals(self, entries, with_account_modification=True):
        self.statbox.assert_equals(entries)
        if with_account_modification:
            self.account_modification_log.assert_equals(entries)

    def setup_statbox_templates(self):
        for logger in self.statbox, self.account_modification_log:
            logger.bind_base(
                unixtime=TimeNow(),
                tskv_format='passport-log',
                py='1',
                ip='127.0.0.1',
                user_agent='-',
                old='-',
                new='-',
                consumer='-',
                uid=str(TEST_UID),
                event='account_modification',
            )

            for op in [
                'added',
                'updated',
                'deleted',
                'created',
            ]:
                logger.bind_entry(
                    op,
                    operation=op,
                )

            logger.bind_entry(
                'domain_modification',
                event='domain_modification',
                ip='127.0.0.1',
                consumer='-',
                _exclude=['uid'],
            )
            logger.bind_entry(
                'add_alias',
                entity='aliases',
                operation='added',
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'rm_alias',
                entity='aliases',
                operation='removed',
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'add_pddalias',
                entity='pdd_alias_login',
                operation='added',
                type=str(ANT['pddalias']),
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'rm_pddalias',
                entity='pdd_alias_login',
                operation='removed',
                type=str(ANT['pddalias']),
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'add_subscription',
                entity='subscriptions',
                operation='added',
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'rm_subscription',
                entity='subscriptions',
                operation='removed',
                _exclude=['old', 'new'],
            )
            logger.bind_entry(
                'frodo_karma',
                action='value1',
                destination='frodo',
                entity='karma',
                old='-',
                new='100',
                login=TEST_ALIAS,
                suid='-',
                uid=str(TEST_UID),
                registration_datetime='-',
            )
            logger.bind_entry(
                'add_phonenumber_alias',
                _inherit_from=['aliases'],
                _exclude=['old', 'new'],
                operation='added',
                type=str(ANT['phonenumber']),
                uid=str(TEST_UID),
            )
            logger.bind_entry(
                'add_mailish_alias',
                _inherit_from=['aliases'],
                _exclude=['old', 'new'],
                operation='added',
                type=str(ANT['mailish']),
                uid=str(TEST_UID),
            )
            logger.bind_entry(
                'family_info_modification',
                event='family_info_modification',
                ip='127.0.0.1',
                consumer='-',
                _exclude=['uid'],
            )
        self.family_statbox.bind_base(
            unixtime=TimeNow(),
            tskv_format='passport-family-log',
            ip='127.0.0.1',
            user_agent='-',
            old='-',
            new='-',
            consumer='-',
            uid=str(TEST_UID),
            event='account_modification',
        )
        for logger in self.family_statbox, self.account_modification_log:
            logger.bind_entry(
                'family_info_modification',
                event='family_info_modification',
                ip='127.0.0.1',
                consumer='-',
                _exclude=['uid'],
            )

    def test_delete_account(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'karma': 100,
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
        })
        acc.is_enabled = True
        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.person.gender = Gender.Male
        acc.person.birthday = Birthday(1901, 6, 15)
        acc.person.display_name = DisplayName('Name', 'fb', 1)
        acc.person.default_avatar = 'ava'
        acc.person.show_fio_in_public_name = True
        acc.password.set('qwerty', 21)

        acc.password.setup_password_changing_requirement(is_required=False)
        acc.hint.question = '?'
        acc.hint.answer = '!'

        acc.plus.enabled = True
        acc.plus.trial_used_ts = unixtime_to_datetime(1)
        acc.plus.subscription_stopped_ts = unixtime_to_datetime(2)
        acc.plus.subscription_expire_ts = unixtime_to_datetime(3)
        acc.plus.next_charge_ts = unixtime_to_datetime(4)
        acc.plus.ott_subscription = 'ott-subscription'
        acc.plus.family_role = 'family-role'
        acc.plus.cashback_enabled = True
        acc.plus.subscription_level = 2
        acc.plus.is_frozen = True
        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON
        acc.family_pay_enabled = 'eda,mail'

        difference = diff(acc, None)
        run_statbox(
            acc,
            None,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'deleted',
                    entity='account.disabled_status',
                    old='enabled',
                ),
                self.statbox.entry(
                    'rm_alias',
                    type=str(ANT['portal']),
                ),
                self.statbox.entry(
                    'deleted',
                    entity='account.family_pay.enabled',
                    old='eda,mail',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.firstname',
                    old='fname',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.lastname',
                    old='lname',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.language',
                    old='RU',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.country',
                    old='RU',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.gender',
                    old='m',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.birthday',
                    old='1901-06-15',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.display_name',
                    old='s:1:fb:Name',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.default_avatar',
                    old='ava',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.show_fio_in_public_name',
                    old='1',
                    new='-',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='person.fullname',
                    old='fname lname',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='password.encrypted',
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'deleted',
                    entity='password.encoding_version',
                    old='1',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='password.quality',
                    old='21',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='hint.question',
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'deleted',
                    entity='hint.answer',
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'frodo_karma',
                    old='100',
                    new='-',
                ),
                self.statbox.entry('rm_subscription', sid='8'),
                self.statbox.entry(
                    'deleted',
                    entity='plus.enabled',
                    old='1',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.trial_used_ts',
                    old=unixtime_to_statbox_datetime(1),
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.subscription_stopped_ts',
                    old=unixtime_to_statbox_datetime(2),
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.subscription_expire_ts',
                    old=unixtime_to_statbox_datetime(3),
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.next_charge_ts',
                    old=unixtime_to_statbox_datetime(4),
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.ott_subscription',
                    old='ott-subscription',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.family_role',
                    old='family-role',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.cashback_enabled',
                    old='1',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.subscription_level',
                    old='2',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.is_frozen',
                    old='1',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='plus.subscriber_state',
                    old=TEST_PLUS_SUBSCRIBER_STATE1_JSON,
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'deleted',
                entity='account.disabled_status',
                old='enabled',
            ),
            self.statbox.entry(
                'rm_alias',
                type=str(ANT['portal']),
            ),
            self.statbox.entry(
                'deleted',
                entity='person.firstname',
                old='fname',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.lastname',
                old='lname',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.language',
                old='RU',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.country',
                old='RU',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.gender',
                old='m',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.birthday',
                old='1901-06-15',
            ),
            self.statbox.entry(
                'deleted',
                entity='person.fullname',
                old='fname lname',
            ),
            self.statbox.entry('rm_subscription', sid='8'),
        ])

    def test_run_statbox_no_runner(self):
        """ValueError в run_statbox, если тип модели не поддерживается и явно не передан runner."""
        unsupported_model = PhonenumberAlias()
        difference = diff(unsupported_model, None)

        with assert_raises(ValueError):
            run_statbox(
                unsupported_model,
                None,
                difference,
                TEST_ENVIRONMENT,
                {},
            )

    def test_created_domain(self):
        domain = Domain(id=1, domain='doma.in')
        difference = diff(None, domain)
        run_statbox(
            None,
            domain,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'domain_modification',
                    domain_id='1',
                    entity='domain_name',
                    old='-',
                    new='doma.in',
                    operation='created',
                ),
                self.statbox.entry(
                    'domain_modification',
                    domain_id='1',
                    entity='domain_id',
                    old='-',
                    new='1',
                    operation='created',
                ),
            ],
            with_account_modification=False,
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_delete_domain(self):
        domain = Domain(id=1, domain='doma.in')
        difference = diff(domain, None)
        run_statbox(
            domain,
            None,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'domain_modification',
                    domain_id='1',
                    entity='domain_name',
                    old='doma.in',
                    new='-',
                    operation='deleted',
                ),
                self.statbox.entry(
                    'domain_modification',
                    domain_id='1',
                    entity='domain_id',
                    old='1',
                    new='-',
                    operation='deleted',
                ),
            ],
            with_account_modification=False,
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_delete_account_with_sid_based_aliases(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
        })
        acc.phonenumber_alias = PhonenumberAlias(acc, number=TEST_PHONE_NUMBER)
        acc.yandexoid_alias = YandexoidAlias(acc, login=acc.login)
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@galatasaray.net')

        difference = diff(acc, None)
        run_statbox(
            acc,
            None,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals([
            self.statbox.entry('rm_alias', type=str(ANT['portal'])),
            self.statbox.entry('rm_alias', type=str(ANT['phonenumber'])),
            self.statbox.entry('rm_subscription', sid='8'),
            self.statbox.entry('rm_subscription', sid='61'),
            self.statbox.entry('rm_subscription', sid='65'),
            self.statbox.entry('rm_subscription', sid='669'),
        ])

    def test_delete_account_with_altdomain_no_sid(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
        })
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@kinopoisk.ru')

        difference = diff(acc, None)
        run_statbox(
            acc,
            None,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals([
            self.statbox.entry('rm_alias', type=str(ANT['portal'])),
            self.statbox.entry('rm_subscription', sid='8'),
            self.statbox.entry('rm_alias', type=str(ANT['altdomain']), domain_id='2'),
        ])

    def test_delete_account_with_phones(self):

        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
            'phones': {
                TEST_PHONE_DICT['id']: TEST_PHONE_DICT,
            },
        })
        acc.parse({
            'phones.secure': TEST_PHONE_DICT['id'],
        })

        difference = diff(acc, None)

        run_statbox(
            acc,
            None,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry('rm_alias', type=str(ANT['portal'])),
                self.statbox.entry(
                    'deleted',
                    entity='phones.secure',
                    old=TEST_PHONE_NUMBER.masked_format_for_statbox,
                    new='-',
                    old_entity_id=str(TEST_PHONE_DICT['id']),
                    new_entity_id='-',
                ),
                self.statbox.entry('rm_subscription', sid='8'),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('rm_alias', type=str(ANT['portal'])),
            self.statbox.entry(
                'deleted',
                entity='phones.secure',
                old=TEST_PHONE_NUMBER.e164,
                new='-',
                old_entity_id=str(TEST_PHONE_DICT['id']),
                new_entity_id='-',
            ),
            self.statbox.entry('rm_subscription', sid='8'),
        ])

    def test_delete_account_with_new_aliases(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({
            'subscriptions': {
                8: {
                    'sid': 8,
                    'login': TEST_ALIAS,
                },
            },
        })
        acc.lite_alias = LiteAlias(acc, email=acc.login + '@kinopoisk.ru')
        acc.pdd_alias = PddAlias(acc, email='test@okna.ru')
        acc.phonish_alias = PhonishAlias(acc, login='phne-test')
        acc.neophonish_alias = NeophonishAlias(acc, alias='nphne-test')
        acc.mailish_alias = MailishAlias(acc, mailish_id='some-string')
        acc.kinopoisk_alias = KinopoiskAlias(acc, alias='100500')
        acc.uber_alias = UberAlias(acc, uber_id='uber.1')
        acc.yambot_alias = YambotAlias(acc, alias='yambot-bot')
        acc.kolonkish_alias = KolonkishAlias(acc, alias='kolonkish-123')
        acc.public_id_alias = PublicIdAlias(acc, alias='public_id')
        acc.domain = PartialPddDomain().parse({
            'domid': 42,
            'domain': 'okna.ru',
        })

        difference = diff(acc, None)
        run_statbox(
            acc,
            None,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry('rm_alias', type=str(ANT['portal'])),
                self.statbox.entry('rm_alias', type=str(ANT['pdd'])),
                self.statbox.entry('rm_alias', type=str(ANT['lite'])),
                self.statbox.entry('rm_alias', type=str(ANT['phonish'])),
                self.statbox.entry('rm_alias', type=str(ANT['neophonish'])),
                self.statbox.entry('rm_alias', type=str(ANT['mailish'])),
                self.statbox.entry('rm_alias', type=str(ANT['kinopoisk'])),
                self.statbox.entry('rm_alias', type=str(ANT['uber'])),
                self.statbox.entry('rm_alias', type=str(ANT['yambot'])),
                self.statbox.entry('rm_alias', type=str(ANT['kolonkish'])),
                self.statbox.entry('rm_alias', type=str(ANT['public_id'])),
                self.statbox.entry(
                    'deleted',
                    entity='domain_name',
                    old='okna.ru',
                ),
                self.statbox.entry(
                    'deleted',
                    entity='domain_id',
                    old='42',
                ),
                self.statbox.entry('rm_subscription', sid='8'),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('rm_alias', type=str(ANT['portal'])),
            self.statbox.entry('rm_alias', type=str(ANT['pdd'])),
            self.statbox.entry('rm_alias', type=str(ANT['lite'])),
            self.statbox.entry('rm_alias', type=str(ANT['phonish'])),
            self.statbox.entry('rm_alias', type=str(ANT['neophonish'])),
            self.statbox.entry('rm_alias', type=str(ANT['mailish'])),
            self.statbox.entry('rm_alias', type=str(ANT['kinopoisk'])),
            self.statbox.entry('rm_alias', type=str(ANT['uber'])),
            self.statbox.entry('rm_alias', type=str(ANT['yambot'])),
            self.statbox.entry('rm_alias', type=str(ANT['kolonkish'])),
            self.statbox.entry('rm_alias', type=str(ANT['public_id'])),
            self.statbox.entry('rm_subscription', sid='8'),
        ])

    def test_create_plus(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.plus.enabled = True
        acc.plus.trial_used_ts = unixtime_to_datetime(1)
        acc.plus.subscription_stopped_ts = unixtime_to_datetime(2)
        acc.plus.subscription_expire_ts = unixtime_to_datetime(3)
        acc.plus.next_charge_ts = unixtime_to_datetime(4)
        acc.plus.ott_subscription = 'ott-subscription'
        acc.plus.family_role = 'family-role'
        acc.plus.cashback_enabled = True
        acc.plus.subscription_level = 2
        acc.plus.is_frozen = True
        acc.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        difference = diff(None, acc)

        run_statbox(
            None,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
                self.statbox.entry('created', entity='plus.enabled', old='-', new='1'),
                self.statbox.entry(
                    'created',
                    entity='plus.trial_used_ts',
                    old='-',
                    new=unixtime_to_statbox_datetime(1),
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.subscription_stopped_ts',
                    old='-',
                    new=unixtime_to_statbox_datetime(2),
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.subscription_expire_ts',
                    old='-',
                    new=unixtime_to_statbox_datetime(3),
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.next_charge_ts',
                    old='-',
                    new=unixtime_to_statbox_datetime(4),
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.ott_subscription',
                    old='-',
                    new='ott-subscription',
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.family_role',
                    old='-',
                    new='family-role',
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.cashback_enabled',
                    old='-',
                    new='1',
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.subscription_level',
                    old='-',
                    new='2',
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.is_frozen',
                    old='-',
                    new='1',
                ),
                self.statbox.entry(
                    'created',
                    entity='plus.subscriber_state',
                    old='-',
                    new=TEST_PLUS_SUBSCRIBER_STATE1_JSON,
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
        ])

    def test_create_takeout_extract(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.takeout.extract_in_progress_since = unixtime_to_datetime(1)

        difference = diff(None, acc)

        run_statbox(
            None,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
                self.statbox.entry(
                    'created',
                    entity='takeout.extract_in_progress_since',
                    old='-',
                    new=unixtime_to_statbox_datetime(1),
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
        ])

    def test_create_personal_data(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse(
            {
                'karma': 100,
                'subscriptions': {
                    8: {
                        'sid': 8,
                        'login': TEST_ALIAS,
                    },
                },
            },
        )
        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.person.gender = Gender.Male
        acc.person.birthday = Birthday(1901, 6, 15)
        acc.person.display_name = DisplayName('Name', 'fb', 1)
        acc.person.default_avatar = 'ava'
        acc.person.show_fio_in_public_name = True
        acc.password.set('qwerty', 21)
        acc.password.setup_password_changing_requirement(is_required=False)
        acc.hint.question = '?'
        acc.hint.answer = '!'
        acc.user_defined_login = TEST_USER_DEFINED_LOGIN
        acc.user_defined_public_id = TEST_USER_DEFINED_PUBLIC_ID
        difference = diff(None, acc)
        run_statbox(
            None,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_equals(
            [
                self.statbox.entry('created', entity='user_defined_login', old='-', new=TEST_USER_DEFINED_LOGIN),
                self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
                self.statbox.entry('created', entity='account.user_defined_public_id', old='-', new=TEST_USER_DEFINED_PUBLIC_ID),
                self.statbox.entry('created', entity='person.firstname', old='-', new='fname'),
                self.statbox.entry('created', entity='person.lastname', old='-', new='lname'),
                self.statbox.entry('created', entity='person.language', old='-', new='RU'),
                self.statbox.entry('created', entity='person.country', old='-', new='RU'),
                self.statbox.entry('created', entity='person.gender', old='-', new='m'),
                self.statbox.entry('created', entity='person.birthday', old='-', new='1901-06-15'),
                self.statbox.entry('created', entity='person.display_name', old='-', new='s:1:fb:Name'),
                self.statbox.entry('created', entity='person.default_avatar', old='-', new='ava'),
                self.statbox.entry('created', entity='person.show_fio_in_public_name', old='-', new='1'),
                self.statbox.entry('created', entity='person.fullname', old='-', new='fname lname'),
                self.statbox.entry('created', entity='password.encrypted', _exclude=['old', 'new']),
                self.statbox.entry('created', entity='password.encoding_version', old='-', new='1'),
                self.statbox.entry('created', entity='password.quality', old='-', new='21'),
                self.statbox.entry('created', entity='hint.question', _exclude=['old', 'new']),
                self.statbox.entry('created', entity='hint.answer', _exclude=['old', 'new']),
                self.statbox.entry('frodo_karma'),
                self.statbox.entry('add_subscription', sid='8'),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('created', entity='user_defined_login', old='-', new=TEST_USER_DEFINED_LOGIN),
            self.statbox.entry('add_alias', type=str(ANT['portal']), value=TEST_ALIAS),
            self.statbox.entry('created', entity='person.firstname', old='-', new='fname'),
            self.statbox.entry('created', entity='person.lastname', old='-', new='lname'),
            self.statbox.entry('created', entity='person.language', old='-', new='RU'),
            self.statbox.entry('created', entity='person.country', old='-', new='RU'),
            self.statbox.entry('created', entity='person.gender', old='-', new='m'),
            self.statbox.entry('created', entity='person.birthday', old='-', new='1901-06-15'),
            self.statbox.entry('created', entity='person.fullname', old='-', new='fname lname'),
            self.statbox.entry('add_subscription', sid='8'),
        ])

    def test_create_personal_data_for_pdd(self):
        """
        Проверяем, что для пользователя ПДД в statbox пишется
        логин с закодированным в punycode-доменом, равно как и
        есть запись о самом домене.
        """
        acc = default_account(
            uid=TEST_PDD_UID,
            alias_type='pdd',
            alias=TEST_ALIAS,
        ).parse({
            'domain': u'тест.ру',
            'karma': 100,
        })

        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.person.gender = Gender.Male
        acc.person.birthday = Birthday(1901, 6, 15)
        acc.password.set('qwerty', 21)
        acc.hint.question = '?'
        acc.hint.answer = '!'
        difference = diff(None, acc)

        run_statbox(
            None,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'add_alias',
                    type=str(ANT['pdd']),
                    uid=str(TEST_PDD_UID),
                    value=TEST_ALIAS,
                ),
                self.statbox.entry(
                    'created',
                    entity='person.firstname',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='fname',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.lastname',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='lname',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.language',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='RU',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.country',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='RU',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.gender',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='m',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.birthday',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='1901-06-15',
                ),
                self.statbox.entry(
                    'created',
                    entity='person.fullname',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='fname lname',
                ),
                self.statbox.entry(
                    'created',
                    entity='domain_name',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='xn--e1aybc.xn--p1ag',
                ),
                self.statbox.entry(
                    'created',
                    entity='password.encrypted',
                    uid=str(TEST_PDD_UID),
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'created',
                    entity='password.encoding_version',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='1',
                ),
                self.statbox.entry(
                    'created',
                    entity='password.quality',
                    uid=str(TEST_PDD_UID),
                    old='-',
                    new='21',
                ),
                self.statbox.entry(
                    'created',
                    entity='hint.question',
                    uid=str(TEST_PDD_UID),
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'created',
                    entity='hint.answer',
                    uid=str(TEST_PDD_UID),
                    _exclude=['old', 'new'],
                ),
                self.statbox.entry(
                    'frodo_karma',
                    login=u'%s@тест.ру' % TEST_ALIAS,
                    uid=str(TEST_PDD_UID),
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'add_alias',
                type=str(ANT['pdd']),
                uid=str(TEST_PDD_UID),
                value=TEST_ALIAS,
            ),
            self.statbox.entry(
                'created',
                entity='person.firstname',
                uid=str(TEST_PDD_UID),
                old='-',
                new='fname',
            ),
            self.statbox.entry(
                'created',
                entity='person.lastname',
                uid=str(TEST_PDD_UID),
                old='-',
                new='lname',
            ),
            self.statbox.entry(
                'created',
                entity='person.language',
                uid=str(TEST_PDD_UID),
                old='-',
                new='RU',
            ),
            self.statbox.entry(
                'created',
                entity='person.country',
                uid=str(TEST_PDD_UID),
                old='-',
                new='RU',
            ),
            self.statbox.entry(
                'created',
                entity='person.gender',
                uid=str(TEST_PDD_UID),
                old='-',
                new='m',
            ),
            self.statbox.entry(
                'created',
                entity='person.birthday',
                uid=str(TEST_PDD_UID),
                old='-',
                new='1901-06-15',
            ),
            self.statbox.entry(
                'created',
                entity='person.fullname',
                uid=str(TEST_PDD_UID),
                old='-',
                new='fname lname',
            ),
        ])

    def test_update_personal_data(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.person.firstname = '.'
        acc.person.lastname = '.'
        acc.person.language = '.'
        acc.person.country = '.'
        acc.person.gender = Gender.Male
        acc.person.birthday = Birthday(1901, 6, 15)
        acc.person.display_name = DisplayName('Name', 'fb', 1)
        acc.person.default_avatar = 'ava'
        acc.password.set('qwerty', 21)
        acc.hint.question = '.'
        acc.hint.answer = '.'

        snapshot = acc.snapshot()
        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.person.gender = Gender.Female
        acc.person.birthday = Birthday(1999, 8, 9)
        acc.person.display_name = DisplayName('New Name', 'fb', 1)
        acc.person.default_avatar = 'new_ava'
        acc.password.set('qwertyy', 22)
        with settings_context(BLACKBOX_URL='http://bb'), FakeBlackbox() as blackbox, FakeTvmCredentialsManager() as tvm:
            tvm.set_data(fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                },
            ))
            blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash='5:hash'),
            )
            acc.password.set('qwertyy', 22, version=5, get_hash_from_blackbox=True)
        acc.password.setup_password_changing_requirement(changing_reason='2')

        acc.hint.question = '?'
        acc.hint.answer = '!'
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('updated', entity='person.firstname', old='.', new='fname'),
                self.statbox.entry('updated', entity='person.lastname', old='.', new='lname'),
                self.statbox.entry('updated', entity='person.language', old='.', new='RU'),
                self.statbox.entry('updated', entity='person.country', old='.', new='RU'),
                self.statbox.entry('updated', entity='person.gender', old='m', new='f'),
                self.statbox.entry('updated', entity='person.birthday', old='1901-06-15', new='1999-08-09'),
                self.statbox.entry('updated', entity='person.display_name', old='s:1:fb:Name', new='s:1:fb:New Name'),
                self.statbox.entry('updated', entity='person.default_avatar', old='ava', new='new_ava'),
                self.statbox.entry('updated', entity='person.fullname', old='. .', new='fname lname'),
                self.statbox.entry('updated', entity='password.encrypted', _exclude=['old', 'new']),
                self.statbox.entry('updated', entity='password.encoding_version', old='1', new='5'),
                self.statbox.entry('updated', entity='password.quality', old='21', new='22'),
                self.statbox.entry('created', entity='password.is_changing_required', old='-', new='2'),
                self.statbox.entry('updated', entity='hint.question', _exclude=['old', 'new']),
                self.statbox.entry('updated', entity='hint.answer', _exclude=['old', 'new']),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('updated', entity='person.firstname', old='.', new='fname'),
            self.statbox.entry('updated', entity='person.lastname', old='.', new='lname'),
            self.statbox.entry('updated', entity='person.language', old='.', new='RU'),
            self.statbox.entry('updated', entity='person.country', old='.', new='RU'),
            self.statbox.entry('updated', entity='person.gender', old='m', new='f'),
            self.statbox.entry('updated', entity='person.birthday', old='1901-06-15', new='1999-08-09'),
            self.statbox.entry('updated', entity='person.fullname', old='. .', new='fname lname'),
        ])

    def test_change_show_fio_in_public_name(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.person.show_fio_in_public_name = None

        snapshot = acc.snapshot()

        acc.person.show_fio_in_public_name = True

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'created',
                    entity='person.show_fio_in_public_name',
                    old='-',
                    new='1',
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_change_ott_subscription_to_empty(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.plus.ott_subscription = 'not-empty'

        snapshot = acc.snapshot()

        acc.plus.ott_subscription = ''

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'deleted',
                    entity='plus.ott_subscription',
                    old='not-empty',
                    new='-',
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_change_plus_family_role_to_empty(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.plus.family_role = 'not-empty'

        snapshot = acc.snapshot()

        acc.plus.family_role = ''

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'deleted',
                    entity='plus.family_role',
                    old='not-empty',
                    new='-',
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_change_plus_timestamps_to_zero(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.plus.enabled = True
        acc.plus.trial_used_ts = unixtime_to_datetime(1)
        acc.plus.subscription_stopped_ts = unixtime_to_datetime(2)
        acc.plus.subscription_expire_ts = unixtime_to_datetime(3)
        acc.plus.next_charge_ts = unixtime_to_datetime(4)
        snapshot = acc.snapshot()

        acc.plus.trial_used_ts = unixtime_to_datetime(0)
        acc.plus.subscription_stopped_ts = unixtime_to_datetime(0)
        acc.plus.subscription_expire_ts = unixtime_to_datetime(0)
        acc.plus.next_charge_ts = unixtime_to_datetime(0)

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='plus.trial_used_ts',
                    old=unixtime_to_statbox_datetime(1),
                    new='-',
                ),
                self.statbox.entry(
                    'updated',
                    entity='plus.subscription_stopped_ts',
                    old=unixtime_to_statbox_datetime(2),
                    new='-',
                ),
                self.statbox.entry(
                    'updated',
                    entity='plus.subscription_expire_ts',
                    old=unixtime_to_statbox_datetime(3),
                    new='-',
                ),
                self.statbox.entry(
                    'updated',
                    entity='plus.next_charge_ts',
                    old=unixtime_to_statbox_datetime(4),
                    new='-',
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_change_personal_data_from_null_to_empty(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.person.firstname = ''
        acc.person.lastname = ''
        acc.person.language = ''
        acc.person.country = ''
        acc.person.birthday = None
        acc.person.gender = None
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written([])

    def test_delete_personal_data(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.person.gender = Gender.Male
        acc.person.birthday = Birthday(1901, 6, 15)
        acc.person.display_name = DisplayName('Name', 'fb', 1)
        acc.person.default_avatar = 'ava'
        acc.hint.question = '?'
        acc.hint.answer = '!'
        snapshot = acc.snapshot()
        acc.person.firstname = None
        acc.person.lastname = None
        acc.person.language = None
        acc.person.country = None
        acc.person.gender = None
        acc.person.birthday = None
        acc.person.display_name = None
        acc.person.default_avatar = None
        acc.hint.question = None
        acc.hint.answer = None
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('deleted', entity='person.firstname', old='fname', new='-'),
                self.statbox.entry('deleted', entity='person.lastname', old='lname', new='-'),
                self.statbox.entry('deleted', entity='person.language', old='RU', new='-'),
                self.statbox.entry('deleted', entity='person.country', old='RU', new='-'),
                self.statbox.entry('deleted', entity='person.gender', old='m', new='-'),
                self.statbox.entry('deleted', entity='person.birthday', old='1901-06-15', new='-'),
                self.statbox.entry('deleted', entity='person.display_name', old='s:1:fb:Name', new='-'),
                self.statbox.entry('deleted', entity='person.default_avatar', old='ava', new='-'),
                self.statbox.entry('deleted', entity='person.fullname', old='fname lname', new='-'),
                self.statbox.entry('deleted', entity='hint.question', _exclude=['old', 'new']),
                self.statbox.entry('deleted', entity='hint.answer', _exclude=['old', 'new']),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('deleted', entity='person.firstname', old='fname', new='-'),
            self.statbox.entry('deleted', entity='person.lastname', old='lname', new='-'),
            self.statbox.entry('deleted', entity='person.language', old='RU', new='-'),
            self.statbox.entry('deleted', entity='person.country', old='RU', new='-'),
            self.statbox.entry('deleted', entity='person.gender', old='m', new='-'),
            self.statbox.entry('deleted', entity='person.birthday', old='1901-06-15', new='-'),
            self.statbox.entry('deleted', entity='person.fullname', old='fname lname', new='-'),
        ])

    def test_mixed_personal_data(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.person.firstname = 'fname'
        acc.person.lastname = 'lname'
        acc.person.language = 'EN'
        acc.person.country = 'GB'
        snapshot = acc.snapshot()
        acc.person.firstname = None
        acc.person.lastname = None
        acc.person.language = 'RU'
        acc.person.country = 'RU'
        acc.hint.question = '?'
        acc.hint.answer = '!'
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('deleted', entity='person.firstname', old='fname', new='-'),
                self.statbox.entry('deleted', entity='person.lastname', old='lname', new='-'),
                self.statbox.entry('updated', entity='person.language', old='EN', new='RU'),
                self.statbox.entry('updated', entity='person.country', old='GB', new='RU'),
                self.statbox.entry('deleted', entity='person.fullname', old='fname lname', new='-'),
                self.statbox.entry('created', entity='hint.question', _exclude=['old', 'new']),
                self.statbox.entry('created', entity='hint.answer', _exclude=['old', 'new']),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry('deleted', entity='person.firstname', old='fname', new='-'),
            self.statbox.entry('deleted', entity='person.lastname', old='lname', new='-'),
            self.statbox.entry('updated', entity='person.language', old='EN', new='RU'),
            self.statbox.entry('updated', entity='person.country', old='GB', new='RU'),
            self.statbox.entry('deleted', entity='person.fullname', old='fname lname', new='-'),
        ])

    def test_subscribe(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({'subscriptions': {2: {'sid': 2, 'suid': 1}}})
        snapshot = acc.snapshot()
        subscribe(acc, Subscription(acc).parse({'sid': '8'}))
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('add_subscription', sid='8'),
            ],
        )

    def test_subscribe_sid_2(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({'subscriptions': {8: {'sid': 8}}})
        snapshot = acc.snapshot()
        subscribe(acc, Subscription(acc).parse({'sid': '2', 'suid': '1'}))
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('add_subscription', sid='2', suid='1'),
            ],
        )

    def test_subscribe_alias_sids(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.yandexoid_alias = YandexoidAlias(acc, login=acc.login)
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@galatasaray.net')
        acc.phonenumber_alias = PhonenumberAlias(acc, number=TEST_PHONE_NUMBER)
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('add_phonenumber_alias'),
                self.statbox.entry('add_subscription', sid='61'),
                self.statbox.entry('add_subscription', sid='65'),
                self.statbox.entry('add_subscription', sid='669'),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'add_phonenumber_alias',
                value=TEST_PHONE_NUMBER.digital,
            ),
            self.statbox.entry('add_subscription', sid='61'),
            self.statbox.entry('add_subscription', sid='65'),
            self.statbox.entry('add_subscription', sid='669'),
        ])

    def test_add_mailish_alias(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.mailish_alias = MailishAlias(acc, mailish_id=TEST_ALIAS)
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'add_mailish_alias',
                    value=TEST_ALIAS,
                ),
            ],
        )

    def test_add_altdomain_alias_without_subscription(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@kinopoisk.ru')
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'add_alias',
                    type=str(ANT['altdomain']),
                    domain_id='2',
                ),
            ],
        )

    def test_pdd_alias_add_multiple_login(self):
        acc = default_account(
            uid=TEST_PDD_UID,
            alias_type='pdd',
            alias=TEST_ALIAS,
        ).parse({
            'domain': u'тест.ру',
            'karma': 100,
        })
        snapshot = acc.snapshot()

        acc.pdd_alias.additional_logins.add('alias')
        acc.pdd_alias.additional_logins.add('alias2')

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'add_pddalias',
                    login='alias',
                    uid=str(TEST_PDD_UID),
                ),
                self.statbox.entry(
                    'add_pddalias',
                    login='alias2',
                    uid=str(TEST_PDD_UID),
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_pdd_alias_rm_multiple_logins(self):
        acc = default_account(
            uid=TEST_PDD_UID,
            alias_type='pdd',
            alias=TEST_ALIAS,
        ).parse({
            'domain': u'test.ru',
            'karma': 100,
            'aliases': {
                str(ANT['pddalias']): [
                    'alias1@test.ru',
                    'alias2@test.ru',
                ],
            },
        })
        snapshot = acc.snapshot()

        acc.pdd_alias.additional_logins.remove('alias1')
        acc.pdd_alias.additional_logins.remove('alias2')

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'rm_pddalias',
                    login='alias1',
                    uid=str(TEST_PDD_UID),
                ),
                self.statbox.entry(
                    'rm_pddalias',
                    login='alias2',
                    uid=str(TEST_PDD_UID),
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])

    def test_unsubscribe(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({'subscriptions': {8: {'sid': 8}}})
        snapshot = acc.snapshot()
        unsubscribe(acc, 8)
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('rm_subscription', sid='8'),
            ],
        )

    def test_unsubscribe_sid_2(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({'subscriptions': {2: {'sid': 2, 'suid': 1}}})
        snapshot = acc.snapshot()
        unsubscribe(acc, 2)
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('rm_subscription', sid='2', suid='1'),
            ],
        )

    def test_unsubscribe_alias_sids(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.yandexoid_alias = YandexoidAlias(acc, login=acc.login)
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@galatasaray.net')
        acc.phonenumber_alias = PhonenumberAlias(acc, number=TEST_PHONE_NUMBER)
        snapshot = acc.snapshot()
        acc.yandexoid_alias = None
        acc.altdomain_alias = None
        acc.phonenumber_alias = None
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('rm_alias', type=str(ANT['phonenumber'])),
                self.statbox.entry('rm_subscription', sid='61'),
                self.statbox.entry('rm_subscription', sid='65'),
                self.statbox.entry('rm_subscription', sid='669'),
            ],
        )

    def test_change_mailish_alias(self):
        acc = default_account(uid=TEST_UID, alias=TEST_EMAIL, alias_type='mailish')
        snapshot = acc.snapshot()
        acc.mailish_alias.mailish_id = TEST_ALIAS
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'add_mailish_alias',
                    operation='updated',
                    old=TEST_EMAIL,
                    new=TEST_ALIAS,
                ),
            ],
        )

    def test_remove_altdomain_alias_without_subscription(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.altdomain_alias = AltDomainAlias(acc, login=acc.login + '@kinopoisk.ru')
        snapshot = acc.snapshot()
        acc.altdomain_alias = None
        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry('rm_alias', type=str(ANT['altdomain']), domain_id='2'),
            ],
        )

    def test_account_global_logout_updated(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.global_logout_datetime = OLD_LOGOUT_DATETIME
        snapshot = acc.snapshot()
        acc.global_logout_datetime = NEW_LOGOUT_DATETIME

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.global_logout_datetime',
                    old=OLD_LOGOUT_DATETIME,
                    new=NEW_LOGOUT_DATETIME,
                ),
            ],
        )

    def test_account_global_logout_created(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.global_logout_datetime = NEW_LOGOUT_DATETIME

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'created',
                    entity='account.global_logout_datetime',
                    old='-',
                    new=NEW_LOGOUT_DATETIME,
                ),
            ],
        )

    def test_account_logout_updated(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.web_sessions_revoked_at = OLD_LOGOUT_DATETIME
        acc.app_passwords_revoked_at = OLD_LOGOUT_DATETIME
        acc.tokens_revoked_at = OLD_LOGOUT_DATETIME
        snapshot = acc.snapshot()
        acc.web_sessions_revoked_at = NEW_LOGOUT_DATETIME
        acc.app_passwords_revoked_at = NEW_LOGOUT_DATETIME
        acc.tokens_revoked_at = NEW_LOGOUT_DATETIME

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.revoker.tokens',
                    old=OLD_LOGOUT_DATETIME,
                    new=NEW_LOGOUT_DATETIME,
                ),
                self.statbox.entry(
                    'updated',
                    entity='account.revoker.web_sessions',
                    old=OLD_LOGOUT_DATETIME,
                    new=NEW_LOGOUT_DATETIME,
                ),
                self.statbox.entry(
                    'updated',
                    entity='account.revoker.app_passwords',
                    old=OLD_LOGOUT_DATETIME,
                    new=NEW_LOGOUT_DATETIME,
                ),
            ],
        )

    def test_account_logout_created(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = acc.snapshot()
        acc.web_sessions_revoked_at = NEW_LOGOUT_DATETIME
        acc.app_passwords_revoked_at = NEW_LOGOUT_DATETIME
        acc.tokens_revoked_at = NEW_LOGOUT_DATETIME

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'created',
                    entity='account.revoker.tokens',
                    old='-',
                    new=NEW_LOGOUT_DATETIME,
                ),
                self.statbox.entry(
                    'created',
                    entity='account.revoker.web_sessions',
                    old='-',
                    new=NEW_LOGOUT_DATETIME,
                ),
                self.statbox.entry(
                    'created',
                    entity='account.revoker.app_passwords',
                    old='-',
                    new=NEW_LOGOUT_DATETIME,
                ),
            ],
        )

    def test_account_disabled(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.is_enabled = True
        snapshot = acc.snapshot()
        acc.is_enabled = False

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.disabled_status',
                    old='enabled',
                    new='disabled',
                ),
            ],
        )

    def test_account_reenabled(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.disabled_status = ACCOUNT_DISABLED_ON_DELETION
        snapshot = acc.snapshot()
        acc.is_enabled = True

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.disabled_status',
                    old='disabled_on_deletion',
                    new='enabled',
                ),
            ],
        )

    def test_mail_status(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        acc.mail_status = MAIL_STATUS_ACTIVE
        snapshot = acc.snapshot()
        acc.mail_status = MAIL_STATUS_FROZEN

        difference = diff(snapshot, acc)
        run_statbox(
            snapshot,
            acc,
            difference,
            TEST_ENVIRONMENT,
            {
                'action': 'value1',
                'name2': 'value2',
            },
        )

        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.mail_status',
                    old='active',
                    new='frozen',
                ),
            ],
        )

    def test_account_emails_add_email(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        old = acc.snapshot()
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
            'native': True,
        })

        acc.emails.add(email)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'added',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_native='1',
                new=mask_email_for_statbox(TEST_EMAIL),
                old='-',
                is_suitable_for_restore='0',
            ),
        ])
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'added',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_native='1',
                new=TEST_EMAIL,
                old='-',
                is_suitable_for_restore='0',
            )
        ])

    def test_account_emails_add_restore_email(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        old = acc.snapshot()
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
            'confirmed': datetime_to_integer_unixtime(TEST_TIME),
            'native': False,
            'rpop': False,
            'unsafe': False,
            'silent': False,
        })

        acc.emails.add(email)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'added',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                new=mask_email_for_statbox(TEST_EMAIL),
                old='-',
                is_suitable_for_restore='1',
                is_unsafe='0',
                is_rpop='0',
                is_native='0',
                is_silent='0',
                confirmed_at=TEST_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            ),
        ])
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'added',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                new=TEST_EMAIL,
                old='-',
                is_suitable_for_restore='1',
                is_unsafe='0',
                is_rpop='0',
                is_native='0',
                is_silent='0',
                confirmed_at=TEST_TIME.strftime('%Y-%m-%d %H:%M:%S'),
            ),
        ])

    def test_account_emails_remove_email(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
        })
        acc.emails.add(email)

        old = acc.snapshot()
        acc.emails.pop(email.address)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'deleted',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                old=mask_email_for_statbox(TEST_EMAIL),
                new='-',
                is_suitable_for_restore='0',
            ),
        ])
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'deleted',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                old=TEST_EMAIL,
                new='-',
                is_suitable_for_restore='0',
            ),
        ])

    def test_account_emails_remove_email_set_none(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
        })
        acc.emails.add(email)

        s1 = acc.snapshot()
        acc.emails = None

        run_statbox(
            s1,
            acc,
            diff(s1, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'deleted',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                old=mask_email_for_statbox(TEST_EMAIL),
                new='-',
                is_suitable_for_restore='0',
            ),
        ])
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'deleted',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                old=TEST_EMAIL,
                new='-',
                is_suitable_for_restore='0',
            ),
        ])

    def test_account_emails_update_email(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
            'bound': 12345,
        })
        acc.emails.add(email)
        old = acc.snapshot()

        email = acc.emails[TEST_EMAIL]
        email.is_rpop = True
        email.is_unsafe = False
        email.created_at = 123
        email.bound_at = None
        email.address = TEST_EMAIL2

        diff(old.emails, acc.emails)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'updated',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_rpop='1',
                is_unsafe='0',
                bound_at='-',
                created_at='123',
                old=mask_email_for_statbox(TEST_EMAIL),
                new=mask_email_for_statbox(TEST_EMAIL2),
                is_suitable_for_restore='0',
            ),
        ])
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'updated',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_rpop='1',
                is_unsafe='0',
                bound_at='-',
                created_at='123',
                old=TEST_EMAIL,
                new=TEST_EMAIL2,
                is_suitable_for_restore='0',
            ),
        ])

    def test_account_emails_update_email_to_restore(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
            'bound': datetime_to_integer_unixtime(TEST_TIME),
            'confirmed': datetime_to_integer_unixtime(TEST_TIME),
            'native': False,
            'rpop': False,
            'unsafe': True,
            'silent': False,
        })
        acc.emails.add(email)
        old = acc.snapshot()

        email = acc.emails[TEST_EMAIL]
        email.is_unsafe = False

        diff(old.emails, acc.emails)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'updated',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_unsafe='0',
                new=mask_email_for_statbox(TEST_EMAIL),
                old=mask_email_for_statbox(TEST_EMAIL),
                is_suitable_for_restore='1',
            ),
        ])

    def test_account_emails_add_multiple_emails(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        old = acc.snapshot()
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
        })
        email2 = Email().parse({
            'id': TEST_EMAIL_ID + 1,
            'address': TEST_EMAIL2,
        })
        # Этот e-mail должен быть проигнорирован, т.к. у него нет ID
        old_email = Email().parse({
            'address': 'old@email.ru',
        })

        acc.emails.add(email)
        acc.emails.add(email2)
        acc.emails.add(old_email)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        assert_that(
            self.statbox.get_entries(),
            contains_inanyorder(
                self.statbox.entry(
                    'added',
                    email_id=str(TEST_EMAIL_ID),
                    entity='account.emails',
                    old='-',
                    new=mask_email_for_statbox(TEST_EMAIL),
                    is_suitable_for_restore='0',
                ),
                self.statbox.entry(
                    'added',
                    email_id=str(TEST_EMAIL_ID + 1),
                    entity='account.emails',
                    old='-',
                    new=mask_email_for_statbox(TEST_EMAIL2),
                    is_suitable_for_restore='0',
                ),
            ),
        ),

    def test_account_emails_remove_multiple_emails(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_EMAIL,
        })
        email2 = Email().parse({
            'id': TEST_EMAIL_ID + 1,
            'address': TEST_EMAIL2,
        })

        acc.emails.add(email)
        acc.emails.add(email2)

        old = acc.snapshot()
        acc.emails.pop(email.address)
        acc.emails.pop(email2.address)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        assert_that(
            self.statbox.get_entries(),
            contains_inanyorder(
                self.statbox.entry(
                    'deleted',
                    email_id=str(TEST_EMAIL_ID),
                    entity='account.emails',
                    old=mask_email_for_statbox(TEST_EMAIL),
                    new='-',
                    is_suitable_for_restore='0',
                ),
                self.statbox.entry(
                    'deleted',
                    email_id=str(TEST_EMAIL_ID + 1),
                    entity='account.emails',
                    old=mask_email_for_statbox(TEST_EMAIL2),
                    new='-',
                    is_suitable_for_restore='0',
                ),
            ),
        )

    def test_account_emails_add_cyrillic_email(self):
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        old = acc.snapshot()
        email = Email().parse({
            'id': TEST_EMAIL_ID,
            'address': TEST_CYRILLIC_EMAIL,
        })

        acc.emails.add(email)

        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written([
            self.statbox.entry(
                'added',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                old='-',
                new=mask_email_for_statbox(TEST_CYRILLIC_EMAIL),
                is_suitable_for_restore='0',
            ),
        ])

    def change_account_flag_attr(self, attribute, blackbox_attribute_name, before, after):
        params = {}
        if before is not None:
            params[blackbox_attribute_name] = '1' if before else '0'
        acc = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse(params)
        old = acc.snapshot()

        temp_obj = acc
        for attr_key in attribute.split('.')[:-1]:
            temp_obj = getattr(temp_obj, attr_key)
        temp_obj.__dict__[attribute.split('.')[-1]] = after
        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    @parameterized.expand(
        [
            ('enable_app_password', 'enable_app_password', 'account.enable_app_password'),
            ('magic_link_login_forbidden', 'account.magic_link_login_forbidden', 'account.magic_link_login_forbidden'),
            ('qr_code_login_forbidden', 'account.qr_code_login_forbidden', 'account.qr_code_login_forbidden'),
            ('sms_code_login_forbidden', 'account.sms_code_login_forbidden', 'account.sms_code_login_forbidden'),
            ('takeout.subscription', 'takeout.subscription', 'takeout.subscription'),
            ('sms_2fa_on', 'account.sms_2fa_on', 'account.sms_2fa_on'),
            ('personal_data_public_access_allowed', 'account.personal_data_public_access_allowed', 'account.personal_data_public_access_allowed'),
            ('personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed', 'account.personal_data_third_party_processing_allowed'),
        ]
    )
    def test_account_flag_attribute_change_state(self, model_field_name, blackbox_attribute_name, statbox_entity_name):
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=None, after=True)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=None, after=False)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=False, after=True)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=True, after=False)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=None, after=None)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=False, after=False)
        self.change_account_flag_attr(attribute=model_field_name, blackbox_attribute_name=blackbox_attribute_name, before=True, after=True)
        self._assert_statbox_has_written(
            [
                self.statbox.entry(  # before=None, after=True
                    'created',
                    old='-',
                    entity=statbox_entity_name,
                    new='1',
                ),
                self.statbox.entry(  # before=None, after=False
                    'created',
                    old='-',
                    entity=statbox_entity_name,
                    new='0',
                ),
                self.statbox.entry(  # before=False, after=True
                    'updated',
                    old='0',
                    entity=statbox_entity_name,
                    new='1',
                ),
                self.statbox.entry(  # before=True, after=False
                    'updated',
                    old='1',
                    entity=statbox_entity_name,
                    new='0',
                ),
                # no messages:
                # before = None, after = None
                # before=False, after=False
                # before=True, after=True
            ],
        )

    def test_change_account_unsubscribed_from_maillists(self):
        acc = default_account(uid=TEST_UID).parse({})
        old = acc.snapshot()

        acc.unsubscribed_from_maillists = UnsubscriptionList('1,2,3')
        run_statbox(
            old,
            acc,
            diff(old, acc),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )
        self._assert_statbox_has_written(
            [
                self.statbox.entry(
                    'updated',
                    entity='account.unsubscribed_from_maillists',
                    old='',
                    new='1,2,3',
                ),
            ],
        )

    def test_create_family(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID)
        difference = diff(None, family)
        run_statbox(
            None,
            family,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='admin_uid',
                    old='-',
                    new=str(TEST_UID),
                    operation='created',
                ),
            ),
        ])

    def test_create_family_with_members(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID)
        member1 = FamilyMember(uid=TEST_UID, parent=family)
        member2 = FamilyMember(uid=EXTRA_UID, parent=family)
        family.members = {
            member1.uid: member1,
            member2.uid: member2,
        }
        difference = diff(None, family)
        run_statbox(
            None,
            family,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='admin_uid',
                    old='-',
                    new=str(TEST_UID),
                    operation='created',
                ),
            ),
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(EXTRA_UID),
                    old='-',
                    attribute='members.%s.uid' % EXTRA_UID,
                    new=str(EXTRA_UID),
                    operation='created',
                ),
            ),
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID),
                    old='-',
                    attribute='members.%s.uid' % TEST_UID,
                    new=str(TEST_UID),
                    operation='created',
                ),
            ),
        ])

    def test_delete_family(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID)
        difference = diff(family, None)
        run_statbox(
            family,
            None,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='admin_uid',
                    new='-',
                    old=str(TEST_UID),
                    operation='deleted',
                ),
            ),
        ])

    def test_delete_family_with_members(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID)
        member1 = FamilyMember(uid=TEST_UID, parent=family)
        member2 = FamilyMember(uid=EXTRA_UID, parent=family)
        family.members = {
            member1.uid: member1,
            member2.uid: member2,
        }
        difference = diff(family, None)
        run_statbox(
            family,
            None,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='admin_uid',
                    new='-',
                    old=str(TEST_UID),
                    operation='deleted',
                ),
            ),
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(EXTRA_UID),
                    new='-',
                    attribute='members.%s.uid' % EXTRA_UID,
                    old=str(EXTRA_UID),
                    operation='deleted',
                ),
            ),
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID),
                    new='-',
                    attribute='members.%s.uid' % TEST_UID,
                    old=str(TEST_UID),
                    operation='deleted',
                ),
            ),
        ])

    def test_delete_family_member(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID)
        member1 = FamilyMember(uid=TEST_UID, parent=family)

        snap = family.snapshot()
        family.members = {member1.uid: member1}
        difference = diff(family, snap)

        run_statbox(
            family,
            snap,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID),
                    new='-',
                    attribute='members.%s.uid' % TEST_UID,
                    old=str(TEST_UID),
                    operation='deleted',
                ),
            ),
        ])

    def test_add_family_member(self):
        family = FamilyInfo(_family_id=TEST_FAMILY_ID, admin_uid=TEST_UID,
                            members=[])
        member1 = FamilyMember(uid=TEST_UID, parent=family)
        family.members = {}
        snap = family.snapshot()
        family.members = {member1.uid: member1}
        difference = diff(snap, family)

        run_statbox(
            snap,
            family,
            difference,
            TEST_ENVIRONMENT,
            {'action': 'value1'},
        )
        self._assert_family_statbox([
            (
                'family_info_modification',
                dict(
                    family_id='f%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID),
                    new=str(TEST_UID),
                    attribute='members.%s.uid' % TEST_UID,
                    old='-',
                    operation='created',
                ),
            ),
        ])

    def test_delete_kiddish(self):
        account = Account()
        account.uid = TEST_UID
        account.kiddish_alias = KiddishAlias(alias=TEST_KIDDISH_LOGIN1)
        account.family_info = AccountFamilyInfo(family_id=TEST_FAMILY_ID)

        difference = diff(account, None)
        run_statbox(
            account,
            None,
            difference,
            TEST_ENVIRONMENT,
            events=dict(action='action'),
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'rm_alias',
                    type=str(EavSerializer.alias_name_to_type('kiddish')),
                ),
                self.statbox.entry(
                    'family_info_modification',
                    attribute='uid',
                    entity='kid',
                    entity_id=str(TEST_UID),
                    family_id='f%s' % TEST_FAMILY_ID,
                    new='-',
                    old=str(TEST_UID),
                    operation='deleted',
                    uid=str(TEST_UID),
                ),
            ],
            with_account_modification=False,
        )
        self.account_modification_infosec_log.assert_has_written([
            self.statbox.entry(
                'rm_alias',
                type=str(EavSerializer.alias_name_to_type('kiddish')),
            ),
        ])

    def test_scholar_create(self):
        account = Account()
        account.uid = TEST_UID
        account.scholar_alias = ScholarAlias(alias=TEST_SCHOLAR_LOGIN1)

        run_statbox(
            None,
            account,
            diff(None, account),
            TEST_ENVIRONMENT,
            events=dict(action='action'),
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'add_alias',
                    type=str(EavSerializer.alias_name_to_type('scholar')),
                    value=TEST_SCHOLAR_LOGIN1,
                ),
            ],
        )

    def test_scholar_delete(self):
        account = Account()
        account.uid = TEST_UID
        account.scholar_alias = ScholarAlias(alias=TEST_SCHOLAR_LOGIN1)

        run_statbox(
            account,
            None,
            diff(account, None),
            TEST_ENVIRONMENT,
            events=dict(action='action'),
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'rm_alias',
                    type=str(EavSerializer.alias_name_to_type('scholar')),
                ),
            ],
        )

    def test_add_forced_change_suspension(self):
        acc = Account()
        acc.uid = TEST_UID
        acc.password = Password()
        acc.password.setup_password_changing_requirement(changing_reason=PASSWORD_CHANGING_REASON_PWNED)
        s1 = acc.snapshot()

        acc.password.setup_password_changing_requirement(is_required=False)
        run_statbox(
            s1,
            acc,
            diff(s1, acc),
            TEST_ENVIRONMENT,
            events=dict(action='action'),
        )

        self._assert_statbox_equals(
            [
                self.statbox.entry(
                    'deleted',
                    entity='password.is_changing_required',
                    old=str(PASSWORD_CHANGING_REASON_PWNED),
                    new='-',
                ),
                self.statbox.entry(
                    'created',
                    entity='password.pwn_forced_changing_suspended_at',
                    old='-',
                    new=DatetimeNow(convert_to_datetime=True),
                ),
            ],
        )
        self.account_modification_infosec_log.assert_has_written([])


class TestPhonenumberAlias(TestCase):
    def setUp(self):
        self.statbox = StatboxLoggerFaker()
        self.statbox.start()
        self._setup_statbox_templates()

    def tearDown(self):
        self.statbox.stop()
        del self.statbox

    def _setup_statbox_templates(self):
        self.statbox.bind_entry(
            'base',
            uid=str(TEST_UID),
            consumer='-',
            user_agent='-',
            ip='127.0.0.1',
        )

        self.statbox.bind_entry(
            'add_subscription',
            _inherit_from=['subscriptions', 'base'],
            operation='added',
        ),
        self.statbox.bind_entry(
            'rm_subscription',
            _inherit_from=['subscriptions', 'base'],
            operation='removed',
        )
        self.statbox.bind_entry(
            'phonenumber_alias_search_enabled',
            _inherit_from=['phonenumber_alias_search_enabled', 'base'],
        )
        self.statbox.bind_entry(
            'phonenumber_alias_search_disabled',
            _inherit_from=['phonenumber_alias_search_enabled', 'base'],
            old='1',
            new='0',
        )
        self.statbox.bind_entry(
            'add_phonenumber_alias',
            _inherit_from=['aliases', 'base'],
            operation='added',
            type=str(ANT['phonenumber']),
        )
        self.statbox.bind_entry(
            'rm_phonenumber_alias',
            _inherit_from=['add_phonenumber_alias'],
            operation='removed',
        )
        self.statbox.bind_entry(
            'change_phonenumber_alias',
            _inherit_from=['add_phonenumber_alias'],
            operation='updated',
        )

    def _create_phonenumber_alias(self, **kwargs):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        snapshot = account.snapshot()
        account.phonenumber_alias = PhonenumberAlias(account, **kwargs)
        difference = diff(snapshot, account)
        run_statbox(
            snapshot,
            account,
            difference,
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def _remove_phonenumber_alias(self, **kwargs):
        with self._update_phonenumber_alias(**kwargs) as account:
            account.phonenumber_alias = None

    @contextmanager
    def _update_phonenumber_alias(self, **kwargs):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        account.phonenumber_alias = PhonenumberAlias(account, **kwargs)
        snapshot = account.snapshot()

        yield account

        run_statbox(
            snapshot,
            account,
            diff(snapshot, account),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def test_phonenumber_alias_add(self):
        self._create_phonenumber_alias(number=TEST_PHONE_NUMBER)
        self.statbox.assert_has_written([
            self.statbox.entry('add_phonenumber_alias'),
            self.statbox.entry('add_subscription', sid='65'),
        ])

    def test_phonenumber_alias_add__search_enabled(self):
        self._create_phonenumber_alias(
            number=TEST_PHONE_NUMBER,
            enable_search=True,
        )
        self.statbox.assert_has_written([
            self.statbox.entry('add_phonenumber_alias'),
            self.statbox.entry('add_subscription', sid='65'),
            self.statbox.entry('phonenumber_alias_search_enabled'),
        ])

    def test_phonenumber_alias_add__search_disabled(self):
        self._create_phonenumber_alias(
            number=TEST_PHONE_NUMBER,
            enable_search=False,
        )
        self.statbox.assert_has_written([
            self.statbox.entry('add_phonenumber_alias'),
            self.statbox.entry('add_subscription', sid='65'),
            self.statbox.entry('phonenumber_alias_search_disabled', old='-'),
        ])

    def test_phonenumber_alias_rm(self):
        self._remove_phonenumber_alias(number=TEST_PHONE_NUMBER)
        self.statbox.assert_has_written([
            self.statbox.entry('rm_phonenumber_alias'),
            self.statbox.entry('rm_subscription', sid='65'),
        ])

    def test_phonenumber_alias_rm__search_enabled(self):
        self._remove_phonenumber_alias(
            number=TEST_PHONE_NUMBER,
            enable_search=True,
        )
        self.statbox.assert_has_written([
            self.statbox.entry('rm_phonenumber_alias'),
            self.statbox.entry('rm_subscription', sid='65'),
        ])

    def test_phonenumber_alias_rm__search_disabled(self):
        self._remove_phonenumber_alias(
            number=TEST_PHONE_NUMBER,
            enable_search=False,
        )
        self.statbox.assert_has_written([
            self.statbox.entry('rm_phonenumber_alias'),
            self.statbox.entry('rm_subscription', sid='65'),
        ])

    def test_phonenumber_alias__turn_on_search(self):
        with self._update_phonenumber_alias(number=TEST_PHONE_NUMBER) as account:
            account.phonenumber_alias.enable_search = True

        self.statbox.assert_has_written([
            self.statbox.entry('phonenumber_alias_search_enabled'),
        ])

    def test_phonenumber_alias__turn_off_search(self):
        with self._update_phonenumber_alias(
            number=TEST_PHONE_NUMBER,
            enable_search=True,
        ) as account:
            account.phonenumber_alias.enable_search = False

        self.statbox.assert_has_written([
            self.statbox.entry(
                'phonenumber_alias_search_disabled',
                operation='updated',
                old='1',
            ),
        ])

    def test_phonenumber_alias__change_number(self):
        with self._update_phonenumber_alias(
            number=TEST_PHONE_NUMBER1,
        ) as account:
            account.phonenumber_alias.number = TEST_PHONE_NUMBER2

        # Подписка на 65-й сид сохранилась, поэтому ничего не пишем.
        self.statbox.assert_has_written([
            self.statbox.entry('change_phonenumber_alias'),
        ])


class TestPhonesStatboxation(TestCase):
    def setUp(self):
        self._statbox_faker = StatboxLoggerFaker()
        self._statbox_faker.start()
        self._account_modification_infosec_faker = AccountModificationInfosecLoggerFaker()
        self._account_modification_infosec_faker.start()

        base_log_template = {
            'uid': str(TEST_UID),
            'new': '-',
            'old': '-',
            'consumer': '-',
        }

        self._statbox_faker.bind_entry(
            'account_modification',
            **base_log_template
        )
        self._account_modification_infosec_faker.bind_entry(
            'account_modification',
            **base_log_template
        )

    def tearDown(self):
        self._account_modification_infosec_faker.stop()
        del self._account_modification_infosec_faker
        self._statbox_faker.stop()
        del self._statbox_faker

    def _build_account_with_phone(self, is_secure=False):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        kwargs = {
            'number': TEST_PHONE_NUMBER.e164,
            'bound': TEST_TIME,
            'confirmed': TEST_TIME,
            'existing_phone_id': TEST_PHONE_ID,
        }
        if is_secure:
            kwargs['secured'] = TEST_TIME
        phone = account.phones.create(**kwargs)
        if is_secure:
            account.phones.secure = phone
        return account, phone

    def _run_statbox(self, old, new):
        run_statbox(
            old,
            new,
            diff(old, new),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def test_create_secure_phone(self):
        account, phone = self._build_account_with_phone()
        snapshot = account.snapshot()
        phone.secured = TEST_TIME
        account.phones.secure = phone

        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='created',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id='-',
                new_entity_id=str(TEST_PHONE_ID),
            ),
        ])
        # self._account_modification_infosec_faker.assert_has_written([
        #     self._account_modification_infosec_faker.entry(
        #         'account_modification',
        #         entity='phones.secure',
        #         operation='created',
        #         new=TEST_PHONE_NUMBER.e164,
        #         old_entity_id='-',
        #         new_entity_id=str(TEST_PHONE_ID),
        #     ),
        # ])

    def test_delete_secure_phone(self):
        account, phone = self._build_account_with_phone(is_secure=True)
        snapshot = account.snapshot()
        account.phones.remove(phone)

        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='deleted',
                old=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id='-',
            ),
        ])

    def test_unsecurize_phone(self):
        account, phone = self._build_account_with_phone(is_secure=True)
        snapshot = account.snapshot()
        account.phones.secure = None
        phone.secured = None

        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='deleted',
                old=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id='-',
            ),
        ])

    def test_change_secure_phone(self):
        account, phone1 = self._build_account_with_phone(is_secure=True)
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            bound=TEST_TIME,
            confirmed=TEST_TIME,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()
        phone2.secured = TEST_TIME
        account.phones.secure = phone2
        phone1.secured = None

        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='updated',
                new=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                old=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id=str(TEST_PHONE_ID2),
            ),
        ])

    def test_start_replace_secure_phone__not_bound(self):
        account, phone1 = self._build_account_with_phone(is_secure=True)
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()

        ReplaceSecurePhoneWithNonboundPhoneOperation.create(
            phone_manager=account.phones,
            secure_phone_id=phone1.id,
            being_bound_phone_id=phone2.id,
            secure_code=TEST_CONFIRMATION_CODE1,
            being_bound_code=TEST_CONFIRMATION_CODE2,
            statbox=None,
        )
        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'base',
                action='phone_operation_created',
                operation_type='replace_secure_phone_with_nonbound_phone',
                being_bound_phone_id=str(TEST_PHONE_ID2),
                being_bound_number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                secure_phone_id=str(TEST_PHONE_ID),
                secure_number=TEST_PHONE_NUMBER.masked_format_for_statbox,
                uid=str(TEST_UID),
                ip='127.0.0.1',
                consumer='-',
                user_agent='-',
            ),
        ])

    def test_start_replace_secure_phone__bound(self):
        account, phone1 = self._build_account_with_phone(is_secure=True)
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            bound=TEST_TIME,
            confirmed=TEST_TIME,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()

        ReplaceSecurePhoneWithBoundPhoneOperation.create(
            phone_manager=account.phones,
            secure_phone_id=phone1.id,
            simple_phone_id=phone2.id,
            secure_code=TEST_CONFIRMATION_CODE1,
            simple_code=TEST_CONFIRMATION_CODE2,
            statbox=None,
        )
        self._run_statbox(snapshot, account)

        self._statbox_faker.assert_has_written([
            self._statbox_faker.entry(
                'base',
                action='phone_operation_created',
                operation_type='replace_secure_phone_with_bound_phone',
                simple_phone_id=str(TEST_PHONE_ID2),
                simple_number=TEST_PHONE_NUMBER2.masked_format_for_statbox,
                secure_phone_id=str(TEST_PHONE_ID),
                secure_number=TEST_PHONE_NUMBER.masked_format_for_statbox,
                uid=str(TEST_UID),
                ip='127.0.0.1',
                consumer='-',
                user_agent='-',
            ),
        ])


class TestPharma(TestCase):
    def setUp(self):
        self._faker = PharmaLoggerFaker()
        self._faker.start()

    def tearDown(self):
        self._faker.stop()
        del self._faker

    def _build_account_with_phone(self, is_secure=False):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        kwargs = {
            'number': TEST_PHONE_NUMBER.e164,
            'bound': TEST_TIME,
            'confirmed': TEST_TIME,
            'existing_phone_id': TEST_PHONE_ID,
        }
        if is_secure:
            kwargs['secured'] = TEST_TIME
        phone = account.phones.create(**kwargs)
        if is_secure:
            account.phones.secure = phone
        return account, phone

    def _run_pharma(self, old, new):
        run_pharma(
            old,
            new,
            diff(old, new),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def test_create_phone(self):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        snapshot = account.snapshot()
        account.phones.create(
            number=TEST_PHONE_NUMBER.e164,
            existing_phone_id=TEST_PHONE_ID,
        )

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([])

    def test_update_phone_number(self):
        account, phone = self._build_account_with_phone()
        snapshot = account.snapshot()
        phone.number = TEST_PHONE_NUMBER2

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'base',
                action='confirmed',
                phonenumber=TEST_PHONE_NUMBER2.digital,
                user_ip='127.0.0.1',
                user_agent='-',
                uid=str(TEST_UID),
            )
        ])

    def test_update_phone_confirmed(self):
        account, phone = self._build_account_with_phone()
        phone.admitted = TEST_TIME
        snapshot = account.snapshot()
        setattr(phone, 'confirmed', TEST_TIME + timedelta(seconds=1))

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'base',
                action='confirmed',
                phonenumber=TEST_PHONE_NUMBER.digital,
                user_ip='127.0.0.1',
                user_agent='-',
                uid=str(TEST_UID),
            )
        ])

    def test_update_phone_other_attributes(self):
        account, phone = self._build_account_with_phone()
        phone.admitted = TEST_TIME
        snapshot = account.snapshot()
        ATTRIBUTES = OrderedDict([
            ('bound', TEST_TIME + timedelta(seconds=2)),
            ('admitted', TEST_TIME + timedelta(seconds=4)),
        ])
        for attribute, new_value in ATTRIBUTES.items():
            setattr(phone, attribute, new_value)

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([])

    def test_delete_attributes(self):
        account, phone = self._build_account_with_phone()
        phone.admitted = TEST_TIME
        snapshot = account.snapshot()
        ATTRIBUTES = ['confirmed', 'bound', 'admitted']
        for attribute in ATTRIBUTES:
            setattr(phone, attribute, None)

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([])

    def test_delete_phone(self):
        account, phone = self._build_account_with_phone()
        phone.bound = None
        snapshot = account.snapshot()
        account.phones.remove(phone)

        self._run_pharma(snapshot, account)

        self._faker.assert_has_written([])


class TestPhonesCryptastatation(TestCase):
    def setUp(self):
        self._faker = CryptastatLoggerFaker()
        self._faker.start()

        self._faker.bind_entry(
            'account_modification',
            tskv_format='passport-sensitive-log',
            uid=str(TEST_UID),
            new='-',
            old='-',
            consumer='-',
        )

    def tearDown(self):
        self._faker.stop()
        del self._faker

    def _build_account_with_phone(self, is_secure=False):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        kwargs = {
            'number': TEST_PHONE_NUMBER.e164,
            'bound': TEST_TIME,
            'confirmed': TEST_TIME,
            'existing_phone_id': TEST_PHONE_ID,
        }
        if is_secure:
            kwargs['secured'] = TEST_TIME
        phone = account.phones.create(**kwargs)
        if is_secure:
            account.phones.secure = phone
        return account, phone

    def _run_cryptastat(self, old, new):
        run_cryptastat(
            old,
            new,
            diff(old, new),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def test_create_phone(self):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        snapshot = account.snapshot()
        account.phones.create(
            number=TEST_PHONE_NUMBER.e164,
            existing_phone_id=TEST_PHONE_ID,
        )

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='created',
                new=TEST_PHONE_NUMBER.e164,
            ),
        ])

    def test_create_phone_with_attributes(self):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        snapshot = account.snapshot()
        ATTRIBUTES = OrderedDict([
            ('number', TEST_PHONE_NUMBER.e164),
            ('confirmed', TEST_TIME + timedelta(seconds=1)),
            ('bound', TEST_TIME + timedelta(seconds=2)),
            ('secured', TEST_TIME + timedelta(seconds=3)),
            ('admitted', TEST_TIME + timedelta(seconds=4)),
        ])
        account.phones.create(
            existing_phone_id=TEST_PHONE_ID,
            **ATTRIBUTES
        )

        self._run_cryptastat(snapshot, account)

        entries = []
        for attribute, new_value in ATTRIBUTES.items():
            entries.append(
                self._faker.entry(
                    'account_modification',
                    entity='phone',
                    entity_id=str(TEST_PHONE_ID),
                    attribute=attribute,
                    operation='created',
                    new=str(new_value),
                ),
            )
        self._faker.assert_has_written(entries)

    def test_update_phone_with_attributes(self):
        account, phone = self._build_account_with_phone()
        phone.admitted = TEST_TIME
        snapshot = account.snapshot()
        ATTRIBUTES = OrderedDict([
            ('confirmed', TEST_TIME + timedelta(seconds=1)),
            ('bound', TEST_TIME + timedelta(seconds=2)),
            ('admitted', TEST_TIME + timedelta(seconds=4)),
        ])
        for attribute, new_value in ATTRIBUTES.items():
            setattr(phone, attribute, new_value)

        self._run_cryptastat(snapshot, account)

        entries = []
        for attribute, new_value in ATTRIBUTES.items():
            entries.append(
                self._faker.entry(
                    'account_modification',
                    entity='phone',
                    entity_id=str(TEST_PHONE_ID),
                    attribute=attribute,
                    operation='updated',
                    old=str(TEST_TIME),
                    new=str(new_value),
                ),
            )
        self._faker.assert_has_written(entries)

    def test_update_phone_number(self):
        account, phone = self._build_account_with_phone()
        snapshot = account.snapshot()
        phone.number = TEST_PHONE_NUMBER2

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='updated',
                old=TEST_PHONE_NUMBER.e164,
                new=TEST_PHONE_NUMBER2.e164,
            ),
        ])

    def test_delete_attributes(self):
        account, phone = self._build_account_with_phone()
        phone.admitted = TEST_TIME
        snapshot = account.snapshot()
        ATTRIBUTES = ['confirmed', 'bound', 'admitted']
        for attribute in ATTRIBUTES:
            setattr(phone, attribute, None)

        self._run_cryptastat(snapshot, account)

        entries = []
        for attribute in ATTRIBUTES:
            entries.append(
                self._faker.entry(
                    'account_modification',
                    entity='phone',
                    entity_id=str(TEST_PHONE_ID),
                    attribute=attribute,
                    operation='deleted',
                    old=str(TEST_TIME),
                    new='-',
                ),
            )
        self._faker.assert_has_written(entries)

    def test_delete_phone(self):
        account, phone = self._build_account_with_phone()
        phone.bound = None
        snapshot = account.snapshot()
        account.phones.remove(phone)

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
                new='-',
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='confirmed',
                operation='deleted',
                old=str(TEST_TIME),
                new='-',
            ),
        ])

    def test_delete_many_phones(self):
        account, phone1 = self._build_account_with_phone()
        phone1.bound = phone1.confirmed = None
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()
        account.phones.remove(phone1)
        account.phones.remove(phone2)

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
                new='-',
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID2),
                attribute='number',
                operation='deleted',
                old=TEST_PHONE_NUMBER2.e164,
                new='-',
            ),
        ])

    def test_create_update_and_delete_attributes(self):
        account, phone = self._build_account_with_phone()
        snapshot = account.snapshot()
        phone.admitted = TEST_TIME
        phone.confirmed = TEST_TIME + timedelta(seconds=1)
        phone.bound = None

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='confirmed',
                operation='updated',
                old=str(TEST_TIME),
                new=str(TEST_TIME + timedelta(seconds=1)),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='bound',
                operation='deleted',
                old=str(TEST_TIME),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='admitted',
                operation='created',
                new=str(TEST_TIME),
            ),
        ])

    def test_create_many_phones(self):
        account = default_account(uid=TEST_UID, alias=TEST_ALIAS).parse({})
        snapshot = account.snapshot()
        account.phones.create(
            number=TEST_PHONE_NUMBER.e164,
            existing_phone_id=TEST_PHONE_ID,
        )
        account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            existing_phone_id=TEST_PHONE_ID2,
        )

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='created',
                new=TEST_PHONE_NUMBER.e164,
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID2),
                attribute='number',
                operation='created',
                new=TEST_PHONE_NUMBER2.e164,
            ),
        ])

    def test_update_many_phones(self):
        account, phone1 = self._build_account_with_phone()
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            confirmed=TEST_TIME,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()
        phone1.confirmed = TEST_TIME + timedelta(seconds=1)
        phone2.confirmed = TEST_TIME + timedelta(seconds=2)

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='confirmed',
                operation='updated',
                old=str(TEST_TIME),
                new=str(TEST_TIME + timedelta(seconds=1)),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID2),
                attribute='confirmed',
                operation='updated',
                old=str(TEST_TIME),
                new=str(TEST_TIME + timedelta(seconds=2)),
            ),
        ])

    def test_create_update_and_delete_phones(self):
        account, phone1 = self._build_account_with_phone()
        phone1.confirmed = phone1.bound = None
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            confirmed=TEST_TIME,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()
        account.phones.create(
            number=TEST_PHONE_NUMBER3.e164,
            existing_phone_id=TEST_PHONE_ID3,
        )
        account.phones.remove(phone1)
        phone2.confirmed = TEST_TIME + timedelta(seconds=1)

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID3),
                attribute='number',
                operation='created',
                new=TEST_PHONE_NUMBER3.e164,
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID2),
                attribute='confirmed',
                operation='updated',
                old=str(TEST_TIME),
                new=str(TEST_TIME + timedelta(seconds=1)),
            ),
        ])

    def test_securify_phone(self):
        account, phone = self._build_account_with_phone()
        snapshot = account.snapshot()
        phone.secured = TEST_TIME
        account.phones.secure = phone

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='created',
                new=TEST_PHONE_NUMBER.e164,
                old_entity_id='-',
                new_entity_id=str(TEST_PHONE_ID),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='secured',
                operation='created',
                new=str(TEST_TIME),
            ),
        ])

    def test_delete_secure_phone(self):
        account, phone = self._build_account_with_phone(is_secure=True)
        snapshot = account.snapshot()
        account.phones.remove(phone)

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id='-',
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='number',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='confirmed',
                operation='deleted',
                old=str(TEST_TIME),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='bound',
                operation='deleted',
                old=str(TEST_TIME),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='secured',
                operation='deleted',
                old=str(TEST_TIME),
            ),
        ])

    def test_unsecurize_phone(self):
        account, phone = self._build_account_with_phone(is_secure=True)
        snapshot = account.snapshot()
        account.phones.secure = None
        phone.secured = None

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='deleted',
                old=TEST_PHONE_NUMBER.e164,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id='-',
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='secured',
                operation='deleted',
                old=str(TEST_TIME),
            ),
        ])

    def test_change_secure_phone(self):
        account, phone1 = self._build_account_with_phone(is_secure=True)
        phone2 = account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            bound=TEST_TIME,
            confirmed=TEST_TIME,
            existing_phone_id=TEST_PHONE_ID2,
        )
        snapshot = account.snapshot()
        phone2.secured = TEST_TIME
        account.phones.secure = phone2
        phone1.secured = None

        self._run_cryptastat(snapshot, account)

        self._faker.assert_has_written([
            self._faker.entry(
                'account_modification',
                entity='phones.secure',
                operation='updated',
                new=TEST_PHONE_NUMBER2.e164,
                old=TEST_PHONE_NUMBER.e164,
                old_entity_id=str(TEST_PHONE_ID),
                new_entity_id=str(TEST_PHONE_ID2),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID),
                attribute='secured',
                operation='deleted',
                old=str(TEST_TIME),
            ),
            self._faker.entry(
                'account_modification',
                entity='phone',
                entity_id=str(TEST_PHONE_ID2),
                attribute='secured',
                operation='created',
                new=str(TEST_TIME),
            ),
        ])


@with_settings_hosts()
class TestRun(TestCase):
    def setUp(self):
        self.statbox_logger = StatboxLoggerFaker()
        self.event_logger = EventLoggerFaker()
        self.db = FakeDB()

        self.patches = [
            self.statbox_logger,
            self.event_logger,
            self.db,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self.statbox_logger
        del self.event_logger
        del self.db

    def test_run_domain(self):
        domain = Domain(id=1, domain='doma.in')

        snapshot = domain.snapshot()

        domain.organization_name = u'Организация'

        run(
            snapshot,
            domain,
            diff(snapshot, domain),
            TEST_ENVIRONMENT,
            {'action': 'value'},
        )
        ok_(self.statbox_logger.write_handler_mock.called)

    def test_historydb_not_run(self):
        acc = default_account(uid=TEST_UID, alias='login')

        snapshot = acc.snapshot()
        acc.person.firstname = 'fname'
        run(
            snapshot, acc, diff(snapshot, acc),
            TEST_ENVIRONMENT,
            {'action': 'value1', 'name2': 'value2'},
            disable_history_db=True,
        )
        eq_(self.event_logger.events, [])
        ok_(self.statbox_logger.write_handler_mock.called)

    def test_retries(self):
        acc = default_account(uid=TEST_UID, alias='login')

        snapshot = acc.snapshot()
        acc.person.firstname = 'fname'

        safe_execute_wrapper = mock.Mock(wraps=safe_execute)
        with mock.patch('passport.backend.core.dbmanager.manager.safe_execute', safe_execute_wrapper):
            run(
                snapshot, acc, diff(snapshot, acc),
                TEST_ENVIRONMENT,
                {'action': 'value1', 'name2': 'value2'},
                disable_history_db=True,
                retries=1,
                with_low_timeout=True,
            )
        execute_engine = safe_execute_wrapper.call_args_list[0][0][0]
        execute_kwargs = safe_execute_wrapper.call_args_list[0][1]
        expected_engine = get_dbm('passportdbshard1')._master.select_engine(with_low_timeout=True)
        eq_(execute_engine, expected_engine)
        eq_(execute_kwargs['retries'], 1)
        eq_(self.event_logger.events, [])

    def test_historydb_external_events_not_written_with_empty_diff(self):
        """В случае пустого диффа внешние события не пишутся в HistoryDB"""
        acc = default_account()

        run(
            acc, acc, diff(acc, acc),
            Environment(),
            {'action': 'value1', 'field': 'value2'},
        )
        ok_(not self.statbox_logger.write_handler_mock.called)
        eq_(len(self.event_logger.events), 0)

    def test_historydb_forced_external_events_with_empty_diff(self):
        """В случае пустого диффа необходимо записать внешние события в HistoryDB при задании флага"""
        acc = default_account()

        run(
            acc, acc, diff(acc, acc),
            Environment(),
            {'action': 'value1', 'field': 'value2'},
            force_history_db_external_events=True,
        )
        ok_(not self.statbox_logger.write_handler_mock.called)
        eq_(len(self.event_logger.events), 2)
        action_event = self.event_logger.events[0]
        eq_(action_event.name, 'action')
        eq_(action_event.value, 'value1')
        field_event = self.event_logger.events[1]
        eq_(field_event.name, 'field')
        eq_(field_event.value, 'value2')

    def test_diff_updates_from_eav_propagated_to_historydb(self):
        acc = default_account().parse({
            'subscriptions': {
                8: {'login_rule': 2, 'sid': 8, 'login': 'login'},
            },
        })
        acc.password.set('test', 0, get_hash_from_blackbox=True, version=5)
        initial_diff = diff(None, acc)
        updated_diff = diff(None, acc)

        with settings_context(BLACKBOX_URL='http://bb'), FakeBlackbox() as blackbox, FakeTvmCredentialsManager() as tvm:
            tvm.set_data(fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                },
            ))
            blackbox.set_blackbox_response_value(
                'create_pwd_hash',
                blackbox_create_pwd_hash_response(password_hash='5:hash'),
            )
            # При вызове сериализатора дифф обновляется
            run(
                None, acc, updated_diff,
                TEST_ENVIRONMENT,
                {'action': 'value1', 'name2': 'value2'},
            )
        eq_(
            initial_diff.added['password'],
            {
                'update_datetime': DatetimeNow(),
                'quality': 0,
                'quality_version': 3,
            },
        )
        eq_(initial_diff.changed, {})
        eq_(
            updated_diff.added['password'],
            {
                'encrypted_password': u'hash',
                'quality_version': 3,
                'update_datetime': DatetimeNow(),
                'quality': 0,
                'encoding_version': 5,
            },
        )
        eq_(updated_diff.changed, {})
        initial_diff = fix_passport_login_rule(None, acc, initial_diff)
        eq_(
            dict(initial_diff.added, password=None),
            dict(updated_diff.added, password=None),
        )
        self.event_logger.assert_event_is_logged('info.password', '5:hash')


class TestScholarPassword(TestCase):
    def setUp(self):
        self.statbox = StatboxLoggerFaker()
        self.statbox.start()
        self.setup_statbox_templates()

    def tearDown(self):
        self.statbox.stop()
        del self.statbox

    def setup_statbox_templates(self):
        self.statbox.bind_entry(
            'base',
            uid=str(TEST_UID),
            consumer='-',
            user_agent='-',
            ip='127.0.0.1',
        )
        self.statbox.bind_entry(
            'account.scholar_password',
            _inherit_from=['base'],
            entity='account.scholar_password',
            event='account_modification',
        )

    def build_scholar_password(self, **kwargs):
        kwargs.setdefault('encoding_version', 1)
        kwargs.setdefault('encrypted_password', 'pwd')
        return ScholarPassword(parent=None, **kwargs)

    @contextmanager
    def update_scholar_password(self, old=Undefined):
        if old is Undefined:
            old = self.build_scholar_password()

        account = default_account(uid=TEST_UID, alias=TEST_ALIAS)
        if old is not None:
            account.scholar_password = old
            old.parent = account
        snapshot = account.snapshot()

        yield account

        run_statbox(
            snapshot,
            account,
            diff(snapshot, account),
            TEST_ENVIRONMENT,
            TEST_EVENTS,
        )

    def test_create(self):
        with self.update_scholar_password(old=None) as account:
            account.scholar_password = self.build_scholar_password()

        self.statbox.assert_has_written([self.statbox.entry('account.scholar_password', operation='created')])

    def test_change(self):
        with self.update_scholar_password() as account:
            account.scholar_password.encrypted_password = 'pwd2'

        self.statbox.assert_has_written([self.statbox.entry('account.scholar_password', operation='updated')])
