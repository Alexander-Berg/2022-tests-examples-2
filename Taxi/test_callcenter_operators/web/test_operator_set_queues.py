import pytest

from callcenter_operators import models
from test_callcenter_operators import test_utils


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_help', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test', 'test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test', 'test_help'],
                'subcluster': '1',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
            },
            {},
            200,
            id='ok request',
        ),
    ),
)
async def test_set_queues(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        pgsql,
):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    # uid1
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 1;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [models.TelState.PAUSED, 'tech', {'test', 'test_help'}]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 2;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [
        models.TelState.DISCONNECTED,
        None,
        {'test', 'test_help'},
    ]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 3;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [models.TelState.CONNECTED, None, {'test', 'test_help'}]

    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_help', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test', 'test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test', 'test_help'],
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
            },
            {},
            200,
            id='ok request',
        ),
    ),
)
async def test_set_queues_wo_subcluster(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mockserver,
        mock_save_status,
        pgsql,
        mock_callcenter_queues,
        mock_system_info,
):
    subcluster = '1'

    @mock_callcenter_queues('/v2/sip_user/state')
    async def _handle_set_state(request, *args, **kwargs):
        if request.method == 'GET':
            raise NotImplementedError
        req = request.json
        req['subcluster'] = subcluster
        return req

    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    # uid1
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 1;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [models.TelState.PAUSED, 'tech', {'test', 'test_help'}]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 2;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [
        models.TelState.DISCONNECTED,
        None,
        {'test', 'test_help'},
    ]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 3;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [models.TelState.CONNECTED, None, {'test', 'test_help'}]

    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_help', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test', 'test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {'metaqueues': [], 'yandex_uids': ['uid1', 'uid2', 'uid3']},
            {},
            200,
            id='ok request',
        ),
    ),
)
async def test_set_empty_queues(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        pgsql,
        mock_system_info,
):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    # uid1
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 1;',
    )
    record = list(cursor.fetchone())
    assert record == [models.TelState.DISCONNECTED, None, []]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 2;',
    )
    record = list(cursor.fetchone())
    assert record == [models.TelState.DISCONNECTED, None, []]

    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 3;',
    )
    record = list(cursor.fetchone())
    assert record == [models.TelState.DISCONNECTED, None, []]

    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_tel_handlers.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['ru_test', 'by_test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru', 'by'],
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'ru_test', 'allowed_clusters': ['1']},
        {'name': 'by_test_help', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_METAQUEUE_PREFIX_TO_SIP_DOMAIN={
        'ru': 'ru',
        'by': 'by',
        '__default__': 'ru',
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['ru_test', 'by_test_help'],
                'subcluster': '1',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
            },
            {
                'code': 'reg_groups_exception',
                'message': 'Too many reg groups from cc-reg',
            },
            400,
            id='sip_conflict',
        ),
    ),
)
async def test_set_queues_sip_conflict(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mockserver,
        mock_save_status,
        mock_system_info,
        mock_set_status_cc_queues,
        mock_callcenter_reg,
):
    @mock_callcenter_reg('/v1/reg_groups')
    async def _handle_urls(request, *args, **kwargs):
        return {
            'reg_groups': [
                {
                    'group_name': 'ru',
                    'regs': ['reg1', 'reg2'],
                    'reg_domain': 'yandex.ru',
                },
                {
                    'group_name': 'by',
                    'regs': ['reg3', 'reg4'],
                    'reg_domain': 'yandex.ru',
                },
            ],
        }

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[{'name': 'test', 'allowed_clusters': ['1']}],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_code', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test', 'test_help'],
                'subclsuter': '1',
                'yandex_uids': ['uid1'],
            },
            'metaqueue_not_found',
            400,
            id='bad queue name',
        ),
    ),
)
async def test_bad_set_queues(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_code,
        status,
        mock_telephony_api_full,
        mock_save_status,
        mock_system_info,
):

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    assert resp.status == status
    res_json = await resp.json()
    assert res_json['code'] == response_code


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_METAQUEUES=[{'name': 'test', 'allowed_clusters': ['1']}],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test'],
                'subcluster': '1',
                'yandex_uids': ['uid1'],
            },
            {
                'code': 'subcluster_not_exists',
                'message': 'Subcluster 1 not exists',
            },
            400,
            id='bad subcluster',
        ),
    ),
)
async def test_bad_cluster(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mock_telephony_api_full,
        mock_save_status,
        mock_callcenter_queues,
        taxi_config,
):
    @mock_callcenter_queues('/v1/queues/list')
    async def _handle_urls(request, *args, **kwargs):
        metaqueues = list()
        subclusters = ['10']  # fill it earlier
        queues = list()
        for item in taxi_config.get('CALLCENTER_METAQUEUES'):
            metaqueues.append(item['name'])
            queues_item = {'metaqueue': item['name'], 'subclusters': list()}
            for subcluster in item['allowed_clusters']:
                queues_item['subclusters'].append(
                    {
                        'name': subcluster,
                        'enabled_for_call_balancing': True,
                        'enabled_for_sip_users_balancing': True,
                        'enabled': True,
                    },
                )
            queues.append(queues_item)
        metaqueues = list(set(metaqueues))
        return {
            'metaqueues': metaqueues,
            'subclusters': subclusters,
            'queues': queues,
            'enabled': True,
        }

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_help', 'allowed_clusters': ['2']},
    ],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test', 'test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_code', 'status'],
    (
        pytest.param(
            {'metaqueues': ['test', 'test_help'], 'yandex_uids': ['uid1']},
            'no_common_subcluster',
            400,
            id='no common clusters',
        ),
    ),
)
async def test_no_common_cluster(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_code,
        status,
        mock_telephony_api_full,
        mock_save_status,
        mock_system_info,
):
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    assert resp.status == status
    res_json = await resp.json()
    assert res_json['code'] == response_code


