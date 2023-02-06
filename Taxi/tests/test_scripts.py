import os
import sys
import typing

import pytest

from scripts import copy_service_data_helper


FAKE_REPO_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_scripts', 'repository',
)
REFS_PATH = os.path.join(FAKE_REPO_DIR, os.path.pardir, 'references')


class Params(typing.NamedTuple):
    service_name: str
    stdout: str
    is_dry_run: bool = False
    has_exit: bool = False
    run_twice: bool = False


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                service_name='common',
                stdout=(
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
            ),
            id='common',
        ),
        pytest.param(
            Params(
                service_name='common',
                stdout=(
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                    'removing: {dst_repo}/schemas/services/common\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
                run_twice=True,
            ),
            id='common twice',
        ),
        pytest.param(
            Params(
                service_name='another-common',
                stdout=(
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'copying: {src_repo}/libraries/common-library/docs/yaml/'
                    'definitions.yaml to {dst_repo}/schemas/services/{service}'
                    '/libraries/common-library\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
            ),
            id='another_common',
        ),
        pytest.param(
            Params(
                service_name='absent-service',
                stdout="""
No dir with path: {service_path}
""".lstrip(),
                has_exit=True,
            ),
            id='absent-service',
        ),
        pytest.param(
            Params(
                service_name='common',
                is_dry_run=True,
                stdout=(
                    'dry-run mode is enabled\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
            ),
            id='common dry_run',
        ),
        pytest.param(
            Params(
                service_name='another-common',
                is_dry_run=True,
                stdout=(
                    'dry-run mode is enabled\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'copying: {src_repo}/libraries/common-library/docs/yaml/'
                    'definitions.yaml to {dst_repo}/schemas/services/{service}'
                    '/libraries/common-library\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
            ),
            id='another_common dry_run',
        ),
        pytest.param(
            Params(
                service_name='common',
                stdout=(
                    'dry-run mode is enabled\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml '
                    'to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                    'dry-run mode is enabled\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'client.yaml to {dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/'
                    'definitions.yaml to '
                    '{dst_repo}/schemas/services/{service}\n'
                    'copying: {src_repo}/services/{service}/docs/yaml/api/'
                    'api.yaml to {dst_repo}/schemas/services/{service}/api\n'
                    'docs/yaml for service {service} and its dependencies '
                    'were copied to schemas\n'
                ),
                run_twice=True,
                is_dry_run=True,
            ),
            id='common twice dry_run',
        ),
    ],
)
def test_copy_service_data_helper(
        tmpdir, monkeypatch, compare_schemas, capsys, params: Params,
):
    monkeypatch.setattr(
        'scripts.copy_service_data_helper._get_service_path',
        _get_testing_service_path,
    )
    monkeypatch.setattr(
        'scripts.copy_service_data_helper._get_dependencies_paths',
        _get_testing_dependencies_paths,
    )
    service_name = params.service_name

    schemas_path = str(tmpdir)
    os.makedirs(os.path.join(tmpdir, 'schemas', 'services'))

    arg_list = [service_name, schemas_path]

    if params.is_dry_run:
        arg_list.append('--dry-run')

    if params.has_exit:
        with pytest.raises(SystemExit) as wrapped_exc:
            copy_service_data_helper.main(arg_list)
        assert wrapped_exc.type == SystemExit
        assert wrapped_exc.value.code == 1
    else:
        copy_service_data_helper.main(arg_list)
        if not params.is_dry_run:
            compare_schemas('schemas-%s-service' % service_name, service_name)
        else:
            dst_schemas_path = os.path.join(
                tmpdir, 'schemas', 'services', service_name,
            )
            assert not os.path.exists(dst_schemas_path)

    if params.run_twice:
        copy_service_data_helper.main(arg_list)

    service_path = _get_testing_service_path(params.service_name)
    reference_stdout = params.stdout.format(
        src_repo=copy_service_data_helper.get_relpath(FAKE_REPO_DIR),
        dst_repo=copy_service_data_helper.get_relpath(tmpdir),
        service_path=copy_service_data_helper.get_relpath(service_path),
        service=service_name,
    )

    stdout, _ = capsys.readouterr()
    assert reference_stdout == stdout


@pytest.mark.parametrize('service_name', ['userver-sample', 'test-service'])
def test_schemas_up_to_date(
        tmpdir,
        monkeypatch,
        compare_with_reference,
        uservices_path,
        service_name: str,
) -> None:
    monkeypatch.chdir(uservices_path)
    monkeypatch.setattr(sys, 'stdout', None)
    tmpdir_path = str(tmpdir)
    os.makedirs(os.path.join(tmpdir_path, 'schemas', 'services'))

    arg_list = [service_name, tmpdir_path]

    try:
        copy_service_data_helper.main(arg_list)
    except SystemExit:
        raise Exception('Unexpected error')

    generated_schemas_path = os.path.join(tmpdir_path, 'schemas', 'services')
    existing_schemas_path = os.path.join(
        uservices_path, '..', 'schemas', 'schemas', 'services',
    )
    result_forward = compare_with_reference(
        generated_schemas_path,
        service_name,
        os.path.join(existing_schemas_path, service_name),
    )
    result_backward = compare_with_reference(
        existing_schemas_path,
        service_name,
        os.path.join(generated_schemas_path, service_name),
    )

    is_up_to_date = result_forward.is_ok() and result_backward.is_ok()
    assert is_up_to_date, (
        f'Schemas for "{service_name}" in uservices are outdated.\n'
        f'Run "./scripts/copy_service_data.py {service_name} ../schemas"\n'
        f'More info here:\n'
        f'https://wiki.yandex-team.ru/taxi/backend'
        f'/userver/codegen/clients/#sxemyklientov'
    )


@pytest.fixture(name='compare_schemas')
def _compare_schemas(compare_with_reference, tmpdir):
    def common_compare(stub_name, service_name):
        tmpdir_path = str(tmpdir)
        if not os.path.exists(os.path.join(REFS_PATH, stub_name)):
            raise FileNotFoundError('Reference folder not found')

        path = os.path.join(tmpdir_path, 'schemas', 'services', service_name)
        result = compare_with_reference(REFS_PATH, stub_name, path)
        assert result.is_ok(), result.make_report()

    return common_compare


@pytest.fixture(name='uservices_path')
def _uservices_path():
    return copy_service_data_helper.USERVICES_DIR


def _get_testing_service_path(service):
    return os.path.join(FAKE_REPO_DIR, 'services', service)


def _get_testing_dependencies_paths(dep_name, dep_value, schemas_path):
    src = os.path.join(
        FAKE_REPO_DIR, dep_name, dep_value, 'docs', 'yaml', 'definitions.yaml',
    )
    if os.path.isfile(src):
        dst = os.path.join(schemas_path, dep_value)
        yield src, dst, copy_service_data_helper.COMMON_DEPENDENCY_RELPATH_INFO
