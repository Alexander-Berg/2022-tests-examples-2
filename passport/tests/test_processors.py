# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

import mock
from nose.tools import eq_
from passport.backend.core.serializers.eav.processors import (
    as_is_processor,
    billing_features_processor,
    boolean_processor,
    datetime_processor,
    default_processor,
    JoinProcessors,
    plus_subscriber_state_processor,
    unary_field_processor,
)
from passport.backend.core.test.consts import (
    TEST_PLUS_SUBSCRIBER_STATE1_JSON,
    TEST_PLUS_SUBSCRIBER_STATE1_PROTO,
)
from passport.protobuf.billing_features.billing_features_pb2 import (
    BillingFeatures,
    FeatureAttributes,
)


class TestCommonProcessors(unittest.TestCase):
    def test_as_is_processor(self):
        eq_(as_is_processor(None), None)
        eq_(as_is_processor(0), 0)
        eq_(as_is_processor(''), '')
        eq_(as_is_processor('bla'), 'bla')

    def test_default_processor(self):
        eq_(default_processor(''), None)
        eq_(default_processor(None), None)
        eq_(default_processor(0), 0)
        eq_(default_processor('bla'), 'bla')

    def test_join_processor(self):
        p1 = mock.Mock()
        p1.return_value = 'value1'
        p2 = mock.Mock()
        p2.return_value = 'value2'

        eq_(JoinProcessors([p1])(p2)('value0'), 'value2')
        eq_(p1.call_count, 1)
        eq_(p2.call_count, 1)

        p1.assert_called_with('value0')
        p2.assert_called_with('value1')

    def test_join_processor_on_stop(self):
        p1 = mock.Mock()
        p1.return_value = 'stop_on'
        p2 = mock.Mock()
        p2.return_value = 'no_execute'

        eq_(JoinProcessors([p1], 'stop_on')(p2)('value0'), 'stop_on')

        eq_(p1.call_count, 1)
        p1.assert_called_with('value0')

        eq_(p2.call_count, 0)

    def test_boolean_processor(self):
        eq_(boolean_processor(True), '1')
        eq_(boolean_processor(False), None)
        eq_(boolean_processor(0), None)
        eq_(boolean_processor(1), '1')
        eq_(boolean_processor('1'), '1')
        eq_(boolean_processor('0'), None)

    def test_unary_field_processor(self):
        eq_(unary_field_processor(None), None)
        eq_(unary_field_processor(0), None)
        eq_(unary_field_processor(False), None)
        eq_(unary_field_processor(True), '1')
        eq_(unary_field_processor(1), '1')

    def test_datetime_processor(self):
        eq_(datetime_processor(None), None)
        eq_(datetime_processor(''), None)
        eq_(datetime_processor(datetime.fromtimestamp(0)), None)
        eq_(datetime_processor(datetime.fromtimestamp(1)), None)
        eq_(datetime_processor(datetime.fromtimestamp(2)), 2)

    def test_billing_features_processor(self):
        eq_(billing_features_processor(None), None)
        eq_(billing_features_processor(''), None)
        eq_(billing_features_processor({}), None)

        bf_str = billing_features_processor(
            {
                '100% cashback': {
                    'in_trial': True,
                    'paid_trial': False,
                    'region_id': 0,
                    'trial_duration': 0,
                    'brand': 'brand',
                },
                'Music_Premium': {
                    'region_id': 9999,
                },
                'Passport': {},
            },
        )
        bf = BillingFeatures()
        bf.ParseFromString(bf_str)
        eq_(
            set([k for k in bf.Features]),
            set(['Music_Premium', 'Passport', '100% cashback']),
        )
        eq_(
            bf.Features['Passport'],
            FeatureAttributes(),
        )
        eq_(
            bf.Features['100% cashback'],
            FeatureAttributes(
                InTrial=True,
                PaidTrial=False,
                RegionId=0,
                TrialDuration=0,
                Brand='brand',
            ),
        )
        eq_(
            bf.Features['Music_Premium'],
            FeatureAttributes(
                RegionId=9999,
            ),
        )

    def test_plus_subscriber_state_processor(self):
        eq_(plus_subscriber_state_processor(None), None)
        eq_(plus_subscriber_state_processor(''), None)
        eq_(plus_subscriber_state_processor({}), None)
        eq_(plus_subscriber_state_processor(TEST_PLUS_SUBSCRIBER_STATE1_JSON), TEST_PLUS_SUBSCRIBER_STATE1_PROTO)
