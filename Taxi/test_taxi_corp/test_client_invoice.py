# pylint: disable=redefined-outer-name

import asyncio

import aiohttp
import pytest

from taxi.clients import billing_v2

from taxi_corp.api.common import codes


INVOICE_EXTERNAL_URL = 'https://invoice_external_url'
INVOICE_INTERNAL_URL = 'https://invoice_internal_url'
REQUEST_ID = 12345


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_result'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 70000, 'contract_id': 123},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 2000.50, 'contract_id': 123},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
        (
            'prepaid_drive',
            {'value': 1000.50, 'contract_id': 234},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
        (
            'prepaid_cargo',
            {'value': 1000.50, 'contract_id': 345},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
        (
            'tanker_cc',
            {'value': 1000.50, 'contract_id': 678},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
        (
            'tanker',
            {'value': 1000.50, 'contract_id': 789},
            {'invoice_url': INVOICE_EXTERNAL_URL},
        ),
    ],
)
async def test_single_post(
        taxi_corp_auth_client,
        patch,
        load_json,
        mock_corp_clients,
        client_id,
        post_content,
        expected_result,
):
    contracts = load_json('corp_clients_response.json').get(client_id, {})
    mock_corp_clients.data.get_contracts_response = contracts

    @patch('taxi.clients.billing_v2.BalanceClient.get_orders_info')
    async def _get_orders_info(contract_id, **kwargs):
        expected_id = str(post_content['contract_id'])
        assert contract_id == expected_id
        return [
            {'ServiceID': 'service_id', 'ServiceOrderID': 'service_order_id'},
        ]

    @patch('taxi.clients.billing_v2.BalanceClient.create_prepay_invoice')
    async def _create_prepay_invoice(*args, **kwargs):
        return billing_v2.PrepayInvoice('', INVOICE_EXTERNAL_URL, '')

    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/invoice'.format(client_id), json=post_content,
    )

    assert response.status == 200
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    [
        'client_id',
        'post_content',
        'expected_response_code',
        'expected_error_codes',
    ],
    [
        # invoice - zero value
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 0, 'contract_id': 123},
            400,
            [codes.GENERAL_ERROR.error_code],
        ),
        # invoice - negative value
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': -500, 'contract_id': 123},
            400,
            [codes.GENERAL_ERROR.error_code],
        ),
        # invoice - non float value
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': '1000a', 'contract_id': 123},
            400,
            [codes.GENERAL_ERROR.error_code],
        ),
        # invoice - non float value
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 40802810223530000000, 'contract_id': 123},
            400,
            [codes.GENERAL_ERROR.error_code],
        ),
        # invoice - client without billing_id
        (
            'b5d5ee2003fe4691b9b544645be7f3ca',
            {'value': 1000, 'contract_id': 123},
            406,
            [codes.INVOICE_BILLING_ID_IS_ABSENT.error_code],
        ),
        # invoice - non prepaid contract
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 1000, 'contract_id': 456},
            406,
            [codes.INVOICE_ONLY_PREPAID_CLIENTS.error_code],
        ),
        # invoice - empty contracts
        (
            'c1bca5657fcc4c2b945e3ea7d7a44c7f',
            {'value': 1000, 'contract_id': 000},
            406,
            [codes.INVOICE_CLIENT_DOESNT_HAVE_CONTRACT.error_code],
        ),
        # invoice - any billing_v2 error
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 1000, 'contract_id': 123},
            500,
            [codes.INVOICE_BILLING_ERROR.error_code],
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.invoice_billing_error': {'ru': '_'},
        'error.invoice_client_doesnt_have_contract': {'ru': '_'},
        'error.invoice_only_prepaid_clients': {'ru': '_'},
        'error.invoice_billing_id_is_absent': {'ru': '_'},
    },
)
async def test_single_post_fail(
        taxi_corp_auth_client,
        patch,
        load_json,
        mock_corp_clients,
        client_id,
        post_content,
        expected_response_code,
        expected_error_codes,
):
    contracts = load_json('corp_clients_response.json').get(
        client_id, {'contracts': []},
    )
    mock_corp_clients.data.get_contracts_response = contracts

    @patch('taxi.clients.billing_v2.' 'BalanceClient.get_orders_info')
    async def _get_orders_info(contract_id, log_extra=None):
        raise billing_v2.BillingError()

    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/invoice'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == expected_response_code, response_json

    error_codes = [error['code'] for error in response_json['errors']]
    assert error_codes == expected_error_codes, error_codes


@pytest.mark.parametrize(
    [
        'client_id',
        'post_content',
        'expected_response_code',
        'error_to_raise',
        'expected_error_codes',
    ],
    [
        # invoice - new billing_v2 errors
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 2000.50, 'contract_id': 123},
            500,
            asyncio.TimeoutError,
            [codes.BILLING_UNAVAILABLE.error_code],
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'value': 2000.50, 'contract_id': 123},
            500,
            aiohttp.ClientError,
            [codes.BILLING_UNAVAILABLE.error_code],
        ),
    ],
)
@pytest.mark.translations(corp={'error.billing_unavailable': {'ru': '_'}})
async def test_single_post_billing_fail(
        taxi_corp_auth_client,
        patch,
        load_json,
        mock_corp_clients,
        load,
        client_id,
        post_content,
        expected_response_code,
        error_to_raise,
        expected_error_codes,
):
    @patch('taxi.clients.billing_v2.' 'BalanceClient.get_orders_info')
    async def _get_orders_info(contract_id, log_extra=None):
        raise error_to_raise

    contracts = load_json('corp_clients_response.json').get(
        client_id, {'contracts': []},
    )
    mock_corp_clients.data.get_contracts_response = contracts

    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/invoice'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == expected_response_code, response_json

    error_codes = [error['code'] for error in response_json['errors']]
    assert error_codes == expected_error_codes, error_codes
