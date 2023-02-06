import datetime

import pytest


@pytest.mark.config(
    CALLCENTER_STATS_USER_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
@pytest.mark.parametrize('db_filled', [False, True])
async def test_user_status_fetcher(
        taxi_callcenter_stats, pgsql, testpoint, mockserver, db_filled,
):
    if db_filled:
        cursor = pgsql['callcenter_stats'].cursor()
        cursor.execute(
            'INSERT INTO callcenter_stats.user_status '
            '(sip_username, status, updated_seq, project) '
            'VALUES (\'sip_1\', \'status\', 0, \'disp\');',
        )
        cursor.close()

    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 2,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 1,
                        'user_status': {
                            'status': 'connected',
                            'sub_status': 'cool_sub_status',
                        },
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project, sub_status'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', 'connected', 1, 'disp', 'cool_sub_status')]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_USER_STATUS_FETCHER_SETTINGS={
        'enabled': False,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_user_status_fetcher_disabled(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    assert not result
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_USER_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_user_status_fetcher_duplicates(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):
    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 3,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 1,
                        'user_status': {
                            'status': 'connected',
                            'sub_status': 'cool_sub_status',
                        },
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 2,
                        'user_status': {'status': 'connected'},
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project, sub_status'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', 'connected', 2, 'disp', None)]
    cursor.close()


@pytest.mark.parametrize(
    ('status', 'sub_status', 'expected_status', 'excpected_sub_status'),
    [
        ('connected', 'cool_sub_status', 'overrided', None),
        ('connected', None, 'connected', None),
        ('connected', 'another_sub_status', 'connected', 'another_sub_status'),
        ('paused', None, 'super_paused', 'some_sub_status'),
    ],
)
@pytest.mark.config(
    CALLCENTER_STATS_USER_STATUS_OVERRIDES={
        '__default__': [
            {
                'from': {
                    'status': 'connected',
                    'sub_status': 'cool_sub_status',
                },
                'to': {'status': 'overrided'},
            },
            {
                'from': {'status': 'paused'},
                'to': {
                    'status': 'super_paused',
                    'sub_status': 'some_sub_status',
                },
            },
        ],
    },
    CALLCENTER_STATS_USER_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_user_status_fetcher_overrides(
        taxi_callcenter_stats,
        pgsql,
        testpoint,
        mockserver,
        status,
        sub_status,
        excpected_sub_status,
        expected_status,
):
    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 2,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 1,
                        'user_status': {
                            'status': status,
                            'sub_status': sub_status,
                        },
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project, sub_status'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    assert result == [
        ('sip_1', expected_status, 1, 'disp', excpected_sub_status),
    ]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_USER_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_status_sub_status_updated_at(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):
    # add operator
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'INSERT INTO callcenter_stats.user_status '
        '(sip_username, status, updated_seq, project) '
        'VALUES (\'sip_1\', \'connected\', 0, \'disp\');',
    )
    cursor.close()

    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 3,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 1,
                        'user_status': {
                            'status': 'connected',
                            'sub_status': 'cool_sub_status',
                        },
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'status_updated_at, sub_status_updated_at'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    row = result[0]
    assert row[0] != datetime.datetime(
        2022, 6, 8, 11, 55, 24, tzinfo=datetime.timezone.utc,
    )
    assert row[1] == datetime.datetime(
        2022, 6, 8, 11, 55, 24, tzinfo=datetime.timezone.utc,
    )
    cursor.close()

    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler_2(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 3,
                'statuses': [
                    {
                        'sip_username': 'sip_1',
                        'project': 'disp',
                        'update_seq': 1,
                        'user_status': {
                            'status': 'paused',
                            'sub_status': 'cool_sub_status',
                        },
                        'updated_at': '2022-06-08T11:55:25+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    async with taxi_callcenter_stats.spawn_task('user_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'status_updated_at, sub_status_updated_at'
        ' from callcenter_stats.user_status',
    )
    result = cursor.fetchall()
    row = result[0]
    assert row[0] == datetime.datetime(
        2022, 6, 8, 11, 55, 25, tzinfo=datetime.timezone.utc,
    )
    assert row[1] == datetime.datetime(
        2022, 6, 8, 11, 55, 24, tzinfo=datetime.timezone.utc,
    )
    cursor.close()
