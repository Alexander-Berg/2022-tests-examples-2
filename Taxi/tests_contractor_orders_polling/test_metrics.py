import json

import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.now('2017-07-14T02:00:00Z')
@pytest.mark.redis_store(
    ['set', 'Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG'],
    [
        'set',
        'Order:SetCar:Driver:Reserv:MD5:Delay:999:888',
        '2017-07-14T02:40:00.000000Z',
    ],
    ['sadd', 'Order:SetCar:Driver:Reserv:Items999:888', 'order0'],
    [
        'hmset',
        'Order:SetCar:Items:999',
        {'order0': json.dumps({'date_view': '2018-07-14T02:40:00Z'})},
    ],
)
async def test_metrics(
        taxi_contractor_orders_polling,
        taxi_contractor_orders_polling_monitor,
        testpoint,
):
    await taxi_contractor_orders_polling.tests_control(reset_metrics=True)

    @testpoint('setcar_redis_error')
    def _setcar_redis_error(data):
        pass

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, params={}, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj.get('md5_setcar') is None
    assert response_obj.get('setcar') is None
    metrics = await taxi_contractor_orders_polling_monitor.get_metric(
        'polling_metrics',
    )
    assert metrics == {'error.set_car': 1}
