import typing

import pytest


WHITE_LABEL_REQUIREMENTS = {
    'request': {
        'white_label_requirements': {
            'source_park_id': 'dbid0',
            'dispatch_requirement': 'only_source_park',
        },
    },
}
NO_WHITE_LABEL_REQUIREMENTS: typing.Dict[str, typing.Any] = {'request': {}}
NO_REQUEST: typing.Dict[str, typing.Any] = {}
NO_ORDER = None

SAAS_PARK = 'dbid0'
NOT_SAAS_PARK = 'dbid1'


@pytest.mark.parametrize(
    'is_getting_orders_from_app, order_proc_order, is_driver_found, park_id',
    [
        # not saas orders and saas parks
        (True, NO_WHITE_LABEL_REQUIREMENTS, True, SAAS_PARK),
        (True, NO_REQUEST, True, SAAS_PARK),
        (True, NO_ORDER, True, SAAS_PARK),
        (False, NO_WHITE_LABEL_REQUIREMENTS, False, SAAS_PARK),
        (False, NO_REQUEST, False, SAAS_PARK),
        (False, NO_ORDER, False, SAAS_PARK),
        (None, NO_WHITE_LABEL_REQUIREMENTS, True, SAAS_PARK),
        (None, NO_REQUEST, True, SAAS_PARK),
        (None, NO_ORDER, True, SAAS_PARK),
        # saas orders and saas parks
        (True, WHITE_LABEL_REQUIREMENTS, True, SAAS_PARK),
        (False, WHITE_LABEL_REQUIREMENTS, True, SAAS_PARK),
        (None, WHITE_LABEL_REQUIREMENTS, True, SAAS_PARK),
        # not saas orders and not saas parks
        (False, NO_WHITE_LABEL_REQUIREMENTS, True, NOT_SAAS_PARK),
        (True, NO_REQUEST, True, NOT_SAAS_PARK),
        (None, NO_ORDER, True, NOT_SAAS_PARK),
    ],
)
async def test_filter_saasparks(
        mongodb,
        taxi_candidates,
        driver_positions,
        is_getting_orders_from_app,
        order_proc_order,
        is_driver_found,
        park_id,
):
    if is_getting_orders_from_app is not None:
        mongodb.dbparks.update_one(
            {'_id': park_id},
            {
                '$set': {
                    'is_getting_orders_from_app': is_getting_orders_from_app,
                },
            },
        )

    await driver_positions(
        [{'dbid_uuid': f'{park_id}_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'filters': ['partners/saas_parks'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'order': order_proc_order,
    }

    response = await taxi_candidates.post('search', json=request_body)

    assert response.status_code == 200
    response_body = response.json()
    assert 'drivers' in response_body
    drivers = response_body['drivers']

    if is_driver_found:
        assert len(drivers) == 1
        assert drivers[0]['uuid'] == 'uuid0'
    else:
        assert not drivers
