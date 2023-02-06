import pytest


# pylint: disable=redefined-outer-name
@pytest.mark.config(
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
    CATEGORY_REQUIRES_DRIVER_TAG={
        '__default__': {
            '__default__': {'requires_tag': False, 'tag': ''},
            'econom': {'requires_tag': False, 'tag': ''},
        },
        'moscow': {
            '__default__': {'requires_tag': False, 'tag': ''},
            'econom': {'requires_tag': True, 'tag': 'new_car'},
            'uberx': {'requires_tag': True, 'tag': 'new_car'},
        },
        'vilnus': {'__default__': {'requires_tag': True, 'tag': 'vilnus_car'}},
    },
)
@pytest.mark.parametrize(
    'zone_id, accepted',
    [
        (
            'moscow',
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0', 'position': [55.0, 35.0]},
                {'dbid': 'dbid1', 'uuid': 'uuid3', 'position': [55.0, 35.0]},
            ],
        ),
        (
            'spb',
            [
                {'dbid': 'dbid0', 'uuid': 'uuid0', 'position': [55.0, 35.0]},
                {'dbid': 'dbid0', 'uuid': 'uuid1', 'position': [55.0, 35.0]},
                {'dbid': 'dbid1', 'uuid': 'uuid3', 'position': [55.0, 35.0]},
            ],
        ),
        (
            'vilnus',
            [{'dbid': 'dbid0', 'uuid': 'uuid4', 'position': [55.0, 35.0]}],
        ),
    ],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # park dbid0
        ('park', 'dbid0', 'new_car'),
        # dbid0_uuid0
        ('dbid_uuid', 'dbid0_uuid0', 'default_block'),
        ('dbid_uuid', 'dbid0_uuid0', 'dirty_car'),
        ('dbid_uuid', 'dbid0_uuid0', 'tag_1'),
        # dbid0_uuid1
        ('park_car_id', 'c88993c1919d413b843518a2c89936b3', 'bad_car'),
        ('udid', '56f968f07c0aa65c44998e4e', 'tag_2'),
        ('udid', '56f968f07c0aa65c44998e4e', 'default_block'),
        # dbid1_uuid3
        ('udid', '56f968f07c0aa65c44998e4f', 'tag_3'),
        ('dbid_uuid', 'dbid1_uuid3', 'bad_car'),
        # dbid0_uuid4
        ('dbid_uuid', 'dbid0_uuid4', 'vilnus_car'),
    ],
)
async def test_filter_driver_tags(
        taxi_candidates,
        driver_positions,
        zone_id,
        accepted,
        dispatch_settings,
):
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'DISPATCH_DRIVER_TAGS_BLOCK': [
                                'default_block',
                                'bad_car',
                                'tag_1',
                                'tag_2',
                                'bla_block',
                            ],
                        },
                    },
                ],
            },
            {
                'zone_name': 'moscow',
                'tariff_name': '__default__base__',
                'parameters': [
                    {
                        'values': {
                            'DISPATCH_DRIVER_TAGS_BLOCK': ['default_block'],
                        },
                    },
                ],
            },
            {
                'zone_name': 'moscow',
                'tariff_name': 'vip',
                'parameters': [
                    {'values': {'DISPATCH_DRIVER_TAGS_BLOCK': ['bad_car']}},
                ],
            },
            {
                'zone_name': 'moscow',
                'tariff_name': 'econom',
                'parameters': [
                    {'values': {'DISPATCH_DRIVER_TAGS_BLOCK': ['dirty_car']}},
                ],
            },
            {
                'zone_name': 'moscow',
                'tariff_name': 'minivan',
                'parameters': [
                    {'values': {'DISPATCH_DRIVER_TAGS_BLOCK': ['bla_block']}},
                ],
            },
            {
                'zone_name': 'moscow',
                'tariff_name': 'uberkids',
                'parameters': [
                    {'values': {'DISPATCH_DRIVER_TAGS_BLOCK': ['bla_block']}},
                ],
            },
            {
                'zone_name': 'spb',
                'tariff_name': '__default__base__',
                'parameters': [{'values': {'DISPATCH_DRIVER_TAGS_BLOCK': []}}],
            },
        ],
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid4', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': [
            'infra/fetch_unique_driver',
            'infra/fetch_car_classes',
            'efficiency/fetch_tags_classes',
            'infra/class',
        ],
        'zone_id': zone_id,
        'point': [55, 35],
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert sorted(json['drivers'], key=lambda x: x['uuid']) == accepted
