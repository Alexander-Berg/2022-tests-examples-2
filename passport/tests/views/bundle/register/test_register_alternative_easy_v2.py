# -*- coding: utf-8 -*-

from functools import partial
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.forms.register import (
    CAPTCHA_VALIDATION_METHOD,
    PHONE_VALIDATION_METHOD,
)
from passport.backend.api.templatetags import span
from passport.backend.api.test.emails import assert_user_notified_about_alias_as_login_and_email_owner_changed
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    make_clean_web_test_mixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.register.test import StatboxTestMixin
from passport.backend.api.tests.views.bundle.register.test.base_test_data import (
    build_headers,
    TEST_DEFAULT_TIMEZONE,
    TEST_HINT_ANSWER,
    TEST_HINT_CUSTOM_QUESTION_ID,
    TEST_HINT_PREDEFINED_QUESTION,
    TEST_HINT_PREDEFINED_QUESTION_ID,
    TEST_HINT_QUESTION,
    TEST_INVALID_PHONE,
    TEST_KARMA,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_HASH,
    TEST_PHONE_NUMBER_MASKED,
    TEST_SERIALIZED_PASSWORD,
    TEST_SUID,
    TEST_UID,
    TEST_UID_2,
    TEST_USER_AGENT,
    TEST_USER_COUNTRY,
    TEST_USER_FIRSTNAME,
    TEST_USER_IP,
    TEST_USER_LASTNAME,
    TEST_USER_LOGIN,
    TEST_USER_LOGIN_NORMALIZED,
    TEST_USER_PASSWORD_QUALITY,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_loginoccupation_response,
    blackbox_phone_bindings_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ANT
from passport.backend.core.frodo.exceptions import FrodoError
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_no_secure_phone,
    assert_secure_phone_bound,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts


eq_ = iterdiff(eq_)


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_URL='http://localhost',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
    **mock_counters()
)
class TestAccountRegisterAlternativeEasyV2(BaseBundleTestViews,
                                           StatboxTestMixin,
                                           make_clean_web_test_mixin('test_with_captcha__ok', ['firstname', 'lastname'], has_force_parameter=False),
                                           EmailTestMixin):

    url = '/2/bundle/account/register/alternative/easy/?consumer=dev'

    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'account': ['register_alternative_easy']}),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.setup_statbox_templates()
        self.patches = []

    def tearDown(self):
        self.env.stop()
        for p in self.patches:
            p.stop()
        del self.env
        del self.track_manager
        del self.patches

    def make_request(self, data, headers):
        return self.env.client.post(
            self.url,
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'login': TEST_USER_LOGIN,
            'password': 'aaa1bbbccc',
            'country': 'ru',
            'language': 'ru',
            'eula_accepted': 'True',
        }
        return merge_dicts(base_params, kwargs)

    def captcha_query_params(self):
        return self.query_params(
            validation_method=CAPTCHA_VALIDATION_METHOD,
            firstname=TEST_USER_FIRSTNAME,
            lastname=TEST_USER_LASTNAME,
            hint_question=TEST_HINT_QUESTION,
            hint_answer=TEST_HINT_ANSWER,
        )

    def phone_query_params(self, phone_number=TEST_PHONE_NUMBER.e164, create_phone_alias=None, **kwargs):
        return self.query_params(
            validation_method=PHONE_VALIDATION_METHOD,
            phone_number=phone_number,
            create_phone_alias=create_phone_alias,
            **kwargs
        )

    def get_registration_sms_counter(self):
        return sms_per_ip.get_registration_completed_with_phone_counter(TEST_USER_IP)

    def get_registration_bad_karma_counter(self):
        return registration_karma.get_bad_buckets()

    def setup_blackbox_free_login(self, login=TEST_USER_LOGIN):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({login: 'free'}),
        )

    def setup_captcha_passed_successfully(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

    def setup_blackbox_phone_bindings(self):
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

    def setup_frodo_spammer_response(self, karma=TEST_KARMA):
        self.env.frodo.set_response_value(
            u'check',
            '<spamlist><spam_user login="%s" weight="%s" /></spamlist>' % (
                TEST_USER_LOGIN_NORMALIZED,
                karma,
            ),
        )

    def assert_db__ok(self, karma=0, centraldb_queries=4, sharddb_queries=1, language=None, tz=None, from_ip=TEST_USER_IP,
                      firstname=TEST_USER_FIRSTNAME, lastname=TEST_USER_LASTNAME,
                      hint_question_id=TEST_HINT_CUSTOM_QUESTION_ID, hint_question=TEST_HINT_QUESTION,
                      hint_answer=TEST_HINT_ANSWER, phone_number=False, phonenumber_alias=None, dealiasify=False):
        timenow = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_queries)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_queries)

        self.env.db.check('aliases', 'portal', TEST_USER_LOGIN_NORMALIZED, uid=TEST_UID, db='passportdbcentral')
        self.env.db.check('attributes', 'account.registration_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'account.user_defined_login', TEST_USER_LOGIN, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.gender', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.city', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.birthday', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'person.country', uid=TEST_UID, db='passportdbshard1')
        if language is None:
            self.env.db.check_missing('attributes', 'person.language', uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check('attributes', 'person.language', language, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'account.is_disabled', uid=TEST_UID, db='passportdbshard1')
        if hint_answer is None:
            self.env.db.check_missing('attributes', 'hint.question.serialized', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'hint.answer.encrypted', uid=TEST_UID, db='passportdbshard1')

        else:
            expected_question = ('%s:%s' % (hint_question_id, hint_question)).encode('utf-8')
            self.env.db.check('attributes', 'hint.question.serialized', expected_question, uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'hint.answer.encrypted', hint_answer, uid=TEST_UID, db='passportdbshard1')

        if firstname is None and lastname is None:
            self.env.db.check_missing('attributes', 'person.firstname', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'person.lastname', uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check('attributes', 'person.firstname', firstname, uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'person.lastname', lastname, uid=TEST_UID, db='passportdbshard1')
        if tz is not None:
            self.env.db.check('attributes', 'person.timezone', tz, uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'person.timezone', uid=TEST_UID, db='passportdbshard1')
        if karma == 0:
            self.env.db.check_missing('attributes', 'karma.value', uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check('attributes', 'karma.value', str(karma), uid=TEST_UID, db='passportdbshard1')

        if phone_number:
            assert_secure_phone_bound.check_db(
                self.env.db,
                uid=TEST_UID,
                phone_attributes={
                    'id': 1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': DatetimeNow(),
                    'bound': DatetimeNow(),
                    'confirmed': DatetimeNow(),
                    'secured': DatetimeNow(),
                },
            )
        else:
            assert_no_secure_phone(self.env.db, TEST_UID)

        if phonenumber_alias:
            self.env.db.check('aliases', 'phonenumber', phonenumber_alias.digital, uid=TEST_UID, db='passportdbcentral')
            if dealiasify:
                self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID_2, db='passportdbcentral')
        else:
            self.env.db.check_missing('aliases', 'phonenumber', uid=TEST_UID, db='passportdbcentral')

        pass_hash_eav = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(pass_hash_eav, TEST_SERIALIZED_PASSWORD)
        else:
            ok_(pass_hash_eav.startswith('1:'))

    def get_expected_frodo_params(self, personal=None, phone=None, language='ru', **kwargs):
        params = EmptyFrodoParams(**{
            'uid': str(TEST_UID),
            'login': TEST_USER_LOGIN_NORMALIZED,
            'iname': '',
            'fname': '',
            'from': '',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': str(TEST_USER_PASSWORD_QUALITY),
            'hintq': '0.0.0.0.0.0',
            'hintqid': '',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': '',
            'v2_yandex_gid': '',
            'fuid': '',
            'useragent': 'curl',
            'host': 'yandex.ru',
            'ip_from': TEST_USER_IP,
            'v2_ip': TEST_USER_IP,
            'valkey': '0000000000',
            'action': 'alternative_phone' if phone else 'alternative_hint',
            'lang': language,
            'xcountry': TEST_USER_COUNTRY,
            'v2_phone_validation_changes': '',
            'v2_phone_validation_error': '',
            'v2_phone_confirmation_sms_count': '',
            'v2_phone_confirmation_confirms_count': '',
            'v2_track_created': TimeNow(),
            'v2_old_password_quality': '',
            'v2_account_country': 'ru',
            'v2_account_language': language,
            'v2_account_timezone': TEST_DEFAULT_TIMEZONE,
            'v2_accept_language': 'ru',
            'v2_account_karma': '',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '0',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '0',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
        })
        if personal:
            params.update({
                'iname': TEST_USER_FIRSTNAME,
                'fname': TEST_USER_LASTNAME,
                'hinta': '16.0.14.0.0.0',
                'hintaex': '4.10.2.0.0',
            })
        if phone:
            params.update({
                'phonenumber': TEST_PHONE_NUMBER_MASKED,
                'v2_phonenumber_hash': TEST_PHONE_NUMBER_HASH,
            })
        params.update(**kwargs)
        return params

    def assert_frodo__ok(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_query_equals(self.get_expected_frodo_params(**kwargs))

    def assert_yasms_not_called(self):
        eq_(len(self.env.yasms.requests), 0)

    def get_expected_historydb_params(self, pass_hash, tz=None, personal=None, hint_question=TEST_HINT_QUESTION,
                                      hint_question_id=99, phone_number=None, aliasify=False, dealiasify=False,
                                      language='ru'):
        events = []
        if dealiasify:
            events.extend([
                {'name': 'alias.phonenumber.rm', 'value': phone_number.international},
                {'name': 'action', 'value': 'phone_alias_delete'},
                {'name': 'consumer', 'value': 'dev'},
            ])
        events.extend([
            {'name': 'info.login', 'value': TEST_USER_LOGIN_NORMALIZED},
            {'name': 'info.login_wanted', 'value': TEST_USER_LOGIN},
            {'name': 'info.ena', 'value': '1'},
            {'name': 'info.disabled_status', 'value': '0'},
            {'name': 'info.reg_date', 'value': DatetimeNow(convert_to_datetime=True)},
            {'name': 'info.mail_status', 'value': '1'},
        ])
        if personal:
            events.extend([
                {'name': 'info.firstname', 'value': 'firstname'},
                {'name': 'info.lastname', 'value': 'lastname'},
            ])
        events.extend([
            {'name': 'info.country', 'value': 'ru'},
            {'name': 'info.tz', 'value': tz},
            {'name': 'info.lang', 'value': language},
            {'name': 'info.password', 'value': pass_hash},
            {'name': 'info.password_quality', 'value': '80'},
            {'name': 'info.password_update_time', 'value': TimeNow()},
        ])
        if personal:
            events.extend([
                {'name': 'info.hintq', 'value': ('%d:%s' % (hint_question_id, hint_question)).encode('utf-8')},
                {'name': 'info.hinta', 'value': TEST_HINT_ANSWER},
            ])
        events.extend([
            {'name': 'info.karma_prefix', 'value': '0'},
            {'name': 'info.karma_full', 'value': '0'},
            {'name': 'info.karma', 'value': '0'},
            {'name': 'alias.portal.add', 'value': TEST_USER_LOGIN_NORMALIZED},
        ])
        if aliasify:
            events.extend([
                {'name': 'alias.phonenumber.add', 'value': phone_number.international},
                {'name': 'info.phonenumber_alias_search_enabled', 'value': '1'},
            ])

        events.extend([
            {'name': 'mail.add', 'value': '1'},
            {'name': 'sid.add', 'value': '8|%s,2' % TEST_USER_LOGIN},
        ])

        if phone_number:
            events.extend([
                {'name': 'phone.1.action', 'value': 'created'},
                {'name': 'phone.1.bound', 'value': TimeNow()},
                {'name': 'phone.1.confirmed', 'value': TimeNow()},
                {'name': 'phone.1.created', 'value': TimeNow()},
                {'name': 'phone.1.number', 'value': phone_number.e164},
                {'name': 'phone.1.secured', 'value': TimeNow()},
                {'name': 'phones.secure', 'value': '1'},
            ])

        events.extend([
            {'name': 'action', 'value': 'account_register'},
            {'name': 'consumer', 'value': 'dev'},
            {'name': 'user_agent', 'value': 'curl'},
        ])

        return events

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='register',
            user_agent=TEST_USER_AGENT,
        )
        super(TestAccountRegisterAlternativeEasyV2, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'aliasify',
            login=TEST_USER_LOGIN,
            uid='-',
        )
        self.env.statbox.bind_entry(
            'account_created',
            _exclude=['language'],
        )

    def assert_statbox_ok(self, suid=str(TEST_SUID), user_ip=TEST_USER_IP, personal=None,
                          phone_number=None, aliasify=None, dealiasify=False,
                          language='ru'):
        entries = [
            self.env.statbox.entry(
                'submitted',
                ip=user_ip,
            ),
        ]

        if aliasify and dealiasify:
            entries.extend([
                self.env.statbox.entry(
                    'phonenumber_alias_taken_away',
                    ip=user_ip,
                    number=phone_number.masked_format_for_statbox,
                ),
                self.env.statbox.entry('phonenumber_alias_removed'),
                self.env.statbox.entry(
                    'phonenumber_alias_subscription_removed',
                    ip=user_ip,
                ),
            ])

        if aliasify:
            entries.append(
                self.env.statbox.entry(
                    'aliasify',
                    is_owner_changed=tskv_bool(dealiasify),
                ),
            )

        entries += [
            self.env.statbox.entry(
                'account_modification',
                entity='account.disabled_status',
                old='-',
                new='enabled',
                ip=user_ip,
            ),
            self.env.statbox.entry(
                'account_modification',
                operation='created',
                entity='account.mail_status',
                old='-',
                new='active',
                ip=user_ip,
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='user_defined_login',
                old='-',
                new=TEST_USER_LOGIN,
                ip=user_ip,
            ),
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='aliases',
                operation='added',
                type=str(ANT['portal']),
                value=TEST_USER_LOGIN_NORMALIZED,
                ip=user_ip,
            ),
        ]

        if aliasify:
            entries += [
                self.env.statbox.entry('phonenumber_alias_added'),
            ]

        if phone_number:
            entries += [
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    new=phone_number.masked_format_for_statbox,
                    new_entity_id='1',
                    old_entity_id='-',
                    ip=user_ip,
                ),
            ]

        if personal:
            for entity, new in [
                ('person.firstname', 'firstname'),
                ('person.lastname', 'lastname'),
            ]:
                entries.append(
                    self.env.statbox.entry(
                        'account_modification',
                        entity=entity,
                        new=new,
                        ip=user_ip,
                    ),
                )
        for entity, new in [
            ('person.language', language),
            ('person.country', 'ru'),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=new,
                    ip=user_ip,
                ),
            )
        if personal:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='person.fullname',
                    new='firstname lastname',
                    ip=user_ip,
                ),
            )
        entries.append(
            self.env.statbox.entry(
                'account_modification',
                _exclude=['old', 'new'],
                entity='password.encrypted',
                ip=user_ip,
            ),
        )
        for entity, new in [
            ('password.encoding_version', str(self.password_hash_version)),
            ('password.quality', str(TEST_USER_PASSWORD_QUALITY)),
        ]:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity=entity,
                    new=new,
                    ip=user_ip,
                ),
            )
        if personal:
            for entity in ['hint.question', 'hint.answer']:
                entries.append(
                    self.env.statbox.entry(
                        'account_modification',
                        _exclude=['old', 'new'],
                        entity=entity,
                        ip=user_ip,
                    ),
                )

        entries.append(
            self.env.statbox.entry(
                'account_register',
                suid=suid,
                ip=user_ip,
            ),
        )
        entries.extend([
            self.env.statbox.entry(
                'subscriptions',
                sid='8',
                ip=user_ip,
            ),
            self.env.statbox.entry(
                'subscriptions',
                sid='2',
                suid=suid,
                ip=user_ip,
            ),

        ])
        if aliasify:
            entries.extend([
                self.env.statbox.entry(
                    'subscriptions',
                    sid='65',
                    ip=user_ip,
                ),
                self.env.statbox.entry(
                    'phonenumber_alias_search_enabled',
                    ip=user_ip,
                ),
            ])
        if phone_number:
            entries.extend([
                self.env.statbox.entry(
                    'phone_confirmed',
                    number=phone_number.masked_format_for_statbox,
                    code_checks_count='0',
                    ip=user_ip,
                ),
                self.env.statbox.entry(
                    'secure_phone_bound',
                    number=phone_number.masked_format_for_statbox,
                    ip=user_ip,
                ),
            ])

        if phone_number:
            entries.append(
                self.env.statbox.entry(
                    'account_created',
                    aliasify=tskv_bool(aliasify),
                    ip=user_ip,
                ),
            )
        else:
            entries.append(
                self.env.statbox.entry(
                    'account_created',
                    ip=user_ip,
                ),
            )

        self.env.statbox.assert_has_written(entries)

    def assert_historydb_and_statbox_records__ok(self, user_ip=TEST_USER_IP, tz=TEST_DEFAULT_TIMEZONE,
                                                 personal=None, phone_number=None,
                                                 aliasify=False, dealiasify=False, language='ru', **kwargs):
        pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            self.get_expected_historydb_params(
                pass_hash,
                tz=tz,
                personal=personal,
                phone_number=phone_number,
                aliasify=aliasify,
                dealiasify=dealiasify,
                language=language,
                **kwargs
            ),
        )
        self.assert_statbox_ok(
            user_ip=user_ip,
            personal=personal,
            phone_number=phone_number,
            aliasify=aliasify,
            dealiasify=dealiasify,
            language=language,
        )

    def assert_registrations_with_bad_karma_counter_incr__ok(self):
        value = self.get_registration_bad_karma_counter().get(TEST_USER_IP)
        eq_(value, 1)

    def assert_track__ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.allow_authorization, True)
        eq_(track.allow_oauth_authorization, True)
        eq_(track.uid, str(TEST_UID))
        eq_(track.login, TEST_USER_LOGIN)
        eq_(track.user_entered_login, TEST_USER_LOGIN)
        eq_(track.human_readable_login, TEST_USER_LOGIN)
        eq_(track.machine_readable_login, TEST_USER_LOGIN_NORMALIZED)
        eq_(track.is_password_passed, True)
        eq_(track.have_password, True)

    def assert_track__empty(self):
        track = self.track_manager.read(self.track_id)
        eq_(
            track._data,
            {
                'track_type': 'register',
                'consumer': 'dev',
                'created': TimeNow(),
            },
        )

    def test_without_required_headers__error(self):
        rv = self.make_request(
            self.captcha_query_params(),
            {},
        )

        self.assert_error_response(rv, ['useragent.empty', 'ip.empty'])

    def test_already_registered__error(self):
        self.setup_blackbox_free_login()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_successful_registered = True

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.already_registered'])

    def test_captcha_not_passed__not_verified_error(self):
        self.setup_blackbox_free_login()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['user.not_verified'])

    def test_eula_not_accepted__error(self):
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()

        rv = self.make_request(
            self.query_params(
                validation_method=CAPTCHA_VALIDATION_METHOD,
                firstname=TEST_USER_FIRSTNAME,
                lastname=TEST_USER_LASTNAME,
                hint_question=TEST_HINT_QUESTION,
                hint_answer=TEST_HINT_ANSWER,
                eula_accepted='False',
            ),
            build_headers(),
        )

        self.assert_error_response(rv, ['eula_accepted.not_accepted'])

    def test_login_not_available__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_USER_LOGIN: 'occupied'}),
        )

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['login.notavailable'])

    def test_invalid_password__error(self):
        self.setup_blackbox_free_login()

        invalid_password_args = [
            (
                '.',
                ['password.short'],
            ),
            (
                TEST_USER_LOGIN,
                ['password.likelogin'],
            ),
            (
                'aaabbb',
                ['password.weak'],
            ),
            (
                TEST_PHONE_NUMBER.e164,
                ['password.likephonenumber'],
            ),
        ]

        for password, expected_errors in invalid_password_args:
            rv = self.make_request(
                self.query_params(
                    password=password,
                    phone_number=TEST_PHONE_NUMBER.e164,
                    validation_method=PHONE_VALIDATION_METHOD,
                ),
                build_headers(),
            )

            self.assert_error_response(rv, expected_errors)

    def test_invalid_phone__error(self):
        self.setup_blackbox_free_login()

        rv = self.make_request(
            self.phone_query_params(phone_number=TEST_INVALID_PHONE),
            build_headers(),
        )

        self.assert_error_response(rv, ['phone_number.invalid'])

    def test_with_captcha__ok(self):
        """При регистрации с капчей, не увеличивается счетчик регистраций через sms"""
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok()
        self.assert_historydb_and_statbox_records__ok(personal=True)
        self.assert_frodo__ok(personal=True)
        # Счетчик "регистраций с помощью sms" не увеличивается
        value = self.get_registration_sms_counter().get(TEST_USER_IP)
        eq_(value, 0)
        self.assert_yasms_not_called()

    def test_captcha_and_hint__ok(self):
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()

        rv = self.make_request(
            self.query_params(
                validation_method=CAPTCHA_VALIDATION_METHOD,
                firstname=TEST_USER_FIRSTNAME,
                lastname=TEST_USER_LASTNAME,
                hint_question_id=1,
                hint_answer=TEST_HINT_ANSWER,
            ),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok(
            hint_question_id=TEST_HINT_PREDEFINED_QUESTION_ID,
            hint_question=TEST_HINT_PREDEFINED_QUESTION,
        )
        self.assert_historydb_and_statbox_records__ok(
            personal=True,
            hint_question_id=TEST_HINT_PREDEFINED_QUESTION_ID,
            hint_question=TEST_HINT_PREDEFINED_QUESTION,
        )
        self.assert_frodo__ok(personal=True, hintqid='1')
        self.assert_yasms_not_called()

    def test_frodo_spammer__ok_with_bad_karma(self):
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()
        self.setup_frodo_spammer_response()

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok(sharddb_queries=2, karma=TEST_KARMA)
        # Записали в логи
        self.assert_event_is_logged(self.env.handle_mock, 'info.karma', str(TEST_KARMA))
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'account_created',
                    karma=str(TEST_KARMA),
                ),
            ],
            offset=-1,
        )
        # Увеличили счетчик "регистраций с плохой кармой"
        self.assert_registrations_with_bad_karma_counter_incr__ok()

        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        # Приняли инфо от ФО
        requests[0].assert_query_equals(
            self.get_expected_frodo_params(personal=True),
        )
        # Ответили в ФО "вас понял"
        requests[1].assert_query_equals({TEST_USER_LOGIN_NORMALIZED: str(TEST_KARMA)})

    def test_frodo_error__ok_with_empty_karma(self):
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()
        self.env.frodo.set_response_side_effect(u'check', FrodoError('Failed'))

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)

        self.assert_db__ok()
        self.assert_historydb_and_statbox_records__ok(personal=True)

    def test_timezone_detected__ok(self):
        self.setup_blackbox_free_login()
        self.setup_captcha_passed_successfully()
        user_ip, user_tz = '8.8.8.8', 'America/New_York'

        rv = self.make_request(
            self.captcha_query_params(),
            build_headers(user_ip=user_ip),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok(tz=user_tz, from_ip=user_ip)
        self.assert_historydb_and_statbox_records__ok(
            tz=user_tz,
            user_ip=user_ip,
            personal=True,
        )
        self.assert_frodo__ok(v2_ip=user_ip, v2_account_timezone=user_tz, ip_from=user_ip, personal=True)

    def test_with_phone__ok(self):
        self.setup_blackbox_free_login()
        self.setup_blackbox_phone_bindings()

        rv = self.make_request(
            self.phone_query_params(),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok(
            centraldb_queries=5,
            sharddb_queries=5,
            firstname=None,
            lastname=None,
            hint_question=None,
            hint_answer=None,
            phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_historydb_and_statbox_records__ok(
            phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_yasms_not_called()
        self.assert_frodo__ok(phone=True)
        self.assert_no_emails_sent()

    def test_with_valid_yandexuid__ok(self):
        self.setup_blackbox_free_login()
        self.setup_blackbox_phone_bindings()

        rv = self.make_request(
            self.phone_query_params(),
            build_headers(cookie='yandexuid=2038872231466443337'),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()

        self.assert_db__ok(
            centraldb_queries=5,
            sharddb_queries=5,
            firstname=None,
            lastname=None,
            hint_question=None,
            hint_answer=None,
            phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_historydb_and_statbox_records__ok(
            phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_yasms_not_called()
        self.assert_frodo__ok(phone=True, yandexuid='2038872231466443337')
        self.assert_no_emails_sent()

    def test_with_phone_and_aliasify_ok(self):
        self.setup_blackbox_free_login()
        self.setup_blackbox_phone_bindings()

        # Проверяем, привязан ли данный телефон как алиас к другому аккаунту
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request(
            self.phone_query_params(create_phone_alias=True),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()
        self.assert_db__ok(
            centraldb_queries=5,
            sharddb_queries=6,
            phonenumber_alias=TEST_PHONE_NUMBER,
            firstname=None,
            lastname=None,
            hint_question=None,
            hint_answer=None,
            phone_number=TEST_PHONE_NUMBER,
        )
        self.assert_historydb_and_statbox_records__ok(
            phone_number=TEST_PHONE_NUMBER,
            aliasify=True,
        )
        self.assert_yasms_not_called()
        self.assert_frodo__ok(phone=True)

        # отправлено одно письмо о привязке алиаса
        self.assert_emails_sent([
            {
                'language': 'ru',
                'addresses': ['%s@%s' % (TEST_PHONE_NUMBER.digital, 'yandex.ru')],
                'subject': 'digitreg.subject',
                'tanker_keys': {
                    'signature.mail': {},
                    'digitreg.notebook_url': {},
                    'digitreg.explanation': {
                        'PHONE_ALIAS_LOGIN': span(TEST_PHONE_NUMBER.digital, 'font-weight: bold;'),
                        'PORTAL_LOGIN': self.get_portal_login_markup(TEST_USER_LOGIN),
                    },
                },
            },
        ])

    def test_with_phone_and_dealiasify_and_aliasify_ok(self):
        self.setup_blackbox_free_login()
        self.setup_blackbox_phone_bindings()

        blackbox_response_with_alias = blackbox_userinfo_response(
            uid=str(TEST_UID_2),
            login=TEST_PHONE_NUMBER.digital,
            aliases={
                'portal': 'alias_owner',
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            attributes={'account.enable_search_by_phone_alias': '1'},
            emails=[{
                'default': True,
                'native': True,
                'validated': True,
                'address': 'withalias@yandex.ru',
            }],
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response_with_alias,
        )

        rv = self.make_request(
            self.phone_query_params(
                create_phone_alias=True,
                language='en',
            ),
            build_headers(),
        )

        self.assert_ok_response(rv, uid=TEST_UID)
        self.assert_track__ok()
        self.assert_db__ok(
            centraldb_queries=7,
            sharddb_queries=7,
            phonenumber_alias=TEST_PHONE_NUMBER,
            phone_number=TEST_PHONE_NUMBER,
            language='en',
            dealiasify=True,
            firstname=None,
            lastname=None,
            hint_question=None,
            hint_answer=None,
        )
        self.assert_historydb_and_statbox_records__ok(
            phone_number=TEST_PHONE_NUMBER,
            aliasify=True,
            dealiasify=True,
            language='en',
        )
        self.assert_yasms_not_called()
        self.assert_frodo__ok(phone=True, language='en')

        # отправлено два письма: об отвязке и привязке алиаса
        self.assert_emails_sent([
            partial(
                assert_user_notified_about_alias_as_login_and_email_owner_changed,
                mailer_faker=self.env.mailer,
                language='ru',
                email_address='withalias@yandex.ru',
                firstname='\u0414',
                login='login',
                portal_email='login@yandex.ru',
                phonenumber_alias=TEST_PHONE_NUMBER.digital,
            ),
            {
                'language': 'en',
                'addresses': ['%s@%s' % (TEST_PHONE_NUMBER.digital, 'yandex.ru')],
                'subject': 'digitreg.subject',
                'tanker_keys': {
                    'signature.mail': {},
                    'digitreg.notebook_url': {},
                    'digitreg.explanation': {
                        'PHONE_ALIAS_LOGIN': span(TEST_PHONE_NUMBER.digital, 'font-weight: bold;'),
                        'PORTAL_LOGIN': self.get_portal_login_markup(TEST_USER_LOGIN),
                    },
                },
            },
        ])


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountRegisterAlternativeEasyV2NoBlackboxHash(TestAccountRegisterAlternativeEasyV2):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
