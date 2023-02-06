# -*- coding: utf-8 -*-

from base64 import b64encode
from datetime import datetime
from operator import attrgetter
from unittest import TestCase

from nose.tools import eq_
from nose_parameterized import parameterized
from passport.backend.core.differ.differ import diff
from passport.backend.core.env import Environment
from passport.backend.core.models.account import (
    Account,
    ACCOUNT_DISABLED_ON_DELETION,
    AccountDeletionOperation,
    MAIL_STATUS_FROZEN,
)
from passport.backend.core.models.alias import (
    AltDomainAlias,
    BankPhoneNumberAlias,
    KiddishAlias,
    KinopoiskAlias,
    KolonkishAlias,
    LiteAlias,
    MailishAlias,
    NeophonishAlias,
    PddAlias,
    PhonenumberAlias,
    PhonishAlias,
    PortalAlias,
    PublicIdAlias,
    ScholarAlias,
    SocialAlias,
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
from passport.backend.core.models.hint import Hint
from passport.backend.core.models.karma import Karma
from passport.backend.core.models.passman_recovery_key import PassManRecoveryKey
from passport.backend.core.models.password import (
    Password,
    PASSWORD_CHANGING_REASON_PWNED,
    ScholarPassword,
)
from passport.backend.core.models.person import (
    DisplayName,
    Person,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.models.plus import Plus
from passport.backend.core.models.rfc_totp_secret import RfcTotpSecret
from passport.backend.core.models.subscription import (
    Host,
    Subscription,
)
from passport.backend.core.models.takeout import Takeout
from passport.backend.core.models.totp_secret import TotpSecret
from passport.backend.core.models.webauthn import WebauthnCredential
from passport.backend.core.processor import (
    fix_passport_login_rule,
    run_historydb,
)
from passport.backend.core.serializers.logs import log_events
from passport.backend.core.serializers.logs.historydb.runner import HistorydbActionRunner
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_DATETIME1,
    TEST_KIDDISH_LOGIN1,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_SCHOLAR_LOGIN1,
)
from passport.backend.core.test.events import (
    EventLoggerFaker,
    EventLoggerTskvFaker,
)
from passport.backend.core.test.test_utils import (
    iterdiff,
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
    unixtime,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.core.types.gender import Gender
from passport.backend.core.types.mail_subscriptions import UnsubscriptionList
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.types.question import Question
from passport.backend.core.types.rfc_totp_secret import RfcTotpSecretType
from passport.backend.core.types.totp_secret import TotpSecretType
from passport.backend.core.undefined import Undefined
from passport.backend.utils.string import (
    always_str,
    smart_text,
)
from passport.backend.utils.time import (
    datetime_to_unixtime,
    unixtime_to_datetime,
)
import pytz
import six


TEST_UID = 11805675
TEST_UID_EXTRA = 2291676
TEST_PHONE_NUMBER = '+79251111111'
TEST_PHONE_ID = 123
TEST_PHONE_ID2 = 234

TEST_TIME = datetime(2001, 1, 2, 12, 34, 56)

TEST_CREATED_DT = datetime(2001, 1, 2, 12, 34, 56)
TEST_BOUND_DT = datetime(2002, 1, 2, 12, 34, 56)
TEST_CONFIRMED_DT = datetime(2003, 1, 2, 12, 34, 56)
TEST_ADMITTED_DT = datetime(2004, 1, 2, 12, 34, 56)
TEST_SECURED_DT = datetime(2005, 1, 2, 12, 34, 56)
TEST_PHONE_OPERATION_ID = 456
TEST_PHONE_OPERATION_ID2 = 567

TEST_PHONE_OPERATION_DATA = {
    'security_identity': int(TEST_PHONE_NUMBER),
    'type': 'bind',
    'started': datetime(2000, 1, 23, 12, 34, 56),
    'finished': datetime(2001, 1, 23, 12, 34, 56),
    'code_value': 'abcdefg',
    'code_checks_count': 2,
    'code_send_count': 1,
    'code_last_sent': datetime(2002, 1, 23, 12, 34, 56),
    'code_confirmed': datetime(2003, 1, 23, 12, 34, 56),
    'password_verified': datetime(2004, 1, 23, 12, 34, 56),
    'flags': PhoneOperationFlags(123),
    'phone_id2': 555,
}

TEST_PHONE_OPERATION_DATA2 = dict(
    TEST_PHONE_OPERATION_DATA,
    security_identity=TEST_PHONE_NUMBER2.digital,
)

TEST_YANDEXUID = u'test-yandexuid'
TEST_USER_IP = u'1.2.3.4'
TEST_USER_AGENT = u'curl'

TEST_PHONE = '+79030915478'

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
        'number': PhoneNumber.parse(TEST_PHONE_NUMBER).e164,
        'created': TEST_PHONE_ATTR_CREATED,
        'bound': TEST_PHONE_ATTR_BOUND,
        'confirmed': TEST_PHONE_ATTR_CONFIRMED,
        'admitted': TEST_PHONE_ATTR_ADMITTED,
        'secured': TEST_PHONE_ATTR_SECURED,
    },
    'operation': TEST_PHONE_OPERATION,
}

TEST_PASSMAN_KEY_ID = b'\xd1\x8a' * 16
TEST_PASSMAN_RECOVERY_KEY = b'\xd1\x8c' * 16

TEST_ENVIRONMENT = Environment(user_ip='127.0.0.1')

TEST_FAMILY_ID = 73

TEST_CREDENTIAL_EXTERNAL_ID = 'some-long-credential-id'
TEST_PUBLIC_KEY = 'some-long-public-key'
TEST_DEVICE_NAME = 'device-name'
TEST_RP_ID = 'rp-id'


class UnorderedCommaJoinedStringMatcher(object):
    def __init__(self, *parts):
        self.parts = sorted(parts)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.parts)

    def __eq__(self, other):
        return isinstance(other, six.string_types) and self.parts == sorted(other.split(','))


def to_unixtime_string(dt):
    return str(int(datetime_to_unixtime(dt)))


class HistorydbActionRunnerTestCase(TestCase):

    def test_action_fields(self):
        """Поля admin, comment, yandexuid записываются в событие action"""
        events = {
            'action': 'business',
            'admin': 'test-admin',
            'comment': 'the-comment',
        }
        runner = HistorydbActionRunner(events, TEST_UID, None, None, 'yandexuid', None)
        eq_(runner.admin, 'test-admin')
        eq_(runner.comment, 'the-comment')
        eq_(runner.yandexuid, 'yandexuid')
        eq_(runner.uid, TEST_UID)

        entry = runner.get_entry('action', 'business')
        eq_(entry.admin, 'test-admin')
        eq_(entry.comment, 'the-comment')
        eq_(entry.yandexuid, 'yandexuid')
        eq_(entry.uid, TEST_UID)

        entry = runner.get_entry('action', 'business', TEST_UID_EXTRA)
        eq_(entry.admin, 'test-admin')
        eq_(entry.comment, 'the-comment')
        eq_(entry.yandexuid, 'yandexuid')
        eq_(entry.uid, TEST_UID_EXTRA)

    def test_action_fields_in_another_event(self):
        """Поля admin, comment, yandexuid заполняются только для события с именем action"""
        events = {
            'param': 'value',
            'admin': 'test-admin',
            'comment': 'the-comment',
        }
        runner = HistorydbActionRunner(events, None, None, None, 'yandexuid', None)
        eq_(runner.admin, 'test-admin')
        eq_(runner.comment, 'the-comment')
        eq_(runner.yandexuid, 'yandexuid')

        entry = runner.get_entry('param', 'value')
        eq_(entry.admin, '')
        eq_(entry.comment, '')
        eq_(entry.yandexuid, '')

    def test_datetime(self):
        """
        Использует заданное время.
        """
        runner = HistorydbActionRunner({}, None, None, None, 'yandexuid', None, datetime_=TEST_TIME)
        eq_(runner.entry_time, TEST_TIME)

    def test_no_datetime(self):
        """
        Использует нынешнее время.
        """
        runner = HistorydbActionRunner({}, None, None, None, 'yandexuid', None)
        eq_(runner.entry_time, DatetimeNow())


class BaseTestEventSerializer(PassportTestCase):
    def setUp(self):
        super(BaseTestEventSerializer, self).setUp()
        self.account = Account().parse({})
        self.account.uid = TEST_UID
        self.account.password = Password(self.account)

    def eq_historydb_events_from_diff(self, modifying_function, expected_name_value):
        self._faker = EventLoggerFaker()
        self._faker_tskv = EventLoggerTskvFaker()
        self._faker.start()
        self._faker_tskv.start()
        if self.account is not None:
            s1 = self.account.snapshot()
        else:
            s1 = None
        modifying_function()
        if self.account is not None:
            s2 = self.account.snapshot()
        else:
            s2 = None
        run_historydb(
            s1,
            s2,
            fix_passport_login_rule(s1, s2, diff(s1, s2)),
            TEST_ENVIRONMENT,
            {},
            10,
        )
        self._faker.assert_events_are_logged(expected_name_value)
        self._faker_tskv.assert_events_are_logged(expected_name_value)
        self._faker.stop()
        self._faker_tskv.stop()
        del self._faker
        del self._faker_tskv


class TestAccountDeleteEventSerializer(BaseTestEventSerializer):

    def setUp(self):
        super(TestAccountDeleteEventSerializer, self).setUp()
        self.account.portal_alias = PortalAlias(
            self.account,
            login='login',
        )
        self.account.user_defined_login = 'login'
        self.runner = HistorydbActionRunner({}, None, None, None, None, None)

    def compare_events_on_deletion_diff(self, account, expected_names_and_values):
        s1 = account.snapshot()
        names_and_values = list(self.runner.serialize(s1, None, diff(s1, None)))
        iterdiff(eq_)(dict(names_and_values), expected_names_and_values)

    def test_delete_basic_account(self):
        self.compare_events_on_deletion_diff(
            self.account,
            {
                'info.login': u'login',
                'info.password': None,
                'info.password_quality': None,
                'info.password_update_time': None,
                'info.totp': 'disabled',
                'info.totp_update_time': None,
                'info.rfc_totp': 'disabled',
            },
        )

    def test_delete_with_pdd_domain(self):
        self.account.domain = PartialPddDomain(
            domain='test-domain.ru',
            id=123,
        )

        self.compare_events_on_deletion_diff(
            self.account,
            {
                'info.login': u'login',
                'info.password': None,
                'info.password_quality': None,
                'info.password_update_time': None,
                'info.domain_name': None,
                'info.domain_id': None,
                'info.totp': 'disabled',
                'info.totp_update_time': None,
                'info.rfc_totp': 'disabled',
            },
        )

    def test_delete_with_subscriptions(self):
        subscriptions = {
            3: {
                'login_rule': 1,
                'login': 'inkvi',
                'service': Service(sid=3),
                'suid': 27560013,
            },
            4: {
                'login_rule': 2,
                'login': 'bezh',
                'service': Service(sid=4),
                'suid': 1,
            },
            100: {
                'login_rule': 1,
                'login': u'bezh@мойдомен.рф',
                'service': Service(sid=100),
            },
        }

        self.account.subscriptions = {
            sid: Subscription(**record)
            for sid, record in six.iteritems(subscriptions)
        }

        self.compare_events_on_deletion_diff(
            self.account,
            {
                'info.login': u'login',
                'info.password': None,
                'info.password_quality': None,
                'info.password_update_time': None,
                'sid.rm': UnorderedCommaJoinedStringMatcher(u'4|bezh', u'3|inkvi', u'100|bezh@мойдомен.рф'),
                'info.totp': 'disabled',
                'info.totp_update_time': None,
                'info.rfc_totp': 'disabled',
            },
        )

    def test_delete_with_phones(self):
        self.account.parse({
            'phones': {
                TEST_PHONE_DICT['id']: TEST_PHONE_DICT,
            },
            'attributes': {
                'phones.secure': TEST_PHONE_DICT['id'],
            },
        })
        self.compare_events_on_deletion_diff(
            self.account,
            {
                'info.login': u'login',
                'info.password': None,
                'info.password_quality': None,
                'info.password_update_time': None,
                'info.totp': 'disabled',
                'info.totp_update_time': None,
                'info.rfc_totp': 'disabled',
                'phone.123.action': 'deleted',
                'phone.123.number': u'+79251111111',
                'phone.123.operation.1.action': 'deleted',
                'phone.123.operation.1.security_identity': u'1',
                'phone.123.operation.1.type': u'bind',
            },
        )

    def test_delete_with_aliases(self):
        phone = PhoneNumber.parse('+79030915478')

        self.account.pdd_alias = PddAlias(
            self.account,
            email='Test.Login@okna.ru',
        )
        self.account.domain = Domain(id=1, domain='okna.ru')

        self.account.portal_alias = PortalAlias(
            self.account,
            login='Test.Login',
        )
        self.account.social_alias = SocialAlias(
            self.account,
            login='uid-test',
        )
        self.account.lite_alias = LiteAlias(
            self.account,
            email='Test.Login@okna.ru',
        )
        self.account.mailish_alias = MailishAlias(
            self.account,
            mailish_id='Some-String',
        )
        self.account.kinopoisk_alias = KinopoiskAlias(
            self.account,
            alias='100500',
        )
        self.account.uber_alias = UberAlias(
            self.account,
            uber_id='uber-1',
        )
        self.account.yambot_alias = YambotAlias(
            self.account,
            alias='yambot-bot',
        )
        self.account.kolonkish_alias = KolonkishAlias(
            self.account,
            alias='kolonkish-123',
        )
        self.account.public_id_alias = PublicIdAlias(
            self.account,
            alias='public.id',
        )
        self.account.altdomain_alias = AltDomainAlias(
            self.account,
            login='Galatasaray.Login@galatasaray.net',
        )
        self.account.phonenumber_alias = PhonenumberAlias(self.account, number=phone)
        self.account.yandexoid_alias = YandexoidAlias(self.account, login='Yandexoid.Login')
        self.account.user_defined_login = 'Test.Login'
        self.account.user_defined_public_id = 'Test.Public.id'

        self.compare_events_on_deletion_diff(
            self.account,
            {
                'info.password': None,
                'info.password_quality': None,
                'info.password_update_time': None,
                'alias.altdomain.rm': u'1/galatasaray-login',
                'alias.phonenumber.rm': u'+7 903 091-54-78',
                'alias.public_id.rm': u'public.id',
                'alias.yandexoid.rm': u'Yandexoid.Login',
                'info.domain_id': None,
                'info.domain_name': None,
                'info.login': u'test-login',
                'info.login_wanted': u'Test.Login',
                'info.totp': 'disabled',
                'info.totp_update_time': None,
                'info.rfc_totp': 'disabled',
                'account.user_defined_public_id': None,
            },
        )

    def test_delete_kiddish_with_family(self):
        account = Account()
        account.uid = TEST_UID
        account.kiddish_alias = KiddishAlias(alias=TEST_KIDDISH_LOGIN1)
        account.family_info = AccountFamilyInfo(family_id=TEST_FAMILY_ID)

        self.compare_events_on_deletion_diff(
            account,
            {
                'family.f%s.family_kid' % TEST_FAMILY_ID: None,
                'info.login': TEST_KIDDISH_LOGIN1,
            },
        )

    def test_delete_scholar(self):
        account = Account()
        account.scholar_alias = ScholarAlias(alias=TEST_SCHOLAR_LOGIN1)
        account.scholar_password = ScholarPassword(
            encoding_version=1,
            encrypted_password='pwd',
            parent=account,
        )
        account.uid = TEST_UID

        self.compare_events_on_deletion_diff(
            account,
            {
                'info.login': smart_text(TEST_SCHOLAR_LOGIN1),
                'info.scholar_password': None,
            },
        )

    def test_delete_with_password_pwn_forced_changing_suspension_time(self):
        account = Account()
        account.password = Password()
        account.password.pwn_forced_changing_suspended_at = datetime.now()

        self.compare_events_on_deletion_diff(
            account,
            {
                'info.password': None,
                'info.password_pwn_forced_changing_suspension_time': None,
                'info.password_quality': None,
                'info.password_update_time': None,
            },
        )


