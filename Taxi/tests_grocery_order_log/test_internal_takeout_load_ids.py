import datetime

import pytest

from tests_grocery_order_log import models


ORDERS = [
    {
        'order_id': '1',
        'yandex_uid': '1000',
        'order_created_date': datetime.datetime(2020, 3, 13),
    },
    {
        'order_id': '2',
        'yandex_uid': '1000',
        'order_created_date': datetime.datetime(2020, 4, 13),
    },
    {
        'order_id': '3',
        'yandex_uid': '1000',
        'order_created_date': datetime.datetime(2020, 5, 13),
        'order_type': 'eats',
    },
    {
        'order_id': '4',
        'yandex_uid': '1001',
        'order_created_date': datetime.datetime(2020, 6, 13),
    },
]


@pytest.fixture(name='internal_load_ids')
def _internal_load_ids(taxi_grocery_order_log):
    async def _inner(
            yandex_uid: str,
            till_dt: datetime.datetime = None,
            order_type: str = None,
            purpose: str = 'load',
            cursor: dict = None,
            status_code=200,
    ):
        till_dt = till_dt or datetime.datetime.now()
        if till_dt.tzinfo is None:
            till_dt = till_dt.replace(tzinfo=models.UTC_TZ)

        params = {}
        if order_type:
            params['order_type'] = order_type

        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/takeout/load-ids',
            json={
                'yandex_uid': yandex_uid,
                'till_dt': till_dt.isoformat(),
                'cursor': cursor,
                'purpose': purpose,
            },
            params=params,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.mark.parametrize(
    'request_data, expected_ids, expected_cursor',
    [
        pytest.param(
            dict(yandex_uid='1000'), ['1', '2', '3'], None, id='basic',
        ),
        pytest.param(
            dict(yandex_uid='1000', till_dt=datetime.datetime(2020, 4, 20)),
            ['1', '2'],
            None,
            id='with_till_dt',
        ),
        pytest.param(
            dict(yandex_uid='1000', cursor=dict(offset=1)),
            ['2', '3'],
            None,
            id='with_cursor',
        ),
        pytest.param(
            dict(yandex_uid='1000'),
            ['1', '2'],
            dict(offset=2),
            marks=pytest.mark.config(
                GROCERY_ORDER_LOG_TAKEOUT_LOAD_IDS_LIMIT=2,
            ),
            id='custom_limit',
        ),
        pytest.param(
            dict(yandex_uid='1000', cursor=dict(offset=2)),
            ['3'],
            None,
            marks=pytest.mark.config(
                GROCERY_ORDER_LOG_TAKEOUT_LOAD_IDS_LIMIT=2,
            ),
            id='custom_limit_with_offset',
        ),
        pytest.param(
            dict(yandex_uid='unknown'), [], None, id='unknown_yandex_uid',
        ),
        pytest.param(
            dict(yandex_uid='1000', order_type='eats'),
            ['3'],
            None,
            id='with_order_type',
        ),
    ],
)
async def test_basic(
        internal_load_ids, pgsql, request_data, expected_ids, expected_cursor,
):
    for order in ORDERS:
        models.OrderLogIndex(pgsql, **order).update_db()

    response = await internal_load_ids(**request_data)
    assert response.get('ids') == expected_ids
    assert response.get('cursor') == expected_cursor


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize('purpose', ('load', 'delete'))
async def test_filter_not_finished(internal_load_ids, pgsql, purpose):
    yandex_uid = 'yandex_uid'

    order_log_index = models.OrderLogIndex(
        pgsql=pgsql,
        yandex_uid=yandex_uid,
        order_state='created',
        order_created_date=models.NOW_DT,
    )
    order_log_index.update_db()

    response = await internal_load_ids(yandex_uid=yandex_uid, purpose=purpose)

    has_order = purpose == 'load'
    assert len(response['ids']) == int(has_order)
