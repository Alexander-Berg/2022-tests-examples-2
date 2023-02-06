import json

import pytest

# should be True only in local changes
DUMP_ACTUAL_SCHEMA = False
INVALID_LOCATION_ERROR = 'invalid_location'


@pytest.mark.parametrize(
    'stage_name, binding_idx, stage_arg_name, expected, schema_name',
    [
        ('logic_1', 0, None, 200, 'input'),
        ('logic_1', 1, None, 200, 'pin_stats'),
        ('logic_1', 2, None, 200, 'zone'),
        ('logic_2', 0, None, 200, 'surge_value_map'),
        ('logic_3', 0, None, 200, 'output'),
        (
            'logic_1',
            99,
            None,
            (
                400,
                'Binding index is out of bound: '
                'requested 99, but stage has only 3',
            ),
            None,
        ),
        (
            'logic_1',
            None,
            None,
            (400, 'No location.in_binding_idx, nor location.stage_arg_name'),
            None,
        ),
        (
            'logic_3',
            0,
            'surge',
            (
                400,
                'Has both location.in_binding_idx, '
                'and location.stage_arg_name',
            ),
            None,
        ),
        (
            'logic_1',
            None,
            'not_existing',
            (
                400,
                'No argument named \'not_existing\' '
                'found in stage \'logic_1\'',
            ),
            None,
        ),
        ('empty_query', 0, None, 200, 'input'),
        ('empty_query', 1, None, 200, 'output'),
        ('empty_query', 2, None, 200, 'empty_query_resources'),
        ('logic_3', None, 'surge', 200, 'surge'),
    ],
)
async def test_basic(
        taxi_surge_calculator,
        load_json,
        stage_name,
        binding_idx,
        stage_arg_name,
        expected,
        schema_name,
):
    if isinstance(expected, tuple):
        expected_code, expected_message = expected
    else:
        expected_code = expected
        expected_message = None

    expected_schemas = load_json('calc_surge_schemas.json')
    pipeline = load_json('pipeline.json')

    request_body = {
        'pipeline': pipeline,
        'location': {'stage_name': stage_name},
    }

    if binding_idx is not None:
        request_body['location']['in_binding_idx'] = binding_idx

    if stage_arg_name is not None:
        request_body['location']['stage_arg_name'] = stage_arg_name

    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/schema', json=request_body,
    )
    assert response.status_code == expected_code
    response_json = response.json()
    if expected_code == 200:
        actual_schema = response_json['schema']
        expected_schema = expected_schemas[schema_name]
        if DUMP_ACTUAL_SCHEMA:
            with open(f'.{schema_name}_dump.schema.json', 'w+') as fp:
                json.dump(actual_schema, fp, ensure_ascii=False, indent=2)
        assert actual_schema == expected_schema
    else:
        assert response_json['code'] == INVALID_LOCATION_ERROR

    if expected_message is not None:
        assert response_json['message'] == expected_message
