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
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_set_queues(taxi_callcenter_queues, pgsql):
    response = await taxi_callcenter_queues.post(
        '/v1/sip_user/queues',
        json={'metaqueues': ['ru_taxi_test'], 'sip_username': '123'},
    )
    assert response.status == 200

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """
       SELECT sip_username, metaqueues, updated_seq
        FROM callcenter_queues.target_queues;
       """,
    )
    result = cursor.fetchone()
    assert result == ('123', ['ru_taxi_test'], 1)


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
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_wanted_subcluster(taxi_callcenter_queues, pgsql):
    response = await taxi_callcenter_queues.post(
        '/v1/sip_user/queues',
        json={
            'metaqueues': ['ru_taxi_test'],
            'wanted_subcluster': '321',
            'sip_username': '123',
        },
    )
    assert response.status == 200

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """
       SELECT sip_username, wanted_subcluster
        FROM callcenter_queues.target_queues;
       """,
    )
    result = cursor.fetchone()
    assert result == ('123', '321')


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
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_set_queues_bad_queue(taxi_callcenter_queues, pgsql):
    response = await taxi_callcenter_queues.post(
        '/v1/sip_user/queues',
        json={'metaqueues': ['by_taxi_test'], 'sip_username': '123'},
    )
    assert response.status == 400
    res_json = response.json()
    assert res_json == {
        'code': 'unknown_metaqueue',
        'message': 'unknown metaqueues by_taxi_test',
    }


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
)
@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
async def test_set_queues_empty(taxi_callcenter_queues, pgsql):
    response = await taxi_callcenter_queues.post(
        '/v1/sip_user/queues', json={'metaqueues': [], 'sip_username': '123'},
    )
    assert response.status == 200
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        """
       SELECT sip_username, metaqueues, updated_seq
        FROM callcenter_queues.target_queues;
       """,
    )
    result = cursor.fetchone()
    assert result == ('123', [], 1)
