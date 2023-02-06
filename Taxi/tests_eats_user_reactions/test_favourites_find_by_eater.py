import pytest


@pytest.mark.parametrize(
    'request_json, response_json',
    [
        # all reactions
        (
            {
                'eater_id': 'eater_id_1',
                'subject_namespaces': ['catalog_brand', 'menu_item'],
                'pagination': {'limit': 1000},
            },
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                    {
                        'created_at': '2020-01-03T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_3',
                        },
                    },
                    {
                        'created_at': '2020-01-04T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_4',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-04T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # all reactions with empty subject_namespaces
        (
            {
                'eater_id': 'eater_id_1',
                'subject_namespaces': [],
                'pagination': {'limit': 1000},
            },
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                    {
                        'created_at': '2020-01-03T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_3',
                        },
                    },
                    {
                        'created_at': '2020-01-04T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_4',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-04T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # all reactions without declared subject_namespaces
        (
            {'eater_id': 'eater_id_1', 'pagination': {'limit': 1000}},
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                    {
                        'created_at': '2020-01-03T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_3',
                        },
                    },
                    {
                        'created_at': '2020-01-04T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_4',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-04T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # Has more results
        (
            {'eater_id': 'eater_id_1', 'pagination': {'limit': 3}},
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                    {
                        'created_at': '2020-01-03T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_3',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-03T00:00:00+0000',
                    'has_more': True,
                },
            },
        ),
        # Has not more when hit the limit
        (
            {'eater_id': 'eater_id_1', 'pagination': {'limit': 4}},
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                    {
                        'created_at': '2020-01-03T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_3',
                        },
                    },
                    {
                        'created_at': '2020-01-04T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_4',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-04T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # Filter by subject_namespaces
        (
            {
                'eater_id': 'eater_id_1',
                'subject_namespaces': ['catalog_brand'],
                'pagination': {'limit': 1000},
            },
            {
                'reactions': [
                    {
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_1',
                        },
                    },
                    {
                        'created_at': '2020-01-02T00:00:00+00:00',
                        'subject': {
                            'namespace': 'catalog_brand',
                            'id': 'subject_id_2',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-02T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # Using cursor
        (
            {
                'eater_id': 'eater_id_1',
                'pagination': {
                    'limit': 3,
                    'cursor': '2020-01-03T00:00:00+0000',
                },
            },
            {
                'reactions': [
                    {
                        'created_at': '2020-01-04T00:00:00+00:00',
                        'subject': {
                            'namespace': 'menu_item',
                            'id': 'subject_id_4',
                        },
                    },
                ],
                'pagination': {
                    'cursor': '2020-01-04T00:00:00+0000',
                    'has_more': False,
                },
            },
        ),
        # Not found
        (
            {
                'eater_id': 'nonexistent_eater_id',
                'pagination': {'limit': 1000},
            },
            {'reactions': [], 'pagination': {'cursor': '', 'has_more': False}},
        ),
    ],
)
async def test_find_by_eater(
        taxi_eats_user_reactions,
        request_json,
        response_json,
        taxi_eats_user_reactions_monitor,
):
    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/find-by-eater', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json

    builder = await taxi_eats_user_reactions_monitor.get_metric('Reaction')
    assert len(builder['reactions']) == 10


async def test_find_by_eater_paginated(taxi_eats_user_reactions):
    first_request_json = {'eater_id': 'eater_id_1', 'pagination': {'limit': 1}}
    first_response_json = {
        'reactions': [
            {
                'created_at': '2020-01-01T00:00:00+00:00',
                'subject': {
                    'namespace': 'catalog_brand',
                    'id': 'subject_id_1',
                },
            },
        ],
        'pagination': {'cursor': '2020-01-01T00:00:00+0000', 'has_more': True},
    }

    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/find-by-eater',
        json=first_request_json,
    )
    assert response.status_code == 200
    assert response.json() == first_response_json

    second_request_json = {
        'eater_id': 'eater_id_1',
        'pagination': {
            'limit': 1,
            'cursor': first_response_json['pagination']['cursor'],
        },
    }
    second_response_json = {
        'reactions': [
            {
                'created_at': '2020-01-02T00:00:00+00:00',
                'subject': {
                    'namespace': 'catalog_brand',
                    'id': 'subject_id_2',
                },
            },
        ],
        'pagination': {'cursor': '2020-01-02T00:00:00+0000', 'has_more': True},
    }
    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/find-by-eater',
        json=second_request_json,
    )
    assert response.status_code == 200
    assert response.json() == second_response_json


async def test_find_by_eater_invalid_cursor(taxi_eats_user_reactions):
    request_json = {
        'eater_id': 'eater_id_1',
        'pagination': {'cursor': 'ololo'},
    }
    response_json = {
        'code': 'invalid_pagination_cursor',
        'message': (
            'Requested value for pagination cursor has invalid format.'
            + ' Use cursor value only from response as is.'
        ),
    }

    response = await taxi_eats_user_reactions.post(
        '/eats-user-reactions/v1/favourites/find-by-eater', json=request_json,
    )
    assert response.status_code == 400
    assert response.json() == response_json
