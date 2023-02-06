# -*- coding: utf-8 -*-

from hamcrest import (
    assert_that,
    equal_to,
)
from passport.backend.api.settings.am_pushes.classes import (
    AllowRule,
    ForbidRule,
)
from passport.backend.core.am_pushes.common import Platforms
from passport.backend.core.am_pushes.subscription_manager import (
    BestSubscriptionPerDeviceFilter,
    CapsFilter,
    ComplexRulesetFilter,
    PlatformFilter,
    PushesSubscriptionManager,
    SubscriptionFilterResult,
)
from passport.backend.core.am_pushes.test.constants import (
    TEST_APP1,
    TEST_APP2,
    TEST_APP3,
    TEST_APP4,
    TEST_DEVICE_ID1,
    TEST_EVENT_NAME,
    TEST_PUSH_SERVICE,
    TEST_PUSH_SERVICE2,
    TEST_TIMESTAMP1,
    TEST_TIMESTAMP2,
    TEST_TIMESTAMP3,
)
from passport.backend.core.am_pushes.test.mixin import (
    AmPushesTestMixin,
    has_subscription_ids,
    TEST_DEVICE_ID2,
    TEST_DEVICE_ID3,
    TEST_LOGIN_ID2,
    TEST_LOGIN_ID3,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    build_blackbox_oauth_token,
    FakeBlackbox,
)
from passport.backend.core.builders.push_api.faker import FakePushApi
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


@with_settings_hosts(
    AM_CAPABILITIES_BY_VERSION_ANDROID={
        (1, 1): {'cap1'},
        (1, 2): {'cap2'},
    },
    AM_CAPABILITIES_BY_VERSION_IOS={
        (1, 3): {'cap1'},
        (1, 4): {'cap2'},
    },
)
class _BaseFilterTestCase(PassportTestCase, AmPushesTestMixin):
    def _collection(self, subs):
        return SubscriptionFilterResult(subscriptions=subs)

    def _make_collection(self, **bundle_kwargs):
        return self._collection(self.make_parsed_subs_bundle(**bundle_kwargs))

    def _assert_subs_filtered(self, state, subs, removed=None):
        assert {s.id for s in state} == set(subs)
        if removed is not None:
            assert {r.subscription.id for r in state.removed} == set(removed)


class CapsFilterTestCase(_BaseFilterTestCase):
    def test__0_caps__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = CapsFilter([]).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 'sup1'],
            [],
        )

    def test__1_cap__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = CapsFilter(['cap1']).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s3', 's4', 's5', 's10', 's11'],
            ['s1', 's2', 's6', 's7', 's8', 's9', 'sup1'],
        )

    def test__2_caps__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = CapsFilter(['cap1', 'cap2']).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s4', 's5', 's11'],
            ['s1', 's2', 's3', 's6', 's7', 's8', 's9', 's10', 'sup1'],
        )


class PlatformFilterTestCase(_BaseFilterTestCase):
    def test_0_platforms__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = PlatformFilter([]).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 'sup1'],
            [],
        )

    def test__1_platform__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = PlatformFilter([Platforms.android]).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s1', 's2', 's3', 's4', 's5'],
            ['s6', 's7', 's8', 's9', 's10', 's11', 'sup1'],
        )

    def test__2_platforms__ok(self):
        subs = self._make_collection(with_unknown_platform=True)
        res = PlatformFilter([Platforms.android, Platforms.ios]).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11'],
            ['sup1'],
        )


