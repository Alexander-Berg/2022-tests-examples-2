# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import ProlongValidView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_prolong_valid_response
from passport.backend.core.models.phones.faker import (
    assert_simple_phone_bound,
    build_phone_bound,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
)


PHONE_ID_ALPHA = 3232
PHONE_NUMBER_ALPHA = u'+79010000001'
PHONE_NUMBER_BETA = u'+79020000002'
UID = 4814
TEST_DATE = datetime(2005, 6, 1, 0, 15, 0)


@nottest
class BaseProlongValidViewTestCase(BaseTestCase):
    def test_no_number_error_when_number_is_empty(self):
        self.assign_all_grants()

        self.make_request(number=None)
        self.assert_response_is_error(u'NONUMBER', u'NONUMBER')

        self.make_request(number=u'')
        self.assert_response_is_error(u'NONUMBER', u'NONUMBER')

    def test_dont_know_you_error_when_invalid_sender_and_invalid_number(self):
        self.assert_dont_know_you_error_when_invalid_sender_and_invalid_phone(u'number')

    def test_no_rights_error_when_sender_misses_rights_and_invalid_number(self):
        self.assert_no_rights_error_when_sender_misses_rights_and_invalid_phone(u'number')

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(ProlongValidView)

    def make_request(self, sender=u'dev', number=PHONE_NUMBER_ALPHA, uid=UID,
                     headers=None):
        self.response = self.env.client.get(
            u'/yasms/api/prolongvalid',
            query_string={u'sender': sender, u'number': number, u'uid': uid},
            headers=headers,
        )
        return self.response

    def assert_response_is_error(self, message, code, encoding=u'utf-8'):
        self.assert_response_is_json_error(code)


@with_settings_hosts
@istest
class TestProlongValidView(BaseProlongValidViewTestCase,
                           BlackboxCommonTestCase,
                           RequiredSenderWhenGrantsAreRequiredTestMixin,
                           RequiredUidWhenGrantsAreRequiredTestMixin):
    def test_status_ok(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(PHONE_ID_ALPHA, PHONE_NUMBER_ALPHA)
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_prolong_valid_response(uid=UID, status=u'OK'),
        )

    def test_write_event_log(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(PHONE_ID_ALPHA, PHONE_NUMBER_ALPHA)
            ),
        )

        self.make_request(sender=u'dev')

        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                u'action': 'prolong_valid',
                u'consumer': u'dev',
                u'phone.%d.number' % PHONE_ID_ALPHA: PHONE_NUMBER_ALPHA,
                u'phone.%d.admitted' % PHONE_ID_ALPHA: TimeNow(),
                u'phone.%d.action' % PHONE_ID_ALPHA: 'changed',
            },
        )

    def test_write_db(self):
        self.assign_grants([grants.PROLONG_VALID])
        user_info = blackbox_userinfo_response(
            uid=UID,
            **build_phone_bound(
                PHONE_ID_ALPHA,
                PHONE_NUMBER_ALPHA,
            )
        )
        self.env.blackbox.set_response_value(u'userinfo', user_info)
        self.env.db.serialize(user_info)

        self.make_request()

        assert_simple_phone_bound.check_db(
            self.env.db,
            UID,
            {
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'admitted': DatetimeNow(),
            },
        )

    def test_dont_write_statbox_log(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

        self.make_request()

        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_account_not_found(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request()

        self.assert_json_responses_equal(
            response,
            yasms_prolong_valid_response(uid=UID, status=u'NOPHONE'),
        )

    def test_no_phone_on_account(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

        response = self.make_request(number=PHONE_NUMBER_BETA)

        self.assert_json_responses_equal(
            response,
            yasms_prolong_valid_response(uid=UID, status=u'NOPHONE'),
        )

    def test_dont_write_db_when_no_phone_on_account(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

        self.make_request(number=PHONE_NUMBER_BETA)

        eq_(self.env.db.query_count(u'passportdbshard1'), 0)

    def test_dont_write_event_log_when_no_phone_on_account(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

        self.make_request(number=PHONE_NUMBER_BETA)

        self.assert_events_are_empty(self.env.handle_mock)

    def test_dont_write_statbox_log_when_no_phone_on_account(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

        self.make_request(number=PHONE_NUMBER_BETA)

        self.check_statbox_log_entries(self.env.statbox_handle_mock, [])

    def test_not_normalized_phone_number(self):
        self.assign_grants([grants.PROLONG_VALID])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    phone_id=PHONE_ID_ALPHA,
                    phone_number=u'+79010011000',
                    is_default=True,
                )
            ),
        )

        response = self.make_request(number=u'89010011000')

        eq_(response.status_code, 200)
        self.assert_json_responses_equal(
            response,
            yasms_prolong_valid_response(uid=UID, status=u'OK'),
        )

    def test_invalid_number(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        response = self.make_request(number=u'02')

        self.assert_json_responses_equal(
            response,
            yasms_prolong_valid_response(uid=UID, status=u'NOPHONE'),
        )

    def setup_blackbox_to_serve_good_response(self):
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                **build_phone_bound(
                    PHONE_ID_ALPHA,
                    PHONE_NUMBER_ALPHA,
                    is_default=True,
                )
            ),
        )

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        self.assert_json_responses_equal(
            self.response,
            yasms_prolong_valid_response(uid=UID, status=u'OK'),
        )
