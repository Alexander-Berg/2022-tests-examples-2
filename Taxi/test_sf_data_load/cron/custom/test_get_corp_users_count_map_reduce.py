# pylint: disable=redefined-outer-name
# pylint: disable=W0212
import inspect
import logging

import pytest


logger = logging.getLogger(__name__)


def _mapper(row):
    output_rows = []
    client_id = row['client_id']
    is_active = row['is_active']

    if not is_active:
        return

    if not row['limits']:
        return

    for service in row['limits']:
        output_rows.append(
            {
                'client_id': client_id,
                'is_active': is_active,
                'service_name': service['service'],
            },
        )

    for data in output_rows:
        yield data


def _reducer(key, rows):
    output_row = {
        'client_id': key['client_id'],
        'service': key['service_name'],
        'users_count': 0,
    }

    for row in rows:
        output_row['users_count'] += bool(row['is_active'])

    yield output_row


async def test_reducers_identical():
    from sf_data_load.crontasks.custom import get_corp_users_count

    assert inspect.getsource(
        get_corp_users_count._reducer,
    ) == inspect.getsource(_reducer), '_reducer in tests != _reducer in cron'


async def test_mapper_identical():
    from sf_data_load.crontasks.custom import get_corp_users_count

    assert inspect.getsource(
        get_corp_users_count._mapper,
    ) == inspect.getsource(_mapper), '_mapper in tests != _mapper in cron'


@pytest.mark.yt(dyn_table_data=['yt_corp_users_info.yaml'])
async def test_map_reduce(yt_apply, cron_context):
    ctx = cron_context
    yt = ctx.yt_wrapper.hahn  # pylint: disable=C0103

    users_path = f'//home/taxi/unittests/replica/mongo/struct/corp/corp_users'

    await yt.unmount_table(users_path, sync=True)
    await yt.mount_table(users_path, sync=True)

    tmp_path = f'//home/taxi/unittests/features/internal-b2b/sf-data-load/tmp'

    with yt.TempTable(tmp_path) as agg_tab:
        await yt.run_map_reduce(
            mapper=_mapper,
            reducer=_reducer,
            source_table=users_path,
            destination_table=agg_tab,
            reduce_by=['client_id', 'service_name'],
        )
        output = list(await yt.read_table(agg_tab))

    assert output == [
        {'client_id': '1', 'service': 'drive', 'users_count': 2},
        {'client_id': '1', 'service': 'taxi', 'users_count': 3},
        {'client_id': '2', 'service': 'drive', 'users_count': 1},
        {'client_id': '2', 'service': 'taxi', 'users_count': 1},
        {'client_id': '4', 'service': 'eats', 'users_count': 1},
    ]
