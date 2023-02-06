# -*- coding: utf-8 -*-

import os


FUNCTION_TESTS_PREFIX = os.path.join("portal", "main", "function_tests")
KOTE_PREFIX = os.path.join(FUNCTION_TESTS_PREFIX, "tests", "kote")
KOTE_CLIENTS_PREFIX = os.path.join(KOTE_PREFIX, "clients")
KOTE_TESTS_PREFIX = os.path.join(KOTE_PREFIX, "tests")
KOTE_SELF_TESTS_PREFIX = os.path.join(KOTE_TESTS_PREFIX, "framework_test")
KOTE_MOCK_PREFIX = os.path.join(KOTE_SELF_TESTS_PREFIX, "mocks")
