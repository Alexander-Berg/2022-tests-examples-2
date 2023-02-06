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
                            'point_b': {'value': 77, 'is_default': False},
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
            selected_class='vip',
        ),
    ],
    ['rpush', 'test_key3', 'invalid'],
)
@pytest.mark.config(
    PIN_STORAGE_DUPLICATE={'coefficient': 0, 'ttl': 0},
    PIN_STORAGE_DYNAMIC_MAX_RADIUS=100,
)
async def test_get_stats(taxi_pin_storage):
    expected = {
        'pins': 3,
        'pins_with_b': 3,
        'pins_with_order': 3,
        'pins_with_driver': 0,
        'prev_pins': (
            26 * (100 * 100) / (27 * 27) + 36 * (100 * 100) / (37 * 37)
        ) / 2,
        'values_by_category': {
            'econom': {
                'estimated_waiting': 25,
                'surge': 28,
                'cost': 21,
                'pins_driver_in_tariff': 0,
                'pins_order_in_tariff': 0,
                'trip': {'distance': 12.3, 'time': 45.6},
            },
            'vip': {
                'estimated_waiting': 35,
                'surge': 38,
                'surge_b': 77,
                'cost': 31,
                'pins_driver_in_tariff': 0,
                'pins_order_in_tariff': 1,
                'trip': {'distance': 12.3, 'time': 45.6},
            },
        },
        'global_pins': 3,
        'global_pins_with_order': 3,
        'global_pins_with_driver': 0,
    }
    response = await taxi_pin_storage.get(
        'v1/get_stats', params={'user_layer': 'default'},
    )
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']
    assert stats == expected

    # filtered categories
    expected_categories = {'econom': True}
    response = await taxi_pin_storage.get(
        'v1/get_stats',
        params={'categories': 'econom', 'user_layer': 'default'},
    )
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']
    for category in list(stats['values_by_category'].keys()):
        assert expected_categories.pop(category)
    assert not expected_categories


# +5 min after pins' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        # merged with 3 by user_id
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
            'test_user_id0',
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
            'test_phone_id0',
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
            1552003200002,
        ),
    ],
    [
        'rpush',
        '1552003200',
        common.build_pin(
            [],
            None,
            'test_order_id0',
            'test_phone_id0',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id0',
            'default',
            [],
            1552003200003,
        ),
    ],
    [
        # matched with 6, discarded because of different offer_id
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
        # merge by phone_id to 6 (same offer_id)
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
    PIN_STORAGE_DYNAMIC_MAX_RADIUS=100,
    ENABLE_DEDUPLICATION_PINS_BY_PERSONAL_PHONE_ID=True,
)
async def test_get_stats_deduplicate(taxi_pin_storage):
    expected_categories = {'econom1': True, 'econom4': True}
    response = await taxi_pin_storage.get(
        'v1/get_stats', params={'user_layer': 'default'},
    )
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']

    # merged pins 1,2,3
    # merged pins 5,6
    assert stats['pins'] == 2

    for category in list(stats['values_by_category'].keys()):
        assert expected_categories.pop(category)
    assert not expected_categories


@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        '1552003200',  # 2019-03-08T00:00:00Z
        common.build_pin(
            [],
            'test_offer_id0',
            'test_order_id0',
            'test_phone_id0',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id0',
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
                            'point_b': {'value': 55, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 10,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 29,
                },
            ],
            1552003200000,
        ),
    ],
    [
        'rpush',
        '1552003260',  # 2019-03-08T00:01:00Z
        common.build_pin(
            [],
            'test_offer_id1',
            'test_order_id1',
            'test_phone_id1',
            12.3,
            45.6,
            12.7,
            45.8,
            'test_user_id1',
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
                            'point_b': {'value': 55, 'is_default': False},
                        },
                    },
                    'surge': {
                        'value': 30,
                        'surcharge': {'alpha': 42, 'beta': 43, 'value': 44},
                    },
                    'value_raw': 29,
                },
            ],
            1552003260000,
        ),
    ],
)
@pytest.mark.parametrize(
    'duplicate_ttl, expected_pins, expected_surge',
    [
        (239, 2, (10 + 30) / 2),
        (240, 3, (10 + 30 * 2) / 3),
        (300, 4, (10 * 2 + 30 * 2) / 4),
    ],
    ids=['no_duplication', 'one', 'both'],
)
@pytest.mark.config(PIN_STORAGE_DYNAMIC_MAX_RADIUS=100)
async def test_get_stats_duplication(
        taxi_pin_storage,
        taxi_config,
        duplicate_ttl,
        expected_pins,
        expected_surge,
):
    taxi_config.set_values(
        dict(PIN_STORAGE_DUPLICATE={'coefficient': 1.0, 'ttl': duplicate_ttl}),
    )
    expected = {
        'pins': expected_pins,
        'pins_with_b': expected_pins,
        'pins_with_order': expected_pins,
        'pins_with_driver': 0,
        'prev_pins': 26 * (100 * 100) / (27 * 27),
        'values_by_category': {
            'econom': {
                'estimated_waiting': 25,
                'surge': expected_surge,
                'surge_b': 55,
                'cost': 21,
                'pins_order_in_tariff': expected_pins,
                'pins_driver_in_tariff': 0,
                'trip': {'distance': 12.3, 'time': 45.6},
            },
        },
        'global_pins': 2,
        'global_pins_with_order': 2,
        'global_pins_with_driver': 0,
    }
    response = await taxi_pin_storage.get(
        'v1/get_stats', params={'user_layer': 'default'},
    )
    assert response.status_code == 200
    data = response.json()
    stats = data['stats']
    assert stats == expected
