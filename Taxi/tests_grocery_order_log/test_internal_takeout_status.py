import datetime

import pytest

from tests_grocery_order_log import models


@pytest.fixture(name='internal_status')
def _internal_status(taxi_grocery_order_log):
    async def _inner(
            yandex_uids: list,
            till_dt: datetime.datetime = None,
            order_type: str = None,
            status_code=200,
    ):
        till_dt = till_dt or datetime.datetime.now()
        if till_dt.tzinfo is None:
            till_dt = till_dt.replace(tzinfo=models.UTC_TZ)

        params = {}
        if order_type:
            params['order_type'] = order_type

        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/takeout/status',
            json={'yandex_uids': yandex_uids, 'till_dt': till_dt.isoformat()},
            params=params,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.mark.parametrize(
    'request_uids, expected_status',
    [
        (['yandex_uid'], 'ready_to_delete'),
        (['yandex_uid', 'unknown'], 'ready_to_delete'),
        (['unknown'], 'empty'),
    ],
)
async def test_basic(internal_status, pgsql, request_uids, expected_status):
    order_log_index = models.OrderLogIndex(
        pgsql=pgsql, yandex_uid='yandex_uid',
    )
    order_log_index.update_db()

    response = await internal_status(yandex_uids=request_uids)
    assert response['status'] == expected_status


@pytest.mark.parametrize(
    'order_state, expected_status',
    [
        pytest.param('created', 'empty'),
        pytest.param('assembling', 'empty'),
        pytest.param('delivering', 'empty'),
        pytest.param('returned', 'empty'),
        pytest.param('closed', 'ready_to_delete'),
        pytest.param('canceled', 'ready_to_delete'),
        pytest.param(
            'created',
            'ready_to_delete',
            marks=pytest.mark.config(
                GROCERY_ORDER_LOG_TAKEOUT_NOT_FINISHED_LIFETIME=1,
            ),
        ),
    ],
)
@pytest.mark.now(models.NOW)
@pytest.mark.config(GROCERY_ORDER_LOG_TAKEOUT_NOT_FINISHED_LIFETIME=2)
async def test_filter_not_finished(
        internal_status, pgsql, order_state, expected_status,
):
    yandex_uid = 'yandex_uid'

    order_log_index = models.OrderLogIndex(
        pgsql=pgsql,
        yandex_uid=yandex_uid,
        order_state=order_state,
        order_created_date=models.NOW_DT - datetime.timedelta(hours=2),
    )
    order_log_index.update_db()

    response = await internal_status([yandex_uid])
    assert response['status'] == expected_status
