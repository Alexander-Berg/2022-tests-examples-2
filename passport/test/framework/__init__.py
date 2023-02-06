# -*- coding: utf-8 -*-
from passport.backend.oauth.core.test.framework.base import YandexAwareClient
from passport.backend.oauth.core.test.framework.testcases import (
    ApiTestCase,
    BaseTestCase,
    BundleApiTestCase,
    DBTestCase,
    FormTestCase,
    ManagementCommandTestCase,
    PatchesMixin,
    TEST_TVM_TICKET,
)


__all__ = (
    'ApiTestCase',
    'BaseTestCase',
    'BundleApiTestCase',
    'DBTestCase',
    'FormTestCase',
    'ManagementCommandTestCase',
    'PatchesMixin',
    'TEST_TVM_TICKET',
    'YandexAwareClient',
)
