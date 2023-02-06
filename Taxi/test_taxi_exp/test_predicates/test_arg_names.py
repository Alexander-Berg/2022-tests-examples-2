import typing

import pytest

from test_taxi_exp import helpers

EXPERIMENT_NAME = 'test_predicate_by_schema'


class Case(typing.NamedTuple):
    arg_name: str
    is_valid: bool


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(arg_name='1233', is_valid=False),
        Case(arg_name='a1233', is_valid=True),
        Case(arg_name='_1233', is_valid=True),
        Case(arg_name='A1233', is_valid=True),
        Case(arg_name='A[3]', is_valid=True),
        Case(arg_name='address.street', is_valid=True),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql', 'fill.sql'])
async def test_arg_name(taxi_exp_client, arg_name, is_valid):
    experiment = helpers.experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=helpers.experiment.eq_predicate(
            1, arg_name=arg_name, arg_type='int',
        ),
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment,
    )

    if is_valid:
        assert response.status == 200
    else:
        assert response.status != 200


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(arg_name='1233', is_valid=False),
        Case(arg_name='a1233', is_valid=True),
        Case(arg_name='_1233', is_valid=True),
        Case(arg_name='A1233', is_valid=True),
        Case(arg_name='A[3]', is_valid=False),
        Case(arg_name='address.street', is_valid=True),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql', 'fill.sql'])
async def test_tag_name(taxi_exp_client, arg_name, is_valid):
    experiment = helpers.experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=helpers.experiment.userhas_predicate(tag=arg_name),
    )
    await helpers.files.post_trusted_file(taxi_exp_client, arg_name, b'')

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment,
    )

    if is_valid:
        assert response.status == 200
    else:
        assert response.status != 200
