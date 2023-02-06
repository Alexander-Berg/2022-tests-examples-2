import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from taxi_exp.lib import trait_tags as trait_tags_module
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment'


@pytest.mark.parametrize('wait_on_prestable', [0, 60])
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'trait_tags': [
                    trait_tags_module.PRESTABLE_TAG,
                    trait_tags_module.ANALYTICAL_TAG,
                ],
                'prestable_flow': {
                    'processing_limit': 101,
                    'default_wait_on_prestable': 0,
                },
            },
        },
        'features': {
            'common': {
                'prestable_flow': True,
                'allow_write_pre_statistics': True,
                'check_biz_revision': True,
            },
        },
    },
)
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-01T00:00:00.000+0000')
async def test_prestable_flow(
        taxi_exp_client, patch_util_now, mocked_time, wait_on_prestable,
):
    # add experiments with prestable tag
    for index in range(10):
        if not index:
            trait_tags = [
                trait_tags_module.PRESTABLE_TAG,
                trait_tags_module.ANALYTICAL_TAG,
            ]
        else:
            trait_tags = [trait_tags_module.PRESTABLE_TAG]
        body = experiment.generate(
            trait_tags=trait_tags,
            prestable_flow=experiment.make_prestable_flow(wait_on_prestable),
        )
        response = await taxi_exp_client.post(
            '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={'name': EXPERIMENT_NAME + str(index)},
            json=body,
        )
        assert response.status == 200, await response.text()

    # move time to future
    mocked_time.sleep(wait_on_prestable + 60)

    # running cron
    await cron_run.main(['taxi_exp.stuff.prestable_flow', '-t', '0'])

    # check that prestable tag removed
    for index in range(10):
        response = await taxi_exp_client.get(
            '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={'name': EXPERIMENT_NAME + str(index)},
        )
        body = await response.json()
        assert trait_tags_module.PRESTABLE_TAG not in body['trait_tags']
        if not index:
            assert body['biz_revision'] == 2
        else:
            assert body['biz_revision'] == 1

    # check that statistic record is append
    response = await db.get_rolling_stats(taxi_exp_client.app)
    assert [item['changes_source'] for item in response] == ['add'] * 10 + [
        'taxi_exp.stuff.prestable_flow',
    ] * 10