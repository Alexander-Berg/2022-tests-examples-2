# pylint: disable=redefined-outer-name

import pytest

from taxi import discovery
from taxi.util import dates

from taxi_sm_monitor import google_play
from taxi_sm_monitor.crontasks import load_google_play_reviews


@pytest.fixture
def patch_google_play_reviews(patch):
    def _wrap(reviews=None):
        @patch(
            'taxi_sm_monitor.crontasks.load_google_play_reviews.'
            '_fetch_unprocessed_reviews',
        )
        async def _dummy_get_reviews(*args, **kwargs):
            return reviews or [
                {
                    'authorName': 'Иван Железняк',
                    'comments': [
                        {
                            'userComment': {
                                'androidOsVersion': 26,
                                'appVersionCode': 3078641,
                                'appVersionName': '3.86.0',
                                'device': 'HWAUM-Q',
                                'lastModified': {
                                    'nanos': 131000000,
                                    'seconds': '1577164647',
                                },
                                'reviewerLanguage': 'ru_RU',
                                'starRating': 1,
                                'text': 'Цены высокие',
                            },
                        },
                    ],
                    'reviewId': 'first_review_id',
                },
                {
                    'comments': [
                        {
                            'userComment': {
                                'androidOsVersion': 26,
                                'appVersionCode': 3078641,
                                'appVersionName': '3.86.0',
                                'device': 'HWAUM-Q',
                                'lastModified': {
                                    'nanos': 131000000,
                                    'seconds': '1577164647',
                                },
                                'reviewerLanguage': 'ru_RU',
                                'starRating': 1,
                                'text': 'Цены низкие',
                            },
                        },
                    ],
                    'reviewId': 'second_review_id',
                },
            ]

        return _dummy_get_reviews

    return _wrap


