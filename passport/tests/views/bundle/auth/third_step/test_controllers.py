# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.api.tests.views.bundle.mixins.account import GetAccountBySessionOrTokenMixin
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.models.phones.faker import (
    build_phone_being_bound,
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.consts import (
    TEST_PHONE_NUMBER2,
    TEST_PHONE_NUMBER_FAKE1,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


ASK_ADDITIONAL_DATA_GRANT = 'account.ask_additional_data'
FREEZE_ADDITIONAL_DATA_ASKING_GRANT = 'account.freeze_additional_data_asking'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestAskAdditionalData(GetAccountBySessionOrTokenMixin, EmailTestMixin, BaseBundleTestViews):
    http_method = 'GET'

    default_url = '/1/bundle/auth/additional_data/ask/'
    consumer = 'dev'

    http_headers = {
        'cookie': TEST_USER_COOKIE,
        'host': TEST_HOST,
    }

    mocked_grants = [ASK_ADDITIONAL_DATA_GRANT]

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = {'track_id': self.track_id}

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def set_blackbox_response(self, uid=None, with_password=True,
                              with_not_bound_phone=False,
                              with_bound_phone=False,
                              with_secure_admitted_phone=False,
                              with_secure_not_admitted_phone=False,
                              with_restore_email=False,
                              with_external_unsafe_email=False,
                              with_external_not_confirmed_email=False,
                              with_weak_password=False,
                              with_nonempty_avatar=False, scope=None, **kwargs):

        common_data = {
            'default_avatar_key': '0/0-0',
            'is_avatar_empty': not with_nonempty_avatar,
        }
        if with_password:
            common_data['attributes'] = {
                'password.update_datetime': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'password.encrypted': '1:%s' % TEST_PASSWORD_HASH,
            }
            common_data['dbfields'] = {
                'password_quality.quality.uid': 10 if with_weak_password else 90,
                'password_quality.version.uid': 3,
            }
        phones = []
        if with_not_bound_phone:
            phones.append(
                build_phone_being_bound(
                    TEST_PHONE_ID1,
                    TEST_PHONE_NUMBER.e164,
                    TEST_OPERATION_ID,
                    phone_created=TEST_PHONE_CREATED_DT,
                ),
            )
        if with_bound_phone:
            phones.append(
                build_phone_bound(
                    TEST_PHONE_ID2,
                    TEST_PHONE_NUMBER1.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                ),
            )
        if with_secure_admitted_phone:
            phones.append(
                build_phone_secured(
                    TEST_PHONE_ID3,
                    TEST_PHONE_NUMBER2.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                    phone_secured=TEST_PHONE_CREATED_DT,
                    phone_admitted=datetime.now(),
                ),
            )
        if with_secure_not_admitted_phone:
            phones.append(
                build_phone_secured(
                    TEST_PHONE_ID4,
                    TEST_PHONE_NUMBER_FAKE1.e164,
                    phone_created=TEST_PHONE_CREATED_DT,
                    phone_bound=TEST_PHONE_CREATED_DT,
                    phone_confirmed=TEST_PHONE_CREATED_DT,
                    phone_secured=TEST_PHONE_CREATED_DT,
                    phone_admitted=None,
                ),
            )
        emails = [self.create_native_email(TEST_LOGIN, 'ya.ru')]
        if with_restore_email:
            emails.append(
                self.create_validated_external_email('restore', 'gmail.com'),
            )
        if with_external_unsafe_email:
            emails.append(
                dict(self.create_validated_external_email('unsafe', 'gmail.com'), unsafe=True),
            )
        if with_external_not_confirmed_email:
            emails.append(
                {
                    'rpop': False,
                    'silent': False,
                    'default': False,
                    'native': False,
                    'validated': False,
                    'address': 'not_bound@gmail.com',
                    'born-date': '2000-01-01 00:00:01',
                },
            )
        phones = deep_merge(*phones)
        bb_session_response = blackbox_sessionid_multi_response(
            emails=emails,
            **deep_merge(common_data, phones, kwargs)
        )
        self.env.db.serialize_sessionid(bb_session_response)
        bb_oauth_response = blackbox_oauth_response(
            scope=scope,
            emails=emails,
            **deep_merge(common_data, phones, kwargs)
        )
        if uid:
            bb_session_response = blackbox_sessionid_multi_append_user(
                bb_session_response,
                uid=uid,
                login='appended',
                attributes={
                    'password.update_datetime': TEST_PASSWORD_UPDATE_TIMESTAMP,
                    'password.encrypted': '1:%s' % TEST_PASSWORD_HASH,
                },
            )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            bb_session_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            bb_oauth_response,
        )

    def assert_track_ok(self, state=None, uid=TEST_UID):
        track = self.track_manager.read(self.track_id)
        if state is None:
            ok_(not track.additional_data_asked)
            ok_(not track.uid)
        else:
            eq_(track.uid, str(uid))
            eq_(track.additional_data_asked, state)

    def test_empty_uid_error(self):
        resp = self.make_request(query_args={'uid': ''})
        self.assert_error_response(resp, ['uid.empty'])
        self.assert_track_ok()

    def test_uid_mismatch(self):
        self.set_blackbox_response()
        resp = self.make_request(query_args={'uid': 2})
        self.assert_error_response(resp, ['sessionid.no_uid'])
        self.assert_track_ok()

    def test_with_uid(self):
        state = 'password'
        self.set_blackbox_response(uid=2)
        resp = self.make_request(query_args={'uid': 2})
        self.assert_ok_response(resp, state=state, action='weak', track_id=self.track_id)
        self.assert_track_ok(state, uid=2)

    def test_starting_point(self):
        state = 'password'
        self.set_blackbox_response(with_weak_password=True)
        resp = self.make_request()
        self.assert_ok_response(resp, state=state, action='weak', track_id=self.track_id)
        self.assert_track_ok(state)

    def test_email_empty_ok(self):
        state = 'email'
        self.set_blackbox_response(with_secure_admitted_phone=True)
        resp = self.make_request()
        self.assert_ok_response(resp, state=state, action='add', track_id=self.track_id)
        self.assert_track_ok(state)

    def test_email_after_phone(self):
        state = 'email'
        self.set_blackbox_response(
            attributes={'account.additional_data_asked': 'phone'},
            with_external_unsafe_email=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='restore',
            addresses=['unsafe@gmail.com'],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_no_data_required(self):
        self.set_blackbox_response(
            with_secure_admitted_phone=True,
            with_restore_email=True,
            with_nonempty_avatar=True,
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_freeze_period_not_finished(self):
        self.set_blackbox_response(
            attributes={
                'account.additional_data_ask_next_datetime': datetime_to_integer_unixtime(datetime.now() + timedelta(days=1)),
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_last_phone_and_phone_again(self):
        state = 'phone'
        self.set_blackbox_response(
            attributes={
                'account.additional_data_ask_next_datetime': 1000,
                'account.additional_data_asked': 'phone',
            },
            with_restore_email=True,
            with_secure_not_admitted_phone=True,
            with_nonempty_avatar=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='admit',
            data=[
                {
                    'id': TEST_PHONE_ID4,
                    'number': TEST_PHONE_NUMBER_FAKE1.e164,
                },
            ],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_last_email_and_email_again(self):
        state = 'email'
        self.set_blackbox_response(
            attributes={
                'account.additional_data_asked': 'email',
            },
            with_secure_admitted_phone=True,
            with_external_not_confirmed_email=True,
            with_nonempty_avatar=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='confirm',
            addresses=['not_bound@gmail.com'],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_last_social__no_fail(self):
        state = 'phone'
        self.set_blackbox_response(
            attributes={
                'account.additional_data_asked': 'social',
            },
            with_not_bound_phone=True,
            with_bound_phone=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='secure',
            data=[
                {
                    'id': TEST_PHONE_ID2,
                    'number': TEST_PHONE_NUMBER1.e164,
                },
            ],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_phone_bound(self):
        state = 'phone'
        self.set_blackbox_response(
            with_not_bound_phone=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='confirm',
            data=[
                {
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                },
            ],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_phone_multiple_conditions(self):
        state = 'phone'
        self.set_blackbox_response(
            with_secure_not_admitted_phone=True,
            with_bound_phone=True,
            with_not_bound_phone=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='admit',
            data=[
                {
                    'id': TEST_PHONE_ID4,
                    'number': TEST_PHONE_NUMBER_FAKE1.e164,
                },
            ],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_email_multiple_conditions(self):
        state = 'email'
        self.set_blackbox_response(
            with_secure_admitted_phone=True,
            with_external_not_confirmed_email=True,
            with_external_unsafe_email=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='restore',
            addresses=['unsafe@gmail.com'],
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_avatar_empty(self):
        state = 'avatar'
        self.set_blackbox_response(
            with_secure_admitted_phone=True,
            with_restore_email=True,
            with_nonempty_avatar=False,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state=state,
            action='add',
            track_id=self.track_id,
        )
        self.assert_track_ok(state)

    def test_phone_after_email(self):
        state = 'phone'
        self.set_blackbox_response(
            attributes={
                'account.additional_data_asked': 'email',
            },
            with_nonempty_avatar=True,
        )

        resp = self.make_request()
        self.assert_ok_response(resp, state=state, action='add', track_id=self.track_id)
        self.assert_track_ok(state)

    def test_no_password(self):
        self.set_blackbox_response(with_password=False, with_nonempty_avatar=True)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_uid_in_track_not_match(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_OTHER_UID
        self.set_blackbox_response()
        resp = self.make_request()
        self.assert_error_response(resp, ['account.uid_mismatch'])

    def test_uid_in_track_exists(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
        state = 'phone'
        self.set_blackbox_response()
        resp = self.make_request()
        self.assert_ok_response(resp, state=state, action='add', track_id=self.track_id)
        self.assert_track_ok(state)

    def test_password_weak_ok(self):
        state = 'password'
        self.set_blackbox_response(
            with_secure_admitted_phone=True,
            with_restore_email=True,
            with_nonempty_avatar=True,
            with_weak_password=True,
        )
        resp = self.make_request()
        self.assert_ok_response(resp, state=state, action='weak', track_id=self.track_id)
        self.assert_track_ok(state)

    def test_password_weak_but_pdd_user_cant_change(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                can_users_change_password='0',
                domain=TEST_PDD_DOMAIN,
            ),
        )
        self.set_blackbox_response(
            with_secure_admitted_phone=True,
            with_restore_email=True,
            with_nonempty_avatar=True,
            with_weak_password=True,
            uid=TEST_PDD_UID,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            domain=TEST_PDD_DOMAIN,
            login=TEST_PDD_LOGIN,
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    IS_TEST=True,
    ADDITIONAL_DATA_FREEZE_PERIOD_AFTER_COMPLETION={'short': timedelta(minutes=5), 'long': timedelta(days=1)},
    ADDITIONAL_DATA_FREEZE_PERIOD_AFTER_DECLINE={'short': timedelta(minutes=5), 'long': timedelta(days=1)},
)
class TestFreezeAdditionalDataAsking(GetAccountBySessionOrTokenMixin, BaseBundleTestViews):
    http_method = 'POST'

    default_url = '/1/bundle/auth/additional_data/freeze/'
    consumer = 'dev'
    http_headers = {
        'cookie': TEST_USER_COOKIE,
        'host': TEST_HOST,
    }

    mocked_grants = [FREEZE_ADDITIONAL_DATA_ASKING_GRANT]

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.set_blackbox_response(attributes={'account.additional_data_asked': 'phone'})
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.http_query_args = {'track_id': self.track_id}
        self.state = 'phone'
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.additional_data_asked = self.state

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def set_blackbox_response(self, uid=TEST_UID, login=TEST_LOGIN, attributes=None, **kwargs):
        attributes = attributes or {}
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=uid, login=login, attributes=attributes),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=uid, login=login, attributes=attributes, **kwargs),
        )

    def check_db_ok(self, state, uid=TEST_UID, is_test=False):
        shard = 'passportdbshard1'
        offset = 300 if is_test else 86400
        self.env.db.check(
            'attributes',
            'account.additional_data_asked',
            state,
            uid=uid,
            db=shard,
        )
        self.env.db.check(
            'attributes',
            'account.additional_data_ask_next_datetime',
            TimeNow(offset=offset),
            uid=uid,
            db=shard,
        )

    def check_events_log(self, state, is_test=False):
        dt = datetime.now() + (timedelta(minutes=5) if is_test else timedelta(days=1))
        entries = {
            'action': 'additional_data_asked',
            'info.additional_data_ask_next_datetime': DatetimeNow(timestamp=dt, convert_to_datetime=True),
        }
        if state:
            entries.update({'info.additional_data_asked': state})
        self.assert_events_are_logged(
            self.env.handle_mock,
            entries,
        )

    def test_empty_uid_error(self):
        resp = self.make_request(query_args={'uid': ''})
        self.assert_error_response(resp, ['uid.empty'])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_uid_mismatch(self):
        resp = self.make_request(query_args={'uid': 2})
        self.assert_error_response(resp, ['sessionid.no_uid'])
        self.assert_events_are_empty(self.env.handle_mock)

    def test_with_uid(self):
        self.set_blackbox_response(uid=2, attributes={'account.additional_data_asked': 'social'})
        resp = self.make_request(query_args={'uid': 2})
        self.assert_ok_response(resp)
        self.check_db_ok(state=self.state, uid=2)
        self.check_events_log(self.state)

    def test_track_invalid_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.additional_data_asked = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.env.db.check_missing(
            'attributes',
            'account.additional_data_ask_next_datetime',
            uid=TEST_UID,
            db='passportdbshard1',
        )
        self.env.db.check_missing(
            'attributes',
            'account.additional_data_asked',
            uid=TEST_UID,
            db='passportdbshard1',
        )
        self.assert_events_are_empty(self.env.handle_mock)

    def test_ok(self):
        self.set_blackbox_response(
            attributes={
                'account.additional_data_asked': 'social',
                'account.additional_data_ask_next_datetime': 100,
            },
        )
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(state=self.state)
        self.check_events_log(self.state)

    def test_user_declined(self):
        self.set_blackbox_response(
            attributes={
                'account.additional_data_asked': 'social',
            },
        )
        resp = self.make_request(query_args={'user_declined': 'yes'})
        self.assert_ok_response(resp)
        self.check_db_ok(self.state)
        self.check_events_log(self.state)

    def test_test_login_in_testing(self):
        self.set_blackbox_response(
            login='yndx-test',
            attributes={
                'account.additional_data_asked': 'email',
            },
        )
        resp = self.make_request(query_args={'user_declined': 'yes'})
        self.assert_ok_response(resp)
        self.check_db_ok(self.state, is_test=True)
        self.check_events_log(self.state, is_test=True)

    def test_prod(self):
        self.set_blackbox_response(
            login='yndx-test',
            attributes={
                'account.additional_data_asked': 'email',
                'account.additional_data_ask_next_datetime': 100,
            },
        )
        with settings_context(
            IS_TEST=False,
            ADDITIONAL_DATA_FREEZE_PERIOD_AFTER_COMPLETION={'short': timedelta(minutes=5), 'long': timedelta(days=1)},
            ADDITIONAL_DATA_FREEZE_PERIOD_AFTER_DECLINE={'short': timedelta(minutes=5), 'long': timedelta(days=1)},
        ):
            resp = self.make_request()
            self.assert_ok_response(resp)
            self.check_db_ok(self.state)
            self.check_events_log(self.state)
