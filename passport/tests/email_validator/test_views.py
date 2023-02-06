# -*- coding: utf-8 -*-

from datetime import datetime
import json
from xml.etree.ElementTree import fromstring

from lxml import etree
from lxml.html import document_fromstring as html_document_fromstring
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.account import default_account
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_track_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters.buckets import get_buckets
from passport.backend.core.eav_type_mapping import (
    EXTENDED_ATTRIBUTES_EMAIL_NAME_TO_TYPE_MAPPING as EMAIL_NAME_MAPPING,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.models.email import Email
from passport.backend.core.models.persistent_track import TRACK_TYPE_EMAIL_CONFIRMATION_CODE
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.email.email import mask_email_for_statbox
from passport.backend.core.types.login.login import masked_login
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
    zero_datetime,
)
from six.moves.urllib.parse import urlencode

from .base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_ADDRESS,
    TEST_ANOTHER_ADDRESS,
    TEST_ANOTHER_UID,
    TEST_BORN_DATE,
    TEST_CODE,
    TEST_CONSUMER_IP,
    TEST_EMAIL_ID,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_NATIVE_ADDRESS,
    TEST_PERSISTENT_TRACK_ID,
    TEST_SESSIONID,
    TEST_TTL,
    TEST_UID,
    TEST_USER_AGENT,
)


TEST_DOMAIN = 'ru'
TEST_SHORT_CODE = '12345'
TEST_OTHER_DOMAIN = 'com.tr'
TEST_PASSPORT_HOST = 'https://validator.yandex.%(tld)s'
TEST_RETPATH = 'https://www.ya.ru'
TEST_SUBJECT = u'Сабж'
TEST_OTHER_LANGUAGE = 'en'
TEST_NOT_SUPPORTED_LANGUAGE = 'tt'
TEST_TRANSLATIONS = {
    'word_of_caution': 'caution',
    'from_address': 'noreply@test.%TLD%',
    'farewell': 'farewell',
    'enable_2fa_today': '2fa',
    'restore_tips': 'tips',
    'from_name': 'Sender',

    'validation_message': '%MASKED_LOGIN% %SHORT_CODE% %VALIDATION_URL%',
    'deletion_message': '%ADDRESS% %MASKED_LOGIN%',
    'confirmation_message': '%ADDRESS% %MASKED_LOGIN%',

    'subject_confirmation': 'Confirmation',
    'subject_deletion': 'Deletion',
    'subject_validation': 'Validation',
}
TEST_NOTIFICATION_TRANSLATIONS = {
    'account_modification.collector_add.push.title': 'test_title {login}',
    'account_modification.collector_add.push.body': 'test_body {login}',
}

UNSAFE_ADDRESS_GRANT = 'email_validator.unsafe'
LINK_SEARCH_RE = r'(http[s]?://[a-zA-Z0-9\-\/\.]+\?[a-zA-Z0-9\&\=\%\.]+[^.\r\n])'


def get_mail_sent_per_uid_and_address_counter():
    return get_buckets(settings.VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER)


def get_mail_sent_per_uid_counter():
    return get_buckets(settings.VALIDATOR_EMAIL_SENT_PER_UID_COUNTER)


def max_out_counter(prefix, key):
    counter = get_buckets(prefix)
    remainder = counter.limit - counter.get(key)

    for i in range(remainder):
        counter.incr(key)
    return counter.get(key)


class MockTranslations(object):
    VALIDATOR = {
        'ru': TEST_TRANSLATIONS,
        'en': dict(
            TEST_TRANSLATIONS,
            subject_validation='English validation',
        ),
    }
    NOTIFICATIONS = {
        'ru': TEST_NOTIFICATION_TRANSLATIONS,
    }

    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