class TestEventSerializer(BaseTestEventSerializer):

    def test_historydb_events_from_diff_for_pdd_domain(self):
        def change_domain():
            self.account.domain = PartialPddDomain(
                domain='test-domain.ru',
                id=123,
            )

        name_and_value = {
            'info.domain_name': 'test-domain.ru',
            'info.domain_id': '123',
        }

        self.eq_historydb_events_from_diff(change_domain, name_and_value)

    def test_historydb_events_from_diff_no_pdd_domain(self):
        self.account.domain = PartialPddDomain(
            domain='test-domain.ru',
            id=123,
        )

        def remove_domain():
            self.account.domain = None

        name_and_value = {}

        self.eq_historydb_events_from_diff(remove_domain, name_and_value)

    def test_historydb_events_from_diff_for_change_password(self):
        self.account.subscriptions = {
            8: Subscription(**{
                'login_rule': 1,
                'login': 'inkvi',
                'service': Service(sid=8),
                'suid': 27560013,
            }),
        }

        def change_pass():
            self.account.password.setup_password_changing_requirement()

        name_and_value = [{
            'name': 'sid.login_rule',
            'value': '8|5',
            'action': 'change',
            'uid': str(TEST_UID),
        }]

        self.eq_historydb_events_from_diff(change_pass, name_and_value)

    def test_historydb_events_from_diff_for_clear_password_changing_requirement(self):
        def clear_requirement():
            self.account.password.setup_password_changing_requirement(is_required=False)

        self.account.subscriptions = {
            8: Subscription(**{'login_rule': 5, 'login': 'c00per', 'service': Service(sid=8)}),
        }
        self.account.password.setup_password_changing_requirement()

        self.eq_historydb_events_from_diff(
            clear_requirement,
            {'sid.login_rule': '8|1'},
        )

    def test_historydb_events_from_diff_for_clear_password_changing_requirement_with_suspension(self):
        def clear_requirement():
            self.account.password.setup_password_changing_requirement(is_required=False)

        self.account.password.setup_password_changing_requirement(changing_reason=PASSWORD_CHANGING_REASON_PWNED)

        self.eq_historydb_events_from_diff(
            clear_requirement,
            {'info.password_pwn_forced_changing_suspension_time': TimeNow()},
        )

    def test_historydb_events_from_diff_for_change_password_update_datetime(self):
        def change_update_datetime():
            self.account.password.update_datetime = datetime.fromtimestamp(1000)

        name_and_value = {
            'info.password_update_time': '1000',
        }
        self.eq_historydb_events_from_diff(change_update_datetime, name_and_value)

    def test_historydb_events_from_diff_for_change_password_version(self):
        # Искуственный тест для проверки правила сериализатора
        password = self.account.password
        password.set('weak', 20, 'salt')

        def change_password_version():
            password.encoding_version = 10

        name_value = {
            'info.password': '10:$1$salt$S50SsPzK2tVeNfb0w..WW0',
        }

        self.eq_historydb_events_from_diff(change_password_version, name_value)

    def test_historydb_events_from_diff_for_change_password_hash_body(self):
        # Искуственный тест для проверки правила сериализатора
        password = self.account.password
        password.set('weak', 20, 'salt')

        def change():
            password.encrypted_password = 'hahash'

        name_value = {
            'info.password': '1:hahash',
        }

        self.eq_historydb_events_from_diff(change, name_value)

    def test_historydb_events_from_diff_for_scholar_password(self):
        password = ScholarPassword(
            encoding_version=1,
            encrypted_password='pwd',
            parent=self.account,
        )

        def create():
            self.account.scholar_alias = ScholarAlias(alias=TEST_SCHOLAR_LOGIN1)
            self.account.scholar_password = password

        self.eq_historydb_events_from_diff(
            create,
            {
                'alias.scholar.add': always_str(TEST_SCHOLAR_LOGIN1),
                'info.login': always_str(TEST_SCHOLAR_LOGIN1),
                'info.scholar_password': '1:pwd',
            },
        )

        def change():
            password.encoding_version = 2
            password.encrypted_password = 'pwd1'

        self.eq_historydb_events_from_diff(change, {'info.scholar_password': '2:pwd1'})

    def test_historydb_events_from_diff_for_subscriptions_add(self):
        def add_subs():
            host = Host(id=1)
            self.account.subscriptions = {
                2: Subscription(**{'login_rule': 1, 'login': 'maillogin', 'service': Service(sid=2), 'suid': 12344567}),
                3: Subscription(**{'login_rule': 1, 'login': 'inkvi', 'service': Service(sid=3), 'suid': 27560013}),
                8: Subscription(**{'login_rule': 1, 'login': 'c00per', 'service': Service(sid=8)}),
                4: Subscription(**{'login_rule': 2, 'login': 'bezh', 'service': Service(sid=4), 'suid': 275013}),
                42: Subscription(**{'login_rule': 2, 'login': 'bezh', 'service': Service(sid=42), 'host': host}),
                100: Subscription(**{'login_rule': 1, 'login': u'bezh@мойдомен.рф', 'service': Service(sid=100)}),
            }

        name_and_value = {
            'sid.add': UnorderedCommaJoinedStringMatcher('2|maillogin', '3|inkvi', '100|bezh@мойдомен.рф', '8|c00per', '42|bezh', '4|bezh'),
            'sid.wwwdgt_wmode': '1',
            'mail.add': '12344567',
        }
        self.eq_historydb_events_from_diff(add_subs, name_and_value)

    def test_historydb_events_from_diff_for_subscriptions_rm(self):
        """
        Тестируем как удаление обычной подписки, так и почтовой
        """
        self.account.subscriptions = {
            2: Subscription(
                **{
                    'parent': self.account,
                    'login_rule': 1,
                    'login': 'inkvi',
                    'suid': 27560013,
                    'service': Service(sid=2),
                }
            ),
            4: Subscription(**{
                'login_rule': 2,
                'login': 'bezh',
                'service': Service(sid=4),
                'suid': 275013,
            }),
        }

        def delete_subs():
            for sid in [2, 4]:
                del self.account.subscriptions[sid]

        name_and_value = {
            'sid.rm.info': '%s|%s|%s' % (self.account.uid, 'inkvi', 27560013),
            'sid.rm': '2|inkvi,4|bezh',
            'mail.rm': '27560013',
        }
        self.eq_historydb_events_from_diff(delete_subs, name_and_value)

    def test_historydb_events_from_diff_for_subscriptions_change(self):
        self.account.subscriptions = {
            2: Subscription(
                **{
                    'parent': self.account, 'login_rule': 1, 'login': 'maillogin', 'suid': 1234567,
                    'service': Service(sid=2),
                }
            ),
            6: Subscription(
                **{
                    'parent': self.account, 'login_rule': 1, 'login': 'inkvi', 'suid': 27560013,
                    'service': Service(sid=6), 'host': Host(id=1),
                }
            ),
            8: Subscription(**{'login_rule': 2, 'login': 'bezh', 'service': Service(sid=8), 'suid': 275013}),
            42: Subscription(**{'login_rule': 2, 'login': 'bezh', 'service': Service(sid=42), 'host': Host(id=1)}),
        }

        def change_subs():
            self.account.subscriptions[42].host.id = 100

        name_and_value = {
            'sid.wwwdgt_wmode': '100',
        }
        self.eq_historydb_events_from_diff(change_subs, name_and_value)

    def test_historydb_events_from_diff_for_subscriptions_change_login_rule_on_mail(self):
        self.account.subscriptions = {
            2: Subscription(
                **{
                    'parent': self.account, 'login_rule': 1, 'login': 'maillogin', 'suid': 1234567,
                    'service': Service(sid=2),
                }
            ),
            6: Subscription(
                **{
                    'parent': self.account, 'login_rule': 1, 'login': 'inkvi', 'suid': 27560013,
                    'service': Service(sid=6), 'host': Host(id=1),
                }
            ),
        }

        def change_subs():
            self.account.subscriptions[2].login_rule = 2
            self.account.subscriptions[6].host.id = 100

        name_and_value = {
            'sid.login_rule': '2|2',
        }
        self.eq_historydb_events_from_diff(change_subs, name_and_value)

    def test_historydb_events_from_diff_for_karma_add(self):
        def change_karma():
            self.account.karma = Karma()
            self.account.karma.prefix = 1
            self.account.karma.suffix = 100

        name_and_value = {
            'info.karma_prefix': '1',
            'info.karma_full': '1100',
            'info.karma': '100',
        }

        self.eq_historydb_events_from_diff(change_karma, name_and_value)

    def test_historydb_events_from_diff_for_sid_login_rule(self):
        self.account.subscriptions = {
            3: Subscription(**{'login_rule': 1, 'login': 'inkvi', 'service': Service(sid=3), 'suid': 27560013}),
            4: Subscription(**{'login_rule': 3, 'login': 'inkvi', 'service': Service(sid=4), 'suid': 27560013}),
        }

        def change_subscriptions():
            self.account.subscriptions[3].login_rule = 2
            self.account.subscriptions[4].login_rule = 4

        self.eq_historydb_events_from_diff(
            change_subscriptions,
            {
                'sid.login_rule': '3|2,4|4',
            },
        )

    def test_unset_is_enabled(self):
        def change_is_enabled():
            self.account.is_enabled = False

        self.eq_historydb_events_from_diff(
            change_is_enabled,
            {
                'info.ena': '0',
                'info.disabled_status': '1',
            },
        )

    def test_set_disabled_on_deletion_status(self):
        def change_disabled_status():
            self.account.disabled_status = ACCOUNT_DISABLED_ON_DELETION

        self.eq_historydb_events_from_diff(
            change_disabled_status,
            {
                'info.ena': '0',
                'info.disabled_status': '2',
            },
        )

    def test_mail_status(self):
        def change_mail_status():
            self.account.mail_status = MAIL_STATUS_FROZEN

        self.eq_historydb_events_from_diff(
            change_mail_status,
            {
                'info.mail_status': '2',
            },
        )

    def test_get_login_rule_name_and_value_for_info(self):
        now = datetime.now()
        now_reg = datetime.today()

        def change_person():
            person = Person()
            person.firstname = 'killer'
            person.firstname_global = 'killer'
            person.lastname = 'queen'
            person.lastname_global = 'queen'
            person.birthday = '1946-10-05'
            person.gender = Gender.Male
            person.country = 'ru'
            person.city = 'Moscow'
            person.email = 'zippie@yandex.ru'
            person.timezone = pytz.timezone("Europe/Moscow")
            person.language = 'RU'
            person.display_name = DisplayName('cooper')
            person.default_avatar = 'ava'
            self.account.person = person

            password = self.account.password
            password.set('weak', 20, 'salt')
            password.update_datetime = now

            hint = Hint()
            hint.question = Question("Who?", 5)
            hint.answer = 'Me'
            self.account.hint = hint

            self.account.is_enabled = True
            self.account.global_logout_datetime = now
            self.account.registration_datetime = now_reg
            self.account.tokens_revoked_at = now
            self.account.web_sessions_revoked_at = now
            self.account.app_passwords_revoked_at = now

        now_ts_string = to_unixtime_string(now)

        name_value = {
            'info.firstname': 'killer',
            'info.firstname_global': 'killer',
            'info.lastname': 'queen',
            'info.lastname_global': 'queen',
            'info.sex': '1',
            'info.birthday': '1946-10-05',
            'info.country': 'ru',
            'info.city': 'Moscow',
            'info.email': 'zippie@yandex.ru',
            'info.ena': '1',
            'info.disabled_status': '0',
            'info.password': '1:$1$salt$S50SsPzK2tVeNfb0w..WW0',
            'info.password_quality': '20',
            'info.password_update_time': to_unixtime_string(now),
            'info.hintq': '5:Who?',
            'info.hinta': 'Me',
            'info.glogout': now_ts_string,
            'info.tokens_revoked': now_ts_string,
            'info.web_sessions_revoked': now_ts_string,
            'info.app_passwords_revoked': now_ts_string,
            'info.reg_date': now_reg.strftime('%Y-%m-%d %H:%M:%S'),
            'info.tz': 'Europe/Moscow',
            'info.display_name': 'p:cooper',
            'info.lang': 'RU',
            'info.default_avatar': 'ava',
        }

        self.eq_historydb_events_from_diff(change_person, name_value)

    def test_get_status_name_and_value_for_changing_info_from_null_to_empty(self):
        """
        Тестируем замену None на ''
        """
        def change_person():
            person = Person()
            person.firstname = ''
            person.lastname = ''
            person.country = ''
            person.city = ''
            person.language = ''
            self.account.person = person

        name_and_value = {}
        self.eq_historydb_events_from_diff(change_person, name_and_value)

    def test_change_hint_answer_but_not_question(self):
        def change_hint_answer():
            self.account.hint.answer = 'He'

        hint = Hint()
        hint.question = Question('Who?', 5)
        hint.answer = 'Me'
        self.account.hint = hint

        self.eq_historydb_events_from_diff(
            change_hint_answer,
            {
                'info.hintq': '5:Who?',
                'info.hinta': 'He',
            },
        )

    def test_change_hint_question_but_not_answer(self):
        def change_hint_question():
            self.account.hint.question = Question('Why?', 5)

        hint = Hint()
        hint.question = Question('Who?', 5)
        hint.answer = 'Me'
        self.account.hint = hint

        self.eq_historydb_events_from_diff(
            change_hint_question,
            {
                'info.hintq': '5:Why?',
                'info.hinta': 'Me',
            },
        )

    def test_change_hint(self):
        def change_hint():
            self.account.hint.question = Question('Why?', 5)
            self.account.hint.answer = u'Потому'

        hint = Hint()
        hint.question = Question('Who?', 5)
        hint.answer = 'Me'
        self.account.hint = hint

        self.eq_historydb_events_from_diff(
            change_hint,
            {
                'info.hintq': '5:Why?',
                'info.hinta': 'Потому',
            },
        )

    def test_delete_hint(self):
        def delete_hint():
            self.account.hint = None

        hint = Hint()
        hint.question = Question('Who?', 5)
        hint.answer = 'Me'
        self.account.hint = hint

        self.eq_historydb_events_from_diff(
            delete_hint,
            {
                'info.hintq': '-',
                'info.hinta': '-',
            },
        )

    def test_historydb_events_from_diff_for_browser_key_update(self):
        def update_browser_key():
            self.account.browser_key = 'new key'

        self.account.browser_key = 'key'

        self.eq_historydb_events_from_diff(update_browser_key, {})

    def test_historydb_events_from_diff_for_browser_key_delete(self):
        def delete_browser_key():
            self.account.browser_key = ''

        self.account.browser_key = 'key'

        self.eq_historydb_events_from_diff(delete_browser_key, {})

    def test_change_enable_app_password(self):
        def change_enable_app_password_to_true():
            self.account.enable_app_password = True

        def change_enable_app_password_to_false():
            self.account.enable_app_password = False

        self.account.enable_app_password = Undefined
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_true,
            {'info.enable_app_password': '1'},
        )

        self.account.enable_app_password = False
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_true,
            {'info.enable_app_password': '1'},
        )

        self.account.enable_app_password = True
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_true,
            {},
        )

        self.account.enable_app_password = Undefined
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_false,
            {'info.enable_app_password': '0'},
        )

        self.account.enable_app_password = True
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_false,
            {'info.enable_app_password': '0'},
        )

        self.account.enable_app_password = False
        self.eq_historydb_events_from_diff(
            change_enable_app_password_to_false,
            {},
        )

    def test_delete_password(self):
        def delete_password():
            self.account.password = None

        self.account.password.update_datetime = 123

        self.eq_historydb_events_from_diff(
            delete_password,
            {
                'info.password': '-',
                'info.password_quality': '-',
                'info.password_update_time': '-',
            },
        )

    def test_delete_enable_app_password(self):
        def delete_enable_app_password():
            self.account.enable_app_password = None

        self.account.enable_app_password = True
        self.eq_historydb_events_from_diff(
            delete_enable_app_password,
            {
                'info.enable_app_password': '-',
            },
        )

    def test_add_account_default_email(self):
        def add_default_email():
            self.account.default_email = u'email@почта.рф'

        self.eq_historydb_events_from_diff(
            add_default_email,
            {
                'info.default_email': 'email@почта.рф',
            },
        )

    def test_delete_account_default_email(self):
        def delete_default_email():
            self.account.default_email = None

        self.account.default_email = 'email@email.email'

        self.eq_historydb_events_from_diff(
            delete_default_email,
            {
                'info.default_email': '-',
            },
        )

    def test_add_account_additional_data(self):
        def add_additional_data():
            self.account.additional_data_asked = 'phone'
            self.account.additional_data_ask_next_datetime = datetime.now()

        self.eq_historydb_events_from_diff(
            add_additional_data,
            {
                'info.additional_data_asked': 'phone',
                'info.additional_data_ask_next_datetime': DatetimeNow(convert_to_datetime=True),
            },
        )

    def test_edit_account_additional_data(self):
        def edit_additional_data():
            self.account.additional_data_asked = 'phone'
            self.account.additional_data_ask_next_datetime = datetime.now()

        self.account.additional_data_asked = 'email'
        self.account.additional_data_ask_next_datetime = datetime(2016, 1, 1)

        self.eq_historydb_events_from_diff(
            edit_additional_data,
            {
                'info.additional_data_asked': 'phone',
                'info.additional_data_ask_next_datetime': DatetimeNow(convert_to_datetime=True),
            },
        )

    def test_delete_account_additional_data(self):
        def delete_additional_data():
            self.account.additional_data_asked = None
            self.account.additional_data_ask_next_datetime = None

        self.account.additional_data_asked = 'email'
        self.account.additional_data_ask_next_datetime = datetime(2016, 1, 1)

        self.eq_historydb_events_from_diff(
            delete_additional_data,
            {
                'info.additional_data_asked': '-',
                'info.additional_data_ask_next_datetime': '-',
            },
        )

    def test_add_external_organization_ids(self):
        def add_additional_data():
            self.account.external_organization_ids = [1, 3, 2]

        self.eq_historydb_events_from_diff(
            add_additional_data,
            {
                'info.external_organization_ids': '1,2,3',
            },
        )

    def test_edit_external_organization_ids(self):
        def edit_additional_data():
            self.account.external_organization_ids = [1, 3, 2]

        self.account.external_organization_ids = [1, 4, 2]

        self.eq_historydb_events_from_diff(
            edit_additional_data,
            {
                'info.external_organization_ids': '1,2,3',
            },
        )

    def test_delete_external_organization_ids(self):
        def delete_additional_data():
            self.account.external_organization_ids = []

        self.account.external_organization_ids = [1, 4, 2]

        self.eq_historydb_events_from_diff(
            delete_additional_data,
            {
                'info.external_organization_ids': '-',
            },
        )

    def test_add_billing_features(self):
        def add_additional_data():
            self.account.billing_features = {
                'Music_Premium': {
                    'region_id': 9999
                },
            }

        self.eq_historydb_events_from_diff(
            add_additional_data,
            {
                'account.billing_features': u'{"Music_Premium": {"region_id": 9999}}',
            },
        )

    def test_delete_billing_features(self):
        def delete_additional_data():
            self.account.billing_features = {}

        self.account.billing_features = {
            'Music_Premium': {
                'region_id': 9999
            },
        }
        self.eq_historydb_events_from_diff(
            delete_additional_data,
            {
                'account.billing_features': '-',
            },
        )


