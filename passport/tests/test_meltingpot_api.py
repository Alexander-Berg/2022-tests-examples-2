# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.meltingpot_api import (
    BaseMeltingpotApiError,
    MeltingpotApi,
    MeltingpotApiInvalidResponseError,
)
from passport.backend.core.builders.meltingpot_api.faker.fake_meltingpot_api import (
    FakeMeltingpotApi,
    meltingpot_error_database_response,
    meltingpot_exception_unhandled,
    meltingpot_ok_add_user_many_response,
    meltingpot_ok_add_user_response,
    meltingpot_ok_response,
    meltingtpot_users_history_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_UID2 = 2
TEST_REASON = 'reason'
TEST_PRIORITY = 5
TEST_MELTINGPOT_API_CONSUMER = 'dev'
TEST_GROUP_ID = 1


@with_settings(
    MELTINGPOT_API_URL='http://meltingpot_api/',
    MELTINGPOT_API_RETRIES=2,
    MELTINGPOT_API_TIMEOUT=1,
    MELTINGPOT_API_CONSUMER=TEST_MELTINGPOT_API_CONSUMER,
)
class BaseMeltingpotTest(unittest.TestCase):
    def setUp(self):
        self.fake_meltingpot = FakeMeltingpotApi()
        self.fake_meltingpot.start()
        self.meltingpot = MeltingpotApi()

    def tearDown(self):
        self.fake_meltingpot.stop()
        del self.fake_meltingpot


class TestAddUserMeltingpotApi(BaseMeltingpotTest):

    def test_ok(self):
        self.fake_meltingpot.set_response_value_without_method(json.dumps(meltingpot_ok_add_user_response()))
        response = self.meltingpot.add_user(
            uid=TEST_UID,
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
        )
        eq_(response, meltingpot_ok_add_user_response())
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='POST',
            url='http://meltingpot_api/1/users/?consumer={}'.format(TEST_MELTINGPOT_API_CONSUMER),
            post_args={
                'uid': TEST_UID,
                'reason': TEST_REASON,
                'priority': TEST_PRIORITY,
            },
        )

    def test_ok_with_group_id(self):
        self.fake_meltingpot.set_response_value_without_method(json.dumps(meltingpot_ok_add_user_response()))
        response = self.meltingpot.add_user(
            uid=TEST_UID,
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )
        eq_(response, meltingpot_ok_add_user_response())
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='POST',
            url='http://meltingpot_api/1/users/?consumer={}'.format(TEST_MELTINGPOT_API_CONSUMER),
            post_args={
                'uid': TEST_UID,
                'reason': TEST_REASON,
                'priority': TEST_PRIORITY,
                'group_id': TEST_GROUP_ID,
            },
        )

    @raises(BaseMeltingpotApiError)
    def test_ok_meltingpot_error(self):
        self.fake_meltingpot.set_meltingpot_response_value(json.dumps(meltingpot_error_database_response()))
        self.meltingpot.add_user(
            uid=TEST_UID,
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )

    @raises(MeltingpotApiInvalidResponseError)
    def test_error(self):
        self.fake_meltingpot.set_meltingpot_response_side_effect(MeltingpotApiInvalidResponseError)
        self.meltingpot.add_user(
            uid=TEST_UID,
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )


