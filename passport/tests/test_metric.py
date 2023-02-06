# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.env_profile import (
    EnvDistance,
    EnvProfileV1,
)
from passport.backend.core.env_profile.metric import Basic3x3CaseMetric
from passport.backend.core.env_profile.tests.base_test_data import UATRAITS_SETTINGS
from passport.backend.core.test.test_utils import with_settings


@with_settings(**UATRAITS_SETTINGS)
class TestBasic3x3CaseMetric(unittest.TestCase):
    def setUp(self):
        self.metric = Basic3x3CaseMetric

    def test_compare(self):
        test_items = (
            ({}, {}, EnvDistance.High),
            ({'AS_list': ['1']}, {}, EnvDistance.High),
            ({'AS_list': ['1']}, {'AS_list': ['1']}, (EnvDistance.Low + EnvDistance.High) / 2),
            ({'country_id': 1}, {'country_id': 1, 'AS_list': ['1']}, (EnvDistance.Low + EnvDistance.High) / 2),
            ({'AS_list': ['1'], 'country_id': 1}, {'country_id': 1}, (EnvDistance.Medium + EnvDistance.High) / 2),
            ({'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3}, {}, EnvDistance.High),
            (
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3},
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3},
                (EnvDistance.High + EnvDistance.Low) / 2,
            ),
            (
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 30},
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3},
                (EnvDistance.High + EnvDistance.Moderate) / 2,
            ),
            (
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3},
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 30},
                EnvDistance.High,
            ),
            (
                {'AS_list': ['1'], 'is_mobile': 1},
                {'AS_list': ['1'], 'is_mobile': 1},
                # low потому что одинаковые AS, moderate потому что mobile
                EnvDistance.Low,
            ),
            (
                {'AS_list': ['1'], 'is_mobile': 0},
                {'AS_list': ['1'], 'is_mobile': 1},
                # low потому что одинаковые AS, moderate потому что mobile
                EnvDistance.Low,
            ),
            (
                {'AS_list': ['1'], 'is_mobile': 1},
                {'AS_list': ['1'], 'is_mobile': 0},
                # low потому что одинаковые AS, moderate потому что mobile
                EnvDistance.Low,
            ),
            (
                {'AS_list': ['1'], 'is_mobile': 1},
                {'AS_list': ['2'], 'is_mobile': 1},
                # high, потому что AS различаются
                EnvDistance.High,
            ),
            (
                {'browser_id': 1, 'os_id': 2, 'yandexuid_timestamp': 3, 'is_mobile': 1},
                {'is_mobile': '1'},
                # high потому что нету AS
                EnvDistance.High,
            )
        )

        for new, old, distance in test_items:
            eq_(self.metric.distance(EnvProfileV1(**new), EnvProfileV1(**old)), distance)