class TestPlusEventSerializer(BaseTestEventSerializer):
    """
    Тестирование сериализации логов account.plus
    """

    def setUp(self):
        super(TestPlusEventSerializer, self).setUp()
        self.account = default_account(uid=TEST_UID)
        self.account.plus = Plus(self.account)

    def test_nothing_changed(self):
        self.account.plus.enabled = True
        self.account.plus.trial_used_ts = datetime.now()
        self.account.plus.subscription_stopped_ts = datetime.now()
        self.account.plus.subscription_expire_ts = datetime.now()
        self.account.plus.next_charge_ts = datetime.now()
        self.account.plus.ott_subscription = 'ott-subscription'
        self.account.plus.family_role = 'family-role'
        self.account.plus.cashback_enabled = True
        self.account.plus.subscription_level = 0
        self.account.plus.is_frozen = True
        self.account.family_pay_enabled = 'eda,mail'
        self.account.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        self.eq_historydb_events_from_diff(
            lambda: None,
            {},
        )

    def test_create_plus(self):
        dt_now = datetime.now()
        expected_ts = str(int(datetime_to_unixtime(dt_now)))

        def create_plus():
            self.account.plus.enabled = True
            self.account.plus.trial_used_ts = dt_now
            self.account.plus.subscription_stopped_ts = dt_now
            self.account.plus.subscription_expire_ts = dt_now
            self.account.plus.next_charge_ts = dt_now
            self.account.plus.ott_subscription = 'ott-subscription'
            self.account.plus.family_role = 'family-role'
            self.account.plus.cashback_enabled = True
            self.account.plus.subscription_level = 0
            self.account.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        self.eq_historydb_events_from_diff(
            create_plus,
            {
                'plus.enabled': '1',
                'plus.trial_used_ts': expected_ts,
                'plus.subscription_stopped_ts': expected_ts,
                'plus.subscription_expire_ts': expected_ts,
                'plus.next_charge_ts': expected_ts,
                'plus.ott_subscription': 'ott-subscription',
                'plus.family_role': 'family-role',
                'plus.cashback_enabled': '1',
                'plus.subscription_level': '0',
                'plus.subscriber_state': TEST_PLUS_SUBSCRIBER_STATE1_JSON,
            },
        )

    def test_disable_plus(self):
        self.account.plus.enabled = True
        self.account.plus.trial_used_ts = datetime.now()
        self.account.plus.subscription_stopped_ts = datetime.now()
        self.account.plus.subscription_expire_ts = datetime.now()
        self.account.plus.next_charge_ts = datetime.now()
        self.account.plus.ott_subscription = 'ott-subscription'
        self.account.plus.family_role = 'family-role'
        self.account.plus.cashback_enabled = True
        self.account.plus.subscription_level = 0
        self.account.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        def disable_plus():
            self.account.plus.enabled = False
            self.account.plus.trial_used_ts = None
            self.account.plus.subscription_stopped_ts = None
            self.account.plus.subscription_expire_ts = None
            self.account.plus.next_charge_ts = None
            self.account.plus.ott_subscription = None
            self.account.plus.family_role = None
            self.account.plus.cashback_enabled = None
            self.account.plus.subscription_level = None
            self.account.plus.subscriber_state = None

        self.eq_historydb_events_from_diff(
            disable_plus,
            {
                'plus.enabled': '0',
                'plus.trial_used_ts': '0',
                'plus.subscription_stopped_ts': '0',
                'plus.subscription_expire_ts': '0',
                'plus.next_charge_ts': '0',
                'plus.ott_subscription': '-',
                'plus.family_role': '-',
                'plus.cashback_enabled': '0',
                'plus.subscription_level': '-',
                'plus.subscriber_state': '-',
            },
        )

    def test_empty_ott_subscription(self):
        self.account.plus.ott_subscription = 'ott-subscription'

        def disable_plus():
            self.account.plus.ott_subscription = ''

        self.eq_historydb_events_from_diff(
            disable_plus,
            {
                'plus.ott_subscription': '-',
            },
        )

    def test_disable_plus_cashback(self):
        self.account.plus.cashback_enabled = True

        def disable_plus():
            self.account.plus.cashback_enabled = False

        self.eq_historydb_events_from_diff(
            disable_plus,
            {
                'plus.cashback_enabled': '0',
            },
        )

    def test_freeze_plus(self):
        def freeze_plus():
            self.account.plus.is_frozen = True

        self.eq_historydb_events_from_diff(
            freeze_plus, {'plus.is_frozen': '1'},
        )

    def test_unfreeze_plus(self):
        self.account.plus.is_frozen = True

        def unfreeze_plus():
            self.account.plus.is_frozen = False

        self.eq_historydb_events_from_diff(
            unfreeze_plus, {'plus.is_frozen': '0'},
        )

    def test_enable_family_pay(self):
        def enable_family_pay():
            self.account.family_pay_enabled = 'eda,mail'

        self.eq_historydb_events_from_diff(
            enable_family_pay, {'account.family_pay.enabled': 'eda,mail'},
        )

    def test_disable_family_pay(self):
        def disable_family_pay():
            self.account.family_pay_enabled = ''

        self.account.family_pay_enabled = 'eda,mail'
        self.eq_historydb_events_from_diff(
            disable_family_pay, {'account.family_pay.enabled': '-'},
        )

    def test_empty_family_role(self):
        self.account.plus.family_role = 'family-role'

        def disable_plus():
            self.account.plus.family_role = ''

        self.eq_historydb_events_from_diff(
            disable_plus,
            {
                'plus.family_role': '-',
            },
        )

    def test_delete_plus_from_account(self):
        self.account.plus.enabled = True
        self.account.plus.trial_used_ts = datetime.now()
        self.account.plus.subscription_stopped_ts = datetime.now()
        self.account.plus.subscription_expire_ts = datetime.now()
        self.account.plus.next_charge_ts = datetime.now()
        self.account.plus.ott_subscription = 'ott-subscription'
        self.account.plus.family_role = 'family-role'
        self.account.plus.cashback_enabled = True
        self.account.plus.subscription_level = '0'
        self.account.plus.is_frozen = True
        self.account.plus.subscriber_state = TEST_PLUS_SUBSCRIBER_STATE1_JSON

        def delete_plus():
            self.account.plus = None

        self.eq_historydb_events_from_diff(
            delete_plus,
            {
                'plus.enabled': '-',
                'plus.trial_used_ts': '-',
                'plus.subscription_stopped_ts': '-',
                'plus.subscription_expire_ts': '-',
                'plus.next_charge_ts': '-',
                'plus.ott_subscription': '-',
                'plus.family_role': '-',
                'plus.cashback_enabled': '-',
                'plus.subscription_level': '-',
                'plus.is_frozen': '-',
                'plus.subscriber_state': '-',
            },
        )


