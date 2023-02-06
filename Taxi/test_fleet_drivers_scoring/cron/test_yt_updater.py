# pylint: disable=redefined-outer-name
import datetime
from unittest import mock

import pytest

from taxi.util import performance
from testsuite.utils import ordered_object

from fleet_drivers_scoring.generated.cron import cron_context as context_module
from fleet_drivers_scoring.generated.cron import run_cron
from fleet_drivers_scoring.utils.yt_updater import updater
import test_fleet_drivers_scoring.utils as global_utils

CONFIG_ENABLED = {
    'is_enabled': True,
    'tables': [
        {
            'is_enabled': True,
            'name': 'ratings',
            'schedules': ['02:00', '17:00'],
        },
    ],
}

SCORING_SOURCE_YT_TABLES_DEFAULT = {
    'dim_driver': '//home/taxi-dwh/dds/dim_driver',
    'dm_order': '//home/taxi-dwh/summary/dm_order',
    'driver_experience': '//home/taxi-dwh/dds/snp_acc_unique_driver',
    'quality_metrics': (
        '//home/taxi-analytics/kvdavydova/quality_rate/quality_metrics'
    ),
    'telemetry_daily_processed': (
        '//home/taxi_ml/production/telemetry/predictions/daily_processed'
    ),
}


async def _run_cron_task():
    await run_cron.main(
        ['fleet_drivers_scoring.crontasks.yt_updater', '-t', '0'],
    )


async def _update_states_count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.write_pool.fetchval(
        'SELECT COUNT(id) FROM fleet_drivers_scoring.yt_update_states;',
    )


async def _updates_count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.write_pool.fetchval(
        'SELECT COUNT(id) FROM fleet_drivers_scoring.yt_updates;',
    )


class TransferManagerMock:
    def get_task_info(self, task_id):
        return {'task_id': task_id, 'state': 'completed'}


def _set_yql_response(
        monkeypatch, status: str, operation_id: str, share_url: str,
) -> None:
    def get_results(*args, **kwargs):
        acc = mock.MagicMock()
        acc.status = status
        return acc

    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.operation_id',
        property(lambda _: operation_id),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.share_url',
        property(lambda _: share_url),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.run', lambda _: None,
    )

    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.run', lambda _: None,
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.get_results',
        get_results,
    )


