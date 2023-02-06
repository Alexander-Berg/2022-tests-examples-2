import pytest

from taxi.util import dates as dates_utils

from abt.logic import context as contexts
from abt.logic import watch
from abt.repositories import storage as repos_storage
from test_abt import consts


SOME_TIMESTRING = '1970-01-01T00:00:00'


def mock_get_table_attributes(storage, func):
    storage.yt.meta.get_table_attributes = func
    return storage


@pytest.mark.pgsql('abt', files=['responses_cache.sql'])
@pytest.mark.parametrize(
    'indexed_at,updated_at,stq_called,precomputes_are_actual',
    [
        pytest.param(
            None, SOME_TIMESTRING, 1, False, id='never indexed -> stq called',
        ),
        pytest.param(
            dates_utils.parse_timestring_aware('2020-01-01T00:00:00+0000'),
            '2020-02-01T00:00:00',
            1,
            False,
            id='table has been updated since last indexing -> stq called',
        ),
        pytest.param(
            dates_utils.parse_timestring_aware('2020-02-01T00:00:00+0000'),
            '2020-01-01T00:00:00',
            0,
            True,
            id='table has NOT been updated since last indexing -> no stq',
        ),
    ],
)
@pytest.mark.config(ABT_WATCH_PRECOMPUTES_TABLES_ENABLED=True)
@pytest.mark.config(
    ABT_RESPONSES_CACHE={'enabled': True, 'handles_settings': []},
)
async def test_correct_update_algorithm(
        stq,
        cron_context,
        abt,
        pgsql,
        indexed_at,
        updated_at,
        stq_called,
        precomputes_are_actual,
):
    def _check_presence(presence):
        cursor = pgsql['abt'].cursor()
        cursor.execute(f'SELECT * FROM abt.responses_cache')

        assert bool(cursor.fetchall()) == presence

        cursor.close()

    await abt.state.add_precomputes_table(indexed_at=indexed_at)

    async def _get_table_attributes_mock(*args, **kwargs):
        return {'modification_time': updated_at}

    _check_presence(True)
    await watch.proceed(
        contexts.WatchPrecomputesTablesContext(
            mock_get_table_attributes(
                repos_storage.from_context(cron_context),
                _get_table_attributes_mock,
            ),
            cron_context.stq,
            cron_context.config,
        ),
    )
    _check_presence(precomputes_are_actual)

    queue = stq.abt_index_precomputes
    if stq_called:
        task_id = (
            f'precomputes_table/{consts.DEFAULT_YT_CLUSTER}.'
            f'{consts.DEFAULT_YT_PATH}'
        )
        task = queue.next_call()
        assert task['id'] == task_id
    else:
        assert stq.is_empty


@pytest.mark.parametrize(
    'stq_called',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(ABT_WATCH_PRECOMPUTES_TABLES_ENABLED=True),
            ],
            id='watch enabled',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(ABT_WATCH_PRECOMPUTES_TABLES_ENABLED=False),
            ],
            id='watch disabled',
        ),
    ],
)
async def test_switcher(cron_runner, stq, yt_apply, abt, stq_called):
    await abt.state.add_precomputes_table(indexed_at=None)

    await cron_runner.watch_precomputes_tables()

    assert stq.is_empty != stq_called


@pytest.mark.config(ABT_WATCH_PRECOMPUTES_TABLES_ENABLED=True)
async def test_yt_error(stq, cron_context, abt):
    await abt.state.add_precomputes_table(indexed_at=None)
    second_precomputes_table = await abt.state.add_precomputes_table(
        indexed_at=None, yt_cluster='hahan',
    )

    async def _get_table_attributes_mock(cluster, path, attrs):
        if cluster == second_precomputes_table['yt_cluster']:
            raise Exception('testsuite exception')
        return {'modification_time': SOME_TIMESTRING}

    await watch.proceed(
        contexts.WatchPrecomputesTablesContext(
            mock_get_table_attributes(
                repos_storage.from_context(cron_context),
                _get_table_attributes_mock,
            ),
            cron_context.stq,
            cron_context.config,
        ),
    )

    task_id = (
        f'precomputes_table/{consts.DEFAULT_YT_CLUSTER}.'
        f'{consts.DEFAULT_YT_PATH}'
    )
    assert stq.abt_index_precomputes.next_call()['id'] == task_id
    assert stq.is_empty
