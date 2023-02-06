# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_almost_equal,
    eq_,
    raises,
)
from passport.backend.core.builders.tensornet import get_tensornet
from passport.backend.core.builders.tensornet.exceptions import (
    TensorNetInvalidResponseError,
    TensorNetTemporaryError,
)
from passport.backend.core.builders.tensornet.faker.tensornet import (
    FakeLocalTensorNet,
    FakeTensorNet,
    tensornet_eval_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts


TEST_MODEL = ('model', '1')


@with_settings_hosts(
    TENSORNET_MODEL_CONFIGS={
        TEST_MODEL: {
            'timeout': 0.1,
            'retries': 1,
            'features_description': (
                ('feature1', 'num'),
                ('feature2', 'num'),
                ('feature3', 'categ'),
            ),
        },
    },
    TENSORNET_API_URL='http://localhost:80/',
)
class TestFakeTensorNet(unittest.TestCase):
    def setUp(self):
        self.faker = FakeTensorNet()
        self.faker.start()
        self.tensornet = get_tensornet(TEST_MODEL)

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_ok_response(self):
        self.faker.set_tensornet_response_value(tensornet_eval_response(0.99))

        score = self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
            'feature4': 100500,
        })

        assert_almost_equal(score, 0.99, places=5)

    @raises(TensorNetTemporaryError)
    def test_error_response(self):
        self.faker.set_tensornet_response_side_effect(TensorNetTemporaryError)

        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
        })

    @raises(TensorNetInvalidResponseError)
    def test_invalid_protobuf_response_error(self):
        self.faker.set_tensornet_response_value(
            '\n\xed\x02\r\x00\x00\xa8A\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x80\xbf\r\x00\x00\x00\x00'
            '\r\x00\x00\x80?\r\x00\x00\x00@\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00'
            '\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r'
            '\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00'
            '\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00'
            '\x80?\r\x00\x00\x80?\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00'
        )

        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
        })


class TestFakeLocalTensorNet(unittest.TestCase):
    def setUp(self):
        self.tensornet = FakeLocalTensorNet('passport.backend.core.builders.tensornet.tensornet.TensorNet')
        self.tensornet.start()

    def tearDown(self):
        self.tensornet.stop()
        del self.tensornet

    def test_set_predict_result_works(self):
        self.tensornet.set_predict_return_value(0.5)

        eq_(get_tensornet(None).predict([1, 2, 3]), 0.5)
        eq_(self.tensornet.predict_call_count, 1)

    @raises(ValueError)
    def test_set_predict_side_effect_works(self):
        self.tensornet.set_predict_side_effect(ValueError)

        get_tensornet(None).predict([1, 2, 3])
