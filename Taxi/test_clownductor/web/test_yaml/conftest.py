import dataclasses
import itertools
from typing import Any
from typing import Dict
from typing import Optional

import pytest

import arc_api.components as arc_api

from clownductor.internal.service_yaml import manager as yaml_manager
from clownductor.internal.service_yaml import models as yaml_models

GITHUB_ORG_URL = 'https://github.yandex-team.ru/taxi'
ARCADIA_URL = 'https://a.yandex-team.ru'


@pytest.fixture(name='github_url')
def _github_url():
    def _wrapper(repo_name, branch='develop'):
        return f'{GITHUB_ORG_URL}/{repo_name}/blob/{branch}/'

    return _wrapper


@pytest.fixture(name='arcadia_url')
def _arcadia_url():
    def _wrapper(repo: str = 'backend-py3', service: str = 'clownductor'):
        return (
            f'{ARCADIA_URL}/arc/trunk/arcadia/taxi/'
            f'{repo}/services/{service}/service.yaml'
        )

    return _wrapper


@pytest.fixture(name='backend_py3_develop')
def _backend_py3_develop(github_url):
    return github_url('backend-py3')


@pytest.fixture(name='uservices_develop')
def _uservices_develop(github_url):
    return github_url('uservices')


@pytest.fixture(name='frontend_develop')
def _frontend_develop(github_url):
    return github_url('frontend')


@pytest.fixture(name='service_yaml_path')
def _service_yaml_path():
    def _wrapper(service_name):
        return f'services/{service_name}/service.yaml'

    return _wrapper


@pytest.fixture(name='backend_py3_yaml_url')
def _backend_py3_yaml_url(backend_py3_develop, service_yaml_path):
    def _wrapper(service_name):
        return f'{backend_py3_develop}{service_yaml_path(service_name)}'

    return _wrapper


@pytest.fixture(name='uservices_yaml_url')
def _uservices_yaml_url(uservices_develop, service_yaml_path):
    def _wrapper(service_name):
        return f'{uservices_develop}{service_yaml_path(service_name)}'

    return _wrapper


@pytest.fixture(name='frontend_yaml_url')
def _frontend_yaml_url(frontend_develop, service_yaml_path):
    def _wrapper(service_name):
        return f'{frontend_develop}{service_yaml_path(service_name)}'

    return _wrapper


@pytest.fixture(name='repo_yaml_url')
def _repo_yaml_url(github_url, service_yaml_path):
    def _wrapper(repo_name, service_name, branch='develop'):
        return (
            f'{github_url(repo_name, branch)}{service_yaml_path(service_name)}'
        )

    return _wrapper


@pytest.fixture(name='expected_units')
def _expected_units():
    def _wrapper(expected_yaml_repr):
        units = []
        for alias in itertools.chain(
                [expected_yaml_repr.clownductor_info.service],
                expected_yaml_repr.clownductor_info.aliases,
        ):
            tvm_name = expected_yaml_repr.tvm_name
            hostnames = None
            debian_unit = None
            deb_units = expected_yaml_repr.debian_units or []
            for deb_unit in deb_units:
                if deb_unit.name in alias.units:
                    tvm_name = deb_unit.tvm_name or tvm_name
                    hostnames = deb_unit.hostnames
                    debian_unit = deb_unit
                    break

            units.append(
                yaml_models.ClownAlias(
                    service_type=expected_yaml_repr.service_type,
                    service_yaml_url=expected_yaml_repr.service_yaml_url,
                    service_name=alias.name,
                    wiki_path=expected_yaml_repr.wiki_path,
                    maintainers=expected_yaml_repr.maintainers,
                    service_info=alias,
                    tvm_name=tvm_name,
                    hostnames=hostnames,
                    debian_unit=debian_unit,
                ),
            )
        return units

    return _wrapper


@pytest.fixture(name='test_parse_yaml')
def _test_parse_yaml(
        web_context,
        patch_github_single_file,
        service_yaml_path,
        expected_units,
):
    async def _wrapper(service_name, service_yaml_name, expected_yaml_repr):
        _get_file = patch_github_single_file(
            service_yaml_path(service_name), service_yaml_name,
        )

        representation = await yaml_manager.get_service_yaml_representation(
            web_context, expected_yaml_repr.service_yaml_url,
        )
        assert dataclasses.asdict(representation) == dataclasses.asdict(
            expected_yaml_repr,
        )

        deploy_units = await yaml_manager.get_clown_aliases(
            web_context, expected_yaml_repr.service_yaml_url,
        )
        assert [
            dataclasses.asdict(item)
            for item in expected_units(expected_yaml_repr)
        ] == [dataclasses.asdict(item) for item in deploy_units]
        assert len(_get_file.calls) == 2

    return _wrapper


@pytest.fixture(name='request_service_from_yaml')
def _request_service_from_yaml(
        patch,
        load,
        login_mockserver,
        task_processor,
        load_yaml,
        web_app_client,
):
    async def _request(
            service_yaml_link: str,
            service_yaml: str,
            database: Optional[dict] = None,
    ):
        @patch('arc_api.components.ArcClient.read_file')
        async def _read_file(*args, **kwargs):
            try:
                yaml_data = load(f'{service_yaml}.yaml')
            except FileNotFoundError:
                raise arc_api.ArcClientBaseError()
            return arc_api.ReadFileResponse(header=None, content=yaml_data)

        login_mockserver()
        task_processor.load_recipe(
            load_yaml('recipes/WaitingToCreateServices.yaml')['data'],
        )
        request: Dict[str, Any]
        request = {'service_yaml_link': service_yaml_link}
        if database:
            request['database'] = database

        response = await web_app_client.post(
            '/v1/requests/service_from_yaml/validate/',
            json=request,
            headers={'X-Yandex-Login': 'deoevgen'},
        )
        return response

    return _request
