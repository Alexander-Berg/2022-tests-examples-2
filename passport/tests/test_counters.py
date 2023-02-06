# -*- coding: utf-8 -*-
from collections import defaultdict
import time
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.conf.default_settings import (
    TEST_COUNTERS_ALWAYS_EMPTY_CONSUMER,
    TEST_COUNTERS_ALWAYS_FULL_CONSUMER,
)
from passport.backend.core.counters import (  # Моки для конфигураций счетчиков лежат в core/passport/test/mock_objects.py
    auth_challenge_per_ip,
    auth_email,
    bad_rfc_otp_counter,
    Buckets,
    calls_per_ip,
    calls_per_phone,
    change_password_counter,
    check_answer_counter,
    check_answer_per_ip_and_uid_counter,
    email_per_uid_and_address_counter,
    email_per_uid_counter,
    get_buckets,
    get_counters_redis_manager,
    login_restore_counter,
    magic_link_per_ip_counter,
    magic_link_per_uid_counter,
    migrate_mailish,
    passman_recovery_key_counter,
    profile_fails,
    question_change_email_counter,
    register_kolonkish_per_creator_uid,
    register_mailish,
    register_phonish_by_phone,
    registration_karma,
    restore_counter,
    restore_semi_auto_compare_counter,
    sms_per_ip,
    sms_per_ip_for_consumer,
    sms_per_phone,
    social_registration_captcha,
    uncompleted_registration_captcha,
    userinfo_counter,
    yapic_upload_ip_uid_counter,
)
from passport.backend.core.counters.buckets import do_buckets_exist
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.host.host import get_current_host
import passport.backend.core.redis_manager
from passport.backend.core.redis_manager.faker.fake_redis import FakeRedis
from passport.backend.core.redis_manager.redis_manager import RedisError
from passport.backend.core.test.consts import (
    TEST_EMAIL1,
    TEST_UID1,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_IP = TEST_IP1 = '127.0.0.1'
TEST_ALWAYS_FULL_IP = '127.0.0.100'
TEST_ALWAYS_EMPTY_IP = '127.0.0.200'
TEST_IP2 = '2a02:6b8:0:101:6267:20ff:fe63:7af4'
TEST_TRUSTED_IP = '87.250.235.4'
TEST_UID = 1234
TEST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_CONSUMER1 = 'dev1'
TEST_CONSUMER2 = 'dev2'


class Base(TestCase):

    def setUp(self):

        self.time = 0.

        self.patches = [
            mock.patch('time.time', lambda: self.time),
        ]

        for patch in self.patches:
            patch.start()

        self.redis = get_counters_redis_manager()
        self.redis.redis_constructor = FakeRedis
        self.redis.configure({
            get_current_host().get_id(): {
                'host': 'localhost',
                'port': 6379,
            },
        })

        # чтобы время не стало отрицательным промотаем на год вперед
        self.tick(60 * 60 * 24 * 365)

        self.grants = FakeGrants()
        self.grants.set_grants_return_value({
            TEST_COUNTERS_ALWAYS_EMPTY_CONSUMER: {
                'networks': [TEST_ALWAYS_EMPTY_IP],
            },
            TEST_COUNTERS_ALWAYS_FULL_CONSUMER: {
                'networks': [TEST_ALWAYS_FULL_IP],
            },
        })
        self.grants.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()

        self.grants.stop()
        passport.backend.core.redis_manager._redises = defaultdict(passport.backend.core.redis_manager.redis_manager.RedisManager)

        del self.patches
        del self.grants
        del self.redis

    def tick(self, seconds):
        self.time += seconds


@with_settings_hosts(**mock_counters())
class TestBuckets(Base):

    def setUp(self):
        super(TestBuckets, self).setUp()
        self.buckets = Buckets('testbuckets', 10, 10, 10)

    def tearDown(self):
        del self.buckets
        super(TestBuckets, self).tearDown()

    def get_current_key(self, user_ip):
        return '%s:%s:%d' % (self.buckets.prefix, TEST_IP1,
                             time.time() // self.buckets.duration)

    def test_incr(self):
        self.redis.incr(self.get_current_key(TEST_IP1))
        eq_(self.redis.hgetall(self.get_current_key(TEST_IP1)), '1')

    def test_get(self):
        self.redis.set(self.get_current_key(TEST_IP1), 1)
        eq_(self.buckets.get(TEST_IP1), 1)

    def test_duration(self):

        eq_(self.buckets.incr(TEST_IP1), 1)

        self.tick(self.buckets.duration / 2)

        # прошла половина периода, корзина ещё не сменилась
        eq_(self.buckets.incr(TEST_IP1), 2)

        self.tick(self.buckets.duration / 2)

        # сменилась корзина, incr возвращает значение из новой
        eq_(self.buckets.incr(TEST_IP1), 1)
        # а старая всё ещё на месте, и сумма с ней может быть получена через get
        eq_(self.buckets.get(TEST_IP1), 3)

    def test_complex(self):
        for i in range(self.buckets.count):
            eq_(self.buckets.get(TEST_IP1), i)
            eq_(self.buckets.incr(TEST_IP1), 1)
            self.tick(self.buckets.duration)
        for i in reversed(range(self.buckets.count)):
            eq_(self.buckets.get(TEST_IP1), i)
            self.tick(self.buckets.duration)

    def test_expire(self):
        key = self.get_current_key(TEST_IP1)
        self.buckets.incr(TEST_IP1)
        self.tick((self.buckets.count + 1) * self.buckets.duration)
        ok_(self.redis.hgetall(key) is False)

    def test_bad_value(self):
        eq_(self.buckets.incr(TEST_IP1), 1)
        self.redis.set(self.get_current_key(TEST_IP1), 'abrakadabra')
        eq_(self.buckets.get(TEST_IP1), 0)

    @raises(ValueError)
    def test_get_unexistent_buckets(self):
        get_buckets('blablablablabla')

    def test_do_buckets_exist(self):
        ok_(not do_buckets_exist('blablablablabla'))
        ok_(do_buckets_exist('sms:ip'))

    def test_bucket_hit_limit_by_ip(self):
        ok_(self.buckets.hit_limit_by_ip(TEST_ALWAYS_FULL_IP))
        ok_(not self.buckets.hit_limit_by_ip(TEST_ALWAYS_EMPTY_IP))
        ok_(not self.buckets.hit_limit_by_ip(TEST_IP))

        for ip in [TEST_ALWAYS_EMPTY_IP, TEST_ALWAYS_FULL_IP, TEST_IP]:
            self.redis.set(self.buckets._id(ip, self.time), self.buckets.limit)

        ok_(self.buckets.hit_limit_by_ip(TEST_ALWAYS_FULL_IP))
        ok_(not self.buckets.hit_limit_by_ip(TEST_ALWAYS_EMPTY_IP))
        ok_(self.buckets.hit_limit_by_ip(TEST_IP))


class RegKarmaBase(Base):
    def setUp(self):
        super(RegKarmaBase, self).setUp()
        self.bad_buckets = registration_karma.get_bad_buckets()
        self.good_buckets = registration_karma.get_good_buckets()

    def tearDown(self):
        del self.bad_buckets
        del self.good_buckets
        super(RegKarmaBase, self).tearDown()


@with_settings_hosts(
    **mock_counters(
        REGKARMA_BAD_COUNTER=(24, 3600, 3),
        REGKARMA_GOOD_COUNTER=(24, 3600, 2),
    )
)
class TestRegKarma(RegKarmaBase):

    def test_get_status(self):
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.WHITE)
        for _ in range(2):
            registration_karma.incr_bad(TEST_IP1)
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.WHITE)
        registration_karma.incr_bad(TEST_IP1)
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.BLOCKED_BLACK)

    def test_expire(self):

        # имеем ip с N плохих регистраций, на одну меньше чем нужно банить
        for _ in range(2):
            registration_karma.incr_bad(TEST_IP1)

        # через час приходит ещё одна плохая регистрация
        self.tick(3600)
        registration_karma.incr_bad(TEST_IP1)
        eq_(self.bad_buckets.get(TEST_IP1), 3)

        # через 23 часа (с начала отсчета, не забываем про добавленный час) IP всё ещё забанен
        self.tick(22 * 3600)
        eq_(self.bad_buckets.get(TEST_IP1), 3)

        # а через 24 часа забыли про N изначальных, осталась одна
        self.tick(3600)
        eq_(self.bad_buckets.get(TEST_IP1), 1)

    def test_good(self):
        # Вначале был белый адрес
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.WHITE)
        # Потом с этого адреса пришли 3 пользователя с плохой кармой
        for _ in range(3):
            registration_karma.incr_bad(TEST_IP1)
        # И адрес стал чёрным
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.BLOCKED_BLACK)
        # Пришёл пользователь с хорошей кармой
        registration_karma.incr_good(TEST_IP1)
        # Но его добра не хватило, чтобы обелить адрес, он остался чёрным
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.BLOCKED_BLACK)
        # И позвал хороший пользователь друга с хорошей кармой,
        registration_karma.incr_good(TEST_IP1)
        # Обелился адрес.
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.AMNISTED_GRAY)

    def test_redis_timeout(self):
        patches = [
            mock.patch('passport.backend.core.redis_manager.faker.fake_redis.FakeRedis.incr', mock.Mock(side_effect=RedisError())),
            mock.patch('passport.backend.core.redis_manager.faker.fake_redis.FakeRedis.get', mock.Mock(side_effect=RedisError())),
            mock.patch('passport.backend.core.redis_manager.faker.fake_redis.FakeRedis.mget', mock.Mock(side_effect=RedisError())),
        ]
        try:
            for patch in patches:
                patch.start()
            eq_(registration_karma.get_status(TEST_IP1), registration_karma.WHITE)
            eq_(registration_karma.incr_bad(TEST_IP1), 0)
        finally:
            for patch in reversed(patches):
                patch.stop()


