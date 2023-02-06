import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'test_name'


@pytest.mark.parametrize(
    'action_time, expected_code',
    [
        (
            {
                'from': '2000-01-01T00:00:00+0300',
                'to': '2019-01-08T12:00:00+0300',
            },
            200,
        ),
        ({'from': '2000-01-01T00:00:00+0300', 'to': ''}, 400),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_action_time(taxi_exp_client, action_time, expected_code):
    data = experiment.generate(
        EXPERIMENT_NAME, action_time=action_time, enabled=False,
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )
    assert response.status == expected_code, await response.text()
