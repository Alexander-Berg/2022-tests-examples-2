import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_bad_predicate(taxi_exp_client):
    data = experiment.generate_default(
        match_predicate={
            'init': {
                'arg_name': 'user_id',
                'divisor': 100,
                'range_from': 0,
                'range_to': 30,
                'salt': 'd6543a74f43860bc4d88edddc33efca9',
                'set_elem_type': 'string',  # bad argument
            },
            'type': 'mod_sha1_with_salt',
        },
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name'},
        json=data,
    )
    assert response.status == 400
