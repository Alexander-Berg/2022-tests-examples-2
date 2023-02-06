# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
# pylint: disable=ungrouped-imports
# import of pytest_plugins must be first
import taxi_config_schemas.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

import contextlib  # noqa: I100
import os
import tempfile

import pytest

from taxi_config_schemas import config_models
from taxi_config_schemas import settings

pytest_plugins = ['taxi_config_schemas.generated.service.pytest_plugins']

CONFIGS = [
    {
        'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        'description': '',
        'group': 'billing',
        'default': 100000000,
        'tags': ['fallback'],
        'validators': ['$integer', {'$gt': 0}],
        'full-description': 'Full description',
        'maintainers': ['dvasiliev89', 'serg-novikov'],
        'wiki': 'https://wiki.yandex-team.ru',
        'turn-off-immediately': True,
    },
    {
        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'description': '',
        'group': 'chatterbox',
        'default': ['YANDEXTAXI'],
        'tags': [],
        'validators': [{'$sequence_of': ['$string']}],
    },
    {
        'name': 'DEVICENOTIFY_USER_TTL',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': [],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'SOME_CONFIG_WITH_DEFINITIONS',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'default': {'value': 90},
        'tags': [],
        'schema': {'additionalProperties': {'$ref': 'some_file.yaml#/int'}},
    },
]


@pytest.fixture
def build_configs_by_group():
    def _build_configs_by_group(configs):
        result = {}
        for config in configs:
            result.setdefault(config['group'], []).append(
                config_models.BaseConfig(
                    name=config.get('name'),
                    description=config.get('description'),
                    full_description=config.get('full-description'),
                    wiki=config.get('wiki'),
                    group=config.get('group'),
                    default=config.get('default'),
                    tags=config.get('tags'),
                    validator_declarations=config.get('validators'),
                    schema=config.get('schema'),
                    maintainers=config.get('maintainers'),
                    turn_off_immediately=config.get('turn-off-immediately'),
                    end_of_life=config.get('end-of-life'),
                ),
            )
        return result

    return _build_configs_by_group


@pytest.fixture
def patcher_tvm_ticket_check(patch):
    def _patcher(src_service_name):
        return _patch_tvm_ticket_check(patch, src_service_name)

    return _patcher


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'expected_service_name')


@pytest.fixture(autouse=True)
def patch_configs_by_group(request, patch, build_configs_by_group):
    configs = CONFIGS
    disable = False
    for marker in request.node.iter_markers('custom_patch_configs_by_group'):
        if 'configs' in marker.kwargs:
            configs = marker.kwargs['configs']
        elif 'disable' in marker.kwargs:
            disable = True
        break

    if disable:
        return

    @patch(
        'taxi_config_schemas.repo_manager.RepoSession.'
        '_collect_configs_by_group',
    )
    def _collect_configs_by_group(*args, **kwargs):
        return build_configs_by_group(configs)


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def git_setup(monkeypatch, patch):
    @patch('taxi_config_schemas.repo_manager.util.GitHelper.clone')
    async def _clone(*args, **kwargs):
        pass

    with tempfile.TemporaryDirectory() as working_area:
        local_path = os.path.join(working_area, 'local_git')
        remote_path = os.path.join(working_area, 'remote_git')
        os.makedirs(local_path)
        os.makedirs(remote_path)
        monkeypatch.setattr(
            'taxi_config_schemas.settings.SCHEMAS_LOCAL_PATH', local_path,
        )
        monkeypatch.setattr(
            'taxi_config_schemas.settings.BRANCHES_TO_FETCH',
            (settings.DEVELOP,),
        )
        yield local_path, remote_path


@pytest.fixture(autouse=True)
def patch_collect_from_archive(patch, tmpdir, request):
    disable = False
    for marker in request.node.iter_markers('patch_collect_from_archive'):
        if 'disable' in marker.kwargs:
            disable = True
        break

    if disable:
        return

    @patch(
        'taxi_config_schemas.repo_manager.util.GitHelper.collect_from_archive',
    )
    @contextlib.asynccontextmanager
    async def _collect_from_archive(*args, **kwargs):
        yield tmpdir


@pytest.fixture
async def patch_call_command(patch):
    @patch('taxi_config_schemas.repo_manager.util.GitHelper._call_command')
    async def _call_command(*args, **kwargs):
        return b'', b''


@pytest.fixture
async def update_schemas_cache(web_app_client):
    await web_app_client.app['context'].config_schemas_cache.refresh_cache()


@pytest.fixture
def patch_collect_definitions(patch):
    @patch('taxi_config_schemas.repo_manager.RepoSession.collect_definitions')
    def _collect_common_definitions(*args, **kwargs):
        return {'some_file.yaml': {'int': {'type': 'number'}}}


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'custom_patch_configs_by_group: custom_patch_configs_by_group',
    )
    config.addinivalue_line(
        'markers', 'patch_collect_from_archive: patch_collect_from_archive',
    )