class TestTakeoutEventSerializer(BaseTestEventSerializer):
    def setUp(self):
        super(TestTakeoutEventSerializer, self).setUp()
        self.account = default_account(uid=TEST_UID)
        self.account.takeout = Takeout(self.account)

    def test_nothing_changed(self):
        self.eq_historydb_events_from_diff(
            lambda: None,
            {},
        )

    def test_start_extraction(self):
        self.account.takeout.extract_in_progress_since = None
        self.account.takeout.archive_s3_key = 'key'
        self.account.takeout.archive_password = 'password'
        self.account.takeout.archive_created_at = datetime.now()
        self.account.takeout.fail_extract_at = None

        def modify():
            self.account.takeout.extract_in_progress_since = unixtime_to_datetime(24)
            self.account.takeout.archive_s3_key = None
            self.account.takeout.archive_password = None
            self.account.takeout.archive_created_at = None
            self.account.takeout.fail_extract_at = unixtime_to_datetime(42)

        self.eq_historydb_events_from_diff(
            modify,
            {
                'takeout.extract_in_progress_since': '24',
                'takeout.archive_s3_key': '-',
                'takeout.archive_password': '-',
                'takeout.archive_created_at': '0',
                'takeout.fail_extract_at': '42',
            },
        )

    def test_finish_extraction(self):
        self.account.takeout.extract_in_progress_since = unixtime_to_datetime(24)
        self.account.takeout.archive_s3_key = None
        self.account.takeout.archive_password = None
        self.account.takeout.archive_created_at = None
        self.account.takeout.fail_extract_at = datetime.now()

        def modify():
            self.account.takeout.extract_in_progress_since = None
            self.account.takeout.archive_s3_key = 'key'
            self.account.takeout.archive_password = 'password'
            self.account.takeout.archive_created_at = unixtime_to_datetime(42)
            self.account.takeout.fail_extract_at = None

        self.eq_historydb_events_from_diff(
            modify,
            {
                'takeout.extract_in_progress_since': '0',
                'takeout.archive_s3_key': '***',
                'takeout.archive_password': '***',
                'takeout.archive_created_at': '42',
                'takeout.fail_extract_at': '0',
            },
        )


