# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.api.tests.views.bundle.register.test.base_test_data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
)
from passport.backend.core.builders.federal_configs_api import FederalConfigsApiNotFoundError
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.login.login import normalize_login


TEST_CYRILLIC_DOMAIN = u'окна.рф'
TEST_DOMAIN_ID = 1
TEST_DOMAIN = 'domain.pdd.yandex.ru'
TEST_GENDER = 'm'
TEST_LOGIN = 'login123'
TEST_YAMBOT_LOGIN = u'yambot-test'
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_UPPERCASE_PDD_LOGIN = '%s@%s' % (TEST_LOGIN.upper(), TEST_DOMAIN)
TEST_CYRILLIC_PDD_LOGIN = u'%s@%s' % (TEST_LOGIN, TEST_CYRILLIC_DOMAIN)
TEST_FIRSTNAME = 'first'
TEST_LASTNAME = 'last'
TEST_PASSWORD = 'qaz123wsx456edc789'
TEST_PASSWORD_QUALITY = 100
TEST_WEAK_PASSWORD = 'login123'
TEST_WEAK_PASSWORD_QUALITY = 40
TEST_HINT_QUESTION = 'Question'
TEST_HINT_ANSWER = 'Answer'
TEST_PASSWORD_HASH = '1:$1$bVOObC.i$HCTUFt1a.mrsXH2mZrHj/.'
TEST_PASSWORD_HASH_ARGON = TEST_PASSWORD_HASH.replace('1:', '7:', 1)
TEST_EXTERNAL_HASH_MD5CRYPT = '$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'
TEST_EXTERNAL_HASH_CRYPT_ARGON = '6:{}'.format(TEST_EXTERNAL_HASH_MD5CRYPT)
TEST_EXTERNAL_HASH_RAW_MD5 = 'ab' * 16
TEST_TIMEZONE = 'America/New_York'
TEST_BIRTHDAY = '1971-01-01'

TEST_LANGUAGE = 'ru'
TEST_OTHER_LANGUAGE = 'en'
TEST_COUNTRY = 'ru'
TEST_OTHER_COUNTRY = 'fi'

TEST_USER_IP = '3.3.3.3'
TEST_USER_LOGIN = 'testlogin'
TEST_UID = TEST_SUID = 1130000000000001
TEST_PUNYCODE_DOMAIN = 'xn--80atjc.xn--p1ai'

