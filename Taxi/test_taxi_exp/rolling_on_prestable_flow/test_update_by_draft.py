import pytest

from taxi_exp.lib import trait_tags as trait_tags_module
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'Exp:Correct_Name'


@pytest.mark.parametrize('is_analytical', [True, False])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'prestable_flow': True,
                'check_biz_revision': True,
                'allow_write_pre_statistics': True,
            },
        },
    },
)
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-01T00:00:00.000+0000')
async def test(taxi_exp_client, patch_util_now, mocked_time, is_analytical):
    trait_tags = [trait_tags_module.ANALYTICAL_TAG] if is_analytical else []
    body = await helpers.init_exp(
        taxi_exp_client, experiment.generate(NAME, trait_tags=trait_tags),
    )
    last_modified_at = body['last_modified_at']
    first_biz_revision = body['biz_revision']

    body = experiment.generate(
        NAME,
        default_value={},
        schema='type: object\nadditionalProperties: false\n',
        trait_tags=[trait_tags_module.PRESTABLE_TAG],
        prestable_flow=experiment.make_prestable_flow(wait_on_prestable=10),
    )
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': last_modified_at},
        json=body,
    )
    assert response.status == 200, await response.text()
    response_body = await response.json()
    assert response_body['data']['status_wait_prestable'] == 'no_warning'
    check_body = response_body['data']['experiment']
    assert check_body['prestable_flow'] == {
        'rollout_stable_time': (
            f'{experiment.CURRENT_YEAR}-01-01T00:00:10+03:00'
        ),
        'wait_on_prestable': 10,
    }

    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/apply/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': last_modified_at},
        json=response_body['data'],
    )
    assert response.status == 200, await response.text()

    assert [
        item['changes_source']
        for item in await db.get_prestable_events(taxi_exp_client.app)
    ] == ['update']

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    check_body = await response.json()
    last_biz_revision = check_body['biz_revision']

    if is_analytical:
        assert first_biz_revision + 1 == last_biz_revision