class TestAddUsersManyMeltingpotApi(BaseMeltingpotTest):
    response_ok = meltingpot_ok_add_user_many_response([TEST_UID, TEST_UID2])

    def test_ok(self):
        self.fake_meltingpot.set_response_value_without_method(json.dumps(self.response_ok))
        response = self.meltingpot.add_users_many(
            uids=[TEST_UID, TEST_UID2],
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
        )
        eq_(response, self.response_ok)
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='POST',
            url='http://meltingpot_api/1/users/many/?consumer={}'.format(TEST_MELTINGPOT_API_CONSUMER),
            post_args={
                'uids': ','.join(map(str, [TEST_UID, TEST_UID2])),
                'reason': TEST_REASON,
                'priority': TEST_PRIORITY,
            },
        )

    def test_ok_with_group_id(self):
        self.fake_meltingpot.set_response_value_without_method(json.dumps(self.response_ok))
        response = self.meltingpot.add_users_many(
            uids=[TEST_UID, TEST_UID2],
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )
        eq_(response, self.response_ok)
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='POST',
            url='http://meltingpot_api/1/users/many/?consumer={}'.format(TEST_MELTINGPOT_API_CONSUMER),
            post_args={
                'uids': ','.join(map(str, [TEST_UID, TEST_UID2])),
                'reason': TEST_REASON,
                'priority': TEST_PRIORITY,
                'group_id': TEST_GROUP_ID,
            },
        )

    @raises(BaseMeltingpotApiError)
    def test_ok_meltingpot_error(self):
        self.fake_meltingpot.set_meltingpot_response_value(json.dumps(meltingpot_error_database_response()))
        self.meltingpot.add_users_many(
            uids=[TEST_UID, TEST_UID2],
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )

    @raises(MeltingpotApiInvalidResponseError)
    def test_error(self):
        self.fake_meltingpot.set_meltingpot_response_side_effect(MeltingpotApiInvalidResponseError)
        self.meltingpot.add_users_many(
            uids=[TEST_UID, TEST_UID2],
            reason=TEST_REASON,
            priority=TEST_PRIORITY,
            group_id=TEST_GROUP_ID,
        )


class TestProxyMeltingpotApi(BaseMeltingpotTest):
    def setUp(self):
        self.fake_meltingpot = FakeMeltingpotApi()
        self.fake_meltingpot.start()
        self.meltingpot = MeltingpotApi()

    def tearDown(self):
        self.fake_meltingpot.stop()
        del self.fake_meltingpot

    def test_ok_get(self):
        self.fake_meltingpot.set_meltingpot_response_value(json.dumps(meltingtpot_users_history_response()))
        response = self.meltingpot.proxy(
            method='GET',
            path='1/users/%s/' % TEST_UID,
        )
        eq_(response, meltingtpot_users_history_response())
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='GET',
            url='http://meltingpot_api/1/users/{}/?consumer={}'.format(TEST_UID, TEST_MELTINGPOT_API_CONSUMER),
        )

    def test_ok_post(self):
        self.fake_meltingpot.set_meltingpot_response_value(json.dumps(meltingpot_ok_response()))
        response = self.meltingpot.proxy(
            method='POST',
            path='1/users/',
            data={
                'uid': TEST_UID,
                'reason': TEST_REASON,
            },
        )
        eq_(response['status'], 'ok')
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='POST',
            url='http://meltingpot_api/1/users/?consumer={}'.format(TEST_MELTINGPOT_API_CONSUMER),
            post_args={
                'uid': TEST_UID,
                'reason': TEST_REASON,
            },
        )

    def test_ok_meltingpot_error(self):
        self.fake_meltingpot.set_meltingpot_response_value(meltingpot_error_database_response())
        response = self.meltingpot.proxy(
            method='GET',
            path='1/users/%s/' % TEST_UID,
        )
        eq_(response['errors'], ['backend.database_failed'])
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='GET',
            url='http://meltingpot_api/1/users/{}/?consumer={}'.format(TEST_UID, TEST_MELTINGPOT_API_CONSUMER),
        )

    def test_ok_unhandled_exception(self):
        self.fake_meltingpot.set_meltingpot_response_value(meltingpot_exception_unhandled())
        response = self.meltingpot.proxy(
            method='GET',
            path='1/users/%s/' % TEST_UID,
        )
        eq_(response['errors'], ['exception.unhandled'])
        self.fake_meltingpot.requests[0].assert_properties_equal(
            method='GET',
            url='http://meltingpot_api/1/users/{}/?consumer={}'.format(TEST_UID, TEST_MELTINGPOT_API_CONSUMER),
        )

    @raises(MeltingpotApiInvalidResponseError)
    def test_error(self):
        self.fake_meltingpot.set_meltingpot_response_side_effect(MeltingpotApiInvalidResponseError)
        self.meltingpot.proxy(
            method='GET',
            path='1/users/%s/' % TEST_UID,
        )