@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test'],
                'subcluster': '1',
                'yandex_uids': ['uid1', 'uid2'],
                'project': 'test',
            },
            {},
            200,
            id='ok set on project queues',
        ),
        pytest.param(
            {
                'metaqueues': ['test', 'test_help'],
                'subcluster': '1',
                'yandex_uids': ['uid3'],
                'project': 'test',
            },
            {
                'code': 'project_mismatch',
                'message': 'Your project: test and metaqueues_project: common',
            },
            400,
            id='NOT ok set multi-project queues',
        ),
        pytest.param(
            {
                'metaqueues': ['test_help'],
                'subcluster': '1',
                'yandex_uids': ['uid3'],
                'project': 'test',
            },
            {
                'code': 'project_mismatch',
                'message': (
                    'Your project: test and metaqueues_project: test_help'
                ),
            },
            400,
            id='NOT ok req project and queues project doesnt match',
        ),
    ),
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_tel_handlers.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'test_help': {
            'metaqueues': ['test_help'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'test': {
            'metaqueues': ['test'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1', '2']},
        {'name': 'test_help', 'allowed_clusters': ['1']},
    ],
)
async def test_project_set_queues(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    def _tel_handle(request):
        return test_utils.make_tel_response()

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )

    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.config(
    CALLCENTER_METAQUEUES=[{'name': 'test', 'allowed_clusters': ['1']}],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test'],
                'subcluster': '1',
                'yandex_uids': [
                    'uid1',
                    'uid2',
                    'uid3',
                    'uid4',
                    'uid5',
                    'uid6',
                    'uid7',
                    'uid8',
                    'uid9',
                    'uid10',
                    'uid11',
                ],
            },
            {
                'code': 'bad_limit',
                'message': 'Requested changes: 11, limit: 10',
            },
            400,
        ),
    ),
)
async def test_set_queues_operators_limitation(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mock_system_info,
):

    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )

    assert resp.status == status
    assert await resp.json() == response_data


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_USE_NEW_DATA=True,
    CALLCENTER_METAQUEUES=[
        {'name': 'test', 'allowed_clusters': ['1']},
        {'name': 'test_help', 'allowed_clusters': ['1']},
    ],
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['test', 'test_help'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
@pytest.mark.parametrize(
    ['request_data', 'response_data', 'status'],
    (
        pytest.param(
            {
                'metaqueues': ['test', 'test_help'],
                'subcluster': '1',
                'yandex_uids': ['uid1'],
            },
            {},
            200,
            id='ok request',
        ),
    ),
)
async def test_set_queues_new(
        taxi_callcenter_operators_web,
        web_context,
        request_data,
        response_data,
        status,
        mock_save_queues,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        pgsql,
):
    resp = await taxi_callcenter_operators_web.post(
        '/cc/v1/callcenter-operators/v1/set_queues', json=request_data,
    )
    # check locally saved
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status, sub_status, metaqueues'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = 1;',
    )
    record = list(cursor.fetchone())
    record[2] = set(record[2])
    assert record == [models.TelState.PAUSED, 'tech', {'test', 'test_help'}]

    assert resp.status == status
    assert await resp.json() == response_data

    # check old handler disabled
    assert not mock_set_status_cc_queues.handle_urls.times_called
    # check cc-stats save history enabled
    assert mock_save_status.handle_urls.times_called
    # check save queues in cc-queues enabled
    assert mock_save_queues.handle_urls.times_called
