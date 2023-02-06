INVALID_API_ERROR_CODE = '400'
INVALID_PIPELINE_ERROR_CODE = 'invalid_pipeline'

NEW_STAGES_LIST = [
    {
        'name': 'start',
        'optional': False,
        'in_bindings': [],
        'conditions': [],
        'out_bindings': [
            {'alias': 'depot_ids', 'optional': False, 'query': 'depot_ids'},
        ],
        'source_code': 'return {depot_ids: []};',
    },
    {
        'name': 'initialization',
        'optional': False,
        'in_bindings': [
            {
                'domain': 'input',
                'optional': False,
                'query': 'depot_ids.*{:depot_id}',
            },
            {
                'domain': 'input',
                'optional': False,
                'query': 'depot_settings[depot_id]{depot_settings}',
            },
            {'domain': 'input', 'optional': False, 'query': 'coeff'},
        ],
        'conditions': [],
        'out_bindings': [
            {
                'alias': 'depot_data',
                'optional': False,
                'query': 'depots[?(@.id==depot_id)]',
            },
        ],
        'source_code': (
            'return {depot_data: {id: depot_id, '
            'settings: depot_settings, coeff: coeff}};'
        ),
    },
]


async def test_pipeline_compile(taxi_grocery_surge):
    pipeline = {'id': '0', 'name': 'new', 'stages': NEW_STAGES_LIST}

    response = await taxi_grocery_surge.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    assert response.status_code == 200, response.content

    expected_response = {
        'metadata': {
            'stages': [
                {'name': 'start', 'arguments': []},
                {
                    'name': 'initialization',
                    'arguments': [
                        {'name': 'coeff', 'type': 'any', 'optional': True},
                        {'name': 'depot_id', 'type': 'any', 'optional': True},
                        {
                            'name': 'depot_settings',
                            'type': 'any',
                            'optional': True,
                        },
                    ],
                },
            ],
        },
    }

    def _arguments_sorter(meta):
        for stage in meta['metadata']['stages']:
            stage['arguments'].sort(key=lambda arg: arg['name'])
        return meta

    assert _arguments_sorter(response.json()) == _arguments_sorter(
        expected_response,
    )


async def test_schema_api_error(taxi_grocery_surge):
    def _check_response(response):
        assert response.status_code == 400
        response_json = response.json()
        assert response_json['code'] == INVALID_API_ERROR_CODE

    pipeline = {'id': '0', 'name': 'new', 'stages': []}

    # Missing name
    del pipeline['name']
    response = await taxi_grocery_surge.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)
    pipeline['name'] = 'new'

    # Stages with wrong type
    pipeline['stages'] = {}
    response = await taxi_grocery_surge.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)


async def test_compile_error(taxi_grocery_surge):
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
                        'query': 'depot_ids.*{:depot_id}',
                    },
                ],
                'conditions': [],
                'out_bindings': [],
                'source_code': 'return {}',
            },
        ],
    }

    response = await taxi_grocery_surge.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )
    _check_response(response)
