import json

import pytest

GEO_SHARING_KEY = 'Order:SetCar:Item:ClientGeoSharing:TrackIds'


@pytest.mark.redis_store(
    [
        'hset',
        f'{GEO_SHARING_KEY}:park_id_0:driver_id_1',
        'alias_id_1',
        json.dumps({'track_id': 'user_id_1'}),
    ],
    [
        'hset',
        'Order:RequestConfirm:Items:park_id_0',
        'alias_id_0',
        10,  # Driving
    ],
    [
        'hset',
        'Order:RequestConfirm:Items:park_id_0',
        'alias_id_1',
        20,  # Waiting
    ],
)
@pytest.mark.parametrize(
    'driver_id, alias_id',
    [('driver_id_0', 'alias_id_0'), ('driver_id_1', 'alias_id_1')],
    ids=['add', 'try_update'],
)
async def test_add_client_geo_sharing(
        taxi_contractor_order_setcar,
        redis_store,
        taxi_config,
        driver_id,
        alias_id,
):
    taxi_config.set_values(
        {'CLIENT_GEO_SHARING_ORDER_STATUSES': ['waiting', 'driving']},
    )
    response = await taxi_contractor_order_setcar.put(
        '/v1/order/client-geo-sharing',
        json={
            'park_id': 'park_id_0',
            'profile_id': driver_id,
            'alias_id': alias_id,
            'user_id': 'user_id_0',
        },
    )
    assert response.json() == {}
    assert response.status_code == 200
    track_obj_b = redis_store.hget(
        f'{GEO_SHARING_KEY}:park_id_0:{driver_id}', alias_id,
    )
    track_obj = json.loads(track_obj_b)
    if alias_id == 'alias_id_1':
        assert track_obj == {'track_id': 'user_id_1'}
    else:
        assert track_obj == {'track_id': 'user_id_0'}


@pytest.mark.redis_store(
    [
        'hset',
        f'{GEO_SHARING_KEY}:park_id_0:driver_id_0',
        'alias_id_0',
        'user_id_0',
    ],
)
@pytest.mark.parametrize(
    'driver_id, alias_id',
    [('driver_id_0', 'alias_id_0'), ('driver_id_1', 'alias_id_1')],
    ids=['delete', 'try_delete'],
)
async def test_delete_client_geo_sharing(
        taxi_contractor_order_setcar,
        redis_store,
        taxi_config,
        driver_id,
        alias_id,
):
    response = await taxi_contractor_order_setcar.delete(
        '/v1/order/client-geo-sharing',
        json={
            'park_id': 'park_id_0',
            'profile_id': driver_id,
            'alias_id': alias_id,
        },
    )
    assert response.json() == {}
    assert response.status_code == 200

    if alias_id == 'alias_id_0':
        assert (
            redis_store.hget(
                f'{GEO_SHARING_KEY}:park_id_0:{driver_id}', alias_id,
            )
            is None
        )