@pytest.fixture
def patch_google_play_paginated(patch):
    call_number = 0

    def _wrap(reviews=None):
        @patch(
            'taxi_sm_monitor.crontasks.load_google_play_reviews.'
            '_init_reviews_resource',
        )
        async def _dummy_build_service(*args, **kwargs):
            return None

        @patch(
            'taxi_sm_monitor.crontasks.load_google_play_reviews.'
            '_get_next_reviews_page',
        )
        def _dummy_get_reviews(
                db, package, max_items, pagination_token, **kwargs,
        ):
            nonlocal call_number
            call_number += 1

            if call_number == 1:
                assert pagination_token is None
                return (
                    [
                        {
                            'authorName': 'Самый новый',
                            'comments': [
                                {
                                    'userComment': {
                                        'androidOsVersion': 26,
                                        'appVersionCode': 3078641,
                                        'appVersionName': '3.86.0',
                                        'device': 'HWAUM-Q',
                                        'lastModified': {
                                            'seconds': '1577164647',
                                        },
                                        'reviewerLanguage': 'ru_RU',
                                        'starRating': 1,
                                        'text': 'Цены высокие',
                                    },
                                },
                            ],
                            'reviewId': 'first_new',
                        },
                    ],
                    '2',
                )

            if call_number == 2:
                assert pagination_token == '2'
                return (
                    [
                        {
                            'authorName': 'Второй по свежести',
                            'comments': [
                                {
                                    'userComment': {
                                        'androidOsVersion': 26,
                                        'appVersionCode': 3078641,
                                        'appVersionName': '3.86.0',
                                        'device': 'HWAUM-Q',
                                        'lastModified': {
                                            'seconds': '1577164640',
                                        },
                                        'reviewerLanguage': 'ru_RU',
                                        'starRating': 1,
                                        'text': 'Цены высокие',
                                    },
                                },
                            ],
                            'reviewId': 'second_new',
                        },
                    ],
                    '3',
                )

            if call_number == 3:
                assert pagination_token == '3'
                return (
                    [
                        {
                            'authorName': 'Первый необработанный',
                            'comments': [
                                {
                                    'userComment': {
                                        'androidOsVersion': 26,
                                        'appVersionCode': 3078641,
                                        'appVersionName': '3.86.0',
                                        'device': 'HWAUM-Q',
                                        'lastModified': {
                                            'seconds': '1577104647',
                                        },
                                        'reviewerLanguage': 'ru_RU',
                                        'starRating': 1,
                                        'text': 'Цены высокие',
                                    },
                                },
                            ],
                            'reviewId': 'first_unprocessed',
                        },
                        {
                            'authorName': 'Последний обработанный',
                            'comments': [
                                {
                                    'userComment': {
                                        'androidOsVersion': 26,
                                        'appVersionCode': 3078641,
                                        'appVersionName': '3.86.0',
                                        'device': 'HWAUM-Q',
                                        'lastModified': {
                                            'seconds': '1577054647',
                                        },
                                        'reviewerLanguage': 'ru_RU',
                                        'starRating': 1,
                                        'text': 'Цены высокие',
                                    },
                                },
                            ],
                            'reviewId': 'last_processed',
                        },
                    ],
                    None,
                )

            raise NotImplementedError

        return _dummy_get_reviews

    return _wrap


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_LOAD_REVIEWS=True)
async def test_google_play_load_reviews(
        sm_monitor_context,
        loop,
        patch_google_play_reviews,
        patch_aiohttp_session,
        response_mock,
):
    patch_google_play_reviews()

    chat_counter = 0
    chatterbox_counter = 0

    expected_request_support_chat = [
        {
            'request_id': (
                'first_review_id_a8bb18820c92222ca15a4ad5956ebc3e_'
                '6088c4b0ae615449bb35700ca94e6fe0'
            ),
            'owner': {'id': 'first_review_id', 'role': 'google_play_review'},
            'message': {
                'metadata': {
                    'rating': 1,
                    'device_model': 'HWAUM-Q',
                    'app_version': 3078641,
                    'android_version': 26,
                    'language': 'ru_RU',
                    'last_modified': '2019-12-24T05:17:27+0000',
                },
                'text': 'Цены высокие',
                'sender': {
                    'id': 'first_review_id',
                    'role': 'google_play_review',
                },
            },
            'metadata': {
                'google_play_app': 'ru.yandex.uber',
                'user_name': 'Иван Железняк',
                'user_locale': 'ru',
            },
        },
        {
            'request_id': (
                'second_review_id_f99e2468fe6a6d869e5a9f635abf5f74_'
                '6088c4b0ae615449bb35700ca94e6fe0'
            ),
            'owner': {'id': 'second_review_id', 'role': 'google_play_review'},
            'message': {
                'metadata': {
                    'rating': 1,
                    'device_model': 'HWAUM-Q',
                    'app_version': 3078641,
                    'android_version': 26,
                    'language': 'ru_RU',
                    'last_modified': '2019-12-24T05:17:27+0000',
                },
                'text': 'Цены низкие',
                'sender': {
                    'id': 'second_review_id',
                    'role': 'google_play_review',
                },
            },
            'metadata': {
                'google_play_app': 'ru.yandex.uber',
                'user_name': 'google_play_name',
                'user_locale': 'ru',
            },
        },
    ]

    expected_request_chatterbox = [
        {
            'type': 'chat',
            'external_id': 'review_chat_1',
            'metadata': {
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'google_play_app_ru_yandex_uber',
                    },
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'google_play_app',
                        'value': 'ru.yandex.uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_name',
                        'value': 'Иван Железняк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_locale',
                        'value': 'ru',
                    },
                    {'change_type': 'set', 'field_name': 'rating', 'value': 1},
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'HWAUM-Q',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'app_version',
                        'value': 3078641,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'android_version',
                        'value': 26,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'language',
                        'value': 'ru_RU',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'last_modified',
                        'value': '2019-12-24T05:17:27+0000',
                    },
                ],
            },
        },
        {
            'type': 'chat',
            'external_id': 'review_chat_1',
            'metadata': {
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'google_play_app_ru_yandex_uber',
                    },
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'google_play_app',
                        'value': 'ru.yandex.uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_name',
                        'value': 'google_play_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_locale',
                        'value': 'ru',
                    },
                    {'change_type': 'set', 'field_name': 'rating', 'value': 1},
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'HWAUM-Q',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'app_version',
                        'value': 3078641,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'android_version',
                        'value': 26,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'language',
                        'value': 'ru_RU',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'last_modified',
                        'value': '2019-12-24T05:17:27+0000',
                    },
                ],
            },
        },
    ]

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        nonlocal chatterbox_counter
        assert method == 'post'
        assert url.startswith('http://chatterbox.taxi.dev.yandex.net/v1/tasks')
        request_data = kwargs['json']
        assert request_data == expected_request_chatterbox[chatterbox_counter]
        chatterbox_counter += 1
        return response_mock(json={'id': 'review_task_1'})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        nonlocal chat_counter
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat'
        request_data = kwargs['json']
        assert request_data == expected_request_support_chat[chat_counter]
        chat_counter += 1
        return response_mock(json={'id': 'review_chat_1'})

    await load_google_play_reviews.do_stuff(sm_monitor_context, loop)
    assert chatterbox.calls
    assert support_chat.calls


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_LOAD_REVIEWS=True)
async def test_pagination(
        taxi_sm_monitor_app_stq,
        sm_monitor_context,
        loop,
        patch_google_play_paginated,
        patch_aiohttp_session,
        response_mock,
):
    patched_google_play = patch_google_play_paginated()

    reviews_processed = 0

    reviews_state = (
        await taxi_sm_monitor_app_stq.db.google_play_reviews_state.find_one(
            {'package_name': 'ru.yandex.uber'},
        )
    )
    assert reviews_state['last_processed_time'] == dates.parse_timestring(
        '2019-12-22T23:00:07+0000', timezone='UTC',
    )

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        nonlocal reviews_processed
        reviews_processed += 1
        return response_mock(json={'id': 'review_task_1'})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        return response_mock(json={'id': 'review_chat_1'})

    await load_google_play_reviews.do_stuff(sm_monitor_context, loop)
    assert chatterbox.calls
    assert support_chat.calls

    assert len(patched_google_play.calls) == 3

    assert reviews_processed == 3

    reviews_state = (
        await taxi_sm_monitor_app_stq.db.google_play_reviews_state.find_one(
            {'package_name': 'ru.yandex.uber'},
        )
    )
    assert reviews_state['last_processed_time'] == dates.parse_timestring(
        '2019-12-24T05:17:27+0000', timezone='UTC',
    )