@with_settings_hosts(
    EMAIL_VALIDATOR_CONFIRMATION_CODE_TTL=TEST_TTL,
    PASSPORT_BASE_URL_TEMPLATE=TEST_PASSPORT_HOST,
    EMAIL_VALIDATOR_SHORT_CODE_LENGTH=5,
    translations=MockTranslations,
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'collector_add'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER=(24, 3600, 10),
        VALIDATOR_EMAIL_SENT_PER_UID_COUNTER=(24, 3600, 26),
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:collector_add': 5},
    )
)
class BaseLegacyViewTestCase(BaseMdapiTestCase, AccountModificationNotifyTestMixin):
    url = '/email-validator/validate.xml'

    def setUp(self):
        super(BaseLegacyViewTestCase, self).setUp()
        self.test_data = {
            'user_ip': TEST_IP,
            'consumer_ip': TEST_CONSUMER_IP,
            'cookie': '',
            'user_agent': TEST_USER_AGENT,
            'accept_language': TEST_ACCEPT_LANGUAGE,
            'host': 'yandex.ru',
        }

        self.generate_track_id_mock = mock.Mock(return_value=TEST_PERSISTENT_TRACK_ID)
        self.generate_track_id_patch = mock.patch(
            'passport.backend.core.models.persistent_track.generate_track_id',
            self.generate_track_id_mock,
        )

        self.code_generator_faker = CodeGeneratorFaker(TEST_SHORT_CODE)
        self.code_generator_faker.start()

        self.generate_track_id_patch.start()
        self.setup_statbox_templates()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.generate_track_id_patch.stop()
        self.code_generator_faker.stop()
        del self.generate_track_id_patch
        del self.code_generator_faker
        del self.generate_track_id_mock

        super(BaseLegacyViewTestCase, self).tearDown()

    def setup_statbox_templates(self):
        pass

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def check_validator_response(self, actual_content, expected):
        root = fromstring(actual_content)
        eq_(root.tag, 'page')

        children = list(root)
        eq_(
            len(children),
            1,
            'Validator response should have no more or less than one node:\n%s' % actual_content,
        )
        first_child = children[0]

        actual_content = {
            'tag': first_child.tag,
        }

        if first_child.attrib:
            actual_content['attrs'] = first_child.attrib

        if first_child.text:
            actual_content['text'] = first_child.text

        eq_(
            actual_content,
            expected,
        )

    def check_email_extended_attributes(self, data, db='passportdbshard1'):
        for attribute, expected_value in data.items():
            actual_value = self.env.db.get(
                'extended_attributes',
                'value',
                entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
                type=EMAIL_NAME_MAPPING[attribute],
                uid=TEST_UID,
                db=db,
            )
            eq_(
                actual_value,
                expected_value,
                'Extended attribute %r %s, but should be %r' % (
                    attribute,
                    ('equals %r' % actual_value) if actual_value else 'is missing',
                    expected_value,
                ),
            )

    def check_email_message_equals(self, message, recipient, subject, expected_body):
        eq_(message.recipients, [(u'', recipient)])
        eq_(message.subject, subject)

        ok_(
            '<!doctype html>' in message.body,
            'Message body should be HTML, but found:\n%s' % message.body,
        )

        # Игнорируем HTML-разметку и прочий мусор вроде пустых строк,
        # т.к. в данном случае нам важно знать какие конкретно тексты
        # пытается отправить валидатор.
        html = html_document_fromstring(message.body)
        body = etree.XPath('//body')(html)[0]
        actual_lines = [
            line.strip()
            for line in body.text_content().split('\n')
            if len(line.strip()) > 0
        ]

        eq_(
            actual_lines,
            expected_body,
            'Message text should be\n\n%s, but found:\n\n%s' % (
                '\n'.join(expected_body),
                '\n'.join(actual_lines),
            ),
        )

    def check_binding_exists(self, bound_at=zero_datetime, address=TEST_ADDRESS):
        self.env.db.check(
            'email_bindings',
            'bound',
            bound_at,
            uid=TEST_UID,
            address=address,
            email_id=TEST_EMAIL_ID,
            db='passportdbshard1',
        )

    def check_binding_does_not_exist(self, address=TEST_ADDRESS):
        self.env.db.check_missing(
            'email_bindings',
            'uid',
            uid=TEST_UID,
            address=address,
            email_id=TEST_EMAIL_ID,
            db='passportdbshard1',
        )

    def check_historydb_records(self, record, uid=TEST_UID):
        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in record if v is not None
        ]
        self.assert_events_are_logged(
            self.env.handle_mock,
            historydb_entries,
        )

    def prepare_testone_address_response(self, address=TEST_NATIVE_ADDRESS, native=True):
        response = {
            'users': [
                {
                    'address-list': [
                        {
                            'address': address,
                            'born-date': TEST_BORN_DATE,
                            'default': True,
                            'native': native,
                            'prohibit-restore': False,
                            'rpop': False,
                            'silent': False,
                            'unsafe': False,
                            'validated': True,
                        },
                    ],
                    'have_hint': False,
                    'have_password': True,
                    'id': str(TEST_UID),
                    'karma': {
                        'value': 0,
                    },
                    'karma_status': {
                        'value': 0,
                    },
                    'login': TEST_LOGIN,
                    'uid': {
                        'hosted': False,
                        'lite': False,
                        'value': str(TEST_UID),
                    },
                },
            ],
        }
        return json.dumps(response)

    def prepare_email_binding(self, address=TEST_ADDRESS, login=TEST_LOGIN, **kwargs):
        account = default_account(
            login,
            datetime.now(),
            {}, {},
        )
        email = Email(
            id=TEST_EMAIL_ID,
            address=address,
            **kwargs
        )
        account.emails.add(email)
        self.env.db._serialize_to_eav(account)

    def check_success_response(self, resp):
        raise NotImplementedError  # pragma: no cover

    def check_deletion_notification_mail_not_sent(self, lang=None):
        eq_(self.env.mailer.message_count, 0)

    def check_deletion_notification_mail_sent(self, lang=None):
        phrases = settings.translations.VALIDATOR[lang or 'ru']

        eq_(self.env.mailer.message_count, 3)

        for ind, (recipient, login) in enumerate([
            (TEST_ANOTHER_ADDRESS, masked_login(TEST_LOGIN)),
            (TEST_NATIVE_ADDRESS, TEST_LOGIN),
            (TEST_ADDRESS, masked_login(TEST_LOGIN)),
        ]):
            self.check_email_message_equals(
                self.env.mailer.messages[ind],
                recipient,
                phrases['subject_deletion'],
                [
                    '%s %s' % (TEST_ADDRESS, login),
                    phrases['word_of_caution'],
                    phrases['restore_tips'],
                    phrases['enable_2fa_today'],
                ],
            )


