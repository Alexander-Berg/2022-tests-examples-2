import pytest

from tests_fleet_customers import utils


ENDPOINT_DELETE = 'v1/takeout/delete'


@pytest.mark.parametrize(
    'personal_phone_ids',
    [
        ['existing_personal_phone_id'],
        ['existing_personal_phone_id', 'existing_personal_phone_id1'],
        ['existing_personal_phone_id', 'deleted_personal_phone_id'],
        ['existing_personal_phone_id', 'not_existing_personal_phone_id'],
    ],
)
async def test_success_has_customers_data(
        taxi_fleet_customers, pgsql, personal_phone_ids,
):
    body_request = {
        'request_id': 'request_id',
        'yandex_uids': [{'uid': 'yandex_uid', 'is_portal': True}],
        'personal_phone_ids': personal_phone_ids,
    }

    assert utils.has_customers_with_phone_ids(pgsql, personal_phone_ids)

    response = await taxi_fleet_customers.delete(
        ENDPOINT_DELETE, json=body_request,
    )
    assert response.status_code == 200

    assert not utils.has_customers_with_phone_ids(pgsql, personal_phone_ids)


@pytest.mark.parametrize(
    'personal_phone_ids',
    [
        ['deleted_personal_phone_id', 'not_existing_personal_phone_id'],
        ['not_existing_personal_phone_id', 'not_existing_personal_phone_id1'],
        ['not_existing_personal_phone_id1'],
        ['deleted_personal_phone_id'],
        None,
    ],
)
async def test_success_has_not_customers_data(
        taxi_fleet_customers, pgsql, personal_phone_ids,
):
    body_request = {
        'request_id': 'request_id',
        'yandex_uids': [{'uid': 'yandex_uid', 'is_portal': True}],
        'personal_phone_ids': personal_phone_ids,
    }

    assert not utils.has_customers_with_phone_ids(pgsql, personal_phone_ids)

    response = await taxi_fleet_customers.delete(
        ENDPOINT_DELETE, json=body_request,
    )
    assert response.status_code == 200

    assert not utils.has_customers_with_phone_ids(pgsql, personal_phone_ids)
