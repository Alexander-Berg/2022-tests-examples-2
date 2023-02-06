import pytest

from tests_bank_topup import common
from .test_topup import (  # pylint: disable=C5521
    _default_bank_core_statement_response,
)
from .test_topup import default_headers  # pylint: disable=C5521
from .test_topup import get_v1_handle_info  # pylint: disable=C5521
from .test_topup import get_v2_handle_info  # pylint: disable=C5521
from .test_topup import json_mock_trust  # pylint: disable=C5521


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_default_currency_precision(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json = handle_info.body
    json['money']['amount'] = '1000.99'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_empty_wallet(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    json = handle_info.body
    json['money']['wallet_id'] = ''
    json['agreement_id'] = ''
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert not bank_core_agreement_mock.get_accessor_handler.has_calls
    assert response.status_code == 400
    assert not bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_core_agreement_404(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    bank_core_agreement_mock.set_http_status_code(404)
    if handle_info.version == 2:
        bank_core_agreement_mock.set_agreement_response(
            {'code': '404', 'message': 'NotFound'},
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json = handle_info.body
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert response.status_code == 404
    assert not bank_core_statement_mock.balance_handler_has_calls()


async def test_wallet_not_found_in_list(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
):
    handle_info = get_v1_handle_info()
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json = handle_info.body
    json['money']['wallet_id'] = 'unknown_wallet'

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert response.status_code == 404
    assert not bank_core_statement_mock.balance_handler_has_calls()


async def test_absent_public_agreement_id_in_accessor(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
):
    handle_info = get_v1_handle_info()
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    bank_core_agreement_mock.set_accessors_response(
        {
            'accessors': [
                {
                    'accessor_id': common.TEST_WALLET_ID,
                    'buid': 'buid',
                    'agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
                    'accessor_type': 'WALLET',
                    'currency': 'RUB',
                },
            ],
        },
    )

    json = handle_info.body
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert response.status_code == 500
    assert not bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_no_wallet_with_currency(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    if handle_info.version == 1:
        bank_core_agreement_mock.set_accessors_response(
            {
                'accessors': [
                    {
                        'accessor_id': common.TEST_WALLET_ID,
                        'buid': 'buid',
                        'agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
                        'accessor_type': 'WALLET',
                        'currency': 'USD',
                    },
                ],
            },
        )
    elif handle_info.version == 2:
        bank_core_agreement_mock.set_agreement_response(
            {
                'agreement_id': common.DEFAULT_AGREEMENT_ID,
                'public_agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
                'buid': 'buid',
                'product': 'WALLET',
                'currency': 'USD',
            },
        )

    json = handle_info.body
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json,
    )

    assert response.status_code == 404
    assert not bank_core_statement_mock.balance_handler_has_calls()
