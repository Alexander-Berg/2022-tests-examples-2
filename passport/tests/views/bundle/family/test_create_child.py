# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BIRTHDAY,
    TEST_CONSUMER,
    TEST_FAMILY_ID,
    TEST_FIRSTNAME,
    TEST_GENDER,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_PASSWORD,
    TEST_PASSWORD_QUALITY,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER1,
    TEST_SERIALIZED_PASSWORD,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import merge_dicts

TEST_CONTENT_RATING_CLASS = 1
TKSV_FORMAT = 'passport-log'
TIMEZONE = '+0300'


class CreateChildTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/create_child/'
    consumer = TEST_CONSUMER
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(CreateChildTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'family': ['create_child']}),
        )
        self.setup_shakur()
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()
        del self.env

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'login': TEST_LOGIN,
            'password': TEST_PASSWORD,
            'firstname': TEST_FIRSTNAME,
            'birthday': TEST_BIRTHDAY,
            'gender': TEST_GENDER,
            'lastname': TEST_LASTNAME,
            'country': TEST_LANGUAGE,
            'language': TEST_LANGUAGE,
            'display_language': TEST_LANGUAGE,
            'force_clean_web': True,
            'eula_accepted': True,
            'content_rating_class': TEST_CONTENT_RATING_CLASS

        }
        return merge_dicts(base_params, kwargs)

    def test_account_and_track_without_secure_phone(self):
        self.setup_account_without_phone()
        self.setup_track_without_phone()
        self.http_query_args = self.query_params()
        rv = self.make_request(headers=self.http_headers)
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_account_without_secure_phone(self):
        self.setup_account_without_phone()
        self.setup_track_with_phone()
        self.http_query_args = self.query_params()
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_expired_confirmation_without_track_phone(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_without_phone()
        self.http_query_args = self.query_params()
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_expired_confirmation_track_not_confirmed(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone(confirmed=False)
        self.http_query_args = self.query_params()
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_account_and_track_diff_secure_phone(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone(number=TEST_PHONE_NUMBER1)
        self.http_query_args = self.query_params()
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['phone.not_confirmed'])

    def test_eula_not_accepted(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone(number=TEST_PHONE_NUMBER1)
        self.http_query_args = self.query_params(**{'eula_accepted': False})
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['eula_accepted.not_accepted'])

    def test_family_not_exist(self):
        self.setup_account_with_secure_phone(expired=True, has_family=False)
        self.setup_track_with_phone()
        self.http_query_args = self.query_params()
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['family.does_not_exist'])

    def test_family_overflowing(self):
        self.setup_account_with_secure_phone(expired=True, family_overflow=True)
        self.setup_track_with_phone()
        self.http_query_args = self.query_params()
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, 20, 30, 40], [0, 1, 2, 3])
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_error_response(rv, ['family.max_capacity'])

    def test_account_expired_track_eq(self):
        self.setup_account_with_secure_phone(expired=True)
        self.setup_track_with_phone()
        self.http_query_args = self.query_params()
        self._members_uid_to_db([TEST_UID])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID])
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_ok_response(rv, uid=TEST_UID2)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_db_written()

    def test_account_recently_confirmed(self):
        self.setup_account_with_secure_phone()
        self.setup_track_with_phone()
        self.http_query_args = self.query_params()
        self._members_uid_to_db([TEST_UID])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID])
        rv = self.make_request(headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'})
        self.assert_ok_response(rv, uid=TEST_UID2)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_db_written()

    def setup_account_with_secure_phone(self, expired=False, has_family=True, family_overflow=False):
        confirmed = datetime.now() - timedelta(hours=4) if expired else datetime.now()
        members = [TEST_UID, 20, 30, 40] if family_overflow else [TEST_UID]
        secure_phone = build_phone_secured(
            phone_id=TEST_PHONE_ID1,
            phone_number=TEST_PHONE_NUMBER.e164,
            phone_confirmed=confirmed
        )
        self.setup_bb_response(
            has_family=has_family, family_members=members, secure_phone=secure_phone)

    def setup_account_without_phone(
        self,
    ):
        self.env.blackbox.set_blackbox_response_value('sessionid', blackbox_sessionid_multi_response())

    def setup_track_with_phone(self, number=TEST_PHONE_NUMBER, confirmed=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = True
            track.phone_confirmation_is_confirmed = confirmed
            track.phone_confirmation_phone_number = number.e164

    def setup_track_without_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.has_secure_phone_number = False

    def setup_shakur(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'child_account_register',
                'uid': str(TEST_UID2),
            },
            {
                'name': 'action',
                'value': 'family_add_child',
                'uid': str(TEST_UID2),
            },
            {
                'name': 'alias.portal.add',
                'value': 'login',
                'uid': str(TEST_UID2),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID2),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.birthday',
                'value': TEST_BIRTHDAY,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.content_rating_class',
                'value': str(TEST_CONTENT_RATING_CLASS),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.lang',
                'value': str(TEST_LANGUAGE),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.country',
                'value': str(TEST_LANGUAGE),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.disabled_status',
                'value': str(0),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.ena',
                'value': str(1),
                'uid': str(TEST_UID2),
            },

            {
                'name': 'info.firstname',
                'value': TEST_FIRSTNAME,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.lastname',
                'value': TEST_LASTNAME,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.karma',
                'value': str(0),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.karma_full',
                'value': str(0),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.karma_prefix',
                'value': str(0),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.login',
                'value': TEST_LOGIN,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.password',
                'value': TEST_SERIALIZED_PASSWORD,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.password_update_time',
                'value': TimeNow(),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.reg_date',
                'value': DatetimeNow(convert_to_datetime=True),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.password_quality',
                'value': str(TEST_PASSWORD_QUALITY),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.sex',
                'value': str(TEST_GENDER),
                'uid': str(TEST_UID2),
            },
            {
                'name': 'sid.add',
                'value': '8|' + TEST_LOGIN,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'info.tz',
                'value': 'America/Los_Angeles',
                'uid': str(TEST_UID2),
            },
            {
                'name': 'consumer',
                'value': TEST_CONSUMER,
                'uid': str(TEST_UID2),
            },
            {
                'name': 'user_agent',
                'value': TEST_USER_AGENT,
                'uid': str(TEST_UID2),
            },
        ]
        expected_events += self.base_historydb_events(TEST_UID2)

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_db_written(self):
        self.env.db.check_table_contents('uid', 'passportdbcentral', [{'id': 1}, {'id': 2}])
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': 1,
                'admin_uid': TEST_UID,
                'meta': '',
            },
        ])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': 1,
                'uid': TEST_UID,
                'place': 0,
            },
            {
                'family_id': 1,
                'uid': TEST_UID2,
                'place': 1,
            },
        ])

    def assert_statbox_ok(self, with_check_cookies=False):
        lines = []
        if with_check_cookies:
            lines.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))

        lines.extend([
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'account.disabled_status',
                    'new': 'enabled',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'type': '1',
                    'uid': str(TEST_UID2),
                    'value': 'login',
                    'entity': 'aliases',
                    'operation': 'added',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'account.content_rating_class',
                    'new': '1',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.firstname',
                    'new': 'Elon',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.lastname',
                    'new': 'Musk',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.language',
                    'new': TEST_LANGUAGE,
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.country',
                    'new': TEST_LANGUAGE,
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.gender',
                    'new': 'm',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.birthday',
                    'new': '1971-06-28',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'person.fullname',
                    'new': 'Elon Musk',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'uid': str(TEST_UID2),
                    'entity': 'password.encrypted',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'password.encoding_version',
                    'new': '6',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'entity': 'password.quality',
                    'new': '80',
                    'operation': 'created',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'old': '-',
                    'uid': str(TEST_UID2),
                    'suid': '-',
                    'destination': 'frodo',
                    'entity': 'karma',
                    'registration_datetime': DatetimeNow(convert_to_datetime=True),
                    'action': 'child_account_register',
                    'new': '0',
                    'login': 'login',
                }
            ),
            self.env.statbox.entry(
                'account_modification',
                **{
                    'uid': str(TEST_UID2),
                    'entity': 'subscriptions',
                    'sid': '8', 'timezone': TIMEZONE,
                    'operation': 'added',
                }
            ),
            self.env.statbox.entry(
                tag='account_modification',
                _exclude=['uid'],
                **{
                    'entity_id': str(TEST_UID2),
                    'old': '-',
                    'attribute': 'members.{}.uid'.format(TEST_UID2),
                    'entity': 'members',
                    'family_id': 'f1',
                    'new': str(TEST_UID2),
                    'operation': 'created',
                    'event': 'family_info_modification',
                }
            ),
        ])

        self.env.statbox.assert_has_written(lines)
