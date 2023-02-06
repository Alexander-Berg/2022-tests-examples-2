# -*- coding: utf-8 -*-
import base64
import datetime
import json

from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_pwdhistory_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api import SocialApiTemporaryError
from passport.backend.core.eav_type_mapping import (
    ATTRIBUTE_NAME_TO_TYPE as AT,
    EXTENDED_ATTRIBUTES_EMAIL_TYPE,
)
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_no_default_phone_chosen,
    assert_no_phone_in_db,
    assert_no_secure_phone,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import deep_merge


TEST_LOGIN = 'login'
TEST_DOMAIN = 'okna.ru'
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_PDD_UID = 1130000000000001
TEST_USER_IP = '8.8.8.8'
TEST_HOST = 'passport-test.yandex.ru'
TEST_COOKIE = 'foo=bar'
TEST_USER_AGENT = 'curl'
TEST_PASSWORD_QUALITY = 30
TEST_PASSWORD_QUALITY_VERSION = 3
TEST_OLD_SERIALIZED_PASSWORD = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'
TEST_PASSWORD_CHANGING_REQUIRED_HACKED = 1
TEST_PASSWORD_CHANGING_REASON_ADMIN = 2

TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=datetime.datetime.fromtimestamp(1),
)
TEST_USER_COUNTRY = 'ru'
TEST_USER_FIRSTNAME = 'a'
TEST_USER_LASTNAME = 'b'
TEST_USER_LANGUAGE = 'ru'
TEST_USER_TIMEZONE = 'Europe/Moscow'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_HINT_QUESTION = '99:question'
TEST_HINT_ANSWER = 'answer'
TEST_TOTP_CHECK_TIME = '123456'
TEST_TOTP_UPDATE_DATETIME = '12345678'

TEST_NEW_PASSWORD = 'secret-password'  # password quality = 100
TEST_NEW_PASSWORD_QUALITY = 100

TEST_DB_NAME = 'passportdbshard2'

# Эта история плохих сессий содержит одно синтетическое значение
# SessionKarma(timestamp=0, authid='test-authid')
TEST_BAD_SESSIONS = base64.b64encode('\x08\x01\x12\x13\x08\x01\x10\x00\x1a\x0btest-authid d')


TEST_PHONE_ID = 1
TEST_PHONE_NUMBER = '+79091232233'
TEST_PHONE_SECURED_ID = 2
TEST_PHONE_SECURED_NUMBER = '+79091232244'


