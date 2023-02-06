# pylint: disable=protected-access
import datetime
import typing

import pytest

from taxi.maintenance import run

from replication import replication_tasks
from replication.common import host_resources
from replication.foundation import consts
from replication.replication import cron_run


class RawTaskDesc(typing.NamedTuple):
    source_id: str
    target_ids: tuple
    replicate_from: typing.Any = None


def cron_task_key(task):
    result = []
    for raw_task in task._raw_tasks:
        result.append(
            RawTaskDesc(
                raw_task.source.id,
                tuple(
                    sorted(
                        unit.state.target.id
                        for unit in raw_task.raw_replication_units
                    ),
                ),
                raw_task.replicate_from,
            ),
        )
    return task.name, tuple(sorted(result))


TEST_RULE = 'test_sharded_rule'
CRON_ALIAS = replication_tasks.TASK_TEMPLATE.format(
    consts.SOURCE_TYPE_QUEUE_MONGO, TEST_RULE,
)

PATH_END = 'test_struct_sharded'
CRON_ALIAS_PATH_END = replication_tasks.TASK_TEMPLATE.format(
    consts.SOURCE_TYPE_QUEUE_MONGO, PATH_END,
)

EXPECTED = [
    (
        CRON_ALIAS,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_0_4',
                target_ids=('yt-test_sharded_rule_no_partial-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_1_4',
                target_ids=(
                    'yt-test_sharded_rule_no_partial-arni',
                    'yt-test_sharded_rule_no_partial-hahn',
                ),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_0_4',
                target_ids=(
                    'yt-test_sharded_rule2_sharded_struct-arni',
                    'yt-test_sharded_rule2_sharded_struct-hahn',
                ),
                replicate_from=datetime.datetime(2019, 5, 28, 1, 20),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_0_4',
                target_ids=(
                    'yt-test_sharded_rule_sharded_struct-arni',
                    'yt-test_sharded_rule_sharded_struct-hahn',
                ),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_1_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_1_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_1_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_1_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_2_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_2_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_2_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 37),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_2_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_3_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_3_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-arni',),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule2_3_4',
                target_ids=('yt-test_sharded_rule2_sharded_struct-hahn',),
                replicate_from=None,
            ),
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_3_4',
                target_ids=('yt-test_sharded_rule_sharded_struct-hahn',),
                replicate_from=datetime.datetime(2019, 5, 28, 2, 20),
            ),
        ),
    ),
    (
        CRON_ALIAS_PATH_END,
        (
            RawTaskDesc(
                source_id='queue_mongo-staging_test_sharded_rule_2_4',
                target_ids=(
                    'yt-test_sharded_rule_sharded_struct-seneca-man',
                    'yt-test_sharded_rule_sharded_struct-seneca-vla',
                ),
                replicate_from=datetime.datetime(2019, 5, 28, 4, 20),
            ),
        ),
    ),
]


async def _get_replication_tasks(monkeypatch, replication_ctx):
    monkeypatch.setattr(host_resources, '_get_free_ram', lambda: (100, 100000))
    monkeypatch.setattr(host_resources, '_get_free_threads', lambda: 100)
    parser = cron_run._get_parser()
    run.add_run_arguments(parser)
    args = parser.parse_args(['--without-lock'])

    # pylint: disable=no-value-for-parameter
    tasks = await cron_run._get_replication_tasks(args)

    tasks.sort(key=cron_task_key)
    assert list(map(cron_task_key, tasks)) == EXPECTED


@pytest.mark.config(
    REPLICATION_CRON_MAIN_SETUP={
        'use_chains': ['test/test_struct_sharded', 'test/test_sharded_pg'],
        'use_new_chains_logic': True,
    },
)
async def test_get_replication_tasks(monkeypatch, replication_ctx):
    await _get_replication_tasks(monkeypatch, replication_ctx)


async def test_get_replication_tasks_use_old_chains_logic(
        monkeypatch, replication_ctx,
):
    await _get_replication_tasks(monkeypatch, replication_ctx)
