import asyncio
import heapq

import dateutil
import pytest

from . import utils


async def stq_submit_order(stq_runner, order):
    await stq_runner.routehistory_grocery_order_add.call(
        task_id=order['order_id'], kwargs={'order': order}, expect_fail=False,
    )


def fetch_db_orders(pgsql):
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)
    cursor.execute(
        'SELECT yandex_uid, created, protobuf_data '
        'FROM routehistory.grocery_order '
        'ORDER BY yandex_uid, created',
    )
    result = cursor.fetchall()
    result = utils.convert_pg_result(result)
    return result


@pytest.mark.parametrize(
    'yandex_uid,min_created,max_records',
    [
        ('111111', None, None),
        ('222222', None, None),
        ('333333', None, None),
        ('222222', None, 2),
        ('222222', '2020-04-02T00:00:00+0000', None),
        ('222222', '2020-05-01T00:00:00+0000', None),
    ],
)
@pytest.mark.parametrize(
    'has_comment',
    [
        pytest.param(True),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    ROUTEHISTORY_TRUNCATE_GROCERY_COMMENT={
                        'enabled': True,
                        'threshold': 0,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2010-01-01T00:00:00+0000')
async def test_stq_grocery_add(
        session_stq_filler,
        orders,
        taxi_routehistory,
        yandex_uid,
        min_created,
        max_records,
        has_comment,
):
    request_body = {
        k: v
        for k, v in (
            (k, locals().get(k)) for k in ('min_created', 'max_records')
        )
        if v is not None
    }
    response = await taxi_routehistory.post(
        'routehistory/grocery-get',
        request_body,
        headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == 200
    for result in response.json()['results']:
        assert (not result['comment_courier']) != has_comment
    if not has_comment:
        for order in orders:
            order['comment'] = ''
    # make expected result
    orders = filter(lambda o: o['yandex_uid'] == yandex_uid, orders)

    orders = utils.parse_grocery_stq_orders(orders).items()
    heapq.nlargest(
        max_records or len(orders),
        orders,
        key=lambda order: order[1]['created'],
    )
    if min_created is not None:
        min_created = dateutil.parser.isoparse(min_created).replace(
            tzinfo=None,
        )
        for idx, order in enumerate(orders):
            if order[1]['created'] > min_created:
                orders = orders[:idx]
                break

    orders = {order_id: order for order_id, order in orders}

    assert orders == utils.parse_grocery_response_orders(response)


async def test_grocery_get_no_yandex_uid(
        session_stq_filler, taxi_routehistory,
):
    response = await taxi_routehistory.post('routehistory/grocery-get', {})
    assert response.status_code == 400


async def test_grocery_get_bad_yandex_uid(
        session_stq_filler, taxi_routehistory,
):
    response = await taxi_routehistory.post(
        'routehistory/grocery-get', {}, headers={'X-Yandex-UID': 'invalid'},
    )
    assert response.status_code == 400


@pytest.fixture(name='orders')
def _orders(load_json):
    return load_json('orders.json')


@pytest.fixture(name='session_stq_filler')
async def _session_stq_filler(orders, pgsql, stq_runner):
    await asyncio.gather(
        *map(lambda order: stq_submit_order(stq_runner, order), orders),
    )
    assert utils.parse_grocery_stq_orders(
        orders,
    ) == utils.parse_grocery_db_orders(fetch_db_orders(pgsql))
