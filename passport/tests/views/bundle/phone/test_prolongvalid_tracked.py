# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_phone_bound,
    build_phone_secured,
    event_lines_phone_admitted,
)
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.utils.common import merge_dicts

from .base import (
    HEADERS,
    TEST_OTHER_EXIST_PHONE_NUMBER,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_UID,
    TEST_USER_IP,
)


@with_settings_hosts(
    YASMS_URL='http://localhost',
    **mock_counters()
)
class TrackedProlongValidSecureViewTestCase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_bundle': ['base']}))

        self.default_url = '/1/bundle/phone/tracked_prolong_valid_secure/?consumer=dev'

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.setup_track()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_track(self, **kwargs):
        """Эта ручка ожидает трек с некоторыми флажками"""
        params = {
            'uid': TEST_UID,
            'secure_phone_number': TEST_PHONE_NUMBER.e164,
            'has_secure_phone_number': True,
        }
        if kwargs:
            params.update(kwargs)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for param, value in params.items():
                setattr(track, param, value)

    def make_request(self, data, headers=HEADERS):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
        }
        return merge_dicts(base_params, kwargs)

    def setup_account(self, userinfo_args=None):
        userinfo_args = userinfo_args or dict(
            uid=TEST_UID,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        )
        userinfo = blackbox_userinfo_response(**userinfo_args)

        if userinfo_args['uid']:
            self.env.db.serialize(userinfo)

        self.env.blackbox.set_blackbox_response_value('userinfo', userinfo)

    def assert_statbox_ok(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                track_id=self.track_id,
                uid=str(TEST_UID),
                number=TEST_PHONE_NUMBER.masked_format_for_statbox,
                ok='1',
                mode='prolongvalid',
                ip=TEST_USER_IP,
                consumer='dev',
                user_agent='curl',
            ),
        ])

    def assert_response_ok(self, resp):
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'ok',
                'track_id': self.track_id,
                'number': TEST_PHONE_NUMBER_DUMPED,
            },
        )

    def test_no_track_id_error(self):
        resp = self.make_request(self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

    def test_no_secure_number_in_track(self):
        self.setup_account()
        self.setup_track(secure_phone_number='')
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_no_has_secure_number_flag_in_track(self):
        self.setup_account()
        self.setup_track(has_secure_phone_number='')
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_account_not_found_error(self):
        self.setup_account(dict(uid=None))
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['account.not_found'])

    def test_account_disabled_on_deletion_error(self):
        self.setup_account(dict(
            uid=TEST_UID,
            enabled=False,
            attributes={
                'account.is_disabled': '2',
            },
        ))
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_no_secure_number_error(self):
        self.setup_account(dict(
            uid=TEST_UID,
            **build_phone_bound(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER.e164,
            )
        ))
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['phone_secure.not_found'])

    def test_secure_number_changed_error(self):
        self.setup_account(dict(
            uid=TEST_UID,
            **build_phone_secured(
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_OTHER_EXIST_PHONE_NUMBER.e164,
            )
        ))
        resp = self.make_request(self.query_params())
        self.assert_error_response(resp, ['phone_secure.not_found'])

    def test_ok(self):
        self.setup_account()
        resp = self.make_request(self.query_params())
        self.assert_response_ok(resp)

        assert_secure_phone_bound.check_db(self.env.db, TEST_UID, {'id': TEST_PHONE_ID1, 'admitted': DatetimeNow()})

        track = self.track_manager.read(self.track_id)
        ok_(track.is_successful_phone_passed)

        self.env.event_logger.assert_contains(
            event_lines_phone_admitted(
                uid=TEST_UID,
                phone_id=TEST_PHONE_ID1,
                phone_number=TEST_PHONE_NUMBER,
            ),
        )
        self.assert_statbox_ok()

    def test_dberror(self):
        self.setup_account()
        self.env.db.set_side_effect_for_db('passportdbshard1', DBError())

        resp = self.make_request(self.query_params())

        eq_(resp.status_code, 200, resp.data)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'errors': ['backend.database_failed'],
            },
        )
