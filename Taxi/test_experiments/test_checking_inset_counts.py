import pytest

from test_taxi_exp.helpers import experiment

EXISTED_EXPERIMENT_NAME = 'existed_experiment'
NEW_EXPERIMENT_NAME = 'new_experiment'

COUNT_ELEMENTS_IN_INSET = 100


@pytest.mark.parametrize(
    'count,status',
    [(COUNT_ELEMENTS_IN_INSET, 200), (COUNT_ELEMENTS_IN_INSET + 1, 400)],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {'in_set_max_elements_count': COUNT_ELEMENTS_IN_INSET},
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql', 'existed_experiment.sql'])
async def test_checking_inset_counts(taxi_exp_client, count, status):
    experiment_body = experiment.generate(
        EXISTED_EXPERIMENT_NAME,
        match_predicate=experiment.inset_predicate(
            [value for value in range(count)],
            arg_name='zone_id',
            set_elem_type='int',
        ),
    )

    # update existed experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXISTED_EXPERIMENT_NAME, 'last_modified_at': 1},
        json=experiment_body,
    )
    assert response.status == status

    # create new experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': NEW_EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == status