@with_settings_hosts(
    **mock_counters(
        REGKARMA_BAD_COUNTER=(24, 3600, 3),
        REGKARMA_GOOD_COUNTER=(24, 3600, 2),
        REGKARMA_GOOD_ENABLED=False,
    )
)
class TestGoodDisabled(RegKarmaBase):
    def test_good_disabled(self):
        for _ in range(2):
            # отключено - выдаем всегда 0
            eq_(registration_karma.incr_good(TEST_IP1), 0)
        for i in range(3):
            eq_(registration_karma.incr_bad(TEST_IP1), i + 1)
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.BLOCKED_GRAY)


@with_settings_hosts(
    **mock_counters(
        REGKARMA_BAD_COUNTER=(24, 3600, 3),
        REGKARMA_GOOD_COUNTER=(24, 3600, 2),
        REGKARMA_BAD_ENABLED=False,
    )
)
class TestBadDisabled(RegKarmaBase):
    def test_bad_disabled(self):
        for _ in range(3):
            eq_(registration_karma.incr_bad(TEST_IP1), 0)
        eq_(registration_karma.get_status(TEST_IP1), registration_karma.WHITE)


TEST_PROVIDER = 'vk'


@with_settings_hosts(
    **mock_counters(
        SOCIALREG_PER_IP_CAPTCHA_LIMIT_COUNTER=(24, 3600, 2),
        SOCIALREG_PER_PROVIDER_CAPTCHA_LIMIT_COUNTER=(24, 3600, 4),
    )
)
class TestSocialRegCaptchaLimit(Base):

    def setUp(self):
        super(TestSocialRegCaptchaLimit, self).setUp()
        self.ip_bucket = social_registration_captcha.get_per_ip_buckets()
        self.pr_bucket = social_registration_captcha.get_per_provider_buckets()

    def tearDown(self):
        del self.ip_bucket
        del self.pr_bucket
        super(TestSocialRegCaptchaLimit, self).tearDown()

    def test_block_by_ip(self):
        self.ip_bucket.incr(TEST_IP)
        ok_(not social_registration_captcha.is_required(TEST_IP, TEST_PROVIDER))
        ok_(social_registration_captcha.is_required(TEST_IP, TEST_PROVIDER))

    def test_block_by_provider(self):
        for _ in range(3):
            self.pr_bucket.incr(TEST_PROVIDER)
        ok_(not social_registration_captcha.is_required(TEST_IP, TEST_PROVIDER))
        ok_(social_registration_captcha.is_required(TEST_IP, TEST_PROVIDER))

    def test_counter_uses_many_buckets(self):
        self.ip_bucket.incr(TEST_IP)
        self.tick(12 * 3600)
        self.ip_bucket.incr(TEST_IP)
        ok_(social_registration_captcha.is_required(TEST_IP, TEST_PROVIDER))


