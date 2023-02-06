# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.api.tests.views.bundle.register.test.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_hosted_domains_response,
    blackbox_lrandoms_response,
    blackbox_phone_bindings_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.phones.faker import assert_secure_phone_bound
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.bit_vector.bit_vector import PhoneBindingsFlags
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.string import smart_text


MAIL_SID = 2
PDD_ADMIN_SID = 104
PDD_EULA_ACCEPTED_SID = 102

TEST_COOKIE_TIMESTAMP = 1383144488

TEST_CYRILLIC_UPPER_DOMAIN = u'яндекс.директория.рф'
TEST_CYRILLIC_DOMAIN = u'поддомен.%s' % TEST_CYRILLIC_UPPER_DOMAIN

TEST_DOMAIN_ID = 1

TEST_UPPER_DOMAIN = 'directory.yandex.ru'
TEST_DOMAIN = 'domain.%s' % TEST_UPPER_DOMAIN
TEST_LOGIN = '--login.-.login123'
TEST_HUMAN_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_CYRILLIC_HUMAN_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_CYRILLIC_DOMAIN)
TEST_FIRSTNAME = 'first'
TEST_LASTNAME = 'last'
TEST_ORGANIZATION = u'Организация'
TEST_PASSWORD = 'qaz123wsx456edc789'
TEST_PASSWORD_QUALITY = 100
TEST_PDD_TEMPLATE = 't:%pdd_username%@%display_domain%'
TEST_PHONE_NUMBER = PhoneNumber.parse('+79033215555')
TEST_RESTRICTED_DIRECTORY_SUBDOMAIN = 'biz'

TEST_APPROVED_DOMAIN_NAMES = [
    'директория.яндекс.рф',
    'directory.yandex.ru',
]

TEST_HOST = 'yandex.ru'
TEST_USER_IP = '3.3.3.3'
TEST_USER_AGENT = 'curl'
TEST_USER_LOGIN = 'testlogin'
TEST_UID = TEST_SUID = 1130000000000001


