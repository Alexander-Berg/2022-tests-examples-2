import dataclasses
import pathlib
from typing import Callable
from typing import Dict
from typing import List

import git
import pytest

import generate_clients
from taxi_buildagent import utils
from tests.utils import repository
from tests.utils.examples import backend_py3
from tests.utils.examples import schemas
from tests.utils.examples import uservices


def load_file_content(path: pathlib.Path) -> str:
    with open(path, 'r', encoding='utf-8') as inp:
        return inp.read()


def clients_uservices_getter(
        target_repo_path: pathlib.Path, services_dir: str,
) -> List[str]:
    service_yaml_path = (
        target_repo_path / services_dir / 'uservice-template' / 'service.yaml'
    )
    return utils.load_yaml(service_yaml_path).get('clients', [])


def clients_py3_getter(
        target_repo_path: pathlib.Path, services_dir: str,
) -> List[str]:
    service_yaml_path = (
        target_repo_path / services_dir / 'example-service' / 'service.yaml'
    )
    return utils.load_yaml(service_yaml_path)['clients']['services']


CLIENTS_GETTER_BY_REPOTYPE: Dict[
    str, Callable[[pathlib.Path, str], List[str]],
] = {
    '--uservices': clients_uservices_getter,
    '--backend-py3': clients_py3_getter,
}


@dataclasses.dataclass(frozen=True)
class ServiceSettings:
    service_name: str
    schemas_exist: bool
    target_repo_exists: bool


@dataclasses.dataclass(frozen=True)
class Params:
    services_settings: List[ServiceSettings]
    repo_init: Callable[[pathlib.Path], git.Repo]
    repo_type_cmd: str


def get_prepared_services(
        schemas_repo: git.Repo,
        target_repo: git.Repo,
        services_settings: List[ServiceSettings],
) -> List[str]:
    schemas_commits: List[repository.Commit] = []
    target_commits: List[repository.Commit] = []
    target_services: List[str] = []
    for settings in services_settings:
        schemas_prefix = f'schemas/services/{settings.service_name}'
        if settings.schemas_exist:
            schemas_commits.append(
                repository.Commit(
                    comment=f'for service: {settings.service_name}',
                    files=[
                        f'{schemas_prefix}/api/api.yaml',
                        f'{schemas_prefix}/client.yaml',
                    ],
                    files_content='{}',
                ),
            )
            target_services.append(settings.service_name)
        if settings.target_repo_exists:
            target_commits.append(
                repository.Commit(
                    comment=f'for service: {settings.service_name}',
                    files=[f'{schemas_prefix}/api.yaml'],
                    files_content='old',
                ),
            )
    repository.apply_commits(schemas_repo, schemas_commits)
    repository.apply_commits(target_repo, target_commits)
    return target_services


def check_files(
        target_repo_path: pathlib.Path,
        services_settings: List[ServiceSettings],
) -> None:
    for settings in services_settings:
        if not settings.schemas_exist:
            continue
        api_filepath = (
            target_repo_path
            / 'schemas'
            / 'services'
            / settings.service_name
            / 'api'
            / 'api.yaml'
        )
        assert load_file_content(api_filepath) == (
            'x-taxi-client-qos:\n'
            '  taxi-config: CLIENT_GENERATION_TESTS_CLIENT_QOS\n'
        )
        client_filepath = (
            target_repo_path
            / 'schemas'
            / 'services'
            / settings.service_name
            / 'client.yaml'
        )
        assert load_file_content(client_filepath) == (
            'host:\n'
            '  production: taxi.yandex.nonexistent\n'
            '  testing: taxi.yandex.nonexistent\n'
        )


SERVICES_SETTINGS: List[ServiceSettings] = [
    ServiceSettings(
        service_name='existing-no-repo',
        schemas_exist=True,
        target_repo_exists=False,
    ),
    ServiceSettings(
        service_name='no-schemas',
        schemas_exist=False,
        target_repo_exists=True,
    ),
    ServiceSettings(
        service_name='both-exists',
        schemas_exist=True,
        target_repo_exists=True,
    ),
]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                services_settings=SERVICES_SETTINGS,
                repo_init=uservices.init,
                repo_type_cmd='--uservices',
            ),
            id='generate uservices',
        ),
        pytest.param(
            Params(
                services_settings=SERVICES_SETTINGS,
                repo_init=backend_py3.init,
                repo_type_cmd='--backend-py3',
            ),
            id='generate backend-py3',
        ),
    ],
)
async def test_generate_clients(tmpdir, params: Params):
    schemas_dir = tmpdir.mkdir('schemas')
    target_dir = tmpdir.mkdir('repository')
    schemas_repo = schemas.init(schemas_dir)
    # ignored typing, issue in MyPy https://github.com/python/mypy/issues/6910
    target_repo: git.Repo = params.repo_init(target_dir)  # type:ignore
    services_to_generate = get_prepared_services(
        schemas_repo=schemas_repo,
        target_repo=target_repo,
        services_settings=params.services_settings,
    )
    repository.apply_commits(
        target_repo,
        [
            repository.Commit(
                comment=f'checking copying',
                files=[
                    (
                        'schemas/configs/declarations/parks/'
                        'PARKS_ENABLE_PHOTO_VALIDITY_CHECK.yaml'
                    ),
                ],
                files_content='old',
            ),
        ],
    )
    target_repo_path = pathlib.Path(target_repo.working_dir)
    services_yaml = target_repo_path / 'services.yaml'
    services_dir = (
        utils.load_yaml(services_yaml)
        .get('services', {})
        .get('directory', '.')
    )
    clients_before = CLIENTS_GETTER_BY_REPOTYPE[params.repo_type_cmd](
        target_repo_path, services_dir,
    )
    clients_before.extend(services_to_generate)
    command: List[str] = [
        '--patch-client-schemas',
        '--schema-source-repo',
        schemas_repo.working_dir,
        '--target-repo',
        target_repo.working_dir,
        params.repo_type_cmd,
        '--services',
        *[settings.service_name for settings in params.services_settings],
    ]

    generate_clients.main(command)

    clients_after = CLIENTS_GETTER_BY_REPOTYPE[params.repo_type_cmd](
        target_repo_path, services_dir,
    )
    assert clients_after == clients_before
    check_files(
        target_repo_path=target_repo_path,
        services_settings=params.services_settings,
    )
    decl_path = target_repo_path / 'schemas' / 'configs' / 'declarations'
    assert load_file_content(decl_path / 'adjust' / 'ADJUST_CONFIG.yaml')
    ignored_file_content = load_file_content(
        decl_path / 'parks' / 'PARKS_ENABLE_PHOTO_VALIDITY_CHECK.yaml',
    )
    assert ignored_file_content == 'old'
