import datetime

import pytest

from tests_contractor_statistics_view import pg_helpers as pgh


@pytest.mark.parametrize(
    'idx',
    ['0', '1', '2'],
    ids=[
        'non_existent_driver',
        'driver_wo_last_order',
        'driver_with_last_order',
    ],
)
@pytest.mark.pgsql(
    'contractor_statistics_view', files=['insert_in_contractors.sql'],
)
async def test_handle_completed_order(stq_runner, pgsql, idx):
    last_order_completion_time = '202{}-03-20T11:22:33.44Z'.format(idx)

    await stq_runner.contractor_statistics_view_handle_completed_order.call(
        task_id='order_id',
        args=[],
        kwargs={
            'driver_profile_id': 'dpid' + idx,
            'park_id': 'pid' + idx,
            'last_order_id': 'last_order_id' + idx,
            'last_order_completion_time': {
                '$date': last_order_completion_time,
            },
        },
        expect_fail=False,
    )

    query = f"""
    SELECT
        last_order_id, last_order_completion_time, updated_at
    FROM contractor_statistics_view.contractors
    WHERE driver_profile_id = 'dpid{idx}' and park_id = 'pid{idx}';
    """

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    time_now = pgh.datetime_from_timestamp(
        str(datetime.datetime.now()), fmt='%Y-%m-%d %H:%M:%S.%f',
    )

    if int(idx):
        assert rows[0][0] == 'last_order_id' + idx
        assert rows[0][1] == pgh.datetime_from_timestamp(
            last_order_completion_time,
        )
        assert (time_now - rows[0][2]).total_seconds() <= 1
    else:
        assert rows == []
