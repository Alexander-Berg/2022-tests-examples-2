import http
import typing

import pytest

from test_eats_integration_offline_orders import conftest


DEFAULT_DATE_TO = '2022-05-17 18:00:00+03:00'
PLACES_INFO = {
    'place_id__1': {'place_name': 'Самый тестовый ресторан'},
    'place_id__2': {'place_name': 'Ресторан "Мясо"'},
    'place_id__3': {'place_name': 'Ресторан "Компот"'},
}


def _create_transaction(
        place_id: str,
        table_id: int,
        order_id: int,
        created_at: str,
        status: str = 'in_progress',
        payment_type: str = 'payture',
) -> typing.Dict:
    return {
        'front_uuid': f'front_uuid__{order_id}',
        'order_id': order_id,
        'order_items': conftest.ADMIN_TRANSACTION_ITEMS,
        'payment_type': payment_type,
        'place_id': place_id,
        'status': status,
        'table_id': table_id,
        'table_pos_id': f'table_id__{table_id}',
        'table_pos_name': f'table_id__{table_id}',
        'table_ya_id': str(table_id),
        'uuid': f'transaction_uuid__{order_id}',
        'created_at': created_at,
        'order_uuid': f'order_uuid__{order_id}',
        'amount': 0.43,
        **PLACES_INFO.get(place_id, {}),
    }


TRANSACTION_1 = _create_transaction(
    'place_id__1',
    table_id=1,
    order_id=1,
    created_at='2022-05-16T13:00:00+03:00',
    status='canceled',
)
TRANSACTION_2 = _create_transaction(
    'place_id__1',
    table_id=1,
    order_id=2,
    created_at='2022-05-16T12:00:00+03:00',
    payment_type='sbp',
)
TRANSACTION_3 = _create_transaction(
    'place_id__2',
    table_id=2,
    order_id=3,
    created_at='2022-05-15T12:30:00+03:00',
    status='success',
)
TRANSACTION_4 = _create_transaction(
    'place_id__2',
    table_id=2,
    order_id=4,
    created_at='2022-05-15T13:00:00+03:00',
    payment_type='sbp',
)
TRANSACTION_5 = _create_transaction(
    'place_id__3',
    table_id=3,
    order_id=5,
    created_at='2022-05-15T12:00:00+03:00',
    status='success',
    payment_type='badge',
)


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    (
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 2},
            http.HTTPStatus.OK,
            {
                'has_more': True,
                'transactions': [TRANSACTION_1, TRANSACTION_2],
                'total_count': 5,
            },
            id='limit',
        ),
        pytest.param(
            {
                'date_to': '2022-05-16 12:59:00+03:00',
                'date_from': '2022-05-16 11:59:00+03:00',
            },
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_2],
                'total_count': 1,
            },
            id='filters-date_from',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'limit': 1, 'offset': 1},
            http.HTTPStatus.OK,
            {
                'has_more': True,
                'transactions': [TRANSACTION_2],
                'total_count': 5,
            },
            id='offset',
        ),
        pytest.param(
            {'date_to': '2022-05-16 12:59:00+03:00', 'limit': 1},
            http.HTTPStatus.OK,
            {
                'has_more': True,
                'transactions': [TRANSACTION_2],
                'total_count': 4,
            },
            id='filters-date_to',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'place_id': 'place_id__2'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_4, TRANSACTION_3],
                'total_count': 2,
            },
            id='filters-place_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'table_id': 3},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_5],
                'total_count': 1,
            },
            id='filters-table_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'order_id': 4},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_4],
                'total_count': 1,
            },
            id='filters-order_id',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'order_uuid': 'order_uuid__3'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_3],
                'total_count': 1,
            },
            id='filters-order_uuid',
        ),
        pytest.param(
            {
                'date_to': DEFAULT_DATE_TO,
                'transaction_uuid': 'transaction_uuid__1',
            },
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_1],
                'total_count': 1,
            },
            id='filters-transaction_uuid',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'front_uuid': 'front_uuid__2'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_2],
                'total_count': 1,
            },
            id='filters-front_uuid',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'status': 'success'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_3, TRANSACTION_5],
                'total_count': 2,
            },
            id='filters-transactions_status',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'payment_type': 'sbp'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_2, TRANSACTION_4],
                'total_count': 2,
            },
            id='filters-payment_type',
        ),
        pytest.param(
            {'date_to': DEFAULT_DATE_TO, 'payment_type': 'sbp,badge'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'transactions': [TRANSACTION_2, TRANSACTION_4, TRANSACTION_5],
                'total_count': 3,
            },
            id='filters-payment_type-multiple',
        ),
        pytest.param(
            {'date_to': '1990-01-01 12:00:00'},
            http.HTTPStatus.OK,
            {'has_more': False, 'transactions': [], 'total_count': 0},
            id='no-data',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'payment_transactions.sql',
    ],
)
async def test_admin_transactions_list(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get(
        '/admin/v1/transactions/list', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
