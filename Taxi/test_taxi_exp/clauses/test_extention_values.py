import copy
import json
import typing

import pytest

from test_taxi_exp import helpers


EXPERIMENT = {
    'clauses': [
        {
            'extension_method': 'replace',
            'predicate': {'type': 'true'},
            'title': '1',
            'value': {
                'another_key': 321,
                'array': [1, 2, 3],
                'deep_key': {'other_inner_key': 'aaaaaa'},
            },
        },
    ],
    'default_value': {
        'array': [99, 67, 56],
        'deep_key': {'inner_key': 'vvvvvv'},
        'key': 123,
    },
    'description': 'TEST_EXP_EXTENDED',
    'match': {
        'action_time': {
            'from': '2019-02-14T13:30:00.000Z',
            'to': '2019-02-14T13:38:00.000Z',
        },
        'consumers': [{'name': 'test_consumer'}],
        'enabled': False,
        'predicate': {'type': 'true'},
        'schema': (
            'description: test value\n'
            'type: object\n'
            'additionalProperties: false\n'
            'required:\n'
            '  - key\n'
            'default:\n'
            '  any_of:\n'
            '  - key: 1\n'
            '  - different_key: \n'
            'properties:\n'
            '  key:\n'
            '    type: integer\n'
            '  different_key:\n'
            '    type: string\n'
            '  another_key:\n'
            '    type: integer\n'
            '  deep_key:\n'
            '    type: object\n'
            '  array:\n'
            '    type: array\n'
            '  other_inner_key:\n'
            '    type: string'
        ),
    },
    'name': 'TEST_EXP_EXTENDED',
    'department': 'common',
}


class ExtentionMethodCase(typing.NamedTuple):
    extention_method: str  # noqa
    expected_calculated_value: typing.Optional[dict]  # noqa
    ext_value_is_exists: bool  # noqa


@pytest.mark.parametrize(
    'extention_method,expected_calculated_value,ext_value_is_exists',
    [
        ExtentionMethodCase(
            extention_method='replace',
            expected_calculated_value=None,
            ext_value_is_exists=False,
        ),
        ExtentionMethodCase(
            extention_method='extend',
            expected_calculated_value={
                'key': 123,
                'another_key': 321,
                'deep_key': {'other_inner_key': 'aaaaaa'},
                'array': [1, 2, 3],
            },
            ext_value_is_exists=True,
        ),
        ExtentionMethodCase(
            extention_method='deep_extend',
            expected_calculated_value={
                'key': 123,
                'another_key': 321,
                'deep_key': {
                    'inner_key': 'vvvvvv',
                    'other_inner_key': 'aaaaaa',
                },
                'array': [1, 2, 3],
            },
            ext_value_is_exists=True,
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_extend_value(
        extention_method,
        expected_calculated_value,
        ext_value_is_exists,
        taxi_exp_client,
):
    experiment = copy.deepcopy(EXPERIMENT)
    experiment['clauses'][0]['extension_method'] = extention_method
    if extention_method == 'replace':
        experiment['clauses'][0]['value']['key'] = 123
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-YaTaxi-Api-Key': 'admin_secret'},
        params={'name': 'test_name'},
        json=experiment,
    )
    assert response.status == 200, await response.text()

    result = await helpers.db.get_experiment(taxi_exp_client.app, 'test_name')
    clauses = json.loads(result['exp_clauses'])

    if ext_value_is_exists:
        extended_value = clauses[0]['extended_value']
        assert extended_value == expected_calculated_value
    else:
        assert 'extended_value' not in clauses[0]
