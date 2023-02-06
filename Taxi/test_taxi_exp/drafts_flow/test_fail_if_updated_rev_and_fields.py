import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'closed_experiment'


@pytest.mark.config(
    EXP_EXTENDED_DRAFTS=[
        {
            'DRAFT_NAME': 'update_closed_experiment',
            'NEED_CHECKING_FILES': True,
            'NEED_CHECKING_BODY': True,
        },
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'closed_experiment.sql'))
async def test_fail_if_updated_rev_and_fields(taxi_exp_client):
    experiment_body = experiment.generate(EXPERIMENT_NAME)

    response = await taxi_exp_client.post(
        '/v1/closed-experiments/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=experiment_body,
    )
    assert response.status == 200

    await db.update_experiment_field(
        taxi_exp_client.app, EXPERIMENT_NAME, default_value={},
    )

    apply_request = (await response.json())['data']
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=apply_request,
    )
    assert response.status == 409
    body = await response.json()
    assert body['code'] == 'FAIL_APPLY_EXPERIMENT'