@with_settings_hosts(**mock_counters())
class TestSmsPerIPCounter(Base):

    def test_get_counters(self):
        trusted = sms_per_ip.get_counter(user_ip=TEST_TRUSTED_IP)  # passportdev-python
        untrusted = sms_per_ip.get_counter(user_ip=TEST_IP)
        ok_(trusted.limit >= untrusted.limit)

    def test_get_registration_completed_with_phone_counters(self):
        trusted = sms_per_ip.get_registration_completed_with_phone_counter(user_ip=TEST_TRUSTED_IP)  # passportdev-python
        untrusted = sms_per_ip.get_registration_completed_with_phone_counter(user_ip=TEST_IP)
        ok_(trusted.limit >= untrusted.limit)

    def test_get_auth_forwarding_counters(self):
        trusted = sms_per_ip.get_auth_forwarding_by_sms_counter(user_ip=TEST_TRUSTED_IP)  # passportdev-python
        untrusted = sms_per_ip.get_auth_forwarding_by_sms_counter(user_ip=TEST_IP)
        ok_(trusted.limit >= untrusted.limit)


@with_settings_hosts(
    **mock_counters(
        UNCOMPLETEDREG_CALLS_CAPTCHA_LIMIT_COUNTER=(24, 3600, 4),
        UNCOMPLETEDREG_PER_IP_CAPTCHA_LIMIT_COUNTER=(24, 3600, 2),
    )
)
class TestUncompletedRegCaptchaLimit(Base):
    def setUp(self):
        super(TestUncompletedRegCaptchaLimit, self).setUp()
        self.ip_bucket = uncompleted_registration_captcha.get_per_ip_buckets()
        self.calls_bucket = uncompleted_registration_captcha.get_calls_bucket()

    def tearDown(self):
        del self.ip_bucket
        del self.calls_bucket
        super(TestUncompletedRegCaptchaLimit, self).tearDown()

    def test_block_by_ip(self):
        self.ip_bucket.incr(TEST_IP)
        ok_(not uncompleted_registration_captcha.is_required(TEST_IP))
        ok_(uncompleted_registration_captcha.is_required(TEST_IP))

    def test_block_by_calls(self):
        for _ in range(3):
            self.calls_bucket.incr()
        ok_(not uncompleted_registration_captcha.is_required(TEST_IP))
        ok_(uncompleted_registration_captcha.is_required(TEST_IP))

    def test_counter_uses_many_buckets(self):
        self.ip_bucket.incr(TEST_IP)
        self.tick(12 * 3600)
        self.ip_bucket.incr(TEST_IP)
        ok_(uncompleted_registration_captcha.is_required(TEST_IP))

    def test_increment_only_ip_if_exceed(self):
        for _ in range(2):
            self.ip_bucket.incr(TEST_IP)
        for _ in range(4):
            self.calls_bucket.incr()
        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.calls_bucket.get(), 4)

        ok_(uncompleted_registration_captcha.is_required(TEST_IP))

        eq_(self.ip_bucket.get(TEST_IP), 3)
        eq_(self.calls_bucket.get(), 4)

    def test_increment_ip_and_calls_if_calls_exceed(self):
        self.ip_bucket.incr(TEST_IP)
        for _ in range(5):
            self.calls_bucket.incr()
        eq_(self.ip_bucket.get(TEST_IP), 1)
        eq_(self.calls_bucket.get(), 5)

        ok_(uncompleted_registration_captcha.is_required(TEST_IP))

        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.calls_bucket.get(), 6)

    def test_increment_ip_and_calls(self):
        self.ip_bucket.incr(TEST_IP)
        for _ in range(3):
            self.calls_bucket.incr()
        eq_(self.ip_bucket.get(TEST_IP), 1)
        eq_(self.calls_bucket.get(), 3)

        ok_(not uncompleted_registration_captcha.is_required(TEST_IP))

        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.calls_bucket.get(), 4)


