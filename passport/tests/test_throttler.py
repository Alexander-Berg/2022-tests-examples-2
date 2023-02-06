# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.core.tvm.tvm_credentials_manager import TvmCredentialsManager
from passport.backend.social.common.builders.kolmogor import (
    Kolmogor,
    KolmogorPermanentError,
    KolmogorTemporaryError,
)
from passport.backend.social.common.counter import ProcessRequestByConsumerCounterDescriptor
from passport.backend.social.common.exception import RateLimitExceededError
from passport.backend.social.common.grants import (
    GrantsConfig,
    GrantsContext,
)
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER2,
    CONSUMER3,
    CONSUMER_IP1,
    CONSUMER_IP2,
)
from passport.backend.social.common.test.grants import FakeGrantsConfig
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.throttler import Throttler


class _BasetThrottlerTestCase(TestCase):
    def setUp(self):
        super(_BasetThrottlerTestCase, self).setUp()

        self._fake_kolmogor = FakeKolmogor()
        self._fake_kolmogor.start()
        LazyLoader.register('kolmogor', Kolmogor)

    def tearDown(self):
        LazyLoader.flush()
        super(_BasetThrottlerTestCase, self).tearDown()


class TestThrottlerFromGrantsContext(_BasetThrottlerTestCase):
    def setUp(self):
        super(TestThrottlerFromGrantsContext, self).setUp()

        self._fake_grants_config = FakeGrantsConfig()
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()

        self.__patches = [
            self._fake_grants_config,
            self._fake_tvm_credentials_manager,
        ]

        for patch in self.__patches:
            patch.start()

        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TestThrottlerFromGrantsContext, self).tearDown()

    @property
    def _grants_config(self):
        tvm_cm = TvmCredentialsManager(keyring_config_name='spam', cache_time=10)
        return GrantsConfig('zarya', tvm_cm)

    def test_consumer(self):
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1])

        throttler = Throttler.from_grants_context(
            'foo',
            self._grants_config,
            GrantsContext(CONSUMER_IP1, CONSUMER1),
        )

        self.assertEqual(throttler.request_name, 'foo')
        self.assertEqual(throttler.consumers, [CONSUMER1])

    def test_unknown_consumer_ip(self):
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1])

        throttler = Throttler.from_grants_context(
            'foo',
            self._grants_config,
            GrantsContext(CONSUMER_IP2, CONSUMER1),
        )

        self.assertEqual(throttler.request_name, 'foo')
        self.assertEqual(throttler.consumers, [])

    def test_invalid_tvm_ticket(self):
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1])

        throttler = Throttler.from_grants_context(
            'foo',
            self._grants_config,
            GrantsContext(CONSUMER_IP1, CONSUMER1, ticket_body='invalid'),
        )

        self.assertEqual(throttler.request_name, 'foo')
        self.assertEqual(throttler.consumers, [])


class TestCreateThrottler(_BasetThrottlerTestCase):
    def test_no_consumers(self):
        throttler = Throttler('bar', [])

        self.assertEqual(throttler.request_name, 'bar')
        self.assertEqual(throttler.consumers, [])

    def test_many_consumers(self):
        throttler = Throttler('hru', ['foo', 'spam'])

        self.assertEqual(throttler.request_name, 'hru')
        self.assertEqual(throttler.consumers, ['foo', 'spam'])


