# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.geosearch import (
    GeoSearchApi,
    GeoSearchApiPermanentError,
)
from passport.backend.core.builders.geosearch.faker import (
    empty_response,
    FakeGeoSearchApi,
    geosearch_response_geo,
    geosearch_response_geo_parsed,
    geosearch_response_org,
    geosearch_response_org_parsed,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)
from requests import Response


TEST_SERVICE_TICKET = 'service-ticket'
TEST_URI_GEO = 'ymapsbm1://geo?text=leningradka&ll=37.536733,55.682336&spn=0.432587,0.095074'
TEST_URI_ORG = 'ymapsbm1://org?oid=1'
TEST_URI_PIN = 'ymapsbm1://pin?ll=37.586926,55.734042'


@with_settings(
    GEOSEARCH_API_URL='http://localhost',
    GEOSEARCH_API_TIMEOUT=1,
    GEOSEARCH_API_RETRIES=2,
)
class TestGeoSearchCommon(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'geosearch_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.geosearch = GeoSearchApi()
        self.geosearch.useragent = mock.Mock()

        self.response = mock.create_autospec(Response)
        self.geosearch.useragent.request.return_value = self.response
        self.geosearch.useragent.request_error_class = self.geosearch.temporary_error_class
        self.response.content = empty_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.geosearch
        del self.response
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_ok(self):
        eq_(self.geosearch.get_info(TEST_URI_GEO), {})

    def test_no_items(self):
        self.response.content = b'{}'
        with assert_raises(GeoSearchApiPermanentError):
            self.geosearch.get_info(TEST_URI_GEO)

    def test_bad_request(self):
        self.response.status_code = 400
        self.response.content = b'not protobuf'
        with assert_raises(GeoSearchApiPermanentError):
            self.geosearch.get_info(TEST_URI_GEO)

    def test_server_error(self):
        self.response.status_code = 500
        with assert_raises(GeoSearchApiPermanentError):
            self.geosearch.get_info(TEST_URI_ORG)


@with_settings(
    GEOSEARCH_API_URL='http://localhost',
    GEOSEARCH_API_TIMEOUT=1,
    GEOSEARCH_API_RETRIES=2,
)
class TestEdadealMethods(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'geosearch_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_geosearch = FakeGeoSearchApi()
        self.fake_geosearch.start()
        self.fake_geosearch.set_response_value('get_info', geosearch_response_geo())
        self.geosearch = GeoSearchApi()

    def tearDown(self):
        self.fake_geosearch.stop()
        del self.fake_geosearch
        del self.geosearch
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_unknown_type__ok(self):
        response = self.geosearch.get_info('ymapsbm1://new?ll=1.0,1.2')
        ok_(not response)
        ok_(not self.fake_geosearch.requests)

    def test_empty_ok(self):
        self.fake_geosearch.set_response_value('get_info', empty_response())
        response = self.geosearch.get_info(TEST_URI_ORG)
        ok_(not response)

    def test_get_info_dont_parse_protobuf__ok(self):
        self.fake_geosearch.set_response_value('get_info', geosearch_response_org())
        response = self.geosearch.get_info(TEST_URI_ORG, parse_protobuf=False)
        assert response == geosearch_response_org()
        self.fake_geosearch.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost?'
                'ms=pb&'
                'origin=maps-passport&'
                'lang=ru&'
                'mode=uri&'
                'type=biz,geo&'
                'uri=ymapsbm1%253A%252F%252Forg%253Foid%253D1&'
                'snippets=businessrating/1.x,photos/2.x',
        )

    def test_get_info_org__ok(self):
        self.fake_geosearch.set_response_value('get_info', geosearch_response_org())
        response = self.geosearch.get_info(TEST_URI_ORG)
        eq_(response, geosearch_response_org_parsed())
        self.fake_geosearch.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost?'
                'ms=pb&'
                'origin=maps-passport&'
                'lang=ru&'
                'mode=uri&'
                'type=biz,geo&'
                'uri=ymapsbm1%253A%252F%252Forg%253Foid%253D1&'
                'snippets=businessrating/1.x,photos/2.x',
        )

    def test_get_info_geo_ok(self):
        response = self.geosearch.get_info(TEST_URI_GEO, lang='en')
        eq_(response, geosearch_response_geo_parsed())
        self.fake_geosearch.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost?'
                'ms=pb&'
                'origin=maps-passport&'
                'lang=en&'
                'mode=uri&'
                'type=biz,geo&'
                'uri=ymapsbm1%253A%252F%252Fgeo%253Ftext%253Dleningradka%2526ll%253D37.536733%252C55.682336%2526spn%253D0.432587%252C0.095074&'
                'snippets=businessrating/1.x,photos/2.x',
        )

    def test_get_info_error(self):
        self.fake_geosearch.set_response_value('get_info', '{message: "everything is wrong"}', status=500)
        with assert_raises(GeoSearchApiPermanentError):
            self.geosearch.get_info(TEST_URI_ORG)
