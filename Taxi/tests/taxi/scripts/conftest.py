import os

import pytest

from taxi.clients import scripts
from taxi.scripts import cron_run


@pytest.fixture(autouse=True)
def _scripts_env(simple_secdist, monkeypatch):
    settings_override = simple_secdist['settings_override']
    settings_override['ADMIN_SCRIPT_LOGS_MDS_S3'] = {}

    async def fake_get_next(*args, **kwargs):
        return {}

    async def fake_get_current_running_count(*args, **kwargs):
        return {'num_running': 0, 'max_num_running': 10}

    monkeypatch.setitem(os.environ, 'PYTHONPATH', 'FAKE_PYTHON_PATH')

    monkeypatch.setattr(
        cron_run.SetupContext, '_check_at_start', lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        scripts.ScriptsClient,
        'get_current_running_count',
        fake_get_current_running_count,
    )
    monkeypatch.setattr(
        scripts.ScriptsClient, 'get_next_script', fake_get_next,
    )


@pytest.fixture
def dump_scripts_client():
    class Client:
        async def get_next_command(self, script):
            return {'sleep_for': 15}

    return Client()
