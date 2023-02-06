# pylint: disable=protected-access
import os
import shutil
import tempfile

import pytest

from taxi_api_admin.generated.web import run_monrun

BASE_DIR_MOCK = '/tmp/log/yandex/taxi-api-admin/failed_audit_log_actions'
FAILED_AUDIT_ACTIONS_LIMIT_MOCK = 3


@pytest.fixture(name='start_check')
def _start_check(disable_schemes_checker):
    async def _wrapper():
        return await run_monrun.run(
            ['taxi_api_admin.monrun.checks.too_many_failed_audit_log_actions'],
        )

    return _wrapper


@pytest.fixture(scope='function')
def created_empty_base_dir():
    with tempfile.TemporaryDirectory(prefix=BASE_DIR_MOCK) as tmp_dir:
        yield tmp_dir


@pytest.fixture
# pylint: disable=redefined-outer-name
def patched_base_dir(created_empty_base_dir, monkeypatch):
    monkeypatch.setattr(
        'taxi_api_admin.utils.BASE_DIR', created_empty_base_dir,
    )
    return created_empty_base_dir


@pytest.fixture(scope='function')
# pylint: disable=redefined-outer-name
def create_log_files(patched_base_dir, search_path):
    file_name = 'test_date_log_action.json'
    file_path = list(search_path(file_name))[0]

    def _create_log_files(count: int):
        for i in range(count):
            created_file_path = os.path.join(
                patched_base_dir, f'test_{i}_log_action.json',
            )
            shutil.copy(file_path, created_file_path)

    yield _create_log_files


async def test__dir_not_exists__check_ok(start_check, monkeypatch):
    if os.path.exists(BASE_DIR_MOCK):
        shutil.rmtree(BASE_DIR_MOCK)

    monkeypatch.setattr('taxi_api_admin.utils.BASE_DIR', BASE_DIR_MOCK)

    result = await start_check()
    assert result == '0; OK'


@pytest.mark.config(
    API_ADMIN_AUDIT_FAILED_ACTIONS_CHECK={
        'limit': FAILED_AUDIT_ACTIONS_LIMIT_MOCK,
    },
)
@pytest.mark.usefixtures('patched_base_dir')
async def test__dir_exists_with_zero_logs__check_ok(start_check):
    result = await start_check()
    assert result == '0; OK'


@pytest.mark.config(
    API_ADMIN_AUDIT_FAILED_ACTIONS_CHECK={
        'limit': FAILED_AUDIT_ACTIONS_LIMIT_MOCK,
    },
)
# pylint: disable=redefined-outer-name
async def test__dir_exists_with_logs_lt_limit__check_ok(
        start_check, create_log_files,
):
    create_log_files(count=2)
    result = await start_check()
    assert result == '0; OK'


@pytest.mark.config(
    API_ADMIN_AUDIT_FAILED_ACTIONS_CHECK={
        'limit': FAILED_AUDIT_ACTIONS_LIMIT_MOCK,
    },
)
# pylint: disable=redefined-outer-name
async def test__dir_exists_with_logs_eq_limit__check_warn(
        start_check, create_log_files,
):
    create_log_files(count=3)
    result = await start_check()
    assert result == '1; WARN: 3 failed audit log actions'


@pytest.mark.config(
    API_ADMIN_AUDIT_FAILED_ACTIONS_CHECK={
        'limit': FAILED_AUDIT_ACTIONS_LIMIT_MOCK,
    },
)
# pylint: disable=redefined-outer-name
async def test__dir_exists_with_logs_gt_limit__check_warn(
        start_check, create_log_files,
):
    create_log_files(count=4)
    result = await start_check()
    assert result == '1; WARN: 4 failed audit log actions'
