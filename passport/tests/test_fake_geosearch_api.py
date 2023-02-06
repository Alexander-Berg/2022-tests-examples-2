# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.geosearch import (
    GeoSearchApi,
    GeoSearchApiPermanentError,
)
from passport.backend.core.builders.geosearch.faker import (
    FakeGeoSearchApi,
    geosearch_response_geo,
    geosearch_response_geo_parsed,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)


TEST_URI = 'ymapsbm1://geo?text=leningradka&ll=37.536733%2C55.682336&spn=0.432587%2C0.095074'
TEST_SERVICE_TICKET = 'service-ticket'


@with_settings(
    GEOSEARCH_API_URL='http://localhost',
    GEOSEARCH_API_TIMEOUT=1,
    GEOSEARCH_API_RETRIES=1,
)
class FakeGeoSearchTestCase(TestCase):
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

        self.faker = FakeGeoSearchApi()
        self.faker.start()
        self.geosearch = GeoSearchApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.geosearch
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_get_info_ok(self):
        self.faker.set_response_value('get_info', geosearch_response_geo())
        eq_(self.geosearch.get_info(TEST_URI, lang='en'), geosearch_response_geo_parsed())
        assert_builder_requested(self.faker, 1)

    @raises(GeoSearchApiPermanentError)
    def test_get_info_error(self):
        self.faker.set_response_side_effect('get_info', GeoSearchApiPermanentError)
        self.geosearch.get_info(TEST_URI)