@with_settings_hosts(
    **mock_counters(
        CHECK_ANSWER_PER_IP_LIMIT_COUNTER=(24, 3600, 4),
        CHECK_ANSWER_PER_UID_LIMIT_COUNTER=(24, 3600, 2),
    )
)
class TestCheckAnswerLimit(Base):

    def setUp(self):
        super(TestCheckAnswerLimit, self).setUp()
        self.ip_bucket = check_answer_counter.get_per_ip_buckets()
        self.uid_bucket = check_answer_counter.get_per_uid_buckets()

    def tearDown(self):
        del self.ip_bucket
        del self.uid_bucket
        super(TestCheckAnswerLimit, self).tearDown()

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not check_answer_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        ok_(not check_answer_counter.is_limit_exceeded(TEST_IP2, TEST_UID))
        ok_(check_answer_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 5)
        eq_(self.uid_bucket.get(TEST_UID), 3)

    def test_block_by_uid(self):
        self.uid_bucket.incr(TEST_UID)
        ok_(not check_answer_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        ok_(check_answer_counter.is_limit_exceeded(TEST_IP2, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 1)
        eq_(self.uid_bucket.get(TEST_UID), 3)


@with_settings_hosts(
    **mock_counters(
        CHECK_ANSWER_PER_IP_LIMIT_COUNTER=(24, 3600, 4),
        CHECK_ANSWER_PER_IP_AND_UID_LIMIT_COUNTER=(24, 3600, 2),
    )
)
class TestCheckAnswerPerIpAndUidLimit(Base):

    def setUp(self):
        super(TestCheckAnswerPerIpAndUidLimit, self).setUp()
        self.ip_bucket = check_answer_counter.get_per_ip_buckets()
        self.ip_uid_bucket = check_answer_per_ip_and_uid_counter.get_per_ip_and_uid_buckets()

    def tearDown(self):
        del self.ip_bucket
        del self.ip_uid_bucket
        super(TestCheckAnswerPerIpAndUidLimit, self).tearDown()

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not check_answer_per_ip_and_uid_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        ok_(not check_answer_per_ip_and_uid_counter.is_limit_exceeded(TEST_IP2, TEST_UID))
        ok_(check_answer_per_ip_and_uid_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 5)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 2)

    def test_block_by_uid(self):
        self.ip_uid_bucket.incr(self._build_ip_uid_key(TEST_IP, TEST_UID))
        ok_(not check_answer_per_ip_and_uid_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        ok_(check_answer_per_ip_and_uid_counter.is_limit_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 3)

    def _build_ip_uid_key(self, ip, uid):
        return u'%s:%s' % (ip, uid)


@with_settings_hosts(
    **mock_counters(
        CHANGE_PASSWORD_PER_PHONE_NUMBER_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class TestChangePasswordPerPhoneNumberCounter(Base):
    def setUp(self):
        super(TestChangePasswordPerPhoneNumberCounter, self).setUp()
        self.counter = change_password_counter.get_per_phone_number_buckets()

    def tearDown(self):
        del self.counter
        super(TestChangePasswordPerPhoneNumberCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit())

        for _ in range(4):
            self.counter.incr()
        ok_(not self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())


@with_settings_hosts(
    **mock_counters(
        CHANGE_PASSWORD_PER_USER_IP_LIMIT_COUNTER=(24, 3600, 7),
    )
)
class TestChangePasswordPerUserIpCounter(Base):
    def setUp(self):
        super(TestChangePasswordPerUserIpCounter, self).setUp()
        self.counter = change_password_counter.get_per_user_ip_buckets()

    def tearDown(self):
        del self.counter
        super(TestChangePasswordPerUserIpCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit())

        for _ in range(6):
            self.counter.incr()
        ok_(not self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())


@with_settings_hosts(
    **mock_counters(
        AUTH_CHALLENGE_PER_IP_LIMIT_COUNTER=(24, 3600, 7),
    )
)
class TestAuthChallengePerIpCounter(Base):
    def setUp(self):
        super(TestAuthChallengePerIpCounter, self).setUp()
        self.counter = auth_challenge_per_ip.get_counter()

    def tearDown(self):
        del self.counter
        super(TestAuthChallengePerIpCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit())

        for _ in range(6):
            self.counter.incr()
        ok_(not self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())


@with_settings_hosts(
    **mock_counters(
        AUTH_EMAIL_RECENTLY_SENT_COUNTER=(1, 300, 1),
    )
)
class TestAuthEmailCounter(Base):
    def setUp(self):
        super(TestAuthEmailCounter, self).setUp()
        self.counter = auth_email.get_counter()

    def tearDown(self):
        del self.counter
        super(TestAuthEmailCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit(TEST_UID))

        for _ in range(2):
            self.counter.incr(TEST_UID)
            ok_(self.counter.hit_limit(TEST_UID))

    def test_function(self):
        ok_(not auth_email.incr_counter_and_check_limit(TEST_UID))

        for _ in range(2):
            ok_(auth_email.incr_counter_and_check_limit(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        PROFILE_FAILS_COUNTER=(10, 1, 10),
    )
)
class TestProfileFailsCounter(Base):
    def setUp(self):
        super(TestProfileFailsCounter, self).setUp()
        self.counter = profile_fails.get_counter()

    def tearDown(self):
        del self.counter
        super(TestProfileFailsCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit())

        for _ in range(9):
            self.counter.incr()
        ok_(not self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())

        self.counter.incr()
        ok_(self.counter.hit_limit())

    def test_is_profile_broken(self):
        for _ in range(9):
            ok_(not profile_fails.is_profile_broken())
        eq_(self.counter.get(), 9)

        ok_(profile_fails.is_profile_broken())

        profile_fails.is_profile_broken()
        eq_(self.counter.get(), 11)


@with_settings_hosts(
    **mock_counters(
        RESTORE_SEMI_AUTO_COMPARE_PER_IP_LIMIT_COUNTER=(24, 3600, 4),
        RESTORE_SEMI_AUTO_COMPARE_PER_UID_LIMIT_COUNTER=(24, 3600, 2),
    )
)
class TestRestoreSemiAutoCompareCounter(Base):
    def setUp(self):
        super(TestRestoreSemiAutoCompareCounter, self).setUp()
        self.uid_bucket = restore_semi_auto_compare_counter.get_per_uid_buckets()
        self.ip_bucket = restore_semi_auto_compare_counter.get_per_ip_buckets()

    def tearDown(self):
        del self.uid_bucket
        del self.ip_bucket
        super(TestRestoreSemiAutoCompareCounter, self).tearDown()

    def test_block_by_uid(self):
        self.uid_bucket.incr(TEST_UID)
        ok_(not restore_semi_auto_compare_counter.is_uid_limit_exceeded(TEST_UID))
        ok_(restore_semi_auto_compare_counter.is_uid_limit_exceeded(TEST_UID))

    def test_only_check_by_uid(self):
        self.uid_bucket.incr(TEST_UID)
        eq_(self.uid_bucket.get(TEST_UID), 1)
        restore_semi_auto_compare_counter.is_uid_limit_exceeded(TEST_UID, only_check=True)
        eq_(self.uid_bucket.get(TEST_UID), 1)

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not restore_semi_auto_compare_counter.is_ip_limit_exceeded(TEST_IP))
        ok_(restore_semi_auto_compare_counter.is_ip_limit_exceeded(TEST_IP))

    def test_only_check_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        eq_(self.ip_bucket.get(TEST_IP), 3)
        restore_semi_auto_compare_counter.is_ip_limit_exceeded(TEST_IP, only_check=True)
        eq_(self.ip_bucket.get(TEST_IP), 3)


@with_settings_hosts(
    **mock_counters(RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 4))
)
class TestRestoreCounter(Base):
    def setUp(self):
        super(TestRestoreCounter, self).setUp()
        self.ip_bucket = restore_counter.get_per_ip_buckets()

    def tearDown(self):
        del self.ip_bucket
        super(TestRestoreCounter, self).tearDown()

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not restore_counter.is_ip_limit_exceeded(TEST_IP))
        ok_(restore_counter.is_ip_limit_exceeded(TEST_IP))
        ok_(not restore_counter.is_ip_limit_exceeded(TEST_IP, limit=6))

    def test_only_check_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        eq_(self.ip_bucket.get(TEST_IP), 3)
        restore_counter.is_ip_limit_exceeded(TEST_IP, only_check=True)
        eq_(self.ip_bucket.get(TEST_IP), 3)


@with_settings_hosts(
    **mock_counters(SHORT_USERINFO_COUNTER=(24, 3600, 4))
)
class TestShortUserInfoCounter(Base):
    def setUp(self):
        super(TestShortUserInfoCounter, self).setUp()
        self.userinfo_bucket = userinfo_counter.get_short_userinfo_bucket()

    def tearDown(self):
        del self.userinfo_bucket
        super(TestShortUserInfoCounter, self).tearDown()

    def test_hit_limit_by_ip(self):
        for _ in range(4):
            self.userinfo_bucket.incr(TEST_IP)

        ok_(userinfo_counter.get_short_userinfo_bucket().hit_limit_by_ip(TEST_IP))


@with_settings_hosts(
    **mock_counters(
        YAPIC_UPLOAD_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_UPLOAD_PER_UID_LIMIT_COUNTER=(2, 60, 2),
    )
)
class TestCheckYapicUploadPerIpAndUidLimit(Base):

    def setUp(self):
        super(TestCheckYapicUploadPerIpAndUidLimit, self).setUp()
        self.ip_bucket = yapic_upload_ip_uid_counter.get_counter_buckets()
        self.ip_uid_bucket = yapic_upload_ip_uid_counter.get_counter_buckets(check='uid')

    def tearDown(self):
        del self.ip_bucket
        del self.ip_uid_bucket
        super(TestCheckYapicUploadPerIpAndUidLimit, self).tearDown()

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not yapic_upload_ip_uid_counter.is_limit_upload_exceeded(TEST_IP, TEST_UID))
        ok_(not yapic_upload_ip_uid_counter.is_limit_upload_exceeded(TEST_IP2, TEST_UID))
        ok_(yapic_upload_ip_uid_counter.is_limit_upload_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 5)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 2)

    def test_block_by_uid(self):
        self.ip_uid_bucket.incr(self._build_ip_uid_key(TEST_IP, TEST_UID))
        ok_(not yapic_upload_ip_uid_counter.is_limit_upload_exceeded(TEST_IP, TEST_UID))
        ok_(yapic_upload_ip_uid_counter.is_limit_upload_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 3)

    def _build_ip_uid_key(self, ip, uid):
        return u'%s:%s' % (ip, uid)


