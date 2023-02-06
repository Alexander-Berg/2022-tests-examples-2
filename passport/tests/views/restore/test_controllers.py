# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.adm_api.test.mock_objects import (
    mock_grants,
    mock_headers,
)
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import (
    BaseViewTestCase,
    ViewsTestEnvironment,
)
from passport.backend.adm_api.tests.views.restore.data import *
from passport.backend.adm_api.views.base import ADM_API_OAUTH_SCOPE
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    event_restore_item,
    events_response,
    events_restore_response,
)
from passport.backend.core.builders.passport.exceptions import PassportPermanentError
from passport.backend.core.builders.passport.faker.fake_passport import (
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.core.historydb.events import *
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.types.restore_id import RestoreId


@with_settings_hosts()
class RestoreAttemptExistsViewTestCase(BaseViewTestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[event_restore_item(restore_id=TEST_RESTORE_ID)]),
        )
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response())
        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

    def make_request(self, restore_id=TEST_RESTORE_ID, headers=None):
        query = dict(restore_id=restore_id)
        return self.env.client.get(
            '/1/restore/attempt/exists/',
            query_string=query,
            headers=headers,
        )

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP, authorization=TEST_AUTHORIZATION):
        return mock_headers(cookie=cookie, host=host, user_ip=ip, authorization=authorization)

    def test_no_headers(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2)
        self.check_response_error(resp, ['ip.empty', 'authorization.empty'])

    def test_no_grants(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(login='looser', scope=ADM_API_OAUTH_SCOPE))
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['access.denied'])

    def test_attempt_not_found(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(login='admin', scope=ADM_API_OAUTH_SCOPE))
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_ok(resp, restore_attempt_exists=False)

    def test_historydb_fail(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(login='admin', scope=ADM_API_OAUTH_SCOPE))
        self.env.historydb_api.set_response_side_effect('events_restore', HistoryDBApiTemporaryError)
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])

    def test_attempt_exists(self):
        self.env.blackbox.set_response_value('oauth', blackbox_oauth_response(login='admin', scope=ADM_API_OAUTH_SCOPE))
        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, restore_attempt_exists=True)


@with_settings_hosts()
class RestoreAttemptsViewTestCase(BaseViewTestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.historydb_api.set_response_value('events', events_response(events=[]))
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response())
        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

    def make_request(self, restore_id=TEST_RESTORE_ID, uid=None, headers=None):
        if uid is None:
            query = dict(restore_id=restore_id)
        else:
            query = dict(uid=uid)
        return self.env.client.get(
            '/1/restore/attempts/',
            query_string=query,
            headers=headers,
        )

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP):
        return mock_headers(cookie=cookie, host=host, user_ip=ip)

    def test_no_headers(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2)
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])

    def test_no_grants(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['access.denied'])

    def test_no_attempts_found(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_ok(resp, restore_attempts=[])

    def test_historydb_fail(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.historydb_api.set_response_side_effect('events', HistoryDBApiTemporaryError)
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])

    def test_attempts_found(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))

        historydb_response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value=TEST_RESTORE_ID_2,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_REQUEST_SOURCE,
                timestamp=2,
                value='changepass',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_PENDING,
            ),
        ]
        self.env.historydb_api.set_response_value('events', events_response(events=historydb_response))

        resp = self.make_request(uid=TEST_UID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            restore_attempts=[
                {
                    u'timestamp': 1,
                    u'datetime': DATETIME_FOR_TS_1,
                    u'request_source': u'restore',
                    u'restore_id': TEST_RESTORE_ID,
                    u'initial_status': RESTORE_STATUS_REJECTED,
                    u'support_decisions': [],
                },
                {
                    u'timestamp': 2,
                    u'datetime': DATETIME_FOR_TS_2,
                    u'request_source': u'changepass',
                    u'restore_id': TEST_RESTORE_ID_2,
                    u'initial_status': RESTORE_STATUS_PENDING,
                    u'support_decisions': [],
                },
            ],
        )

    def test_attempts_with_support_decision(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))

        historydb_response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value=TEST_RESTORE_ID,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_PASSED,
            ),
        ]
        self.env.historydb_api.set_response_value('events', events_response(events=historydb_response))

        resp = self.make_request(uid=TEST_UID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            restore_attempts=[
                {
                    u'timestamp': 1,
                    u'datetime': DATETIME_FOR_TS_1,
                    u'request_source': u'restore',
                    u'restore_id': TEST_RESTORE_ID,
                    u'initial_status': RESTORE_STATUS_REJECTED,
                    u'support_decisions': [
                        {
                            u'timestamp': 2,
                            u'datetime': DATETIME_FOR_TS_2,
                            u'admin': u'support',
                            u'status': RESTORE_STATUS_PASSED,
                        },
                    ],
                },
            ],
        )


