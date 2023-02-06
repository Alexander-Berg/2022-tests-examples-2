import os

import pytest

from dmp_suite.exceptions import DWHError
from dmp_suite.py_env import service_setup

current_test_dir = os.path.dirname(__file__)
new_source_root = os.path.join(current_test_dir, 'data')


def get_test_service(name):
    root = (name == 'root')
    if root:
        home_dir = new_source_root
    else:
        home_dir =os.path.abspath(
            os.path.join(new_source_root, name))
    return service_setup.Service(
            name=name,
            distribution_name='yandex-taxi-dmp-' + name,
            home_dir=home_dir,
            root=root
        )


class TestResolveService:

    @pytest.mark.parametrize('workdir, expected_name', [
        (os.path.join(new_source_root, 'a'), 'a'),
        (os.path.join(new_source_root, 'a', 'a'), 'a'),
        (os.path.join(new_source_root, 'a', 'aa'), 'a'),
        (os.path.join(new_source_root, 'a', 'aa'), 'a'),
        (os.path.join(new_source_root, 'b'), 'b'),
        (new_source_root, 'root'),
        (current_test_dir, 'root'),
    ])
    def test_by_workdir(self, monkeypatch, workdir, expected_name):
        monkeypatch.setattr(
            service_setup.sources_root, 'SOURCES_ROOT', new_source_root)
        monkeypatch.delenv(service_setup.SERVICE_NAME_ENV, raising=False)
        monkeypatch.chdir(workdir)

        assert service_setup.resolve_service() == get_test_service(expected_name)


    @pytest.mark.parametrize('workdir, env_val, expected_name', [
        (new_source_root, 'a', 'a'),
        (os.path.join(new_source_root, 'a'), 'a', 'a'),
        (os.path.join(new_source_root, 'a', 'a'), 'a', 'a'),
        (os.path.join(new_source_root, 'b'), 'a', 'a'),
    ])
    def test_env_variable(self, monkeypatch, workdir, env_val, expected_name):
        monkeypatch.chdir(workdir)
        monkeypatch.setattr(
            service_setup.sources_root, 'SOURCES_ROOT', new_source_root)
        monkeypatch.setenv(service_setup.SERVICE_NAME_ENV, env_val)
        monkeypatch.syspath_prepend(os.path.join(new_source_root, expected_name))

        assert service_setup.resolve_service() == get_test_service(expected_name)

    @pytest.mark.parametrize('workdir, env_val, expected_name', [
        (new_source_root, 'b', 'b'),
        (new_source_root, 'non_exist', 'non_exist'),
        (new_source_root, 'no_setup', 'no_setup'),
    ])
    def test_invalid_env_variable(self, monkeypatch, workdir, env_val, expected_name):
        if os.path.exists(workdir):
            monkeypatch.chdir(workdir)
        else:
            monkeypatch.chdir(new_source_root)
        monkeypatch.setattr(
            service_setup.sources_root, 'SOURCES_ROOT', new_source_root)
        monkeypatch.setenv(service_setup.SERVICE_NAME_ENV, env_val)
        monkeypatch.syspath_prepend(
            os.path.join(new_source_root, expected_name))

        with pytest.raises(DWHError):
            service_setup.resolve_service()

@pytest.mark.parametrize('workdir, env_val, expected_name', [
    (os.path.join(new_source_root, 'a'), None, 'a'),
    (os.path.join(new_source_root, 'a', 'aa', 'foo'), None, 'a'),
    (os.path.join(new_source_root, 'a'), 'b', 'a'),
    (os.path.join(new_source_root, 'b'), None, 'b'),
    (os.path.join(new_source_root, 'no_setup'), None, 'root'),
])
def test_resolve_service_by_path(monkeypatch, workdir, env_val, expected_name):
    if os.path.isdir(workdir):
        monkeypatch.chdir(workdir)
    else:
        monkeypatch.chdir(new_source_root)
    monkeypatch.setattr(
        service_setup.sources_root, 'SOURCES_ROOT', new_source_root)
    monkeypatch.setenv(service_setup.SERVICE_NAME_ENV, env_val)
    monkeypatch.syspath_prepend(
        os.path.join(new_source_root, expected_name))

    assert service_setup.resolve_service_by_path(workdir) == get_test_service(expected_name)


@pytest.mark.parametrize('workdir, exception', [
    (os.path.join(new_source_root, 'non_exist'), ValueError),
    (current_test_dir, DWHError),
])
def test_invalid_resolve_service_by_path(monkeypatch, workdir, exception):
    if os.path.isdir(workdir):
        monkeypatch.chdir(workdir)
    else:
        monkeypatch.chdir(new_source_root)
    monkeypatch.setattr(
        service_setup.sources_root, 'SOURCES_ROOT', new_source_root)

    with pytest.raises(exception):
        service_setup.resolve_service_by_path(workdir)
