import copy
from typing import List
from typing import NamedTuple

import pytest

from taxi_stories.repositories import stories as stories_repo
from test_taxi_stories.web import data_generators

STORIES_PATH = '/4.0/stories'
DEFAULT_USER_ID = 'user_id'
DEFAULT_YANDEX_UID = 'yandex_uid'
DEFAULT_LOCATION = [37.642407, 55.734258]
USER_HEADERS = {
    'X-YaTaxi-UserId': DEFAULT_USER_ID,
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
}
DEFAULT_HEADERS = {
    'Accept-Language': 'ru-RU',
    'X-Request-Application': (
        'app_ver3=34174,app_name=iphone,app_build=release,'
        'platform_ver2=4,app_ver2=95,platform_ver1=12,app_ver1=4'
    ),
}
DEFAULT_ZONE_NAME = 'Москва'
DEFAULT_ORDER_ID = 'default_order'
DEFAULT_CONFIGS = {
    'STORIES_SERVICE': {'default_locale': 'ru'},
    'LOCALES_SUPPORTED': ['ru', 'en', 'fr'],
}
DEFAULT_CLIENT_MESSAGES = {
    'promo_story.default.button_title': data_generators.BUTTON_TITLES,
    'exceptions.stories.not_found_error': {
        'ru': 'Слишком много контактов',
        'en': 'Too many contacts',
    },
}
EXPERIMENTS = {
    'superapp_stories': {
        'grocery': {
            'stories': [
                data_generators.create_db_story(
                    'grocery_story' + str(i), ['ru', 'en'],
                )
                for i in range(3)
            ],
        },
    },
}


YANDEX_UID_ARG = {
    'type': 'string',
    'name': 'yandex_uid',
    'value': DEFAULT_YANDEX_UID,
}
USER_ID_ARG = {'type': 'string', 'name': 'user_id', 'value': DEFAULT_USER_ID}
POINT_A_ARG = {'type': 'point', 'name': 'point_a', 'value': DEFAULT_LOCATION}
ZONE_NAME_ARG = {
    'type': 'string',
    'name': 'zone_name',
    'value': DEFAULT_ZONE_NAME,
}


class Response(NamedTuple):
    name: str
    value: dict


@pytest.mark.config(
    STORIES_STUBS_V2={
        'stories': [
            data_generators.create_db_story(
                'aaaa0000000000000000000' + str(i), ['ru', 'en'],
            )
            for i in range(3)
        ],
    },
    STORIES_BY_COUNTRIES={
        'safety_center': {
            'rus': {
                'include': [
                    'aaaa00000000000000000000',
                    'aaaa00000000000000000001',
                ],
            },
        },
    },
    **DEFAULT_CONFIGS,
)
@pytest.mark.translations(client_messages=DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'story_context,expected_context',
    (
        pytest.param(
            'safety_center',
            'aaaa0000000000000000000',
            marks=[pytest.mark.config(STORIES_FROM_DB_ENABLED=True)],
            id='New default stories flow',
        ),
        pytest.param(
            'safety_center',
            'aaaa0000000000000000000',
            marks=[pytest.mark.config(STORIES_FROM_DB_ENABLED=False)],
            id='Old default stories flow',
        ),
        ('ride_details', 'aaaa0000000000000000000'),
        ('cashback', 'cccc0000000000000000000'),
    ),
)
@pytest.mark.parametrize(
    'accept_language,expected_locale,response_status',
    (
        ('ru-RU', 'ru', 200),
        ('en-US', 'en', 200),
        ('fr-FR', 'ru', 200),  # test default locale fallback
    ),
)
@pytest.mark.parametrize(
    'authorize_status,order_status,stories_count_by_context',
    (
        [
            'authorized',
            'has_order',
            {'safety_center': 2, 'ride_details': 2, 'cashback': 2},
        ],
        # there is '0' because '__all__' is empty for safety_center context
        [
            'non_authorized',
            'has_order',
            {'safety_center': 0, 'ride_details': 0, 'cashback': 2},
        ],
        [
            'authorized',
            'has_no_order',
            {'safety_center': 0, 'ride_details': 0, 'cashback': 2},
        ],
        [
            'non_authorized',
            'has_no_order',
            {'safety_center': 0, 'ride_details': 0, 'cashback': 2},
        ],
    ),
)
async def test_stories_context(
        web_app_client,
        mock_archive_response,
        story_context,
        expected_context,
        authorize_status,
        order_status,
        stories_count_by_context,
        accept_language,
        expected_locale,
        response_status,
):
    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers.update({'Accept-Language': accept_language})
    if authorize_status == 'authorized':
        headers.update(USER_HEADERS)

    if order_status == 'has_no_order':
        mock_archive_response(None)
    else:
        mock_archive_response(
            {
                'nz': DEFAULT_ZONE_NAME,
                'user_id': DEFAULT_USER_ID,
                'yandex_uid': DEFAULT_YANDEX_UID,
            },
            DEFAULT_YANDEX_UID,
            {'nearest_zone': DEFAULT_ZONE_NAME, 'id': DEFAULT_ORDER_ID},
        )
    stories_count = stories_count_by_context[story_context]

    ordered_response = await web_app_client.get(
        f'/4.0/stories?context={story_context}&order_id={DEFAULT_ORDER_ID}',
        headers=headers,
    )
    expected_data = {
        'stories': [
            data_generators.create_response_story(
                expected_context + str(i), expected_locale,
            )
            for i in range(stories_count)
        ],
    }
    if order_status == 'has_no_order':
        assert ordered_response.status == 404
    else:
        assert ordered_response.status == 200
        assert await ordered_response.json() == expected_data

    no_order_get_response = await web_app_client.get(
        f'/4.0/stories?context={story_context}', headers=headers,
    )
    no_order_post_response = await web_app_client.post(
        '/4.0/stories', json={'context': story_context}, headers=headers,
    )

    assert no_order_get_response.status == no_order_post_response.status == 200
    no_order_get_data = await no_order_get_response.json()
    no_order_post_data = await no_order_post_response.json()
    assert no_order_get_data == no_order_post_data == expected_data


