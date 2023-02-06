import os
import pathlib
import sys
from typing import Set

import jsonschema
import pytest
import yatest.common  # pylint: disable=import-error

from taxi_testsuite.plugins.yamlcase import pytest_plugin as yamlcase
from testsuite.utils import compat
from testsuite.utils import yaml_util


@pytest.fixture
def _search_directories(
        request,
        static_dir,
        initial_data_path,
        service_source_dir,
        get_service_name,
):
    fullname = pathlib.Path(yatest.common.source_path(request.module.__file__))
    test_module_name = pathlib.Path(fullname.stem)
    node_name = request.node.name
    if '[' in node_name:
        node_name = node_name[: node_name.index('[')]
    local_path = [test_module_name / node_name, test_module_name, 'default']
    search_directories = [static_dir / subdir for subdir in local_path]
    service_static_default_dir = (
        service_source_dir
        / 'testsuite'
        / f'tests_{get_service_name}'.replace('-', '_')
        / 'static'
        / 'default'
    )
    search_directories.append(service_static_default_dir)
    search_directories.extend(initial_data_path)
    return tuple(search_directories)


@pytest.fixture(scope='session')
def experiments3_schemas_path():
    return yatest.common.source_path(
        'taxi/uservices/submodules/testsuite/'
        'taxi_testsuite/plugins/experiments3/schemas',
    )


@pytest.fixture(scope='session')
def wait_service_started(service_client_session_factory):
    def _print_stderr(message: str) -> None:
        print(message, file=sys.stderr)

    @compat.asynccontextmanager
    async def waiter(*, args, health_check):
        process = None
        async with service_client_session_factory() as session:
            if not await health_check(session=session, process=process):
                command = ' '.join(args)
                _print_stderr('--------------------------------------------')
                _print_stderr('')
                _print_stderr(
                    'Service is not running yet you may want to start it from '
                    'outside of testsuite, e.g. using gdb:',
                )
                _print_stderr('')
                _print_stderr(
                    '$(arc root)/ya tool gdb --args {}'.format(command),
                )
                _print_stderr('')
                _print_stderr('Waiting for service to start...')
                _print_stderr('--------------------------------------------')
                while not await health_check(session=session, process=process):
                    pass
                _print_stderr('')

        yield None

    return waiter


class YamlModule(yamlcase.YamlFile, pytest.Module):
    class FakeModule:
        def __init__(self, fspath: os.PathLike) -> None:
            self.__file__ = str(fspath)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._module = self.FakeModule(self.fspath)

    @property
    def obj(self):
        return self._module

    @classmethod
    def _get_schema_validator(cls):
        if not cls._yamlcase_validator:
            schema_path = yatest.common.source_path(
                'taxi/uservices/submodules/testsuite/'
                'taxi_testsuite/plugins/yamlcase/schemas/yamlcase.yaml',
            )

            schema = yaml_util.load_file(schema_path)
            cls._yamlcase_validator = jsonschema.Draft4Validator(schema)
        return cls._yamlcase_validator


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    collect_func = session.collect

    def wrapper(*args, **kwargs):
        collected_dirs: Set[pathlib.Path] = set()
        for node in collect_func(*args, **kwargs):
            yield node
            collected_dirs.add(pathlib.Path(node.obj.__file__).parent)

        collected_paths: Set[pathlib.Path] = set()
        for test_dir in collected_dirs:
            if pathlib.Path('taxi/uservices') not in test_dir.parents:
                continue
            test_path = pathlib.Path(yatest.common.source_path(str(test_dir)))
            for path in test_path.rglob('test_*.yaml'):
                collected_paths.add(path)

        for path in collected_paths:
            yield YamlModule.from_parent(session, fspath=str(path))

    session.collect = wrapper
