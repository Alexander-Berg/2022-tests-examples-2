import pytest


ENDPOINT = 'v1/customers/names'

HEADERS = {'X-Park-ID': 'park_id'}


async def test_all_customers_have_names(taxi_fleet_customers):
    personal_phone_ids = [
        'existing_personal_phone_id',
        'existing_personal_phone_id1',
    ]

    response = await taxi_fleet_customers.post(
        ENDPOINT,
        json={'personal_phone_ids': personal_phone_ids},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'customers': [
            {
                'personal_phone_id': 'existing_personal_phone_id',
                'id': 'existing_customer_id',
                'name': 'existing_name',
            },
            {
                'personal_phone_id': 'existing_personal_phone_id1',
                'id': 'existing_customer_id1',
                'name': 'existing_name1',
            },
        ],
    }


async def test_one_customer_has_not_name(taxi_fleet_customers):
    personal_phone_ids = [
        'existing_personal_phone_id',
        'existing_personal_phone_id2',
    ]

    response = await taxi_fleet_customers.post(
        ENDPOINT,
        json={'personal_phone_ids': personal_phone_ids},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'customers': [
            {
                'personal_phone_id': 'existing_personal_phone_id',
                'id': 'existing_customer_id',
                'name': 'existing_name',
            },
            {
                'personal_phone_id': 'existing_personal_phone_id2',
                'id': 'existing_customer_id2',
            },
        ],
    }


@pytest.mark.parametrize(
    'personal_phone_ids',
    [
        ['existing_personal_phone_id', 'deleted_personal_phone_id'],
        ['existing_personal_phone_id', 'not_existing_personal_phone_id'],
        ['existing_personal_phone_id', 'personal_phone_id_other_park'],
    ],
)
async def test_one_customer_does_not_exist(
        taxi_fleet_customers, personal_phone_ids,
):
    response = await taxi_fleet_customers.post(
        ENDPOINT,
        json={'personal_phone_ids': personal_phone_ids},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'customers': [
            {
                'personal_phone_id': 'existing_personal_phone_id',
                'id': 'existing_customer_id',
                'name': 'existing_name',
            },
        ],
    }


@pytest.mark.parametrize(
    'personal_phone_ids',
    [
        ['deleted_personal_phone_id', 'not_existing_personal_phone_id'],
        ['not_existing_personal_phone_id', 'not_existing_personal_phone_id1'],
        ['not_existing_personal_phone_id', 'personal_phone_id_other_park'],
        ['deleted_personal_phone_id', 'personal_phone_id_other_park'],
    ],
)
async def test_all_customers_do_not_exist(
        taxi_fleet_customers, personal_phone_ids,
):
    response = await taxi_fleet_customers.post(
        ENDPOINT,
        json={'personal_phone_ids': personal_phone_ids},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'customers': []}
