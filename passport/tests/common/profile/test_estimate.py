# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.api.common.profile.estimate import estimate
from passport.backend.core.builders.tensornet.faker.tensornet import (
    FakeTensorNet,
    tensornet_eval_response,
)
from passport.backend.core.env_profile.helpers import make_profile_from_raw_data
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)


TEST_MODEL_1 = ('profile', '1')
TEST_MODEL_2 = ('profile', '2')


@with_settings_hosts()
class EstimateExperimentTestCase(unittest.TestCase):
    def setUp(self):
        self.tensornet = FakeTensorNet()
        self.tensornet.start()

    def tearDown(self):
        self.tensornet.stop()
        del self.tensornet

    def test_estimate_experiment_selection(self):
        self.tensornet.set_tensornet_response_value(tensornet_eval_response(0.5))

        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})
        full_profile = {}
        with settings_context(
            TENSORNET_API_URL='http://tensornet',
            TENSORNET_MODEL_CONFIGS={
                TEST_MODEL_2: {
                    'timeout': 0.03,
                    'retries': 2,
                    'features_description': [],
                    'denominator': 40,  # Модель на 3%
                    'threshold': 0.5,
                    'features_builder_version': 2,
                },
                TEST_MODEL_1: {
                    'timeout': 0.03,
                    'retries': 2,
                    'features_description': [],
                    'denominator': 20,  # Эта модель на 5% - 3% = 2%
                    'threshold': 0.5,
                    'features_builder_version': 2,
                },
            },
        ):
            estimate(20, fresh_profile=fresh_profile, full_profile=full_profile)  # попадает в модель 1
            estimate(40, fresh_profile=fresh_profile, full_profile=full_profile)  # попадает в модель 2
            estimate(41, fresh_profile=fresh_profile, full_profile=full_profile)  # попадает в модель 1 по умолчанию

        requests = self.tensornet.requests
        eq_(len(requests), 3)

        requests[0].assert_properties_equal(
            method='POST',
            url='http://tensornet/%s/%s/eval' % TEST_MODEL_1,
        )
        requests[1].assert_properties_equal(
            method='POST',
            url='http://tensornet/%s/%s/eval' % TEST_MODEL_2,
        )
        requests[2].assert_properties_equal(
            method='POST',
            url='http://tensornet/%s/%s/eval' % TEST_MODEL_1,
        )
