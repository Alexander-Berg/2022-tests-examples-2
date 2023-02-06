import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'watchers_alerts': {
                    'template_name': 'template.j2',
                    'diff_template_name': 'diff_template.j2',
                    'chunk_size': 10,
                },
            },
            'common': {'in_set_max_elements_count': 100},
        },
    },
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_fill_experiments(taxi_exp_client):
    data = experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=(
            experiment.allof_predicate(
                [
                    experiment.inset_predicate([1, 2, 3], set_elem_type='int'),
                    experiment.inset_predicate(
                        ['msk', 'spb'],
                        set_elem_type='string',
                        arg_name='city_id',
                    ),
                    experiment.gt_predicate(
                        '1.1.1',
                        arg_name='app_version',
                        arg_type='application_version',
                    ),
                ],
            )
        ),
        applications=[
            {
                'name': 'android',
                'version_range': {'from': '3.14.0', 'to': '3.20.0'},
            },
        ],
        consumers=[{'name': 'test_consumer'}],
        owners=[],
        watchers=['another_login', 'first-login'],
        trait_tags=[],
        st_tickets=['TAXIEXP-228'],
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    # get experiment
    response = await taxi_exp_client.get(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['watchers'] == ['another_login', 'first-login']

    # update experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200, await response.text()

    # get experiment
    response = await taxi_exp_client.get(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['watchers'] == ['another_login', 'first-login']