class TestLegacyAPIGrants(BaseLegacyViewTestCase):

    def setUp(self):
        super(TestLegacyAPIGrants, self).setUp()

        self.test_data['consumer_ip'] = TEST_IP

        self.get_consumers_mock = mock.Mock()
        self.get_consumers_mock.return_value = ['dev']
        self.get_consumers_by_ip_patch = mock.patch(
            'passport.backend.api.email_validator.base.determine_consumers_by_ip',
            self.get_consumers_mock,
        )
        self.get_consumers_by_ip_patch.start()
        self.env.grants.set_grant_list([])

        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

    def tearDown(self):
        self.get_consumers_by_ip_patch.stop()
        del self.get_consumers_by_ip_patch
        del self.get_consumers_mock
        super(TestLegacyAPIGrants, self).tearDown()

    def test_ok_many_consumers_one_with_grant(self):
        self.env.grants.set_grants_return_value({
            'consumer1': {
                'grants': {
                    'email_validator': [
                        'unsafe',
                        'api_getkey',
                    ],
                },
                'networks': [TEST_CONSUMER_IP],
            },
            'consumer2': {
                'grants': {},
                'networks': [],
            },
            'dev': {
                'grants': {},
                'networks': [],
            },
        })
        self.get_consumers_mock.return_value = [
            'consumer1',
            'consumer2',
            'dev',
        ]
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'false',
        })

        self.check_validator_response(
            resp.data,
            {
                'tag': 'validation-key',
                'text': TEST_CODE,
            },
        )

    def test_ok_many_consumers_all_with_grant(self):
        self.env.grants.set_grants_return_value({
            'consumer1': {
                'grants': {
                    'email_validator': [
                        'unsafe',
                        'api_getkey',
                    ],
                },
                'networks': [TEST_CONSUMER_IP],
            },
            'consumer2': {
                'grants': {
                    'email_validator': 'unsafe',
                },
                'networks': [],
            },
            'dev': {
                'grants': {
                    'email_validator': 'unsafe',
                },
                'networks': [],
            },
        })
        self.get_consumers_mock.return_value = [
            'consumer1',
            'consumer2',
            'dev',
        ]
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'false',
        })

        self.check_validator_response(
            resp.data,
            {
                'tag': 'validation-key',
                'text': TEST_CODE,
            },
        )

    def test_error_unsafe_flag_false_needs_grant(self):
        self.env.grants.set_grant_list(['email_validator.api_getkey'])
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'false',
        })

        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-no-grants',
                'attrs': {
                    'missing': UNSAFE_ADDRESS_GRANT,
                },
            },
        )

    def test_error_if_grant_require_tvm(self):
        self.env.grants.set_grants_return_value({
            'consumer1': {
                'client': {'client_id': 123},
                'grants': {
                    'email_validator': [
                        'unsafe',
                        'api_getkey',
                    ],
                },
                'networks': [TEST_CONSUMER_IP],
            },

        })
        self.get_consumers_mock.return_value = [
            'consumer1',
        ]
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'false',
        })

        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-no-grants',
                'attrs': {
                    'missing': 'email_validator.api_getkey',
                },
            },
        )


class TestAddRPOPView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_addrpop']

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'new_rpop_added',
            action='rpop_added',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_rpop_addition_recorded_to_statbox(self, address=TEST_ADDRESS):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                entity='account.emails',
                email_id=str(TEST_EMAIL_ID),
                operation='added',
                is_unsafe='1',
                is_rpop='1',
                ip=TEST_IP,
                consumer='-',
                user_agent='curl',
                new=mask_email_for_statbox(address),
                old='-',
                created_at=DatetimeNow(convert_to_datetime=True),
                bound_at=DatetimeNow(convert_to_datetime=True),
                confirmed_at=DatetimeNow(convert_to_datetime=True),
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'new_rpop_added',
                action='rpop_added',
            ),
        ])

    def check_historydb_recorded_modification(self, address=TEST_ADDRESS, is_rpop=True):
        record = [
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'updated'),
            ('email.%d.address' % TEST_EMAIL_ID, address),
            ('email.%d.bound_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.confirmed_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_rpop' % TEST_EMAIL_ID, '1' if is_rpop else None),
            ('user_agent', 'curl'),
        ]
        self.check_historydb_records(record)

    def check_historydb_recorded_addition(self, address=TEST_ADDRESS):
        record = [
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'created'),
            ('email.%d.address' % TEST_EMAIL_ID, address),
            ('email.%d.created_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.bound_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.confirmed_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_rpop' % TEST_EMAIL_ID, '1'),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1'),
            ('user_agent', 'curl'),
        ]
        self.check_historydb_records(record)

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-rpop-added',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )

    def test_error_address_is_native(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                ),
                self.prepare_testone_address_response(),
            ],
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Address %s valid as native.' % TEST_ADDRESS,
            },
        )

    def test_ok(self):
        self.setup_kolmogor()
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)
        self.check_rpop_addition_recorded_to_statbox()

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.check_email_extended_attributes({
            'is_rpop': '1',
            'is_unsafe': '1',
            'address': TEST_ADDRESS,
            'confirmed': TimeNow(),
            'bound': TimeNow(),
            'created': TimeNow(),
        })
        self.check_historydb_recorded_addition()
        self.check_binding_exists(bound_at=DatetimeNow())
        self.check_account_modification_push_sent(
            event_name='collector_add',
            uid=TEST_UID,
            ip=TEST_IP,
            title='test_title {}'.format(TEST_LOGIN),
            body='test_body {}'.format(TEST_LOGIN),
        )

    def test_ok_email_already_exists(self):
        self.setup_kolmogor()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        },
                    },
                ],
            ),
        )
        self.prepare_email_binding()

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_email_extended_attributes({
            'is_rpop': '1',
            'confirmed': TimeNow(),
            'bound': TimeNow(),
        })
        self.check_historydb_recorded_modification()
        self.check_binding_exists(bound_at=DatetimeNow())
        self.check_account_modification_push_sent(
            event_name='collector_add',
            uid=TEST_UID,
            ip=TEST_IP,
            title='test_title {}'.format(TEST_LOGIN),
            body='test_body {}'.format(TEST_LOGIN),
        )

    def test_error_emails_over_limit(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                email_attributes=[
                    {
                        'id': i,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: u'test_{}@another-yandex.ru'.format(i),
                        },
                    } for i in range(100)
                ],
            ),
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-error',
                'text': 'Bad things happened: email.limit_per_profile_reached',
            },
        )
        self.check_account_modification_push_not_sent()

    def test_ok_email_already_exists_and_rpop(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_rpop']: '1',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.prepare_email_binding(is_rpop=True)

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_email_extended_attributes({
            'confirmed': TimeNow(),
            'bound': TimeNow(),
        })
        self.check_historydb_recorded_modification(is_rpop=False)
        self.check_binding_exists(bound_at=DatetimeNow())
        self.check_account_modification_push_not_sent()

    def test_ok_email_already_exists_and_rpop_validated(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                            EMAIL_NAME_MAPPING['is_rpop']: '1',
                            EMAIL_NAME_MAPPING['confirmed']: '2',
                            EMAIL_NAME_MAPPING['bound']: '3',
                        },
                    },
                ],
            ),
        )
        self.prepare_email_binding(is_rpop=True)

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)

        self.check_email_extended_attributes({})
        self.check_historydb_records({})
        self.check_binding_exists()
        self.check_account_modification_push_not_sent()

    def test_push_counter_overflow__push_not_sent(self):
        self.setup_kolmogor(rate=6)
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'addrpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)
        self.check_account_modification_push_not_sent()


