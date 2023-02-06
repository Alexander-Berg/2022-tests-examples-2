import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

from test_eats_tips_admin import conftest


def _format_request_params():
    return {
        'date_from': '2021-11-21T00:00:00+03:00',
        'date_to': '2021-11-22T00:00:00+03:00',
    }


def _format_headers(jwt=conftest.JWT_USER_1):
    return {'X-Chaevie-Token': jwt}


def _format_expected_response(amount):
    return {'amount': {'price_value': amount}}


def make_pytest_param(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        request_params: typing.Any = conftest.SENTINEL,
        request_headers: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(request_params, _format_request_params()),
        conftest.value_or_default(request_headers, _format_headers()),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(
            expected_response, _format_expected_response(amount='300.00'),
        ),
        id=id,
    )


@pytest.mark.parametrize(
    (
        'request_params',
        'request_headers',
        'expected_status',
        'expected_response',
    ),
    [make_pytest_param(id='success')],
)
async def test_get_transactions(
        taxi_eats_tips_admin_web,
        mock_eats_tips_payments,
        mock_eats_tips_partners,
        # params:
        request_params,
        request_headers,
        expected_status,
        expected_response,
):
    @mock_eats_tips_payments('/internal/v1/orders/list')
    async def _mock_v1_orders_list(request: http.Request):
        assert request.query['recipient_ids'] == conftest.USER_ID_1
        assert request.query['date_from'] == '2021-11-21T00:00:00+03:00'
        assert request.query['date_to'] == '2021-11-22T00:00:00+03:00'
        assert request.query['status'] == 'COMPLETED'
        return web.json_response(
            {
                'orders': [
                    {
                        'order_id': 'a77402b0-d792-4b74-b57c-5bf429b15001',
                        'recipient_id': conftest.USER_ID_1,
                        'created_at': '2021-11-21T20:50:00+03:00',
                        'recipient_amount': {'price_value': '100.00'},
                        'status': 'COMPLETED',
                    },
                    {
                        'order_id': 'adef44d8-55c1-429c-841d-912bf7cc3351',
                        'recipient_id': conftest.USER_ID_1,
                        'created_at': '2021-11-21T20:50:00+03:00',
                        'recipient_amount': {'price_value': '200.00'},
                        'status': 'COMPLETED',
                    },
                ],
            },
            status=200,
        )

    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request: http.Request):
        return web.json_response({'id': conftest.USER_ID_1, 'alias': '1'})

    response = await taxi_eats_tips_admin_web.get(
        '/v1/recipient/income', params=request_params, headers=request_headers,
    )
    assert response.status == expected_status
    assert await response.json() == expected_response
