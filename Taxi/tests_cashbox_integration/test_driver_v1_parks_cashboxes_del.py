import pytest

from tests_cashbox_integration import utils


ENDPOINT = '/driver/cashbox/v1/parks/cashboxes'
PARK_ID = 'park_123'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


@pytest.mark.parametrize('cashbox_id', ['id_abc123', 'id_abc789'])
async def test_delete_ok(
        taxi_cashbox_integration, pgsql, cashbox_id, fleet_parks,
):
    cashbox_before = utils.get_cashboxes_by_id(pgsql, PARK_ID, [cashbox_id])

    response = await taxi_cashbox_integration.delete(
        ENDPOINT, params={'id': cashbox_id}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {}

    cashbox_after = utils.get_cashboxes_by_id(pgsql, PARK_ID, [cashbox_id])
    assert cashbox_before[0].pop('date_updated') != cashbox_after[0].pop(
        'date_updated',
    )
    cashbox_before[0]['state'] = 'deleted'
    assert cashbox_before == cashbox_after


@pytest.mark.parametrize(
    'cashbox_id, expected_response, expected_code',
    [
        (
            'id_abc456',
            {
                'code': 'can_not_delete_current_cashbox',
                'message': 'can_not_delete_current_cashbox',
            },
            400,
        ),
        (
            'net_takogo',
            {'code': 'no_such_cashbox', 'message': 'no_such_cashbox'},
            404,
        ),
    ],
)
async def test_bad_request(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        cashbox_id,
        expected_response,
        expected_code,
):
    response = await taxi_cashbox_integration.delete(
        ENDPOINT, params={'id': cashbox_id}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response


async def test_not_self_assigned(
        taxi_cashbox_integration, fleet_parks, pgsql, mockserver,
):
    authorized_headers = AUTHORIZED_HEADERS
    authorized_headers['X-YaTaxi-Park-Id'] = 'big_park'

    response = await taxi_cashbox_integration.delete(
        ENDPOINT, params={'id': '1'}, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'not_self_assigned'
