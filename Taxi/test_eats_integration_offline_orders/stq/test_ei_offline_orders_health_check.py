import datetime

from aiohttp import web
import asynctest
import pytest

from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)
from eats_integration_offline_orders.stq import pos_health_check
SAME_SAVED_ORDERS = [
    {
        'order_uuid': 'order_uuid__1',
        'table_pos_id': 'table_id__1',
        'place_id': 'place_id__1',
        'created_at': datetime.datetime(
            2022, 5, 15, 12, 0, tzinfo=datetime.timezone.utc,
        ),
    },
    {
        'order_uuid': 'order_uuid__2',
        'table_pos_id': 'table_id__2',
        'place_id': 'place_id__1',
        'created_at': datetime.datetime(
            2022, 5, 15, 12, 20, tzinfo=datetime.timezone.utc,
        ),
    },
]
FAIL_CHECK_STAT = {
    'kind': 'IGAUGE',
    'labels': {'event': 'fail', 'sensor': 'pos_health_check'},
    'timestamp': None,
    'value': 1,
}
SUCCESS_CHECK_STAT = {
    'kind': 'IGAUGE',
    'labels': {'event': 'success', 'sensor': 'pos_health_check'},
    'timestamp': None,
    'value': 1,
}
UNAVAILABLE_CHECK_STAT = {
    'kind': 'IGAUGE',
    'labels': {'event': 'rest_unavailable', 'sensor': 'pos_health_check'},
    'timestamp': None,
    'value': 1,
}


@pytest.mark.parametrize(
    'pos_type, place_id, table_pos_id, file_name, expected_stats, '
    'expected_rest_last_time_table_check, expected_saved_orders',
    (
        pytest.param(
            'iiko',
            'place_id__1',
            'table_id__1',
            'answer_with_old_order',
            [SUCCESS_CHECK_STAT],
            datetime.datetime(
                2022, 5, 15, 12, 30, tzinfo=datetime.timezone.utc,
            ),
            SAME_SAVED_ORDERS,
            id='answer with old order',
        ),
        pytest.param(
            'iiko',
            'place_id__1',
            'table_id__1',
            'answer_with_new_order',
            [SUCCESS_CHECK_STAT],
            datetime.datetime(
                2022, 5, 15, 12, 30, tzinfo=datetime.timezone.utc,
            ),
            [
                {
                    'order_uuid': 'order_uuid__1',
                    'table_pos_id': 'table_id__1',
                    'place_id': 'place_id__1',
                    'created_at': datetime.datetime(
                        2022, 5, 15, 12, 0, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'order_uuid': 'order_uuid__2',
                    'table_pos_id': 'table_id__2',
                    'place_id': 'place_id__1',
                    'created_at': datetime.datetime(
                        2022, 5, 15, 12, 20, tzinfo=datetime.timezone.utc,
                    ),
                },
                {
                    'order_uuid': 'order_uuid__3',
                    'table_pos_id': 'table_id__1',
                    'place_id': 'place_id__1',
                    'created_at': datetime.datetime(
                        2022, 5, 15, 12, 30, tzinfo=datetime.timezone.utc,
                    ),
                },
            ],
            id='answer with new order',
        ),
        pytest.param(
            'iiko',
            'place_id__1',
            'table_id__2',
            'answer_with_no_order',
            [SUCCESS_CHECK_STAT],
            datetime.datetime(
                2022, 5, 15, 12, 30, tzinfo=datetime.timezone.utc,
            ),
            SAME_SAVED_ORDERS,
            id='answer with no order',
        ),
        pytest.param(
            'iiko',
            'place_id__1',
            'table_id__2',
            None,
            [FAIL_CHECK_STAT],
            datetime.datetime(
                2022, 5, 15, 12, 20, tzinfo=datetime.timezone.utc,
            ),
            SAME_SAVED_ORDERS,
            id='no answer',
        ),
        pytest.param(
            'rkeeper',
            'place_id__2',
            'table_id__3',
            None,
            [FAIL_CHECK_STAT, UNAVAILABLE_CHECK_STAT],
            datetime.datetime(2022, 5, 15, 9, tzinfo=datetime.timezone.utc),
            SAME_SAVED_ORDERS,
            id='no answer too long',
        ),
    ),
)
@pytest.mark.now('2022-05-15T15:30:00.0+03:00')
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'restaurants.sql', 'partners_table_orders.sql'],
)
async def test_ei_offline_orders_health_check(
        stq3_context,
        mockserver,
        load_json,
        pos_client_mock,
        get_stats_by_label_values,
        stq,
        pos_type,
        place_id,
        table_pos_id,
        file_name,
        expected_stats,
        expected_rest_last_time_table_check,
        expected_saved_orders,
):
    if file_name:
        pos_client_mock.get_check = asynctest.CoroutineMock(
            return_value=api_module.PosOrders.deserialize(
                data=load_json(f'{file_name}.json'),
            ),
        )
    else:
        pos_client_mock.get_check = asynctest.CoroutineMock(
            side_effect=web.HTTPRequestTimeout,
        )

    await pos_health_check.task(
        context=stq3_context,
        pos_type=pos_type,
        place_id=place_id,
        table_pos_id=table_pos_id,
    )

    rest_last_time_table_check = await stq3_context.pg.secondary.fetchval(
        f'SELECT last_time_table_check FROM restaurants where place_id=$1;',
        place_id,
    )
    assert rest_last_time_table_check == expected_rest_last_time_table_check

    saved_orders = await stq3_context.pg.secondary.fetch(
        f'SELECT * FROM partners_table_orders;',
    )
    if len(saved_orders) == 2:
        assert [dict(row) for row in saved_orders] == expected_saved_orders
    else:
        assert len(saved_orders) == len(expected_saved_orders)
        assert [dict(row) for row in saved_orders][
            :2
        ] == expected_saved_orders[:2]

    stats = get_stats_by_label_values(
        stq3_context, {'sensor': pos_health_check.SENSOR_NAME},
    )
    assert stats == expected_stats
