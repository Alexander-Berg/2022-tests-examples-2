# pylint: disable=protected-access
import itertools

import pytest

from taxi_exp import cron_run
from taxi_exp.stuff import send_alert_after_update_experiments as send_module
from test_taxi_exp.helpers import db
from test_taxi_exp.stuff.send_alert_after_update_experiments import common

EXPERIMENT_NAME = 'drivers_experiment'


@pytest.fixture(autouse=True)
def _init_phones(patch_user_api):
    for phone_id, phone in zip(common.USER_API_PHONE_IDS, common.PHONES):
        patch_user_api.add(phone_id, phone)


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
@pytest.mark.parametrize(
    'data, expected, with_exception',
    [
        ([], 'Inform 123 for updates:', True),
        pytest.param(
            [
                send_module.ExperimentChangeInfo(
                    name=EXPERIMENT_NAME,
                    exp_id=1,
                    is_config=False,
                    current_rev=2,
                    previous_rev=1,
                    revisions=[2],
                    update_time='2021-01-22T19:08:12.310762+03:00',
                ),
            ],
            """Inform 123 for updates:

<!--





-->
<p>Experiment drivers_experiment updated: 2021-01-22T19:08:12.310762+03:00</p>
<h3><a href="https://tariff-editor.taxi.yandex-team.ru/experiments3/"""
            'experiments/show/drivers_experiment/all/1_2">'
            'View diff in tariff-editor '
            """for experiment drivers_experiment</a></h3>
""",
            False,
            id='success_generate_by__diff_template',
        ),
        pytest.param(
            [
                send_module.ExperimentChangeInfo(
                    name=EXPERIMENT_NAME,
                    exp_id=1,
                    is_config=False,
                    current_rev=2,
                    previous_rev=1,
                    revisions=[2],
                    update_time='2021-01-22T19:09:55.885557+03:00',
                ),
            ],
            """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Notify 123 for updates:</title>
</head>
<body>
<h1>Notify 123 for updates</h1>

<!--





-->
<p>Experiment drivers_experiment updated: 2021-01-22T19:09:55.885557+03:00</p>
<h3><a href="https://tariff-editor.taxi.yandex-team.ru/experiments3/"""
            'experiments/show/drivers_experiment/all/1_2">'
            'View diff in tariff-editor for experiment drivers_experiment'
            """</a></h3>

</body>""",
            False,
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'settings': {
                        'backend': {
                            'watchers_alerts': {
                                'template_name': 'template_v2.j2',
                                'diff_template_name': 'diff_template_v2.j2',
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
            ),
            id='success_generate_by__diff_template_v2',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_get_changed_experiments_by_watchers(
        taxi_exp_client, data, expected, with_exception,
):
    await common.fill_experiments(taxi_exp_client, EXPERIMENT_NAME)

    taxi_exp_client.app.templates_store = (
        cron_run.TaxiExpCronApplication._get_templates_store()
    )
    alert_sender = send_module.AlertSender(taxi_exp_client.app)

    if with_exception:
        with pytest.raises(send_module.NoNeedSendMessage):
            await alert_sender.get_text_message('123', data)
        return

    result = await alert_sender.get_text_message('123', data)
    for index, lines in enumerate(
            itertools.zip_longest(expected.splitlines(), result.splitlines()),
    ):
        e_line, line = lines
        if any(
                (
                    'last_manual_update' in e_line,
                    'created' in e_line,
                    'update_time' in e_line,
                    '<p>Experiment updated' in e_line,
                ),
        ):
            continue
        assert e_line == line, index + 1