class TestGetConfirmationCodeView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_getkey']

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'get_key',
            action='get_key',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            address=mask_email_for_statbox(TEST_ADDRESS),
            is_unsafe='1',
            sessionid='0',
        )

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validation-key',
                'text': TEST_CODE,
            },
        )

    def check_historydb_recorded_addition(self, address=TEST_ADDRESS, is_unsafe=True):
        self.check_historydb_records((
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'created'),
            ('email.%d.address' % TEST_EMAIL_ID, address),
            ('email.%d.created_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1' if is_unsafe else '0'),
            ('user_agent', 'curl'),
        ))

    def check_confirmation_track_created(self, db='passportdbshard1'):
        self.env.db.check(
            'tracks',
            'uid',
            TEST_UID,
            track_id=str(TEST_PERSISTENT_TRACK_ID),
            content='{"address": "%s", "short_code": "%s", "type": %d}' % (
                TEST_ADDRESS,
                TEST_SHORT_CODE,
                TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
            ),
            db=db,
        )

    def check_key_generation_to_statbox(self, is_unsafe=True, with_sessionid=False):
        entries = []

        if with_sessionid:
            entry = self.env.statbox.entry('check_cookies')
            del entry['consumer']
            entries.append(entry)
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='account.emails',
                email_id=str(TEST_EMAIL_ID),
                operation='added',
                created_at=DatetimeNow(convert_to_datetime=True),
                is_unsafe='1' if is_unsafe else '0',
                ip=TEST_IP,
                old='-',
                new=mask_email_for_statbox(TEST_ADDRESS),
                consumer='-',
                user_agent='curl',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'get_key',
                sessionid='1' if with_sessionid else '0',
            ),
        ])
        self.env.statbox.assert_has_written(entries)

    def test_ok(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'true',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 3)
        self.check_email_extended_attributes({
            'is_unsafe': '1',
            'address': TEST_ADDRESS,
        })
        self.check_confirmation_track_created()
        self.check_binding_exists()
        self.check_key_generation_to_statbox()

        self.check_historydb_recorded_addition()

    def test_ok_unsafe_not_set(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.grants.set_grant_list([
            'email_validator.api_getkey',
            'email_validator.unsafe',
        ])

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'unsafe': 'false',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 3)
        self.check_email_extended_attributes({
            'is_unsafe': None,
            'address': TEST_ADDRESS,
        })
        self.check_confirmation_track_created()
        self.check_binding_exists()
        self.check_historydb_recorded_addition(is_unsafe=False)

    def test_ok_email_already_exists_unsafe_not_set(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                email_attributes=[
                    {
                        'id': TEST_EMAIL_ID,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        },
                    },
                ],
            ),
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 1)
        self.check_email_extended_attributes({
            'is_unsafe': None,
        })
        self.check_confirmation_track_created()

    def test_error_emails_over_limit(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                email_attributes=[
                    {
                        'id': i,
                        'attributes': {
                            EMAIL_NAME_MAPPING['address']: u'test_{}@domain'.format(i),
                        },
                    } for i in range(100)
                ],
            ),
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-error',
                'text': 'Bad things happened: email.limit_per_profile_reached',
            },
        )

    def test_ok_with_sessionid(self):
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'sessionid': TEST_SESSIONID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count('passportdbshard1'), 3)
        self.check_email_extended_attributes({
            'is_unsafe': '1',
            'address': TEST_ADDRESS,
        })
        self.check_confirmation_track_created()
        self.check_binding_exists()
        self.check_key_generation_to_statbox(with_sessionid=True)

        self.check_historydb_recorded_addition()

    def test_error_address_is_native(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                ),
                self.prepare_testone_address_response(),
            ],
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': TEST_ADDRESS,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Address %s valid as native.' % TEST_ADDRESS,
            },
        )

    def test_error_bad_email(self):
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'getkey',
            'email': 'asdbasdf;@',
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Bad e-mail format: asdbasdf;@',
            },
        )