class TestPhonesEventSerializer(BaseTestEventSerializer):
    """
    Тестирование сериализации логов, связанных с account.phones.
    """

    def setUp(self):
        super(TestPhonesEventSerializer, self).setUp()
        self.account = self._create_account()

    def _create_account(self):
        account = default_account(uid=TEST_UID)
        account.password = Password(self.account)
        return account

    def test_nothing_changed(self):
        """
        На аккаунте с телефонами ничего не менялось, значит и писать ничего не должны.
        """
        self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            existing_phone_id=TEST_PHONE_ID,
            operation_data=TEST_PHONE_OPERATION_DATA,
        )

        self.eq_historydb_events_from_diff(
            lambda: None,
            {},
        )

    def test_create_phone_simple(self):
        """
        Создание телефона на аккаунте, без доп атрибутов и операции.
        Должны появиться базовые записи.
        """
        def create_phone():
            self.account.phones.create(
                number=TEST_PHONE_NUMBER,
                existing_phone_id=TEST_PHONE_ID,
            )

        self.eq_historydb_events_from_diff(
            create_phone,
            {
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.123.action': 'created',
                'phone.123.created': TimeNow(),
            },
        )

    def test_phones_with_all_attrs_and_operation(self):
        """
        Создание и удаление двух телефонов (чтобы проверить, что записи не конфликтуют)
        на аккаунте с полным набором атрибутов и операцией.
        """
        def create_phones():
            phone1 = self.account.phones.create(
                number=TEST_PHONE_NUMBER,
                created=TEST_CREATED_DT,
                bound=TEST_BOUND_DT,
                confirmed=TEST_CONFIRMED_DT,
                admitted=TEST_ADMITTED_DT,
                secured=TEST_SECURED_DT,
                existing_phone_id=TEST_PHONE_ID,
                operation_data=TEST_PHONE_OPERATION_DATA,
            )

            phone2 = self.account.phones.create(
                number=TEST_PHONE_NUMBER2.e164,
                created=TEST_CREATED_DT,
                bound=TEST_BOUND_DT,
                confirmed=TEST_CONFIRMED_DT,
                admitted=TEST_ADMITTED_DT,
                secured=TEST_SECURED_DT,
                existing_phone_id=TEST_PHONE_ID2,
                operation_data=TEST_PHONE_OPERATION_DATA2,
            )

            # Поскольку не было честной сериализации модели, id поставим руками.
            phone1.operation.id = TEST_PHONE_OPERATION_ID
            phone2.operation.id = TEST_PHONE_OPERATION_ID2

        self.eq_historydb_events_from_diff(
            create_phones,
            {
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.123.action': 'created',
                'phone.123.created': to_unixtime_string(TEST_CREATED_DT),
                'phone.123.bound': to_unixtime_string(TEST_BOUND_DT),
                'phone.123.confirmed': to_unixtime_string(TEST_CONFIRMED_DT),
                'phone.123.admitted': to_unixtime_string(TEST_ADMITTED_DT),
                'phone.123.secured': to_unixtime_string(TEST_SECURED_DT),

                'phone.123.operation.456.action': 'created',
                'phone.123.operation.456.started': to_unixtime_string(TEST_PHONE_OPERATION_DATA['started']),
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),
                'phone.123.operation.456.finished': to_unixtime_string(TEST_PHONE_OPERATION_DATA['finished']),
                'phone.123.operation.456.code_confirmed': to_unixtime_string(TEST_PHONE_OPERATION_DATA['code_confirmed']),
                'phone.123.operation.456.password_verified': to_unixtime_string(TEST_PHONE_OPERATION_DATA['password_verified']),
                'phone.123.operation.456.phone_id2': str(TEST_PHONE_OPERATION_DATA['phone_id2']),

                'phone.234.action': 'created',
                'phone.234.number': TEST_PHONE_NUMBER2.e164,
                'phone.234.created': to_unixtime_string(TEST_CREATED_DT),
                'phone.234.bound': to_unixtime_string(TEST_BOUND_DT),
                'phone.234.confirmed': to_unixtime_string(TEST_CONFIRMED_DT),
                'phone.234.admitted': to_unixtime_string(TEST_ADMITTED_DT),
                'phone.234.secured': to_unixtime_string(TEST_SECURED_DT),

                'phone.234.operation.567.action': 'created',
                'phone.234.operation.567.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.234.operation.567.security_identity': TEST_PHONE_NUMBER2.digital,
                'phone.234.operation.567.finished': to_unixtime_string(TEST_PHONE_OPERATION_DATA['finished']),
                'phone.234.operation.567.started': to_unixtime_string(TEST_PHONE_OPERATION_DATA['started']),
                'phone.234.operation.567.code_confirmed': to_unixtime_string(TEST_PHONE_OPERATION_DATA['code_confirmed']),
                'phone.234.operation.567.password_verified': to_unixtime_string(TEST_PHONE_OPERATION_DATA['password_verified']),
                'phone.234.operation.567.phone_id2': str(TEST_PHONE_OPERATION_DATA['phone_id2']),
            },
        )

        # Теперь удалим созданные телефоны.
        def delete_phones():
            self.account.phones.remove(TEST_PHONE_ID)
            self.account.phones.remove(TEST_PHONE_ID2)

        # Важно: в лог пишутся не все поля, которые были на телефоне и операции!
        self.eq_historydb_events_from_diff(
            delete_phones,
            {
                'phone.123.action': 'deleted',
                'phone.123.number': TEST_PHONE_NUMBER,

                'phone.123.operation.456.action': 'deleted',
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),

                'phone.234.action': 'deleted',
                'phone.234.number': TEST_PHONE_NUMBER2.e164,

                'phone.234.operation.567.action': 'deleted',
                'phone.234.operation.567.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.234.operation.567.security_identity': TEST_PHONE_NUMBER2.digital,
            },
        )

    def test_phone_operation(self):
        """
        На существующем телефоне создаем операцию, модифицируем, удаляем.
        Проверим логирование каждого шага.
        При изменении только операции не пишем phone.id.action=changed!
        """
        self.phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            existing_phone_id=TEST_PHONE_ID,
        )

        def create_operation():
            self.phone.create_operation(**TEST_PHONE_OPERATION_DATA)
            self.phone.operation.id = TEST_PHONE_OPERATION_ID

        # Важно: в лог пишутся не все поля, которые были на телефоне и операции!
        self.eq_historydb_events_from_diff(
            create_operation,
            {
                'phone.123.number': TEST_PHONE_NUMBER,

                'phone.123.operation.456.action': 'created',
                'phone.123.operation.456.started': to_unixtime_string(TEST_PHONE_OPERATION_DATA['started']),
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),
                'phone.123.operation.456.finished': to_unixtime_string(TEST_PHONE_OPERATION_DATA['finished']),
                'phone.123.operation.456.code_confirmed': to_unixtime_string(TEST_PHONE_OPERATION_DATA['code_confirmed']),
                'phone.123.operation.456.password_verified': to_unixtime_string(TEST_PHONE_OPERATION_DATA['password_verified']),
                'phone.123.operation.456.phone_id2': str(TEST_PHONE_OPERATION_DATA['phone_id2']),
            },
        )

        # Изменим все поля.
        def edit_operation():
            op = self.phone.operation
            dt = datetime(2010, 1, 2, 12, 34, 56)
            op.finished = dt
            op.code_confirmed = dt
            op.password_verified = dt
            op.phone_id2 = 777

            # Эти поля не пишутся в лог:
            op.code_value = '123'
            op.code_checks_count = 2
            op.code_send_count = 2
            op.code_last_sent = dt
            op.flags = PhoneOperationFlags(2)

        unixtime_string = to_unixtime_string(datetime(2010, 1, 2, 12, 34, 56))

        self.eq_historydb_events_from_diff(
            edit_operation,
            {
                'phone.123.number': TEST_PHONE_NUMBER,

                'phone.123.operation.456.action': 'changed',
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),
                'phone.123.operation.456.finished': unixtime_string,
                'phone.123.operation.456.code_confirmed': unixtime_string,
                'phone.123.operation.456.password_verified': unixtime_string,
                'phone.123.operation.456.phone_id2': '777',
            },
        )

        # Изменим все поля, которые не пишутся в лог. Проверим, что ничего не записалось (включая номер телефона)
        def edit_operation():
            op = self.phone.operation
            dt = datetime(2012, 1, 2, 12, 34, 56)
            # Эти поля не пишутся в лог:
            op.code_value = '456'
            op.code_checks_count = 3
            op.code_send_count = 3
            op.code_last_sent = dt
            op.flags = PhoneOperationFlags(3)

        self.eq_historydb_events_from_diff(
            edit_operation,
            {},
        )

        # Удалим все поля.
        def remove_operation_fields():
            op = self.phone.operation
            op.finished = None
            op.code_confirmed = None
            op.password_verified = None
            op.phone_id2 = None

        self.eq_historydb_events_from_diff(
            remove_operation_fields,
            {
                'phone.123.number': TEST_PHONE_NUMBER,

                'phone.123.operation.456.action': 'changed',
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),
                'phone.123.operation.456.finished': '0',
                'phone.123.operation.456.code_confirmed': '0',
                'phone.123.operation.456.password_verified': '0',
                'phone.123.operation.456.phone_id2': '0',
            },
        )

        # Удалим всю операцию.
        def remove_operation():
            self.phone.operation = None

        self.eq_historydb_events_from_diff(
            remove_operation,
            {
                'phone.123.number': TEST_PHONE_NUMBER,

                'phone.123.operation.456.action': 'deleted',
                'phone.123.operation.456.type': TEST_PHONE_OPERATION_DATA['type'],
                'phone.123.operation.456.security_identity': str(int(TEST_PHONE_NUMBER)),
            },
        )

    def test_phones_fields(self):
        """
        Проверим логирование изменения account.phones.default и account.phones.secure.
        """
        self.phone1 = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            created=TEST_CREATED_DT,
            existing_phone_id=TEST_PHONE_ID,
        )
        self.phone2 = self.account.phones.create(
            number=TEST_PHONE_NUMBER2.e164,
            created=TEST_CREATED_DT,
            bound=TEST_BOUND_DT,
            existing_phone_id=TEST_PHONE_ID2,
        )
        self.account.phones.default = None

        def set_attrs():
            self.account.phones.default = self.phone1
            self.phone2.secured = TEST_SECURED_DT
            self.account.phones.secure = self.phone2

        self.eq_historydb_events_from_diff(
            set_attrs,
            {
                'phones.default': str(TEST_PHONE_ID),
                'phones.secure': str(TEST_PHONE_ID2),
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.234.action': 'changed',
                'phone.234.number': TEST_PHONE_NUMBER2.e164,
                'phone.234.secured': to_unixtime_string(TEST_SECURED_DT),
            },
        )

        # Удалим атрибуты
        def del_attrs():
            self.account.phones.default = None
            self.account.phones.secure = None

        self.eq_historydb_events_from_diff(
            del_attrs,
            {
                'phones.default': '0',
                'phones.secure': '0',
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.234.number': TEST_PHONE_NUMBER2.e164,
            },
        )

    def test_phones_fields_single_number_record(self):
        """
        Поставим одинаковые account.phones.default и account.phones.secure, еще и изменим что-то на телефоне.
        Проверим, что phone.id.number присутствует в ответе только один раз.
        """
        self.phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            created=TEST_CREATED_DT,
            existing_phone_id=TEST_PHONE_ID,
        )
        self.account.phones.default = None

        def set_attrs():
            self.phone.secured = TEST_SECURED_DT
            self.phone.bound = TEST_BOUND_DT
            self.account.phones.default = self.phone
            self.account.phones.secure = self.phone

        self.eq_historydb_events_from_diff(
            set_attrs,
            {
                'phones.default': str(TEST_PHONE_ID),
                'phones.secure': str(TEST_PHONE_ID),

                'phone.123.action': 'changed',
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.123.bound': to_unixtime_string(TEST_BOUND_DT),
                'phone.123.secured': to_unixtime_string(TEST_SECURED_DT),
            },
        )

    def test_phone_fields(self):
        """
        Добавим, изменим, а потом удалим все атрибуты телефона.
        """
        self.phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            created=TEST_CREATED_DT,
            existing_phone_id=TEST_PHONE_ID,
        )

        def fill_phone_fields():
            self.phone.bound = TEST_BOUND_DT
            self.phone.confirmed = TEST_CONFIRMED_DT
            self.phone.admitted = TEST_ADMITTED_DT
            self.phone.secured = TEST_SECURED_DT

        self.eq_historydb_events_from_diff(
            fill_phone_fields,
            {
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.123.action': 'changed',

                'phone.123.bound': to_unixtime_string(TEST_BOUND_DT),
                'phone.123.confirmed': to_unixtime_string(TEST_CONFIRMED_DT),
                'phone.123.admitted': to_unixtime_string(TEST_ADMITTED_DT),
                'phone.123.secured': to_unixtime_string(TEST_SECURED_DT),
            },
        )

        # Удалим атрибуты телефона
        def remove_phone_fields():
            self.phone.bound = None
            self.phone.confirmed = None
            self.phone.admitted = None
            self.phone.secured = None

        self.eq_historydb_events_from_diff(
            remove_phone_fields,
            {
                'phone.123.number': TEST_PHONE_NUMBER,
                'phone.123.action': 'changed',

                'phone.123.bound': '0',
                'phone.123.confirmed': '0',
                'phone.123.admitted': '0',
                'phone.123.secured': '0',
            },
        )

    def test_phone_operation_replace(self):
        """
        Заменяем одну телефонную операцию другой.
        """
        self.phone = self.account.phones.create(
            number=TEST_PHONE_NUMBER,
            existing_phone_id=TEST_PHONE_ID,
        )
        self.phone.create_operation(**TEST_PHONE_OPERATION_DATA)
        self.phone.operation.id = TEST_PHONE_OPERATION_ID

        def edit_operation():
            self.phone.operation.id = TEST_PHONE_OPERATION_ID2

        op1_prefix = 'phone.%d.operation.%d' % (
            TEST_PHONE_ID,
            TEST_PHONE_OPERATION_ID,
        )
        op2_prefix = 'phone.%d.operation.%d' % (
            TEST_PHONE_ID,
            TEST_PHONE_OPERATION_ID2,
        )

        self.eq_historydb_events_from_diff(
            edit_operation,
            {
                'phone.%d.number' % TEST_PHONE_ID: TEST_PHONE_NUMBER,

                '%s.action' % op1_prefix: 'deleted',
                '%s.type' % op1_prefix: TEST_PHONE_OPERATION_DATA['type'],
                '%s.security_identity' % op1_prefix: str(TEST_PHONE_OPERATION_DATA['security_identity']),

                '%s.action' % op2_prefix: 'created',
                '%s.type' % op2_prefix: TEST_PHONE_OPERATION_DATA['type'],
                '%s.security_identity' % op2_prefix: str(TEST_PHONE_OPERATION_DATA['security_identity']),
                '%s.started' % op2_prefix: to_unixtime_string(TEST_PHONE_OPERATION_DATA['started']),
                '%s.finished' % op2_prefix: to_unixtime_string(TEST_PHONE_OPERATION_DATA['finished']),
                '%s.code_confirmed' % op2_prefix: to_unixtime_string(TEST_PHONE_OPERATION_DATA['code_confirmed']),
                '%s.password_verified' % op2_prefix: to_unixtime_string(TEST_PHONE_OPERATION_DATA['password_verified']),
                '%s.phone_id2' % op2_prefix: str(TEST_PHONE_OPERATION_DATA['phone_id2']),
            },
        )

    def test_create_account__phone__without_operation(self):
        """
        Создаём новую учётную запись с телефоном, но без операции на нём.
        """
        def create_account():
            account = self._create_account()
            phone = account.phones.create(
                existing_phone_id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER,
                created=TEST_CREATED_DT,
                bound=TEST_BOUND_DT,
                confirmed=TEST_CONFIRMED_DT,
                secured=TEST_SECURED_DT,
                admitted=TEST_ADMITTED_DT,
            )

            account.phones.secure = phone
            account.phones.default = phone

            self.account = account

        self.account = None

        fmt_phone = 'phone.%d.' % TEST_PHONE_ID
        self.eq_historydb_events_from_diff(
            create_account,
            {
                'alias.portal.add': 'login',
                'info.login': 'login',

                fmt_phone + 'action': 'created',

                fmt_phone + 'number': TEST_PHONE_NUMBER,
                fmt_phone + 'created': to_unixtime_string(TEST_CREATED_DT),
                fmt_phone + 'bound': to_unixtime_string(TEST_BOUND_DT),
                fmt_phone + 'secured': to_unixtime_string(TEST_SECURED_DT),
                fmt_phone + 'confirmed': to_unixtime_string(TEST_CONFIRMED_DT),
                fmt_phone + 'admitted': to_unixtime_string(TEST_ADMITTED_DT),

                'phones.secure': str(TEST_PHONE_ID),
                'phones.default': str(TEST_PHONE_ID),
            },
        )

    def test_create_account__phone__with_operation(self):
        """
        Создаём новую учётную запись с телефоном и операцией на нём.
        """
        def create_account():
            account = self._create_account()
            phone = account.phones.create(
                existing_phone_id=TEST_PHONE_ID,
                number=TEST_PHONE_NUMBER,
                created=TEST_CREATED_DT,
            )

            phone.create_operation('bind', SECURITY_IDENTITY, started=TEST_CREATED_DT)
            phone.operation.id = TEST_PHONE_OPERATION_ID

            self.account = account

        self.account = None

        fmt_phone = 'phone.%d.' % TEST_PHONE_ID
        fmt_op = fmt_phone + 'operation.%d.' % TEST_PHONE_OPERATION_ID
        self.eq_historydb_events_from_diff(
            create_account,
            {
                'alias.portal.add': 'login',
                'info.login': 'login',

                fmt_phone + 'action': 'created',

                fmt_phone + 'number': TEST_PHONE_NUMBER,
                fmt_phone + 'created': to_unixtime_string(TEST_CREATED_DT),

                fmt_op + 'action': 'created',
                fmt_op + 'type': 'bind',
                fmt_op + 'security_identity': str(SECURITY_IDENTITY),
                fmt_op + 'started': to_unixtime_string(TEST_CREATED_DT),
            },
        )

    def test_change_secure_phone__existent(self):
        """
        Меняем защищённый телефон на другой привязанный телефон.
        """
        phone1 = self.account.phones.create(
            existing_phone_id=TEST_PHONE_ID,
            number=TEST_PHONE_NUMBER,
            bound=TEST_BOUND_DT,
            secured=TEST_SECURED_DT,
        )
        phone2 = self.account.phones.create(
            existing_phone_id=TEST_PHONE_ID2,
            number=TEST_PHONE_NUMBER2.e164,
            bound=TEST_BOUND_DT,
            secured=TEST_SECURED_DT,
        )
        self.account.phones.secure = phone1

        def change_secure_phone():
            self.account.phones.secure = phone2

        self.eq_historydb_events_from_diff(
            change_secure_phone,
            {
                'phone.%d.number' % TEST_PHONE_ID2: TEST_PHONE_NUMBER2.e164,
                'phones.secure': str(TEST_PHONE_ID2),
            },
        )

    def test_change_secure_phone__not_existent(self):
        """
        Меняем защищённый телефон на новый.
        """
        phone1 = self.account.phones.create(
            existing_phone_id=TEST_PHONE_ID,
            number=TEST_PHONE_NUMBER,
            bound=TEST_BOUND_DT,
            secured=TEST_SECURED_DT,
        )
        self.account.phones.secure = phone1

        def change_secure_phone():
            phone2 = self.account.phones.create(
                existing_phone_id=TEST_PHONE_ID2,
                number=TEST_PHONE_NUMBER2.e164,
                created=TEST_CREATED_DT,
                bound=TEST_BOUND_DT,
                secured=TEST_SECURED_DT,
            )
            self.account.phones.secure = phone2

        phone_fmt = 'phone.%d.' % TEST_PHONE_ID2
        self.eq_historydb_events_from_diff(
            change_secure_phone,
            {
                phone_fmt + 'action': 'created',
                phone_fmt + 'number': TEST_PHONE_NUMBER2.e164,
                phone_fmt + 'created': to_unixtime_string(TEST_CREATED_DT),
                phone_fmt + 'bound': to_unixtime_string(TEST_BOUND_DT),
                phone_fmt + 'secured': to_unixtime_string(TEST_SECURED_DT),
                'phones.secure': str(TEST_PHONE_ID2),
            },
        )

    def test_change_default_and_secure(self):
        """
        Меняем одновременно телефон для уведомлений и защищённый на другие
        разные телефоны.
        """
        phone1 = self.account.phones.create(
            existing_phone_id=TEST_PHONE_ID,
            number=TEST_PHONE_NUMBER,
            bound=TEST_BOUND_DT,
            secured=TEST_SECURED_DT,
        )
        phone2 = self.account.phones.create(
            existing_phone_id=TEST_PHONE_ID2,
            number=TEST_PHONE_NUMBER2.e164,
            bound=TEST_BOUND_DT,
            secured=TEST_SECURED_DT,
        )
        self.account.phones.secure = phone1
        self.account.phones.default = phone2

        def exchange():
            self.account.phones.secure = phone2
            self.account.phones.default = phone1

        self.eq_historydb_events_from_diff(
            exchange,
            {
                'phone.%d.number' % TEST_PHONE_ID2: TEST_PHONE_NUMBER2.e164,
                'phones.secure': str(TEST_PHONE_ID2),
                'phone.%d.number' % TEST_PHONE_ID: TEST_PHONE_NUMBER,
                'phones.default': str(TEST_PHONE_ID),
            },
        )

    def test_create_passman_recovery_key(self):
        def create():
            self.account.passman_recovery_key = PassManRecoveryKey(
                self.account,
                key_id=TEST_PASSMAN_KEY_ID,
                recovery_key=TEST_PASSMAN_RECOVERY_KEY,
            )

        self.eq_historydb_events_from_diff(
            create,
            {
                'info.passman_key_id': b64encode(TEST_PASSMAN_KEY_ID).decode('utf8'),
            },
        )

    def test_change_phone_number(self):
        phone = self.account.phones.create(existing_phone_id=1, number=TEST_PHONE_NUMBER)

        def exchange():
            phone.number = TEST_PHONE_NUMBER2

        self.eq_historydb_events_from_diff(
            exchange,
            {
                'phone.1.number': TEST_PHONE_NUMBER2.e164,
                'phone.1.action': 'changed',
            },
        )


class TestTotpSecretEventSerializer(BaseTestEventSerializer):
    def test_set_totp_secret(self):
        def set_secret():
            self.account.totp_secret = TotpSecret(self.account)
            self.account.totp_secret.set(TotpSecretType('encrypted_secret'))
            self.account.totp_secret.secret_ids = {1: datetime.now()}
            self.account.totp_secret.yakey_device_ids = ['d1', 'd2']

        self.eq_historydb_events_from_diff(
            set_secret,
            {
                'info.totp': 'enabled',
                'info.totp_secret.1': '*',
                'info.totp_update_time': TimeNow(),
                'info.totp_yakey_device_ids': 'd1,d2',
            },
        )

    def test_delete_totp_secret(self):
        def delete_secret():
            self.account.totp_secret = None

        self.account.totp_secret = TotpSecret(self.account)
        self.account.totp_secret.set(TotpSecretType('encrypted_secret'))
        self.account.totp_secret.secret_ids = {1: datetime.now(), 2: datetime.now()}
        self.account.totp_secret.yakey_device_ids = ['d1', 'd2']

        self.eq_historydb_events_from_diff(
            delete_secret,
            {
                'info.totp': 'disabled',
                'info.totp_secret.1': '-',
                'info.totp_secret.2': '-',
                'info.totp_update_time': '-',
            },
        )

    def test_edit_totp_secret(self):
        def edit_secret():
            self.account.totp_secret.secret_ids = {2: datetime.now(), 3: datetime.now()}
            self.account.totp_secret.yakey_device_ids = ['d2', 'd3']

        self.account.totp_secret = TotpSecret(self.account)
        self.account.totp_secret.set(TotpSecretType('encrypted_secret'))
        self.account.totp_secret.secret_ids = {1: datetime.now(), 2: datetime.now()}
        self.account.totp_secret.yakey_device_ids = ['d1', 'd2']

        self.eq_historydb_events_from_diff(
            edit_secret,
            {
                'info.totp_secret.1': '-',
                'info.totp_secret.3': '*',
                'info.totp_yakey_device_ids': 'd2,d3',
            },
        )


