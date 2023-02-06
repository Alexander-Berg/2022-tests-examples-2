# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    FakeBlackbox,
)
from passport.backend.core.test.test_utils import (
    check_url_contains_params,
    check_url_equals,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import unixtime
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.common import merge_dicts

from .test_blackbox import BaseBlackboxTestCase


@with_settings(
    BLACKBOX_URL=u'http://blackb.ox/',
)
class TestBuildRequest(BaseBlackboxTestCase):
    DEFAULT_ARGS = dict(need_current=True, need_history=True, need_unbound=True,
                        phone_numbers=[], phone_ids=[], bound_after_time=0,
                        should_ignore_binding_limit=False)

    def setUp(self):
        super(TestBuildRequest, self).setUp()
        self.faker = FakeBlackbox()
        self.faker.start()
        blackbox = Blackbox()
        self.build_request = blackbox.build_phone_bindings_request

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestBuildRequest, self).tearDown()

    def test_argument_is_not_in_url_when_its_value_is_none(self):
        kwargs = merge_dicts(
            self.DEFAULT_ARGS,
            dict(
                phone_numbers=None,
                phone_ids=None,
                bound_after_time=None,
                should_ignore_binding_limit=None,
            ),
        )
        request = self.build_request(**kwargs)

        check_url_equals(
            request.url,
            'http://blackb.ox/blackbox/?type=all&method=phone_bindings&format=json',
        )

    def test_need_current_only(self):
        kwargs = merge_dicts(self.DEFAULT_ARGS, dict(need_history=False, need_unbound=False))
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'type': u'current'})

    def test_need_history_only(self):
        kwargs = merge_dicts(self.DEFAULT_ARGS, dict(need_current=False, need_unbound=False))
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'type': u'history'})

    def test_need_unbound_only(self):
        kwargs = merge_dicts(self.DEFAULT_ARGS, dict(need_current=False, need_history=False))
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'type': u'all'})

    @raises(ValueError)
    def test_value_error_when_both_need_history_and_need_current_are_false(self):
        kwargs = merge_dicts(
            self.DEFAULT_ARGS,
            dict(need_current=False, need_history=False, need_unbound=False),
        )
        self.build_request(**kwargs)

    def test_comma_separated_lists_are_built(self):
        kwargs = merge_dicts(
            self.DEFAULT_ARGS,
            dict(
                phone_numbers=[u'+79011111111', u'+79022222222'],
                phone_ids=[u'45', u'62'],
            ),
        )
        request = self.build_request(**kwargs)

        check_url_contains_params(
            request.url,
            {u'numbers': u'+79011111111,+79022222222', u'phoneids': u'45,62'},
        )

    def test_bound_after_time_is_specified(self):
        kwargs = merge_dicts(self.DEFAULT_ARGS, dict(bound_after_time=12345))
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'bound_after': u'12345'})

    def test_should_ignore_binding_limit_is_specified(self):
        kwargs = merge_dicts(
            self.DEFAULT_ARGS,
            dict(should_ignore_binding_limit=False),
        )
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'ignorebindlimit': u'0'})

        kwargs = merge_dicts(
            self.DEFAULT_ARGS,
            dict(should_ignore_binding_limit=True),
        )
        request = self.build_request(**kwargs)

        check_url_contains_params(request.url, {u'ignorebindlimit': u'1'})