class TestConfirmEmailByCodeView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_confirm']

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'confirmed_by_code',
            action='confirmed_by_code',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            keystring=TEST_PERSISTENT_TRACK_ID,
            is_unsafe='1',
            sessionid='0',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_confirmation_recorded_to_statbox(self, address=TEST_ADDRESS, with_sessionid=False):
        entries = []
        if with_sessionid:
            entry = self.env.statbox.entry('check_cookies')
            del entry['consumer']
            entries.append(entry)
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='account.emails',
                email_id=str(TEST_EMAIL_ID),
                operation='updated',
                ip=TEST_IP,
                new=mask_email_for_statbox(address),
                old=mask_email_for_statbox(address),
                consumer='-',
                user_agent='curl',
                bound_at=DatetimeNow(convert_to_datetime=True),
                confirmed_at=DatetimeNow(convert_to_datetime=True),
                is_unsafe='1',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'confirmed_by_code',
                sessionid='1' if with_sessionid else '0',
            ),
        ])
        self.env.statbox.assert_has_written(entries)

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-key-ok',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )

    def check_invalid_key_error_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-key-error',
                'attrs': {
                    'uid': str(TEST_UID),
                },
                'text': TEST_PERSISTENT_TRACK_ID,
            },
        )

    def check_email_already_validated_error_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-key-already-validated',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
                'text': TEST_PERSISTENT_TRACK_ID,
            },
        )

    def check_confirmation_message_sent(self):
        phrases = settings.translations.VALIDATOR['ru']
        eq_(self.env.mailer.message_count, 2)

        self.check_email_message_equals(
            self.env.mailer.messages[0],
            TEST_ADDRESS,
            phrases['subject_confirmation'],
            [
                '%s %s' % (TEST_ADDRESS, masked_login(TEST_LOGIN)),
            ],
        )

        self.check_email_message_equals(
            self.env.mailer.messages[1],
            TEST_NATIVE_ADDRESS,
            phrases['subject_confirmation'],
            [
                '%s %s' % (TEST_ADDRESS, TEST_LOGIN),
            ],
        )

    def test_ok(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '0',
                    },
                },
            ],
        )
        get_track_response = blackbox_get_track_response(
            uid=TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content={
                'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                'address': TEST_ADDRESS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )
        self.prepare_email_binding()

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.check_email_extended_attributes({
            'confirmed': TimeNow(),
            'bound': TimeNow(),
            'is_unsafe': '1',
        })

        self.check_historydb_records((
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'updated'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_ADDRESS),
            ('email.%d.bound_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.confirmed_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1'),
            ('user_agent', 'curl'),
        ))
        self.check_binding_exists(bound_at=DatetimeNow())
        self.check_confirmation_recorded_to_statbox()
        self.check_confirmation_message_sent()

    def test_ok_by_sessionid(self):
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '0',
                    },
                },
            ],
        )
        get_track_response = blackbox_get_track_response(
            uid=TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content={
                'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                'address': TEST_ADDRESS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )
        self.prepare_email_binding()

        resp = self.make_request(data={
            'sessionid': TEST_SESSIONID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.check_email_extended_attributes({
            'confirmed': TimeNow(),
            'bound': TimeNow(),
            'is_unsafe': '1',
        })

        self.check_historydb_records((
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'updated'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_ADDRESS),
            ('email.%d.bound_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.confirmed_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1'),
            ('user_agent', 'curl'),
        ))
        self.check_binding_exists(bound_at=DatetimeNow())
        self.check_confirmation_recorded_to_statbox(with_sessionid=True)
        self.check_confirmation_message_sent()

    def test_error_email_not_found(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: 'notfound@email.ru',
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
            ],
        )
        get_track_response = blackbox_get_track_response(
            uid=TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content={
                'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                'address': TEST_ADDRESS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })

        self.check_invalid_key_error_response(resp)

    def test_error_code_not_found(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
            ],
        )
        get_track_response = {}
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })

        self.check_invalid_key_error_response(resp)

    def test_error_invalid_track_type(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
            ],
        )
        get_track_response = blackbox_get_track_response(
            uid=TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content={
                'type': 12345,
                'address': TEST_ADDRESS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })

        self.check_invalid_key_error_response(resp)

    def test_error_email_already_validated(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                        EMAIL_NAME_MAPPING['confirmed']: '12345',
                    },
                },
            ],
        )
        get_track_response = blackbox_get_track_response(
            uid=TEST_UID,
            track_id=TEST_PERSISTENT_TRACK_ID,
            content={
                'type': TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
                'address': TEST_ADDRESS,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            get_track_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })

        self.check_email_already_validated_error_response(resp)

    def test_error_bad_uid(self):
        resp = self.make_request(data={
            'uid': 'abcdefg',
            'op': 'confirm',
            'key': TEST_PERSISTENT_TRACK_ID,
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Bad uid: abcdefg',
            },
        )

    def test_error_empty_key(self):
        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'confirm',
            'key': '',
            'host': TEST_HOST,
            'unsafe': 'true',
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Bad key!',
            },
        )


class TestDeleteUnsafeView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_deleteunsafe']

    def setUp(self):
        super(TestDeleteUnsafeView, self).setUp()
        self.prepare_email_binding(is_unsafe=True)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'delete',
            action='delete',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_deletion_logged_to_statbox(self, address=TEST_ADDRESS):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_unsafe='1',
                ip=TEST_IP,
                old=mask_email_for_statbox(address),
                new='-',
                operation='deleted',
                user_agent='curl',
                consumer='-',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry('delete'),
        ])

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )

    def check_no_notifications_sent(self):
        eq_(self.env.mailer.message_count, 0)

    def test_ok(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
                {
                    'address': TEST_ANOTHER_ADDRESS,
                    'validated': True,
                    'default': False,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': False,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleteunsafe',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_deletion_notification_mail_not_sent()
        self.check_email_extended_attributes({})
        self.check_binding_does_not_exist()
        self.check_deletion_logged_to_statbox()

    def test_error_email_is_not_unsafe(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleteunsafe',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'attrs': {
                    'address': TEST_ADDRESS,
                    'uid': str(TEST_UID),
                },
                'text': 'Address "%s" is not unsafe.' % TEST_ADDRESS,
            },
        )
        self.check_no_notifications_sent()

    def test_error_email_not_found(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleteunsafe',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )
        self.check_no_notifications_sent()


class TestDeleteRpopView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_deleterpop']

    def setUp(self):
        super(TestDeleteRpopView, self).setUp()
        self.prepare_email_binding(is_rpop=True)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'delete',
            action='delete',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_deletion_logged_to_statbox(self, address=TEST_ADDRESS):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_rpop='1',
                ip=TEST_IP,
                old=mask_email_for_statbox(address),
                new='-',
                operation='deleted',
                user_agent='curl',
                consumer='-',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry('delete'),
        ])

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )

    def check_no_notifications_sent(self):
        eq_(self.env.mailer.message_count, 0)

    def test_ok(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
                {
                    'address': TEST_ANOTHER_ADDRESS,
                    'validated': True,
                    'default': False,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': False,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_rpop']: '1',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleterpop',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_deletion_notification_mail_not_sent()
        self.check_email_extended_attributes({})
        self.check_binding_does_not_exist()
        self.check_deletion_logged_to_statbox()

    def test_error_email_is_not_rpop(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_rpop']: '0',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleterpop',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'attrs': {
                    'address': TEST_ADDRESS,
                    'uid': str(TEST_UID),
                },
                'text': 'Address "%s" is not rpop.' % TEST_ADDRESS,
            },
        )
        self.check_no_notifications_sent()

    def test_error_email_not_found(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'deleterpop',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )
        self.check_no_notifications_sent()


