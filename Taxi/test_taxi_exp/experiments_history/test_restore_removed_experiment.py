import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

NAME = 'experiment_for_restore'


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.now('2020-11-01T23:59:59+03:00')
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_experiment_removing': True,
                'show_removed': True,
            },
        },
    },
)
async def test(taxi_exp_client):
    # generate experiment body
    body = experiment.generate(
        consumers=[{'name': 'test_consumer'}],
        default_value={},
        applications=[
            {
                'name': 'ios',
                'version_range': {'from': '0.0.0', 'to': '99.99.99'},
            },
        ],
        action_time={
            'from': '2020-01-01T12:35:00+03:00',
            'to': '2020-12-31T23:59:59+03:00',
        },
        name=NAME,
    )

    # create experiment
    create_response = await helpers.init_exp(taxi_exp_client, body)

    # remove experiment
    await helpers.remove_exp(
        taxi_exp_client, NAME, create_response['last_modified_at'],
    )
    # get removed experiment
    get_response = await helpers.get_experiment(taxi_exp_client, NAME)
    assert get_response['removed']
    assert 'removed_stamp' in get_response

    # success restore experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={
            'name': NAME,
            'last_modified_at': get_response['last_modified_at'],
            'revision': create_response['last_modified_at'],
        },
    )
    assert response.status == 200, await response.text()

    # check restore
    check_response = await helpers.get_experiment(taxi_exp_client, NAME)
    assert not check_response['removed']
    assert 'removed_stamp' not in check_response