def _patch_dates(patch, datetime_str):
    @patch('datetime.date.today')
    def _date_today():
        return datetime.datetime.fromisoformat(datetime_str)

    @patch('datetime.datetime.today')
    def _datetime_today():
        return datetime.datetime.fromisoformat(datetime_str)

    @patch('datetime.datetime.utcnow')
    def _utcnow():
        return datetime.datetime.fromisoformat(datetime_str)


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER={'is_enabled': False, 'tables': []},
)
async def test_config_disabled(cron_context: context_module.Context):
    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 0


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER={'is_enabled': True, 'tables': []},
)
async def test_config_empty_tables(cron_context: context_module.Context):
    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 0


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER={
        'is_enabled': True,
        'tables': [
            {'is_enabled': False, 'name': 'ratings', 'schedules': ['17:00']},
        ],
    },
)
async def test_config_scheduled_table_disabled(
        cron_context: context_module.Context,
):
    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 0


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_calc_already_exists.sql'],
)
@pytest.mark.config(FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED)
async def test_calc_table_already_exists(
        cron_context: context_module.Context, patch,
):
    datetime_str = '2020-05-08T17:10:00'
    _patch_dates(patch, datetime_str)

    @patch(
        'fleet_drivers_scoring.utils.yt_updater.calculator.'
        '_get_tables_performed_calc',
    )
    async def _tables_performed_calc(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.copier.run_copy')
    async def _run_copy(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.converter.run_convert')
    async def _run_convert(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_update(*args, **kwargs):
        return

    before_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_count = await _update_states_count(cron_context)
    assert before_count == after_count


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_calc_table(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:01:00'
    operation_status = 'RUNNING'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 1

    record = await cron_context.pg.write_pool.fetchrow(
        'SELECT * FROM fleet_drivers_scoring.yt_update_states;',
    )
    assert record['name'] == 'ratings'
    assert record['type'] == 'calc'
    assert record['status'] == 'pending'
    assert record['created_at']
    assert record['updated_at']
    assert record['revision']


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_calc_table_at_previous_period(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T16:01:00'
    operation_status = 'RUNNING'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 1

    record = await cron_context.pg.write_pool.fetchrow(
        'SELECT * FROM fleet_drivers_scoring.yt_update_states;',
    )
    assert record['name'] == 'ratings'
    assert record['type'] == 'calc'
    assert record['status'] == 'pending'
    assert record['created_at']
    assert record['updated_at']
    assert record['revision']


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_calc_table_failed(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:01:00'
    operation_status = 'ERROR'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 1

    record = await cron_context.pg.write_pool.fetchrow(
        'SELECT * FROM fleet_drivers_scoring.yt_update_states;',
    )
    assert record['name'] == 'ratings'
    assert record['type'] == 'calc'
    assert record['status'] == 'failed'
    assert record['created_at']
    assert record['updated_at']
    assert record['revision']


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_run_copy_table(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:03:00'
    operation_status = 'COMPLETED'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def _copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        return [
            f'task_id_{i}_{id(src_yt_client)}_{id(dst_yt_clients)}'
            for i, path in enumerate(paths)
        ]

    @patch('fleet_drivers_scoring.utils.yt_updater.converter.run_convert')
    async def _convert(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_convert(*args, **kwargs):
        return

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 4

    calc_record = await cron_context.pg.write_pool.fetchrow(
        """
        SELECT * FROM fleet_drivers_scoring.yt_update_states WHERE type='calc';
        """,
    )

    copy_record = await cron_context.pg.write_pool.fetchrow(
        """
        SELECT * FROM fleet_drivers_scoring.yt_update_states WHERE type='copy';
        """,
    )
    assert copy_record['parent_id'] == calc_record['id']
    assert copy_record['name'] == 'ratings'
    assert copy_record['type'] == 'copy'
    assert copy_record['status'] == 'done'
    assert copy_record['dst_path']
    assert copy_record['src_cluster'] == 'hahn'
    assert copy_record['dst_cluster'] in [
        'seneca-man',
        'seneca-sas',
        'seneca-vla',
    ]
    assert copy_record['created_at']
    assert copy_record['updated_at']
    assert copy_record['revision']


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_copy_already_exists.sql'],
)
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_copy_already_exists(
        cron_context: context_module.Context, patch,
):
    datetime_str = '2020-05-08T16:03:00'

    @patch('fleet_drivers_scoring.utils.yt_updater.converter.run_convert')
    async def _run_convert(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_update(*args, **kwargs):
        return

    _patch_dates(patch, datetime_str)

    before_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_count = await _update_states_count(cron_context)
    assert before_count == after_count


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_convert_already_exists.sql'],
)
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_convert_already_exists(
        cron_context: context_module.Context, patch,
):
    datetime_str = '2020-05-08T16:03:00'

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_update(*args, **kwargs):
        return

    _patch_dates(patch, datetime_str)

    before_count = await _update_states_count(cron_context)

    await _run_cron_task()

    after_count = await _update_states_count(cron_context)
    assert before_count == after_count


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_check_copy_table(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:03:00'
    operation_status = 'COMPLETED'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def _copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        return [
            f'task_id_{i}_{id(src_yt_client)}_{id(dst_yt_clients)}'
            for i, path in enumerate(paths)
        ]

    @patch('fleet_drivers_scoring.utils.yt_updater.common.tm_client')
    def _tm_client(src_yt_client):
        return TransferManagerMock()

    @patch('fleet_drivers_scoring.utils.yt_updater.converter.run_convert')
    async def _convert(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_convert(*args, **kwargs):
        return

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 4

    copy_records = await cron_context.pg.write_pool.fetch(
        """
        SELECT * FROM fleet_drivers_scoring.yt_update_states WHERE type='copy';
        """,
    )

    def _has_completed(record) -> bool:
        return record['status'] == 'done'

    assert all(_has_completed(x) for x in copy_records)


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_convert_table(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:04:00'
    operation_status = 'COMPLETED'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def _copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        return [
            f'task_id_{i}_{id(src_yt_client)}_{id(dst_yt_clients)}'
            for i, path in enumerate(paths)
        ]

    @patch('fleet_drivers_scoring.utils.yt_updater.common.tm_client')
    def _tm_client(src_yt_client):
        return TransferManagerMock()

    @patch('taxi.yt_wrapper.YtClient.alter_table')
    def _alter_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.mount_table')
    def _mount_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.run_merge')
    def _run_merge(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.move')
    def _move(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    @patch('fleet_drivers_scoring.utils.yt_updater.updater.run_update')
    async def _run_convert(*args, **kwargs):
        return

    await _run_cron_task()

    count = await _update_states_count(cron_context)
    assert count == 7

    calc_record = await cron_context.pg.write_pool.fetchrow(
        """
        SELECT * FROM fleet_drivers_scoring.yt_update_states WHERE type='calc';
        """,
    )

    convert_record = await cron_context.pg.write_pool.fetchrow(
        """
        SELECT
            *
        FROM fleet_drivers_scoring.yt_update_states WHERE type='convert';
        """,
    )
    assert convert_record['parent_id'] == calc_record['id']
    assert convert_record['name'] == 'ratings'
    assert convert_record['type'] == 'convert'
    assert convert_record['status'] == 'done'
    assert convert_record['dst_path']
    assert convert_record['src_cluster'] in [
        'seneca-man',
        'seneca-sas',
        'seneca-vla',
    ]
    assert convert_record['dst_cluster'] in [
        'seneca-man',
        'seneca-sas',
        'seneca-vla',
    ]
    assert convert_record['created_at']
    assert convert_record['updated_at']
    assert convert_record['revision']


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_run_update(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:04:00'
    operation_status = 'COMPLETED'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def _copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        return [
            f'task_id_{i}_{id(src_yt_client)}_{id(dst_yt_clients)}'
            for i, path in enumerate(paths)
        ]

    @patch('fleet_drivers_scoring.utils.yt_updater.common.tm_client')
    def _tm_client(src_yt_client):
        return TransferManagerMock()

    @patch('taxi.yt_wrapper.YtClient.alter_table')
    def _alter_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.mount_table')
    def _mount_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.run_merge')
    def _run_merge(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.move')
    def _move(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    await _run_cron_task()

    update = await cron_context.pg.write_pool.fetchrow(
        'SELECT * FROM fleet_drivers_scoring.yt_updates;',
    )

    assert update['name'] == 'ratings'
    assert update['path']
    assert update['revision']


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_update_already_exists.sql'],
)
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED,
    FLEET_DRIVERS_SCORING_SOURCE_YT_TABLES=SCORING_SOURCE_YT_TABLES_DEFAULT,
)
async def test_update_already_exists(
        cron_context: context_module.Context, monkeypatch, patch,
):
    datetime_str = '2020-05-08T17:04:00'
    operation_status = 'COMPLETED'
    operation_id = 'operation_id'
    share_url = 'share_url'

    _patch_dates(patch, datetime_str)

    _set_yql_response(monkeypatch, operation_status, operation_id, share_url)

    @patch('taxi.yt_wrapper.transfer_manager.copy')
    def _copy(paths, src_yt_client, dst_yt_clients, *args, **kwargs):
        return [
            f'task_id_{i}_{id(src_yt_client)}_{id(dst_yt_clients)}'
            for i, path in enumerate(paths)
        ]

    @patch('fleet_drivers_scoring.utils.yt_updater.common.tm_client')
    def _tm_client(src_yt_client):
        return TransferManagerMock()

    @patch('taxi.yt_wrapper.YtClient.alter_table')
    def _alter_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.mount_table')
    def _mount_table(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.run_merge')
    def _run_merge(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.move')
    def _move(*args, **kwargs):
        return

    @patch('taxi.yt_wrapper.YtClient.remove')
    def _remove(*args, **kwargs):
        return

    await _run_cron_task()

    count = await _updates_count(cron_context)

    assert count == 1


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_update_not_ready.sql'],
)
@pytest.mark.config(FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED)
async def test_update_not_ready(cron_context: context_module.Context, patch):
    datetime_str = '2020-05-08T12:03:00'

    _patch_dates(patch, datetime_str)

    before_count = await _updates_count(cron_context)

    await _run_cron_task()

    after_count = await _updates_count(cron_context)
    assert before_count == after_count


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_update_ready_1_of_2.sql'],
)
@pytest.mark.config(FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED)
async def test_update_ready_1_of_2(
        cron_context: context_module.Context, patch,
):
    datetime_str = '2020-05-08T12:03:00'

    _patch_dates(patch, datetime_str)

    time_storage = performance.TimeStorage('YT updater')
    await updater.run_update(cron_context, time_storage)

    after_count = await _updates_count(cron_context)
    assert after_count == 1


@pytest.mark.parametrize(
    'db_state, expected_yt_updates',
    [
        (
            'test_update_ready_same_revisions.sql',
            [
                {
                    'name': 'high_speed_driving',
                    'path': (
                        '//home/opteum/fm/unittests/features/'
                        'scoring/2020-05-08_02-00'
                    ),
                    'revision': '2020-05-08 02:00:00',
                },
                {
                    'name': 'ratings',
                    'path': (
                        '//home/opteum/fm/unittests/features/'
                        'scoring/2020-05-08_02-00'
                    ),
                    'revision': '2020-05-08 02:00:00',
                },
            ],
        ),
        (
            'test_update_ready_same_revision_stored.sql',
            [
                {
                    'name': 'high_speed_driving',
                    'path': (
                        '//home/opteum/fm/testing/features/scoring/'
                        'high_speed_driving/2020-05-04'
                    ),
                    'revision': '2020-05-08 02:00:00',
                },
                {
                    'name': 'ratings',
                    'path': (
                        '//home/opteum/fm/unittests/features/'
                        'scoring/2020-05-08_02-00'
                    ),
                    'revision': '2020-05-08 02:00:00',
                },
            ],
        ),
    ],
)
@pytest.mark.config(FLEET_DRIVERS_SCORING_YT_UPDATER=CONFIG_ENABLED)
async def test_update_ready_same_revisions(
        cron_context: context_module.Context,
        patch,
        pgsql,
        load,
        db_state,
        expected_yt_updates,
):
    global_utils.execute_file(pgsql, load, db_state)
    datetime_str = '2020-05-08T12:03:00'

    _patch_dates(patch, datetime_str)

    time_storage = performance.TimeStorage('YT updater')
    await updater.run_update(cron_context, time_storage)

    yt_updates = global_utils.fetch_all_yt_updates(pgsql)
    for update in yt_updates:
        update.pop('id')
        update.pop('created_at')

    ordered_object.assert_eq(
        yt_updates, global_utils.date_parsed(expected_yt_updates), paths=[''],
    )