class BaseFlushPddTestCase(BaseBundleTestViews, EmailTestMixin):

    default_url = None
    http_method = 'post'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_COOKIE,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'pdd': ['flush']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_account(self, **kwargs):
        if not kwargs:
            kwargs = self.account_kwargs()
        blackbox_response = blackbox_userinfo_response(**kwargs)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

        # Сериализатора для totp.check_time нет, поэтому запишем какой-нибудь мусор
        self.env.db.insert(
            table_name='attributes',
            db='passportdbshard2',
            uid=TEST_PDD_UID,
            type=AT['account.totp.check_time'],
            value=TEST_TOTP_CHECK_TIME,
        )

        # Сериализатор для totp.update_time пока что, работает только на создании модели totp
        self.env.db.insert(
            table_name='attributes',
            db='passportdbshard2',
            uid=TEST_PDD_UID,
            type=AT['account.totp.update_datetime'],
            value=TEST_TOTP_UPDATE_DATETIME,
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def account_kwargs(self, with_subscriptions=True, with_phone=True, **kwargs):
        base_kwargs = dict(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            domain=TEST_DOMAIN,
            dbfields={
                'password_quality.quality.uid': TEST_PASSWORD_QUALITY,
                'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
                'subscription.login_rule.8': 5,
            },
            attributes={
                'person.firstname': TEST_USER_FIRSTNAME,
                'person.lastname': TEST_USER_LASTNAME,
                'person.country': TEST_USER_COUNTRY,
                'person.timezone': TEST_USER_TIMEZONE,
                'person.language': TEST_USER_LANGUAGE,
                'account.totp.secret': '1',
                'account.totp.secret_ids': '1:100',
                'account.totp.failed_pin_checks_count': '2',
                'account.enable_app_password': '1',
                'password.forced_changing_reason': '1',
                'password.encrypted': TEST_OLD_SERIALIZED_PASSWORD,
                # обычно sms_2fa не может быть включёна одновременно с обычной 2fa, но для теста это не важно
                'account.sms_2fa_on': '1',
                'account.forbid_disabling_sms_2fa': '1',
            },
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        if with_subscriptions:
            base_kwargs['subscribed_to'] = [
                100,
                102,
            ]
        if with_phone:
            phone = build_phone_bound(
                TEST_PHONE_ID,
                TEST_PHONE_NUMBER,
                is_default=True,
            )
            phone_secured = build_phone_secured(
                TEST_PHONE_SECURED_ID,
                TEST_PHONE_SECURED_NUMBER,
                is_default=False,
            )
            phones = deep_merge(phone, phone_secured)
            base_kwargs = deep_merge(base_kwargs, phones)
        return deep_merge(base_kwargs, kwargs)

    def check_response(self, rv, expected_values):
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            expected_values,
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestFlushPddSubmit(BaseFlushPddTestCase):
    default_url = '/1/account/%s/flush_pdd/submit/?consumer=dev' % TEST_PDD_UID

    def setUp(self):
        super(TestFlushPddSubmit, self).setUp()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

    def tearDown(self):
        self.track_id_generator.stop()
        del self.track_id_generator
        super(TestFlushPddSubmit, self).tearDown()

    def check_statbox(self):
        entries = [
            self.env.statbox.entry(
                'submitted',
                action='submitted',
                mode='flush_pdd',
                uid=str(TEST_PDD_UID),
                track_id=self.track_id,
                consumer='dev',
            ),
        ]
        self.env.statbox.assert_has_written(entries)

    def check_track_poststate(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_PDD_UID))
        eq_(track.is_strong_password_policy_required, False)
        eq_(track.login, TEST_PDD_LOGIN)
        assert_is_none(track.password_hash)

    def check_blackbox_call(self):
        eq_(self.env.blackbox._mock.request.call_count, 1)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_PDD_UID,
        })

    def test_ok(self):
        self.setup_account()
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'ok',
                'track_id': self.track_id,
            },
        )
        self.check_track_poststate()
        self.check_statbox()
        self.check_blackbox_call()

    def test_account_not_found(self):
        blackbox_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        rv = self.make_request(query_args=dict(uid=1))
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['account.not_found'],
            },
        )

    def test_not_pdd(self):
        self.setup_account(
            uid=1,
            login=TEST_LOGIN,
            aliases={
                'portal': TEST_LOGIN,
            },
            domain=TEST_DOMAIN,
            subscribed_to=[100],
        )
        rv = self.make_request(query_args=dict(uid=1))
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['account.invalid_type'],
            },
        )

    def test_attempt_to_change_track_uid(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID + 1
        rv = self.make_request(query_args=dict(track_id=self.track_id))
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['track.invalid_state'],
                'track_id': self.track_id,
            },
        )


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    SOCIAL_API_URL='http://localhost/',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class BaseFlushPddCommitTestCase(BaseFlushPddTestCase):
    default_url = '/1/account/%s/flush_pdd/commit/?consumer=dev' % TEST_PDD_UID
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        super(BaseFlushPddCommitTestCase, self).setUp()

        self.env.social_api.set_social_api_response_value('')

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID

        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: False}),
        )

        self.http_query_args = dict(
            track_id=self.track_id,
            password=TEST_NEW_PASSWORD,
            quality=TEST_NEW_PASSWORD_QUALITY,
        )

    def check_attribute(self, attribute, value):
        self.env.db.check('attributes', attribute, value, uid=TEST_PDD_UID, db=TEST_DB_NAME)

    def check_attribute_missing(self, attribute):
        self.env.db.check_missing('attributes', attribute, uid=TEST_PDD_UID, db=TEST_DB_NAME)

    def check_db(self, pwd_changing_reason=None):
        timenow = TimeNow()

        # персональные данные

        for attribute in (
            'person.firstname',
            'person.lastname',
            'person.gender',
            'person.birthday',
            'person.country',
            'person.language',
            'person.timezone',

            # прочие поля
            'account.browser_key',
            # карма
            'karma.value',
            # пароль
            'account.totp.secret',
            'account.totp.update_datetime',
            'account.totp.failed_pin_checks_count',
            'account.totp.check_time',
            'account.enable_app_password',
            'account.sms_2fa_on',

            'password.is_creating_required',
            'account.is_pdd_agreement_accepted',
        ):
            self.check_attribute_missing(attribute)

        if pwd_changing_reason:
            self.check_attribute('password.forced_changing_reason', str(pwd_changing_reason))
        else:
            self.check_attribute_missing('password.forced_changing_reason')

        # этот атрибут не изменился, но и не помешал выключить sms_2fa
        self.check_attribute('account.forbid_disabling_sms_2fa', '1')

        self.check_attribute('account.global_logout_datetime', timenow)
        self.check_attribute('password.update_datetime', timenow)
        self.check_attribute('password.quality', '3:%s' % TEST_NEW_PASSWORD_QUALITY)
        # телефоны, emails, соц. профили - не проверить, проверим вызовы
        assert_no_phone_in_db(
            self.env.db,
            TEST_PDD_UID,
            TEST_PHONE_ID,
            TEST_PHONE_NUMBER,
        )
        assert_no_phone_in_db(
            self.env.db,
            TEST_PDD_UID,
            TEST_PHONE_SECURED_ID,
            TEST_PHONE_SECURED_NUMBER,
        )
        assert_no_secure_phone(
            self.env.db,
            TEST_PDD_UID,
        )
        assert_no_default_phone_chosen(
            self.env.db,
            TEST_PDD_UID,
        )

    def check_historydb(self, with_subscriptions=True, with_phone=True, pwd_changing_required=False):
        eav_pass_hash = self.env.db.get(
            'attributes',
            'password.encrypted',
            uid=TEST_PDD_UID,
            db=TEST_DB_NAME,
        )
        entries = {
            'info.firstname': '-',
            'info.lastname': '-',
            'info.sex': '-',
            'info.birthday': '-',
            'info.country': '-',
            'info.lang': '-',
            'info.tz': '-',
            'info.hintq': '-',
            'info.hinta': '-',
            'info.totp': 'disabled',
            'info.totp_secret.1': '-',
            'info.totp_update_time': '-',
            'info.enable_app_password': '-',
            'info.sms_2fa_on': '0',
            'info.glogout': TimeNow(),
            'info.password': eav_pass_hash,
            'info.password_update_time': TimeNow(),
            'info.password_quality': '100',
            'sid.login_rule': '8|1',
            'action': 'flush_pdd',
            'consumer': 'dev',
            'user_agent': 'curl',
        }
        if with_subscriptions:
            entries['sid.rm'] = '100|%(login)s,102|%(login)s' % {'login': TEST_PDD_LOGIN}

        if pwd_changing_required:
            entries['sid.login_rule'] = '8|5'

        if with_phone:
            secured_number = PhoneNumber.parse(TEST_PHONE_SECURED_NUMBER)
            entries.update({
                'phone.%s.action' % TEST_PHONE_ID: 'deleted',
                'phone.%s.number' % TEST_PHONE_ID: TEST_PHONE_NUMBER,
                'phone.%s.action' % TEST_PHONE_SECURED_ID: 'deleted',
                'phone.%s.number' % TEST_PHONE_SECURED_ID: TEST_PHONE_SECURED_NUMBER,
                'phones.default': '0',
                'phones.secure': '0',

            })
        self.assert_events_are_logged(
            self.env.handle_mock,
            entries,
        )

    def check_calls_to_blackbox(self):
        call_count = 4 if self.is_password_hash_from_blackbox else 3
        eq_(len(self.env.blackbox.requests), call_count)
        userinfo_request = self.env.blackbox.requests[0]
        userinfo_request.assert_post_data_contains({
            'method': 'userinfo',
            'uid': TEST_PDD_UID,
        })
        userinfo_request.assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        userinfo_request.assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def check_calls_to_social_api(self):
        eq_(self.env.social_api._mock.request.call_count, 1)
        eq_(
            self.env.social_api._mock.request.call_args[0][1],
            'http://localhost/user/%d?consumer=passport' % TEST_PDD_UID,
        )

    def check_calls_to_services(self):
        self.check_calls_to_blackbox()
        self.check_calls_to_social_api()

    def check_statbox(self, with_subscriptions=True, with_phone=True, pwd_changing_reason=0,
                      old_changing_required_reason=TEST_PASSWORD_CHANGING_REQUIRED_HACKED):
        self.env.statbox.bind_entry(
            'account_modification',
            uid=str(TEST_PDD_UID),
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            consumer='dev',
        )
        entries = []

        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                entity='account.enable_app_password',
                operation='deleted',
                new='-',
                old='1',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.global_logout_datetime',
                operation='updated',
                new=DatetimeNow(convert_to_datetime=True),
                old=TEST_GLOBAL_LOGOUT_DATETIME,
            ),
        ])
        if with_phone:
            entries.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='phones.secure',
                    operation='deleted',
                    new='-',
                    new_entity_id='-',
                    old='+79091******',
                    old_entity_id=str(TEST_PHONE_SECURED_ID),
                ),
            )
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='account.sms_2fa_on',
                operation='updated',
                new='0',
                old='1',
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.firstname',
                operation='deleted',
                new='-',
                old=TEST_USER_FIRSTNAME,
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.lastname',
                operation='deleted',
                new='-',
                old=TEST_USER_LASTNAME,
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.language',
                operation='deleted',
                new='-',
                old=TEST_USER_LANGUAGE,
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.country',
                operation='deleted',
                new='-',
                old=TEST_USER_COUNTRY,
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.gender',
                operation='deleted',
                new='-',
                old='m',
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.birthday',
                operation='deleted',
                new='-',
                old='1963-05-15',
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='person.fullname',
                operation='deleted',
                new='-',
                old='{} {}'.format(TEST_USER_FIRSTNAME, TEST_USER_LASTNAME),
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='password.encrypted',
                operation='updated',
            ),
        ])
        if self.password_hash_version == PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON:
            entries.append(self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='password.encoding_version',
                operation='updated',
                new=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON),
                old=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT),
            ))
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='password.quality',
                operation='updated',
                new=str(TEST_NEW_PASSWORD_QUALITY),
                old=str(TEST_PASSWORD_QUALITY),
            ),
            self.env.statbox.entry(
                'account_modification',
                uid=str(TEST_PDD_UID),
                entity='password.is_changing_required',
                operation='deleted' if not pwd_changing_reason else 'created',
                new='-' if not pwd_changing_reason else str(pwd_changing_reason),
                old=str(old_changing_required_reason) if old_changing_required_reason else '-',
            ),
        ])
        if with_subscriptions:
            entries.extend([
                self.env.statbox.entry(
                    'account_modification',
                    uid=str(TEST_PDD_UID),
                    entity='subscriptions',
                    operation='removed',
                    sid='100',
                ),
                self.env.statbox.entry(
                    'account_modification',
                    uid=str(TEST_PDD_UID),
                    entity='subscriptions',
                    operation='removed',
                    sid='102',
                ),
            ])
        entries.extend([
            self.env.statbox.entry(
                'flushed',
                action='flushed',
                mode='flush_pdd',
                track_id=self.track_id,
                uid=str(TEST_PDD_UID),
                consumer='dev',
            ),
        ])

        self.env.statbox.assert_has_written(entries)