@pytest.mark.config(STORIES_FROM_DB_ENABLED=True, **DEFAULT_CONFIGS)
@pytest.mark.translations(client_messages=DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    ['expected_story_names_order'],
    [
        pytest.param(
            [
                'aaaa00000000000000000000_name',
                'aaaa00000000000000000001_name',
                'aaaa00000000000000000002_name',
            ],
            marks=pytest.mark.config(
                STORIES_BY_COUNTRIES={
                    'safety_center': {
                        'rus': {
                            'include': [
                                'aaaa00000000000000000000',
                                'aaaa00000000000000000001',
                                'aaaa00000000000000000002',
                            ],
                        },
                    },
                },
            ),
        ),
        pytest.param(
            [
                'aaaa00000000000000000002_name',
                'aaaa00000000000000000001_name',
                'aaaa00000000000000000000_name',
            ],
            marks=pytest.mark.config(
                STORIES_BY_COUNTRIES={
                    'safety_center': {
                        'rus': {
                            'include': [
                                'aaaa00000000000000000002',
                                'aaaa00000000000000000001',
                                'aaaa00000000000000000000',
                            ],
                        },
                    },
                },
            ),
        ),
        pytest.param(
            [
                'aaaa00000000000000000001_name',
                'aaaa00000000000000000002_name',
                'aaaa00000000000000000000_name',
            ],
            marks=pytest.mark.config(
                STORIES_BY_COUNTRIES={
                    'safety_center': {
                        '__all__': ['aaaa00000000000000000000'],
                        'rus': {
                            'include': [
                                'aaaa00000000000000000001',
                                'aaaa00000000000000000002',
                            ],
                        },
                    },
                },
            ),
            id='common story ids at the bottom',
        ),
    ],
)
async def test_db_stories_order(
        web_app_client,
        mock_archive_response,
        expected_story_names_order: List[str],
):
    mock_archive_response(
        {
            'nz': DEFAULT_ZONE_NAME,
            'user_id': DEFAULT_USER_ID,
            'yandex_uid': DEFAULT_YANDEX_UID,
        },
        DEFAULT_YANDEX_UID,
        {'nearest_zone': DEFAULT_ZONE_NAME, 'id': DEFAULT_ORDER_ID},
    )
    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers.update({'Accept-Language': 'ru-RU'})
    headers.update(USER_HEADERS)
    response = await web_app_client.get(
        f'/4.0/stories?context=safety_center&order_id={DEFAULT_ORDER_ID}',
        headers=headers,
    )
    assert response.status == 200
    response_json = await response.json()
    response_story_names_order = [s['name'] for s in response_json['stories']]
    assert response_story_names_order == expected_story_names_order


