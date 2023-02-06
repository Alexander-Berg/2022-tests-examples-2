# pylint: disable=unused-variable
import pytest

from taxi_config_schemas import config_models
from taxi_config_schemas import db_wrappers
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
    {
        'name': 'CONFIG_WITH_COMMON',
        'description': '',
        'group': 'chatterbox',
        'default': {},
        'full_description': '',
        'tags': [],
        'maintainers': [],
        'schema': {'$ref': '/common/client.yaml#/settings'},
        'wiki': '',
        'turn_off_immediately': False,
    },
]


@pytest.mark.config(
    CONFIG_SCHEMAS_RUNTIME_FEATURES={'definitions_diff': 'enabled'},
)
@pytest.mark.custom_patch_configs_by_group(disable=True)
@pytest.mark.patch_collect_from_archive(disable=True)
async def test_native_get_schemas_diff(
        git_setup,
        web_context,
        patcher_tvm_ticket_check,
        web_app_client,
        patch,
):
    local, remote = git_setup
    first_hash, last_hash = await git_helper.create_git_repos(
        repo_root=local,
        remote_repo=remote,
        skip_commits=4,
        args=[
            git_helper.GitArg(
                common_definition=git_helper.CommonDefinition(
                    name='client',
                    directory='common/test',
                    schema={
                        'settings': {
                            'type': 'object',
                            'additionalProperties': False,
                        },
                    },
                ),
                commit_message=(
                    'Aleksandr Piskarev',
                    (
                        'feat conf: add common definition\n\n'
                        'Relates: TAXI-123'
                    ),
                ),
            ),
            git_helper.GitArg(
                common_definition=git_helper.CommonDefinition(
                    name='qos_client',
                    directory='test',
                    schema={
                        'settings': {
                            'type': 'object',
                            'additionalProperties': False,
                        },
                    },
                ),
                commit_message=(
                    'Serg Novikov',
                    (
                        'feat conf: add qos  common definition\n\n'
                        'Relates: TAXI-12345'
                    ),
                ),
            ),
            git_helper.GitArg(
                config=config_models.BaseConfig(
                    name='CONFIG_WITH_COMMON',
                    description='',
                    full_description='',
                    wiki='',
                    group='chatterbox',
                    default={},
                    tags=[],
                    validator_declarations=None,
                    schema={
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'property1': {
                                '$ref': '/common/test/client.yaml#/settings',
                            },
                            'property2': {
                                '$ref': '/test/qos_client.yaml#/settings',
                            },
                        },
                    },
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
            git_helper.GitArg(
                common_definition=git_helper.CommonDefinition(
                    name='client',
                    directory='common/test',
                    schema={
                        'settings': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {},
                        },
                    },
                ),
                commit_message=(
                    'Aleksandr Piskarev',
                    (
                        'feat conf: add common definition (#34)\n\n'
                        'Relates: TAXI-123'
                    ),
                ),
            ),
            git_helper.GitArg(
                common_definition=git_helper.CommonDefinition(
                    name='qos_client',
                    directory='test',
                    schema={
                        'settings': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {'property': {'type': 'string'}},
                        },
                    },
                ),
                commit_message=(
                    'Aleksandr Cherniy',
                    (
                        'feat conf: update qos definition (#341)\n\n'
                        'Relates: TAXI-8123'
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
    assert web_app_client.app[
        'context'
    ].config_schemas_cache.configs_by_name.get('CONFIG_WITH_COMMON')

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/schemas/diff/',
        headers={'X-Ya-Service-Ticket': 'good'},
        params={'commit': last_hash},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['commit'] == last_hash
    assert body['groups'] == [
        {
            'name': 'chatterbox',
            'changes': [
                {
                    'before': {
                        'default': {},
                        'description': '',
                        'group': 'chatterbox',
                        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                        'tags': [],
                        'maintainers': [],
                        'wiki': '',
                        'schema': {'additionalProperties': False},
                    },
                    'after': {
                        'default': {},
                        'description': '',
                        'group': 'chatterbox',
                        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                        'tags': [],
                        'maintainers': [],
                        'wiki': '',
                        'schema': {'additionalProperties': True},
                    },
                    'authors': [
                        {
                            'author': 'Natalia Dunaeva',
                            'message': (
                                'feat configs: '
                                'add Startreck Extra Ticket (#1234)'
                            ),
                        },
                    ],
                },
            ],
        },
        {
            'name': 'common_definition:/common/test/client.yaml',
            'changes': [
                {
                    'before': {
                        'schema': {
                            'settings': {
                                'additionalProperties': False,
                                'type': 'object',
                            },
                        },
                    },
                    'after': {
                        'schema': {
                            'settings': {
                                'additionalProperties': False,
                                'properties': {},
                                'type': 'object',
                            },
                        },
                    },
                    'authors': [
                        {
                            'author': 'Aleksandr Piskarev',
                            'message': (
                                'feat conf: add common definition (#34)'
                            ),
                        },
                    ],
                    'affected': ['CONFIG_WITH_COMMON'],
                },
            ],
        },
        {
            'name': 'common_definition:/test/qos_client.yaml',
            'changes': [
                {
                    'before': {
                        'schema': {
                            'settings': {
                                'additionalProperties': False,
                                'type': 'object',
                            },
                        },
                    },
                    'after': {
                        'schema': {
                            'settings': {
                                'additionalProperties': False,
                                'properties': {'property': {'type': 'string'}},
                                'type': 'object',
                            },
                        },
                    },
                    'authors': [
                        {
                            'author': 'Aleksandr Cherniy',
                            'message': (
                                'feat conf: update qos definition (#341)'
                            ),
                        },
                    ],
                    'affected': ['CONFIG_WITH_COMMON'],
                },
            ],
        },
    ]