class TestDeleteEmailView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_delete']

    def setUp(self):
        super(TestDeleteEmailView, self).setUp()
        self.prepare_email_binding(is_unsafe=True)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'delete',
            action='delete',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_no_notifications_sent(self):
        eq_(self.env.mailer.message_count, 0)

    def check_deletion_logged_to_statbox(self, address=TEST_ADDRESS, is_confirmed=False):
        addendum = {}
        if is_confirmed:
            addendum['confirmed_at'] = datetime_to_string(unixtime_to_datetime(1))
            addendum['is_suitable_for_restore'] = '1'
        else:
            addendum['is_suitable_for_restore'] = '0'

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'account_modification',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                ip=TEST_IP,
                new='-',
                old=mask_email_for_statbox(address),
                operation='deleted',
                user_agent='curl',
                consumer='-',
                **addendum
            ),
            self.env.statbox.entry('delete'),
        ])

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )

    def check_deletion_recorded_to_historydb(self, address=TEST_ADDRESS):
        self.check_historydb_records([
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'deleted'),
            ('email.%d.address' % TEST_EMAIL_ID, address),
            ('user_agent', 'curl'),
        ])

    def test_ok(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_ANOTHER_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': False,
                },
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'delete',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_deletion_notification_mail_not_sent()
        self.check_email_extended_attributes({})
        self.check_binding_does_not_exist()
        self.check_deletion_logged_to_statbox()
        self.check_deletion_recorded_to_historydb()

    def test_ok_confirmed_email_notification_sent(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_ANOTHER_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': False,
                },
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['confirmed']: '1',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'delete',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.check_deletion_notification_mail_sent()
        self.check_deletion_logged_to_statbox(is_confirmed=True)
        self.check_deletion_recorded_to_historydb()
        self.check_email_extended_attributes({})
        self.check_binding_does_not_exist()

    def test_error_email_not_found(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'delete',
            'email': TEST_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-address-deleted',
                'attrs': {
                    'uid': str(TEST_UID),
                    'address': TEST_ADDRESS,
                },
            },
        )
        self.check_no_notifications_sent()


