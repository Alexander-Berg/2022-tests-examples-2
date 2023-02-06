# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.datasync_api.exceptions import (
    DatasyncAccountInvalidTypeError,
    DatasyncApiAuthorizationInvalidError,
    DatasyncApiObjectNotFoundError,
    DatasyncApiPermanentError,
    DatasyncApiTemporaryError,
    DatasyncUserBlockedError,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import (
    error_response,
    FakePersonalityApi,
    maps_bookmarks_response,
    passport_external_data_batch_error,
    passport_external_data_batch_item,
    passport_external_data_batch_response,
    passport_external_data_item,
    passport_external_data_response,
    passport_external_data_response_multi,
    video_favorites_successful_response,
)
from passport.backend.core.builders.datasync_api.personality_api import PersonalityApi
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)


TEST_UID = 123


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class TestPersonalityApiCommon(unittest.TestCase):
    def setUp(self):
        self.personality_api = PersonalityApi(tvm_credentials_manager=mock.Mock())
        self.personality_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.personality_api.useragent.request.return_value = self.response
        self.personality_api.useragent.request_error_class = self.personality_api.temporary_error_class
        self.response.status_code = 200

    def tearDown(self):
        del self.personality_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = 'not a json'
        with assert_raises(DatasyncApiPermanentError):
            self.personality_api.video_favorites(uid=TEST_UID)

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = error_response('ServerError')
        with assert_raises(DatasyncApiPermanentError):
            self.personality_api.video_favorites(uid=TEST_UID)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = error_response('IAmATeapot')
        with assert_raises(DatasyncApiPermanentError):
            self.personality_api.video_favorites(uid=TEST_UID)

    def test_unauthorized_error(self):
        self.response.status_code = 403
        self.response.content = error_response('UnauthorizedError')
        with assert_raises(DatasyncApiAuthorizationInvalidError):
            self.personality_api.video_favorites(uid=TEST_UID)

    def test_object_not_found_error(self):
        self.response.status_code = 404
        self.response.content = error_response('NotFound')
        with assert_raises(DatasyncApiObjectNotFoundError):
            self.personality_api.passport_external_data_get(uid=TEST_UID, object_id='test_id')

    def test_no_data_in_response_error(self):
        self.response.status_code = 404
        self.response.content = error_response('{}')
        with assert_raises(DatasyncApiObjectNotFoundError):
            self.personality_api.passport_external_data_get(uid=TEST_UID, object_id='test_id')


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class TestPersonalityApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_personality_api = FakePersonalityApi()
        self.fake_personality_api.start()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()
        self.personality_api = PersonalityApi()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.fake_personality_api.stop()
        del self.fake_tvm_credentials_manager
        del self.fake_personality_api

    def test_video_favorites_default_ok(self):
        self.fake_personality_api.set_response_value(
            'video_favorites',
            video_favorites_successful_response(),
        )
        response = self.personality_api.video_favorites(uid=TEST_UID)
        eq_(
            response,
            json.loads(video_favorites_successful_response()).get('items'),
        )
        eq_(len(self.fake_personality_api.requests), 1)
        self.fake_personality_api.requests[0].assert_url_starts_with(
            'http://localhost/v1/personality/profile/videosearch/likes',
        )
        self.fake_personality_api.requests[0].assert_query_equals({
            'query.order.asc': 'False',
            'offset': '0',
            'limit': '20',
        })
        self.fake_personality_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_video_favorites_custom_ok(self):
        items = [
            {
                'id': '1',
                'url': 'url1',
            },
            {
                'id': '2',
                'url': 'url2',
            },
            {
                'id': '3',
                'url': 'url3',
                'title': 'title3',
            },
        ]
        self.fake_personality_api.set_response_value(
            'video_favorites',
            video_favorites_successful_response(items),
        )
        response = self.personality_api.video_favorites(uid=TEST_UID, offset=1, limit=10)
        eq_(response, items)
        eq_(len(self.fake_personality_api.requests), 1)
        self.fake_personality_api.requests[0].assert_url_starts_with(
            'http://localhost/v1/personality/profile/videosearch/likes',
        )
        self.fake_personality_api.requests[0].assert_query_equals({
            'query.order.asc': 'False',
            'offset': '1',
            'limit': '10',
        })
        self.fake_personality_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_maps_bookmarks_ok(self):
        self.fake_personality_api.set_response_value(
            'maps_bookmarks',
            maps_bookmarks_response(),
        )
        response = self.personality_api.maps_bookmarks(uid=TEST_UID, limit=20, offset=40)
        eq_(
            response,
            json.loads(maps_bookmarks_response())['items'],
        )
        eq_(len(self.fake_personality_api.requests), 1)
        self.fake_personality_api.requests[0].assert_url_starts_with(
            'http://localhost/v1/personality/profile/maps_common/bookmarks',
        )
        self.fake_personality_api.requests[0].assert_query_equals({
            'offset': '40',
            'limit': '20',
        })
        self.fake_personality_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_passport_external_data_get_all(self):
        self.fake_personality_api.set_response_value(
            'passport_external_data_get_all',
            passport_external_data_response_multi(
                items=[
                    passport_external_data_item(),
                ],
            ),
        )
        eq_(
            self.personality_api.passport_external_data_get_all(uid=TEST_UID),
            [
                {'id': 'test_id', 'modified_at': 100, 'data': 'test_data'},
            ],
        )

    def test_passport_external_data_get(self):
        self.fake_personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(meta='test_meta'),
        )
        eq_(
            self.personality_api.passport_external_data_get(uid=TEST_UID, object_id='test_id'),
            {'id': 'test_id', 'modified_at': 100, 'data': 'test_data', 'meta': 'test_meta'},
        )

    def test_passport_external_data_update(self):
        self.fake_personality_api.set_response_value(
            'passport_external_data_update',
            passport_external_data_response(meta='test_meta'),
        )
        ok_(
            self.personality_api.passport_external_data_update(
                uid=TEST_UID,
                object_id='test_id',
                data='test_data',
                meta='test_meta',
                modified_at=100,
            ) is None,
        )

    def test_passport_external_data_delete(self):
        self.fake_personality_api.set_response_value(
            'passport_external_data_delete',
            '{}',
        )
        ok_(
            self.personality_api.passport_external_data_delete(uid=TEST_UID, object_id='test_id') is None,
        )

    def test_batch_request_single_passport_get(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_item(passport_external_data_response()),
            ]),
        )
        eq_(
            self.personality_api.batch_get(1111, [
                {
                    'url': '/v1/personality/profile/passport/external_data/test_id',
                },
            ]),
            [
                {'id': 'test_id', 'modified_at': 100, 'data': 'test_data'},
            ],
        )

    def test_batch_request_single_passport_get_all(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_item(passport_external_data_response_multi()),
            ]),
        )
        eq_(
            self.personality_api.batch_get(1111, [
                {
                    'url': '/v1/personality/profile/passport/external_data',
                },
            ]),
            [
                [{'id': 'test_id', 'modified_at': 100, 'data': 'test_data'}],
            ],
        )

    def test_batch_request_single_other_get_all(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_item(maps_bookmarks_response()),
            ]),
        )
        eq_(
            self.personality_api.batch_get(1111, [
                {
                    'url': '/v1/personality/profile/maps_common/bookmarks',
                },
            ]),
            [
                json.loads(maps_bookmarks_response())['items'],
            ],
        )

    def test_batch_request_errors(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_error(),
                passport_external_data_batch_error(code=401, error='DiskUnsupportedUserAccountTypeError'),
                passport_external_data_batch_error(code=401, error='DiskUserBlockedError'),
                passport_external_data_batch_error(code=404),
                passport_external_data_batch_error(code=500, error='DiskServiceUnavailableError'),
            ]),
        )
        rv = self.personality_api.batch_get(1111, [
            {
                'url': '/v1/personality/profile/passport/external_data',
            },
        ] * 5)
        eq_(len(rv), 5)
        eq_(type(rv[0]), DatasyncApiPermanentError)
        eq_(str(rv[0]), 'unknown_error')
        eq_(type(rv[1]), DatasyncAccountInvalidTypeError)
        eq_(str(rv[1]), 'DiskUnsupportedUserAccountTypeError')
        eq_(type(rv[2]), DatasyncUserBlockedError)
        eq_(str(rv[2]), 'DiskUserBlockedError')
        eq_(type(rv[3]), DatasyncApiObjectNotFoundError)
        eq_(str(rv[3]), 'unknown_error')
        eq_(type(rv[4]), DatasyncApiTemporaryError)
        eq_(str(rv[4]), 'DiskServiceUnavailableError')

    def test_batch_request_no_url(self):
        with assert_raises(TypeError):
            self.personality_api.batch_get(1111, [
                {
                },
            ])

    def test_batch_request_request_response_inequality(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_item(passport_external_data_response()),
                passport_external_data_batch_item(passport_external_data_response()),
            ]),
        )
        with assert_raises(AssertionError):
            self.personality_api.batch_get(1111, [
                {
                    'url': '/v1/personality/profile/passport/external_data/test_id',
                },
            ])

    def test_batch_request_bad_json_in_response_body(self):
        self.fake_personality_api.set_response_value(
            'batch_request',
            passport_external_data_batch_response([
                passport_external_data_batch_item(b'{'),
            ]),
        )
        with assert_raises(DatasyncApiPermanentError):
            self.personality_api.batch_get(1111, [
                {
                    'url': '/v1/personality/profile/passport/external_data/test_id',
                },
            ])
