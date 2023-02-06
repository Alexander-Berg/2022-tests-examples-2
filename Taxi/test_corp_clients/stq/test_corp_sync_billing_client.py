import logging

import pytest

from corp_clients.stq import corp_sync_client_info


logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ['billing_id', 'client_id'], [pytest.param('billing_1', 'client_1')],
)
async def test_sync_billing_client_info(
        patch, mock_corp_edo, db, stq3_context, stq, billing_id, client_id,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(*args, **kwargs):
        return [
            {
                'SERVICES': [650],
                'EXTERNAL_ID': 'taxi_contract',
                'ID': 1,
                'IS_ACTIVE': 1,
                'PERSON_ID': 1,
                'CURRENCY': 'RUR',
                'CONTRACT_TYPE': 9,
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'FIRM_ID': 13,
            },
            {
                'SERVICES': [1173],
                'EXTERNAL_ID': 'market_contract',
                'ID': 2,
                'IS_ACTIVE': 1,
                'PERSON_ID': 1,
                'CURRENCY': 'RUR',
                'CONTRACT_TYPE': 9,
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'FIRM_ID': 111,
            },
        ]

    await corp_sync_client_info.task(
        stq3_context, billing_client_id=billing_id, client_id=client_id,
    )
    new_client = await db.corp_clients.find_one(
        {'_id': client_id},
        projection={
            'updated': False,
            'updated_at': False,
            'created': False,
            'yandex_id': False,
            'yandex_login': False,
            'yandex_login_id': False,
        },
    )

    assert new_client == {'_id': client_id, 'billing_id': billing_id}