@with_settings_hosts(
    **mock_counters(
        YAPIC_DELETE_PER_IP_LIMIT_COUNTER=(6, 600, 4),
        YAPIC_DELETE_PER_UID_LIMIT_COUNTER=(2, 60, 2),
    )
)
class TestCheckYapicDeletePerIpAndUidLimit(Base):

    def setUp(self):
        super(TestCheckYapicDeletePerIpAndUidLimit, self).setUp()
        self.ip_bucket = yapic_upload_ip_uid_counter.get_counter_buckets(mode='delete')
        self.ip_uid_bucket = yapic_upload_ip_uid_counter.get_counter_buckets(check='uid', mode='delete')

    def tearDown(self):
        del self.ip_bucket
        del self.ip_uid_bucket
        super(TestCheckYapicDeletePerIpAndUidLimit, self).tearDown()

    def test_block_by_ip(self):
        for _ in range(3):
            self.ip_bucket.incr(TEST_IP)
        ok_(not yapic_upload_ip_uid_counter.is_limit_delete_exceeded(TEST_IP, TEST_UID))
        ok_(not yapic_upload_ip_uid_counter.is_limit_delete_exceeded(TEST_IP2, TEST_UID))
        ok_(yapic_upload_ip_uid_counter.is_limit_delete_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 5)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 2)

    def test_block_by_uid(self):
        self.ip_uid_bucket.incr(self._build_ip_uid_key(TEST_IP, TEST_UID))
        ok_(not yapic_upload_ip_uid_counter.is_limit_delete_exceeded(TEST_IP, TEST_UID))
        ok_(yapic_upload_ip_uid_counter.is_limit_delete_exceeded(TEST_IP, TEST_UID))
        eq_(self.ip_bucket.get(TEST_IP), 2)
        eq_(self.ip_uid_bucket.get(self._build_ip_uid_key(TEST_IP, TEST_UID)), 3)

    def _build_ip_uid_key(self, ip, uid):
        return u'%s:%s' % (ip, uid)


