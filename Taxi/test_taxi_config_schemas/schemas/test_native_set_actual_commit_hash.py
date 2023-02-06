# pylint: disable=unused-variable
import pytest

from config_schemas_lib import storage

from taxi_config_schemas import config_models
from taxi_config_schemas import db_wrappers
from taxi_config_schemas.generated.cron import run_cron
from test_taxi_config_schemas.helpers import git_helper

CONFIGS = [
    {
        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'description': '',
        'group': 'chatterbox',
        'default': {},
        'tags': [],
        'full-description': '',
        'maintainers': [],
        'schema': {'additionalProperties': False},
        'wiki': '',
        'turn-off-immediately': False,
    },
]


@pytest.mark.config(
    CONFIG_SCHEMAS_RUNTIME_FEATURES={
        'report_collect_ticket': 'TAXIEXP-454',
        'report_method': 'add_to_one_ticket',
        'taxi_config_schemas.crontasks.send_alerts_for_update': 'enabled',
    },
)
@pytest.mark.custom_patch_configs_by_group(configs=CONFIGS)
async def test_native_set_actual_commit_hash(
        patch,
        git_setup,
        web_context,
        patcher_tvm_ticket_check,
        web_app_client,
):
    @patch(
        'taxi_config_schemas.report_manager.'
        'collect_to_ticket.CommentCommonTicket._send_comment',
    )
    async def fake_send(*args, **kwargs):
        pass

    local, remote = git_setup
    first_hash, last_hash = await git_helper.create_git_repos(
        repo_root=local,
        remote_repo=remote,
        skip_commits=1,
        args=[
            git_helper.GitArg(
                config=config_models.BaseConfig(
                    name='STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                    description='',
                    full_description='',
                    wiki='',
                    group='chatterbox',
                    default={},
                    tags=[],
                    validator_declarations=None,
                    schema={'additionalProperties': False},
                    maintainers=[],
                    turn_off_immediately=False,
                ),
                commit_message=(
                    'Aleksandr Piskarev',
                    (
                        'feat conf: fix startreck extra ticket\n\n'
                        'Relates: TAXI-123'
                    ),
                ),
            ),
            git_helper.GitArg(
                config=config_models.BaseConfig(
                    name='STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                    description='',
                    full_description='',
                    wiki='',
                    group='chatterbox',
                    default={},
                    tags=[],
                    validator_declarations=None,
                    schema={'additionalProperties': True},
                    maintainers=[],
                    turn_off_immediately=False,
                ),
                commit_message=(
                    'Natalia Dunaeva',
                    (
                        'feat configs: add Startreck Extra Ticket (#1234)\n\n'
                        'Relates: TAXI-124'
                    ),
                ),
            ),
        ],
    )
    await db_wrappers.set_actual_commit_hash(
        web_context.mongo, first_hash, first_hash, 'serg-novikov',
    )
    await web_app_client.app['context'].config_schemas_cache.refresh_cache()
    assert (
        web_app_client.app['context'].config_schemas_cache.configs_by_name.get(
            'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        )
    )

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/schemas/actual_commit/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json={'commit': last_hash},
    )
    assert response.status == 200
    doc = await web_context.mongo.configs_meta.find_one(
        {'_id': storage.CONFIG_SCHEMAS_META_ID},
    )
    assert doc['hash'] == last_hash

    await run_cron.main(
        ['taxi_config_schemas.crontasks.send_alerts_for_update', '-t', '0'],
    )

    assert fake_send.calls == [
        {
            'args': (
                'collect_ticket',
                {
                    'New schema for config "(('
                    'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                    'dev/configs/edit/STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES '
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES))" '
                    'was applied in admin',
                },
            ),
            'kwargs': {},
        },
    ]
