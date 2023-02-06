# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.collections import (
    CollectionsApi,
    CollectionsApiInvalidResponseError,
    CollectionsApiPermanentError,
)
from passport.backend.core.builders.collections.faker.fake_collections_api import (
    collections_successful_response,
    FakeCollectionsApi,
    pictures_successful_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_PUBLIC_ID = 'test-normalized-public-id'


@with_settings(
    COLLECTIONS_API_URL='http://collections-api/',
    COLLECTIONS_API_TIMEOUT=0.5,
    COLLECTIONS_API_RETRIES=2,
)
class FakeCollectionsApiTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_collections_api = FakeCollectionsApi()
        self.fake_collections_api.start()

    def tearDown(self):
        self.fake_collections_api.stop()
        del self.fake_collections_api

    def test_set_response_side_effect(self):
        ok_(not self.fake_collections_api._mock.request.called)

        builder = CollectionsApi()
        self.fake_collections_api.set_response_side_effect(
            'collections',
            CollectionsApiInvalidResponseError,
        )
        with assert_raises(CollectionsApiPermanentError):
            builder.collections(public_id=TEST_PUBLIC_ID)
        assert_builder_requested(self.fake_collections_api, times=1)

    def test_set_collections_response_value(self):
        ok_(not self.fake_collections_api._mock.request.called)

        builder = CollectionsApi()
        self.fake_collections_api.set_response_value(
            'collections',
            collections_successful_response(),
        )
        result = builder.collections(public_id=TEST_PUBLIC_ID)
        eq_(result, json.loads(collections_successful_response())['results'])
        assert_builder_requested(self.fake_collections_api, times=1)

    def test_set_pictures_response(self):
        ok_(not self.fake_collections_api._mock.request.called)

        builder = CollectionsApi()
        self.fake_collections_api.set_response_value(
            'pictures',
            pictures_successful_response(),
        )
        result = builder.pictures(public_id=TEST_PUBLIC_ID)
        eq_(result, json.loads(pictures_successful_response())['results'])
        assert_builder_requested(self.fake_collections_api, times=1)
