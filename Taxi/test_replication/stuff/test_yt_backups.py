import datetime

import pytest

from replication.foundation import consts
from replication.stuff import yt_backups
from replication.targets.yt.control.table_updater import backups
from replication.targets.yt.control.table_updater import (
    backups_collection_plugin as plugin,
)

NOW = datetime.datetime(2018, 12, 27, 0, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(YT_BACKUPS_SETTINGS={'prefix_aliases': ['taxi']})
@pytest.mark.parametrize(
    'repl_settings_doc,expected_backup_operations',
    [
        (
            None,
            {
                (
                    '//home/taxi/unittests/replica/example/example_rule',
                    'hahn/2018-12-27/replica/example/example_rule',
                ),
            },
        ),
        (
            {
                'name': 'hahn',
                'created': NOW,
                'rules': [
                    {
                        'source': (
                            '//home/taxi/unittests/'
                            'replica/example/example_rule'
                        ),
                        'status': backups.STATUS_WAIT,
                    },
                ],
                'start_day': NOW,
            },
            {
                (
                    '//home/taxi/unittests/replica/example/example_rule',
                    'hahn/2018-12-27/replica/example/example_rule',
                ),
            },
        ),
        (
            {
                'name': 'hahn',
                'created': NOW,
                'rules': [
                    {
                        'source': (
                            '//home/taxi/unittests'
                            '/replica/example/example_rule'
                        ),
                        'status': backups.STATUS_OK,
                    },
                    {
                        'source': (
                            '//home/taxi/unittests/'
                            'replica/example/example_rule_bonus'
                        ),
                        'status': backups.STATUS_OK,
                    },
                ],
                'start_day': NOW,
            },
            set(),
        ),
    ],
)
async def test_do_stuff(
        patch,
        _fake_context,
        yt_clients_storage,
        repl_settings_doc,
        expected_backup_operations,
):
    class CronCtx:
        # pylint: disable=invalid-name
        class data:
            replication_core = _fake_context

    event_storage = None

    if repl_settings_doc:
        event_storage = plugin.get_settings_storage(
            _fake_context, repl_settings_doc['name'],
        )
        await event_storage.load_settings()
        await event_storage.update_settings_versioned(repl_settings_doc)

    backup_operations = set()

    @patch('replication.targets.yt.control.table_updater.backups._run_merge')
    def _run_merge(
            yt_client, source_path, target_path, tg_attributes, spec, **kwargs,
    ):
        assert spec['data_size_per_job'] == backups.BACKUP_DATA_SIZE_PER_JOB
        backup_operations.add((source_path, target_path))
        yt_client.rows_by_ids[target_path] = {}

    with yt_clients_storage(
            default_clients_data={
                'hahn-backup': {
                    '//home/taxi/unittests/replica/example/example_rule': {},
                    '//home/taxi/unittests/'
                    'replica/example/example_rule/@compression_codec': 'lz4',
                    '//home/taxi/unittests/'
                    'replica/example/example_rule/@unflushed_timestamp': int(
                        NOW.timestamp() * 2.0 ** 30,
                    ),
                },
            },
    ) as all_clients:
        await yt_backups.do_stuff(CronCtx, None)
    assert backup_operations == expected_backup_operations
    if expected_backup_operations:
        backup_client = all_clients['hahn-backup']
        assert dict(backup_client.rows_by_ids) == {
            '//home/taxi/unittests/replica/example/example_rule': {},
            'hahn/2018-12-27/replica/example': {},
            'hahn/2018-12-27/replica/example/example_rule': {},
        }

    # checks for consistency
    if repl_settings_doc:
        assert event_storage
        await _fake_context.db.replication_settings.remove(
            {
                # pylint: disable=protected-access
                '_id': plugin._YT_BACKUPS_TEMPLATE.format(
                    client_name=repl_settings_doc['name'],
                ),
            },
        )
        await event_storage.load_settings(force=True)
        await event_storage.update_settings_versioned(repl_settings_doc)

    backup_operations = set()
    with yt_clients_storage(default_clients=all_clients):
        await yt_backups.do_stuff(CronCtx, None)
        assert backup_operations == set()

        await yt_backups.do_stuff(CronCtx, None)
        assert backup_operations == set()


@pytest.fixture
def _fake_context(replication_ctx, monkeypatch):
    old_getter = replication_ctx.rule_keeper.rules_storage.get_rules_list

    def get_rules_list(*args, **kwargs):
        return old_getter(
            rule_name='example_rule',
            source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
        )

    monkeypatch.setattr(
        replication_ctx.rule_keeper.rules_storage,
        'get_rules_list',
        get_rules_list,
    )
    return replication_ctx