class TestThrottlerThrottle(_BasetThrottlerTestCase):
    def build_settings(self):
        settings = super(TestThrottlerThrottle, self).build_settings()
        config = dict(
            counter_limit_for_process_request_by_consumer={
                (CONSUMER1, 'bar'): 2,
                (CONSUMER2, 'foo'): 1,
                (CONSUMER2, 'bar'): 1,
            },
            consumer_translation_for_counters={CONSUMER3: CONSUMER1},
        )
        settings['social_config'].update(config)
        return settings

    def _assert_request_get_kolmogor_counters(self, request, counters):
        request.assert_url_starts_with('https://kolmogor/get?')
        request.assert_query_equals(
            {
                'space': 'socialism_short_life',
                'keys': ','.join(counters),
            },
        )

    def _assert_request_increase_kolmogor_counter(self, request, counter):
        request.assert_url_starts_with('https://kolmogor/inc')
        request.assert_post_data_equals(
            {
                'space': 'socialism_short_life',
                'keys': counter,
            },
        )

    def test_no_consumers(self):
        with self.assertRaises(RateLimitExceededError) as assertion:
            Throttler('foo', []).throttle()

        self.assertEqual(str(assertion.exception), 'Consumer is unknown')

    def test_no_limit_for_consumer(self):
        Throttler('foo', [CONSUMER1]).throttle()
        self.assertFalse(self._fake_kolmogor.requests)

    def test_consumer_not_exceed_limit(self):
        self._fake_kolmogor.set_response_side_effect('get', ['0'])
        self._fake_kolmogor.set_response_side_effect('inc', ['OK'])

        Throttler('bar', [CONSUMER1]).throttle()

        self.assertEqual(len(self._fake_kolmogor.requests), 2)
        self._assert_request_get_kolmogor_counters(
            self._fake_kolmogor.requests[0],
            [
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
            ],
        )
        self._assert_request_increase_kolmogor_counter(
            self._fake_kolmogor.requests[1],
            ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
        )

    def test_consumer_exceed_limit(self):
        self._fake_kolmogor.set_response_side_effect('get', ['2'])

        with self.assertRaises(RateLimitExceededError) as assertion:
            Throttler('bar', [CONSUMER1]).throttle()

        self.assertEqual(
            str(assertion.exception),
            'Rate limit for %s on %s is exceeded' % (CONSUMER1, 'bar'),
        )

        self.assertEqual(len(self._fake_kolmogor.requests), 1)
        self._assert_request_get_kolmogor_counters(
            self._fake_kolmogor.requests[0],
            [
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
            ],
        )

    def test_kolmogor_temporary_failed_on_get(self):
        self._fake_kolmogor.set_response_side_effect('get', [KolmogorTemporaryError])
        Throttler('bar', [CONSUMER1]).throttle()

    def test_kolmogor_permanent_failed_on_get(self):
        self._fake_kolmogor.set_response_side_effect('get', [KolmogorPermanentError])
        Throttler('bar', [CONSUMER1]).throttle()

    def test_kolmogor_temporary_failed_on_inc(self):
        self._fake_kolmogor.set_response_side_effect('get', ['1'])
        self._fake_kolmogor.set_response_side_effect('inc', [KolmogorTemporaryError])
        Throttler('bar', [CONSUMER1]).throttle()

    def test_kolmogor_permanent_failed_on_inc(self):
        self._fake_kolmogor.set_response_side_effect('get', ['1'])
        self._fake_kolmogor.set_response_side_effect('inc', [KolmogorPermanentError])
        Throttler('bar', [CONSUMER1]).throttle()

    def test_many_consumers_not_exceed_limit(self):
        self._fake_kolmogor.set_response_side_effect('get', ['0,0'])
        self._fake_kolmogor.set_response_side_effect('inc', ['OK'])

        Throttler('bar', [CONSUMER1, CONSUMER2]).throttle()

        self.assertEqual(len(self._fake_kolmogor.requests), 2)
        self._assert_request_get_kolmogor_counters(
            self._fake_kolmogor.requests[0],
            [
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER2).name,
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
            ],
        )
        self._assert_request_increase_kolmogor_counter(
            self._fake_kolmogor.requests[1],
            ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
        )

    def test_many_consumers_some_exceed_limit(self):
        self._fake_kolmogor.set_response_side_effect('get', ['0,2'])
        self._fake_kolmogor.set_response_side_effect('inc', ['OK'])

        Throttler('bar', [CONSUMER1, CONSUMER2]).throttle()

        self.assertEqual(len(self._fake_kolmogor.requests), 2)
        self._assert_request_get_kolmogor_counters(
            self._fake_kolmogor.requests[0],
            [
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER2).name,
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
            ],
        )
        self._assert_request_increase_kolmogor_counter(
            self._fake_kolmogor.requests[1],
            ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER2).name,
        )

    def test_custom_consumer_name(self):
        self._fake_kolmogor.set_response_side_effect('get', ['0'])
        self._fake_kolmogor.set_response_side_effect('inc', ['OK'])

        Throttler('bar', [CONSUMER3]).throttle()

        self.assertEqual(len(self._fake_kolmogor.requests), 2)
        self._assert_request_get_kolmogor_counters(
            self._fake_kolmogor.requests[0],
            [
                ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
            ],
        )
        self._assert_request_increase_kolmogor_counter(
            self._fake_kolmogor.requests[1],
            ProcessRequestByConsumerCounterDescriptor('bar', CONSUMER1).name,
        )
