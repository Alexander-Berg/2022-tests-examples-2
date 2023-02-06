import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from taxi_exp.util import pg_helpers
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files
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
EXPERIMENT_NAME = 'silent_experiment'
WATCHER_LOGIN = 'another_login'
TAG_NAME = 'trusted'
TAG_CONTENT = b'trusted content'
STEPS = 1
UPDATE_DATE_QUERY = (
    """
WITH t AS (
    SELECT id FROM clients_schema.experiments
    WHERE name='{name}'
)
UPDATE clients_schema.watchers
        SET last_revision=$1::BIGINT
        FROM t
        WHERE
            experiment_id=t.id
            AND watcher_login=$2::text
    ;
""".format(
        name=EXPERIMENT_NAME,
    )
)


@pytest.fixture
async def _init(patch_user_api, patch_staff, taxi_exp_client):
    for phone_id, phone in zip(common.USER_API_PHONE_IDS, common.PHONES):
        patch_user_api.add(phone_id, phone)

    patch_staff.fill(CONVERT_LOGIN_TO_EMAIL)

    # create trusted file
    response = await files.post_trusted_file(
        taxi_exp_client, TAG_NAME, TAG_CONTENT,
    )
    assert response.status == 200, await response.text()

    # create exp
    body = experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=(experiment.userhas_predicate(TAG_NAME)),
        applications=[
            {
                'name': 'android',
                'version_range': {'from': '3.14.0', 'to': '3.20.0'},
            },
        ],
        consumers=[{'name': 'test_consumer'}],
        owners=[],
        watchers=[WATCHER_LOGIN],
        trait_tags=['test_1', 'test_2'],
        st_tickets=['TAXIEXP-228'],
    )
    first_obj = await helpers.init_exp(taxi_exp_client, body)
    # mark watcher record as sended
    await pg_helpers.fetch(
        taxi_exp_client.app['pool'],
        UPDATE_DATE_QUERY,
        first_obj['last_modified_at'],
        WATCHER_LOGIN,
    )

    # update trusted file
    for step in range(STEPS):
        response = await files.post_trusted_file(
            taxi_exp_client,
            TAG_NAME,
            (TAG_CONTENT.decode('utf-8') + str(step)).encode('utf-8'),
        )
        assert response.status == 200, await response.text()

    return first_obj


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
@pytest.mark.now(f'{experiment.CURRENT_YEAR}-01-09T12:00:00')
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'watchers_alerts': {
                    'template_name': 'template.j2',
                    'chunk_size': 10,
                    'subject': 'Updation experiments report',
                    'date_threshold': 1,
                },
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
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
        taxi_exp_client, patch_sticker, _init,
):
    first_obj = _init

    # check revisions before
    last_obj = await helpers.get_experiment(taxi_exp_client, EXPERIMENT_NAME)
    assert (
        last_obj['last_modified_at'] == first_obj['last_modified_at'] + STEPS
    )
    assert last_obj['last_manual_update'] == first_obj['last_manual_update']

    response = await pg_helpers.fetch(
        taxi_exp_client.app['pool'], 'SELECT * FROM clients_schema.watchers;',
    )
    assert [item['last_revision'] for item in response] == [
        first_obj['last_modified_at'],
    ]

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.send_alert_after_update_experiments', '-t', '0'],
    )

    # check no send emails
    assert not patch_sticker.data

    # check revisions after
    response = await pg_helpers.fetch(
        taxi_exp_client.app['pool'], 'SELECT * FROM clients_schema.watchers;',
    )
    assert [item['last_revision'] for item in response] == [
        last_obj['last_modified_at'],
    ]
