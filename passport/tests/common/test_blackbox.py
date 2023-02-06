# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.oauth.core.common.blackbox import get_blackbox
from passport.backend.oauth.core.common.blackbox_helpers import (
    get_login_or_uid_by_uid,
    get_uid_by_login_or_uid,
    try_convert_uids_to_logins,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ANOTHER_LOGIN,
    TEST_ANOTHER_UID,
    TEST_LOGIN,
    TEST_REMOTE_ADDR,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework import (
    BaseTestCase,
    PatchesMixin,
    TEST_TVM_TICKET,
)


TEST_NORMALIZED_LOGIN = TEST_LOGIN.replace('.', '-')
TEST_USER_IP = TEST_REMOTE_ADDR


class BaseBlackboxTestcase(BaseTestCase, PatchesMixin):
    def setUp(self):
        super(BaseBlackboxTestcase, self).setUp()
        self.patch_environment()
        self.patch_tvm_credentials_manager()

    def tearDown(self):
        self.stop_patches()
        super(BaseBlackboxTestcase, self).tearDown()


class TestBlackbox(BaseBlackboxTestcase):
    def test_tvm_used(self):
        get_blackbox().userinfo(TEST_UID, TEST_USER_IP)
        self.fake_blackbox.requests[0].assert_properties_equal(
            headers={'X-Ya-Service-Ticket': TEST_TVM_TICKET},
        )


class TestGetLoginOrUidByUid(BaseBlackboxTestcase):
    def test_ok(self):
        eq_(get_login_or_uid_by_uid(TEST_UID), TEST_NORMALIZED_LOGIN)

    def test_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None, login=None),
        )
        eq_(get_login_or_uid_by_uid(TEST_UID), TEST_UID)

    def test_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        eq_(get_login_or_uid_by_uid(TEST_UID), TEST_UID)


class TestGetUidByLoginOrUid(BaseBlackboxTestcase):
    def test_ok_by_uid(self):
        eq_(get_uid_by_login_or_uid(TEST_UID), TEST_UID)

    def test_ok_by_login(self):
        eq_(get_uid_by_login_or_uid(TEST_LOGIN), TEST_UID)

    def test_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        ok_(get_uid_by_login_or_uid(TEST_LOGIN) is None)

    def test_negative_uid_not_accepted(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        ok_(get_uid_by_login_or_uid(-1) is None)

    def test_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        ok_(get_uid_by_login_or_uid(TEST_LOGIN) is None)


class TestTryConvertUidsToLogins(BaseBlackboxTestcase):
    def setUp(self):
        super(TestTryConvertUidsToLogins, self).setUp()
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': TEST_UID, 'id': TEST_UID, 'login': TEST_LOGIN},
                {'uid': TEST_ANOTHER_UID, 'id': TEST_ANOTHER_UID, 'login': TEST_ANOTHER_LOGIN},
            ]),
        )

    def test_ok(self):
        eq_(
            try_convert_uids_to_logins([TEST_UID, TEST_ANOTHER_LOGIN]),
            {
                TEST_UID: TEST_LOGIN,
                TEST_ANOTHER_UID: TEST_ANOTHER_LOGIN,
            },
        )

    def test_empty(self):
        eq_(
            try_convert_uids_to_logins([]),
            {},
        )
        eq_(len(self.fake_blackbox.requests), 0)

    def test_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response_multiple([
                {'uid': TEST_UID, 'id': TEST_UID, 'login': TEST_LOGIN},
                {'uid': None, 'id': TEST_ANOTHER_UID, 'login': None},
            ]),
        )
        eq_(
            try_convert_uids_to_logins([TEST_UID, TEST_ANOTHER_LOGIN]),
            {
                TEST_UID: TEST_LOGIN,
                TEST_ANOTHER_UID: str(TEST_ANOTHER_UID),
            },
        )

    def test_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        eq_(
            try_convert_uids_to_logins([TEST_UID, TEST_ANOTHER_UID]),
            {
                TEST_UID: str(TEST_UID),
                TEST_ANOTHER_UID: str(TEST_ANOTHER_UID),
            },
        )
