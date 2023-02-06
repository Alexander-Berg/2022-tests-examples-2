import pytest

from taxi_exp import util
from taxi_exp.generated.cron import run_cron as cron_run
from taxi_exp.util import pg_helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.stuff.send_alert_after_update_experiments import common

EXPERIMENT_NAME = 'experiment'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'watchers_alerts': {
                    'template_name': 'template.j2',
                    'diff_template_name': 'diff_template.j2',
                    'chunk_size': 10,
                    'subject': 'Updation experiments report',
                    'date_threshold': 10,
                },
            },
            'common': {
                'in_set_max_elements_count': 100,
                'trait_tags_v2': {
                    'test_1': {'availability': ['__any__']},
                    'test_2': {'availability': ['__any__']},
                },
            },
        },
    },
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
)
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-09T12:00:00')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_case(taxi_exp_client):
    await common.fill_experiments(taxi_exp_client, EXPERIMENT_NAME)
    response = await pg_helpers.fetch(
        taxi_exp_client.app['pool'],
        """UPDATE clients_schema.experiments
           SET last_manual_update=$1::timestamp
           RETURNING *
        ;""",
        util.parse_and_clean_datetime('2018-12-15T12:00:00'),
    )

    await cron_run.main(
        ['taxi_exp.stuff.send_alert_after_update_experiments', '-t', '0'],
    )

    response = await pg_helpers.fetch(
        taxi_exp_client.app['pool'], 'SELECT * FROM clients_schema.watchers;',
    )
    assert [item['last_revision'] for item in response] == [2, 2]