TEST_IDP_DOMAIN_ID = 2997121  # id домена sso-adfs-test-domain.com в тестинге


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
class TestAccountRegisterPddView(BaseMdapiTestCase,
                                 make_clean_web_test_mixin('test_basic_case_with_person_info', ['firstname', 'lastname'], statbox_action='submitted'),
                                 ):
    url = '/1/bundle/account/register/pdd/?consumer=dev'
    mocked_grants = {
        'account': 'register_pdd',
    }
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        super(TestAccountRegisterPddView, self).setUp()
        self.setup_trackid_generator(track_type='register')
        self.setup_statbox_templates()

        self.generate_yambot_login_patch = mock.patch(
            'passport.backend.core.types.login.login.generate_yambot_login',
            mock.Mock(return_value=TEST_YAMBOT_LOGIN),
        )
        self.generate_yambot_login_patch.start()

        self.form_data = {
            'login': TEST_LOGIN,
            'domain': TEST_DOMAIN,
            'password': TEST_PASSWORD,
        }

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(
                {
                    TEST_PDD_LOGIN: 'free',
                    TEST_UPPERCASE_PDD_LOGIN: 'free',
                    TEST_CYRILLIC_PDD_LOGIN: 'free',
                    TEST_YAMBOT_LOGIN: 'free',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_DOMAIN,
                domid=TEST_DOMAIN_ID,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.federal_configs_api.set_response_side_effect('config_by_domain_id', FederalConfigsApiNotFoundError())

    def tearDown(self):
        self.generate_yambot_login_patch.stop()
        del self.generate_yambot_login_patch
        del self.track_id_generator
        super(TestAccountRegisterPddView, self).tearDown()

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='account_register_pdd',
        )

        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
            consumer='dev',
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
            login=TEST_PDD_LOGIN,
            domain=TEST_DOMAIN,
        )
        self.env.statbox.bind_entry(
            'subscription_created',
            _inherit_from='account_modification',
            _exclude=['old'],
            entity='subscriptions',
            operation='added',
        )
        self.env.statbox.bind_entry(
            'password_validation_error',
            action='password_validation_error',
            track_id=self.track_id,
        )

    def check_statbox_entries(self, login=TEST_PDD_LOGIN, domain=TEST_DOMAIN, with_personal_info=False,
                              password_quality=TEST_PASSWORD_QUALITY, has_hint_question=False,
                              is_enabled=True, no_password=False, is_creating_required=False,
                              external_password_hash=False, is_password_validation_failed=False,
                              language=TEST_LANGUAGE, country=TEST_COUNTRY, with_yambot_alias=False,
                              raw_md5_hash=False):
        expected_entries = [
            self.env.statbox.entry('submitted'),
        ]
        if is_password_validation_failed:
            expected_entries.append(
                self.env.statbox.entry(
                    'password_validation_error',
                    like_login='1',
                    policy='basic',
                ),
            )

        expected_entries += [
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                operation='created',
                old='-',
                new='enabled' if is_enabled else 'disabled',
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                entity='account.mail_status',
                old='-',
                new='active',
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old'],
                type=str(ANT['pdd']),
                entity='aliases',
                operation='added',
                value=normalize_login(login),
            ),
        ]
        if with_yambot_alias:
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['old'],
                    type=str(ANT['yambot']),
                    entity='aliases',
                    operation='added',
                    value=TEST_YAMBOT_LOGIN,
                ),
            )

        modified_entities = []
        if with_personal_info:
            modified_entities.extend([
                ('person.firstname', TEST_FIRSTNAME),
                ('person.lastname', TEST_LASTNAME),
            ])

        modified_entities.extend([
            ('person.language', language),
            ('person.country', country),
        ])

        if with_personal_info:
            modified_entities.extend([
                ('person.gender', TEST_GENDER),
                ('person.birthday', TEST_BIRTHDAY),
                ('person.fullname', u'{} {}'.format(TEST_FIRSTNAME, TEST_LASTNAME)),
            ])

        modified_entities.extend([
            ('domain_name', domain),
            ('domain_id', str(TEST_DOMAIN_ID)),
        ])

        for entity, value in modified_entities:
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=value,
                ),
            )

        if not no_password:
            if not external_password_hash:
                password_hash_version = self.password_hash_version
            elif raw_md5_hash:
                password_hash_version = PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON
            else:
                password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

            expected_entries.extend(
                [
                    self.env.statbox.entry(
                        'account_modification',
                        _exclude=['old', 'new'],
                        entity='password.encrypted',
                    ),
                    self.env.statbox.entry(
                        'account_modification',
                        entity='password.encoding_version',
                        new=str(password_hash_version),
                    ),
                ],
            )

        if password_quality is not None:
            expected_entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.quality',
                    new=str(password_quality),
                ),
            )

        if has_hint_question:
            expected_entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['old'],
                    entity='hint.question',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    _exclude=['old'],
                    entity='hint.answer',
                ),
            ])

        expected_entries.extend([
            self.env.statbox.entry(
                'account_modification',
                _exclude=['operation'],
                action='account_create_mdapi',
                entity='karma',
                destination='frodo',
                registration_datetime=DatetimeNow(convert_to_datetime=True),
                login=normalize_login(login),
                suid=str(TEST_SUID),
                new='0',
            ),
            self.env.statbox.entry(
                'subscription_created',
                sid='2',
                suid=str(TEST_SUID),
            ),
            self.env.statbox.entry(
                'account_created',
                login=login,
                domain=domain,
                is_enabled='1' if is_enabled else '0',
                password_hash='1' if external_password_hash else '0',
                no_password='1' if no_password else '0',
            ),
        ])

        if is_creating_required:
            expected_entries.insert(
                len(expected_entries) - 1,
                self.env.statbox.entry(
                    'subscription_created',
                    sid='100',
                ),
            )

        self.env.statbox.assert_has_written(expected_entries)

    def check_historydb_entries(self, uid=TEST_UID, login=TEST_LOGIN,
                                domain=TEST_DOMAIN, password_quality=TEST_PASSWORD_QUALITY,
                                with_personal_info=False, has_hint_question=False,
                                is_enabled=True, is_creating_required=False, is_maillist=False,
                                language=TEST_LANGUAGE, country=TEST_COUNTRY, user_defined_login=None,
                                with_yambot_alias=False):
        # Проверим, что пароль пользователю был установлен корректно.
        eav_pass_hash = self.env.db.get(
            'attributes',
            'password.encrypted',
            uid=uid,
            db='passportdbshard2',
        )

        firstname, lastname, gender, birthday = (None,) * 4
        if with_personal_info:
            firstname, lastname, gender, birthday = TEST_FIRSTNAME, TEST_LASTNAME, '1', TEST_BIRTHDAY

        encoded_domain = domain.encode('utf-8')
        historydb_record = [
            ('info.login', '%s@%s' % (login, encoded_domain)),
        ]
        if user_defined_login is not None:
            historydb_record.append(
                ('info.login_wanted', user_defined_login),
            )
        historydb_record += [
            ('info.ena', '1' if is_enabled else '0'),
            ('info.disabled_status', '0' if is_enabled else '1'),
            ('info.reg_date', DatetimeNow(convert_to_datetime=True)),
            ('info.is_maillist', '1' if is_maillist else '0'),
            ('info.mail_status', '1'),
            ('info.firstname', firstname),
            ('info.lastname', lastname),
            ('info.sex', gender),
            ('info.birthday', birthday),
            ('info.country', country),
            ('info.tz', TEST_TIMEZONE),
            ('info.lang', language),
            ('info.domain_name', domain.encode('idna')),
            ('info.domain_id', '1'),
            ('info.password', eav_pass_hash if eav_pass_hash else None),
            ('info.password_quality', str(password_quality) if password_quality is not None else None),
            ('info.password_update_time', TimeNow() if eav_pass_hash else None),
            ('info.hintq', ('99:%s' % TEST_HINT_QUESTION if has_hint_question else None)),
            ('info.hinta', TEST_HINT_ANSWER if has_hint_question else None),
            ('info.karma_prefix', '0'),
            ('info.karma_full', '0'),
            ('info.karma', '0'),
            ('alias.pdd.add', '1/login123'),
        ]
        if with_yambot_alias:
            historydb_record += [
                ('alias.yambot.add', TEST_YAMBOT_LOGIN),
            ]
        historydb_record += [
            ('mail.add', '%d' % uid),
            ('sid.add', '2,100' if is_creating_required else '2'),
            ('action', 'account_create_mdapi'),
            ('consumer', 'dev'),
            ('user_agent', 'curl'),
        ]
        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record if v is not None
        ]

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            historydb_entries,
        )

    def check_db_entries(self, uid=TEST_UID, domain_id=TEST_DOMAIN_ID,
                         login=TEST_LOGIN, with_personal_info=False,
                         is_creating_required=False, password_quality=100,
                         is_enabled=True, no_password=False, has_hint_question=False,
                         is_maillist=False, language=None, country=None, user_defined_login=None,
                         with_yambot_alias=False):
        present_attributes = [
            ('account.registration_datetime', TimeNow()),
            ('person.timezone', TEST_TIMEZONE),
        ]

        missing_attributes = [
            'karma.value',
            'subscription.mail.login_rule',
        ]

        if user_defined_login is not None:
            present_attributes.append(
                ('account.user_defined_login', user_defined_login),
            )
        else:
            missing_attributes.append('account.user_defined_login')

        if has_hint_question:
            present_attributes.extend([
                ('hint.question.serialized', '99:%s' % TEST_HINT_QUESTION),
                ('hint.answer.encrypted', TEST_HINT_ANSWER),
            ])

        if language:
            present_attributes.append(('person.language', language))
        else:
            missing_attributes.append('person.language')

        if country:
            present_attributes.append(('person.country', country))
        else:
            missing_attributes.append('person.country')

        if not no_password:
            present_attributes.append(('password.update_datetime', TimeNow()))
        else:
            missing_attributes.append('password.encrypted')

        if is_enabled:
            missing_attributes.append('account.is_disabled')
        else:
            present_attributes.append(('account.is_disabled', '1'))

        if password_quality is not None:
            present_attributes.append(('password.quality', '3:%d' % password_quality))
        else:
            missing_attributes.append('password.quality')

        if is_creating_required:
            present_attributes.append(('password.is_creating_required', '1'))
        else:
            missing_attributes.append('password.is_creating_required')

        if is_maillist:
            present_attributes.append(('account.is_maillist', '1'))
        else:
            missing_attributes.append('account.is_maillist')

        if with_personal_info:
            present_attributes.extend([
                ('person.firstname', TEST_FIRSTNAME),
                ('person.lastname', TEST_LASTNAME),
                ('person.gender', 'm'),
                ('person.birthday', TEST_BIRTHDAY),
            ])
        else:
            missing_attributes.extend([
                'person.firstname',
                'person.lastname',
                'person.gender',
                'person.birthday',
            ])

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

        # Проверяем, что алиас создался
        self.env.db.check(
            'aliases',
            'value',
            '%i/%s' % (domain_id, login),
            uid=uid,
            type=str(ANT['pdd']),
            db='passportdbcentral',
        )
        # Проверяем, что портальный алиас _не_ создался
        self.env.db.check_missing(
            'aliases',
            'value',
            uid=uid,
            type=str(ANT['portal']),
            db='passportdbcentral',
        )
        if with_yambot_alias:
            self.env.db.check(
                'aliases',
                'value',
                TEST_YAMBOT_LOGIN,
                uid=uid,
                type=str(ANT['yambot']),
                db='passportdbcentral',
            )
        else:
            self.env.db.check_missing(
                'aliases',
                'value',
                uid=uid,
                type=str(ANT['yambot']),
                db='passportdbcentral',
            )

        # Информация о доменах хранится на центральном узле БД
        eq_(self.env.db.query_count('passportdbcentral'), 4)
        # Информация о подписках ПДД-пользователя хранится на ином шарде.
        eq_(self.env.db.query_count('passportdbshard2'), 1)
        eq_(self.env.db.query_count('passportdbshard2'), 1)

    def check_error_response(self, response, errors):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'error')
        eq_(
            response_data['errors'],
            errors,
        )
        return response_data

    def check_password_hash(self, hash, uid=TEST_UID):
        saved_pass_hash = self.env.db.get(
            'attributes',
            'password.encrypted',
            uid=uid,
            db='passportdbshard2',
        )
        eq_(
            saved_pass_hash,
            hash,
            'User password hash is "%s", but should be "%s"' % (
                saved_pass_hash,
                hash,
            ),
        )

    def test_basic_case(self):
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries()
        self.check_statbox_entries()
        self.check_historydb_entries()

    def test_uppercase_login(self):
        self.form_data.update(login=TEST_LOGIN.upper())
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(user_defined_login=TEST_LOGIN.upper())
        self.check_statbox_entries(login='%s@%s' % (TEST_LOGIN.upper(), TEST_DOMAIN))
        self.check_historydb_entries(user_defined_login=TEST_LOGIN.upper())

    def test_basic_case_with_person_info(self):
        self.form_data.update({
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'gender': TEST_GENDER,
            'birthday': TEST_BIRTHDAY,
        })
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(with_personal_info=True)
        self.check_statbox_entries(with_personal_info=True)
        self.check_historydb_entries(with_personal_info=True)

    def test_basic_case_with_explicit_country_and_language(self):
        self.form_data.update({
            'language': TEST_OTHER_LANGUAGE,
            'country': TEST_OTHER_COUNTRY,
        })
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(
            language=TEST_OTHER_LANGUAGE,
            country=TEST_OTHER_COUNTRY,
        )
        self.check_statbox_entries(
            language=TEST_OTHER_LANGUAGE,
            country=TEST_OTHER_COUNTRY,
        )
        self.check_historydb_entries(
            language=TEST_OTHER_LANGUAGE,
            country=TEST_OTHER_COUNTRY,
        )

    def test_basic_case_hint_question(self):
        self.form_data.update({
            'hint_question': TEST_HINT_QUESTION,
            'hint_answer': TEST_HINT_ANSWER,
        })
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(has_hint_question=True)
        self.check_statbox_entries(has_hint_question=True)
        self.check_historydb_entries(has_hint_question=True)

    def test_is_creating_required(self):
        self.form_data['is_creating_required'] = 'true'

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(is_creating_required=True)
        self.check_statbox_entries(is_creating_required=True)
        self.check_historydb_entries(is_creating_required=True)

    def test_is_maillist(self):
        self.form_data['is_maillist'] = 'true'

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(is_maillist=True)
        self.check_statbox_entries()
        self.check_historydb_entries(is_maillist=True)

    def test_is_enabled(self):
        self.form_data['is_enabled'] = 'false'

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(is_enabled=False)
        self.check_statbox_entries(is_enabled=False)
        self.check_historydb_entries(is_enabled=False)

    def test_weak_password_is_ok(self):
        self.form_data.update({
            'weak_password': 'true',
            'password': TEST_WEAK_PASSWORD,
        })
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(
            is_creating_required=True,
            password_quality=TEST_WEAK_PASSWORD_QUALITY,
        )
        self.check_statbox_entries(
            password_quality=TEST_WEAK_PASSWORD_QUALITY,
            is_creating_required=True,
            is_password_validation_failed=True,
        )
        self.check_historydb_entries(
            password_quality=TEST_WEAK_PASSWORD_QUALITY,
            is_creating_required=True,
        )

    def test_external_password_hash_md5crypt(self):
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_EXTERNAL_HASH_CRYPT_ARGON),
        )
        self.form_data['password_hash'] = TEST_EXTERNAL_HASH_MD5CRYPT
        self.form_data.pop('password')

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(password_quality=None)
        self.check_statbox_entries(
            password_quality=None,
            external_password_hash=True,
        )
        self.check_historydb_entries(password_quality=None)
        self.check_password_hash(TEST_EXTERNAL_HASH_CRYPT_ARGON)

    def test_external_password_hash_raw_md5(self):
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_PASSWORD_HASH_ARGON),
        )

        self.form_data['password_hash'] = TEST_EXTERNAL_HASH_RAW_MD5
        self.form_data.pop('password')

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(password_quality=None)
        self.check_statbox_entries(
            password_quality=None,
            external_password_hash=True,
            raw_md5_hash=True,
        )
        self.check_historydb_entries(password_quality=None)
        self.check_password_hash(TEST_PASSWORD_HASH_ARGON)

    def test_no_password(self):
        self.form_data['no_password'] = 'true'
        self.form_data.pop('password')

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(password_quality=None, no_password=True)
        self.check_statbox_entries(password_quality=None, no_password=True)
        self.check_historydb_entries(password_quality=None)
        self.check_password_hash(None)

    def test_error_domain_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )

        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['domain.not_found'],
        )

    def test_error_domain_is_an_alias(self):
        alias_domain = blackbox_hosted_domains_response(
            count=1,
            master_domain=TEST_DOMAIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            alias_domain,
        )

        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['domain.invalid_type'],
        )

    def test_error_domain_is_saml_sso(self):
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())
        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['domain.invalid_type'],
        )

    def test_ok_register_maillist_on_saml_sso_domain(self):
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())
        self.form_data['is_maillist'] = 'true'
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(is_maillist=True)
        self.check_statbox_entries()
        self.check_historydb_entries(is_maillist=True)

    def test_error_login_is_occupied(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PDD_LOGIN: 'occupied'}),
        )

        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['login.notavailable'],
        )

    def test_error_weak_password(self):
        self.form_data['password'] = TEST_WEAK_PASSWORD

        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['password.likelogin'],
        )

    def test_error_no_password_false_no_hash_or_text_also(self):
        invalid_data = {
            'login': TEST_LOGIN,
            'domain': TEST_DOMAIN,
            'no_password': 'false',
        }

        resp = self.make_request(data=invalid_data)
        self.check_error_response(
            resp,
            [
                'password.empty',
                'password_hash.empty',
            ],
        )

    def test_with_punycode_domain(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_PUNYCODE_DOMAIN,
                domid=TEST_DOMAIN_ID,
            ),
        )

        self.form_data['domain'] = TEST_PUNYCODE_DOMAIN

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries()
        self.check_statbox_entries(login=TEST_CYRILLIC_PDD_LOGIN, domain=TEST_PUNYCODE_DOMAIN)
        self.check_historydb_entries(domain=TEST_CYRILLIC_DOMAIN)

    def test_with_yambot_alias(self):
        self.form_data['with_yambot_alias'] = 'yes'
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_db_entries(with_yambot_alias=True)
        self.check_statbox_entries(with_yambot_alias=True)
        self.check_historydb_entries(with_yambot_alias=True)


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterPddViewNoBlackboxHash(TestAccountRegisterPddView):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