class TestRfcTotpSecretEventSerializer(BaseTestEventSerializer):
    def test_set_rfc_totp_secret(self):
        def set_secret():
            self.account.rfc_totp_secret = RfcTotpSecret(self.account)
            self.account.rfc_totp_secret.set(RfcTotpSecretType('secret'))

        self.eq_historydb_events_from_diff(
            set_secret,
            {
                'info.rfc_totp': 'enabled',
            },
        )

    def test_delete_rfc_totp_secret(self):
        def delete_secret():
            self.account.rfc_totp_secret = None

        self.account.rfc_totp_secret = RfcTotpSecret(self.account)
        self.account.rfc_totp_secret.set(RfcTotpSecretType('secret'))

        self.eq_historydb_events_from_diff(
            delete_secret,
            {
                'info.rfc_totp': 'disabled',
            },
        )


class TestAccountFlagsEventSerializer(BaseTestEventSerializer):
    @parameterized.expand(
        [
            ('audience_on', 'info.audience_on'),
            ('is_shared', 'info.is_shared'),
            ('magic_link_login_forbidden', 'info.magic_link_login_forbidden'),
            ('qr_code_login_forbidden', 'info.qr_code_login_forbidden'),
            ('sms_code_login_forbidden', 'info.sms_code_login_forbidden'),
            ('takeout.subscription', 'takeout.subscription'),
            ('is_connect_admin', 'info.is_connect_admin'),
            ('is_easily_hacked', 'info.is_easily_hacked'),
            ('is_employee', 'info.is_employee'),
            ('is_maillist', 'info.is_maillist'),
            ('force_challenge', 'account.force_challenge'),
            ('plus.cashback_enabled', 'plus.cashback_enabled'),
            ('sms_2fa_on', 'info.sms_2fa_on'),
            ('forbid_disabling_sms_2fa', 'info.forbid_disabling_sms_2fa'),
            ('is_verified', 'info.is_verified'),
            ('hide_yandex_domains_emails', 'info.hide_yandex_domains_emails'),
        ]
    )
    def test_change_boolean_flag(self, model_field_name, historydb_event_name):
        def change_attribute(attribute_path, value):
            def _change_attribute():
                temp_obj = self.account
                for attr_key in attribute_path.split('.')[:-1]:
                    temp_obj = getattr(temp_obj, attr_key)
                temp_obj.__dict__[attribute_path.split('.')[-1]] = value
            return _change_attribute

        change_attribute(model_field_name, Undefined)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, True),
            {historydb_event_name: '1'},
        )

        change_attribute(model_field_name, False)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, True),
            {historydb_event_name: '1'},
        )

        change_attribute(model_field_name, True)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, True),
            {},
        )

        change_attribute(model_field_name, Undefined)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, False),
            {historydb_event_name: '0'},
        )

        change_attribute(model_field_name, True)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, False),
            {historydb_event_name: '0'},
        )

        change_attribute(model_field_name, False)()
        self.eq_historydb_events_from_diff(
            change_attribute(model_field_name, False),
            {},
        )

    def test_set_account_is_money_agreement_accepted(self):
        def set_is_money_agreement_accepted():
            self.account.is_money_agreement_accepted = True

        self.eq_historydb_events_from_diff(
            set_is_money_agreement_accepted,
            {
                'info.money_eula_accepted': '1',
            },
        )


