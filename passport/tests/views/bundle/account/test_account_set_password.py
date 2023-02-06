# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import BaseMdapiTestCase
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_hosted_domains_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.models.domain import Domain
from passport.backend.core.models.password import (
    PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
    PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
)
from passport.backend.core.test.data import (
    TEST_PASSWORD_HASH_MD5_CRYPT_ARGON,
    TEST_PASSWORD_HASH_RAW_MD5_ARGON,
    TEST_SERIALIZED_PASSWORD,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.types.account.account import (
    KINOPOISK_UID_BOUNDARY,
    PDD_UID_BOUNDARY,
)
from passport.backend.utils.common import merge_dicts


BEGINNING_OF_TIME = datetime.fromtimestamp(1).strftime('%Y-%m-%d %H:%M:%S')

TEST_IP = '3.3.3.3'
TEST_UID = 1
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_PDD_2FA_UID = TEST_PDD_UID + 1
TEST_KP_UID = KINOPOISK_UID_BOUNDARY + 1

TEST_LOGIN = 'admin'
TEST_DOMAIN = 'okna.ru'
TEST_PDD_LOGIN = '%s@%s' % (TEST_LOGIN, TEST_DOMAIN)
TEST_KP_LOGIN = ''
TEST_PASSWORD = 'password123'
TEST_SALTED_PASSWORD_HASH = '$1$boTQI3R3$aWySwHZUZRPjIGEMz.sep.'
TEST_HEX_PASSWORD_HASH = '1e82635542756448df026aed77612103'
TEST_SERIALIZED_ARGONIZED_RAW_MD5_HASH = '%s:%s' % (PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON, TEST_PASSWORD_HASH_RAW_MD5_ARGON)
TEST_SERIALIZED_ARGONIZED_CRYPT_MD5_HASH = '%s:%s' % (PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON, TEST_PASSWORD_HASH_MD5_CRYPT_ARGON)
TEST_PASSWORD_QUALITY = 71

Response = namedtuple('Response', ['content', 'status_code'])


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class TestAccountSetPasswordView(BaseMdapiTestCase):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON
    mocked_grants = ['account.set_password']

    def set_request_uid(self, uid):
        self.url = '/1/bundle/account/%d/password/?consumer=dev' % uid

    def check_new_password_saved_to_db(self, uid, is_password_changing_required=False):
        self.env.db.check(
            'attributes',
            'password.update_datetime',
            TimeNow(),
            uid=uid,
            db='passportdbshard2',
        )
        pass_hash_eav = self.env.db.get('attributes', 'password.encrypted', uid=uid, db='passportdbshard2')
        if self.is_password_hash_from_blackbox:
            eq_(pass_hash_eav, TEST_SERIALIZED_PASSWORD)
        else:
            ok_(pass_hash_eav.startswith('%s:' % self.password_hash_version))
        if is_password_changing_required:
            self.env.db.check(
                'attributes',
                'password.forced_changing_reason',
                PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
                uid=uid,
                db='passportdbshard2',
            )
        else:
            self.env.db.check_missing(
                'attributes',
                'password.forced_changing_reason',
                uid=uid,
                db='passportdbshard2',
            )

    def check_password_hash_saved_to_db(self, uid, hash):
        self.env.db.check(
            'attributes',
            'password.encrypted',
            hash,
            uid=uid,
            db='passportdbshard2',
        )
        self.env.db.check_missing(
            'attributes',
            'password.quality',
            uid=uid,
            db='passportdbshard2',
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='account_set_password',
            consumer='dev',
            ip=TEST_IP,
            uid=str(TEST_PDD_UID),
            user_agent='curl',
            unixtime=TimeNow(),
        )
        self.env.statbox.bind_entry(
            'local_base',
            user_agent='curl',
            ip=TEST_IP,
            operation='created',
        )
        self.env.statbox.bind_entry(
            'submitted',
            _exclude=['uid'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'set_password',
            action='set_password',
            is_hash='0',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from=['local_base'],
            _exclude=['mode'],
            consumer='-',
            event='account_modification',
            entity=None,
            old='-',
            ip=TEST_IP,
            operation='created',
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            '2fa_disabled',
            action='2fa_disabled',
        )

    def check_password_change_recorded_to_statbox(self, uid, is_hash=False,
                                                  otp_disabled=False,
                                                  quality=TEST_PASSWORD_QUALITY,
                                                  password_version=None,
                                                  is_password_changing_required=False):
        expected_records = [
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry(
                'set_password',
                is_hash=str(int(is_hash)),
                uid=str(uid),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='account.global_logout_datetime',
                old=BEGINNING_OF_TIME,
                new=DatetimeNow(convert_to_datetime=True),
                uid=str(uid),
                operation='updated',
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.encrypted',
                _exclude=['old', 'new'],
                uid=str(uid),
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='password.encoding_version',
                uid=str(uid),
                new=str(password_version or self.password_hash_version),
            ),
        ]

        if quality is not None:
            expected_records.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.quality',
                    new=str(quality),
                    uid=str(uid),
                ),
            )

        if is_password_changing_required:
            expected_records.append(
                self.env.statbox.entry(
                    'account_modification',
                    entity='password.is_changing_required',
                    new=PASSWORD_CHANGING_REASON_FLUSHED_BY_ADMIN,
                    uid=str(uid),
                ),
            )

        if otp_disabled:
            expected_records.insert(
                2,
                self.env.statbox.entry(
                    '2fa_disabled',
                    uid=str(uid),
                ),
            )

        self.env.statbox.assert_equals(expected_records)

    def check_password_change_recorded_to_historydb(self, uid,
                                                    quality=TEST_PASSWORD_QUALITY,
                                                    otp_disabled=False,
                                                    is_password_changing_required=False):
        eav_pass_hash = self.env.db.select(
            'attributes',
            'password.encrypted',
            db='passportdbshard2',
        )[0][2]

        historydb_record = [
            ('action', 'set_password'),
            ('info.glogout', TimeNow()),
            ('info.password', eav_pass_hash),
            ('info.password_quality', str(quality) if quality else None),
            ('info.password_update_time', TimeNow()),
        ]
        if is_password_changing_required:
            historydb_record.append(('sid.login_rule', '8|5'))
        historydb_record.append(('user_agent', 'curl'))

        if otp_disabled:
            historydb_record.insert(5, ('info.totp_update_time', '-'))
            historydb_record.insert(5, ('info.totp', 'disabled'))

        historydb_entries = [
            {
                'uid': str(uid),
                'name': k,
                'value': v,
            }
            for k, v in historydb_record if v is not None
        ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            historydb_entries,
        )

        # Проверяем, что события historydb можно потом отпарсить для выдаче в ручке /account/events
        parsed_events = self.env.event_logger.parse_events()
        eq_(len(parsed_events), 1)
        expected_actions = [
            {
                'type': 'global_logout',
            },
            {
                'type': 'password_change',
            },
        ]
        if otp_disabled:
            expected_actions.append({
                'type': 'totp_disabled',
            })

        eq_(parsed_events[0].event_type, 'password')
        eq_(sorted(expected_actions), parsed_events[0].actions)

    def setUp(self):
        super(TestAccountSetPasswordView, self).setUp()
        self.userinfo = {}
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            self.blackbox_userinfo_selector,
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.create_user(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases=dict(pdd=TEST_PDD_LOGIN),
            domain=TEST_DOMAIN,
            domid=1,
        )
        self.create_user(
            uid=TEST_KP_UID,
            login=TEST_KP_LOGIN,
            aliases=dict(kinopoisk='100500'),
        )
        self.create_user(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )

        hosted_domains_response = blackbox_hosted_domains_response(
            count=1,
            domid=1,
            domain=TEST_DOMAIN,
            is_enabled=True,
            can_users_change_password=False,
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            hosted_domains_response,
        )
        test_domain = Domain().parse(
            get_parsed_blackbox_response(
                'hosted_domains',
                hosted_domains_response,
            ),
        )
        self.env.db._serialize_to_eav(test_domain)
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.setup_statbox_templates()
        self.form_data = {
            'password': TEST_PASSWORD,
        }

    def blackbox_userinfo_selector(self, method, url, params, **kwargs):
        return Response(status_code=200, content=self.userinfo[params['uid']])

    def create_user(self, uid, login, **kwargs):
        userinfo_args = {
            'uid': uid,
            'login': login,
        }
        userinfo_response = blackbox_userinfo_response(
            **merge_dicts(
                userinfo_args,
                kwargs,
            )
        )
        self.userinfo[uid] = userinfo_response
        self.env.db.serialize(userinfo_response)

    def test_error_change_password_pdd_no_specific_grants(self):
        self.set_request_uid(TEST_PDD_UID)
        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['access.denied'],
        )

    def test_error_change_password_kinopoisk_no_specific_grants(self):
        self.set_request_uid(TEST_KP_UID)
        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['access.denied'],
        )

    def test_error_change_password_normal_user_invalid_type(self):
        self.set_request_uid(TEST_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
        ])
        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['account.invalid_type'],
        )

    def test_change_password_pdd_ok(self):
        self.set_request_uid(TEST_PDD_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
        ])

        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_new_password_saved_to_db(TEST_PDD_UID)
        self.check_password_change_recorded_to_statbox(TEST_PDD_UID)
        self.check_password_change_recorded_to_historydb(TEST_PDD_UID)

    def test_change_password_pdd_with_force_password_change_ok(self):
        self.set_request_uid(TEST_PDD_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
        ])

        resp = self.make_request(data=dict(self.form_data, force_password_change='1'))
        self.check_response_ok(resp)

        self.check_new_password_saved_to_db(TEST_PDD_UID, is_password_changing_required=True)
        self.check_password_change_recorded_to_statbox(TEST_PDD_UID, is_password_changing_required=True)
        self.check_password_change_recorded_to_historydb(TEST_PDD_UID, is_password_changing_required=True)

    def test_change_password_hash_pdd_ok(self):
        self.set_request_uid(TEST_PDD_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
            'account.set_password_hash',
        ])

        self.form_data = {
            'password_hash': TEST_SALTED_PASSWORD_HASH,
        }
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_ARGONIZED_CRYPT_MD5_HASH),
        )
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_password_hash_saved_to_db(TEST_PDD_UID, TEST_SERIALIZED_ARGONIZED_CRYPT_MD5_HASH)
        self.check_password_change_recorded_to_statbox(
            TEST_PDD_UID,
            is_hash=True,
            quality=None,
            password_version=PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
        )
        self.check_password_change_recorded_to_historydb(TEST_PDD_UID, quality=0)

    def test_change_password_hash_hex_pdd_ok(self):
        self.set_request_uid(TEST_PDD_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
            'account.set_password_hash',
        ])
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_ARGONIZED_RAW_MD5_HASH),
        )

        self.form_data = {
            'password_hash': TEST_HEX_PASSWORD_HASH,
        }
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_password_hash_saved_to_db(
            TEST_PDD_UID,
            TEST_SERIALIZED_ARGONIZED_RAW_MD5_HASH,
        )
        self.check_password_change_recorded_to_statbox(
            TEST_PDD_UID,
            is_hash=True,
            quality=None,
            password_version=PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
        )
        self.check_password_change_recorded_to_historydb(TEST_PDD_UID, quality=0)

    def test_error_change_password_hash_no_specific_grants(self):
        self.set_request_uid(TEST_PDD_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
        ])

        self.form_data = {
            'password_hash': TEST_SALTED_PASSWORD_HASH,
        }
        resp = self.make_request(data=self.form_data)
        self.check_error_response(
            resp,
            ['access.denied'],
        )

    def test_change_password_hash_hex_kinopoisk_ok(self):
        self.set_request_uid(TEST_KP_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_kinopoisk',
            'account.set_password_hash',
        ])
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_ARGONIZED_RAW_MD5_HASH),
        )

        self.form_data = {
            'password_hash': TEST_HEX_PASSWORD_HASH,
        }
        resp = self.make_request(data=self.form_data)
        self.check_response_ok(resp)

        self.check_password_hash_saved_to_db(
            TEST_KP_UID,
            TEST_SERIALIZED_ARGONIZED_RAW_MD5_HASH,
        )
        self.check_password_change_recorded_to_statbox(
            TEST_KP_UID,
            is_hash=True,
            quality=None,
            password_version=PASSWORD_ENCODING_VERSION_RAW_MD5_ARGON,
        )
        self.check_password_change_recorded_to_historydb(TEST_KP_UID, quality=0)

    def test_password_change_turns_2fa_off(self):
        self.set_request_uid(TEST_PDD_2FA_UID)
        self.env.grants.set_grant_list([
            'account.set_password',
            'account.set_password_pdd',
        ])
        self.create_user(
            TEST_PDD_2FA_UID,
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            attributes={
                'account.2fa_on': '1',
            },
        )
        self.make_request(data=self.form_data)

        self.check_password_change_recorded_to_statbox(
            TEST_PDD_2FA_UID,
            otp_disabled=True,
        )
        self.check_password_change_recorded_to_historydb(
            TEST_PDD_2FA_UID,
            otp_disabled=True,
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class TestAccountSetPasswordViewNoBlackboxHash(TestAccountSetPasswordView):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