async def test_token_refresh_error():
    with pytest.raises(google_play.AccessTokenCanNotBeRefreshed):
        creds = google_play.NoRefreshTokenCredentials(None, None, None)
        creds.refresh(None)


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_LOAD_REVIEWS=True)
async def test_google_play_load_reviews_conflict(
        sm_monitor_context,
        loop,
        patch_google_play_reviews,
        patch_aiohttp_session,
        response_mock,
):
    patch_google_play_reviews()

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        raise Exception()

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat'
        return response_mock(json={'id': 'review_chat_1'}, status=409)

    await load_google_play_reviews.do_stuff(sm_monitor_context, loop)
    assert not chatterbox.calls
    assert support_chat.calls


@pytest.mark.config(SM_MONITOR_GOOGLE_PLAY_LOAD_REVIEWS=True)
async def test_empty_reviews(
        sm_monitor_context,
        loop,
        patch_google_play_reviews,
        patch_aiohttp_session,
        patch,
):
    @patch(
        'taxi_sm_monitor.crontasks.load_google_play_reviews.'
        '_fetch_unprocessed_reviews',
    )
    async def _dummy_get_reviews(*args, **kwargs):
        return []

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def chatterbox(method, url, **kwargs):
        pass

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat(method, url, **kwargs):
        pass

    await load_google_play_reviews.do_stuff(sm_monitor_context, loop)
    assert not chatterbox.calls
    assert not support_chat.calls