@with_settings_hosts(
    **mock_counters(
        SMS_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
    )
)
class TestSmsPerPhoneCounter(Base):
    def setUp(self):
        super(TestSmsPerPhoneCounter, self).setUp()
        self.phone_number = '79090000001'
        self.phone_bucket = sms_per_phone.get_per_phone_buckets()

    def tearDown(self):
        del self.phone_bucket
        super(TestSmsPerPhoneCounter, self).tearDown()

    def test_hit_limit(self):
        ok_(not self.phone_bucket.hit_limit(self.phone_number))

        for _ in range(self.phone_bucket.limit - 1):
            self.phone_bucket.incr(self.phone_number)
            ok_(not self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))


@with_settings_hosts(
    **mock_counters(
        SMS_PER_PHONE_ON_REGISTRATION_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class TestSmsPerPhoneOnRegistrationCounter(Base):
    def setUp(self):
        super(TestSmsPerPhoneOnRegistrationCounter, self).setUp()
        self.phone_number = '79090000001'
        self.phone_bucket = sms_per_phone.get_per_phone_on_registration_buckets()

    def tearDown(self):
        del self.phone_bucket
        super(TestSmsPerPhoneOnRegistrationCounter, self).tearDown()

    def test_hit_limit(self):
        ok_(not self.phone_bucket.hit_limit(self.phone_number))

        for _ in range(self.phone_bucket.limit - 1):
            self.phone_bucket.incr(self.phone_number)
            ok_(not self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))


@with_settings_hosts(
    **mock_counters(
        SMS_PER_PHONISH_ON_REGISTRATION_LIMIT_COUNTER=(24, 3600, 10),
    )
)
class TestSmsPerPhonishOnRegistrationCounter(Base):
    def setUp(self):
        super(TestSmsPerPhonishOnRegistrationCounter, self).setUp()
        self.phone_number = '79090000001'
        self.phone_bucket = sms_per_phone.get_per_phone_on_registration_buckets(is_phonish=True)

    def tearDown(self):
        del self.phone_bucket
        super(TestSmsPerPhonishOnRegistrationCounter, self).tearDown()

    def test_hit_limit(self):
        ok_(not self.phone_bucket.hit_limit(self.phone_number))

        for _ in range(self.phone_bucket.limit - 1):
            self.phone_bucket.incr(self.phone_number)
            ok_(not self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))


@with_settings_hosts(
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 5),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 5),
    )
)
class TestLoginRestoreCounters(Base):
    def setUp(self):
        super(TestLoginRestoreCounters, self).setUp()
        self.phone_number = '79090000001'
        self.phone_bucket = login_restore_counter.get_per_phone_buckets()
        self.ip_bucket = login_restore_counter.get_per_ip_buckets()

    def tearDown(self):
        del self.phone_bucket
        del self.ip_bucket
        super(TestLoginRestoreCounters, self).tearDown()

    def test_hit_limit_by_phone(self):
        ok_(not self.phone_bucket.hit_limit(self.phone_number))

        for _ in range(self.phone_bucket.limit - 1):
            self.phone_bucket.incr(self.phone_number)
            ok_(not self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))

        self.phone_bucket.incr(self.phone_number)
        ok_(self.phone_bucket.hit_limit(self.phone_number))

    def test_hit_limit_by_ip(self):
        ok_(not self.ip_bucket.hit_limit(TEST_IP))

        for _ in range(self.ip_bucket.limit - 1):
            self.ip_bucket.incr(TEST_IP)
            ok_(not self.ip_bucket.hit_limit(TEST_IP))

        self.ip_bucket.incr(TEST_IP)
        ok_(self.ip_bucket.hit_limit(TEST_IP))

        self.ip_bucket.incr(TEST_IP)
        ok_(self.ip_bucket.hit_limit(TEST_IP))


@with_settings_hosts(
    **mock_counters(
        VALIDATOR_EMAIL_SENT_PER_UID_AND_ADDRESS_COUNTER=(24, 3600, 2),
    )
)
class TestEmailPerUidAndAddressCounter(Base):
    def _key(self):
        bucket_no = time.time() // 3600
        return 'email_validator:total_sent:123/yehlo@isis.us:%d' % bucket_no

    def test_counter_id(self):
        eq_(email_per_uid_and_address_counter.counter_id(TEST_EMAIL1, TEST_UID1), '123/yehlo@isis.us')

    def test_incr(self):
        ok_(not self.redis.hgetall(self._key()))

        email_per_uid_and_address_counter.incr(TEST_EMAIL1, TEST_UID1)
        eq_(self.redis.hgetall(self._key()), '1')

        email_per_uid_and_address_counter.incr(TEST_EMAIL1, TEST_UID1)
        eq_(self.redis.hgetall(self._key()), '2')

    def test_hit_limit(self):
        ok_(not email_per_uid_and_address_counter.hit_limit(TEST_EMAIL1, TEST_UID1))

        email_per_uid_and_address_counter.incr(TEST_EMAIL1, TEST_UID1)
        ok_(not email_per_uid_and_address_counter.hit_limit(TEST_EMAIL1, TEST_UID1))

        email_per_uid_and_address_counter.incr(TEST_EMAIL1, TEST_UID1)
        ok_(email_per_uid_and_address_counter.hit_limit(TEST_EMAIL1, TEST_UID1))


