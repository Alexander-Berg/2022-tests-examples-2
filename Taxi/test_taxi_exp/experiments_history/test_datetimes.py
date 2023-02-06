import datetime

import pytest

from taxi_exp import util
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'
DELTA = datetime.timedelta(seconds=20)


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_experiments_history(taxi_exp_client):
    data = experiment.generate(
        EXPERIMENT_NAME,
        enabled=True,
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
        consumers=[{'name': 'test_consumer'}, {'name': 'launch'}],
        owners=[],
        watchers=[],
        trait_tags=[],
        st_tickets=['TAXIEXP-228'],
        department=None,
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    # update experiment
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200, await response.text()

    # off experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/disable/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 2},
    )
    assert response.status == 200, await response.text()

    # on experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/enable/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 3},
    )
    assert response.status == 200, await response.text()

    # get experiments by rev and check last_manual_update
    stamps = []
    for rev in range(1, 4):
        response = await taxi_exp_client.get(
            '/v1/history/',
            headers={'X-Ya-Service-Ticket': '123'},
            params={'revision': rev},
        )
        assert response.status == 200, await response.text()
        content = await response.json()
        stamps.append(
            util.parse_and_clean_datetime(
                content['body'].pop('last_manual_update'),
            ),
        )

    for index, stamp in enumerate(stamps[:-1]):
        for checked_stamp in stamps[index + 1 :]:
            assert stamp - checked_stamp < DELTA, (stamp, checked_stamp)
