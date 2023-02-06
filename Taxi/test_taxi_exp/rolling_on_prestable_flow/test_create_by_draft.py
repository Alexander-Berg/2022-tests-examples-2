import pytest

from taxi_exp.lib import trait_tags as trait_tags_module
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'Exp:Correct_Name'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'prestable_flow': True,
                'allow_write_pre_statistics': True,
            },
        },
    },
)
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-01T00:00:00.000+0000')
async def test(taxi_exp_client, patch_util_now, mocked_time):
    body = experiment.generate(
        NAME,
        default_value={},
        schema='type: object\nadditionalProperties: false\n',
        trait_tags=[trait_tags_module.PRESTABLE_TAG],
        prestable_flow=experiment.make_prestable_flow(wait_on_prestable=10),
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()
    response_body = await response.json()
    check_body = response_body['data']
    assert check_body['status_wait_prestable'] == 'no_warning'
    assert check_body['experiment']['prestable_flow'] == {
        'rollout_stable_time': (
            f'{experiment.CURRENT_YEAR}-01-01T00:00:10+03:00'
        ),
        'wait_on_prestable': 10,
    }

    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=check_body,
    )
    assert response.status == 200, await response.text()

    assert [
        item['changes_source']
        for item in await db.get_prestable_events(taxi_exp_client.app)
    ] == ['add']