class TestAliasEventSerializer(BaseTestEventSerializer):
    def test_historydb_events_from_diff_for_portal_alias_add(self):
        def add_portal_alias():
            self.account.portal_alias = PortalAlias(self.account, login='Test.Login')
            self.account.user_defined_login = 'Test.Login'

        name_and_value = {
            'alias.portal.add': 'test-login',
            'info.login': 'test-login',
            'info.login_wanted': 'Test.Login',
        }
        self.eq_historydb_events_from_diff(add_portal_alias, name_and_value)

    def test_historydb_events_from_diff_for_pdd_alias_add(self):
        def add_pdd_alias_and_domain():
            self.account.pdd_alias = PddAlias(self.account, email='Test.Login@okna.ru')
            self.account.user_defined_login = 'Test.Login'
            self.account.domain = Domain(id=1, domain='okna.ru')

        name_and_value = {
            'info.domain_id': '1',
            'info.domain_name': 'okna.ru',
            'alias.pdd.add': '1/test.login',
            'info.login': 'test.login@okna.ru',
            'info.login_wanted': 'Test.Login',
        }
        self.eq_historydb_events_from_diff(add_pdd_alias_and_domain, name_and_value)

    def test_historydb_events_from_diff_for_social_alias_add(self):
        def add_social_alias():
            self.account.social_alias = SocialAlias(self.account, login='uid-test')

        name_and_value = {
            'alias.social.add': 'uid-test',
            'info.login': 'uid-test',
        }
        self.eq_historydb_events_from_diff(add_social_alias, name_and_value)

    def test_historydb_events_from_diff_for_lite_alias_add(self):
        def add_lite_alias():
            self.account.lite_alias = LiteAlias(self.account, email='Test.Login@okna.ru')

        name_and_value = {
            'alias.lite.add': 'Test.Login@okna.ru',
            'info.login': 'test.login@okna.ru',
        }
        self.eq_historydb_events_from_diff(add_lite_alias, name_and_value)

    def test_historydb_events_from_diff_for_phonish_alias_add(self):
        def add_phonish_alias():
            self.account.phonish_alias = PhonishAlias(self.account, login='phne-test')

        name_and_value = {
            'alias.phonish.add': 'phne-test',
            'info.login': 'phne-test',
        }
        self.eq_historydb_events_from_diff(add_phonish_alias, name_and_value)

    def test_historydb_events_from_diff_for_neophonish_alias_add(self):
        def add_neophonish_alias():
            self.account.neophonish_alias = NeophonishAlias(self.account, alias='nphne-test')

        name_and_value = {
            'alias.neophonish.add': 'nphne-test',
            'info.login': 'nphne-test',
        }
        self.eq_historydb_events_from_diff(add_neophonish_alias, name_and_value)

    def test_historydb_events_from_diff_for_mailish_alias_add(self):
        def add_mailish_alias():
            self.account.mailish_alias = MailishAlias(self.account, mailish_id='Some-String')

        name_and_value = {
            'alias.mailish.add': 'some-string',
            'info.login': 'some-string',
        }
        self.eq_historydb_events_from_diff(add_mailish_alias, name_and_value)

    def test_historydb_events_from_diff_for_kinopoisk_alias_add(self):
        def add_kinopoisk_alias():
            self.account.kinopoisk_alias = KinopoiskAlias(self.account, alias='100500')

        name_and_value = {
            'alias.kinopoisk.add': '100500',
        }
        self.eq_historydb_events_from_diff(add_kinopoisk_alias, name_and_value)

    def test_historydb_events_from_diff_for_creating_account_with_kinopoisk_alias(self):
        """
        Создаём новую учётную запись для Кинопоиска (логина нет).
        """
        def create_account():
            self.account = Account()
            self.account.kinopoisk_alias = KinopoiskAlias(alias='100500')

        self.account = None
        name_and_value = {
            'alias.kinopoisk.add': '100500',
        }
        self.eq_historydb_events_from_diff(create_account, name_and_value)

    def test_historydb_events_from_diff_for_uber_alias_add(self):
        def add_uber_alias():
            self.account.uber_alias = UberAlias(self.account, uber_id='1.1')

        name_and_value = {
            'alias.uber.add': '1.1',
            'info.login': '1-1',
        }
        self.eq_historydb_events_from_diff(add_uber_alias, name_and_value)

    def test_historydb_events_from_diff_for_creating_account_with_uber_alias(self):
        def create_account():
            self.account = Account()
            self.account.uber_alias = UberAlias(self.account, uber_id='1')

        self.account = None
        name_and_value = {
            'alias.uber.add': '1',
            'info.login': '1',
        }
        self.eq_historydb_events_from_diff(create_account, name_and_value)

    def test_historydb_events_from_diff_for_yambot_alias_add(self):
        def add_yambot_alias():
            self.account.yambot_alias = YambotAlias(self.account, alias='yambot-bot')

        name_and_value = {
            'alias.yambot.add': 'yambot-bot',
            'info.login': 'yambot-bot',
        }
        self.eq_historydb_events_from_diff(add_yambot_alias, name_and_value)

    def test_historydb_events_from_diff_for_kolonkish_alias_add(self):
        def add_kolonkish_alias():
            self.account.kolonkish_alias = KolonkishAlias(self.account, alias='kolonkish-123')

        name_and_value = {
            'alias.kolonkish.add': 'kolonkish-123',
            'info.login': 'kolonkish-123',
        }
        self.eq_historydb_events_from_diff(add_kolonkish_alias, name_and_value)

    def test_historydb_events_from_diff_for_public_id_alias_add(self):
        def add_public_id_alias():
            self.account.public_id_alias = PublicIdAlias(self.account, alias='public_id-123')
            self.account.user_defined_public_id = 'Public_Id-123'

        name_and_value = {
            'alias.public_id.add': 'public_id-123',
            'account.user_defined_public_id': 'Public_Id-123',
        }
        self.eq_historydb_events_from_diff(add_public_id_alias, name_and_value)

    def test_historydb_events_from_diff_for_public_id_alias_update(self):
        self.account.public_id_alias = PublicIdAlias(self.account, alias='public.id.1')
        self.account.user_defined_public_id = 'Public.Id.1'

        def add_public_id_alias():
            self.account.public_id_alias = PublicIdAlias(self.account, alias='public.id.2')
            self.account.user_defined_public_id = 'Public.Id.2'

        name_and_value = {
            'alias.public_id.upd': 'public.id.2',
            'account.user_defined_public_id': 'Public.Id.2',
        }
        self.eq_historydb_events_from_diff(add_public_id_alias, name_and_value)

    def test_public_id_alias_remove_multiple_old_public_ids(self):
        self.account.domain = Domain(id=1, domain='okna.ru')
        self.account.public_id_alias = PublicIdAlias(self.account, alias='public_id-123')
        self.account.public_id_alias.old_public_ids.add('old_public_id-1')
        self.account.public_id_alias.old_public_ids.add('old_public_id-2')

        def set_remove_multiple_logins():
            for login in ['old_public_id-1', 'old_public_id-2']:
                self.account.public_id_alias.old_public_ids.remove(login)

        self.eq_historydb_events_from_diff(
            set_remove_multiple_logins,
            {
                'alias.old_public_id.rm': 'old_public_id-1,old_public_id-2',
            },
        )

    def test_historydb_events_from_diff_for_kolonkish_creator_uid(self):
        def set_creator_uid():
            self.account.creator_uid = TEST_UID * 2

        name_and_value = {
            'account.creator_uid': str(TEST_UID * 2),
        }
        self.eq_historydb_events_from_diff(set_creator_uid, name_and_value)

    def test_historydb_events_from_diff_for_altdomain_alias_add(self):
        def add_altdomain_alias():
            self.account.altdomain_alias = AltDomainAlias(self.account, login='Galatasaray.Login@galatasaray.net')

        name_and_value = {
            'alias.altdomain.add': '1/galatasaray-login',
        }
        self.eq_historydb_events_from_diff(add_altdomain_alias, name_and_value)

    def test_historydb_events_from_diff_for_phonenumber_alias_add(self):
        def add_phonenumber_alias():
            self.account.phonenumber_alias = PhonenumberAlias(self.account, number=TEST_PHONE_NUMBER1)

        self.eq_historydb_events_from_diff(
            add_phonenumber_alias,
            {
                'alias.phonenumber.add': TEST_PHONE_NUMBER1.international,
            },
        )

    def test_historydb_events_from_diff_for_phonenumber_alias_add___search_enabled(self):
        def add_phonenumber_alias_with_enabled_search():
            self.account.phonenumber_alias = PhonenumberAlias(
                self.account,
                number=TEST_PHONE_NUMBER1,
                enable_search=True,
            )

        self.eq_historydb_events_from_diff(
            add_phonenumber_alias_with_enabled_search,
            {
                'alias.phonenumber.add': TEST_PHONE_NUMBER1.international,
                'info.phonenumber_alias_search_enabled': '1',
            },
        )

    def test_historydb_events_from_diff_for_phonenumber_alias_add___search_disabled(self):
        def add_phonenumber_alias_with_disabled_search():
            self.account.phonenumber_alias = PhonenumberAlias(
                self.account,
                number=TEST_PHONE_NUMBER1,
                enable_search=False,
            )

        self.eq_historydb_events_from_diff(
            add_phonenumber_alias_with_disabled_search,
            {
                'alias.phonenumber.add': TEST_PHONE_NUMBER1.international,
                'info.phonenumber_alias_search_enabled': '0',
            },
        )

    def test_historydb_events_from_diff_for_phonenumber_alias_change(self):
        def change_phonenumber_alias():
            self.account.phonenumber_alias.number = TEST_PHONE_NUMBER2

        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
        )

        self.eq_historydb_events_from_diff(
            change_phonenumber_alias,
            {
                'alias.phonenumber.change': TEST_PHONE_NUMBER2.international,
            },
        )

    def test_historydb_events_from_diff_for_turn_on_phonenumber_alias_search(self):
        def turn_on_phonenumber_alias_search():
            self.account.phonenumber_alias.enable_search = True

        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
        )

        self.eq_historydb_events_from_diff(
            turn_on_phonenumber_alias_search,
            {
                'info.phonenumber_alias_search_enabled': '1',
            },
        )

    def test_historydb_events_from_diff_for_turn_off_phonenumber_alias_search(self):
        def turn_off_phonenumber_alias_search():
            self.account.phonenumber_alias.enable_search = False

        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
            enable_search=True,
        )

        self.eq_historydb_events_from_diff(
            turn_off_phonenumber_alias_search,
            {
                'info.phonenumber_alias_search_enabled': '0',
            },
        )

    def test_historydb_events_from_diff_for_yandexoid_alias_add(self):
        def add_yandexoid_alias():
            self.account.yandexoid_alias = YandexoidAlias(self.account, login='Yandexoid.Login')

        name_and_value = {
            'alias.yandexoid.add': 'yandexoid-login',
        }
        self.eq_historydb_events_from_diff(add_yandexoid_alias, name_and_value)

    def test_historydb_events_from_diff_for_multiple_aliases_add(self):
        def add_aliases():
            self.account.yandexoid_alias = YandexoidAlias(self.account, login='yandexoid_login')
            self.account.altdomain_alias = AltDomainAlias(self.account, login='kp@kinopoisk.ru')
            phone = PhoneNumber.parse('+79030915478')
            self.account.phonenumber_alias = PhonenumberAlias(self.account, number=phone)

        name_and_value = {
            'alias.yandexoid.add': 'yandexoid_login',
            'alias.phonenumber.add': '+7 903 091-54-78',
            'alias.altdomain.add': '2/kp',
        }
        self.eq_historydb_events_from_diff(add_aliases, name_and_value)

    def test_historydb_events_from_diff_for_altdomain_alias_rm(self):
        """
        Тестируем удаление altdomain алиаса
        """
        self.account.altdomain_alias = AltDomainAlias(self.account, login='login@kinopoisk.ru')

        def delete_alias():
            self.account.altdomain_alias = None

        name_and_value = {
            'alias.altdomain.rm': '2/login',
        }
        self.eq_historydb_events_from_diff(delete_alias, name_and_value)

    def test_historydb_events_from_diff_for_phonenumber_alias_rm(self):
        """
        Тестируем удаление phonenumber алиаса
        """
        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
        )

        def delete_alias():
            self.account.phonenumber_alias = None

        self.eq_historydb_events_from_diff(
            delete_alias,
            {'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international},
        )

    def test_historydb_events_from_diff_for_phonenumber_alias_rm__search_disabled(self):
        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
            enable_search=False,
        )

        def delete_alias():
            self.account.phonenumber_alias = None

        self.eq_historydb_events_from_diff(
            delete_alias,
            {'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international},
        )

    def test_historydb_events_from_diff_for_phonenumber_alias_rm__search_enabled(self):

        self.account.phonenumber_alias = PhonenumberAlias(
            self.account,
            number=TEST_PHONE_NUMBER1,
            enable_search=True,
        )

        def delete_alias():
            self.account.phonenumber_alias = None

        self.eq_historydb_events_from_diff(
            delete_alias,
            {'alias.phonenumber.rm': TEST_PHONE_NUMBER1.international},
        )

    def test_historydb_events_from_diff_for_yandexoid_alias_rm(self):
        """
        Тестируем удаление yandexoid алиаса
        """
        self.account.yandexoid_alias = YandexoidAlias(self.account, login='yandexoid_login')

        def delete_alias():
            self.account.yandexoid_alias = None

        name_and_value = {
            'alias.yandexoid.rm': 'yandexoid_login',
        }
        self.eq_historydb_events_from_diff(delete_alias, name_and_value)

    def test_historydb_events_from_diff_for_altdomain_alias_not_exists_rm(self):
        """
        Тестируем удаление altdomain алиаса, а алиаса и не было
        """
        def delete_alias():
            self.account.altdomain_alias = None

        self.eq_historydb_events_from_diff(delete_alias, {})

    def test_historydb_events_from_diff_for_phonenumber_alias_not_exists_rm(self):
        """
        Тестируем удаление phonenumber алиаса, а алиаса и не было
        """
        def delete_alias():
            self.account.phonenumber_alias = None

        self.eq_historydb_events_from_diff(delete_alias, {})

    def test_historydb_events_from_diff_for_yandexoid_alias_not_exists_rm(self):
        """
        Тестируем удаление yandexoid алиаса, а алиаса и не было
        """
        def delete_alias():
            self.account.yandexoid_alias = None

        self.eq_historydb_events_from_diff(delete_alias, {})

    def test_historydb_events_from_diff_for_mailish_alias_not_exists_rm(self):
        """
        Тестируем удаление mailish алиаса, а алиаса и не было
        """
        def delete_alias():
            self.account.mailish_alias = None

        self.eq_historydb_events_from_diff(delete_alias, {})

    def test_pdd_alias_remove_multiple_additional_login(self):
        self.account.domain = Domain(id=1, domain='okna.ru')
        self.account.pdd_alias = PddAlias(self.account, email='Test.Login@okna.ru')
        self.account.pdd_alias.additional_logins.add('alias')
        self.account.pdd_alias.additional_logins.add('alias2')

        def set_remove_multiple_logins():
            for login in ['alias', 'alias2']:
                self.account.pdd_alias.additional_logins.remove(login)

        self.eq_historydb_events_from_diff(
            set_remove_multiple_logins,
            {
                'alias.pddalias.rm': 'alias@okna.ru,alias2@okna.ru',
            },
        )

    def test_modify_pdd_alias_additional_login(self):
        self.account.pdd_alias = PddAlias(self.account, email='Test.Login@okna.ru')
        self.account.domain = Domain(id=1, domain='okna.ru')

        self.eq_historydb_events_from_diff(
            lambda: self.account.pdd_alias.additional_logins.add('alias'),
            {
                'alias.pddalias.add': 'alias@okna.ru',
            },
        )

        self.eq_historydb_events_from_diff(
            lambda: self.account.pdd_alias.additional_logins.remove('alias'),
            {
                'alias.pddalias.rm': 'alias@okna.ru',
            },
        )

    def test_historydb_events_from_diff_for_bank_phonenumber_alias_add(self):
        def add_alias():
            self.account.bank_phonenumber_alias = BankPhoneNumberAlias(
                self.account,
                alias=TEST_PHONE_NUMBER1.digital,
            )

        self.eq_historydb_events_from_diff(
            add_alias,
            {'alias.bank_phonenumber.add': TEST_PHONE_NUMBER1.digital},
        )

    def test_historydb_events_from_diff_for_bank_phonenumber_alias_rm(self):
        self.account.bank_phonenumber_alias = BankPhoneNumberAlias(
            self.account,
            alias=TEST_PHONE_NUMBER1.digital
        )

        def delete_alias():
            self.account.bank_phonenumber_alias = None

        self.eq_historydb_events_from_diff(
            delete_alias,
            {'alias.bank_phonenumber.rm': '-'},
        )


class TestEmailsEventSerializer(BaseTestEventSerializer):
    def test_add_cyrillic_email(self):
        email = Email().parse({
            'address': u'админ@окна.рф',
            'id': 1,
        })

        def add_email():
            self.account.emails[email.address] = email

        self.eq_historydb_events_from_diff(
            add_email,
            {
                'email.1': 'created',
                'email.1.address': 'админ@окна.рф',
            },
        )

    def test_add_single_email(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'created': 12345,
            'unsafe': '1',
        })

        def add_email():
            self.account.emails[email.address] = email

        self.eq_historydb_events_from_diff(
            add_email,
            {
                'email.1': 'created',
                'email.1.address': 'admin@okna.ru',
                'email.1.is_unsafe': '1',
                'email.1.created_at': '12345',
            },
        )

    def test_change_single_email(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'created': 12345,
            'unsafe': '1',
        })
        self.account.emails[email.address] = email

        def change_email():
            email.is_unsafe = False

        self.eq_historydb_events_from_diff(
            change_email,
            {
                'email.1': 'updated',
                'email.1.address': 'admin@okna.ru',
                'email.1.is_unsafe': '0',
            },
        )

    def test_change_multiple_emails(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'unsafe': '1',
            'created': 12345,
        })
        email2 = Email().parse({
            'address': 'user@okna.ru',
            'id': 2,
            'unsafe': '1',
            'created': 12346,
        })
        old_email = Email().parse({
            'address': 'old@email.ru',
            'unsafe': '1',
            'created': 12346,
        })

        for instance in (email, email2, old_email):
            self.account.emails[instance.address] = instance

        def change_emails():
            for instance in (email, email2, old_email):
                self.account.emails[instance.address].is_unsafe = False

        self.eq_historydb_events_from_diff(
            change_emails,
            {
                'email.1': 'updated',
                'email.1.address': 'admin@okna.ru',
                'email.1.is_unsafe': '0',
                'email.2.address': 'user@okna.ru',
                'email.2': 'updated',
                'email.2.is_unsafe': '0',
            },
        )

    def test_remove_single_email(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'created': 12345,
        })
        self.account.emails[email.address] = email

        def remove_email():
            self.account.emails.pop(email.address)

        self.eq_historydb_events_from_diff(
            remove_email,
            {
                'email.1': 'deleted',
                'email.1.address': 'admin@okna.ru',
            },
        )

    def test_add_multiple_emails(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'unsafe': '1',
            'created': 12345,
        })
        email2 = Email().parse({
            'address': 'user@okna.ru',
            'id': 2,
            'created': 12346,
        })

        def add_email():
            for instance in (email, email2):
                self.account.emails[instance.address] = instance

        self.eq_historydb_events_from_diff(
            add_email,
            {
                'email.1': 'created',
                'email.1.address': 'admin@okna.ru',
                'email.1.is_unsafe': '1',
                'email.1.created_at': '12345',
                'email.2': 'created',
                'email.2.address': 'user@okna.ru',
                'email.2.created_at': '12346',
            },
        )

    def test_remove_multiple_emails(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'unsafe': '1',
            'created': 12345,
        })
        email2 = Email().parse({
            'address': u'тест@яндекс.рф',
            'id': 2,
            'created': 12346,
            'confirmed': 123467,
        })

        for instance in (email, email2):
            self.account.emails[instance.address] = instance

        def remove_multiple_emails():
            for instance in (email, email2):
                self.account.emails.pop(instance.address)

        self.eq_historydb_events_from_diff(
            remove_multiple_emails,
            {
                'email.1': 'deleted',
                'email.1.address': 'admin@okna.ru',
                'email.2': 'deleted',
                'email.2.address': 'тест@яндекс.рф',
            },
        )

    def test_remove_all_emails(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'unsafe': '1',
            'created': 12345,
        })
        email2 = Email().parse({
            'address': u'пользователь@окна.рф',
            'id': 2,
            'created': 12346,
        })

        for instance in (email, email2):
            self.account.emails.add(instance)

        def remove_all_emails():
            self.account.emails = None

        self.eq_historydb_events_from_diff(
            remove_all_emails,
            {
                'email.1': 'deleted',
                'email.1.address': 'admin@okna.ru',
                'email.2': 'deleted',
                'email.2.address': 'пользователь@окна.рф',
            },
        )

    def test_remove_all_emails_with_external(self):
        email = Email().parse({
            'address': 'admin@okna.ru',
            'id': 1,
            'unsafe': '1',
            'created': 12345,
        })
        email2 = Email().parse({
            'address': 'user@okna.ru',
            'id': 2,
            'created': 12346,
        })
        external = Email().parse({
            'address': 'old@okna.ru',
            'id': Undefined,
            'created': 12340,
        })

        for instance in (email, email2, external):
            self.account.emails.add(instance)

        def remove_all_emails():
            self.account.emails = None

        self.eq_historydb_events_from_diff(
            remove_all_emails,
            {
                'email.1': 'deleted',
                'email.1.address': 'admin@okna.ru',
                'email.2': 'deleted',
                'email.2.address': 'user@okna.ru',
            },
        )


