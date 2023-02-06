# pylint: disable=protected-access
import datetime

import pytest

from archiving import admin_sync
from archiving import settings
from archiving.config import consts as config_consts
from archiving.config import utils as config_utils

_RULE_NAME = 'test_rule'
_LINK = 'test_link'

_EXCEPTION = admin_sync.EXCEPTION
_IN_PROGRESS = admin_sync.IN_PROGRESS
_FINISHED = admin_sync.FINISHED


@pytest.mark.parametrize(
    'num_removed, statuses, expected_is_reported',
    [
        (
            [2, 1500, 12000, 24000, 24001, 24002],
            [
                _IN_PROGRESS,
                _IN_PROGRESS,
                _IN_PROGRESS,
                _IN_PROGRESS,
                _IN_PROGRESS,
                _FINISHED,
            ],
            [True, False, True, True, False, True],
        ),
        ([2, 30], [_IN_PROGRESS, _EXCEPTION], [True, True]),
        ([3000], [_FINISHED], [True]),
        ([0], [_EXCEPTION], [True]),
    ],
)
@pytest.mark.config(
    ARCHIVING_SERVICE_SETTINGS={config_consts.SYNC_RATE_CONFIG_KEY: 10000},
)
async def test_sync_reporter(
        cron_context,
        num_removed,
        statuses,
        expected_is_reported,
        requests_handlers,
):
    sync_reporter = admin_sync.SyncReporter(
        archiving_admin_client=cron_context.clients.archiving_admin,
        rule_name=_RULE_NAME,
        task_id=_LINK,
        start_time=datetime.datetime(2019, 1, 1),
        sync_rate_bulk_size=config_utils.get_setting_service_config(
            cron_context.config,
            config_consts.SYNC_RATE_CONFIG_KEY,
            settings.DEFAULT_STATS_MULTIPLIER,
        ),
        shard_alias=None,
    )
    for idx, removed in enumerate(num_removed):
        is_reported = await sync_reporter._report_archiving_status(
            status=statuses[idx], total_removed_documents=removed,
        )
        assert is_reported == expected_is_reported[idx], f'index: {idx}'