@with_settings_hosts()
class RestoreSupportDecisionViewTestCase(BaseViewTestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.historydb_api.set_response_value('events', events_response())
        self.base_restore_data = deepcopy(TEST_FACTORS_DATA_VERSION_MULTISTEP_42)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_response(uid=TEST_SUPPORT_UID, login='admin'),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, login=TEST_USER_LOGIN),
        )
        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

    def make_request(self, restore_id=TEST_RESTORE_ID, passed=False, regenerate_link=False, headers=None):
        query = dict(restore_id=restore_id, passed=passed)
        if regenerate_link is not None:
            query['regenerate_link'] = regenerate_link
        return self.env.client.post(
            '/1/restore/support_decision/',
            data=query,
            headers=headers,
        )

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP, authorization=TEST_AUTHORIZATION):
        return mock_headers(cookie=cookie, host=host, user_ip=ip, authorization=authorization)

    def assert_statbox_entries_written(self, restore_id=TEST_RESTORE_ID, login=TEST_USER_LOGIN,
                                       support_uid=TEST_SUPPORT_UID, support_login='admin', decision_taken=True,
                                       decision=RESTORE_STATUS_PASSED, link_generated=True, is_decision_changed=False,
                                       is_for_learning=False):
        restore_id = RestoreId.from_string(restore_id)
        context = {
            u'tskv_format': u'passport-adminka-log',
            u'host': TEST_HOST,
            u'ip': TEST_IP,
            u'restore_id': TEST_RESTORE_ID_2,
            u'support_uid': str(TEST_SUPPORT_UID),
            u'support_login': support_login,
            u'track_id': restore_id.track_id,
            u'uid': str(restore_id.uid),
            u'login': TEST_USER_LOGIN,
            u'user_agent': 'curl',
        }
        entries = []
        if link_generated:
            entries.append(
                self.env.adm_statbox_logger.entry(
                    'base',
                    action=u'restoration_link_generated',
                    **context
                )
            )
        if decision_taken:
            entries.append(
                self.env.adm_statbox_logger.entry(
                    'base',
                    action=u'restore_decision_taken',
                    decision=decision,
                    is_decision_changed=tskv_bool(is_decision_changed),
                    is_for_learning=tskv_bool(is_for_learning),
                    **context
                ),
            )
        self.env.adm_statbox_logger.assert_has_written(entries)

    def test_no_headers(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2)
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_no_grants(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response())
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['access.denied'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_restore_id_not_found_in_event_log(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_3, headers=self.get_headers())
        self.check_response_error(resp, ['restore_id.not_found'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_restore_id_not_found_in_restore_log(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['restore_id.not_found'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_restore_id_invalid_version(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(dict(self.base_restore_data, version='invalid')),
                ),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['restore_id.unknown_version'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_historydb_fail(self):
        self.env.historydb_api.set_response_side_effect('events', HistoryDBApiTemporaryError)
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_initially_rejected(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_REJECTED),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_already_has_decision(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])

    def test_blackbox_userinfo_fail(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_error(resp, ['backend.blackbox_failed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_deleted_account_fails(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_error(resp, ['account.not_found'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_create_restoration_link_unavailable(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.passport.set_response_side_effect(
            'create_restoration_link',
            PassportPermanentError,
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_error(resp, ['backend.passport_permanent_error'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 1)

    def test_create_restoration_link_fails_with_error(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_bundle_api_error_response('account.invalid_type'),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_error(resp, ['account.invalid_type'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 1)

    def test_create_restoration_link_fails_with_state(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_ok_response(state='complete_pdd'),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_error(resp, ['complete_pdd'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 1)

    def test_decision_passed_applied(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_ok_response(secret_link=TEST_RESTORATION_LINK),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_ok(resp, restoration_link=TEST_RESTORATION_LINK)
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            {
                EVENT_ACTION: ACTION_RESTORE_SEMI_AUTO_DECISION,
                EVENT_INFO_RESTORE_ID: TEST_RESTORE_ID_2,
                EVENT_INFO_RESTORE_STATUS: RESTORE_STATUS_PASSED,
                'admin': 'admin',
            },
        )
        self.assert_statbox_entries_written(restore_id=TEST_RESTORE_ID_2)
        eq_(len(self.env.passport.requests), 1)

    def test_decision_rejected_applied(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value='directurl'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=False, headers=self.get_headers())

        self.check_response_ok(resp, restoration_link=None)
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            {
                EVENT_ACTION: ACTION_RESTORE_SEMI_AUTO_DECISION,
                EVENT_INFO_RESTORE_ID: TEST_RESTORE_ID_2,
                EVENT_INFO_RESTORE_STATUS: RESTORE_STATUS_REJECTED,
                'admin': 'admin',
            },
        )
        self.assert_statbox_entries_written(
            restore_id=TEST_RESTORE_ID_2,
            decision=RESTORE_STATUS_REJECTED,
            link_generated=False,
        )
        eq_(len(self.env.passport.requests), 0)

    def test_regenerate_link_with_positive_decision_works(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_ok_response(secret_link=TEST_RESTORATION_LINK),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp, restoration_link=TEST_RESTORATION_LINK)
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.assert_statbox_entries_written(decision_taken=False, restore_id=TEST_RESTORE_ID_2)
        eq_(len(self.env.passport.requests), 1)

    def test_regenerate_link_with_changed_positive_decision_works(self):
        """Решение по анкете изменено с отрицательного на положительное, возможна перегенерация ссылки"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_REJECTED),
                event_item(name=EVENT_ACTION, timestamp=4, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=4, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=4, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_ok_response(secret_link=TEST_RESTORATION_LINK),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp, restoration_link=TEST_RESTORATION_LINK)
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.assert_statbox_entries_written(decision_taken=False, restore_id=TEST_RESTORE_ID_2)
        eq_(len(self.env.passport.requests), 1)

    def test_regenerate_link_with_negative_decision_does_not_work(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_REJECTED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_regenerate_link_without_decision_does_not_work(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_regenerate_link_not_passed_decision_does_not_work(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=False,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_decision_changing_works(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_REJECTED),
            ]),
        )
        self.env.passport.set_response_value(
            'create_restoration_link',
            passport_ok_response(secret_link=TEST_RESTORATION_LINK),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp, restoration_link=TEST_RESTORATION_LINK)
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            {
                EVENT_ACTION: ACTION_RESTORE_SEMI_AUTO_DECISION,
                EVENT_INFO_RESTORE_ID: TEST_RESTORE_ID_2,
                EVENT_INFO_RESTORE_STATUS: RESTORE_STATUS_PASSED,
                'admin': 'admin',
            },
        )
        self.assert_statbox_entries_written(
            restore_id=TEST_RESTORE_ID_2,
            decision=RESTORE_STATUS_PASSED,
            is_decision_changed=True,
            link_generated=True,
        )
        eq_(len(self.env.passport.requests), 1)

    def test_regenerate_link_with_decision_changing_does_not_work(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_REJECTED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=True,
            regenerate_link=True,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_decision_changing_with_negative_decision_does_not_works(self):
        """Нельзя изменить решение с положительного на отрицательное"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=2, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=2, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=2, value='changepass'),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=2, value=RESTORE_STATUS_PENDING),
                event_item(name=EVENT_ACTION, timestamp=3, value=ACTION_RESTORE_SEMI_AUTO_DECISION, admin='support'),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=3, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=3, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(self.base_restore_data),
                ),
            ]),
        )

        resp = self.make_request(
            restore_id=TEST_RESTORE_ID_2,
            passed=False,
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['action.not_allowed'])
        self.assert_events_are_empty(self.env.event_handle_mock)
        self.env.adm_statbox_logger.assert_has_written([])
        eq_(len(self.env.passport.requests), 0)

    def test_positive_decision_for_learning_works(self):
        """При обучении только записываем решение в Статбокс"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value=TEST_REQUEST_SOURCE),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(dict(self.base_restore_data, is_for_learning=True)),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_ok(resp)
        self.assert_events_are_empty(self.env._event_logger)
        self.assert_statbox_entries_written(
            restore_id=TEST_RESTORE_ID_2,
            link_generated=False,
            is_for_learning=True,
        )
        eq_(len(self.env.passport.requests), 0)

    def test_negative_decision_for_learning_works(self):
        """При обучении только записываем решение в Статбокс"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value=TEST_REQUEST_SOURCE),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PENDING),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(dict(self.base_restore_data, is_for_learning=True)),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=False, headers=self.get_headers())

        self.check_response_ok(resp)
        self.assert_events_are_empty(self.env._event_logger)
        self.assert_statbox_entries_written(
            restore_id=TEST_RESTORE_ID_2,
            link_generated=False,
            decision=RESTORE_STATUS_REJECTED,
            is_for_learning=True,
        )
        eq_(len(self.env.passport.requests), 0)

    def test_can_write_decision_for_learning_with_auto_decision_present(self):
        """При обучении можно записать решение при наличии автоматического решения"""
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(name=EVENT_ACTION, timestamp=1, value=ACTION_RESTORE_SEMI_AUTO_REQUEST),
                event_item(name=EVENT_INFO_RESTORE_ID, timestamp=1, value=TEST_RESTORE_ID_2),
                event_item(name=EVENT_INFO_RESTORE_REQUEST_SOURCE, timestamp=1, value=TEST_REQUEST_SOURCE),
                event_item(name=EVENT_INFO_RESTORE_STATUS, timestamp=1, value=RESTORE_STATUS_PASSED),
            ]),
        )
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                event_restore_item(
                    restore_id=TEST_RESTORE_ID_2,
                    data_json=json.dumps(
                        dict(
                            self.base_restore_data,
                            is_for_learning=True,
                            restore_status=RESTORE_STATUS_PASSED,
                        ),
                    ),
                ),
            ]),
        )
        restore_id = RestoreId.from_string(TEST_RESTORE_ID_2)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=restore_id.uid, login=TEST_USER_LOGIN),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, passed=True, headers=self.get_headers())

        self.check_response_ok(resp)
        self.assert_events_are_empty(self.env._event_logger)
        self.assert_statbox_entries_written(
            restore_id=TEST_RESTORE_ID_2,
            link_generated=False,
            is_for_learning=True,
        )
        eq_(len(self.env.passport.requests), 0)
