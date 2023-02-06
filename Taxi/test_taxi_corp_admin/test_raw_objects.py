import datetime

import pytest

from taxi.clients import billing_v2
from taxi.clients import drive


@pytest.mark.parametrize(
    ['user_id', 'is_error', 'expected_result'],
    [
        (
            'user_id_1',
            False,
            {
                'drive.b2baccounts': {'result': 'result'},
                'client.getclientcontracts': [
                    {'result': '2020-02-02T00:00:00+00:00'},
                ],
            },
        ),
        (
            'user_id_1',
            True,
            {
                'drive.b2baccounts': {'error': 'Drive API error: error text'},
                'client.getclientcontracts': {
                    'error': (
                        'Request to billing failed. '
                        'billing_id: billing_id_1 exc: error text'
                    ),
                },
            },
        ),
    ],
)
async def test_raw_objects_user(
        taxi_corp_admin_client, patch, user_id, is_error, expected_result,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(*args, **kwargs):
        if is_error:
            raise billing_v2.BillingError('error text')
        return [{'result': datetime.datetime(2020, 2, 2)}]

    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'yandex_uid_1': 'drive_user_id_1'}]}

    @patch('taxi.clients.drive.DriveClient.accounts_by_user_id')
    async def _accounts_by_user_id(*args, **kwargs):
        if is_error:
            raise drive.BaseError('error text')
        return {'result': 'result'}

    response = await taxi_corp_admin_client.post(
        '/v1/clients/client_id_1/raw_objects/user',
        json={'user': {'user_id': user_id}},
    )

    assert response.status == 200
    assert (await response.json()) == expected_result