@with_settings_hosts(
    **mock_counters(
        VALIDATOR_EMAIL_SENT_PER_UID_COUNTER=(24, 3600, 2),
    )
)
class TestEmailPerUidCounter(Base):
    def _key(self):
        bucket_no = time.time() // 3600
        return 'email_validator:total_sent_per_uid:123:%d' % bucket_no

    def test_incr(self):
        ok_(not self.redis.hgetall(self._key()))

        email_per_uid_counter.incr(TEST_UID1)
        eq_(self.redis.hgetall(self._key()), '1')

        email_per_uid_counter.incr(TEST_UID1)
        eq_(self.redis.hgetall(self._key()), '2')

    def test_hit_limit(self):
        ok_(not email_per_uid_counter.hit_limit(TEST_UID1))

        email_per_uid_counter.incr(TEST_UID1)
        ok_(not email_per_uid_counter.hit_limit(TEST_UID1))

        email_per_uid_counter.incr(TEST_UID1)
        ok_(email_per_uid_counter.hit_limit(TEST_UID1))


@with_settings_hosts(**mock_counters(DB_NAME_TO_COUNTER={'sms:ip_and_consumer:inventor': (24, 3600, 5)}))
class TestSmsPerIpForConsumerCounter(Base):
    def test_no_counter(self):
        ok_(not sms_per_ip_for_consumer.exists('freya'))

        with assert_raises(ValueError):
            sms_per_ip_for_consumer.get_counter('freya')

    def test_has_counter(self):
        ok_(sms_per_ip_for_consumer.exists('inventor'))

        counter = sms_per_ip_for_consumer.get_counter('inventor')
        ok_(isinstance(counter, Buckets))
        eq_(counter.prefix, 'sms:ip_and_consumer:inventor')
        eq_(counter.count, 24)
        eq_(counter.duration, 3600)
        eq_(counter.limit, 5)
        eq_(counter.get(TEST_IP), 0)


@with_settings_hosts(
    **mock_counters(
        PASSMAN_RECOVERY_KEY_ADD_COUNTER=(1, 300, 1),
    )
)
class TestPassmanRecoveryKeyCounter(Base):
    def setUp(self):
        super(TestPassmanRecoveryKeyCounter, self).setUp()
        self.counter = passman_recovery_key_counter.get_counter()

    def tearDown(self):
        del self.counter
        super(TestPassmanRecoveryKeyCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit(TEST_UID))

        for _ in range(2):
            self.counter.incr(TEST_UID)
            ok_(self.counter.hit_limit(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        BAD_RFC_OTP_COUNTER=(6, 600, 2),
    )
)
class TestBadRfcOtpCounter(Base):
    def setUp(self):
        super(TestBadRfcOtpCounter, self).setUp()
        self.counter = bad_rfc_otp_counter.get_counter()

    def tearDown(self):
        del self.counter
        super(TestBadRfcOtpCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit(TEST_UID))

        self.counter.incr(TEST_UID)
        ok_(not self.counter.hit_limit(TEST_UID))

        for _ in range(2):
            self.counter.incr(TEST_UID)
            ok_(self.counter.hit_limit(TEST_UID))

    def test_function(self):
        ok_(not bad_rfc_otp_counter.incr_counter_and_check_limit_afterwards(TEST_UID))

        for _ in range(3):
            ok_(bad_rfc_otp_counter.incr_counter_and_check_limit_afterwards(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_SHORT_TERM=(1, 300, 1),
    )
)
class TestRegistrationKolonkishPerCreatorUidShortTermCounter(Base):
    def setUp(self):
        super(TestRegistrationKolonkishPerCreatorUidShortTermCounter, self).setUp()
        self.counter = register_kolonkish_per_creator_uid.get_short_term_counter()

    def tearDown(self):
        del self.counter
        super(TestRegistrationKolonkishPerCreatorUidShortTermCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit(TEST_UID))

        for _ in range(2):
            self.counter.incr(TEST_UID)
            ok_(self.counter.hit_limit(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        REGISTRATION_KOLONKISH_PER_CREATOR_UID_LONG_TERM=(1, 300, 1),
    )
)
class TestRegistrationKolonkishPerCreatorUidLongTermCounter(Base):
    def setUp(self):
        super(TestRegistrationKolonkishPerCreatorUidLongTermCounter, self).setUp()
        self.counter = register_kolonkish_per_creator_uid.get_long_term_counter()

    def tearDown(self):
        del self.counter
        super(TestRegistrationKolonkishPerCreatorUidLongTermCounter, self).tearDown()

    def test_counter(self):
        ok_(not self.counter.hit_limit(TEST_UID))

        for _ in range(2):
            self.counter.incr(TEST_UID)
            ok_(self.counter.hit_limit(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        REGISTER_PHONISH_BY_PHONE_PER_CONSUMER_COUNTER=(60, 60, 5),
    )
)
class TestRegisterPhonishByPhoneCounter(Base):
    def setUp(self):
        super(TestRegisterPhonishByPhoneCounter, self).setUp()
        self.counter = register_phonish_by_phone.get_per_consumer_counter()

    def tearDown(self):
        del self.counter
        super(TestRegisterPhonishByPhoneCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))

        for _ in range(4):
            self.counter.incr(TEST_CONSUMER1)
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))

        self.counter.incr(TEST_CONSUMER1)
        self.counter.incr(TEST_CONSUMER2)
        ok_(self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))


