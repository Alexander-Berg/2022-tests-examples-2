# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.staff import Staff
from passport.backend.core.builders.staff.exceptions import (
    StaffAuthorizationInvalidError,
    StaffEntityNotFoundError,
    StaffPermanentError,
    StaffTemporaryError,
)
from passport.backend.core.builders.staff.faker.fake_staff import (
    FakeStaff,
    staff_get_department_id_response,
    staff_get_user_info_response,
    staff_paginated_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_OAUTH_TOKEN = 'token'
TEST_DEPARTMENT_URL = 'dep_url'
TEST_DEPARTMENT_ID = 123
TEST_UID = 1
TEST_LOGIN = 'login0test'


@with_settings(
    STAFF_URL='http://localhost/',
    STAFF_TIMEOUT=3,
    STAFF_RETRIES=2,
)
class TestStaffCommon(unittest.TestCase):
    def setUp(self):
        self.staff = Staff()

        self.response = mock.Mock()
        self.staff.useragent.request = mock.Mock()
        self.staff.useragent.request.return_value = self.response
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.staff
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 400
        self.response.content = b'not a json'
        with assert_raises(StaffPermanentError):
            self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL)

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(StaffTemporaryError):
            self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL)

    def test_oauth_token_invalid_error(self):
        self.response.status_code = 401
        self.response.content = b'"token invalid"'
        with assert_raises(StaffAuthorizationInvalidError):
            self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL)

    def test_entity_not_found_error(self):
        self.response.status_code = 404
        self.response.content = b'"not found"'
        with assert_raises(StaffEntityNotFoundError):
            self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL)

    def test_passport_default_initialization(self):
        staff = Staff()
        ok_(staff.useragent is not None)
        eq_(staff.url, 'http://localhost/')


