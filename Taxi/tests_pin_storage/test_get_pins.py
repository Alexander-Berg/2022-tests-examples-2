import json

import pytest

from tests_pin_storage import common


# +5 min after pins' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id0',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id0',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id1',
            12.4,
            45.7,
            12.8,
            45.9,
            'test_user_id1',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [
                {
                    'experiment_id': 'ex0',
                    'experiment_name': 'test_experiment_name',
                    'classes': [
                        {
                            'name': 'econom',
                            'cost': 1,
                            'estimated_waiting': 5,
                            'calculation_meta': {
                                'counts': {
                                    # 'by_statuses': {},
                                    'free': 2,
                                    'free_chain': 3,
                                    'total': 4,
                                    'pins': 6,
                                    'radius': 7,
                                },
                                'smooth': {
                                    'point_a': {
                                        'value': 45,
                                        'is_default': False,
                                    },
                                },
                            },
                            'surge': {
                                'value': 8,
                                'surcharge': {
                                    'alpha': 42,
                                    'beta': 43,
                                    'value': 44,
                                },
                            },
                            'value_raw': 9,
                        },
                        {
                            'name': 'vip',
                            'cost': 11,
                            'estimated_waiting': 15,
                            'calculation_meta': {
                                'counts': {
                                    # 'by_statuses': {},
                                    'free': 12,
                                    'free_chain': 13,
                                    'total': 14,
                                    'pins': 16,
                                    'radius': 17,
                                },
                                'smooth': {
                                    'point_a': {
                                        'value': 45,
                                        'is_default': False,
                                    },
                                },
                            },
                            'surge': {
                                'value': 18,
                                'surcharge': {
                                    'alpha': 42,
                                    'beta': 43,
                                    'value': 44,
                                },
                            },
                            'value_raw': 19,
                        },
                    ],
                },
            ],
            'test_offer_id',
            'test_order_id',
            'test_phone_id2',
            12.5,
            45.8,
            12.9,
            45.0,
            'test_user_id2',
            'default',
            [
                {
                    'name': 'econom',
                    'cost': 21,
                    'estimated_waiting': 25,
                    'calculation_meta': {
                        'counts': {
                            # 'by_statuses': {},
                            'free': 22,
                            'free_chain': 23,
                            'total': 24,
                            'pins': 26,
                            'radius': 27,
                        },
                        'smooth': {
                            'point_a': {'value': 45, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 28,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 29,
                },
                {
                    'name': 'vip',
                    'cost': 31,
                    'estimated_waiting': 35,
                    'calculation_meta': {
                        'counts': {
                            # 'by_statuses': {},
                            'free': 32,
                            'free_chain': 33,
                            'total': 34,
                            'pins': 36,
                            'radius': 37,
                        },
                        'smooth': {
                            'point_a': {'value': 45, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 38,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 39,
                },
            ],
            1552003200000,
        ),
    ],
    ['rpush', 'test_key3', 'invalid'],
)
@pytest.mark.config(PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0})
async def test_get_pins(taxi_pin_storage):
    # invalid format
    response = await taxi_pin_storage.get('v1/get_pins', params={'format': 42})
    assert response.status_code == 400

    # all match (flatbuffer)
    expected_user_id = {
        'test_user_id0': True,
        'test_user_id1': True,
        'test_user_id2': True,
    }
    response = await taxi_pin_storage.get(
        'v1/get_pins', params={'format': 'fb'},
    )
    assert response.status_code == 200
    pins = common.parse_pins(response.content)
    for pin in pins:
        assert expected_user_id.pop(pin.UserId().decode())
    assert not expected_user_id

    # all match (json)
    expected_user_id = {
        'test_user_id0': True,
        'test_user_id1': True,
        'test_user_id2': True,
    }
    response = await taxi_pin_storage.get(
        'v1/get_pins', params={'format': 'json'},
    )
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']
    for pin in pins:
        assert expected_user_id.pop(pin['user_id'])
    assert not expected_user_id

    # filtered categories (flatbuffer)
    expected_categories = {'econom': True}
    expected_categories_exp = {'econom': True}
    response = await taxi_pin_storage.get(
        'v1/get_pins',
        params={'format': 'fb', 'types': 'test_type1', 'categories': 'econom'},
    )
    assert response.status_code == 200
    pins = common.parse_pins(response.content)
    for pin in pins:
        for j in range(pin.ValuesLength()):
            assert expected_categories.pop(pin.Values(j).Category().decode())
        for j in range(pin.ExperimentsLength()):
            for k in range(pin.Experiments(j).ValuesLength()):
                assert expected_categories_exp.pop(
                    pin.Experiments(j).Values(k).Category().decode(),
                )
    assert not expected_categories
    assert not expected_categories_exp

    # filtered categories (json)
    expected_categories = {'econom': True}
    expected_categories_exp = {'econom': True}
    response = await taxi_pin_storage.get(
        'v1/get_pins',
        params={
            'format': 'json',
            'types': 'test_type1',
            'categories': 'econom',
        },
    )
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']
    for pin in pins:
        for class_info in pin['classes']:
            assert expected_categories.pop(class_info['name'])
        for experiment in pin['experiments']:
            for class_info in experiment['classes']:
                assert expected_categories_exp.pop(class_info['name'])
    assert not expected_categories
    assert not expected_categories_exp


# +5 min after pins' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id0',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id0',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id1',
            12.4,
            45.7,
            12.8,
            45.9,
            'test_user_id1',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id2',
            12.5,
            45.8,
            12.9,
            45.0,
            'test_user_id2',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id3',
            12.6,
            45.9,
            12.0,
            45.1,
            'test_user_id3',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id4',
            12.7,
            45.0,
            12.1,
            45.2,
            'test_user_id4',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_id',
            'test_order_id',
            'test_phone_id5',
            12.8,
            45.1,
            12.2,
            45.3,
            'test_user_id5',
            'default',
            [],
            1552003200000,
        ),
    ],
    ['rpush', 'test_key2', 'invalid'],
)
@pytest.mark.config(PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0})
async def test_get_pins_uneven_lists(taxi_pin_storage):
    response = await taxi_pin_storage.get(
        'v1/get_pins', params={'format': 'json'},
    )
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']
    assert len(pins) == 6