@pytest.mark.config(
    STORIES_BY_COUNTRIES={
        'all_context': {'__all__': ['id1']},
        'one_country_context': {
            '__all__': ['id2'],
            'rus': {'include': ['id1'], 'exclude': ['id2']},
        },
        'country_only_context': {'rus': {'include': ['id1']}},
    },
)
@pytest.mark.parametrize(
    'story_context,all_result',
    (
        ('all_context', ['id1']),
        ('one_country_context', ['id2']),
        ('country_only_context', list()),
    ),
)
def test_ids_by_context(story_context, all_result, web_context):
    result = stories_repo.get_ids_by_context(
        country='rus', story_context=story_context, config=web_context.config,
    )

    assert result == ['id1']

    assert not stories_repo.skip_story_condition(result, 'id1')
    assert not stories_repo.skip_story_condition(None, 'any_id')
    assert stories_repo.skip_story_condition(result, 'id2')
    assert stories_repo.skip_story_condition({}, 'id1')

    no_country_result = stories_repo.get_ids_by_context(
        country='no_country',
        story_context=story_context,
        config=web_context.config,
    )
    assert no_country_result == all_result


@pytest.mark.parametrize(
    'payload',
    [
        pytest.param(
            {'context': 'grocery'},
            marks=[
                pytest.mark.client_experiments3(
                    experiment_name='superapp_stories',
                    consumer='stories/stories',
                    args=[YANDEX_UID_ARG, USER_ID_ARG],
                    value=EXPERIMENTS['superapp_stories'],
                ),
            ],
        ),
        pytest.param(
            {'context': 'grocery', 'location': [37.642407, 55.734258]},
            marks=[
                pytest.mark.client_experiments3(
                    experiment_name='superapp_stories',
                    consumer='stories/stories',
                    args=[
                        YANDEX_UID_ARG,
                        USER_ID_ARG,
                        ZONE_NAME_ARG,
                        POINT_A_ARG,
                    ],
                    value=EXPERIMENTS['superapp_stories'],
                ),
            ],
        ),
    ],
)
@pytest.mark.translations(client_messages=DEFAULT_CLIENT_MESSAGES)
@pytest.mark.config(
    STORIES_BY_COUNTRIES={
        'all_context': {'__all__': ['id1']},
        'grocery': {'__all__': ['grocery_story0']},
    },
)
async def test_post_handler(
        web_app_client, mockserver, mock_archive_response, payload,
):
    @mockserver.json_handler('/taxi-protocol/3.0/nearestzone')
    def _nearestzone_response(req):
        assert req.json == {'point': payload['location']}
        return {'nearest_zone': DEFAULT_ZONE_NAME}

    mock_archive_response(None)

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers.update(USER_HEADERS)
    response = await web_app_client.post(
        '/4.0/stories', json=payload, headers=headers,
    )
    assert response.status == 200
    assert await response.json() == {
        'stories': [
            data_generators.create_response_story('grocery_story0', 'ru'),
        ],
    }


@pytest.mark.translations(client_messages=DEFAULT_CLIENT_MESSAGES)
@pytest.mark.parametrize(
    'passport_flags,expected_story_ids',
    [
        pytest.param(
            '',
            ['cccc00000000000000000002', 'cccc00000000000000000001'],
            id='no-passport-flags',
        ),
        pytest.param(
            'portal,pdd',
            ['cccc00000000000000000002', 'cccc00000000000000000001'],
            id='no-ya-plus',
        ),
        pytest.param(
            'phonish,ya-plus',
            ['cccc00000000000000000003', 'cccc00000000000000000001'],
            id='has-ya-plus',
        ),
        pytest.param(
            'portal,ya-plus,cashback-plus',
            ['cccc00000000000000000004', 'cccc00000000000000000001'],
            id='has-cashback-plus',
        ),
    ],
)
async def test_cashback_plus_stories(
        web_app_client,
        passport_flags,
        expected_story_ids,
        mock_archive_response,
):
    mock_archive_response(None)
    expected_stories = [
        data_generators.create_response_story(story_id, 'ru')
        for story_id in expected_story_ids
    ]

    headers = {
        **DEFAULT_HEADERS,
        **USER_HEADERS,
        'X-YaTaxi-Pass-Flags': passport_flags,
    }

    response = await web_app_client.post(
        '/4.0/stories',
        headers=headers,
        json={'context': 'cashback', 'location': DEFAULT_LOCATION},
    )
    assert response.status == 200

    response_data = await response.json()
    response_stories = response_data['stories']

    assert response_stories == expected_stories
