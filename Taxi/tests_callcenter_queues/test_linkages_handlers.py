import pytest


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {
            'name': 'ru_taxi_test',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
        {
            'name': 'ru_taxi_help',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
    ],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        '99': {
            'endpoint': 'QPROC-s1',
            'endpoint_count': 2,
            'endpoint_strategy': 'TOPDOWN',
            'timeout_sec': 300,
            'endpoint_strategy_option': 1,
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['ru_taxi_help'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'test': {
            'metaqueues': ['ru_taxi_test'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_linkage_enabler(taxi_callcenter_queues, pgsql):
    await taxi_callcenter_queues.invalidate_caches()

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.callcenter_system_info
       (
       metaqueue,
       subcluster,
       enabled_for_call_balancing,
       enabled_for_sip_user_autobalancing,
       enabled
       )
       VALUES ('ru_taxi_test', '99', true, true, true);""",
    )

    # try to disable bad
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled': False,
        },
    )
    assert response.status == 409  # can't do it because other params are True

    # try to disable good
    cursor.execute(
        """
        UPDATE callcenter_queues.callcenter_system_info
       SET
       enabled_for_call_balancing = false,
       enabled_for_sip_user_autobalancing = false
       WHERE metaqueue = 'ru_taxi_test' AND subcluster = '99';""",
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled': False,
        },
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
           enabled_for_sip_user_autobalancing, enabled
           from callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (False, False, False)

    # linkage not found in db, but adding is ok for it
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_help',
            'subcluster': '99',
            'enabled': False,
        },
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
           enabled_for_sip_user_autobalancing, enabled
           from callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (False, False, False)

    # enable
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled': True,
        },
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
         enabled_for_sip_user_autobalancing, enabled from
          callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (False, False, True)
    cursor.close()

    # bad project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled': False,
            'project': 'help',
        },
    )
    assert response.status == 409
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
         enabled_for_sip_user_autobalancing, enabled from
          callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (False, False, True)
    cursor.close()

    # good project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/enabler/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled': False,
            'project': 'test',
        },
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
         enabled_for_sip_user_autobalancing, enabled from
          callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (False, False, False)
    cursor.close()


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {
            'name': 'ru_taxi_test',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
        {
            'name': 'ru_taxi_help',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
    ],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        '99': {
            'endpoint': 'QPROC-s1',
            'endpoint_count': 2,
            'endpoint_strategy': 'TOPDOWN',
            'timeout_sec': 300,
            'endpoint_strategy_option': 1,
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['ru_taxi_help'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'test': {
            'metaqueues': ['ru_taxi_test'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_linkage_params(taxi_callcenter_queues, pgsql):
    await taxi_callcenter_queues.invalidate_caches()

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.callcenter_system_info
       (
       metaqueue,
       subcluster,
       enabled_for_call_balancing,
       enabled_for_sip_user_autobalancing,
       enabled
       )
       VALUES ('ru_taxi_test', '99', false, false, false);""",
    )

    # bad state in db
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/params/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled_for_call_balancing': True,
            'enabled_for_sip_user_autobalancing': True,
        },
    )
    assert response.status == 409  # cause it is not enabled
    # try to change good
    cursor.execute(
        """
        UPDATE callcenter_queues.callcenter_system_info
       SET
              enabled = true
       WHERE metaqueue = 'ru_taxi_test' AND subcluster = '99';""",
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/params/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled_for_call_balancing': True,
            'enabled_for_sip_user_autobalancing': True,
        },
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """SELECT enabled_for_call_balancing,
         enabled_for_sip_user_autobalancing, enabled
          from callcenter_queues.callcenter_system_info
           WHERE metaqueue='ru_taxi_test' AND subcluster='99'""",
    )
    result = cursor.fetchone()
    assert result == (True, True, True)

    # bad state wo db
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/params/',
        json={
            'metaqueue': 'ru_taxi_help',
            'subcluster': '99',
            'enabled_for_call_balancing': True,
            'enabled_for_sip_user_autobalancing': True,
        },
    )
    assert response.status == 409

    # bad project
    cursor.execute(
        """
        UPDATE callcenter_queues.callcenter_system_info
       SET
              enabled = true
       WHERE metaqueue = 'ru_taxi_test' AND subcluster = '99';""",
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/params/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled_for_call_balancing': True,
            'enabled_for_sip_user_autobalancing': True,
            'project': 'help',
        },
    )
    assert response.status == 409

    # good project
    cursor.execute(
        """
        UPDATE callcenter_queues.callcenter_system_info
       SET
              enabled = true
       WHERE metaqueue = 'ru_taxi_test' AND subcluster = '99';""",
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/system/linkage/params/',
        json={
            'metaqueue': 'ru_taxi_test',
            'subcluster': '99',
            'enabled_for_call_balancing': True,
            'enabled_for_sip_user_autobalancing': True,
            'project': 'test',
        },
    )
    assert response.status == 200
    cursor.close()


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {
            'name': 'ru_taxi_test',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
        {
            'name': 'ru_taxi_help',
            'number': '123',
            'allowed_clusters': ['99'],
            'tags': [],
        },
    ],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        '99': {
            'endpoint': 'QPROC-s1',
            'endpoint_count': 2,
            'endpoint_strategy': 'TOPDOWN',
            'timeout_sec': 300,
            'endpoint_strategy_option': 1,
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['ru_taxi_help'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'test': {
            'metaqueues': ['ru_taxi_test'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_subcluster_info_holder_from_db(taxi_callcenter_queues, pgsql):
    await taxi_callcenter_queues.invalidate_caches()
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """INSERT INTO callcenter_queues.callcenter_system_info
       (
       metaqueue,
       subcluster,
       enabled_for_call_balancing,
       enabled_for_sip_user_autobalancing,
       enabled
       )
       VALUES ('ru_taxi_test', '99', true, true, true);""",
    )

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.get(
        '/tests/system-info-holder/get_info',
    )
    assert response.status == 200
    result = response.json()
    assert result == {
        'metaqueues_info': {
            'ru_taxi_test': {
                'subclusters': [
                    {
                        'enabled_for_call_balancing': True,
                        'enabled_for_sip_user_autobalancing': True,
                        'enabled': True,
                        'subcluster': '99',
                    },
                ],
            },
            'ru_taxi_help': {
                'subclusters': [
                    {
                        'enabled_for_call_balancing': False,
                        'enabled_for_sip_user_autobalancing': False,
                        'enabled': False,
                        'subcluster': '99',
                    },
                ],
            },
        },
        'subcluster_list': ['99'],
    }
    cursor.close()
