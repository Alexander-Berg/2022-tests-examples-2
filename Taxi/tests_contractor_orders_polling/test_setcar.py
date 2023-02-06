import json

import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.now('2017-07-14T02:00:00Z')
async def test_setcar_no_tag_in_redis(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()

    # Server tag is empty so we should not return anything
    assert response_obj.get('md5_setcar') is None
    assert response_obj.get('setcar') is None
    assert response_obj.get('client_locations') is None


@pytest.mark.now('2017-07-14T02:00:00Z')
@pytest.mark.redis_store(
    ['set', 'Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG'],
)
async def test_setcar_delay_not_set_in_redis(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_setcar'] == 'SETCAR-ETAG_3155378975999999999'
    assert response_obj.get('setcar') is None


@pytest.mark.parametrize(
    ('md5_setcar', 'expected_md5_setcar', 'expected_setcar'),
    [
        pytest.param(
            None,
            'SETCAR-ETAG_636671328000000000',
            None,
            id='no tag in request - return servers',
        ),
        pytest.param(
            '',
            'SETCAR-ETAG_636671328000000000',
            None,
            id='empty tag in request is the same as no tag at all',
        ),
        pytest.param(
            'SETCAR-ETAG_636355968000000000',
            'SETCAR-ETAG_636355968000000000',
            None,
            id='tag does not differ',
        ),
        pytest.param(
            'SETCAR-ETAG-BAD_UNPARSABLE',
            'SETCAR-ETAG_636671328000000000',
            None,
            id='Return the date of the nearest order in the future',
        ),
        pytest.param(
            'ONLYTAG',
            'SETCAR-ETAG_636671328000000000',
            None,
            id='No delay in request',
        ),
    ],
)
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
async def test_setcar_md5_tag(
        taxi_contractor_orders_polling,
        md5_setcar,
        expected_md5_setcar,
        expected_setcar,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': md5_setcar} if md5_setcar else {},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj.get('md5_setcar') == expected_md5_setcar
    assert response_obj.get('setcar') == expected_setcar


@pytest.mark.now('2017-07-14T02:00:00Z')
@pytest.mark.redis_store(
    ['set', 'Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG'],
    [
        'set',
        'Order:SetCar:Driver:Reserv:MD5:Delay:999:888',
        '2017-07-14T02:40:00.000000Z',
    ],
)
async def test_setcar_no_orders_on_server(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG-DIFFERENT_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj.get('md5_setcar') == 'SETCAR-ETAG_3155378975999999999'
    assert response_obj.get('setcar') is None


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
        {'order0': json.dumps({'date_view': '2017-07-14T02:00:00Z'})},
    ],
)
async def test_setcar_no_statuses_in_redis(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG-BAD_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_setcar'] == 'SETCAR-ETAG_3155378975999999999'
    assert response_obj['setcar'] == {
        'order0': {'date_view': '2017-07-14T02:00:00Z'},
    }


@pytest.mark.now('2017-07-14T02:00:00Z')
@pytest.mark.redis_store(
    ['set', 'Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG'],
    [
        'set',
        'Order:SetCar:Driver:Reserv:MD5:Delay:999:888',
        '2017-07-14T02:40:00.000000Z',
    ],
    [
        'sadd',
        'Order:SetCar:Driver:Reserv:Items999:888',
        'order0',
        'order1',
        'order3',
    ],
    [
        'hmset',
        'Order:SetCar:Items:999',
        {
            'order0': json.dumps({'date_view': '2017-07-14T02:40:00Z'}),
            'order1': json.dumps({'date_view': '2017-07-14T01:40:00Z'}),
            'order3': json.dumps({'field': 'value'}),
        },
    ],
)
async def test_setcar_delay_in_the_future_and_past(
        taxi_contractor_orders_polling, redis_store,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_setcar': 'SETCAR-ETAG-BAD_636355968000000000'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_setcar'] == 'SETCAR-ETAG_636355968000000000'

    # Order0 is in the future so should not be returned
    assert response_obj['setcar'] == {
        'order1': {'date_view': '2017-07-14T01:40:00Z'},
        'order3': {'field': 'value'},
    }

    # Check that delay is updated, because it was different
    assert (
        redis_store.get('Order:SetCar:Driver:Reserv:MD5:Delay:999:888')
        == b'2017-07-14T02:40:00.000000Z'
    )