# +5 min after pins' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        # merged with 3 by personal_phone_id
        'rpush',
        '1552003200',
        common.build_pin(
            [
                {
                    'experiment_id': 'ex0',
                    'experiment_name': 'test_experiment_name',
                    'classes': [],
                },
            ],
            None,
            'test_order_id0',
            'test_phone_id0',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id99',
            'default',
            [],
            1552003200000,
        ),
    ],
    [
        # merged with 3 by user_id
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            None,
            'test_order_id0',
            'test_phone_id99',
            12.4,
            45.7,
            12.8,
            45.9,
            'test_user_id0',
            'default',
            [
                {
                    'name': 'econom1',
                    'cost': 11,
                    'estimated_waiting': 15,
                    'calculation_meta': {
                        'counts': {
                            # 'by_statuses': {},
                            'free': 12,
                            'free_chain': 13,
                            'total': 14,
                            'pins': 16,
                            'radius': 17,
                        },
                        'smooth': {
                            'point_a': {'value': 45, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 18,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 19,
                },
            ],
            1552003200001,
        ),
    ],
    [
        'rpush',
        '1552003200',
        json.dumps(
            {
                'created': 1552003200002,
                'pin': dict(
                    experiments=[],
                    order_id='test_order_id0',
                    personal_phone_id='test_phone_id0',
                    point={'lat': 12.4, 'lon': 44.2},
                    user_id='test_user_id0',
                    user_layer='default',
                    driver_id='clid_uuid',
                    classes=[],
                ),
            },
        ),
    ],
    [
        # matched with 7, discarded because of different offer_id
        'rpush',
        '1552003200',
        common.build_pin(
            [
                {
                    'experiment_id': 'ex1',
                    'experiment_name': 'test_experiment_name',
                    'classes': [],
                },
            ],
            'test_offer_idB',
            'test_order_id2',
            'test_phone_id1',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id1',
            'default',
            [],
            1552003200004,
        ),
    ],
    [
        # merge by phone_id to 7 (same offer_id)
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_idA',
            'test_order_id3',
            'test_phone_id1',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id-no-match',
            'default',
            [
                {
                    'name': 'econom4',
                    'cost': 41,
                    'estimated_waiting': 45,
                    'calculation_meta': {
                        'counts': {
                            # 'by_statuses': {},
                            'free': 42,
                            'free_chain': 43,
                            'total': 44,
                            'pins': 46,
                            'radius': 47,
                        },
                        'smooth': {
                            'point_a': {'value': 45, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 48,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 49,
                },
            ],
            1552003200005,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            'test_offer_idA',
            None,
            'test_phone_id1',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id1',
            'default',
            [],
            1552003200006,
        ),
    ],
)
@pytest.mark.config(
    PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0},
    ENABLE_DEDUPLICATION_PINS_BY_PERSONAL_PHONE_ID=True,
)
async def test_get_pins_deduplicate(taxi_pin_storage):
    response = await taxi_pin_storage.get('v1/get_pins')
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']

    assert len(pins) == 2

    # merged pins 1,2,3
    one = next(p for p in pins if p.get('offer_id') is None)
    assert one['experiments'] != []
    assert one['classes'] != []
    assert one['driver_id'] == 'clid_uuid'
    assert one['order_id'] == 'test_order_id0'
    assert one['point'] == {'lat': 12.4, 'lon': 44.2}
    assert one['point_b'] == [12.8, 45.9]
    # provided by create_pin in pins 1 and 2
    assert 'trip' in one

    # merged pins 6,7
    two = next(p for p in pins if p.get('offer_id') is not None)
    assert two['experiments'] == []
    assert two['classes'] != []
    assert two['offer_id'] == 'test_offer_idA'
    assert two.get('order_id') is None
