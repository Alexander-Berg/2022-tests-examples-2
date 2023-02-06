import datetime

import pytest

BASE_TEL_RESPONSE = {
    'PARAM': {},
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSDESC': None,
    'STATUS': 'TRUE',
}

BAD_TEL_RESPONSE = {
    'PARAM': {},
    'TYPE': 'REPLY',
    'STATUSCODE': 500,
    'STATUSDESC': None,
    'STATUS': 'TRUE',
}


@pytest.mark.config(
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        's1': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's2': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's3': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
    },
    CALLCENTER_METAQUEUES=[
        {'allowed_clusters': ['s1', 's2'], 'name': 'disp', 'number': '840100'},
        {'allowed_clusters': ['s3'], 'name': 'corp', 'number': '840100'},
    ],
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.pgsql(
    'callcenter_queues',
    files=['insert_agent.sql', 'insert_cc_system_info.sql'],
)
@pytest.mark.parametrize(
    [
        'status',
        'metaqueues',
        'subcluster',
        'target_status',
        'target_metaqueues',
        'target_subcluster',
        'expected_is_connected',
        'expected_is_paused',
        'expected_tel_metaqueues',
        'expected_tel_subcluster',
        'tel_called',
        'expect_fail',
    ],
    (
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'disconnected',
            '{disp}',
            None,
            False,
            False,
            [],
            None,
            1,
            False,
            id='disconnect with target_queues',
        ),
        pytest.param(
            'paused',
            '{disp}',
            's1',
            'disconnected',
            '{disp}',
            None,
            False,
            False,
            [],
            None,
            1,
            False,
            id='disconnect from paused',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'disconnected',
            '{}',
            None,
            False,
            False,
            [],
            None,
            1,
            False,
            id='disconnect with empty target_queues',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'connected',
            '{}',
            None,
            False,
            False,
            [],
            None,
            1,
            False,
            id='cannot connect with empty queues, disconnect him',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'connected',
            '{corp}',
            None,
            True,
            False,
            ['corp'],
            's3',
            4,  # disconnect + del mvp q + add mvp 1 + connect
            False,
            id='reconnect other queue',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'connected',
            '{disp}',
            's2',
            True,
            False,
            ['disp'],
            's2',
            4,  # disconnect + del mvp q + add mvp 1 + connect
            False,
            id='reconnect other sub',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'connected',
            '{disp}',
            's3',
            True,
            False,
            ['disp'],
            's1',
            0,  # s3 sub is not in disp,
            # choose best one, best is current one, no tel changes
            False,
            id='bad sub for disp, will use best one',
        ),
        pytest.param(
            'connected',
            '{corp}',
            's4',  # for emulation purpose
            'connected',
            '{corp}',
            's3',
            True,
            False,
            ['corp'],
            's3',
            4,  # s4 sub is not in disp,
            # choose best one, best is NOT current one
            False,
            id='bad sub for disp, will use best one',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'connected',
            '{corp}',
            's3',
            True,
            False,
            ['corp'],
            's3',
            4,  # disconnect + del mvp q + add mvp 1 + connect
            False,
            id='other sub + other queue',
        ),
        pytest.param(
            'disconnected',
            '{}',
            '',
            'connected',
            '{disp}',
            None,
            True,
            False,
            ['disp'],
            's2',
            3,  # del mvp + add mvp + connect
            False,
            id='connect from disconnect',
        ),
        pytest.param(
            'disconnected',
            '{}',
            '',
            'paused',
            '{disp}',
            None,
            True,
            True,
            ['disp'],
            's2',
            3,  # del mvp + add mvp + connect
            False,
            id='paused from disconnect',
        ),
        pytest.param(
            'paused',
            '{disp}',
            's1',
            'connected',
            '{disp}',
            's1',
            True,
            False,
            ['disp'],
            's1',
            1,  # sub and queu is the same
            False,
            id='connect from pause, no changes in queues',
        ),
        pytest.param(
            'paused',
            '{disp}',
            's1',
            'connected',
            '{disp}',
            's2',
            True,
            False,
            ['disp'],
            's2',
            4,  # disc + del mvp + add mvp + conn
            False,
            id='connect from pause, changes in queues',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'paused',
            '{disp}',
            's1',
            True,
            True,
            ['disp'],
            's1',
            1,  # sub and queue is the same
            False,
            id='pause from connected, no changes in queues',
        ),
        pytest.param(
            'connected',
            '{disp}',
            's1',
            'paused',
            '{disp}',
            's2',
            True,
            True,
            ['disp'],
            's2',
            4,  # disc + del mvp + add mvp + conn
            False,
            id='pause from connected, changes in queues',
        ),
    ),
)
async def test_stq(
        stq_runner,
        taxi_callcenter_queues,
        status,
        target_status,
        metaqueues,
        target_metaqueues,
        subcluster,
        target_subcluster,
        expected_is_connected,
        expected_is_paused,
        expected_tel_subcluster,
        expected_tel_metaqueues,
        tel_called,
        pgsql,
        mockserver,
        taxi_config,
        expect_fail,
        stq,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    cursor = pgsql['callcenter_queues'].cursor()
    # update target status
    if target_status is not None:
        cursor.execute(
            f'UPDATE callcenter_queues.target_status'
            f' SET status = \'{target_status}\''
            f' WHERE sip_username=\'a\'',
        )
    # update target queues
    if target_metaqueues is not None:
        cursor.execute(
            f'UPDATE callcenter_queues.target_queues'
            f' SET metaqueues = \'{target_metaqueues}\''
            f' WHERE sip_username=\'a\'',
        )
    # update target subcluster
    if target_subcluster is not None:
        cursor.execute(
            f'UPDATE callcenter_queues.target_queues'
            f' SET wanted_subcluster ='
            f' \'{target_subcluster}\' WHERE sip_username=\'a\'',
        )

    # update current tel state
    if status is not None:
        mapping = taxi_config.get(
            'CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING',
        )
        tel_state = mapping.get(status, mapping['__default__'])
        is_connected = tel_state['is_connected']
        is_paused = tel_state['is_paused']
        cursor.execute(
            f'UPDATE callcenter_queues.tel_state SET'
            f' is_connected = {is_connected},'
            f' is_paused = {is_paused} WHERE sip_username=\'a\'',
        )
    if metaqueues is not None:
        cursor.execute(
            f'UPDATE callcenter_queues.tel_state SET'
            f' metaqueues= \'{metaqueues}\''
            f' WHERE sip_username=\'a\'',
        )
    if subcluster is not None:
        cursor.execute(
            f'UPDATE callcenter_queues.tel_state SET'
            f' subcluster= \'{subcluster}\''
            f' WHERE sip_username=\'a\'',
        )
    cursor.close()

    username = 'a'

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert username.lower() in request.path_qs.lower()
        return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}

    await stq_runner.callcenter_queues_status_changer.call(
        task_id=username,
        kwargs={'username': username},
        expect_fail=expect_fail,
    )

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        f'SELECT metaqueues, is_connected, is_paused, subcluster'
        f' FROM callcenter_queues.tel_state  WHERE sip_username=\'a\'',
    )
    result = cursor.fetchall()
    assert result == [
        (
            expected_tel_metaqueues,
            expected_is_connected,
            expected_is_paused,
            expected_tel_subcluster,
        ),
    ]
    cursor.close()

    assert tel.times_called == tel_called


