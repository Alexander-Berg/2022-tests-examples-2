# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    assert_almost_equal,
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.tensornet import get_tensornet
from passport.backend.core.builders.tensornet.exceptions import (
    TensorNetInvalidResponseError,
    TensorNetMissingFeatureError,
    TensorNetTemporaryError,
)
from passport.backend.core.builders.tensornet.faker.tensornet import (
    FakeTensorNet,
    tensornet_eval_response,
)
from passport.backend.core.test.test_utils import with_settings_hosts


TEST_MODEL = ('model', '1')
TEST_ERRONEOUS_PROTOBUF = (
    b'\n\xed\x02\r\x00\x00\xa8A\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x80\xbf\r\x00\x00\x00\x00\r\x00\x00'
    b'\x80?\r\x00\x00\x00@\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00'
    b'\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00'
    b'\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00'
    b'\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x00\x00\r\x00\x00\x80?\r\x00\x00\x80?\r\x00\x00\x00\x00\r\x00\x00\x00'
    b'\x00\r\x00\x00\x00\x00\r\x00'
)
TEST_FEATURES_DESCRIPTION = (
    ('feature1', 'num'),
    ('feature2', 'num'),
    ('feature3', 'categ'),
)
TEST_MODEL_CONFIGS = {
    TEST_MODEL: {
        'timeout': 0.1,
        'retries': 2,
        'features_description': TEST_FEATURES_DESCRIPTION,
    },
}
TEST_REQUEST_PROTOBUF = b'\n\x12\r\x00\x00\x80?\r\x00\x00\x00@\x12\x06banana'


@with_settings_hosts(
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    TENSORNET_API_URL='http://localhost:80/',
)
class TestTensorNetErrorHandling(unittest.TestCase):
    def setUp(self):
        self.tensornet = get_tensornet(TEST_MODEL)
        self.tensornet.useragent = mock.Mock()

        self.response = mock.Mock()
        self.tensornet.useragent.request.return_value = self.response
        self.tensornet.useragent.request_error_class = self.tensornet.temporary_error_class

    def tearDown(self):
        del self.tensornet
        del self.response

    @raises(TensorNetTemporaryError)
    def test_bad_status_code_response(self):
        self.response.status_code = 501
        self.response.content = TEST_ERRONEOUS_PROTOBUF

        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
        })

    @raises(TensorNetTemporaryError)
    def test_bad_status_code_response_with_empty_content(self):
        self.response.status_code = 501
        self.response.content = ''

        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
        })

    @raises(TensorNetInvalidResponseError)
    def test_invalid_protobuf_response_error(self):
        self.response.content = TEST_ERRONEOUS_PROTOBUF
        self.response.status_code = 200

        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
            'feature3': 'banana',
        })

    @raises(ValueError)
    def test_non_serializable_num_feature_error(self):
        self.tensornet.eval({
            'feature1': '\xff\xfd',
            'feature2': 2,
            'feature3': 'banana',
        })

    @raises(TensorNetMissingFeatureError)
    def test_missing_features_error(self):
        self.tensornet.eval({
            'feature1': 1,
            'feature2': 2,
        })

    def test_default_initialization(self):
        tensornet = get_tensornet(TEST_MODEL)
        ok_(tensornet.useragent is not None)
        eq_(tensornet.url, 'http://localhost:80/')
        eq_(tensornet.model_name, 'model')
        eq_(tensornet.model_version, '1')
        eq_(tensornet.features_description, TEST_FEATURES_DESCRIPTION)


@with_settings_hosts(
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    TENSORNET_API_URL='http://localhost:80/',
)
class TestTensorNetEval(unittest.TestCase):
    def setUp(self):
        self.tensornet = get_tensornet(TEST_MODEL)
        self.faker = FakeTensorNet()
        self.faker.start()

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
        eq_(len(self.faker.requests), 1)
        request = self.faker.requests[0]
        request.assert_properties_equal(
            method='POST',
            url='http://localhost:80/model/1/eval',
        )
        eq_(request.post_args, TEST_REQUEST_PROTOBUF)

    def test_error_response(self):
        self.faker.set_tensornet_response_side_effect(TensorNetTemporaryError)

        with assert_raises(TensorNetTemporaryError):
            self.tensornet.eval({
                'feature1': 1,
                'feature2': 2,
                'feature3': 'banana',
                'feature4': 100500,
            })

        eq_(len(self.faker.requests), 2)
        request = self.faker.requests[0]
        request.assert_properties_equal(
            method='POST',
            url='http://localhost:80/model/1/eval',
        )
        eq_(request.post_args, TEST_REQUEST_PROTOBUF)

    def test_empty_target_response(self):
        self.faker.set_tensornet_response_value(tensornet_eval_response(None))

        with assert_raises(TensorNetInvalidResponseError):
            self.tensornet.eval({
                'feature1': 1,
                'feature2': 2,
                'feature3': 'banana',
                'feature4': 100500,
            })
