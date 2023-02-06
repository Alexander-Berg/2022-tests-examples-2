# pylint: disable=too-many-lines
import pytest

SUBCLUSTERS = {
    '1': {
        'endpoint': 'QPROC-s1',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 1,
    },
    '2': {
        'endpoint': 'QPROC-s2',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 2,
    },
    '3': {
        'endpoint': 'QPROC-reserve',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
    },
}
DEFAULT_METAQUEUES = [
    {
        'name': 'test',
        'number': '123',
        'allowed_clusters': ['1', '2', '3'],
        'tags': [],
    },
    {
        'name': 'work',
        'number': '123',
        'allowed_clusters': ['1', '2', '3'],
        'tags': [],
    },
]

BASE_TEL_RESPONSE = {
    'PARAM': {},
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSDESC': None,
    'STATUS': 'TRUE',
}

SIP_USERNAME = 'agent_1'


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=True,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_disconnect_with_cache(
        taxi_callcenter_queues, mockserver, pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.tel_state
        (
        sip_username,
        is_connected,
        is_paused,
        metaqueues,
        subcluster,
        is_valid
        )
        VALUES ('agent_1', true, true, '{test, work}', '1', true);""",
    )
    cursor.close()
    tel_times_called = {'disconnect': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'disconnect' in request.path_qs.lower():
            tel_times_called['disconnect'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'disconnected',
            'metaqueues': [],
        },
    )
    assert tel.times_called
    assert tel_times_called == {'disconnect': 1}
    assert response.status == 200
    assert response.json() == {
        'status': 'disconnected',
        'metaqueues': [],
        'sip_username': 'agent_1',
    }
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM callcenter_queues.tel_state;""")
    row = cursor.fetchall()[0]
    assert not row[1]  # is connected
    assert not row[2]  # is paused
    assert not row[3]  # queues


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=True,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_connect_with_cache(taxi_callcenter_queues, mockserver, pgsql):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.tel_state
        (
        sip_username,
        is_connected,
        is_paused,
        metaqueues,
        subcluster,
        is_valid
        )
        VALUES ('agent_1', false, false, '{}', Null, true);""",
    )
    cursor.close()
    tel_times_called = {'connect_wo_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if (
                'connect' in request.path_qs.lower()
                and '150/0' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_wo_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        # we need only queue names
        if 'show' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'connect_wo_pause': 1}
    assert response.status == 200
    assert response.json() == {
        'status': 'connected',
        'metaqueues': ['test', 'work'],
        'sip_username': 'agent_1',
        'subcluster': '2',
    }
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM callcenter_queues.tel_state;""")
    row = cursor.fetchall()[0]
    assert row[1]  # is connected
    assert not row[2]  # is paused
    assert set(row[3]) == {'test', 'work'}  # queues
    assert row[4] == '2'  # subcluster


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=True,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_pause_from_disconnect_with_cache(
        taxi_callcenter_queues, mockserver, pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.tel_state
        (
        sip_username,
        is_connected,
        is_paused,
        metaqueues,
        subcluster,
        is_valid
        )
        VALUES ('agent_1', false, false, '{}', Null, true);""",
    )
    cursor.close()
    tel_times_called = {'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if (
                'connect' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        # we need only queue names
        if 'show' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'connect_with_pause': 1}
    assert response.status == 200
    assert response.json() == {
        'status': 'paused',
        'metaqueues': ['test', 'work'],
        'sip_username': 'agent_1',
        'subcluster': '2',
    }
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM callcenter_queues.tel_state;""")
    row = cursor.fetchall()[0]
    assert row[1]  # is connected
    assert row[2]  # is paused
    assert set(row[3]) == {'test', 'work'}  # queues
    assert row[4] == '2'  # subcluster


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=True,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_pause_from_connect_with_cache(
        taxi_callcenter_queues, mockserver, pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.tel_state
        (
        sip_username,
        is_connected,
        is_paused,
        metaqueues,
        subcluster,
        is_valid
        )
        VALUES ('agent_1', true, false, '{test, work}', '2', true);""",
    )
    cursor.close()
    tel_times_called = {'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if (
                'changestatus' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'connect_with_pause': 1}
    assert response.status == 200
    assert response.json() == {
        'status': 'paused',
        'metaqueues': ['test', 'work'],
        'sip_username': 'agent_1',
        'subcluster': '2',
    }
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM callcenter_queues.tel_state;""")
    row = cursor.fetchall()[0]
    assert row[1]  # is connected
    assert row[2]  # is paused
    assert set(row[3]) == {'test', 'work'}  # queues
    assert row[4] == '2'  # subcluster


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=True,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_old_and_new_queues_mismatch(
        taxi_callcenter_queues, mockserver, pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    db = pgsql['callcenter_queues']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.tel_state
        (
        sip_username,
        is_connected,
        is_paused,
        metaqueues,
        subcluster,
        is_valid
        )
        VALUES ('agent_1', false, false, '{}', Null, true);""",
    )
    cursor.close()
    tel_times_called = {'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if (
                'connect' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'DATA': False, 'STATUSMSG': ''}
        # we need only queue names
        if 'show' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'connect_with_pause': 1}
    assert response.status == 200

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'connect_with_pause': 1}
    assert response.status == 400  # mismatch


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.now('2025-08-09 00:00:00.000Z')
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_disconnect_wo_cache_ok(taxi_callcenter_queues, mockserver):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'disconnect': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {
                    'CALLCENTERID': '1',
                    'QUEUES': {
                        'test_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                        'work_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                    },
                },
            }
        if 'disconnect' in request.path_qs.lower():
            assert 'test_on_1' in request.path_qs.lower()
            assert 'work_on_1' in request.path_qs.lower()
            tel_times_called['disconnect'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'disconnected',
            'metaqueues': [],  # it is not necessary
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 1, 'disconnect': 1}
    assert response.status == 200


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_connect_from_disconnect_wo_cache_ok(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_wo_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {'CALLCENTERID': '1', 'QUEUES': {}},
            }
        if (
                'connect' in request.path_qs.lower()
                and '150/0' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_wo_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 2, 'connect_wo_pause': 1}
    # one show for mvp handler
    assert response.status == 200


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_connect_from_pause_wo_cache_ok(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_wo_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {
                    'CALLCENTERID': '1',
                    'QUEUES': {
                        'test_on_2': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                        'work_on_2': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                    },
                },
            }
        if (
                'changestatus' in request.path_qs.lower()
                and '150/0' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_wo_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 1, 'connect_wo_pause': 1}
    assert response.status == 200


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_pause_from_disconnect_wo_cache_ok(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {'CALLCENTERID': '1', 'QUEUES': {}},
            }
        if (
                'connect' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 2, 'connect_with_pause': 1}
    # 1 in show for mvp handler
    assert response.status == 200


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_pause_from_connect_wo_cache_ok(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {
                    'CALLCENTERID': '1',
                    'QUEUES': {
                        'test_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '0',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                        'work_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '0',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                    },
                },
            }
        if (
                'changestatus' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_1' in request.path_qs.lower()
            assert 'work_on_1' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '1',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 1, 'connect_with_pause': 1}
    assert response.status == 200


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_unconsistent_queues_while_connect(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_wo_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {
                    'CALLCENTERID': '1',
                    'QUEUES': {
                        'test_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                        'work_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '1',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                    },
                },
            }
        if (
                'connect' in request.path_qs.lower()
                and '150/0' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_wo_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 1, 'connect_wo_pause': 0}
    assert response.status == 400


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_unconsistent_queues_while_pause(
        taxi_callcenter_queues, mockserver,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_with_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {
                    'CALLCENTERID': '1',
                    'QUEUES': {
                        'test_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '0',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                        'work_on_1': {
                            'STATUS': 1,
                            'VENDPAUSED': '0',
                            'PRIOR': 1,
                            'CURPRIOR': '1',
                        },
                    },
                },
            }
        if (
                'connect' in request.path_qs.lower()
                and '150/1' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_with_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'paused',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert tel_times_called == {'show': 1, 'connect_with_pause': 0}
    assert response.status == 400


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': True},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_bad_request(taxi_callcenter_queues, mockserver):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'default',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert response.status == 400


@pytest.mark.config(
    CALLCENTER_QUEUES_QUEUE_STATUS_TO_TEL_STATUS_MAPPING={
        '__default__': {'is_connected': False, 'is_paused': False},
        'connected': {'is_connected': True, 'is_paused': False},
        'paused': {'is_connected': True, 'is_paused': True},
        'disconnected': {'is_connected': False, 'is_paused': False},
    },
)
@pytest.mark.config(
    CALLCENTER_QUEUES_TEL_CACHE_ENABLER=False,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
async def test_metrics(
        taxi_callcenter_queues, mockserver, taxi_callcenter_queues_monitor,
):
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    tel_times_called = {'show': 0, 'connect_wo_pause': 0}

    @mockserver.json_handler('/yandex-tel', prefix=True)
    async def tel(request):
        assert SIP_USERNAME.lower() in request.path_qs.lower()
        if 'show' in request.path_qs.lower():
            tel_times_called['show'] += 1
            return {
                **BASE_TEL_RESPONSE,
                'STATUSMSG': 'SUCCESS',
                'DATA': {'CALLCENTERID': '1', 'QUEUES': {}},
            }
        if (
                'connect' in request.path_qs.lower()
                and '150/0' in request.path_qs.lower()
        ):
            assert 'test_on_2' in request.path_qs.lower()
            assert 'work_on_2' in request.path_qs.lower()
            tel_times_called['connect_wo_pause'] += 1
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        if 'mvp' in request.path_qs.lower():
            return {**BASE_TEL_RESPONSE, 'STATUSMSG': 'SUCCESS', 'DATA': {}}
        raise NotImplementedError

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.post(
        '/v2/sip_user/state',
        json={
            'sip_username': SIP_USERNAME,
            'status': 'connected',
            'metaqueues': ['test', 'work'],
            'subcluster': '2',
        },
    )
    assert tel.times_called
    assert response.status == 200
    metrics_response = await taxi_callcenter_queues_monitor.get('/')
    metrics = metrics_response.json()['tel-adapter']
    assert metrics['successful_select']['test']['2']  # add on this sub
    assert metrics['successful_select']['work']['2']  # and on this
    assert metrics['successful_select_wo_metaqueues']['2']

    await taxi_callcenter_queues.invalidate_caches()
    metrics_response = await taxi_callcenter_queues_monitor.get('/')
    metrics = metrics_response.json()['tel-adapter']
    assert not metrics['successful_select']['test']['2']  # cleared
    assert not metrics['successful_select']['work']['2']  # cleared
    assert not metrics['successful_select_wo_metaqueues']['2']
