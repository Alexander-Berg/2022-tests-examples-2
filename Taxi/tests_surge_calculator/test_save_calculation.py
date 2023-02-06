import pytest


@pytest.mark.now('2117-01-01T00:00:00.00000+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'], SAVE_CALCULATIONS_TO_PIN_STORAGE=True,
)
@pytest.mark.parametrize('use_component_queue', [True, False])
async def test_add_calculation(
        taxi_surge_calculator, mockserver, taxi_config, use_component_queue,
):
    taxi_config.set_values(
        {'SAVE_CALCULATIONS_USE_REQUESTS_QUEUE': use_component_queue},
    )
    actual_requests = []

    @mockserver.json_handler('/pin-storage/v1/add-calculation')
    def add_calculation(request):
        actual_requests.append(request.json)
        return {'timestamp': '2018-08-01T12:59:23.231000+00:00'}

    request = {'point_a': [38.1, 51]}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    await add_calculation.wait_call()
    # calculation_id is randomized, so check that it is just present
    actual_request = actual_requests[0]
    assert 'calculation_id' in actual_request
    actual_request.pop('calculation_id')
    assert actual_request == {
        'classes': [
            {
                'calculation_meta': {
                    'counts': {
                        'free': 148,
                        'free_chain': 3,
                        'pins': 6,
                        'radius': 7,
                        'total': 4,
                    },
                    'reason': 'pins_free',
                    'smooth': {
                        'point_a': {'is_default': False, 'value': 45.0},
                    },
                },
                'name': 'econom',
                'surge': {
                    'surcharge': {'alpha': 42.0, 'beta': 43.0, 'value': 44.0},
                    'value': 8.0,
                },
                'value_raw': 9.0,
            },
        ],
        'experiments': [],
        'zone_id': 'test_id',
        'user_layer': 'default',
    }