@pytest.mark.parametrize(
    ['sleep_time_ms', 'enable_limiting', 'max_attempts', 'will_be_recalled'],
    (
        pytest.param(1000, False, 1000, True, id='check new eta'),
        pytest.param(1000, False, 0, True, id='check limiting disabled'),
        pytest.param(1000, True, 0, False, id='limiting enabled'),
    ),
)
@pytest.mark.now('2022-02-02 15:00:00.000')
async def test_stq_rescheduling(
        stq_runner,
        taxi_callcenter_queues,
        mockserver,
        stq,
        sleep_time_ms,
        enable_limiting,
        max_attempts,
        will_be_recalled,
        taxi_config,
):
    taxi_config.set_values(
        {
            'CALLCENTER_QUEUES_STQ_STATUS_CHANGER_RESCHEDULING_SETTINGS': {
                'sleep_time_ms': sleep_time_ms,
                'attempts_limit': max_attempts,
                'enable_attempts_limiting': enable_limiting,
            },
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    username = 'a'

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def _tel(request):
        assert username.lower() in request.path_qs.lower()
        return {**BAD_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}

    await stq_runner.callcenter_queues_status_changer.call(
        task_id=username, kwargs={'username': username}, expect_fail=False,
    )

    if will_be_recalled:
        assert stq.callcenter_queues_status_changer.times_called > 0
        stq_call = stq.callcenter_queues_status_changer.next_call()
        assert stq_call['eta'] == datetime.datetime(2022, 2, 2, 15, 0, 1, 0)
    else:
        assert not stq.callcenter_queues_status_changer.times_called


@pytest.mark.config(
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        's1': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's2': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's3': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
    },
    CALLCENTER_METAQUEUES=[
        {'allowed_clusters': ['s1', 's2'], 'name': 'disp', 'number': '840100'},
        {'allowed_clusters': ['s3'], 'name': 'corp', 'number': '840100'},
    ],
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
    CALLCENTER_QUEUES_STQ_STATUS_CHANGER_RESCHEDULING_SETTINGS={
        'sleep_time_ms': 100,
        'attempts_limit': 1000,
        'enable_attempts_limiting': False,
        'debug_mode': True,
    },
)
@pytest.mark.pgsql(
    'callcenter_queues',
    files=['insert_agent_with_changes.sql', 'insert_cc_system_info.sql'],
)
async def test_stq_debug_mode(stq_runner, taxi_callcenter_queues, mockserver):
    await taxi_callcenter_queues.invalidate_caches()
    username = 'a'

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert username.lower() in request.path_qs.lower()
        return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}

    await stq_runner.callcenter_queues_status_changer.call(
        task_id=username, kwargs={'username': username}, expect_fail=False,
    )
    assert not tel.times_called


