# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.staff import Staff
from passport.backend.core.builders.staff.faker.fake_staff import (
    FakeStaff,
    staff_get_department_id_response,
    staff_get_user_info_response,
    staff_paginated_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_OAUTH_TOKEN = 'token'
TEST_DEPARTMENT_ID = 1
TEST_DEPARTMENT_URL = 'dep-url'
TEST_UID = 2
TEST_LOGIN = 'login0test'


@with_settings(
    STAFF_URL='http://localhost/',
    STAFF_RETRIES=2,
    STAFF_TIMEOUT=3,
)
class FakeStaffTestCase(TestCase):
    def setUp(self):
        self.faker = FakeStaff()
        self.faker.start()
        self.staff = Staff()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_get_department_id(self):
        self.faker.set_response_value(
            'get_department_id',
            json.dumps(staff_get_department_id_response(TEST_DEPARTMENT_ID)),
        )
        eq_(
            self.staff.get_department_id(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_URL),
            TEST_DEPARTMENT_ID,
        )

    def test_get_user_info(self):
        self.faker.set_response_value(
            'get_user_info',
            json.dumps(staff_get_user_info_response(uid=TEST_UID)),
        )
        eq_(
            self.staff.get_user_info(TEST_OAUTH_TOKEN, TEST_UID),
            staff_get_user_info_response(uid=TEST_UID),
        )

    def test_get_team(self):
        self.faker.set_response_value(
            'get_team',
            json.dumps(staff_paginated_response([])),
        )
        eq_(
            self.staff.get_team(TEST_OAUTH_TOKEN, TEST_DEPARTMENT_ID),
            [],
        )

    def test_get_user_groups(self):
        self.faker.set_response_value(
            'get_user_groups',
            json.dumps(staff_paginated_response([])),
        )
        eq_(
            self.staff.get_user_groups(TEST_OAUTH_TOKEN, TEST_LOGIN),
            [],
        )
