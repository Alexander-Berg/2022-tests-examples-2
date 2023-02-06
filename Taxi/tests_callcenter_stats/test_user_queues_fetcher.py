import pytest


@pytest.mark.config(
    CALLCENTER_STATS_USER_QUEUES_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
@pytest.mark.parametrize('db_filled', [False, True])
async def test_user_queues_fetcher(
        taxi_callcenter_stats, pgsql, testpoint, mockserver, db_filled,
):
    if db_filled:
        cursor = pgsql['callcenter_stats'].cursor()
        cursor.execute(
            'INSERT INTO callcenter_stats.user_queues '
            '(sip_username, metaqueues, updated_seq) '
            'VALUES (\'sip_1\', \'{test_metaqueue}\', 0);',
        )
        cursor.close()

    @mockserver.json_handler('/callcenter-queues/v1/sip_user/queues/list')
    def _cc_queues_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 2,
                'queues': [
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 1,
                        'metaqueues': ['new_metaqueue'],
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_queues_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_queues_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, updated_seq'
        ' from callcenter_stats.user_queues',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', ['new_metaqueue'], 1)]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_USER_QUEUES_FETCHER_SETTINGS={
        'enabled': False,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_user_queues_fetcher_disabled(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_queues_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_queues_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, updated_seq'
        ' from callcenter_stats.user_queues',
    )
    result = cursor.fetchall()
    assert not result
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_USER_QUEUES_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_user_queues_fetcher_duplicates(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):
    @mockserver.json_handler('/callcenter-queues/v1/sip_user/queues/list')
    def _cc_queues_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 3,
                'queues': [
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 1,
                        'metaqueues': ['new_metaqueue'],
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 2,
                        'metaqueues': ['new_new_metaqueue'],
                        'updated_at': '2022-06-08T11:55:25+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('user_queues_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('user_queues_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, updated_seq'
        ' from callcenter_stats.user_queues',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', ['new_new_metaqueue'], 2)]
    cursor.close()