@with_settings(
    STAFF_URL='http://localhost/',
    STAFF_TIMEOUT=3,
    STAFF_RETRIES=2,
)
class TestStaffMethods(unittest.TestCase):
    def setUp(self):
        self.fake_staff = FakeStaff()
        self.fake_staff.start()
        self.staff = Staff()

    def tearDown(self):
        self.fake_staff.stop()
        del self.fake_staff

    def test_get_department_id_ok(self):
        self.fake_staff.set_response_value(
            'get_department_id',
            json.dumps(staff_get_department_id_response(TEST_DEPARTMENT_ID)),
        )
        response = self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL)
        eq_(
            response,
            TEST_DEPARTMENT_ID,
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/persons')
        self.fake_staff.requests[0].assert_query_equals({
            'department_group.url': TEST_DEPARTMENT_URL,
            '_fields': 'department_group.department.id',
            '_one': '1',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_user_info_ok(self):
        self.fake_staff.set_response_value(
            'get_user_info',
            json.dumps(staff_get_user_info_response(uid=TEST_UID)),
        )
        response = self.staff.get_user_info(TEST_OAUTH_TOKEN, TEST_UID)
        eq_(
            response,
            staff_get_user_info_response(uid=TEST_UID),
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/persons')
        self.fake_staff.requests[0].assert_query_equals({
            'uid': str(TEST_UID),
            '_fields': 'uid,login,official.is_robot',
            '_one': '1',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_team_by_url_ok(self):
        self.fake_staff.set_response_value(
            'get_team',
            json.dumps(staff_paginated_response([
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ])),
        )
        response = self.staff.get_team(
            oauth_token=TEST_OAUTH_TOKEN,
            department_url=TEST_DEPARTMENT_URL,
            fields=['uid', 'login'],
        )
        eq_(
            response,
            [
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ],
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/persons')
        self.fake_staff.requests[0].assert_query_equals({
            '_query': 'department_group.url==\'%(url)s\' or department_group.ancestors.url==\'%(url)s\'' % {
                'url': TEST_DEPARTMENT_URL,
            },
            '_fields': 'uid,login',
            '_page': '1',
            'official.is_dismissed': 'false',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_team_by_id_ok(self):
        self.fake_staff.set_response_value(
            'get_team',
            json.dumps(staff_paginated_response([
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ])),
        )
        response = self.staff.get_team(
            oauth_token=TEST_OAUTH_TOKEN,
            department_id=TEST_DEPARTMENT_ID,
            fields=['uid', 'login'],
        )
        eq_(
            response,
            [
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ],
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/persons')
        self.fake_staff.requests[0].assert_query_equals({
            '_query': 'department_group.department.id==%(id)s or department_group.ancestors.department.id==%(id)s' % {
                'id': TEST_DEPARTMENT_ID,
            },
            '_fields': 'uid,login',
            '_page': '1',
            'official.is_dismissed': 'false',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_team_wo_params_error(self):
        self.fake_staff.set_response_value(
            'get_team',
            json.dumps(staff_paginated_response([
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ])),
        )
        with assert_raises(ValueError):
            self.staff.get_team(
                oauth_token=TEST_OAUTH_TOKEN,
                fields=['uid', 'login'],
            )

    def test_get_team_paginated_ok(self):
        self.fake_staff.set_response_side_effect(
            'get_team',
            [
                json.dumps(staff_paginated_response(
                    items=[
                        {'uid': 1, 'login': 'login1'},
                    ],
                    page=1,
                    total_pages=2,
                )).encode('utf-8'),
                json.dumps(staff_paginated_response(
                    items=[
                        {'uid': 2, 'login': 'login2'},
                    ],
                    page=2,
                    total_pages=2,
                )).encode('utf-8'),
            ],
        )
        response = self.staff.get_team(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_ID, fields=['uid', 'login'])
        eq_(
            response,
            [
                {'uid': 1, 'login': 'login1'},
                {'uid': 2, 'login': 'login2'},
            ],
        )
        eq_(len(self.fake_staff.requests), 2)
        self.fake_staff.requests[0].assert_query_contains({
            '_page': '1',
        })
        self.fake_staff.requests[1].assert_query_contains({
            '_page': '2',
        })

    def test_get_team_paginated_page_limit(self):
        self.fake_staff.set_response_side_effect(
            'get_team',
            [
                json.dumps(staff_paginated_response(
                    items=[
                        {'uid': 1, 'login': 'login1'},
                    ],
                    page=1,
                    total_pages=2,
                )).encode('utf-8'),
                json.dumps(staff_paginated_response(
                    items=[
                        {'uid': 2, 'login': 'login2'},
                    ],
                    page=2,
                    total_pages=2,
                )).encode('utf-8'),
            ],
        )
        response = self.staff.get_team(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_ID, fields=['uid', 'login'], max_pages=1)
        eq_(
            response,
            [
                {'uid': 1, 'login': 'login1'},
            ],
        )
        eq_(len(self.fake_staff.requests), 1)

    def test_get_user_groups_ok(self):
        self.fake_staff.set_response_value(
            'get_user_groups',
            json.dumps(staff_paginated_response([
                {
                    'group': {
                        'url': 'yandex_search_tech_searchinfradev',
                        'ancestors': [
                            {'url': 'yandex'},
                            {'url': 'yandex_main'},
                            {'url': 'yandex_main_searchadv'},
                            {'url': 'yandex_rkub_portal'},
                        ],
                    },
                },
            ])),
        )
        response = self.staff.get_user_groups(
            oauth_token=TEST_OAUTH_TOKEN,
            login=TEST_LOGIN,
        )
        eq_(
            response,
            [
                {
                    'group': {
                        'url': 'yandex_search_tech_searchinfradev',
                        'ancestors': [
                            {'url': 'yandex'},
                            {'url': 'yandex_main'},
                            {'url': 'yandex_main_searchadv'},
                            {'url': 'yandex_rkub_portal'},
                        ],
                    },
                },
            ],
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/groupmembership')
        self.fake_staff.requests[0].assert_query_equals({
            'person.login': TEST_LOGIN,
            '_fields': 'group.url,group.ancestors.url',
            '_page': '1',
            'group.type': 'department',
            'group.ancestors.type': 'department',
            'group.is_deleted': 'false',
            'group.ancestors.is_deleted': 'false',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })

    def test_get_user_groups_with_ids_ok(self):
        self.fake_staff.set_response_value(
            'get_user_groups',
            json.dumps(staff_paginated_response([
                {
                    'group': {
                        'url': 'yandex_search_tech_searchinfradev',
                        'ancestors': [
                            {'id': 962},
                            {'id': 62126},
                            {'id': 62131},
                            {'id': 42149},
                        ],
                        'id': 47,
                    },
                },
            ])),
        )
        response = self.staff.get_user_groups(
            oauth_token=TEST_OAUTH_TOKEN,
            login=TEST_LOGIN,
            fields=['group.url', 'group.id', 'group.ancestors.id'],
        )
        eq_(
            response,
            [
                {
                    'group': {
                        'url': 'yandex_search_tech_searchinfradev',
                        'ancestors': [
                            {'id': 962},
                            {'id': 62126},
                            {'id': 62131},
                            {'id': 42149},
                        ],
                        'id': 47,
                    },
                },
            ],
        )
        eq_(len(self.fake_staff.requests), 1)
        self.fake_staff.requests[0].assert_url_starts_with('http://localhost/v3/groupmembership')
        self.fake_staff.requests[0].assert_query_equals({
            'person.login': TEST_LOGIN,
            '_fields': 'group.url,group.id,group.ancestors.id',
            '_page': '1',
            'group.type': 'department',
            'group.ancestors.type': 'department',
            'group.is_deleted': 'false',
            'group.ancestors.is_deleted': 'false',
        })
        self.fake_staff.requests[0].assert_headers_contain({
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        })