class TestValidateByEmailView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_validate']

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'validation_email_sent',
            action='validation_email_sent',
            uid=str(TEST_UID),
            mode='legacy_email_validator',
            keystring=TEST_PERSISTENT_TRACK_ID,
            unsafe='1',
            sessionid='1',
            created='1',
            address=mask_email_for_statbox(TEST_ADDRESS),
        )

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-request-sent-ok',
            },
        )

    def check_error_response(self, resp, tag=None, attrs=None):
        expected_response = dict(tag=tag or 'validator-error')
        if attrs:
            expected_response['attrs'] = attrs

        self.check_validator_response(
            resp.data,
            expected_response,
        )

    def check_validation_mail_sent(self, address=TEST_ADDRESS, language=None, tld=None):
        eq_(self.env.mailer.message_count, 1)
        message = self.env.mailer.messages[0]
        phrases = settings.translations.VALIDATOR[language or 'ru']

        eq_(message.recipients, [(u'', address)])
        eq_(message.subject, phrases['subject_validation'])

        eq_(
            message.sender[0].strip('"'),
            phrases['from_name'],
        )
        eq_(
            message.sender[1],
            settings.MAIL_DEFAULT_FROM_ADDRESS % (tld or 'ru'),
        )

    def check_mail_counters(self, address=TEST_ADDRESS, uid=TEST_UID):
        sent_per_uid_and_address = get_mail_sent_per_uid_and_address_counter().get('%d/%s' % (uid, address))
        sent_per_uid = get_mail_sent_per_uid_counter().get(str(uid))
        eq_(sent_per_uid, sent_per_uid_and_address)
        eq_(
            sent_per_uid_and_address,
            1,
            'Total count for address %s on UID %d should equal 1, but found %d' % (
                address,
                uid,
                sent_per_uid_and_address,
            ),
        )

    def check_nothing_happened(self, address=TEST_ADDRESS, uid=TEST_UID, sent_per_uid=0, sent_per_uid_and_address=0):
        eq_(self.env.mailer.message_count, 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        eq_(self.env.db.query_count('passportdbcentral'), 0)

        actually_sent_per_uid_and_address = get_mail_sent_per_uid_and_address_counter().get('%d/%s' % (uid, address))
        actually_sent_per_uid = get_mail_sent_per_uid_counter().get(str(uid))
        eq_(
            actually_sent_per_uid_and_address,
            sent_per_uid_and_address,
            'Expected to send %d messages per uid and address, but sent %d' % (
                sent_per_uid_and_address,
                actually_sent_per_uid_and_address,
            ),
        )
        eq_(
            actually_sent_per_uid,
            sent_per_uid,
            'Expected to send %d messages per uid, but sent %d' % (
                sent_per_uid,
                actually_sent_per_uid,
            ),
        )

        self.env.statbox.assert_equals([])
        self.check_historydb_records([])
        self.check_no_email_created()

    def check_new_email_added(self, is_unsafe=False, address=TEST_ADDRESS):
        historydb_record = [
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'created'),
            ('email.%d.address' % TEST_EMAIL_ID, address),
            ('email.%d.created_at' % TEST_EMAIL_ID, TimeNow()),
            ('email.%d.is_unsafe' % TEST_EMAIL_ID, '1' if is_unsafe else '0'),
            ('user_agent', 'curl'),
        ]

        db_record = {
            'address': address,
            'created': TimeNow(),
        }

        self.check_email_extended_attributes(db_record)
        self.check_historydb_records(historydb_record)

    def check_confirmation_track_created(self, uid=TEST_UID):
        self.env.db.check(
            'tracks',
            'content',
            '{"address": "%s", "short_code": "%s", "type": %d}' % (
                TEST_ADDRESS,
                TEST_SHORT_CODE,
                TRACK_TYPE_EMAIL_CONFIRMATION_CODE,
            ),
            uid=uid,
            track_id=TEST_PERSISTENT_TRACK_ID,
            db='passportdbshard1',
        )

    def check_no_email_created(self, address=TEST_ADDRESS):
        self.env.db.check_missing(
            'extended_attributes',
            'value',
            uid=TEST_UID,
            db='passportdbshard1',
        )

    def check_validation_with_creation_recorded_to_statbox(self, address=TEST_ADDRESS,
                                                           is_unsafe=False,
                                                           with_sessionid=False, host='passport-test.yandex.ru'):
        entries = []
        if with_sessionid:
            check_cookeis_entry = self.env.statbox.entry('check_cookies')
            del check_cookeis_entry['consumer']
            check_cookeis_entry['host'] = host
            entries.append(check_cookeis_entry)
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='account.emails',
                created_at=DatetimeNow(convert_to_datetime=True),
                is_unsafe='1' if is_unsafe else '0',
                uid=str(TEST_UID),
                ip=TEST_IP,
                user_agent='curl',
                operation='added',
                old='-',
                new=mask_email_for_statbox(address),
                consumer='-',
                email_id=str(TEST_EMAIL_ID),
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'validation_email_sent',
                unsafe='1' if is_unsafe else '0',
                sessionid='1' if with_sessionid else '0',
            ),
        ])
        self.env.statbox.assert_equals(entries)

    def check_validation_recorded_to_statbox(self, address=TEST_ADDRESS,
                                             is_unsafe=False,
                                             with_sessionid=False):
        self.env.statbox.assert_equals([
            self.env.statbox.entry(
                'validation_email_sent',
                created='0',
                unsafe='1' if is_unsafe else '0',
                sessionid='1' if with_sessionid else '0',
            ),
        ])

    def check_sent_validation_link(self, host=None, uid=TEST_UID,
                                   key=TEST_PERSISTENT_TRACK_ID,
                                   retpath=None, tld=TEST_DOMAIN,
                                   language=None):
        message = self.env.mailer.messages[0]
        if not host:
            host = TEST_PASSPORT_HOST % dict(tld=tld)
        query = {
            'key': key,
            'mode': 'changeemails',
        }
        if retpath:
            query['retpath'] = retpath
        expected_url = '%s/passport?%s' % (host, urlencode(query))

        phrases = settings.translations.VALIDATOR[language or 'ru']
        self.check_email_message_equals(
            message,
            TEST_ADDRESS,
            phrases['subject_validation'],
            [
                '%s %s %s' % (masked_login(TEST_LOGIN), TEST_SHORT_CODE, expected_url),
            ],
        )

    def test_ok_email_not_found_and_created(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent()
        self.check_sent_validation_link()
        self.check_new_email_added()
        self.check_confirmation_track_created()
        self.check_validation_with_creation_recorded_to_statbox()

    def test_ok_email_not_found_and_created_by_sessionid(self):
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.prepare_testone_address_response(
                address=TEST_ADDRESS,
                native=False,
            ),
        )

        resp = self.make_request(data={
            'sessionid': TEST_SESSIONID,
            'host': 'yandex.ru',
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent()
        self.check_sent_validation_link()
        self.check_new_email_added()
        self.check_confirmation_track_created()
        self.check_validation_with_creation_recorded_to_statbox(
            with_sessionid=True,
            host='yandex.ru',
        )

    def test_ok_email_exists(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent()
        self.check_sent_validation_link()
        self.check_no_email_created()
        self.check_confirmation_track_created()
        self.check_validation_recorded_to_statbox()

    def test_error_email_exists_and_already_confirmed(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['confirmed']: '12345',
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_error_response(resp)

        self.check_nothing_happened()

    def test_error_email_is_native(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    email_attributes=[
                        {
                            'id': TEST_EMAIL_ID,
                            'attributes': {
                                EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                                EMAIL_NAME_MAPPING['confirmed']: '12345',
                            },
                        },
                    ],
                ),
                self.prepare_testone_address_response(),
            ],
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_NATIVE_ADDRESS,
        })
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-invalid-argument',
                'text': 'Address test@yandex.ru valid as native.',
            },
        )
        self.check_nothing_happened()

    def test_ok_email_exists_so_increase_counters(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)
        self.check_mail_counters()

    def test_error_email_exists_and_too_many_messages_sent(self):
        maxed_value = max_out_counter(
            settings.VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER,
            '%d/%s' % (TEST_UID, TEST_ADDRESS),
        )
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_error_response(
            resp,
            'validator-already-sent-error',
            attrs={'retry-in': '15'},
        )

        self.check_nothing_happened(sent_per_uid_and_address=maxed_value)

    def test_error_email_exists_and_too_many_messages_sent_per_uid(self):
        maxed_value = max_out_counter(
            settings.VALIDATOR_EMAIL_SENT_PER_UID_COUNTER,
            str(TEST_UID),
        )
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_error_response(
            resp,
            'validator-already-sent-error',
            attrs={'retry-in': '15'},
        )

        self.check_nothing_happened(sent_per_uid=maxed_value)

    def test_ok_email_exists_and_too_many_messages_sent_but_force_is_with_us(self):
        max_out_counter(
            settings.VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER,
            '%d/%s' % (TEST_UID, TEST_ADDRESS),
        )
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'force': 'true',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

    def test_ok_one_uid_maxed_out_but_another_one_looks_good(self):
        max_out_counter(
            settings.VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER,
            '%d/%s' % (TEST_ANOTHER_UID, TEST_ADDRESS),
        )
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
        })
        self.check_success_response(resp)

    def test_ok_email_sent_with_retpath(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
            'retpath': TEST_RETPATH,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent()
        self.check_sent_validation_link(retpath=TEST_RETPATH)

    def test_ok_domain_changes_validator_tld(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
            'domain': TEST_OTHER_DOMAIN,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent(tld=TEST_OTHER_DOMAIN)
        self.check_sent_validation_link(tld=TEST_OTHER_DOMAIN)

    def test_ok_lang_changes_mail_contents_not_tld(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
            'lang': TEST_OTHER_LANGUAGE,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent(
            tld=TEST_DOMAIN,
            language=TEST_OTHER_LANGUAGE,
        )
        self.check_sent_validation_link(
            tld=TEST_DOMAIN,
            language=TEST_OTHER_LANGUAGE,
        )

    def test_ok_not_supported_lang(self):
        userinfo_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            email_attributes=[],
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request(data={
            'uid': TEST_UID,
            'op': 'validate',
            'email': TEST_ADDRESS,
            'lang': TEST_NOT_SUPPORTED_LANGUAGE,
        })
        self.check_success_response(resp)

        self.check_validation_mail_sent(
            tld=TEST_DOMAIN,
            language=TEST_ACCEPT_LANGUAGE,
        )
        self.check_sent_validation_link(
            tld=TEST_DOMAIN,
            language=TEST_ACCEPT_LANGUAGE,
        )


class TestDeleteAllEmailsView(BaseLegacyViewTestCase):
    mocked_grants = ['email_validator.api_deleteemails']

    def check_basic_recorded_to_statbox(self):
        entry = self.env.statbox.entry('check_cookies')
        del entry['consumer']
        self.env.statbox.assert_has_written([
            entry,
            self.env.statbox.entry(
                'deleteemails',
                action='deleteall',
                mode='legacy_email_validator',
                uid=str(TEST_UID),
            ),
        ])

    def check_deletion_recorded_to_statbox(self):
        check_cookies_entry = self.env.statbox.entry('check_cookies')
        del check_cookies_entry['consumer']
        self.env.statbox.assert_has_written([
            check_cookies_entry,
            self.env.statbox.entry(
                'account_modification',
                email_id=str(TEST_EMAIL_ID + 1),
                entity='account.emails',
                ip=TEST_IP,
                new='-',
                old=mask_email_for_statbox('test.' + TEST_ADDRESS),
                operation='deleted',
                user_agent='curl',
                consumer='-',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'account_modification',
                email_id=str(TEST_EMAIL_ID),
                entity='account.emails',
                is_unsafe='1',
                ip=TEST_IP,
                new='-',
                old=mask_email_for_statbox(TEST_ADDRESS),
                operation='deleted',
                user_agent='curl',
                consumer='-',
                is_suitable_for_restore='0',
            ),
            self.env.statbox.entry(
                'deleteemails',
                action='deleteall',
                mode='legacy_email_validator',
                uid=str(TEST_UID),
            ),
        ])

    def check_success_response(self, resp):
        self.check_validator_response(
            resp.data,
            {
                'tag': 'validator-emails-deleted',
            },
        )

    def test_ok_deleted_only_external_emails_from_extended_attributes(self):
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                {
                    'address': TEST_ANOTHER_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': False,
                },
                {
                    'address': TEST_NATIVE_ADDRESS,
                    'validated': True,
                    'default': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                    'native': True,
                },
            ],
            email_attributes=[
                {
                    'id': TEST_EMAIL_ID,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: TEST_ADDRESS,
                        EMAIL_NAME_MAPPING['is_unsafe']: '1',
                    },
                },
                {
                    'id': TEST_EMAIL_ID + 1,
                    'attributes': {
                        EMAIL_NAME_MAPPING['address']: 'test.' + TEST_ADDRESS,
                    },
                },
            ],
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(data={
            'sessionid': TEST_SESSIONID,
            'host': TEST_HOST,
            'op': 'deleteemails',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)
        self.check_historydb_records([
            ('action', 'validator'),
            ('email.%d' % TEST_EMAIL_ID, 'deleted'),
            ('email.%d.address' % TEST_EMAIL_ID, TEST_ADDRESS),
            ('email.%d' % (TEST_EMAIL_ID + 1), 'deleted'),
            ('email.%d.address' % (TEST_EMAIL_ID + 1), 'test.' + TEST_ADDRESS),
            ('user_agent', 'curl'),
        ])
        self.check_deletion_recorded_to_statbox()

    def test_ok_nothing_deleted(self):
        sessionid_response = blackbox_sessionid_multi_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_response,
        )

        resp = self.make_request(data={
            'sessionid': TEST_SESSIONID,
            'host': TEST_HOST,
            'op': 'deleteemails',
        })
        self.check_success_response(resp)

        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 0)
        self.check_historydb_records([])
        self.check_basic_recorded_to_statbox()