@with_settings(
    BLACKBOX_URL=u'http://blackb.ox/',
)
class TestPhoneBindings(BaseBlackboxTestCase):
    _good_response = blackbox_phone_bindings_response([
        {
            u'number': u'+79011111111',
            u'phone_id': 101501,
            u'type': u'current',
            u'bound': datetime(2004, 5, 2, 12, 4, 1),
        },
        {
            u'number': u'+79011111111',
            u'phone_id': 101501,
            u'type': u'history',
            u'bound': datetime(2008, 9, 12, 9, 11, 2),
        },
        {
            u'number': u'+79011111111',
            u'phone_id': 101500,
            u'type': u'unbound',
            u'bound': None,
            u'uid': 2,
        },
        {
            u'number': u'+380390000000',
            u'phone_id': 101499,
            u'type': u'history',
            u'bound': datetime(1970, 1, 1, 0, 0, 0),
        },
    ])

    def setUp(self):
        super(TestPhoneBindings, self).setUp()
        self.faker = FakeBlackbox()
        self.faker.start()
        self.blackbox = Blackbox()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        super(TestPhoneBindings, self).tearDown()

    def test_defaults_with_phone_numbers(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        self.faker.requests[0].assert_properties_equal(
            url='http://blackb.ox/blackbox/?numbers=%2B79011111111&method=phone_bindings&type=all&format=json',
        )

    def test_defaults_with_phone_ids(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.blackbox.phone_bindings(phone_ids=[81])

        self.faker.requests[0].assert_properties_equal(
            url='http://blackb.ox/blackbox/?phoneids=81&method=phone_bindings&type=all&format=json',
        )

    def test_empty_list_when_both_phone_number_and_phone_ids_are_empty(self):
        bindings = self.blackbox.phone_bindings(phone_ids=[], phone_numbers=[])

        eq_(bindings, [])

    def test_no_phone_bindings(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(bindings, [])

    def test_no_phone_id(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([{
                u'number': u'+79011111111',
                u'phone_id': None,
            }]),
        )

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(
            bindings,
            [{
                u'type': u'history',
                u'phone_number': PhoneNumber.parse(u'+79011111111'),
                u'phone_id': None,
                u'uid': 1,
                u'binding_time': 12345,
                u'should_ignore_binding_limit': False,
            }],
        )

    def test_phone_id(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([{
                u'number': u'+79011111111',
                u'phone_id': 101501,
            }]),
        )

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(
            bindings,
            [{
                u'type': u'history',
                u'phone_number': PhoneNumber.parse(u'+79011111111'),
                u'phone_id': 101501,
                u'uid': 1,
                u'binding_time': 12345,
                u'should_ignore_binding_limit': False,
            }],
        )

    def test_current_and_history_and_unbound_bindings(self):
        self.faker.set_response_value(u'phone_bindings', self._good_response)

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(
            bindings,
            [
                {
                    u'type': u'current',
                    u'phone_number': PhoneNumber.parse(u'+79011111111'),
                    u'phone_id': 101501,
                    u'uid': 1,
                    u'binding_time': unixtime(2004, 5, 2, 12, 4, 1),
                    u'should_ignore_binding_limit': False,
                },
                {
                    u'type': u'history',
                    u'phone_number': PhoneNumber.parse(u'+79011111111'),
                    u'phone_id': 101501,
                    u'uid': 1,
                    u'binding_time': unixtime(2008, 9, 12, 9, 11, 2),
                    u'should_ignore_binding_limit': False,
                },
                {
                    u'type': u'unbound',
                    u'phone_number': PhoneNumber.parse(u'+79011111111'),
                    u'phone_id': 101500,
                    u'uid': 2,
                    u'binding_time': 0,
                    u'should_ignore_binding_limit': False,
                },
                {
                    u'type': u'history',
                    u'phone_number': PhoneNumber.parse(u'+380390000000', allow_impossible=True),
                    u'phone_id': 101499,
                    u'uid': 1,
                    u'binding_time': unixtime(1970, 1, 1, 0, 0, 0),
                    u'should_ignore_binding_limit': False,
                },
            ],
        )

    def test_binding_limit_ignored_is_true(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([{
                u'number': u'+79011111111',
                u'flags': 1,
            }]),
        )

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(
            bindings,
            [{
                u'type': u'history',
                u'phone_number': PhoneNumber.parse(u'+79011111111'),
                u'phone_id': 1,
                u'uid': 1,
                u'binding_time': 12345,
                u'should_ignore_binding_limit': True,
            }],
        )

    def test_binding_limit_ignored_is_false(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([{
                u'number': u'+79011111111',
                u'flags': 0,
            }]),
        )

        bindings = self.blackbox.phone_bindings(phone_numbers=[u'+79011111111'])

        eq_(
            bindings,
            [{
                u'type': u'history',
                u'phone_number': PhoneNumber.parse(u'+79011111111'),
                u'phone_id': 1,
                u'uid': 1,
                u'binding_time': 12345,
                u'should_ignore_binding_limit': False,
            }],
        )

    def test_url(self):
        self.faker.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.blackbox.phone_bindings(
            phone_numbers=[u'+7901111111', u'+79022222222'],
            phone_ids=[81, 91],
            bound_after_time=12345,
            should_ignore_binding_limit=False,
        )

        self.faker.requests[0].assert_properties_equal(
            url='http://blackb.ox/blackbox/?format=json&phoneids=81%2C91&numbers=%2B7901111111%2C%2B79022222222&bound_after=12345&type=all&method=phone_bindings&ignorebindlimit=0',
        )

    def test_need_current_and_history(self):
        self.faker.set_response_value(u'phone_bindings', self._good_response)

        bindings = self.blackbox.phone_bindings(
            phone_numbers=[u'+79011111111'],
            need_unbound=False,
        )

        eq_(len(bindings), 3)
        eq_(bindings[0][u'type'], u'current')
        eq_(bindings[1][u'type'], u'history')
        eq_(bindings[2][u'type'], u'history')

    def test_need_unbound_and_history(self):
        self.faker.set_response_value(u'phone_bindings', self._good_response)

        bindings = self.blackbox.phone_bindings(
            phone_numbers=[u'+79011111111'],
            need_current=False,
        )

        eq_(len(bindings), 3)
        eq_(bindings[0][u'type'], u'history')
        eq_(bindings[1][u'type'], u'unbound')
        eq_(bindings[2][u'type'], u'history')

    def test_need_unbound_and_current(self):
        self.faker.set_response_value(u'phone_bindings', self._good_response)

        bindings = self.blackbox.phone_bindings(
            phone_numbers=[u'+79011111111'],
            need_history=False,
        )

        eq_(len(bindings), 2)
        eq_(bindings[0][u'type'], u'current')
        eq_(bindings[1][u'type'], u'unbound')
