# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.mail_apis import (
    HuskyApi,
    HuskyInvalidResponseError,
    HuskyTaskAlreadyExistsError,
    HuskyTemporaryError,
)
from passport.backend.core.builders.mail_apis.faker import (
    FakeHuskyApi,
    husky_delete_user_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_UID = 1


@with_settings_hosts(
    HUSKY_API_URL='http://localhost/',
    HUSKY_API_RETRIES=10,
    HUSKY_API_TIMEOUT=1,
)
class TestHuskyApi(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'husky',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.husky_api = HuskyApi()

        self.fake_husky_api = FakeHuskyApi()
        self.fake_husky_api.start()

        self.methods = [
            ('delete_user', self.husky_api.delete_user),
        ]

    def tearDown(self):
        self.fake_husky_api.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_husky_api
        del self.husky_api
        del self.fake_tvm_credentials_manager
        del self.methods

    def test_delete_user__ok(self):
        self.fake_husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(),
        )

        resp = self.husky_api.delete_user(TEST_UID)

        eq_(resp, json.loads(husky_delete_user_response()))

        requests = self.fake_husky_api.requests
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/delete_user/%d' % TEST_UID,
        )

    def test_retries_error(self):
        for i, (method_name, method) in enumerate(self.methods):
            self.fake_husky_api.set_response_side_effect(method_name, HuskyTemporaryError)
            with assert_raises(HuskyTemporaryError):
                method(TEST_UID)
        eq_(len(self.fake_husky_api.requests), 10 * (i + 1))

    def test_invalid_json(self):
        for method_name, method in self.methods:
            self.fake_husky_api.set_response_value(method_name, 'invalid json')
            with assert_raises(HuskyInvalidResponseError):
                method(TEST_UID)
        eq_(len(self.fake_husky_api.requests), 1)

    def test_no_tasks__error(self):
        self.fake_husky_api.set_response_value(
            'delete_user',
            json.dumps({'status': 'ok'}),
        )
        with assert_raises(HuskyInvalidResponseError):
            self.husky_api.delete_user(TEST_UID)

    def test_user_not_found__error(self):
        self.fake_husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(
                status='error',
                code=2,
                error_message='Cannot find user shard, uid: u\'%s\'' % TEST_UID,
            ),
        )
        with assert_raises(HuskyTaskAlreadyExistsError):
            self.husky_api.delete_user(TEST_UID)

    def test_task_exists__error(self):
        self.fake_husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(
                status='error',
                code=3,
                error_message='Task exists',
            ),
        )
        with assert_raises(HuskyInvalidResponseError):
            self.husky_api.delete_user(TEST_UID)

    def test_husky_temporary_error(self):
        self.fake_husky_api.set_response_value(
            'delete_user',
            husky_delete_user_response(status='error'),
        )
        with assert_raises(HuskyTemporaryError):
            self.husky_api.delete_user(TEST_UID)