class BestSubscriptionPerDeviceFilterTestCase(_BaseFilterTestCase):
    def test__different_apps__best_app(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s2'], ['s1', 's3'])

    def test__similar_apps__best_ts(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP2),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s3'], ['s1', 's2'])

    def test__similar_everything__first_element(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s1'], ['s2', 's3'])

    def test__none_everything__first_element(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            _s('s1', TEST_DEVICE_ID1, None, None),
            _s('s2', TEST_DEVICE_ID1, None, None),
            _s('s3', TEST_DEVICE_ID1, None, None),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s1'], ['s2', 's3'])

    def test__unknown_apps__best_ts(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            _s('s1', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP2),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP3),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s3'], ['s1', 's2'])

    def test__multiple__determined_rating__ok(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            # Устройство 1: в приоритете TEST_APP1
            _s('s1', TEST_DEVICE_ID1, TEST_APP2, TEST_TIMESTAMP3),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP3),
            _s('s3', TEST_DEVICE_ID1, TEST_APP3, TEST_TIMESTAMP1),
            # Устройство 2: в приоритете TEST_TIMESTAMP3
            _s('s4', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP2),
            _s('s5', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP3),
            _s('s6', TEST_DEVICE_ID2, TEST_APP1, TEST_TIMESTAMP1),
            # Устройство 3: в приоритете TEST_TIMESTAMP3
            _s('s7', TEST_DEVICE_ID3, TEST_APP3, TEST_TIMESTAMP2),
            _s('s8', TEST_DEVICE_ID3, TEST_APP4, TEST_TIMESTAMP3),
            _s('s9', TEST_DEVICE_ID3, TEST_APP3, TEST_TIMESTAMP1),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(
            res,
            ['s2', 's5', 's8'],
            ['s1', 's3', 's4', 's6', 's7', 's9'],
        )

    def test__multiple__undetermined_rating__ok(self):
        _s = self._sub_info
        subs = self._collection(self.subs_to_parsed_subs([
            # Рейтинг одинаковый, выбирается первый элемент
            _s('s1', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s2', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
            _s('s3', TEST_DEVICE_ID1, TEST_APP1, TEST_TIMESTAMP1),
        ]))
        priority = [TEST_APP1, TEST_APP2]
        res = BestSubscriptionPerDeviceFilter(priority).filter(subs)
        self._assert_subs_filtered(res, ['s1'], ['s2', 's3'])


class ComplexRulesetFilterTestCase(_BaseFilterTestCase, AmPushesTestMixin):
    def test_default_allow(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', platform='fcm'),
        ]))
        res = ComplexRulesetFilter([
            ForbidRule(platform='ios'),
        ]).filter(subs)
        self._assert_subs_filtered(res, ['s1'])

    def test_platform_allow(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', platform='fcm'),
        ]))
        res = ComplexRulesetFilter([
            ForbidRule(platform='ios'),
            AllowRule(platform='android'),
            ForbidRule(platform='android'),
        ]).filter(subs)
        self._assert_subs_filtered(res, ['s1'])

    def test_platform__deny(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', platform='fcm'),
        ]))
        res = ComplexRulesetFilter([
            AllowRule(platform='ios'),
            ForbidRule(platform='android'),
            AllowRule(platform='ios')
        ]).filter(subs)
        self._assert_subs_filtered(res, [], ['s1'])

    def test_app_allow(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', app=TEST_APP1),
        ]))
        res = ComplexRulesetFilter([
            ForbidRule(app=TEST_APP2),
            AllowRule(app=TEST_APP1),
            ForbidRule(app=TEST_APP2),
        ]).filter(subs)
        self._assert_subs_filtered(res, ['s1'])

    def test_app_deny(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', app=TEST_APP1),
        ]))
        res = ComplexRulesetFilter([
            AllowRule(app=TEST_APP2),
            ForbidRule(app=TEST_APP1),
            AllowRule(app=TEST_APP2),
        ]).filter(subs)
        self._assert_subs_filtered(res, [], ['s1'])

    def test_push_service_allow(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1'),
        ]))
        res = ComplexRulesetFilter([
            ForbidRule(push_service=TEST_PUSH_SERVICE2),
            AllowRule(app=TEST_PUSH_SERVICE),
            ForbidRule(app=TEST_PUSH_SERVICE2),
        ]).filter(subs, TEST_PUSH_SERVICE, TEST_EVENT_NAME)
        self._assert_subs_filtered(res, ['s1'])

    def test_push_service_deny(self):
        subs = self._collection(self.subs_to_parsed_subs([
            self._sub_info(id_='s1', app=TEST_APP1),
        ]))
        res = ComplexRulesetFilter([
            ForbidRule(push_service=TEST_PUSH_SERVICE),
            AllowRule(app=TEST_PUSH_SERVICE2),
            ForbidRule(app=TEST_PUSH_SERVICE),
        ]).filter(subs, TEST_PUSH_SERVICE, TEST_EVENT_NAME)
        self._assert_subs_filtered(res, [], ['s1'])


