INVALID_API_ERROR_CODE = '400'
INVALID_PIPELINE_ERROR_CODE = 'invalid_pipeline'

NEW_STAGES_LIST = [
    {
        'name': 'start',
        'optional': False,
        'in_bindings': [],
        'conditions': [],
        'out_bindings': [
            {'alias': 'places', 'optional': False, 'query': 'places'},
        ],
        'source_code': 'return {places: []};',
    },
    {
        'name': 'initialization',
        'optional': False,
        'in_bindings': [
            {
                'domain': 'input',
                'optional': False,
                'query': 'place_ids.*{:place_id}',
            },
            {
                'domain': 'input',
                'optional': False,
                'query': 'places_settings[place_id]{place_settings}',
            },
            {'domain': 'input', 'optional': False, 'query': 'coeff'},
        ],
        'conditions': [],
        'out_bindings': [
            {
                'alias': 'place_data',
                'optional': False,
                'query': 'places[?(@.id==place_id)]',
            },
        ],
        'source_code': (
            'return {place_data: {id: place_id, '
            'settings: place_settings, coeff: coeff}};'
        ),
    },
    {
        'name': 'arguments_with_types',
        'optional': False,
        'in_bindings': [
            {
                'domain': 'resource',
                'optional': False,
                'query': 'groceries_arrivals.*{idx:}',
                'children': [
                    {'query': 'couriers_arrival_limit_time{limit_time}'},
                    {'query': 'new_arrival_time'},
                ],
            },
        ],
        'conditions': [],
        'out_bindings': [],
        'source_code': '',
    },
]


async def test_schema_api_error(taxi_eda_surge_calculator):
    def _check_response(response):
        assert response.status_code == 400
        response_json = response.json()
        assert response_json['code'] == INVALID_API_ERROR_CODE

    pipeline = {'name': 'new', 'stages': []}

    # Missing name
    del pipeline['name']
    response = await taxi_eda_surge_calculator.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)
    pipeline['name'] = 'new'

    # Stages with wrong type
    pipeline['stages'] = {}
    response = await taxi_eda_surge_calculator.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)


async def test_compile_error(taxi_eda_surge_calculator):
    def _check_response(response):
        assert response.status_code == 400
        response_json = response.json()
        assert response_json['code'] == INVALID_PIPELINE_ERROR_CODE

    # Semantic error - fetching resource without initialization
    pipeline = {
        'id': '0',
        'name': 'new',
        'stages': [
            {
                'name': 'initialization',
                'optional': False,
                'in_bindings': [
                    {
                        'domain': 'resource',
                        'optional': False,
                        'query': 'place_ids.*{:place_id}',
                    },
                ],
                'conditions': [],
                'out_bindings': [],
                'source_code': 'return {}',
            },
        ],
    }

    response = await taxi_eda_surge_calculator.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)
