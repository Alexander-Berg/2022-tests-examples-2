import pytest

from tests_cashbox_integration import utils


ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes'
PARK_ID = 'park_123'


@pytest.mark.parametrize('cashbox_id', ['id_abc123', 'id_abc789'])
async def test_delete_ok(taxi_cashbox_integration, pgsql, cashbox_id):
    cashbox_before = utils.get_cashboxes_by_id(pgsql, PARK_ID, [cashbox_id])

    response = await taxi_cashbox_integration.delete(
        ENDPOINT,
        params={'park_id': PARK_ID, 'id': cashbox_id},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
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
        pgsql,
        cashbox_id,
        expected_response,
        expected_code,
):
    response = await taxi_cashbox_integration.delete(
        ENDPOINT,
        params={'park_id': PARK_ID, 'id': cashbox_id},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
