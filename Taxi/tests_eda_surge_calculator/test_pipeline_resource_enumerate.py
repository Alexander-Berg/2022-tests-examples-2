# pylint: disable=redefined-outer-name, unused-variable

INVALID_CONSUMER_ERROR_CODE = 'invalid_consumer'


def _name_sorter(element):
    return element['name']


async def test_resource_enumerate(taxi_eda_surge_calculator, load_json):
    supply_instance_schema = load_json('supply_instance_schema.json')
    supply_params_schema = load_json('supply_params_schema.json')
    extended_instance_schema = load_json('extended_instance_schema.json')
    extended_params_schema = load_json('extended_params_schema.json')
    surge_history_params = load_json('surge_history_params.json')

    response = await taxi_eda_surge_calculator.get(
        'v1/js/pipeline/resource/enumerate',
    )
    assert response.status_code == 200

    sorted_response = sorted(response.json(), key=_name_sorter)

    expected_response = [
        {'is_prefetch_only': False, 'name': 'courier_counters'},
        {
            'name': 'eda_supply',
            'instance_schema': supply_instance_schema,
            'params_schema': supply_params_schema,
            'is_prefetch_only': False,
        },
        {
            'name': 'extended_supply',
            'instance_schema': extended_instance_schema,
            'params_schema': extended_params_schema,
            'is_prefetch_only': False,
        },
        {'is_prefetch_only': False, 'name': 'places_settings'},
        {
            'name': 'surge_history',
            'params_schema': surge_history_params,
            'is_prefetch_only': False,
        },
        {
            'name': 'taxi_candidates',
            'params_schema': load_json('taxi_candidates_params.json'),
            'instance_schema': load_json(
                'taxi_candidates_instance_schema.json',
            ),
            'is_prefetch_only': False,
        },
        {
            'name': 'warehouse_taxi_surge',
            'params_schema': load_json('taxi_surge_params.json'),
            'instance_schema': load_json(
                'warehouse_taxi_surge_instance_schema.json',
            ),
            'is_prefetch_only': False,
        },
    ]

    assert sorted_response == expected_response


async def test_unknown_consumer(taxi_eda_surge_calculator):
    response = await taxi_eda_surge_calculator.get(
        'v1/js/pipeline/resource/enumerate',
        params={'consumer': 'something-not-existing'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == INVALID_CONSUMER_ERROR_CODE
