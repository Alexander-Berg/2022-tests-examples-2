import json

import pytest

from tests_contractor_orders_polling import utils

TAXIMETER_MESSAGES = {
    'multiorder.route.order_start': {'ru': 'Старт'},
    'multiorder.route.order_finish': {'ru': 'Финиш'},
    'multiorder.route.order_start_1': {'ru': 'Старт №1'},
    'multiorder.route.order_finish_1': {'ru': 'Финиш №1'},
    'multiorder.route.current_order': {'ru': 'Текущий заказ'},
    'multiorder.route.next_order': {'ru': 'Следующий заказ'},
    'multiorder.route.order_name_1': {'ru': '1'},
    'multiorder.route.order_name_2': {'ru': '2'},
}

# pylint: disable=C0103
def _open_setcars(testcase, load_json):
    d = load_json(f'{testcase}_setcars.json')
    res = dict()
    for k, v in d.items():
        res[k] = json.dumps(v)
    return res


# pylint: disable=C0103
def _serialize_status(s):
    if s == 'driving':
        return 10
    if s == 'transporting':
        return 40
    if s == 'complete':
        return 50
    return None


# pylint: disable=C0103
def _setup_redis(redis_store, setcars_dict, statuses):
    redis_store.set('Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG')
    redis_store.set(
        'Order:SetCar:Driver:Reserv:MD5:Delay:999:888',
        '2017-07-14T02:40:00.000000Z',
    )
    redis_store.hmset('Order:SetCar:Items:999', setcars_dict)
    redis_store.sadd(
        'Order:SetCar:Driver:Reserv:Items999:888', *setcars_dict.keys(),
    )
    for setcar_id, status in statuses.items():
        redis_store.hset(
            'Order:RequestConfirm:Items:999',
            setcar_id,
            _serialize_status(status),
        )


@pytest.mark.translations(taximeter_messages=TAXIMETER_MESSAGES)
@pytest.mark.parametrize(
    'testcase',
    ['one', 'chain', 'combo', 'finish_combo', 'bad_match', 'new_chain'],
)
@pytest.mark.now('2017-07-14T02:00:00Z')
async def test_base(
        taxi_contractor_orders_polling, redis_store, load_json, testcase,
):
    setcars_dict = _open_setcars(testcase, load_json)
    statuses = load_json(f'{testcase}_statuses.json')
    _setup_redis(redis_store, setcars_dict, statuses)

    setcar_ids = sorted(list(setcars_dict.keys()))

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG-BAD_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert sorted(list(response_json['setcar'].keys())) == setcar_ids
    expected = load_json(f'{testcase}_multi_order_info.json')
    got = response_json['multi_order_info']
    assert got == expected
