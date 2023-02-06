import pytest


async def test_retrieve(taxi_parks_activation):
    park_ids = ['park1']
    response = await taxi_parks_activation.post(
        'v1/parks/activation/retrieve', json={'ids_in_set': park_ids},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'can_subsidy': False,
                },
            },
        ],
    }


async def test_retrieve_wrong_id(taxi_parks_activation):
    park_ids = ['wrong_id']
    response = await taxi_parks_activation.post(
        'v1/parks/activation/retrieve', json={'ids_in_set': park_ids},
    )
    assert response.status_code == 200
    assert response.json() == {'parks_activation': []}


async def test_retrieve_wrong_id_with_correct(taxi_parks_activation):
    park_ids = ['wrong_id', 'park1']
    response = await taxi_parks_activation.post(
        'v1/parks/activation/retrieve', json={'ids_in_set': park_ids},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'can_subsidy': False,
                },
            },
        ],
    }


async def test_retrieve_multiple(taxi_parks_activation):
    park_ids = ['park1', 'park2', 'park3']
    response = await taxi_parks_activation.post(
        'v1/parks/activation/retrieve', json={'ids_in_set': park_ids},
    )
    assert response.status_code == 200
    assert response.json() == {
        'parks_activation': [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                    'can_subsidy': False,
                },
            },
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'can_subsidy': False,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'moscow',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                    'can_subsidy': True,
                },
            },
        ],
    }


@pytest.mark.config(
    PARKS_ACTIVATION_RETRIEVE_HANDLER={
        'max_request_count': 1,
        'db_timeout_ms': 250,
    },
)
async def test_retrieve_many_ids(taxi_parks_activation):
    park_ids = ['wrong_id', 'another_wrong_id']
    response = await taxi_parks_activation.post(
        'v1/parks/activation/retrieve', json={'ids_in_set': park_ids},
    )
    assert response.status_code == 400
