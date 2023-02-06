# -*- coding: utf-8 -*-

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    equal_to,
    has_entries,
    has_entry,
    has_property,
    instance_of,
)
from passport.backend.core.am_pushes.test.constants import (
    TEST_APP1,
    TEST_APP2,
    TEST_APP3,
    TEST_DEVICE_ID1,
    TEST_DEVICE_ID2,
    TEST_DEVICE_ID3,
    TEST_DEVICE_ID4,
    TEST_LOGIN_ID1,
    TEST_LOGIN_ID2,
    TEST_LOGIN_ID3,
    TEST_LOGIN_ID4,
    TEST_TIMESTAMP1,
)
from passport.backend.core.builders.push_api.faker import (
    push_api_app_subscription_info,
    push_api_subscription_info,
)
from passport.backend.core.builders.push_api.push_api import (
    make_extra_data,
    Subscription,
    subscription_dict_to_obj,
)


def has_subscription_ids(subscription_ids):
    return contains_inanyorder(*[
        all_of(
            instance_of(Subscription),
            has_property('id', sub_id),
        )
        for sub_id in subscription_ids
    ])


class AmPushesTestMixin(object):
    @staticmethod
    def _sub_info(
        id_, device=TEST_DEVICE_ID1, app=TEST_APP1, init_time=TEST_TIMESTAMP1,
        platform='fcm', am_version='1.3', login_id=None,
    ):
        if am_version is not None or login_id is not None:
            extra = make_extra_data(am_version=am_version, login_id=login_id)
        else:
            extra = ''

        return push_api_app_subscription_info(
            id_=id_,
            device=device,
            app=app,
            init_time=init_time,
            last_sent=1607613458,
            uuid='aabbccddeeff112233445566',
            platform=platform,
            extra=extra,
        )

    @staticmethod
    def _autotests_subscription_info(sub_id):
        return push_api_subscription_info(
            id_=sub_id,
            device=None,
            platform=None,
            uuid='123456',
            client='passport_autotests',
        )

    def make_xtokens_bundle(self, has_trusted_xtokens=True):
        return [
            dict(token_id=1, login_id=TEST_LOGIN_ID1, device_id=TEST_DEVICE_ID1, is_xtoken_trusted=False),
            dict(token_id=2, login_id=TEST_LOGIN_ID2, device_id=TEST_DEVICE_ID2, is_xtoken_trusted=has_trusted_xtokens),
            dict(token_id=3, login_id=TEST_LOGIN_ID3, device_id=TEST_DEVICE_ID3, is_xtoken_trusted=has_trusted_xtokens),
            dict(token_id=4, login_id=TEST_LOGIN_ID4, device_id=TEST_DEVICE_ID4, is_xtoken_trusted=False),
            dict(token_id=5, is_xtoken_trusted=has_trusted_xtokens),
        ]

    def make_subs_bundle(self, with_unknown_platform=False, with_unknown_device=False):
        _s = self._sub_info
        res = [
            _s('s1', am_version=None, platform='fcm', login_id=TEST_LOGIN_ID1),
            _s('s2', am_version='1.0', platform='fcm'),
            _s('s3', am_version='1.1', platform='fcm', app=TEST_APP2),
            _s('s4', am_version='1.2', platform='fcm', app=TEST_APP2),
            _s('s5', am_version='1.3', platform='fcm', login_id=TEST_LOGIN_ID2, device=TEST_DEVICE_ID2),
            _s('s6', am_version=None, platform='apns', login_id=TEST_LOGIN_ID3, device=TEST_DEVICE_ID3),
            _s('s7', am_version='1.0', platform='apns', login_id=TEST_LOGIN_ID3, device=TEST_DEVICE_ID3),
            _s('s8', am_version='1.1', platform='apns', app=TEST_APP2),
            _s('s9', am_version='1.2', platform='apns', app=TEST_APP3),
            _s('s10', am_version='1.3', platform='apns', app=None),
            _s('s11', am_version='1.4', platform='apns', login_id=TEST_LOGIN_ID4, device=TEST_DEVICE_ID4),
        ]
        if with_unknown_platform:
            res.append(
                _s('sup1', am_version='1.4', platform='wrong-unknown', login_id=TEST_LOGIN_ID4, device=TEST_DEVICE_ID4),
            )
        if with_unknown_device:
            res.append(
                _s('sud1', am_version='1.4', platform='apns', login_id=TEST_LOGIN_ID4, device=None),
            )
        return res

    def subs_to_parsed_subs(self, subs):
        return [subscription_dict_to_obj(s) for s in subs]

    def make_parsed_subs_bundle(self, with_unknown_platform=False, with_unknown_device=False):
        return self.subs_to_parsed_subs(self.make_subs_bundle(
            with_unknown_platform=with_unknown_platform,
            with_unknown_device=with_unknown_device,
        ))

    def assert_list_called(self, uids):
        assert_that(
            self.fake_push_api.get_requests_by_method('list'),
            contains(*[
                has_property('query_params', has_entry('user', [str(uid)]))
                for uid in uids
            ]),
        )

    def assert_list_not_called(self):
        self.assert_list_called([])

    def assert_blackbox_called(self, uids):
        assert_that(
            self.fake_blackbox.get_requests_by_method('get_oauth_tokens'),
            contains(*[
                has_property('query_params', has_entries(
                    uid=[str(uid)],
                    xtoken_only=['yes'],
                    get_is_xtoken_trusted=['yes'],
                )) for uid in uids
            ]),
        )

    def assert_blackbox_not_called(self):
        assert_that(self.fake_blackbox.get_requests_by_method('get_oauth_tokens'), equal_to([]))
