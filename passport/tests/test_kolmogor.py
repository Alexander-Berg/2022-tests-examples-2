# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.kolmogor import (
    Kolmogor,
    KolmogorBadRequestError,
    KolmogorPermanentError,
    KolmogorTemporaryError,
)
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.test.test_utils import with_settings


TEST_SPACE = 'keyspace'
TEST_KEYS = ['key1', 'key2']
TEST_SERVICE_TICKET = 'service-ticket'


@with_settings(
    KOLMOGOR_URL='http://localhost/',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=2,
)
class TestKolmogorCommon(unittest.TestCase):
    def setUp(self):
        self.kolmogor = Kolmogor()
        self.kolmogor.useragent = mock.Mock()

        self.response = mock.Mock()
        self.kolmogor.useragent.request_error_class = KolmogorTemporaryError
        self.kolmogor.useragent.request.return_value = self.response
        self.response.content = b'OK'
        self.response.status_code = 200

    def tearDown(self):
        del self.kolmogor
        del self.response

    def test_bad_request(self):
        self.response.status_code = 400
        self.response.content = b'Error:keys arg is empty'
        with assert_raises(KolmogorBadRequestError):
            self.kolmogor.get(TEST_SPACE, [])

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'server is down'
        with assert_raises(KolmogorPermanentError):
            self.kolmogor.get(TEST_SPACE, TEST_KEYS)


@with_settings(
    KOLMOGOR_URL='http://localhost/',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=2,
)
class TestKolmogorMethods(unittest.TestCase):
    def setUp(self):
        self.fake_kolmogor = FakeKolmogor()
        self.fake_kolmogor.start()
        self.fake_kolmogor.set_response_value('get', b'0,0')
        self.fake_kolmogor.set_response_value('inc', b'OK')
        self.kolmogor = Kolmogor()

    def tearDown(self):
        self.fake_kolmogor.stop()
        del self.fake_kolmogor

    def test_get_ok(self):
        response = self.kolmogor.get(TEST_SPACE, TEST_KEYS)
        eq_(
            response,
            {'key1': 0, 'key2': 0},
        )
        self.fake_kolmogor.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/get?space=%s&keys=key1,key2' % TEST_SPACE,
            headers=None,
        )

    def test_get_dict(self):
        self.fake_kolmogor.set_response_value('get', {'c': 1, 'b': 2, 'a': 3})
        response = self.kolmogor.get(TEST_SPACE, ['c', 'a', 'b'])
        eq_(
            response,
            {'a': 3, 'b': 2, 'c': 1},
        )
        self.fake_kolmogor.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/get?space=%s&keys=a,b,c' % TEST_SPACE,
            headers=None,
        )

    def test_dist_side_effect(self):
        self.fake_kolmogor.set_response_side_effect('get', [{'c': 1, 'b': 2, 'a': 3}, {'d': 4}])
        response = self.kolmogor.get(TEST_SPACE, ['c', 'a', 'b'])
        eq_(
            response,
            {'a': 3, 'b': 2, 'c': 1},
        )
        self.fake_kolmogor.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/get?space=%s&keys=a,b,c' % TEST_SPACE,
            headers=None,
        )
        response = self.kolmogor.get(TEST_SPACE, ['d'])
        eq_(
            response,
            {'d': 4},
        )
        self.fake_kolmogor.requests[-1].assert_properties_equal(
            method='GET',
            url='http://localhost/get?space=%s&keys=d' % TEST_SPACE,
            headers=None,
        )

    def test_side_effect_error(self):
        self.fake_kolmogor.set_response_side_effect('get', KolmogorPermanentError)
        with assert_raises(KolmogorPermanentError):
            self.kolmogor.get(TEST_SPACE, TEST_KEYS)

    def test_get_bad_kolmogor_reponse(self):
        # Колмогор отдал меньше значений, чем мы запросили
        self.fake_kolmogor.set_response_value('get', b'0')
        with assert_raises(KolmogorPermanentError):
            self.kolmogor.get(TEST_SPACE, TEST_KEYS)

    def test_inc_ok(self):
        response = self.kolmogor.inc(TEST_SPACE, TEST_KEYS)
        ok_(response is None)
        self.fake_kolmogor.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/inc',
            post_args=dict(
                space=TEST_SPACE,
                keys='key1,key2',
            ),
            headers=None,
        )

    def test_with_tvm_ok(self):
        tvm_mock = mock.Mock()
        tvm_mock.get_ticket_by_alias.return_value = TEST_SERVICE_TICKET
        kolmogor = Kolmogor(use_tvm=True, tvm_credentials_manager=tvm_mock)

        response = kolmogor.get(TEST_SPACE, TEST_KEYS)
        eq_(
            response,
            {'key1': 0, 'key2': 0},
        )
        self.fake_kolmogor.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/get?space=%s&keys=key1,key2' % TEST_SPACE,
            headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        )
