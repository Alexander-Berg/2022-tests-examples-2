# pylint: disable=unused-variable
import logging
from typing import Any
from typing import Optional

import pytest

from config_schemas_lib import storage

from taxi_config_schemas import config_models
from taxi_config_schemas import db_wrappers
from test_taxi_config_schemas.helpers import git_helper

logger = logging.getLogger(__name__)


async def _save_config_value(
        context,
        config: config_models.BaseConfig,
        value: Any,
        service_name: Optional[str] = None,
):
    config_for_update = config_models.ConfigWithValue.from_base_config(
        config, value,
    )
    if service_name:
        config_for_update.service_name = service_name
    collection, query = db_wrappers.select_collection_and_query(
        context, config_for_update,
    )
    await collection.update(
        query,
        {
            '$set': {storage.CONFIG_FIELDS.VALUE: value},
            '$currentDate': {storage.CONFIG_FIELDS.UPDATED: True},
        },
        upsert=True,
    )


@pytest.mark.usefixtures('patch_configs_by_group')
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            {
                'code': 'NEW_VALIDATOR_ERROR',
                'details': {
                    'config_by_service': [
                        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES->chatterbox',
                    ],
                    'prs': [
                        'https://github.yandex-team.ru/taxi/schemas/pull/1234',
                    ],
                },
                'message': (
                    'Can\'t change actual commit, validation does not '
                    'pass on values from db. '
                    'Details: errors occurred during validation of config '
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES: '
                    'Additional properties are '
                    'not allowed (\'other_options\' was unexpected)\n'
                    '\n'
                    'Failed validating \'additionalProperties\' in schema:\n'
                    '    {\'additionalProperties\': False,\n'
                    '     \'properties\': {\'name\': '
                    '{\'type\': \'string\'}},\n'
                    '     \'type\': \'object\'}\n'
                    '\n'
                    'On instance:\n'
                    '    {\'name\': \'hello\', \'other_options\': []}. '
                    'See pull requests: '
                    'https://github.yandex-team.ru/taxi/schemas/pull/1234. '
                    'See service values for configs: '
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES->chatterbox'
                ),
                'status': 'error',
            },
            id='github_pr_link',
        ),
        pytest.param(
            {
                'code': 'NEW_VALIDATOR_ERROR',
                'details': {
                    'config_by_service': [
                        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES->chatterbox',
                    ],
                    'prs': ['https://a.yandex-team.ru/review/1810664/'],
                },
                'message': (
                    'Can\'t change actual commit, '
                    'validation does not pass on values from db. '
                    'Details: errors occurred during validation of config '
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES: '
                    'Additional properties are '
                    'not allowed (\'other_options\' was unexpected)\n'
                    '\n'
                    'Failed validating \'additionalProperties\' in schema:\n'
                    '    {\'additionalProperties\': False,\n'
                    '     \'properties\': {\'name\': '
                    '{\'type\': \'string\'}},\n'
                    '     \'type\': \'object\'}\n'
                    '\n'
                    'On instance:\n'
                    '    {\'name\': \'hello\', \'other_options\': []}. '
                    'See pull requests: '
                    'https://a.yandex-team.ru/review/1810664/. '
                    'See service values for configs: '
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES->chatterbox'
                ),
                'status': 'error',
            },
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={'allow_arcadia': 'enabled'},
            ),
            id='arcadia_pr_link',
        ),
    ],
)
async def test_native_set_actual_commit_hash(
        expected_response,
        git_setup,
        web_context,
        patcher_tvm_ticket_check,
        web_app_client,
):
    local, remote = git_setup
    config_before = config_models.BaseConfig(
        name='STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        description='',
        full_description='',
        wiki='',
        group='chatterbox',
        default={},
        tags=['by-service'],
        validator_declarations=None,
        schema={
            'type': 'object',
            'additionalProperties': True,
            'properties': {'name': {'type': 'string'}},
        },
        maintainers=[],
        turn_off_immediately=False,
    )
    config_after = config_models.BaseConfig(
        name='STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        description='',
        full_description='',
        wiki='',
        group='chatterbox',
        default={},
        tags=['by-service'],
        validator_declarations=None,
        schema={
            'type': 'object',
            'additionalProperties': False,
            'properties': {'name': {'type': 'string'}},
        },
        maintainers=[],
        turn_off_immediately=False,
    )

    first_hash, last_hash = await git_helper.create_git_repos(
        repo_root=local,
        remote_repo=remote,
        skip_commits=1,
        args=[
            git_helper.GitArg(
                config=config_before,
                commit_message=(
                    'Aleksandr Piskarev',
                    (
                        'feat conf: fix startreck extra ticket\n\n'
                        'Relates: TAXI-123\n\n'
                        'REVIEW: 1810663'
                    ),
                ),
            ),
            git_helper.GitArg(
                config=config_after,
                commit_message=(
                    'Natalia Dunaeva',
                    (
                        'feat configs: add Startreck Extra Ticket (#1234)\n\n'
                        'Relates: TAXI-124\n\n'
                        'REVIEW: 1810664'
                    ),
                ),
            ),
        ],
    )
    await _save_config_value(
        web_context, config_before, value={'name': 'hello'},
    )
    await _save_config_value(
        web_context,
        config_before,
        value={'name': 'hello', 'other_options': []},
        service_name='chatterbox',
    )
    await db_wrappers.set_actual_commit_hash(
        web_context.mongo, first_hash, first_hash, 'serg-novikov',
    )
    web_app_client.app['context'].config_schemas_cache.configs_by_name = {
        config_before.name: config_before,
    }

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/schemas/actual_commit/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json={'commit': last_hash},
    )
    assert response.status == 422
    body = await response.json()
    assert body == expected_response
