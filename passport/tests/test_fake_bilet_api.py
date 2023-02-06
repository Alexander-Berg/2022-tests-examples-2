# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.bilet_api import (
    BaseBiletApiError,
    BiletApi,
)
from passport.backend.core.builders.bilet_api.faker.fake_bilet_api import (
    FakeBiletApi,
    order_successful_response,
    TEST_ORDERS_RESPONSE,
    TEST_USER_POINTS_RESPONSE,
)
from passport.backend.core.test.test_utils import with_settings


TEST_METHODS_ARGS_RESPONSES = (
    ('orders', dict(sessionid='sessid', host='yandex.ru'), TEST_ORDERS_RESPONSE),
    ('order', dict(order_id='order-id', sessionid='sessid', host='yandex.ru'), order_successful_response()),
    ('user_points', dict(sessionid='sessid', host='yandex.ru'), TEST_USER_POINTS_RESPONSE),
)


@with_settings(
    BILET_API_URL='http://localhost/',
    BILET_API_TIMEOUT=1,
    BILET_API_RETRIES=2,
    BILET_API_KEY='key1',
    BILET_API_CLIENT_KEY='key2',
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class FakeBiletApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeBiletApi()
        self.faker.start()
        self.bilet_api = BiletApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_set_response_side_effect(self):
        ok_(not self.faker._mock.request.called)

        builder = BiletApi()
        for method, params, _ in TEST_METHODS_ARGS_RESPONSES:
            self.faker.set_response_side_effect(method, BaseBiletApiError())
            with assert_raises(BaseBiletApiError):
                getattr(builder, method)(**params)
        assert_builder_requested(self.faker, times=len(TEST_METHODS_ARGS_RESPONSES))

    def test_set_response_value(self):
        ok_(not self.faker._mock.request.called)

        builder = BiletApi()
        for method, params, response in TEST_METHODS_ARGS_RESPONSES:
            self.faker.set_response_value(method, response)
            result = getattr(builder, method)(**params)
            eq_(result, json.loads(response)['result'])
        assert_builder_requested(self.faker, times=len(TEST_METHODS_ARGS_RESPONSES))
