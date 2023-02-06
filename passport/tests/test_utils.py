# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from nose.tools import eq_
from passport.backend.core.avatars.utils import get_avatar_mds_key
from passport.backend.core.test.test_utils import PassportTestCase


TEST_UID = 123456789

TEST_RANDINT_VALUE = 0
TEST_DATETIME_NOW_VALUE = datetime(2017, 7, 14, 5, 40)
# passport.backend.core.avatars.utils.get_avatar_mds_key возвращает такую строчку,
# если замокать randint и datetime.now значениями выше
TEST_AVATAR_KEY = '6vh7Xyxc6wM8pK7XOthOjJrvw8-1'


class TestGetMdsKey(PassportTestCase):
    def setUp(self):
        super(TestGetMdsKey, self).setUp()
        patch_random = mock.patch(
            'passport.backend.core.avatars.utils.randint',
            mock.Mock(return_value=TEST_RANDINT_VALUE),
        )
        patch_datetime = mock.patch(
            'passport.backend.core.avatars.utils.datetime',
            mock.Mock(now=mock.Mock(return_value=TEST_DATETIME_NOW_VALUE)),
        )

        self.patches = [
            patch_random,
            patch_datetime,
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        super(TestGetMdsKey, self).tearDown()

    def test_ok(self):
        eq_(
            get_avatar_mds_key(TEST_UID),
            TEST_AVATAR_KEY,
        )
