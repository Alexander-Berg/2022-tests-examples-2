# pylint: disable=redefined-outer-name
from concurrent import futures
import datetime
import pathlib

import pytest

from replication.plugins.secrets import monitoring
from replication.plugins.secrets import secrets_confirm

_MODULE = 'replication.plugins.secrets.monitoring'

NOW_OK = datetime.datetime(2022, 1, 10, 2, 30)
NOW_WARN = datetime.datetime(2022, 1, 10, 2, 35)
NOW_CRIT = datetime.datetime(2022, 1, 10, 2, 45)


REPLICATION_SECRETS_MARK = pytest.mark.config(
    REPLICATION_SECRETS={'secrets_refresh_period_seconds': 180},
)


@pytest.mark.nofilldb
@REPLICATION_SECRETS_MARK
@pytest.mark.parametrize(
    'expected_status, expected_description',
    [
        pytest.param(
            'OK',
            'OK; secrets age is 300 sec',
            marks=pytest.mark.now(NOW_OK.isoformat()),
        ),
        pytest.param(
            'WARN',
            (
                'Last update of secrets was too long ago 10 min > 9 min\n'
                'Logs: https://kibana'
            ),
            marks=pytest.mark.now(NOW_WARN.isoformat()),
        ),
        pytest.param(
            'CRIT',
            (
                'Last update of secrets was too long ago 20 min > 18 min\n'
                'Logs: https://kibana'
            ),
            marks=pytest.mark.now(NOW_CRIT.isoformat()),
        ),
    ],
)
async def test_do_check(
        replication_ctx, expected_status, expected_description, secrets_dir,
):
    executor = futures.ThreadPoolExecutor(max_workers=1)
    secrets = secrets_confirm.SecretsConfirm(
        secrets_dir=secrets_dir, executor=executor,
    )
    status, description = await monitoring.run_check(
        replication_ctx.shared_deps.config_service, secrets,
    )
    assert description == expected_description
    assert status == expected_status


@REPLICATION_SECRETS_MARK
@pytest.mark.nofilldb
async def test_do_check_not_found(replication_ctx, static_dir: pathlib.Path):
    executor = futures.ThreadPoolExecutor(max_workers=1)
    secrets = secrets_confirm.SecretsConfirm(
        secrets_dir=static_dir.joinpath('not_found'), executor=executor,
    )
    status, description = await monitoring.run_check(
        replication_ctx.shared_deps.config_service, secrets,
    )
    assert description.startswith('Secrets path not found')
    assert status == 'CRIT'