class TestWebauthnCredentialsEventSerializer(BaseTestEventSerializer):
    def test_add_cred(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'public_key': '1:%s' % TEST_PUBLIC_KEY,
            'device_name': TEST_DEVICE_NAME,
            'sign_count': 42,
            'created': 12345,
            'relying_party_id': TEST_RP_ID,
            'os_family_id': 10,
            'browser_id': 11,
            'is_device_mobile': '1',
            'is_device_tablet': '1',
        })

        def add_cred():
            self.account.webauthn_credentials.add(cred)

        self.eq_historydb_events_from_diff(
            add_cred,
            {
                'webauthn_cred.1': 'created',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'webauthn_cred.1.public_key': TEST_PUBLIC_KEY,
                'webauthn_cred.1.device_name': TEST_DEVICE_NAME,
                'webauthn_cred.1.sign_count': '42',
                'webauthn_cred.1.created_at': '12345',
                'webauthn_cred.1.relying_party_id': TEST_RP_ID,
                'webauthn_cred.1.os_family_id': '10',
                'webauthn_cred.1.browser_id': '11',
                'webauthn_cred.1.is_device_mobile': '1',
                'webauthn_cred.1.is_device_tablet': '1',
            },
        )

    def test_add_multiple_creds(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'created': 12345,
        })
        cred2 = WebauthnCredential().parse({
            'id': 2,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
            'created': 12346,
        })

        def add_creds():
            for instance in (cred, cred2):
                self.account.webauthn_credentials.add(instance)

        self.eq_historydb_events_from_diff(
            add_creds,
            {
                'webauthn_cred.1': 'created',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'webauthn_cred.1.sign_count': '0',
                'webauthn_cred.1.created_at': '12345',
                'webauthn_cred.2': 'created',
                'webauthn_cred.2.external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
                'webauthn_cred.2.sign_count': '0',
                'webauthn_cred.2.created_at': '12346',
            },
        )

    def test_change_cred(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'public_key': '1:%s' % TEST_PUBLIC_KEY,
            'device_name': TEST_DEVICE_NAME,
            'sign_count': 42,
            'created': 12345,
        })
        self.account.webauthn_credentials.add(cred)

        def change_cred():
            cred.sign_count = 43

        self.eq_historydb_events_from_diff(
            change_cred,
            {
                'webauthn_cred.1': 'updated',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'webauthn_cred.1.sign_count': '43',
            },
        )

    def test_remove_single_cred(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'public_key': '1:%s' % TEST_PUBLIC_KEY,
            'device_name': TEST_DEVICE_NAME,
            'sign_count': 42,
            'created': 12345,
        })
        self.account.webauthn_credentials.add(cred)

        def remove_cred():
            self.account.webauthn_credentials.remove(cred.external_id)

        self.eq_historydb_events_from_diff(
            remove_cred,
            {
                'webauthn_cred.1': 'deleted',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            },
        )

    def test_remove_multiple_creds(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'created': 12345,
        })
        cred2 = WebauthnCredential().parse({
            'id': 2,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
            'created': 12346,
        })

        for instance in (cred, cred2):
            self.account.webauthn_credentials.add(instance)

        def remove_multiple_creds():
            for instance in (cred, cred2):
                self.account.webauthn_credentials.remove(instance.external_id)

        self.eq_historydb_events_from_diff(
            remove_multiple_creds,
            {
                'webauthn_cred.1': 'deleted',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'webauthn_cred.2': 'deleted',
                'webauthn_cred.2.external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
            },
        )

    def test_remove_all_creds(self):
        cred = WebauthnCredential().parse({
            'id': 1,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'created': 12345,
        })
        cred2 = WebauthnCredential().parse({
            'id': 2,
            'external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
            'created': 12346,
        })

        for instance in (cred, cred2):
            self.account.webauthn_credentials.add(instance)

        def remove_all_creds():
            self.account.webauthn_credentials = None

        self.eq_historydb_events_from_diff(
            remove_all_creds,
            {
                'webauthn_cred.1': 'deleted',
                'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                'webauthn_cred.2': 'deleted',
                'webauthn_cred.2.external_id': TEST_CREDENTIAL_EXTERNAL_ID + '2',
            },
        )


class TestUnsubscriptionFromMaillistsEventSerializer(BaseTestEventSerializer):
    @parameterized.expand([('1,2,3',), ('all',)])
    def test_set_unsubscribed_from_maillists(self, value):
        def set_unsubscribed():
            self.account.unsubscribed_from_maillists = UnsubscriptionList(value)

        self.eq_historydb_events_from_diff(
            set_unsubscribed,
            {
                'account.unsubscribed_from_maillists': value,
            },
        )

    def test_delete_unsubscribed_from_maillists(self):
        self.account.unsubscribed_from_maillists = UnsubscriptionList('1,2,3')

        def set_unsubscribed():
            self.account.unsubscribed_from_maillists = UnsubscriptionList('')

        self.eq_historydb_events_from_diff(
            set_unsubscribed,
            {
                'account.unsubscribed_from_maillists': '-',
            },
        )


@with_settings_hosts()
class TestLogEvents(TestCase):
    def setUp(self):
        self._faker = EventLoggerFaker()
        self._faker_tskv = EventLoggerTskvFaker()
        self._faker.start()
        self._faker_tskv.start()

    def tearDown(self):
        self._faker.stop()
        self._faker_tskv.stop()
        del self._faker
        del self._faker_tskv

    def test_no_users(self):
        log_events({}, TEST_USER_IP, TEST_USER_AGENT, TEST_YANDEXUID)
        eq_(self._faker.events, [])

    def test_no_events(self):
        log_events({TEST_UID: {}}, TEST_USER_IP, TEST_USER_AGENT, TEST_YANDEXUID)
        eq_(self._faker.events, [])

    def test_event(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
        )

        eq_(len(self._faker.events), 2)

        events = sorted(self._faker.events, key=attrgetter(u'name'))

        eq_(events[0].uid, str(TEST_UID))
        eq_(events[0].name, u'name')
        eq_(events[0].value, u'value')
        eq_(events[0].time, DatetimeNow())
        eq_(events[0].user_ip, TEST_USER_IP)

        eq_(events[1].uid, str(TEST_UID))
        eq_(events[1].name, u'user_agent')
        eq_(events[1].value, TEST_USER_AGENT)
        eq_(events[1].time, DatetimeNow())
        eq_(events[1].user_ip, TEST_USER_IP)

        eq_(events[0].time, events[1].time)

    def test_many_events(self):
        log_events(
            {
                TEST_UID: {
                    u'name1': u'value1',
                    u'name2': u'value2',
                },
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
        )

        eq_(len(self._faker.events), 3)

        events = sorted(self._faker.events, key=attrgetter(u'name'))

        eq_(events[0].uid, str(TEST_UID))
        eq_(events[0].name, u'name1')
        eq_(events[0].value, u'value1')

        eq_(events[1].uid, str(TEST_UID))
        eq_(events[1].name, u'name2')
        eq_(events[1].value, u'value2')

        eq_(events[2].name, u'user_agent')

        eq_(events[0].time, events[1].time)

    def test_many_users(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
                TEST_UID_EXTRA: {u'name': u'value'},
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
            initiator_uid=TEST_UID_EXTRA,
        )

        eq_(len(self._faker.events), 3)

        events = sorted(self._faker.events, key=attrgetter(u'uid', u'name'))

        eq_(events[0].uid, str(TEST_UID))
        eq_(events[0].name, u'name')
        # user_ip пишется только для initiator_uid
        eq_(events[0].user_ip, u'-')

        eq_(events[1].uid, str(TEST_UID_EXTRA))
        eq_(events[1].name, u'name')
        eq_(events[1].user_ip, TEST_USER_IP)

        # user_agent пишется только для initiator_uid
        eq_(events[2].uid, str(TEST_UID_EXTRA))
        eq_(events[2].name, u'user_agent')
        eq_(events[2].user_ip, TEST_USER_IP)

        eq_(events[0].time, events[1].time)

    def test_client_name(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
        )

        eq_(self._faker.events[0].client_name, 'passport')

    def test_yandexuid(self):
        log_events(
            {
                TEST_UID: {
                    u'action': u'value',
                    u'other': u'value',
                },
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
        )

        events = sorted(self._faker.events, key=attrgetter(u'name'))

        eq_(events[0].name, u'action')
        eq_(events[0].yandexuid, TEST_YANDEXUID)

        eq_(events[1].name, u'other')
        eq_(events[1].yandexuid, u'-')

        eq_(events[2].name, u'user_agent')
        eq_(events[2].yandexuid, u'-')

    def test_datetime(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
            datetime_=TEST_TIME,
        )

        events = self._faker.events
        eq_(events[0].time, TEST_TIME)
        eq_(events[1].time, TEST_TIME)

    def test_no_user_agent(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
            },
            TEST_USER_IP,
            None,
            TEST_YANDEXUID,
        )

        eq_(len(self._faker.events), 1)

    def test_too_long_user_agent(self):
        log_events(
            {
                TEST_UID: {u'name': u'value'},
            },
            TEST_USER_IP,
            u'x' * 250,
            TEST_YANDEXUID,
        )

        events = sorted(self._faker.events, key=attrgetter(u'name'))
        eq_(events[1].value, u'x' * 200)

    def test_admin_comment(self):
        log_events(
            {
                TEST_UID: {
                    u'action': u'action',
                    u'admin': u'admin',
                    u'comment': u'comment',
                },
            },
            TEST_USER_IP,
            TEST_USER_AGENT,
            TEST_YANDEXUID,
        )

        eq_(len(self._faker.events), 2)

        events = sorted(self._faker.events, key=attrgetter(u'name'))

        eq_(events[0].name, u'action')
        eq_(events[0].admin, u'admin')
        eq_(events[0].comment, u'comment')

        eq_(events[1].name, u'user_agent')
        eq_(events[1].admin, u'-')
        eq_(events[1].comment, u'-')


class TestAccountDeletionOperationSerializer(BaseTestEventSerializer):
    def setUp(self):
        super(TestAccountDeletionOperationSerializer, self).setUp()
        self._runner = HistorydbActionRunner({}, None, None, None, None, None)
        self._snapshot = self.account

    def _build_snapshot(self):
        self._snapshot = self.account.snapshot()

    def _serialize(self):
        return list(self._runner.serialize(self._snapshot, self.account, diff(self._snapshot, self.account)))

    def test_create(self):
        self._build_snapshot()
        self.account.deletion_operation = AccountDeletionOperation(self.account, started_at=datetime.now())

        eq_(self._serialize(), [('deletion_operation', 'created')])

    def test_delete(self):
        self.account.deletion_operation = AccountDeletionOperation(self.account, started_at=datetime.now())
        self._build_snapshot()
        self.account.deletion_operation = None

        eq_(self._serialize(), [('deletion_operation', 'deleted')])

    def test_update(self):
        self.account.deletion_operation = AccountDeletionOperation(self.account, started_at=datetime.now())
        self._build_snapshot()
        self.account.deletion_operation.started_at = TEST_DATETIME1

        eq_(
            self._serialize(),
            [
                ('deletion_operation', 'updated'),
                ('deletion_operation.started_at', str(TEST_DATETIME1)),
            ],
        )

    def test_not_changed(self):
        self.account.deletion_operation = AccountDeletionOperation(self.account, started_at=datetime.now())
        self._build_snapshot()

        eq_(self._serialize(), [])


class TestFamilySerializer(BaseTestEventSerializer):
    def setUp(self):
        self.family = FamilyInfo(
            _family_id=TEST_FAMILY_ID,
            admin_uid=TEST_UID,
        )
        self.family.members = {
            TEST_UID: FamilyMember(uid=TEST_UID, parent=self.family),
        }

    def eq_historydb_events_from_diff(self, modifying_function, expected_name_value, external_events=None):
        self._faker = EventLoggerFaker()
        self._faker_tskv = EventLoggerTskvFaker()
        self._faker.start()
        self._faker_tskv.start()
        s1 = self.family.snapshot() if self.family is not None else None
        modifying_function()
        s2 = self.family.snapshot() if self.family is not None else None
        run_historydb(
            s1,
            s2,
            diff(s1, s2),
            TEST_ENVIRONMENT,
            external_events if external_events is not None else {},
            10,
        )
        self._faker.assert_events_are_logged(expected_name_value)
        self._faker_tskv.assert_events_are_logged(expected_name_value)
        self._faker.stop()
        self._faker_tskv.stop()
        del self._faker
        del self._faker_tskv

    def test_create_family(self):
        _family = self.family
        self.family = None

        def modify():
            self.family = _family
            self.family.members[TEST_UID_EXTRA] = FamilyMember(
                uid=TEST_UID_EXTRA,
                parent=self.family,
            )

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_admin' % TEST_FAMILY_ID,
                'value': str(TEST_UID),
                'action': 'create',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID),
                'action': 'create',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID_EXTRA),
                'action': 'create',
                'uid': str(TEST_UID_EXTRA),
            },
        ])

    def test_delete_family(self):
        self.family.members[TEST_UID_EXTRA] = FamilyMember(
            uid=TEST_UID_EXTRA,
            parent=self.family,
        )

        def modify():
            self.family = None

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_admin' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID_EXTRA),
            },
        ])

    def test_change_family_admin(self):
        def modify():
            self.family.admin_uid = TEST_UID_EXTRA

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_admin' % TEST_FAMILY_ID,
                'value': str(TEST_UID_EXTRA),
                'action': 'change',
                'uid': str(TEST_UID_EXTRA),
            },
        ])

    def test_add_family_member(self):
        def modify():
            self.family.members[TEST_UID_EXTRA] = FamilyMember(
                uid=TEST_UID_EXTRA,
                parent=self.family,
            )

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID_EXTRA),
                'action': 'create',
                'uid': str(TEST_UID_EXTRA),
            },
        ])

    def test_delete_family_member(self):
        self.family.members[TEST_UID_EXTRA] = FamilyMember(
            uid=TEST_UID_EXTRA,
            parent=self.family,
        )

        def modify():
            del self.family.members[TEST_UID_EXTRA]

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID_EXTRA),
            },
        ])

    def test_delete_family_with_external(self):
        self.family.members[TEST_UID_EXTRA] = FamilyMember(
            uid=TEST_UID_EXTRA,
            parent=self.family,
        )

        def modify():
            self.family = None

        self.eq_historydb_events_from_diff(modify, [
            {
                'name': 'family.f%s.family_admin' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID),
            },
            {
                'name': 'external',
                'value': 'event',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.f%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'action': 'delete',
                'uid': str(TEST_UID_EXTRA),
            },
            {
                'name': 'external',
                'value': 'event',
                'uid': str(TEST_UID_EXTRA),
            },
        ], {'external': 'event'})