class TestFlushPddCommitTestCase(BaseFlushPddCommitTestCase):

    def check_db(self, pwd_changing_reason=None):
        super(TestFlushPddCommitTestCase, self).check_db(pwd_changing_reason=pwd_changing_reason)
        self.env.db.check_missing(
            'extended_attributes',
            'value',
            entity_type=EXTENDED_ATTRIBUTES_EMAIL_TYPE,
            uid=TEST_PDD_UID,
            db='passportdbshard2',
        )

    def test_ok(self):
        self.setup_account()
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'ok',
            },
        )
        self.check_statbox()
        self.check_db()
        self.check_historydb()
        self.check_calls_to_services()

    def test_invalid_track_state(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = None
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['track.invalid_state'],
            },
        )

    def test_uids_from_track_and_url_differ(self):
        self.setup_account()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 2
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['track.invalid_state'],
            },
        )

    def test_not_pdd(self):
        self.setup_account(
            uid=1,
            login=TEST_LOGIN,
        )
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'error',
                'errors': ['account.invalid_type'],
            },
        )

    def test_pdd_not_complete(self):
        self.setup_account(**self.account_kwargs(with_phone=False))
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'ok',
            },
        )
        self.check_statbox(with_phone=False)
        self.check_db()
        self.check_historydb(with_phone=False)
        self.check_calls_to_services()

    def test_pdd_absolutely_not_complete(self):
        self.setup_account(**self.account_kwargs(with_subscriptions=False, with_phone=False))
        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'ok',
            },
        )
        self.check_statbox(with_subscriptions=False, with_phone=False)
        self.check_db()
        self.check_historydb(with_subscriptions=False, with_phone=False)
        self.check_calls_to_services()

    def test_external_services_failed(self):
        self.setup_account()
        self.env.social_api.set_social_api_response_side_effect(
            SocialApiTemporaryError(),
        )

        rv = self.make_request()
        self.check_response(
            rv,
            {
                'status': 'ok',
            },
        )
        self.check_statbox()
        self.check_db()

    def test_force_password_change(self):
        account_kwargs = self.account_kwargs(attributes={'password.forced_changing_reason': None})
        self.setup_account(**account_kwargs)
        rv = self.make_request(query_args={'force_password_change': '1'})
        self.check_response(
            rv,
            {
                'status': 'ok',
            },
        )
        self.check_statbox(
            pwd_changing_reason=TEST_PASSWORD_CHANGING_REASON_ADMIN,
            old_changing_required_reason=0,
        )
        self.check_db(pwd_changing_reason=TEST_PASSWORD_CHANGING_REASON_ADMIN)
        self.check_historydb(pwd_changing_required=True)
        self.check_calls_to_services()


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestFlushPddCommitTestCaseNoBlackboxHash(TestFlushPddCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
