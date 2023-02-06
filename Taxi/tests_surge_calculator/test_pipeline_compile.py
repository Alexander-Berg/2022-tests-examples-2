# pylint: disable=E1101,W0612
import pytest  # noqa: F401

INVALID_PIPELINE = 'invalid_pipeline'


async def test_basic(taxi_surge_calculator):
    pipeline = {
        'id': '0',
        'name': 'test_name',
        'consumer': 'taxi-surge',
        'stages': [
            {
                'conditions': [],
                'in_bindings': [],
                'name': 'start',
                'out_bindings': [{'alias': 'classes', 'query': 'classes'}],
                'source_code': 'return {classes: []};',
            },
            {
                'conditions': [],
                'in_bindings': [
                    {
                        'domain': 'input',
                        'query': 'request',
                        'children': [
                            {'query': 'point_a'},
                            {'query': 'point_b'},
                            {'query': 'tariff_zone'},
                            {'query': 'classes.*{class_idx:class_name}'},
                            {
                                'query': 'prefetched_counts',
                                'children': [
                                    {'query': 'pins'},
                                    {
                                        'query': 'counts',
                                        'children': [
                                            {'query': 'something_inside'},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'domain': 'resource',
                        'query': 'zone',
                        'children': [
                            {'query': 'base_class'},
                            {
                                'query': 'experiment',
                                'children': [
                                    {'query': 'is_active'},
                                    {'query': 'explicit_antisurge_threshold'},
                                    {
                                        'query': 'rules.*{rule_name:}',
                                        'children': [
                                            {'query': 'surge_rules'},
                                            {'query': 'surge_value'},
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'domain': 'output',
                        'query': 'classes.*{o_class_name:}',
                        'children': [{'query': 'value_raw'}],
                    },
                ],
                'name': 'stage_one',
                'out_bindings': [],
                'source_code': '',
            },
        ],
    }

    arguments = [
        {'name': 'point_a', 'type': 'array', 'optional': False},
        {'name': 'point_b', 'type': 'array', 'optional': True},
        {'name': 'tariff_zone', 'type': 'string', 'optional': True},
        {'name': 'class_idx', 'type': 'integer', 'optional': False},
        {'name': 'class_name', 'type': 'string', 'optional': False},
        {'name': 'pins', 'type': 'object', 'optional': True},
        {'name': 'something_inside', 'type': 'any', 'optional': True},
        {'name': 'base_class', 'type': 'string', 'optional': False},
        {'name': 'is_active', 'type': 'boolean', 'optional': False},
        {
            'name': 'explicit_antisurge_threshold',
            'type': 'number',
            'optional': True,
        },
        {'name': 'rule_name', 'type': 'string', 'optional': False},
        {'name': 'surge_rules', 'type': 'array', 'optional': False},
        {'name': 'surge_value', 'type': 'number', 'optional': True},
        {'name': 'o_class_name', 'type': 'string', 'optional': False},
        {'name': 'value_raw', 'type': 'number', 'optional': True},
    ]

    expected = {
        'metadata': {
            'stages': [
                {'name': 'start', 'arguments': []},
                {'name': 'stage_one', 'arguments': arguments},
            ],
        },
    }

    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == expected


@pytest.mark.parametrize(
    'pipeline, expected',
    [
        ({'name': 'test_name', 'stages': []}, '400'),
        ({'id': '0', 'stages': []}, '400'),
        ({'id': '0', 'name': 'test_name', 'stages': {}}, '400'),
        (
            {
                'id': '0',
                'name': 'test_name',
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
            },
            INVALID_PIPELINE,
        ),
        (
            {
                'id': '0',
                'name': 'test_name',
                'stages': [
                    {
                        'conditions': [],
                        'in_bindings': [],
                        'name': 'start',
                        'out_bindings': [{'alias': 'classes'}],
                        'source_code': 'return null;',
                    },
                ],
            },
            INVALID_PIPELINE,
        ),
    ],
    ids=[
        'missing id',
        'missing name',
        'wrong stages type',
        'invalid pipeline',
        'invalid out binding',
    ],
)
async def test_compile_error(taxi_surge_calculator, pipeline, expected):
    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/compile', json={'pipeline': pipeline},
    )

    assert response.status_code == 400
    data = response.json()
    assert data['code'] == expected


@pytest.mark.parametrize(
    'out_binding, expected_code',
    [
        pytest.param(
            {
                'query': 'classes[?(@.name==sample_name)]',
                'children': [{'query': 'surge', 'alias': 'surge'}],
            },
            400,
            id='expose one field',
        ),
        pytest.param(
            {
                'query': 'classes[?(@.name==sample_name)]',
                'children': [
                    {'query': 'surge', 'alias': 'surge'},
                    {'query': 'name', 'alias': 'name'},
                ],
            },
            400,
            id='expose two fields',
        ),
        pytest.param(
            {'query': 'classes', 'alias': 'classes'},
            200,
            id='expose top level array',
        ),
        pytest.param(
            {'query': 'classes[?(@.name==sample_name)]', 'alias': 'class'},
            200,
            id='expose top level elements',
        ),
        pytest.param(
            {
                'query': 'classes[?(@.name==sample_name)]',
                'children': [
                    {'query': 'surge', 'alias': 'surge'},
                    {'query': 'name', 'alias': 'name'},
                    {'query': 'value_raw', 'alias': 'value_raw'},
                ],
            },
            200,
            id='expose all required',
        ),
        pytest.param(
            {
                'query': 'classes[?(@.name==sample_name)]',
                'children': [
                    {
                        'query': 'surge',
                        'children': [
                            {'query': 'surcharge', 'alias': 'surcharge'},
                        ],
                    },
                    {'query': 'name', 'alias': 'name'},
                    {'query': 'value_raw', 'alias': 'value_raw'},
                ],
            },
            400,
            id='expose deeper',
        ),
    ],
)
async def test_required_validation(
        taxi_surge_calculator, out_binding, expected_code,
):
    pipeline = {
        'id': '0',
        'name': 'validation_test',
        'consumer': 'taxi-surge',
        'stages': [
            {
                'conditions': [],
                'in_bindings': [
                    {
                        'domain': 'input',
                        'query': 'layer_meta.name{sample_name}',
                    },
                ],
                'out_bindings': [out_binding],
                'name': 'sample_usage',
                'optional': False,
                'source_code': 'return {};',
            },
        ],
    }

    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/compile',
        json={'pipeline': pipeline, 'extended_check': True},
    )
    response_json = response.json()
    assert response.status_code == expected_code, response_json
    if expected_code == 400:
        assert response_json['code'] == INVALID_PIPELINE
        assert 'cannot be filled in pipeline' in response_json['message']


@pytest.mark.parametrize(
    'in_bindings, out_bindings, expected',
    [
        pytest.param(
            [{'domain': 'input', 'query': 'required_categories.foobar'}],
            [],
            {
                'stages': {
                    'sample_usage': {
                        'in_bindings': [
                            {
                                'path': [0],
                                'error': {
                                    'message': (
                                        'accessing array unknown '
                                        'static property "foobar"'
                                    ),
                                },
                            },
                        ],
                        'out_bindings': [],
                    },
                },
            },
            id='input binding error',
        ),
        pytest.param(
            [
                {'domain': 'input', 'query': 'required_categories'},
                {
                    'domain': 'input',
                    'query': 'request',
                    'children': [
                        {'query': 'user_id'},
                        {'query': 'non_existent'},
                    ],
                },
            ],
            [],
            {
                'stages': {
                    'sample_usage': {
                        'in_bindings': [
                            {
                                'path': [1, 1],
                                'error': {
                                    'message': (
                                        'no property named "non_existent" '
                                        'in object schema'
                                    ),
                                },
                            },
                        ],
                        'out_bindings': [],
                    },
                },
            },
            id='child input binding error',
        ),
        pytest.param(
            [],
            [
                {
                    'query': 'classes.econom',
                    'children': [
                        {'alias': 'name', 'query': 'name'},
                        {'alias': 'foobar', 'query': 'foobar'},
                    ],
                },
            ],
            {
                'stages': {
                    'sample_usage': {
                        'in_bindings': [],
                        'out_bindings': [
                            {
                                'path': [0, 1],
                                'error': {
                                    'message': (
                                        'no property named "foobar" '
                                        'in object schema'
                                    ),
                                },
                            },
                        ],
                    },
                },
            },
            id='output binding error',
        ),
    ],
)
async def test_compile_error_details(
        taxi_surge_calculator, in_bindings, out_bindings, expected,
):
    pipeline = {
        'id': '0',
        'name': 'details_test',
        'consumer': 'taxi-surge',
        'stages': [
            {
                'conditions': [],
                'in_bindings': in_bindings,
                'out_bindings': out_bindings,
                'name': 'sample_usage',
                'optional': False,
                'source_code': 'return {};',
            },
        ],
    }
    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/compile',
        json={'pipeline': pipeline, 'extended_check': True},
    )
    response_json = response.json()

    assert response.status_code == 400
    assert expected == response_json['details'], response_json
