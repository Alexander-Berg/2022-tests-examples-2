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
            0.123,
            0.456,
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
            10.124,
            10.457,
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
            20.125,
            20.458,
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
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius', params={'format': 42},
    )
    assert response.status_code == 400

    # invalid point (flatbuffer)
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'fb', 'point': '0', 'radius': 1},
    )
    assert response.status_code == 400

    # invalid point (json)
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'json', 'point': '0', 'radius': 1},
    )
    assert response.status_code == 400

    # invalid radius (flatbuffer)
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'fb', 'point': '0,0', 'radius': 'abc'},
    )
    assert response.status_code == 400

    # invalid radius (json)
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'json', 'point': '0,0', 'radius': 'abc'},
    )
    assert response.status_code == 400

    # some match (radius) (flatbuffer)
    expected_user_id = {'test_user_id0': True}
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'fb', 'point': '0,0', 'radius': 60000},
    )
    assert response.status_code == 200
    pins = common.parse_pins(response.content)
    for pin in pins:
        assert expected_user_id.pop(pin.UserId().decode())
    assert not expected_user_id

    # some match (radius) (json)
    expected_user_id = {'test_user_id0': True}
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'json', 'point': '0,0', 'radius': 60000},
    )
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']
    for pin in pins:
        assert expected_user_id.pop(pin['user_id'])
    assert not expected_user_id

    # all match (flatbuffer)
    expected_user_id = {
        'test_user_id0': True,
        'test_user_id1': True,
        'test_user_id2': True,
    }
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={'format': 'fb', 'point': '0,0', 'radius': 3200000},
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
        'v1/get_pins/radius',
        params={'format': 'json', 'point': '0,0', 'radius': 3200000},
    )
    assert response.status_code == 200
    data = response.json()
    pins = data['pins']
    for pin in pins:
        assert expected_user_id.pop(pin['user_id'])
    assert not expected_user_id

    # filtered categories (flatbuffers)
    expected_categories = {'econom': True}
    expected_categories_exp = {'econom': True}
    response = await taxi_pin_storage.get(
        'v1/get_pins/radius',
        params={
            'format': 'fb',
            'point': '0,0',
            'radius': 3200000,
            'categories': 'econom',
        },
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
        'v1/get_pins/radius',
        params={
            'format': 'json',
            'point': '0,0',
            'radius': 3200000,
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