@pytest.mark.config(
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        's1': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's2': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
        's3': {
            'endpoint': 'QPROC01',
            'endpoint_count': 1,
            'endpoint_strategy': 'TOPDOWN',
            'endpoint_strategy_option': 1,
            'timeout_sec': 180,
        },
    },
    CALLCENTER_METAQUEUES=[
        {'allowed_clusters': ['s1', 's2'], 'name': 'disp', 'number': '840100'},
        {'allowed_clusters': ['s3'], 'name': 'corp', 'number': '840100'},
    ],
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.pgsql(
    'callcenter_queues',
    files=['insert_agent_with_changes.sql', 'insert_cc_system_info.sql'],
)
@pytest.mark.parametrize(
    ['whitelist', 'times_called'], ((None, 1), (['a'], 1), (['b'], 0)),
)
async def test_stq_whitelist(
        stq_runner,
        taxi_callcenter_queues,
        mockserver,
        taxi_config,
        whitelist,
        times_called,
):
    taxi_config.set_values(
        {
            'CALLCENTER_QUEUES_STQ_STATUS_CHANGER_RESCHEDULING_SETTINGS': {
                'sleep_time_ms': 100,
                'attempts_limit': 100,
                'enable_attempts_limiting': False,
                'users_whitelist': whitelist,
            },
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    username = 'a'

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert username.lower() in request.path_qs.lower()
        return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}

    await stq_runner.callcenter_queues_status_changer.call(
        task_id=username, kwargs={'username': username}, expect_fail=False,
    )
    assert tel.times_called == times_called
