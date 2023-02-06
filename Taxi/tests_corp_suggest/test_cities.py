# pylint: disable=invalid-name

import pytest

pytestmark = pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'rus': {'root_geo_node': 'br_russia'}},
)

GEO_NODES_PERM = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'country',
        'parent_name': 'br_root',
        'tanker_key': 'name.br_russia',
        'region_id': '225',
    },
    {
        'name': 'br_privolzhskij_fo',
        'name_en': 'Volga Federal District',
        'name_ru': 'Приволжский ФО',
        'node_type': 'node',
        'parent_name': 'br_russia',
        'tanker_key': 'name.br_privolzhskij_fo',
        'region_id': '40',
    },
    {
        'name': 'br_permskij_kraj',
        'name_en': 'Perm Territory',
        'name_ru': 'Пермский край',
        'node_type': 'node',
        'parent_name': 'br_privolzhskij_fo',
        'tanker_key': 'name.br_permskij_kraj',
        'region_id': '11108',
    },
    {
        'name': 'br_perm_region',
        'name_en': 'Perm region',
        'name_ru': 'Пермский регион',
        'node_type': 'agglomeration',
        'parent_name': 'br_permskij_kraj',
        'tanker_key': 'name.br_perm_region',
        'region_id': '11108',
    },
    {
        'name': 'br_perm',
        'name_en': 'Perm',
        'name_ru': 'Пермь',
        'node_type': 'agglomeration',
        'parent_name': 'br_permskij_kraj',
        'tanker_key': 'name.br_perm',
        'region_id': '50',
    },
]


@pytest.mark.parametrize(
    ('uri', 'headers'),
    [
        pytest.param('corp-suggest/v1/cities', {}, id='non-mobile'),
        pytest.param(
            '4.0/corp-suggest/v1/cities',
            {'X-Request-Language': 'ru'},
            id='mobile',
        ),
    ],
)
async def test_cities(taxi_corp_suggest, uri, headers):
    response = await taxi_corp_suggest.post(
        uri, json={'query': 'мос', 'country': 'rus'}, headers=headers,
    )
    response_json = response.json()

    assert response.status_code == 200, response_json
    assert response_json == {
        'items': [
            {
                'description': 'Московская область, Центральный ФО, Россия',
                'text': 'Москва',
                'city': 'Москва',
            },
        ],
    }


@pytest.mark.geo_nodes(GEO_NODES_PERM)
@pytest.mark.parametrize(
    ('uri', 'headers'),
    [
        pytest.param('corp-suggest/v1/cities', {}, id='non-mobile'),
        pytest.param(
            '4.0/corp-suggest/v1/cities',
            {'X-Request-Language': 'ru'},
            id='mobile',
        ),
    ],
)
async def test_cities_skip_duplicates(taxi_corp_suggest, uri, headers):
    response = await taxi_corp_suggest.post(
        uri, json={'query': 'Перм', 'country': 'rus'}, headers=headers,
    )
    response_json = response.json()

    assert response.status_code == 200, response_json
    assert response_json == {
        'items': [
            {
                'description': 'Пермский край, Приволжский ФО, Россия',
                'text': 'Пермь',
                'city': 'Пермь',
            },
        ],
    }


@pytest.mark.parametrize(
    ('uri', 'headers'),
    [
        pytest.param(
            'corp-suggest/v1/cities',
            {'Accept-Language': 'unknown'},
            id='non-mobile',
        ),
        pytest.param('4.0/corp-suggest/v1/cities', {}, id='mobile'),
    ],
)
async def test_cities_accept_language(taxi_corp_suggest, uri, headers):
    response = await taxi_corp_suggest.post(
        uri, json={'query': 'mos', 'country': 'rus'}, headers=headers,
    )
    response_json = response.json()

    assert response.status_code == 200, response_json
    assert response_json == {
        'items': [
            {
                'description': (
                    'Moscow Region, Central Federal District, Russia'
                ),
                'text': 'Moscow',
                'city': 'Москва',
            },
        ],
    }


@pytest.mark.parametrize(
    ('uri', 'headers'),
    [
        pytest.param('corp-suggest/v1/cities', {}, id='non-mobile'),
        pytest.param(
            '4.0/corp-suggest/v1/cities',
            {'X-Request-Language': 'ru'},
            id='mobile',
        ),
    ],
)
async def test_cities_not_matched(taxi_corp_suggest, uri, headers):
    response = await taxi_corp_suggest.post(
        uri, json={'query': 'Балаха', 'country': 'rus'}, headers=headers,
    )
    response_json = response.json()

    assert response.status_code == 200, response_json
    assert response_json == {'items': []}


@pytest.mark.parametrize(
    ('uri', 'headers'),
    [
        pytest.param('corp-suggest/v1/cities', {}, id='non-mobile'),
        pytest.param(
            '4.0/corp-suggest/v1/cities',
            {'X-Request-Language': 'ba'},
            id='mobile',
        ),
    ],
)
async def test_cities_bad_country(taxi_corp_suggest, uri, headers):
    response = await taxi_corp_suggest.post(
        uri, json={'query': 'Балаха', 'country': 'ba'}, headers=headers,
    )
    response_json = response.json()

    assert response.status_code == 400, response_json
    assert response_json == {
        'code': 'COUNTRY_IS_NOT_SUPPORTED',
        'message': 'Country ba is not supported',
    }
