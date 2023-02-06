import pytest


@pytest.mark.config(
    CALLCENTER_STATS_TEL_STATE_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
@pytest.mark.parametrize('db_filled', [False, True])
async def test_tel_state_fetcher(
        taxi_callcenter_stats, pgsql, testpoint, mockserver, db_filled,
):
    if db_filled:
        cursor = pgsql['callcenter_stats'].cursor()
        cursor.execute(
            'INSERT INTO callcenter_stats.tel_state '
            '(sip_username, metaqueues, subcluster, '
            'is_connected, is_paused, is_valid, updated_seq) '
            'VALUES (\'sip_1\', \'{test_metaqueue}\', '
            '\'1\', True, True, True, 0);',
        )
        cursor.close()

    @mockserver.json_handler('/callcenter-queues/v1/sip_user/tel_state/list')
    def _cc_queues_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 2,
                'states': [
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 1,
                        'metaqueues': ['new_metaqueue'],
                        'subcluster': '2',
                        'is_connected': True,
                        'is_paused': False,
                        'is_valid': True,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('tel_state_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('tel_state_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, subcluster, '
        'is_connected, is_paused, is_valid, updated_seq'
        ' from callcenter_stats.tel_state',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', ['new_metaqueue'], '2', True, False, True, 1)]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_TEL_STATE_FETCHER_SETTINGS={
        'enabled': False,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_tel_state_fetcher_disabled(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('tel_state_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('tel_state_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, subcluster, '
        'is_connected, is_paused, is_valid, updated_seq'
        ' from callcenter_stats.tel_state',
    )
    result = cursor.fetchall()
    assert not result
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_TEL_STATE_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_tel_state_fetcher_duplicates(
        taxi_callcenter_stats, pgsql, testpoint, mockserver,
):
    @mockserver.json_handler('/callcenter-queues/v1/sip_user/tel_state/list')
    def _cc_queues_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 3,
                'states': [
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 1,
                        'metaqueues': ['new_metaqueue'],
                        'subcluster': '2',
                        'is_connected': True,
                        'is_paused': False,
                        'is_valid': True,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                    {
                        'sip_username': 'sip_1',
                        'update_seq': 2,
                        'metaqueues': ['new_new_metaqueue'],
                        'subcluster': '3',
                        'is_connected': True,
                        'is_paused': True,
                        'is_valid': True,
                        'updated_at': '2022-06-08T11:55:24+0000',
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    @testpoint('tel_state_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_stats.spawn_task('tel_state_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, metaqueues, subcluster, '
        'is_connected, is_paused, is_valid, updated_seq'
        ' from callcenter_stats.tel_state',
    )
    result = cursor.fetchall()
    assert result == [
        ('sip_1', ['new_new_metaqueue'], '3', True, True, True, 2),
    ]
    cursor.close()
