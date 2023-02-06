import pytest


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'support': {
            'metaqueues': ['ru_taxi_support'],
            'display_name': '',
            'should_use_internal_queue_service': False,
            'reg_groups': [],
        },
    },
    CALLCENTER_OPERATORS_STATUS_TO_QUEUE_STATUS_MAPPING={
        '__default__': {
            '__default__': {'__default__': 'disconnected'},
            'connected': {
                '__default__': 'connected',
                'cool_sub_status': 'extra_status',
            },
        },
    },
    CALLCENTER_QUEUES_TARGET_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
@pytest.mark.parametrize('db_filled', [False, True])
async def test_target_status_fetcher(
        taxi_callcenter_queues, pgsql, testpoint, mockserver, db_filled,
):
    if db_filled:
        cursor = pgsql['callcenter_queues'].cursor()
        cursor.execute(
            'INSERT INTO callcenter_queues.target_status '
            '(sip_username, status, updated_seq, project) '
            'VALUES (\'sip_1\', \'status\', 0, \'disp\');',
        )
        cursor.close()

    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        assert 'filter' in request.json
        assert request.json['filter'] == {'projects': ['disp']}
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

    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('target_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_queues.spawn_task('target_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project'
        ' from callcenter_queues.target_status',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', 'extra_status', 1, 'disp')]
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'support': {
            'metaqueues': ['ru_taxi_support'],
            'display_name': '',
            'should_use_internal_queue_service': False,
            'reg_groups': [],
        },
    },
    CALLCENTER_QUEUES_TARGET_STATUS_FETCHER_SETTINGS={
        'enabled': False,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_target_status_fetcher_disabled(
        taxi_callcenter_queues, pgsql, testpoint, mockserver,
):

    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('target_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_queues.spawn_task('target_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project'
        ' from callcenter_queues.target_status',
    )
    result = cursor.fetchall()
    assert not result
    cursor.close()


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'support': {
            'metaqueues': ['ru_taxi_support'],
            'display_name': '',
            'should_use_internal_queue_service': False,
            'reg_groups': [],
        },
    },
    CALLCENTER_OPERATORS_STATUS_TO_QUEUE_STATUS_MAPPING={
        '__default__': {
            '__default__': {'__default__': 'disconnected'},
            'connected': {
                '__default__': 'connected',
                'cool_sub_status': 'extra_status',
            },
        },
    },
    CALLCENTER_QUEUES_TARGET_STATUS_FETCHER_SETTINGS={
        'enabled': True,
        'period_ms': 100,
        'limit': 2,
    },
)
async def test_target_status_fetcher_duplicates(
        taxi_callcenter_queues, pgsql, testpoint, mockserver,
):
    @mockserver.json_handler('/callcenter-reg/v1/sip_user/status/list')
    def _cc_reg_handler(request):
        assert 'filter' in request.json
        assert request.json['filter'] == {'projects': ['disp']}
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

    await taxi_callcenter_queues.invalidate_caches()

    @testpoint('target_status_fetcher::iteration')
    def one_iteration(arg):
        pass

    async with taxi_callcenter_queues.spawn_task('target_status_fetcher'):
        await one_iteration.wait_call()

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SELECT '
        'sip_username, status, updated_seq, project'
        ' from callcenter_queues.target_status',
    )
    result = cursor.fetchall()
    assert result == [('sip_1', 'connected', 2, 'disp')]
    cursor.close()
