# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.api.yasms import exceptions as yasms_exceptions
from passport.backend.core.builders.blackbox import exceptions as blackbox_builder_exceptions
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_json_error_response,
    blackbox_phone_bindings_response,
)
from passport.backend.core.test.time_utils.time_utils import unixtime

from .base import BaseYasmsTestCase


class TestPhoneBindingsHistory(BaseYasmsTestCase):
    def test_empty_history_when_blackbox_returns_empty_list(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        response = self._yasms.phone_bindings_history([
            u'+79010099888',
        ])

        eq_(response, {u'status': u'ok', u'history': []})

    def test_success(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': u'+79010099888',
                    u'bound': datetime(2008, 3, 9, 10, 15, 20),
                    u'uid': 41,
                },
                {
                    u'number': u'+79010099888',
                    u'bound': datetime(2004, 3, 9, 10, 20, 31),
                    u'uid': 33,
                },
                {
                    u'number': u'+79030099888',
                    u'bound': datetime(2003, 2, 11, 20, 10, 0),
                    u'uid': 41,
                },
            ]),
        )

        response = self._yasms.phone_bindings_history([
            u'+79010099888',
            u'+79020099888',
            u'+79030099888',
        ])

        eq_(
            response,
            {
                u'status': u'ok',
                u'history': [
                    {
                        u'uid': 41,
                        u'phone': u'+79030099888',
                        u'ts': unixtime(2003, 2, 11, 20, 10, 0),
                    },
                    {
                        u'uid': 33,
                        u'phone': u'+79010099888',
                        u'ts': unixtime(2004, 3, 9, 10, 20, 31),
                    },
                    {
                        u'uid': 41,
                        u'phone': u'+79010099888',
                        u'ts': unixtime(2008, 3, 9, 10, 15, 20),
                    },
                ],
            },
        )

    def test_non_normalized_phone_number(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'number': u'+79010099888',
                    u'bound': datetime(2007, 2, 4, 12, 5, 1),
                    u'uid': 41,
                },
            ]),
        )

        response = self._yasms.phone_bindings_history([
            u'89010099888',
        ])

        eq_(
            response,
            {
                u'status': u'ok',
                u'history': [{
                    u'uid': 41,
                    u'phone': u'89010099888',
                    u'ts': unixtime(2007, 2, 4, 12, 5, 1),
                }],
            },
        )

    def test_blackbox_args(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self._yasms.phone_bindings_history([
            u'+79010099888',
        ])

        requests = self.env.blackbox.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'method': 'phone_bindings',
            u'type': u'history',
            u'numbers': u'+79010099888',
            u'ignorebindlimit': u'0',
        })

    def test_invalid_phone(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        response = self._yasms.phone_bindings_history([u'+79999999999', u'+792264'])

        eq_(response, {u'status': u'ok', u'history': []})

        requests = self.env.blackbox.requests
        eq_(len(requests), 1)
        requests[0].assert_query_contains({
            u'method': 'phone_bindings',
            u'type': u'history',
            u'numbers': u'+79999999999,+792264',
            u'ignorebindlimit': u'0',
        })

    @raises(yasms_exceptions.YaSmsPhoneNumberValueError)
    def test_invalid_args(self):
        self._yasms.phone_bindings_history([])

    @raises(blackbox_builder_exceptions.BlackboxTemporaryError)
    def test_db_fetch_failed_error_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_json_error_response(u'DB_FETCHFAILED'),
        )
        self._do_request()

    @raises(blackbox_builder_exceptions.BlackboxTemporaryError)
    def test_db_exception_error_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_json_error_response(u'DB_EXCEPTION'),
        )
        self._do_request()

    @raises(blackbox_builder_exceptions.BlackboxUnknownError)
    def test_unknown_error_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_json_error_response(u'UNKNOWN'),
        )
        self._do_request()

    @raises(blackbox_builder_exceptions.BlackboxInvalidResponseError)
    def test_syntax_error(self):
        self.env.blackbox.set_response_value(u'phone_bindings', u'invalid json')
        self._do_request()

    @raises(blackbox_builder_exceptions.AccessDenied)
    def test_access_denied_error_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_json_error_response(u'ACCESS_DENIED'),
        )
        self._do_request()

    @raises(blackbox_builder_exceptions.BlackboxInvalidParamsError)
    def test_invalid_params_error_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_json_error_response(u'INVALID_PARAMS'),
        )
        self._do_request()

    def _do_request(self):
        return self._yasms.phone_bindings_history([
            u'+79010099888',
        ])
