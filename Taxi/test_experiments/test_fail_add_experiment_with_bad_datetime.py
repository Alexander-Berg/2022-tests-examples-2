# pylint: disable=invalid-name
import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_fail_add_experiment_with_bad_datetime(taxi_exp_client):
    data = experiment.generate(
        match_predicate=experiment.eq_predicate(
            'a2019-01-12T12:99:00Z', arg_type='datetime', arg_name='test',
        ),
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'CHECK_PREDICATES_SCHEMA_ERROR',
        'message': (
            'predicate has incorrect format: '
            '{\'type\': \'eq\', \'init\': {\'value\': '
            '\'a2019-01-12T12:99:00Z\', '
            '\'arg_name\': \'test\', \'arg_type\': '
            '\'datetime\'}} '
            'is not valid under any of the given schemas, '
            'check it by path: `match.predicate`'
        ),
    }
