# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import inspect
import logging

import pytest


logger = logging.getLogger(__name__)


def _mapper(row):
    yield {
        key: row.get(key) for key in ('client_id', 'last_seen', 'is_active')
    }


def _reducer(key, input_row_iterator):
    output_row = {
        'client_id': key['client_id'],
        'last_seen': 0.0,
        'users_count': 0,
    }
    for row in input_row_iterator:
        if row['last_seen'] is not None:
            output_row['last_seen'] = max(
                output_row['last_seen'], row['last_seen'],
            )
        output_row['users_count'] += bool(row['is_active'])

    yield output_row


async def test_reducers_identical():
    from sf_data_load.crontasks.yt_crons import corp_users_info

    assert inspect.getsource(corp_users_info._reducer) == inspect.getsource(
        _reducer,
    ), '_reducer in tests != _reducer in cron'


async def test_mapper_identical():
    from sf_data_load.crontasks.yt_crons import corp_users_info

    assert inspect.getsource(corp_users_info._mapper) == inspect.getsource(
        _mapper,
    ), '_mapper in tests != _mapper in cron'


@pytest.mark.yt(dyn_table_data=['yt_corp_users_info.yaml'])
async def test_map_reduce(yt_apply, cron_context):
    ctx = cron_context
    yt = ctx.yt_wrapper.hahn  # pylint: disable=C0103

    corp_path = f'//home/taxi/unittests/replica/mongo/struct/corp/'
    attendance_path = yt.TablePath(
        name=corp_path + 'corp_client_attendance',
        columns=['client_id', 'last_seen'],
    )
    users_path = yt.TablePath(
        name=corp_path + 'corp_users', columns=['client_id', 'is_active'],
    )

    for tab in (attendance_path, users_path):
        await yt.unmount_table(tab, sync=True)
        await yt.mount_table(tab, sync=True)

    tmp_path = f'//home/taxi/unittests/features/internal-b2b/sf-data-load/tmp'

    with yt.TempTable(tmp_path) as agg_tab:
        await yt.run_map_reduce(
            mapper=_mapper,
            reducer=_reducer,
            source_table=[attendance_path, users_path],
            destination_table=agg_tab,
            reduce_by=['client_id'],
        )
        output = list(await yt.read_table(agg_tab))

    assert output == [
        {
            'client_id': 'qwerty1',
            'last_seen': 1654495268.512,
            'users_count': 2,
        },
        {
            'client_id': 'qwerty2',
            'last_seen': 1654495270.512,
            'users_count': 1,
        },
    ]
