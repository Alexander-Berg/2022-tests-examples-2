# -*- coding: utf-8 -*-

from django.test.utils import override_settings
from passport.backend.oauth.core.test.base_test_data import TEST_CIPHER_KEYS
from passport.backend.oauth.core.test.framework.testcases.management_command_testcase import ManagementCommandTestCase
from passport.backend.oauth.tvm_api.tests.base import TEST_ROBOT_UID


@override_settings(
    ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS,
    ABC_ROBOT_UID=TEST_ROBOT_UID,
    STAFF_URL='api.staff.yandex.net',
    STAFF_TIMEOUT=1.0,
    STAFF_RETRIES=1,
    ABC_URL='api.abc.yandex.net',
    ABC_TIMEOUT=1.0,
    ABC_RETRIES=1,
)
class BaseTVMManagementCommandTestCase(ManagementCommandTestCase):
    pass
