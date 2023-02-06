import pytest

import taxi.util.dates as dates

PG_TEST_PENDING = 'pg_test_pending.sql'


def check_expected(call_result, expected_data):
    def predicat(x):
        return x['labels']['skilltag'] + x['labels']['task_state']

    return sorted(call_result, key=predicat) == sorted(
        expected_data, key=predicat,
    )


@pytest.mark.parametrize(
    'pg_insert_file, solomon_expected',
    [
        ('pg_test_case_1.sql', 'solomon_test_case_1.json'),
        ('pg_test_case_2.sql', 'solomon_test_case_2.json'),
        ('pg_test_case_3.sql', 'solomon_test_case_3.json'),
        ('pg_test_case_4.sql', 'solomon_test_case_4.json'),
        ('pg_test_case_5.sql', 'solomon_test_case_5.json'),
    ],
)
@pytest.mark.now('2020-01-01 12:00:00')
async def test_count_skilltag_distribution(
        cron_context,
        cron_runner,
        load,
        load_json,
        mock_solomon,
        pg_insert_file,
        solomon_expected,
):
    solomon_mock = mock_solomon()
    solomon_request = load_json(solomon_expected)
    async with cron_context.pg.master_pool.acquire() as conn:
        await conn.execute(load(pg_insert_file))

    await cron_runner.count_skilltag_distribution()

    assert solomon_mock.times_called == 1

    call_result = solomon_mock.next_call()['request'].json['sensors']
    expected_data = solomon_request['sensors']
    assert check_expected(call_result, expected_data)


@pytest.mark.parametrize(
    'current_time, expected_data',
    [
        ('2020-01-01T10:00:01+0000', 'no_pending.json'),
        ('2020-01-01T11:00:01+0000', 'single_pending.json'),
        ('2020-01-01T12:00:01+0000', 'four_pending.json'),
        ('2020-01-01T14:00:01+0000', 'triple_pending.json'),
        ('2020-01-01T15:00:01+0000', 'double_pending.json'),
        ('2020-01-01T16:00:01+0000', 'end_all.json'),
    ],
)
async def test_pending_task_distribution(
        cron_client,
        mocked_time,
        cron_context,
        cron_runner,
        load,
        load_json,
        mock_solomon,
        current_time,
        expected_data,
):
    mocked_time.set(dates.parse_timestring(current_time))
    await cron_client.invalidate_caches()

    solomon_mock = mock_solomon()
    solomon_request = load_json(expected_data)

    async with cron_context.pg.master_pool.acquire() as conn:
        await conn.execute(load(PG_TEST_PENDING))

    await cron_runner.count_skilltag_distribution()
    assert solomon_mock.times_called == 1

    call_result = solomon_mock.next_call()['request'].json['sensors']
    expected_data = solomon_request['sensors']
    assert check_expected(call_result, expected_data)
