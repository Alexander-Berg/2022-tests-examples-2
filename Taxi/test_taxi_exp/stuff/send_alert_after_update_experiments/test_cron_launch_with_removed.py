import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.stuff.send_alert_after_update_experiments import common

CONVERT_LOGIN_TO_EMAIL = {
    'another_login': {
        'login': 'another_login',
        'work_email': 'work_email@yandex-team.ru',
    },
    'first-login': {
        'login': 'first-login',
        'work_email': 'team-t@yandex-team.ru',
    },
}
EXPERIMENT_NAME = 'experiment'


@pytest.fixture(autouse=True)
def _init(patch_user_api, patch_staff):
    for phone_id, phone in zip(common.USER_API_PHONE_IDS, common.PHONES):
        patch_user_api.add(phone_id, phone)
    patch_staff.fill(CONVERT_LOGIN_TO_EMAIL)


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-09T12:00:00')
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
        'features': {
            'common': {
                'enable_experiment_removing': True,
                'enable_convert_phone_to_phone_id': True,
            },
        },
    },
    EXP_BACK_EMAIL_FOR_ALERTS='serg-novikov@yandex-team.ru',
)
async def test_send_alert_after_update_experiment(
        taxi_exp_client, patch_sticker,
):
    await common.fill_experiments(taxi_exp_client, EXPERIMENT_NAME)

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.send_alert_after_update_experiments', '-t', '0'],
    )
    assert len(patch_sticker.data) == 2