@with_settings_hosts(
    BLACKBOX_URL='test.blackbox',
    PUSH_API_TIMEOUT=3,
    PUSH_API_RETRIES=2,
    PUSH_API_URL='test',
    PUSH_API_SERVICE_NAME='passport-push',
    AM_CAPABILITIES_BY_VERSION_ANDROID={
        (1, 1): {'cap1', 'push:passport_protocol'},
        (1, 2): {'cap2'},
    },
    AM_CAPABILITIES_BY_VERSION_IOS={
        (1, 3): {'cap1', 'push:passport_protocol'},
        (1, 4): {'cap2'},
    },
    AM_SUBSCRIPTION_APP_RULES=[
        ForbidRule(platform='android', app=TEST_APP2),
        ForbidRule(platform='ios', app=TEST_APP3),
    ],
)
class SubscriptionManagerTestCase(PassportTestCase, AmPushesTestMixin):
    def setUp(self):
        self.fake_blackbox = FakeBlackbox()
        self.fake_push_api = FakePushApi()
        self.tvm = FakeTvmCredentialsManager()
        self.tvm.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'blackbox',
                        'ticket': TEST_TICKET,
                    },
                    '2': {
                        'alias': 'push_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.manager = PushesSubscriptionManager(TEST_UID)

        self.patches = [self.fake_blackbox, self.fake_push_api, self.tvm]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

    def setup_blackbox(self, has_trusted_xtokens=True):
        self.fake_blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(
                self.make_xtokens_bundle(has_trusted_xtokens),
            ),
        )

    def setup_push_api(self, subs=None):
        self.fake_push_api.set_response_value(
            'list',
            self.make_subs_bundle() if subs is None else subs,
        )

    def assert_blackbox_ok(self):
        self.assert_blackbox_called([TEST_UID])

    def test_get_trusted_xtokens__ok(self):
        self.setup_blackbox()

        res = self.manager.trusted_xtokens
        assert_that(res, equal_to([
            build_blackbox_oauth_token(token_id=2, login_id=TEST_LOGIN_ID2, device_id=TEST_DEVICE_ID2, is_xtoken_trusted=True),
            build_blackbox_oauth_token(token_id=3, login_id=TEST_LOGIN_ID3, device_id=TEST_DEVICE_ID3, is_xtoken_trusted=True),
            build_blackbox_oauth_token(token_id=5, is_xtoken_trusted=True),
        ]))
        self.assert_blackbox_ok()
        self.assert_list_not_called()

    def test_get_trusted_login_ids__ok(self):
        self.setup_blackbox()

        res = self.manager.trusted_login_ids
        assert_that(res, equal_to({TEST_LOGIN_ID2, TEST_LOGIN_ID3}))
        self.assert_blackbox_ok()
        self.assert_list_not_called()

    def test_get_trusted_device_ids__ok(self):
        self.setup_blackbox()

        res = self.manager.trusted_device_ids
        assert_that(res, equal_to({TEST_DEVICE_ID2, TEST_DEVICE_ID3}))
        self.assert_blackbox_ok()
        self.assert_list_not_called()

    def test_get_subscriptions__ok(self):
        self.setup_blackbox()
        self.setup_push_api()

        res = self.manager.subscriptions

        assert_that(
            res,
            has_subscription_ids([s['id'] for s in self.make_subs_bundle()]),
        )
        self.assert_blackbox_not_called()
        self.assert_list_called([TEST_UID])

    def test_get_trusted_subscriptions__ok(self):
        self.setup_blackbox()
        self.setup_push_api()

        res = self.manager.trusted_subscriptions

        assert_that(res, has_subscription_ids(['s5']), 'res={}'.format(res))
        self.assert_blackbox_ok()
        self.assert_list_called([TEST_UID])

    def test_get_trusted_subscriptions__no_trusted_tokens__push_api_not_called(self):
        self.setup_blackbox(has_trusted_xtokens=False)
        self.setup_push_api()

        res = self.manager.trusted_subscriptions
        assert_that(res, equal_to([]))
        self.assert_blackbox_ok()
        self.assert_list_not_called()

    def test_filter_subscriptions__complex_case__ok(self):
        _s = self._sub_info
        self.setup_push_api([
            _s('s1', am_version=None, platform='fcm'),
            _s('s2', am_version='1.0', platform='fcm'),
            _s('s3', am_version='1.1', platform='fcm', app=TEST_APP2),
            _s('s4', am_version='1.2', platform='fcm'),
            _s('s5', am_version='1.3', platform='fcm', login_id=TEST_LOGIN_ID2, device=TEST_DEVICE_ID2),
            _s('s6', am_version=None, platform='apns'),
            _s('s7', am_version='1.0', platform='apns', device=TEST_DEVICE_ID3),
            _s('s8', am_version='1.1', platform='apns'),
            _s('s9', am_version='1.2', platform='apns'),
            _s('s10', am_version='1.3', platform='apns'),
            _s('s11', am_version='1.4', platform='apns'),
            _s('s11', am_version='1.4', platform='apns'),
            self._autotests_subscription_info('st1'),
            self._autotests_subscription_info('st2'),
        ])

        res = self.manager.filter_subscriptions(
            self.manager.subscriptions,
            filters=[
                CapsFilter(['cap1']),
                PlatformFilter([Platforms.android]),
                BestSubscriptionPerDeviceFilter([TEST_APP1, TEST_APP2]),
            ],
        )
        assert_that(res, has_subscription_ids(['s4', 's5']), 'res: {}'.format(res))
        assert_that(
            self.manager.test_subscriptions,
            has_subscription_ids(['st1', 'st2']),
            'test_subs: {}'.format(self.manager.test_subscriptions),
        )
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()

    def test_get_am_compatible_subscriptions__ok(self):
        self.setup_push_api()

        res = self.manager.am_compatible_subscriptions
        assert_that(
            res,
            has_subscription_ids(['s5', 's10', 's11']),
            'res={}'.format(res),
        )
        self.assert_list_called([TEST_UID])
        self.assert_blackbox_not_called()

    def test_result_caching(self):
        self.setup_push_api()
        self.setup_blackbox()

        _ = self.manager.trusted_xtokens
        _ = self.manager.trusted_xtokens
        _ = self.manager.trusted_device_ids
        _ = self.manager.trusted_device_ids
        _ = self.manager.trusted_login_ids
        _ = self.manager.trusted_login_ids
        _ = self.manager.trusted_subscriptions
        _ = self.manager.trusted_subscriptions
        _ = self.manager.am_compatible_subscriptions
        _ = self.manager.am_compatible_subscriptions
        _ = self.manager.subscriptions
        _ = self.manager.subscriptions
        _ = self.manager.trusted_xtokens
        _ = self.manager.trusted_xtokens
        _ = self.manager.trusted_device_ids
        _ = self.manager.trusted_device_ids
        _ = self.manager.trusted_login_ids
        _ = self.manager.trusted_login_ids

        self.assert_list_called([TEST_UID])
        self.assert_blackbox_ok()
