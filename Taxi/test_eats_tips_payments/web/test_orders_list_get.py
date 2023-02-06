import typing

import pytest

from test_eats_tips_payments import conftest


def _format_request_params(
        recipient_ids: typing.Optional[typing.List[str]] = None,
        date_from: str = '2022-01-31T06:00:00',
        date_to: str = '2022-01-31T18:00:00',
        limit: int = 3,
        status: typing.Optional[str] = None,
):
    result = {
        'recipient_ids': recipient_ids or ['recipient_id_1'],
        'date_from': date_from,
        'date_to': date_to,
        'limit': limit,
        'status': status,
    }
    return dict(filter(lambda item: item[1] is not None, result.items()))


def _format_order(
        order_id: str,
        created_at: str,
        recipient_amount: str,
        place_id: typing.Optional[str],
        status: str,
):
    result = {
        'order_id': order_id,
        'created_at': created_at,
        'recipient_amount': {'price_value': recipient_amount},
        'recipient_id': 'recipient_id_1',
        'status': status,
        'place_id': place_id,
    }
    return dict(filter(lambda item: item[1] is not None, result.items()))


ORDER_1 = _format_order(
    'order_id_1', '2022-01-31T09:00:00+03:00', '47', 'place_id_1', 'COMPLETED',
)
ORDER_2 = _format_order(
    'order_id_2', '2022-01-31T10:00:00+03:00', '90', 'place_id_2', 'COMPLETED',
)
ORDER_3 = _format_order(
    'order_id_3', '2022-01-31T11:00:00+03:00', '180000.50', None, 'CREATED',
)


def _format_expected_response(*orders):
    return {'orders': list(orders)}


def make_pytest_param(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        request_params: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(request_params, _format_request_params()),
        conftest.value_or_default(
            expected_response,
            _format_expected_response(ORDER_3, ORDER_2, ORDER_1),
        ),
        id=id,
    )


@pytest.mark.parametrize(
    'request_params,expected_response',
    [
        make_pytest_param(id='success'),
        make_pytest_param(
            request_params=_format_request_params(limit=2),
            expected_response=_format_expected_response(ORDER_3, ORDER_2),
            id='small limit',
        ),
        make_pytest_param(
            request_params=_format_request_params(
                date_to='2022-01-31T10:30:00+03:00',
            ),
            expected_response=_format_expected_response(ORDER_2, ORDER_1),
            id='date_to differs',
        ),
        make_pytest_param(
            request_params=_format_request_params(
                date_from='2022-01-31T09:30:00+03:00',
            ),
            expected_response=_format_expected_response(ORDER_3, ORDER_2),
            id='date_from differs',
        ),
        make_pytest_param(
            request_params=_format_request_params(status='COMPLETED'),
            expected_response=_format_expected_response(ORDER_2, ORDER_1),
            id='completed only',
        ),
    ],
)
async def test_orders_list_get(
        taxi_eats_tips_payments_web,
        # params:
        request_params,
        expected_response,
):
    response = await taxi_eats_tips_payments_web.get(
        '/internal/v1/orders/list', params=request_params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
