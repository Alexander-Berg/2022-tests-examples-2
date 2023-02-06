import http
import typing

import pytest

from test_eats_integration_offline_orders import conftest

DEFAULT_DATE_TO = '2022-05-17 18:00:00'

PLACES_INFO = {
    'place_id__1': {'place_name': 'Самый тестовый ресторан'},
    'place_id__2': {'place_name': 'Ресторан "Мясо"'},
}


def _create_order(
        order_id: int,
        created_at: str,
        table_id: int,
        place_id: str,
        service_fee: float = 0.0,
        waiter_id: typing.Optional[str] = None,
        status: typing.Optional[str] = None,
        mark_status: typing.Optional[str] = 'success',
) -> typing.Dict:
    result = {
        'created_at': created_at,
        'id': order_id,
        'items': conftest.ADMIN_ORDER_ITEMS,
        'place_id': place_id,
        'service_fee': service_fee,
        'table_id': table_id,
        'table_pos_id': f'table_id__{table_id}',
        'table_pos_name': f'table_id__{table_id}',
        'table_ya_id': str(table_id),
        'uuid': f'order_uuid__{order_id}',
        'inner_id': f'inner_id__{order_id}',
        'status': status,
        'mark_status': mark_status,
        'amount': 0.43,
        'in_pay_amount': 0.33,
        'paid_amount': 0.0,
        'base_amount': 0.43,
        **PLACES_INFO.get(place_id, {}),
    }
    if waiter_id:
        result['waiter_id'] = waiter_id
    if mark_status is not None:
        result['mark_status'] = mark_status
    return result


ORDER_1 = _create_order(
    1, '2022-05-16T13:00:00+03:00', 1, 'place_id__1', status='paid',
)
ORDER_2 = _create_order(
    2, '2022-05-16T12:00:00+03:00', 1, 'place_id__1', status='closed',
)
ORDER_3 = _create_order(
    3,
    '2022-05-15T12:30:00+03:00',
    1,
    'place_id__1',
    waiter_id='waiter_id__1',
    status='created',
)
ORDER_4 = _create_order(
    4,
    '2022-05-15T13:00:00+03:00',
    2,
    'place_id__2',
    status='paid',
    mark_status='error',
)
ORDER_5 = _create_order(
    5, '2022-05-15T12:00:00+03:00', 2, 'place_id__2', status='new',
)


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    (
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 2},
            http.HTTPStatus.OK,
            {'has_more': True, 'orders': [ORDER_1, ORDER_2]},
            id='limit',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 1, 'offset': 1},
            http.HTTPStatus.OK,
            {'has_more': True, 'orders': [ORDER_2]},
            id='offset',
        ),
        pytest.param(
            {'date_to': '2022-05-16 12:59:00+03:00', 'limit': 1},
            http.HTTPStatus.OK,
            {'has_more': True, 'orders': [ORDER_2]},
            id='filters-date_to',
        ),
        pytest.param(
            {
                'date_to': '2022-05-16 12:59:00+03:00',
                'date_from': '2022-05-16 11:59:00+03:00',
            },
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_2]},
            id='filters-date_from',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'place_id': 'place_id__2'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_4, ORDER_5]},
            id='filters-place_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'table_id': 2},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_4, ORDER_5]},
            id='filters-table_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'order_uuid': 'order_uuid__4'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_4]},
            id='filters-order_uuid',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'order_id': 5},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_5]},
            id='filters-order_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'inner_id': 'inner_id__2'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_2]},
            id='filters-inner_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'waiter_id': 'waiter_id__1'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_3]},
            id='filters-waiter_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'status': 'paid'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_1, ORDER_4]},
            id='filters-status-paid',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'status': 'created,closed'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_2, ORDER_3]},
            id='filters-status-few',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'mark_status': 'error'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': [ORDER_4]},
            id='filters-mark_status',
        ),
        pytest.param(
            {'date_to': '1990-01-01 12:00:00'},
            http.HTTPStatus.OK,
            {'has_more': False, 'orders': []},
            id='no-data',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders.sql'],
)
@pytest.mark.now('2022-05-16T10:00:30+00:00')
async def test_admin_orders_list(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get('/admin/v1/orders/list', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