@with_settings_hosts(
    DOMAINS_USED_BY_DIRECTORY=[TEST_UPPER_DOMAIN, TEST_CYRILLIC_UPPER_DOMAIN],
    RESTRICTED_DIRECTORY_SUBDOMAINS=[TEST_RESTRICTED_DIRECTORY_SUBDOMAIN],
    OPTIONS_USE_NEW_SERIALIZATION_SCHEME=True,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
class TestAccountRegisterDirectoryView(BaseMdapiTestCase,
                                       make_clean_web_test_mixin('test_ok', ['firstname', 'lastname'], statbox_action='submitted'),
                                       ):
    url = '/1/bundle/account/register/directory/?consumer=dev'
    mocked_grants = {
        'account': 'register_directory',
    }
    form_data = {
        'domain': TEST_DOMAIN,
        'firstname': TEST_FIRSTNAME,
        'lastname': TEST_LASTNAME,
        'login': TEST_LOGIN,
        'organization': TEST_ORGANIZATION,
        'password': TEST_PASSWORD,
        'eula_accepted': 'true',
    }
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        super(TestAccountRegisterDirectoryView, self).setUp()
        self.setup_trackid_generator()
        self.form_data['track_id'] = self.track_id
        self.setup_statbox_templates()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value(
            u'check',
            u'<spamlist></spamlist>',
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )

    def tearDown(self):
        del self.track_id_generator
        super(TestAccountRegisterDirectoryView, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='account_register_directory',
            track_id=self.track_id,
            ip=TEST_USER_IP,
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'pdd_alias_added',
            event='account_modification',
            ip=TEST_USER_IP,
            user_agent='curl',
            consumer='dev',
            entity='aliases',
            operation='added',
            uid=str(TEST_UID),
            type=str(ANT['pdd']),
            value='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'domain_modification',
            consumer='dev',
            domain_id=str(TEST_DOMAIN_ID),
            old='-',
            event='domain_modification',
            user_agent='curl',
            ip=TEST_USER_IP,
            operation='created',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            consumer='dev',
            old='-',
            event='account_modification',
            user_agent='curl',
            ip=TEST_USER_IP,
            operation='created',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'account_created',
            _inherit_from='local_base',
            action='account_created',
            uid=str(TEST_UID),
            country='ru',
            login=TEST_HUMAN_LOGIN,
            domain=TEST_DOMAIN,
        )
        self.env.statbox.bind_entry(
            'subscription_created',
            _inherit_from='account_modification',
            _exclude=['old'],
            entity='subscriptions',
            operation='added',
        )

        phone_env = dict(
            mode='account_register_directory',
            track_id=self.track_id,
            ip=TEST_USER_IP,
            user_agent='curl',
            number=TEST_PHONE_NUMBER.masked_format_for_statbox,
            login=TEST_HUMAN_LOGIN,
            uid=str(TEST_UID),
            _exclude=['operation_id', 'consumer'],
        )
        self.env.statbox.bind_entry(
            'phone_confirmed',
            code_checks_count='0',
            **phone_env
        )
        self.env.statbox.bind_entry(
            'secure_phone_bound',
            **phone_env
        )

    def check_counters(self):
        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)
        eq_(counter.get(TEST_USER_IP), 1)

    def check_statbox_entries(self, domain=TEST_DOMAIN, organization=None):
        expected_entries = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_name',
                new='domain.directory.yandex.ru',
            ),
            self.env.statbox.entry(
                'domain_modification',
                entity='domain_organization_name',
                new=organization,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                old='-',
                new='enabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                entity='account.mail_status',
                old='-',
                new='active',
            ),
            self.env.statbox.entry('pdd_alias_added'),
            self.env.statbox.entry(
                'account_modification',
                entity='phones.secure',
                new=TEST_PHONE_NUMBER.masked_format_for_statbox,
                old_entity_id='-',
                new_entity_id='1',
            ),
        ]

        modified_entries = [
            ('person.firstname', TEST_FIRSTNAME),
            ('person.lastname', TEST_LASTNAME),
            ('person.language', 'ru'),
            ('person.country', 'ru'),
            ('person.fullname', '{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME)),
            ('domain_name', 'domain.directory.yandex.ru'),
            ('domain_id', str(TEST_DOMAIN_ID)),
        ]

        if organization:
            modified_entries.append(('domain_organization_name', smart_text(organization)))

        for entity, value in modified_entries:
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=value,
                ),
            )

        expected_entries.extend([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='password.encrypted',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.encoding_version',
                new=str(self.password_hash_version),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.quality',
                new=str(TEST_PASSWORD_QUALITY),
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['operation'],
                action='account_create_directory',
                entity='karma',
                destination='frodo',
                registration_datetime=DatetimeNow(convert_to_datetime=True),
                login=TEST_HUMAN_LOGIN,
                suid=str(TEST_SUID),
                new='0',
            ),
            self.env.statbox.entry(
                'subscription_created',
                sid='104',
            ),
            self.env.statbox.entry(
                'subscription_created',
                sid='2',
                suid=str(TEST_SUID),
            ),
            self.env.statbox.entry(
                'subscription_created',
                sid='102',
            ),
            self.env.statbox.entry(
                'account_created',
                domain=domain,
            ),
            self.env.statbox.entry(
                'phone_confirmed',
                _exclude=['operation_id', 'consumer'],
            ),
            self.env.statbox.entry(
                'secure_phone_bound',
                _exclude=['operation_id', 'consumer'],
            ),
        ])

        self.env.statbox.assert_has_written(expected_entries)

    def check_yasms_not_called(self):
        requests = self.env.yasms.requests
        eq_(len(requests), 0)

    def check_historydb_entries(self, uid, login=TEST_LOGIN, domain=TEST_DOMAIN, user_defined_login=None):
        # Проверим, что пароль пользователю был установлен корректно.
        eav_pass_hash = self.env.db.get(
            'attributes',
            'password.encrypted',
            uid=uid,
            db='passportdbshard2',
        )

        encoded_domain = domain.encode('utf-8')
        historydb_record = [
            ('info.login', '%s@%s' % (login, encoded_domain)),
        ]
        if user_defined_login is not None:
            historydb_record.append(
                ('info.login_wanted', user_defined_login),
            )
        historydb_record += [
            ('info.ena', '1'),
            ('info.disabled_status', '0'),
            ('info.reg_date', DatetimeNow(convert_to_datetime=True)),
            ('info.is_connect_admin', '1'),
            ('info.mail_status', '1'),
            ('info.firstname', TEST_FIRSTNAME),
            ('info.lastname', TEST_LASTNAME),
            ('info.country', 'ru'),
            ('info.tz', 'America/New_York'),
            ('info.lang', 'ru'),
            ('info.domain_name', domain.encode('idna')),
            ('info.domain_id', '1'),
            ('info.password', eav_pass_hash),
            ('info.password_quality', str(TEST_PASSWORD_QUALITY)),
            ('info.password_update_time', TimeNow()),
            ('info.karma_prefix', '0'),
            ('info.karma_full', '0'),
            ('info.karma', '0'),
            ('alias.pdd.add', '1/--login.-.login123'),
            ('mail.add', '%d' % uid),
            ('sid.add', '%s,%s,%s' % (PDD_ADMIN_SID, MAIL_SID, PDD_EULA_ACCEPTED_SID)),
            ('phone.1.action', 'created'),
            ('phone.1.bound', TimeNow()),
            ('phone.1.confirmed', TimeNow()),
            ('phone.1.created', TimeNow()),
            ('phone.1.number', TEST_PHONE_NUMBER.e164),
            ('phone.1.secured', TimeNow()),
            ('phones.secure', '1'),
            ('action', 'account_create_directory'),
            ('consumer', 'dev'),
            ('user_agent', 'curl'),
        ]
        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record
        ]

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            historydb_entries,
        )

    def check_db_entries(self, uid=TEST_UID, domain=TEST_DOMAIN,
                         domain_id=TEST_DOMAIN_ID, login=TEST_LOGIN,
                         organization=TEST_ORGANIZATION, user_defined_login=None):
        present_attributes = [
            ('account.is_pdd_admin', '1'),
            ('account.is_connect_admin', '1'),
            ('account.registration_datetime', TimeNow()),
            ('password.update_datetime', TimeNow()),
            ('password.quality', '3:%d' % TEST_PASSWORD_QUALITY),
            ('person.firstname', TEST_FIRSTNAME),
            ('person.lastname', TEST_LASTNAME),
            ('person.timezone', 'America/New_York'),
        ]

        missing_attributes = [
            'hint.question.serialized',
            'hint.answer.encrypted',
            'karma.value',
            'password.forced_changing_reason',
            'subscription.mail.login_rule',
            'person.birthday',
            'person.country',
            'person.language',
            'person.gender',
        ]

        if user_defined_login is not None:
            present_attributes.append(
                ('account.user_defined_login', user_defined_login),
            )
        else:
            missing_attributes.append('account.user_defined_login')

        for attribute_name, value in present_attributes:
            self.env.db.check(
                'attributes',
                attribute_name,
                value,
                uid=uid,
                db='passportdbshard2',
            )

        for attribute_name in missing_attributes:
            self.env.db.check_missing(
                'attributes',
                attribute_name,
                uid=uid,
                db='passportdbshard2',
            )

        # Проверяем, что домен создался
        options = {'2': organization}

        self.env.db.check(
            'domains',
            'name',
            domain,
            admin_uid=uid,
            options=json.dumps(options),
            db='passportdbcentral',
        )

        # Проверяем, что алиас создался
        self.env.db.check(
            'aliases',
            'value',
            '%i/%s' % (domain_id, login),
            uid=uid,
            db='passportdbcentral',
        )
        # Проверяем, что портальный алиас _не_ создался
        self.env.db.check_missing(
            'aliases',
            'portal',
            uid=uid,
            db='passportdbcentral',
        )

        binding_flags = PhoneBindingsFlags()
        binding_flags.should_ignore_binding_limit = False
        assert_secure_phone_bound.check_db(
            self.env.db,
            uid=uid,
            phone_attributes={
                'id': 1,
                'number': TEST_PHONE_NUMBER.e164,
                'created': DatetimeNow(),
                'bound': DatetimeNow(),
                'confirmed': DatetimeNow(),
                'secured': DatetimeNow(),
            },
            binding_flags=binding_flags,
            shard_db='passportdbshard2',
        )

        # Информация о доменах хранится на центральном узле БД
        eq_(self.env.db.query_count('passportdbcentral'), 8)
        # Информация о подписках ПДД-пользователя хранится на ином шарде.
        eq_(self.env.db.query_count('passportdbshard2'), 5)

    def check_error_response(self, response, errors):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'error')
        eq_(
            response_data['errors'],
            errors,
        )
        return response_data

    def check_track(self, login=TEST_LOGIN, domain=TEST_DOMAIN, user_defined_login=TEST_LOGIN):
        track = self.track_manager.read(self.track_id)

        ok_(track.allow_authorization)
        ok_(track.is_successful_registered)
        eq_(track.domain, domain)
        eq_(track.uid, str(TEST_UID))
        eq_(
            track.login,
            u'%s@%s' % (user_defined_login, domain),
        )
        eq_(
            track.human_readable_login,
            u'%s@%s' % (login, domain),
        )
        eq_(
            track.machine_readable_login,
            u'%s@%s' % (login, domain.encode('idna')),
        )
        eq_(track.is_password_passed, True)
        eq_(track.have_password, True)
        eq_(track.is_otp_restore_passed, False)
        eq_(track.country, 'ru')

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests

        frodo_args = {
            'action': 'directoryreg',
            'consumer': 'dev',
            'fname': TEST_LASTNAME,
            'fuid': u'fuid',
            'hinta': u'0.0.0.0.0.0',
            'hintaex': u'0.0.0.0.0.0',
            'hintq': u'0.0.0.0.0.0',
            'hintqex': u'0.0.0.0.0.0',
            'host': u'passport-test.yandex.ru',
            'iname': u'first',
            'ip_from': TEST_USER_IP,
            'host': u'passport-test.yandex.ru',
            'iname': TEST_FIRSTNAME,
            'ip_from': TEST_USER_IP,
            'lang': 'ru',
            'login': u'%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            'uid': str(TEST_UID),
            'passwd': u'18.0.9.9',
            'passwdex': u'2.7.0.0',
            'phonenumber': TEST_PHONE_NUMBER.masked_format_for_frodo,
            'useragent': 'curl',
            'v2_accept_language': u'ru',
            'v2_account_country': u'ru',
            'v2_account_karma': u'',
            'v2_account_language': u'ru',
            'v2_account_timezone': u'America/New_York',
            'v2_cookie_l_login': u'test_user',
            'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
            'v2_cookie_l_uid': u'1',
            'v2_cookie_my_block_count': u'1',
            'v2_cookie_my_language': u'tt',
            'v2_has_cookie_l': u'1',
            'v2_has_cookie_my': u'1',
            'v2_has_cookie_yandex_login': u'0',
            'v2_has_cookie_yp': u'0',
            'v2_has_cookie_ys': u'0',
            'v2_ip': TEST_USER_IP,
            'v2_is_ssl': u'1',
            'v2_password_quality': str(TEST_PASSWORD_QUALITY),
            'v2_phonenumber_hash': get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            'v2_track_created': TimeNow(),
            'v2_yandex_gid': u'yandex_gid',
            'valkey': u'0000000000',
            'xcountry': u'ru',
            'yandexuid': u'yandexuid',
        }
        frodo_args.update(**kwargs)

        eq_(len(requests), 1)
        requests[0].assert_query_equals(
            EmptyFrodoParams(**frodo_args),
        )

    @parameterized.expand(['firstname', 'lastname'])
    def test_fraud(self, field):
        resp = self.make_request(data=dict(
            self.form_data,
            **{field: u'Заходи дорогой, гостем будешь диваны.рф'}
        ))
        self.check_error_response(resp, ['{}.invalid'.format(field)])

    def test_error_domain_exists(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, domain=TEST_DOMAIN),
        )
        resp = self.make_request(data=self.form_data)
        self.check_error_response(resp, ['domain.already_exists'])

    def test_error_eula_not_accepted(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )

        form_data = merge_dicts(
            self.form_data,
            dict(eula_accepted='false'),
        )
        resp = self.make_request(data=form_data)
        self.check_error_response(resp, ['eula_accepted.not_accepted'])

    def test_error_already_registered(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_successful_registered = True

        resp = self.make_request(data=self.form_data)
        self.check_error_response(resp, ['account.already_registered'])

    def test_error_similar_upper_domain(self):
        resp = self.make_request(data=merge_dicts(
            self.form_data,
            dict(domain=TEST_UPPER_DOMAIN[:3] + TEST_UPPER_DOMAIN),
        ))
        self.check_error_response(resp, ['domain.invalid_type'])

    def test_error_invalid_domain_without_dot(self):
        resp = self.make_request(data=merge_dicts(
            self.form_data,
            dict(domain=u'okna-bez-tocheck'),
        ))
        self.check_error_response(resp, ['domain.invalid'])

    def test_error_domain_not_served_by_directory(self):
        resp = self.make_request(data=merge_dicts(
            self.form_data,
            dict(domain=u'okna.ru'),
        ))
        self.check_error_response(resp, ['domain.invalid_type'])

    def test_error_subdomain_not_served_by_directory(self):
        resp = self.make_request(data=merge_dicts(
            self.form_data,
            dict(domain='biz.%s' % TEST_UPPER_DOMAIN),
        ))
        self.check_error_response(resp, ['domain.invalid_type'])

    def test_ok_valid_domain_with_differing_register(self):
        resp = self.make_request(data=merge_dicts(
            self.form_data,
            dict(domain=TEST_DOMAIN.upper()),
        ))
        self.check_response_ok(resp)

    def test_error_phone_not_confirmed(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = False

        resp = self.make_request(data=self.form_data)
        self.check_error_response(resp, ['user.not_verified'])

    def test_error_password_like_email(self):
        resp = self.make_request(data=dict(self.form_data, password=TEST_HUMAN_LOGIN))
        self.check_error_response(resp, ['password.likelogin'])

    def test_ok(self):
        resp = self.make_request(data=self.form_data)
        resp_data = self.check_response_ok(resp)

        self.check_db_entries()
        self.check_statbox_entries(organization=TEST_ORGANIZATION)
        self.check_historydb_entries(resp_data['uid'])
        self.check_yasms_not_called()
        self.check_frodo_call()
        self.check_counters()
        self.check_track()

    def test_ok_uppercase_login(self):
        form_data = dict(self.form_data, login=TEST_LOGIN.upper())
        resp = self.make_request(data=form_data)
        resp_data = self.check_response_ok(resp)

        self.check_db_entries(user_defined_login=TEST_LOGIN.upper())
        self.check_statbox_entries(organization=TEST_ORGANIZATION)
        self.check_historydb_entries(resp_data['uid'], user_defined_login=TEST_LOGIN.upper())
        self.check_yasms_not_called()
        self.check_frodo_call()
        self.check_counters()
        self.check_track(user_defined_login=TEST_LOGIN.upper())

    def test_ok_cyrillic_domain_idna(self):
        idna_encoded_domain = TEST_CYRILLIC_DOMAIN.encode('idna')
        form_data = merge_dicts(
            self.form_data,
            dict(domain=idna_encoded_domain),
        )

        resp = self.make_request(data=form_data)

        resp_data = self.check_response_ok(resp)
        self.check_db_entries(domain=TEST_CYRILLIC_DOMAIN.encode('idna'))
        self.check_historydb_entries(
            resp_data['uid'],
            domain=TEST_CYRILLIC_DOMAIN,
        )
        self.check_yasms_not_called()
        self.check_frodo_call(login=TEST_CYRILLIC_HUMAN_LOGIN)
        self.check_counters()
        self.check_track(domain=TEST_CYRILLIC_DOMAIN)

    def test_ok_cyrillic_domain_as_is(self):
        idna_encoded_domain = TEST_CYRILLIC_DOMAIN.encode('idna')
        form_data = merge_dicts(
            self.form_data,
            dict(domain=TEST_CYRILLIC_DOMAIN),
        )

        resp = self.make_request(data=form_data)
        resp_data = self.check_response_ok(resp)
        self.check_db_entries(domain=idna_encoded_domain)

        self.check_historydb_entries(
            resp_data['uid'],
            domain=TEST_CYRILLIC_DOMAIN,
        )
        self.check_yasms_not_called()
        self.check_frodo_call(login=TEST_CYRILLIC_HUMAN_LOGIN)
        self.check_counters()
        self.check_track(domain=TEST_CYRILLIC_DOMAIN)

    def test_ok_without_organization_name(self):
        data = dict(self.form_data)
        data.pop('organization')
        resp = self.make_request(data=data)
        resp_data = self.check_response_ok(resp)

        self.check_db_entries(organization=TEST_DOMAIN.lower())
        self.check_statbox_entries(organization=TEST_DOMAIN.lower())
        self.check_historydb_entries(resp_data['uid'])
        self.check_yasms_not_called()
        self.check_frodo_call()
        self.check_counters()
        self.check_track()


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterDirectoryViewNoBlackboxHash(TestAccountRegisterDirectoryView):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