@with_settings_hosts(
    **mock_counters(
        PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER=(1, 600, 3),
        UNTRUSTED_PHONE_CONFIRMATION_CALLS_PER_IP_LIMIT_COUNTER=(1, 600, 2),
    )
)
class TestCallsPerIPCounter(Base):
    def setUp(self):
        super(TestCallsPerIPCounter, self).setUp()
        self.trusted = calls_per_ip.get_counter(user_ip=TEST_TRUSTED_IP)  # passportdev-python
        self.untrusted = calls_per_ip.get_counter(user_ip=TEST_IP)

    def tearDown(self):
        del self.trusted
        del self.untrusted
        super(TestCallsPerIPCounter, self).tearDown()

    def test_counters(self):
        ok_(self.trusted.limit >= self.untrusted.limit)

        ok_(not self.trusted.hit_limit(TEST_TRUSTED_IP))
        ok_(not self.untrusted.hit_limit(TEST_IP))

        for _ in range(self.untrusted.limit):
            self.trusted.incr(TEST_TRUSTED_IP)
            self.untrusted.incr(TEST_IP)

        ok_(not self.trusted.hit_limit(TEST_TRUSTED_IP))
        ok_(self.untrusted.hit_limit(TEST_IP))

        self.trusted.incr(TEST_TRUSTED_IP)
        ok_(self.trusted.hit_limit(TEST_TRUSTED_IP))


@with_settings_hosts(
    **mock_counters(
        PHONE_CONFIRMATION_CALLS_PER_PHONE_LIMIT_COUNTER=(1, 600, 2),
    )
)
class TestCallsPerPhoneCounter(Base):
    def setUp(self):
        super(TestCallsPerPhoneCounter, self).setUp()
        self.counter = calls_per_phone.get_counter()

    def tearDown(self):
        del self.counter
        super(TestCallsPerPhoneCounter, self).tearDown()

    def test_counters(self):
        ok_(not self.counter.hit_limit(TEST_PHONE_NUMBER.digital))
        for _ in range(self.counter.limit):
            self.counter.incr(TEST_PHONE_NUMBER.digital)

        ok_(self.counter.hit_limit(TEST_PHONE_NUMBER.digital))


@with_settings_hosts(
    **mock_counters(
        REGISTER_MAILISH_PER_CONSUMER_COUNTER=(60, 60, 5),
    )
)
class TestRegisterMailishCounter(Base):
    def setUp(self):
        super(TestRegisterMailishCounter, self).setUp()
        self.counter = register_mailish.get_per_consumer_counter()

    def tearDown(self):
        del self.counter
        super(TestRegisterMailishCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))

        for _ in range(4):
            self.counter.incr(TEST_CONSUMER1)
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))

        self.counter.incr(TEST_CONSUMER1)
        self.counter.incr(TEST_CONSUMER2)
        ok_(self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))


@with_settings_hosts(
    **mock_counters(
        MIGRATE_MAILISH_PER_CONSUMER_COUNTER=(1, 60, 5),
    )
)
class TestMigrateMailishCounter(Base):
    def setUp(self):
        super(TestMigrateMailishCounter, self).setUp()
        self.counter = migrate_mailish.get_per_consumer_counter()

    def tearDown(self):
        del self.counter
        super(TestMigrateMailishCounter, self).tearDown()

    def test(self):
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))

        for _ in range(4):
            self.counter.incr(TEST_CONSUMER1)
        ok_(not self.counter.hit_limit(TEST_CONSUMER1))

        self.counter.incr(TEST_CONSUMER1)
        self.counter.incr(TEST_CONSUMER2)
        ok_(self.counter.hit_limit(TEST_CONSUMER1))
        ok_(not self.counter.hit_limit(TEST_CONSUMER2))


@with_settings_hosts(
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UID_COUNTER=(1, 600, 10),
    )
)
class TestAuthMagicLinkPerUidCounter(Base):
    def test_counters(self):
        ok_(not magic_link_per_uid_counter.hit_limit(TEST_UID))
        for _ in range(10):
            magic_link_per_uid_counter.incr(TEST_UID)

        ok_(magic_link_per_uid_counter.hit_limit(TEST_UID))


@with_settings_hosts(
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER=(1, 600, 3),
    )
)
class TestAuthMagicLinkPerIPCounter(Base):
    def setUp(self):
        super(TestAuthMagicLinkPerIPCounter, self).setUp()
        self.trusted = magic_link_per_ip_counter.get_counter(user_ip=TEST_TRUSTED_IP)
        self.untrusted = magic_link_per_ip_counter.get_counter(user_ip=TEST_IP)

    def tearDown(self):
        del self.trusted
        del self.untrusted
        super(TestAuthMagicLinkPerIPCounter, self).tearDown()

    def test_counters(self):
        ok_(self.trusted.limit >= self.untrusted.limit)

        ok_(not self.trusted.hit_limit(TEST_TRUSTED_IP))
        ok_(not self.untrusted.hit_limit(TEST_IP))

        for _ in range(self.untrusted.limit):
            self.trusted.incr(TEST_TRUSTED_IP)
            self.untrusted.incr(TEST_IP)

        ok_(not self.trusted.hit_limit(TEST_TRUSTED_IP))
        ok_(self.untrusted.hit_limit(TEST_IP))

        for _ in range(self.trusted.limit - self.untrusted.limit):
            self.trusted.incr(TEST_TRUSTED_IP)

        ok_(self.trusted.hit_limit(TEST_TRUSTED_IP))


@with_settings_hosts(
    **mock_counters(
        QUESTION_CHANGE_EMAIL_NOTIFICATION_COUNTER=(1, 600, 10),
    )
)
class TestQuestionChangeEmailCounter(Base):
    def test_counter(self):
        ok_(not question_change_email_counter.hit_limit(TEST_UID))

        for _ in range(9):
            question_change_email_counter.incr(TEST_UID)
        ok_(not question_change_email_counter.hit_limit(TEST_UID))

        question_change_email_counter.incr(TEST_UID)
        ok_(question_change_email_counter.hit_limit(TEST_UID))

        question_change_email_counter.incr(TEST_UID)
        ok_(question_change_email_counter.hit_limit(TEST_UID))
