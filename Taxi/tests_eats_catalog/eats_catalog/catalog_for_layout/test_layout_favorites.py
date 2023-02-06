from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils

FIND_BY_EATER = (
    '/eats-user-reactions/eats-user-reactions/v1/favourites/find-by-eater'
)

SINGLE_BLOCK_REQUEST_JSON = {
    'location': {'latitude': 0, 'longitude': 0},
    'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
}


async def test_slug_features_favourite_experiment_disabled(
        catalog_for_layout, eats_catalog_storage,
):
    eats_catalog_storage.add_place(storage.Place())

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
            'X-Eats-User': 'user_id=333',
            'X-Eats-Session': 'blablabla',
        },
        **SINGLE_BLOCK_REQUEST_JSON,
    )

    assert response.status_code == 200

    [block] = response.json()['blocks']
    [place] = block['list']
    assert 'favorite' not in place['payload']['data']['features']


@experiments.ENABLE_FAVORITES
@pytest.mark.parametrize(
    'headers,reactions_calls',
    [
        pytest.param(
            {'X-Eats-User': 'user_id=123'}, 1, id='no X-Eats-Session header',
        ),
        pytest.param(
            {'X-Eats-Session': 'qweetestsuit'}, 0, id='no X-Eats-User header',
        ),
        pytest.param(
            {'X-Eats-Session': 'qweetestsuit', 'X-Eats-User': 'user_id=123'},
            1,
            id='authorized request',
        ),
    ],
)
async def test_favorite_unauthorized(
        catalog_for_layout,
        mockserver,
        eats_catalog_storage,
        headers,
        reactions_calls,
):
    """Тест проверяет, что не будет запросов к сервису избранного в случае,
    если запрос неавторизован."""

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, brand=storage.Brand(brand_id=1)),
    )

    @mockserver.json_handler(FIND_BY_EATER)
    def eats_user_reactions(request):
        return {
            'reactions': [
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '1'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
            ],
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    default_headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'superapp_taxi_web',
        'x-app-version': '1.12.0',
        'cookie': 'some cookie',
    }
    for k in headers:
        default_headers[k] = headers[k]

    response = await catalog_for_layout(
        location={'longitude': 0, 'latitude': 0},
        headers=default_headers,
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )
    assert response.status_code == 200

    assert eats_user_reactions.times_called == reactions_calls

    data = response.json()

    found_favorite = False
    for item in data['filters']['list']:
        if item['type'] == 'favorite':
            found_favorite = True
            break

    if reactions_calls > 0:
        assert found_favorite, 'could not find favorite filter'

    block = layout_utils.find_block('any', data)
    for place in block:
        features = place['payload']['data']['features']
        assert 'favorite' in features
        assert features['favorite']['active'] == (reactions_calls > 0)


@experiments.ENABLE_FAVORITES
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_favorite_feature(
        catalog_for_layout, mockserver, eats_catalog_storage,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug='closed',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2020-01-01T10:00:00+00:00'),
                    end=parser.parse('2020-01-01T14:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4,
            brand=storage.Brand(brand_id=4),
            slug='closed_but_not_favorite',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4,
            place_id=4,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2020-01-01T10:00:00+00:00'),
                    end=parser.parse('2020-01-01T14:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, brand=storage.Brand(brand_id=2), slug='open',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='open_but_not_favorite',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(FIND_BY_EATER)
    def eats_user_reactions(request):
        assert request.json == {
            'eater_id': '123',
            'subject_namespaces': ['catalog_brand'],
            'pagination': {'limit': 1000},
        }
        return {
            'reactions': [
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '1'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '2'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
            ],
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'some cookie',
            'X-Eats-Session': 'qweetestsuit',
            'X-Eats-User': 'user_id=123',
        },
        location={'longitude': 37.591503, 'latitude': 55.802998},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200
    assert eats_user_reactions.times_called == 1

    data = response.json()

    block = layout_utils.find_block('any', data)

    open_place_favorite = layout_utils.find_place_by_slug('open', block)
    assert open_place_favorite['payload']['availability']['is_available']
    assert open_place_favorite['payload']['data']['features']['favorite'][
        'active'
    ]

    open_place = layout_utils.find_place_by_slug(
        'open_but_not_favorite', block,
    )
    assert open_place['payload']['availability']['is_available']
    assert not open_place['payload']['data']['features']['favorite']['active']

    closed_favorite = layout_utils.find_place_by_slug('closed', block)
    assert not closed_favorite['payload']['availability']['is_available']
    assert closed_favorite['payload']['data']['features']['favorite']['active']

    closed_place = layout_utils.find_place_by_slug(
        'closed_but_not_favorite', block,
    )
    assert not closed_place['payload']['availability']['is_available']
    assert not closed_place['payload']['data']['features']['favorite'][
        'active'
    ]
