# -*- coding: utf-8 -*-
import time
import unittest

import mock
from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.api.tests.views.bundle.test_base_data import TEST_USER_IP
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    **mock_counters(
        PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 1, 2),
    )
)
class TestCountersMockTestCase(unittest.TestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        # надо остановить время в fake_redis, чтобы протухание ключей не работало
        self.fake_redis_time_mock = mock.Mock(time=mock.Mock(return_value=time.time()))
        self.fake_redis_time_patch = mock.patch(
            'passport.backend.core.redis_manager.faker.fake_redis.time',
            self.fake_redis_time_mock,
        )
        self.fake_redis_time_patch.start()

    def tearDown(self):
        self.fake_redis_time_patch.stop()
        del self.fake_redis_time_patch

        self.env.stop()
        del self.env

    def test_mock_ok(self):
        # Временное окно счётчика - 1 секунда
        # Через 2с окно сдвигается и значение счётчика должно быть утеряно.
        # ViewsTestEnvironment "замораживает" время внутри кода счётчиков и окно не двигается.
        # Благодаря этому тесты не мигают от того, что в реальности время бежит.
        counter = sms_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)
        assert counter.get(TEST_USER_IP) == 2
        time.sleep(2)
        # можно получить значение счётчика
        assert counter.get(TEST_USER_IP) == 2

    def test_no_mock_ok(self):
        # Временное окно счётчика - 1 секунда
        # Через 2с окно сдвигается и значение счётчика должно быть утеряно.
        # ViewsTestEnvironment "замораживает" время внутри кода счётчиков и окно не двигается.
        # Благодаря этому тесты не мигают от того, что в реальности время бежит.

        self.env._counters_time_freeze_patch.stop()

        counter = sms_per_ip.get_counter(TEST_USER_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_USER_IP)
        time.sleep(2)
        # значение счётчика заэкспайрилось
        assert counter.get(TEST_USER_IP) == 0
