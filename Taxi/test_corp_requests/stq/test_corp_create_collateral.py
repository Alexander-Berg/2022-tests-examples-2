# pylint: disable=redefined-outer-name
import datetime

import pytest

from corp_requests import consts
from corp_requests.stq import corp_create_collateral

SERVICE_UPDATE = {'is_active': True, 'is_visible': True}

NOW = datetime.datetime.now().replace(microsecond=0)


@pytest.fixture
def mock_balance(mockserver, patch, load_json):
    class MockBalance:
        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.create_collateral')
        async def create_collateral(*args, **kwargs):
            return

        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
        async def create_offer(*args, **kwargs):
            return {'EXTERNAL_ID': 'EXTERNAL_ID', 'ID': 'TANKER_CONTRACT_ID'}

        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
        async def client_contracts(*args, **kwargs):
            contracts = load_json('balance_contracts.json')
            return contracts[kwargs['client_id']]

    return MockBalance()


@pytest.mark.parametrize(
    [
        'collateral_id',
        'expected_create_offer',
        'expected_create_collateral',
        'updated_services',
    ],
    [
        pytest.param(
            'collateral_id_1',
            [],
            [
                {
                    'operator_id': '0',
                    'contract_id': 123456,
                    'collateral_type': 1001,
                    'services': [650, 668, 672],
                    'sign': 1,
                    'print_form_type': 3,
                    'memo': 'ДС о переходе на единый договор создан автоматически LEGALTAXI-4823',  # noqa: E501
                    'num': 'Ф-б/н',
                },
            ],
            {'drive': 1, 'eats2': 1, 'tanker': 0},
            id='common',
        ),
        pytest.param(
            'collateral_id_2',
            [
                {
                    'operator_uid': '0',
                    'client_id': 'billing_id_2',
                    'person_id': 'person_id_2',
                    'services': [636],
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'country': 225,
                    'region': 225,
                    'firm_id': 124,
                    'currency': 'RUB',
                },
            ],
            [
                {
                    'operator_id': '0',
                    'contract_id': 234567,
                    'collateral_type': 1101,
                    'services': [650, 668, 672, 1171],
                    'link_contract_id': 'TANKER_CONTRACT_ID',
                    'sign': 1,
                    'print_form_type': 3,
                    'memo': 'Д/с на привязку Заправок к ЕД LEGALTAXI-16062',
                    'num': 'Ф-б/н',
                },
            ],
            {'drive': 0, 'eats2': 0, 'tanker': 1},
            id='tanker',
        ),
        pytest.param(
            'collateral_id_3',
            [
                {
                    'operator_uid': '0',
                    'client_id': 'billing_id_3',
                    'person_id': 'person_id_3',
                    'services': [636],
                    'manager_uid': 123456789,
                    'payment_type': 2,
                    'country': 225,
                    'region': 225,
                    'firm_id': 124,
                    'currency': 'RUB',
                },
            ],
            [
                {
                    'operator_id': '0',
                    'contract_id': 345678,
                    'collateral_type': 1001,
                    'services': [135, 650, 668, 672],
                    'sign': 1,
                    'print_form_type': 3,
                    'memo': 'ДС о переходе на единый договор создан автоматически LEGALTAXI-4823',  # noqa: E501
                    'num': 'Ф-б/н',
                },
                {
                    'operator_id': '0',
                    'contract_id': 345678,
                    'collateral_type': 1101,
                    'services': [135, 650, 668, 672, 1171],
                    'link_contract_id': 'TANKER_CONTRACT_ID',
                    'sign': 1,
                    'print_form_type': 3,
                    'memo': 'Д/с на привязку Заправок к ЕД LEGALTAXI-16062',
                    'num': 'Ф-б/н',
                },
            ],
            {'drive': 1, 'eats2': 1, 'tanker': 1},
            id='common_tanker',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CORP_OFFER_BALANCE_MANAGER_UIDS={'rus': {'__default__': [123456789]}},
)
async def test_corp_create_collateral(
        db,
        stq3_context,
        stq,
        collateral_id,
        expected_create_offer,
        expected_create_collateral,
        updated_services,
        mock_corp_clients,
        mock_balance,
):
    collateral = await db.corp_collaterals.find_one({'_id': collateral_id})

    await corp_create_collateral.task(stq3_context, collateral=collateral)

    _create_offer_calls = [
        c['kwargs'] for c in mock_balance.create_offer.calls
    ]
    assert _create_offer_calls == expected_create_offer

    _create_collateral_calls = [
        c['kwargs'] for c in mock_balance.create_collateral.calls
    ]
    assert _create_collateral_calls == expected_create_collateral

    assert (
        mock_corp_clients.service_eats2.times_called
        == updated_services['eats2']
    )
    if updated_services['eats2']:
        assert (
            mock_corp_clients.service_eats2.next_call()['request'].json
            == SERVICE_UPDATE
        )

    assert (
        mock_corp_clients.service_drive.times_called
        == updated_services['drive']
    )
    if updated_services['drive']:
        assert (
            mock_corp_clients.service_drive.next_call()['request'].json
            == SERVICE_UPDATE
        )

    assert (
        mock_corp_clients.service_tanker.times_called
        == updated_services['tanker']
    )
    if updated_services['tanker']:
        assert (
            mock_corp_clients.service_tanker.next_call()['request'].json
            == SERVICE_UPDATE
        )

    updated_collateral = await db.corp_collaterals.find_one(
        {'_id': collateral_id},
    )
    assert updated_collateral['status'] == consts.CollateralStatus.ACCEPTED

    assert stq.corp_sync_contracts_info.times_called == 1
    assert stq.corp_sync_contracts_info.next_call()['kwargs'] == {
        'client_id': collateral['client_id'],
        'billing_client_id': collateral['billing_id'],
    }


@pytest.mark.parametrize(
    ['collateral_id'],
    [
        pytest.param('collateral_id_4', id='common'),
        pytest.param('collateral_id_5', id='tanker'),
        pytest.param('collateral_id_6', id='common_tanker'),
    ],
)
async def test_corp_create_collateral_fail(
        db, stq3_context, collateral_id, mock_balance,
):
    collateral = await db.corp_collaterals.find_one({'_id': collateral_id})

    await corp_create_collateral.task(stq3_context, collateral=collateral)
    updated_collateral = await db.corp_collaterals.find_one(
        {'_id': collateral_id},
    )
    assert updated_collateral['status'] == consts.CollateralStatus.FAILED
    assert (
        updated_collateral['last_error']['error']
        == consts.TankerErrors.SERVICE_EXISTS_ERROR.value
    )
