# -*- coding: utf-8 -*-
import time

import jwt
import mock
from nose.tools import eq_
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.common.jwt import make_jwt
from passport.backend.oauth.core.test.base_test_data import (
    TEST_FAKE_UUID,
    TEST_HOST,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


TEST_SECRET = 'secret'


class TestJwt(BaseTestCase):
    def setUp(self):
        super(TestJwt, self).setUp()
        self.uuid_patch = mock.patch('uuid.uuid1', mock.Mock(return_value=TEST_FAKE_UUID))
        self.uuid_patch.start()

    def tearDown(self):
        self.uuid_patch.stop()
        super(TestJwt, self).tearDown()

    def test_minimal_ok(self):
        jwt_token = make_jwt(
            TEST_SECRET,
            expires=int(time.time()) + 60,
            issuer=TEST_HOST,
        )
        eq_(
            jwt.decode(jwt_token, TEST_SECRET, algorithms=['HS256']),
            {
                'iat': TimeNow(),
                'jti': TEST_FAKE_UUID,
                'exp': TimeNow(offset=60),
                'iss': TEST_HOST,
            },
        )

    def test_custom_ok(self):
        jwt_token = make_jwt(
            TEST_SECRET,
            expires=int(time.time()) + 60,
            issuer=TEST_HOST,
            custom_fields={'field': 'value'},
        )
        eq_(
            jwt.decode(jwt_token, TEST_SECRET, algorithms=['HS256']),
            {
                'iat': TimeNow(),
                'jti': TEST_FAKE_UUID,
                'exp': TimeNow(offset=60),
                'iss': TEST_HOST,
                'field': 'value',
            },
        )
