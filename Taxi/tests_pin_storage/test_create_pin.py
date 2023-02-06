import json

import pytest


@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(PIN_STORAGE_CREATE_PIN_REQUESTS=True)
async def test_create_pin(
        taxi_pin_storage, redis_store, load_json, mockserver, testpoint,
):
    surger_requests = []

    @mockserver.json_handler('/surger/create_pin')
    def _mock_create_pin(request):
        surger_requests.append(request.json)
        return {'created': '2019-03-08T00:00:00Z'}

    @testpoint('surger_create_pin')
    def surger_create_pin(data):
        pass

    response = await taxi_pin_storage.put(
        'v1/create_pin',
        headers={'Content-Type': 'application/json'},
        params={},
        data=json.dumps(
            {
                'pin': {
                    'experiments': [],
                    'personal_phone_id': 'test_phone_id',
                    'point': {'lon': 12.3, 'lat': 45.6},
                    'user_id': 'test_user_id',
                    'user_layer': 'default',
                    'order_id': 'some_order_id',
                    'offer_id': 'some_offer_id',
                    'selected_class': 'vip',
                    'altpin_offer_id': '0ffErrr',
                    'orders_complete': 10,
                    'position_accuracy': 0.001,
                    'explicit_antisurge_offer_id': 'great0ffErrr',
                    'payment_type': 'cash',
                    'combo_order_offer_id': 'someKind0fCombo',
                    'plus_promo_offer_id': 'nopainnogain',
                    'zone_id': 'test_surge_zone_id',
                    'extra': {'is_lightweight_routestats': True},
                    'classes': [
                        {
                            'name': 'econom',
                            'cost': 1,
                            'estimated_waiting': 5,
                            'calculation_meta': {
                                'counts': {
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
                                    'free': 12,
                                    'free_chain': 13,
                                    'total': 14,
                                    'pins': 16,
                                    'radius': 17,
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
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    assert 'timestamp' in data

    await surger_create_pin.wait_call()
    assert surger_requests == [
        {
            'extra': {'is_lightweight_routestats': True},
            'estimated_waiting': {'vip': 15, 'econom': 5},
            'offer_id': 'some_offer_id',
            'order_id': 'some_order_id',
            'personal_phone_id': 'test_phone_id',
            'point': [12.3, 45.6],
            'save_to_storage': False,
            'selected_class': 'vip',
            'altpin_offer_id': '0ffErrr',
            'orders_complete': 10,
            'position_accuracy': 0.001,
            'explicit_antisurge_offer_id': 'great0ffErrr',
            'payment_type': 'cash',
            'combo_order_offer_id': 'someKind0fCombo',
            'plus_promo_offer_id': 'nopainnogain',
            'surge': {
                'classes': [
                    {
                        'free': 2,
                        'free_chain': 3,
                        'name': 'econom',
                        'pins': 6,
                        'radius': 7.0,
                        'reason': 'no',
                        'surcharge': 44.0,
                        'surcharge_alpha': 42.0,
                        'surcharge_beta': 43.0,
                        'total': 4,
                        'value': 8.0,
                        'value_raw': 9.0,
                        'value_smooth': 45.0,
                        'value_smooth_is_default': False,
                    },
                    {
                        'free': 12,
                        'free_chain': 13,
                        'name': 'vip',
                        'pins': 16,
                        'radius': 17.0,
                        'reason': 'no',
                        'surcharge': 44.0,
                        'surcharge_alpha': 42.0,
                        'surcharge_beta': 43.0,
                        'total': 14,
                        'value': 18.0,
                        'value_raw': 19.0,
                        'value_smooth': 1.0,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'zone_id': 'test_surge_zone_id',
            },
            'trip_info': {
                'cost_info': [
                    {'cost': 1.0, 'name': 'econom'},
                    {'cost': 11.0, 'name': 'vip'},
                ],
            },
            'user_id': 'test_user_id',
        },
    ]

    assert redis_store.keys() == [b'1552003200']
    pins_in_redis = redis_store.lrange('1552003200', 0, -1)
    assert len(pins_in_redis) == 1
    pin_from_redis = json.loads(pins_in_redis[0])
    del pin_from_redis['pin']['trace_id']
    assert pin_from_redis == load_json('pin.json')
