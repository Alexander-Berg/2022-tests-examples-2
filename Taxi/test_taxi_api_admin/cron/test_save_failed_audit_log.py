import os
import shutil

import pytest


from taxi.clients import audit

from taxi_api_admin.generated.cron import run_cron

BASE_DIR = '/tmp/log/yandex/taxi-api-admin/failed_audit_log_actions'


@pytest.fixture
def patched_base_dir(monkeypatch):
    monkeypatch.setattr('taxi_api_admin.utils.BASE_DIR', BASE_DIR)


@pytest.mark.parametrize('is_error', [False, True])
# pylint: disable=redefined-outer-name
async def test_save_log(
        api_admin_cron_app, patch, patched_base_dir, is_error, search_path,
):
    @patch('taxi.clients.audit.AuditClient.create_log')
    async def _audit_log(document, **kwargs):
        if is_error:
            raise audit.BaseError('test error', doc=document)
        return 'id'

    file_name = 'test_date_log_action.json'
    paths = list(search_path(file_name))
    os.makedirs(BASE_DIR, exist_ok=True)
    shutil.copy(paths[0], BASE_DIR)
    await run_cron.main(
        ['taxi_api_admin.cron.save_failed_audit_log', '-t', '0'],
    )
    if is_error:
        assert os.path.isfile(os.path.join(BASE_DIR, file_name))
    else:
        assert not os.path.isfile(os.path.join(BASE_DIR, file_name))
