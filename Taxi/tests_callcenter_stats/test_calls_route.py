# pylint: disable=C0302

import logging
import urllib.parse

from aiohttp import web
import pytest

logger = logging.getLogger(__name__)

ENDPOINT = '/v1/calls/route/'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
SUBCLUSTERS = {
    's1': {
        'endpoint': 'QPROC-s1',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 1,
    },
    's2': {
        'endpoint': 'QPROC-s2',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 2,
    },
    'reserve': {
        'endpoint': 'QPROC-reserve',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
    },
}
DEFAULT_METAQUEUES = [
    {
        'name': 'disp',
        'number': '123',
        'allowed_clusters': ['s1', 's2', 'broken_cluster'],
        'disabled_clusters': {
            'disabled_for_routing': ['broken_cluster', 'unknown_cluster'],
        },
        'tags': ['check_active_order'],
    },
]


def dial(number='123', status=False):
    return {
        'ACTION': 'DIAL',
        'PARAMS': {
            'IGNORESTATUS': status,
            'TIMEOUT': 300,
            'ROUTE': 'GLOBAL_ROUTING',
        },
        'VALUE': f'GLOBAL/{number}',
    }


@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74959999991': {
            'metaqueue': 'queue1',
            'queue_project_key': 'phone_map_key1',
        },
        '+74959999992': {
            'metaqueue': 'queue2',
            'queue_project_key': 'phone_map_key2',
            'queue_route': 'phone_map_route2',
        },
        '+74959999993': {
            'metaqueue': 'queue2',
            'queue_route': 'phone_map_route3',
        },
        '+74959999994': {'metaqueue': 'queue3'},
    },
    CALLCENTER_STATS_ROUTING_EMERGENCY_MODE={'mode': 'auto'},
    CALLCENTER_METAQUEUES=[
        {'name': 'queue1', 'number': '111', 'allowed_clusters': ['s1']},
        {
            'name': 'queue2',
            'number': '222',
            'queue_project_key': 'queue2_key',
            'allowed_clusters': ['s1'],
        },
        {
            'name': 'queue3',
            'number': '333',
            'queue_project_key': 'queue3_key',
            'queue_route': 'queue3_route',
            'allowed_clusters': ['s1'],
        },
        {
            'name': 'queue4',
            'number': '444',
            'queue_project_key': 'queue4_key',
            'allowed_clusters': ['s1'],
        },
        {
            'name': 'queue5',
            'number': '555',
            'queue_project_key': 'queue5_key',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
)
@pytest.mark.parametrize(
    [
        'called_num',
        'called_dn',
        'exp_file',
        'expected_key',
        'expected_route',
        'expected_queue_number',
    ],
    (
        pytest.param(
            '+74959999991',
            '+74959999991',
            None,
            'phone_map_key1',
            'phone_map_key1',
            'GLOBAL/111',
            id='phone map key',
        ),
        pytest.param(
            '+74959999992',
            '+74959999992',
            None,
            'phone_map_key2',
            'phone_map_route2',
            'GLOBAL/222',
            id='phone map and metaqueue keys',
        ),
        pytest.param(
            '+74959999993',
            '+74959999993',
            None,
            'queue2_key',
            'phone_map_route3',
            'GLOBAL/222',
            id='metaqueue key',
        ),
        pytest.param(
            '+74959999994',
            '333',
            None,
            'queue3_key',
            'queue3_route',
            'GLOBAL/333',
            id='not direct external',
        ),
        pytest.param(
            '+74959999994',
            '+74959999994',
            'exp3_phone_routing_push_metaqueue.json',
            'queue4_key',
            'queue4_key',
            'GLOBAL/444',
            id='exp3 push metaqueue',
        ),
        pytest.param(
            '+74959999994',
            '+74959999994',
            'exp3_phone_routing_config_push_metaqueue.json',
            'queue5_key',
            'queue5_key',
            'GLOBAL/555',
            id='exp3 config push metaqueue',
        ),
    ),
)
async def test_queue_project_key_and_route(
        taxi_callcenter_stats,
        called_num,
        called_dn,
        exp_file,
        expected_key,
        expected_route,
        expected_queue_number,
        mock_personal,
        experiments3,
        load_json,
):
    if exp_file:
        experiments3.add_experiments_json(load_json(exp_file))
        await taxi_callcenter_stats.invalidate_caches()

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid_1',
                'ORIGINAL_DN': called_num,
                'CALLED_DN': called_dn,
                'CALLERID': '+79991111111',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    assert queue_action['0']['PARAM'] == 'PROJECTKEY'
    assert queue_action['0']['VALUE'] == expected_key
    assert queue_action['1']['PARAM'] == 'Route'
    assert queue_action['1']['VALUE'] == expected_route
    assert queue_action['2']['ACTION'] == 'DIAL'
    assert queue_action['2']['VALUE'] == expected_queue_number


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
)
@pytest.mark.pgsql('callcenter_stats', files=['insert_agents_emergency.sql'])
@pytest.mark.parametrize(
    ['called_phone_number', 'expected_code', 'expected_queue_number'],
    (
        pytest.param(
            '+74959999999',
            200,
            'GLOBAL/123',
            id='normal route',
            marks=pytest.mark.config(
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '__default__': {'metaqueue': 'cargo'},
                    '+74959999999': {'metaqueue': 'disp'},
                },
            ),
        ),
        pytest.param(
            '+74959999999',
            200,
            'GLOBAL/123',
            id='switch to __default__',
            marks=pytest.mark.config(
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '__default__': {'metaqueue': 'disp'},
                    '+74959999994': {'metaqueue': 'cargo'},
                },
            ),
        ),
        pytest.param(
            '+74959999999',
            500,
            'GLOBAL/123',
            id='no route at all',
            marks=pytest.mark.config(
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '+74959999994': {'metaqueue': 'cargo'},
                },
            ),
        ),
    ),
)
async def test_queue_routing(
        taxi_callcenter_stats,
        called_phone_number,
        expected_code,
        expected_queue_number,
        mock_callcenter_queues,
        mock_personal,
        mockserver,
):
    @mockserver.json_handler('/ivr-dispatcher/has_order_status')
    def _has_order_status(request):
        return {'has_order_status': False}

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid_1',
                'ORIGINAL_DN': f'{called_phone_number}',
                'CALLED_DN': f'{called_phone_number}',
                'CALLERID': '+79991111111',
            },
        ),
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0']
        assert queue_action['ACTION'] == 'DIAL'
        assert queue_action['VALUE'] == expected_queue_number


@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={'__default__': {'metaqueue': 'disp'}},
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    IVR_SETTINGS={
        'application_settings': {
            'test_call_center': {
                'has_order_status': True,
                'gateway_settings': {},
                'locale': 'ru',
                'sms_settings': {
                    'intent': 'intent',
                    'sender': 'go',
                    'sms_enabled': True,
                },
            },
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_DIAL_TIMEOUT_MAP={
        'order_status_worker_number': 180,
    },
)
@pytest.mark.pgsql('callcenter_stats', files=['insert_agents_3_2.sql'])
@pytest.mark.parametrize(
    ('caller_id', 'expected_action'),
    [
        pytest.param('+5678', dial(), id='no_order'),
        pytest.param(
            '+1234',
            {
                'ACTION': 'DIAL',
                'VALUE': 'GLOBAL/order_status_worker_number',
                'PARAMS': {
                    'IGNORESTATUS': False,
                    'TIMEOUT': 180,
                    'ROUTE': 'GLOBAL_ROUTING',
                },
            },
            id='has_order',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_ivr_routing.json')
async def test_ivr_route(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        mock_callcenter_queues,
        caller_id,
        expected_action,
        experiments3,
):
    @mockserver.json_handler('/ivr-dispatcher/has_order_status')
    def _has_order_status(request):
        assert request.json['call_guid'] == 'call_guid', request.json
        assert (
            request.json['origin_called_number'] == '+74959999999'
        ), request.json
        assert request.json['personal_phone_id'] == caller_id + '_id'
        return {
            'has_order_status': (
                request.json['personal_phone_id'] == '+1234_id'
            ),
        }

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74959999999',
                'CALLED_DN': '+74959999999',
                'CALLERID': caller_id,
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0']
    assert action == expected_action


@pytest.mark.config(
    CALLCENTER_STATS_ROUTING_PHONE_MAP={'__default__': {'metaqueue': 'disp'}},
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    IVR_SETTINGS={
        'application_settings': {
            'test_call_center': {
                'has_order_status': True,
                'gateway_settings': {},
                'locale': 'ru',
                'sms_settings': {
                    'intent': 'intent',
                    'sender': 'go',
                    'sms_enabled': True,
                },
            },
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_DIAL_TIMEOUT_MAP={
        'order_status_worker_number': 180,
    },
)
@pytest.mark.parametrize(
    'has_tag',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['s1', 's2', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': [
                                'broken_cluster',
                                'unknown_cluster',
                            ],
                        },
                        'tags': [],
                    },
                ],
            ),
            id='without tag',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES),
            id='with tag',
        ),
    ],
)
@pytest.mark.parametrize(
    'has_order',
    [pytest.param(True, id='has_order'), pytest.param(False, id='no_order')],
)
@pytest.mark.experiments3(filename='exp3_ivr_routing.json')
async def test_ivr_route2(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        mock_callcenter_queues,
        experiments3,
        has_tag,
        has_order,
):
    @mockserver.json_handler('/ivr-dispatcher/has_order_status')
    def _has_order_status(request):
        return {'has_order_status': has_order}

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74959999999',
                'CALLED_DN': '+74959999999',
                'CALLERID': '+79872676410',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    redirect_action = {
        'ACTION': 'DIAL',
        'VALUE': 'GLOBAL/order_status_worker_number',
        'PARAMS': {
            'IGNORESTATUS': False,
            'TIMEOUT': 180,
            'ROUTE': 'GLOBAL_ROUTING',
        },
    }
    action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0']
    assert (action == redirect_action) == (has_order and has_tag)


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'tags': ['detect_newbies'],
            'allowed_clusters': ['s1'],
        },
        {'name': 'newbie_queue', 'number': '+7', 'allowed_clusters': ['s1']},
    ],
    CALLCENTER_NEWBIES_RIDES_NUMBER=6,
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74999999999': {
            'application': 'call_center',
            'city_name': 'Moscow',
            'country': 'rus',
            'geo_zone_coords': {'lat': 0.0, 'lon': 0.0},
        },
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.experiments3(filename='exp3_phone_routing.json')
@pytest.mark.parametrize(
    ['user_rides_number', 'expected_queue_number'],
    (
        pytest.param(4, 'GLOBAL/+7', id='newbie'),
        pytest.param(7, 'GLOBAL/+74999999999', id='mature'),
    ),
)
async def test_newbie_redirection(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        user_rides_number,
        expected_queue_number,
        experiments3,
        mock_callcenter_queues,
):
    @mockserver.json_handler('/user-statistics/v1/orders')
    async def orders_handle(request):
        assert request.json['identities'][0]['type'] == 'phone_id'
        assert request.json['identities'][0]['value'] == '+1234_up_id'
        assert request.json['filters'][0]['name'] == 'brand'
        assert request.json['filters'][0]['values'][0] == 'yataxi'
        return {
            'data': [
                {
                    'identity': {'type': 'phone_id', 'value': '+1234_up_id'},
                    'counters': [
                        {
                            'properties': [
                                {'name': 'brand', 'value': 'yataxi'},
                            ],
                            'value': user_rides_number,
                            'counted_from': '2021-04-22T09:00:00+0000',
                            'counted_to': '2021-10-01T09:00:00+0000',
                        },
                    ],
                },
            ],
        }

    exp3_recorder = experiments3.record_match_tries('cc_stats_phone_routing')

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    assert orders_handle.times_called == 1
    data = response.json()
    queue_number = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0'][
        'VALUE'
    ]
    assert queue_number == expected_queue_number
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['phone_pd_id'] == '+1234_id'


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.experiments3(filename='exp3_phone_routing_playback.json')
async def test_playback_and_hangup(
        taxi_callcenter_stats,
        mock_callcenter_queues,
        mockserver,
        mock_personal,
):
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '0': {'ACTION': 'ANSWER', 'VALUE': 0},
        '1': {
            'ACTION': 'APP',
            'PARAMS': {'PROJECT': 'YANDEX_TAXI', 'CONTENT': 'test_sound'},
            'VALUE': 'APPL_PLAYBACK',
        },
        '2': {'ACTION': 'HANGUP', 'VALUE': '16'},
    }
    assert action == expected_action


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.parametrize(
    ['exp_result', 'expected_testpoint_data', 'expected_action'],
    (
        pytest.param(
            {'push_to_metaqueue': 'metaqueue', 'redirect_to_phone': '+1234'},
            {
                'from': 'cc_stats_phone_routing',
                'exp_count': 2,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': '',
            },
            None,
            id='bad result 1+2',
        ),
        pytest.param(
            {
                'push_to_metaqueue': 'metaqueue',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing',
                'exp_count': 2,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 1+3',
        ),
        pytest.param(
            {
                'redirect_to_phone': '+1234',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing',
                'exp_count': 2,
                'push_to_metaqueue': '',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 2+3',
        ),
        pytest.param(
            {
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing',
                'exp_count': 3,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 1+2+3',
        ),
        pytest.param(
            {
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                    'code': '21',
                },
            },
            None,
            {
                '0': {'ACTION': 'ANSWER', 'VALUE': 0},
                '1': {
                    'ACTION': 'APP',
                    'PARAMS': {
                        'PROJECT': 'YANDEX_TAXI',
                        'CONTENT': 'test_sound',
                    },
                    'VALUE': 'APPL_PLAYBACK',
                },
                '2': {'ACTION': 'HANGUP', 'VALUE': '21'},
            },
            id='with hangup code',
        ),
    ),
)
async def test_exp3_phone_routing_result(
        taxi_callcenter_stats,
        experiments3,
        load_json,
        testpoint,
        exp_result,
        expected_testpoint_data,
        expected_action,
        mockserver,
        mock_personal,
        mock_callcenter_queues,
):
    @testpoint('exp-routing-error')
    def exp_routing_error(data):
        nonlocal expected_testpoint_data
        assert data == expected_testpoint_data

    exp_json = load_json('exp3_phone_routing_playback.json')
    exp_json['experiments'][0]['clauses'][0]['value'] = exp_result
    experiments3.add_experiments_json(exp_json)
    await taxi_callcenter_stats.invalidate_caches()
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    if expected_testpoint_data:
        assert exp_routing_error.times_called == 1
    if expected_action:
        data = response.json()
        action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
        assert action == expected_action


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.parametrize(
    ['exp_result', 'expected_testpoint_data', 'expected_action'],
    (
        pytest.param(
            {'push_to_metaqueue': 'metaqueue', 'redirect_to_phone': '+1234'},
            {
                'from': 'cc_stats_phone_routing_config',
                'exp_count': 2,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': '',
            },
            None,
            id='bad result 1+2',
        ),
        pytest.param(
            {
                'push_to_metaqueue': 'metaqueue',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing_config',
                'exp_count': 2,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 1+3',
        ),
        pytest.param(
            {
                'redirect_to_phone': '+1234',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing_config',
                'exp_count': 2,
                'push_to_metaqueue': '',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 2+3',
        ),
        pytest.param(
            {
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            {
                'from': 'cc_stats_phone_routing_config',
                'exp_count': 3,
                'push_to_metaqueue': 'metaqueue',
                'redirect_to_phone': '+1234',
                'playback_and_hangup': 'YANDEX_TAXI/test_sound/16',
            },
            None,
            id='bad result 1+2+3',
        ),
        pytest.param(
            {
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                    'code': '21',
                },
            },
            None,
            {
                '0': {'ACTION': 'ANSWER', 'VALUE': 0},
                '1': {
                    'ACTION': 'APP',
                    'PARAMS': {
                        'PROJECT': 'YANDEX_TAXI',
                        'CONTENT': 'test_sound',
                    },
                    'VALUE': 'APPL_PLAYBACK',
                },
                '2': {'ACTION': 'HANGUP', 'VALUE': '21'},
            },
            id='with hangup code',
        ),
        pytest.param(
            {
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            None,
            {
                '0': {'ACTION': 'ANSWER', 'VALUE': 0},
                '1': {
                    'ACTION': 'APP',
                    'PARAMS': {
                        'PROJECT': 'YANDEX_TAXI',
                        'CONTENT': 'test_sound',
                    },
                    'VALUE': 'APPL_PLAYBACK',
                },
                '2': {'ACTION': 'HANGUP', 'VALUE': '16'},
            },
            id='without hangup code',
        ),
    ),
)
async def test_exp3_phone_routing_config_result(
        taxi_callcenter_stats,
        experiments3,
        load_json,
        testpoint,
        exp_result,
        expected_testpoint_data,
        expected_action,
        mockserver,
        mock_personal,
        mock_callcenter_queues,
):
    @testpoint('exp-routing-error')
    def exp_routing_error(data):
        nonlocal expected_testpoint_data
        assert data == expected_testpoint_data

    exp_json = load_json('exp3_phone_routing_config_playback.json')
    exp_json['configs'][0]['clauses'][0]['value'] = exp_result
    experiments3.add_experiments_json(exp_json)
    await taxi_callcenter_stats.invalidate_caches()
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    if expected_testpoint_data:
        assert exp_routing_error.times_called == 1
    if expected_action:
        data = response.json()
        action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
        assert action == expected_action


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'tags': ['detect_corps'],
            'allowed_clusters': ['s1'],
        },
        {'name': 'corp_queue', 'number': '+7', 'allowed_clusters': ['s1']},
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74999999999': {
            'application': 'call_center',
            'city_name': 'Moscow',
            'country': 'rus',
            'geo_zone_coords': {'lat': 0.0, 'lon': 0.0},
        },
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.parametrize(
    ['payment_type', 'zone_available', 'expected_queue_number'],
    (
        pytest.param('corp', True, 'GLOBAL/+7', id='corp'),
        pytest.param(
            None, None, 'GLOBAL/+74999999999', id='bad paymentmethods',
        ),
        pytest.param(
            'corp', False, 'GLOBAL/+74999999999', id='zone unavailable',
        ),
    ),
)
@pytest.mark.experiments3(filename='exp3_phone_routing.json')
async def test_corp_redirection(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        experiments3,
        payment_type,
        zone_available,
        expected_queue_number,
        mock_callcenter_queues,
):
    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def _paymentmethods_handler(request):
        if payment_type is None:
            return web.Response(status=500)
        return {
            'methods': [
                {
                    'type': payment_type,
                    'id': 'corp-<uuid>',
                    'label': 'Команда яндекс такси',
                    'description': 'Осталось 123 из 6000 руб.',
                    'cost_center': 'TAXI',
                    'cost_centers': {
                        'required': False,
                        'format': 'text',
                        'values': [],
                    },
                    'client_comment': '',
                    'currency': 'RUB',
                    'classes_available': [],
                    'hide_user_cost': False,
                    'can_order': False,
                    'order_disable_reason': 'Недостаточно средств на счете',
                    'zone_available': zone_available,
                    'zone_disable_reason': 'Нельзя кататься в другой стране',
                },
            ],
        }

    exp3_recorder = experiments3.record_match_tries('cc_stats_phone_routing')

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    queue_number = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0'][
        'VALUE'
    ]
    assert queue_number == expected_queue_number
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['phone_pd_id'] == '+1234_id'


@pytest.mark.config(CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS)
@pytest.mark.pgsql('callcenter_stats', files=['insert_agents_3_2.sql'])
@pytest.mark.parametrize(
    ['expected_code', 'expected_action', 'expected_metrics', 'exp_result'],
    (
        pytest.param(
            200,
            {'0': dial()},
            {'routing_by_metaqueue': {'disp': {'1min': {'normal': 1}}}},
            None,
            id='route to metaqueue',
            marks=pytest.mark.config(
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '__default__': {'metaqueue': 'disp'},
                },
                CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
            ),
        ),
        pytest.param(
            200,
            {'0': dial()},
            {
                'routing_by_metaqueue': {'disp': {'1min': {'normal': 1}}},
                'deprecated_calls': {
                    '+74959999999': {'+74999999999': {'1min': 1}},
                },
            },
            None,
            id='deprecated calls metrics',
            marks=pytest.mark.config(
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '__default__': {'metaqueue': 'disp'},
                },
                CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
            ),
        ),
        pytest.param(
            200,
            {'0': dial('999')},
            {'routing_by_numbers': {'999': {'1min': {'normal': 1}}}},
            None,
            id='route to number',
            marks=[
                pytest.mark.config(
                    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
                    CALLCENTER_STATS_ROUTING_DIAL_TIMEOUT_MAP={'999': 300},
                    CALLCENTER_STATS_ROUTING_PHONE_MAP={
                        '__default__': {'metaqueue': 'disp'},
                    },
                ),
                pytest.mark.experiments3(
                    filename='exp3_call_routing_for_metrics.json',
                ),
            ],
        ),
        pytest.param(
            200,
            {
                '0': {'ACTION': 'ANSWER', 'VALUE': 0},
                '1': {
                    'ACTION': 'APP',
                    'PARAMS': {
                        'PROJECT': 'YANDEX_TAXI',
                        'CONTENT': 'test_sound',
                    },
                    'VALUE': 'APPL_PLAYBACK',
                },
                '2': {'ACTION': 'HANGUP', 'VALUE': '16'},
            },
            {
                'playback': {
                    'YANDEX_TAXI': {'test_sound': {'1min': {'normal': 1}}},
                },
            },
            {
                'playback_and_hangup': {
                    'project': 'YANDEX_TAXI',
                    'record': 'test_sound',
                },
            },
            id='playback',
            marks=pytest.mark.config(
                CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp_test',
                        'number': '+74959999999',
                        'allowed_clusters': ['s1'],
                    },
                ],
                CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
                    '__default__': {
                        'application': 'test_call_center',
                        'city_name': 'Неизвестен',
                        'geo_zone_coords': {'lat': 0, 'lon': 0},
                    },
                },
                CALLCENTER_STATS_ROUTING_PHONE_MAP={
                    '+74959999999': {'metaqueue': 'disp_test'},
                },
            ),
        ),
    ),
)
async def test_metrics(
        taxi_callcenter_stats,
        testpoint,
        expected_code,
        expected_action,
        expected_metrics,
        exp_result,
        experiments3,
        load_json,
        mockserver,
        mock_personal,
):
    @mockserver.json_handler('/ivr-dispatcher/has_order_status')
    def _has_order_status(request):
        return {'has_order_status': False}

    @mockserver.json_handler('/callcenter-queues/v1/queues/list')
    async def _queues_list_handle(request):
        return {
            'queues': [
                {
                    'metaqueue': 'disp',
                    'subclusters': [
                        {
                            'name': 's1',
                            'enabled_for_call_balancing': True,
                            'enabled_for_sip_users_balancing': True,
                            'enabled': True,
                        },
                        {
                            'name': 's2',
                            'enabled_for_call_balancing': True,
                            'enabled_for_sip_users_balancing': True,
                            'enabled': True,
                        },
                        {
                            'name': 'broken_subcluster',
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                        },
                    ],
                },
            ],
            'subclusters': ['s1', 's2', 'broken_subcluster'],
            'metaqueues': ['disp'],
        }

    exp_json = load_json('exp3_phone_routing_config_playback.json')
    exp_json['configs'][0]['clauses'][0]['value'] = exp_result
    experiments3.add_experiments_json(exp_json)
    await taxi_callcenter_stats.invalidate_caches()

    metrics_before = {}
    metrics_after = {}

    @testpoint('call-routing-started')
    def call_routing_started(data):
        nonlocal metrics_before
        metrics_before = data

    @testpoint('call-routing-finished')
    def call_routing_finished(data):
        nonlocal metrics_after
        metrics_after = data

    # Make zero for 999
    await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid_0',
                'ORIGINAL_DN': '+74959999999',
                'CALLED_DN': '+74959999999',
                'CALLERID': '+7',
            },
        ),
    )

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid_10',
                'ORIGINAL_DN': '+74959999999',
                'CALLED_DN': '+74959999999',
                'CALLERID': '+79991111111',
            },
        ),
    )

    await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid_10',
                'ORIGINAL_DN': '+74959999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+79991111111',
            },
        ),
    )

    # get subtree by template
    def filter_tree(data, tmpl):
        if not isinstance(data, dict):
            return data

        res = dict()
        for x in data:
            if x in tmpl:
                res[x] = filter_tree(data[x], tmpl[x])
        return res

    # subtract one tree from another
    def subtract_tree(data1, data2):
        assert isinstance(data1, type(data2))
        if not isinstance(data1, dict):
            return data1 - data2

        res = dict()
        for x in data1:
            assert x in data2
            res[x] = subtract_tree(data1[x], data2[x])
        return res

    # Check answer
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        result_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
        assert result_action == expected_action

    # Check metrics
    assert call_routing_started.has_calls
    assert call_routing_finished.has_calls
    metrics_before = filter_tree(metrics_before, expected_metrics)
    metrics_after = filter_tree(metrics_after, expected_metrics)
    metrics = subtract_tree(metrics_after, metrics_before)
    assert metrics == expected_metrics


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
            'tags': ['check_user_tags'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
    CALLCENTER_STATS_PASSENGER_TAGS_TO_ATTRIBUTES_MAP={
        'cashrunner': 'antifraud_cashrunner_block_cash',
    },
)
@pytest.mark.experiments3(filename='exp3_phone_routing_check_tags.json')
async def test_cashrunner_block(
        taxi_callcenter_stats, mockserver, mock_personal,
):
    @mockserver.json_handler('/passenger-tags/v3/match_single')
    async def passenger_tags_handler(request):
        return {'tags': {'cashrunner': {}}}

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    assert passenger_tags_handler.times_called == 1
    data = response.json()
    action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '0': {'ACTION': 'ANSWER', 'VALUE': 0},
        '1': {
            'ACTION': 'APP',
            'PARAMS': {'PROJECT': 'YANDEX_TAXI', 'CONTENT': 'test_sound'},
            'VALUE': 'APPL_PLAYBACK',
        },
        '2': {'ACTION': 'HANGUP', 'VALUE': '21'},
    }
    assert action == expected_action


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={},
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
)
@pytest.mark.experiments3(filename='exp3_phone_routing_check_tags.json')
async def test_cannot_parse_metaqueue(
        taxi_callcenter_stats, mockserver, mock_personal,
):
    await taxi_callcenter_stats.invalidate_caches()
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '0': {'ACTION': 'ANSWER', 'VALUE': 0},
        '1': {
            'ACTION': 'APP',
            'PARAMS': {
                'PROJECT': 'YANDEX_TAXI',
                'CONTENT': 'unknown_callcenter_number',
            },
            'VALUE': 'APPL_PLAYBACK',
        },
        '2': {'ACTION': 'HANGUP', 'VALUE': '21'},
    }
    assert action == expected_action


@pytest.mark.now('2022-01-14T00:00:00')
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
            'tags': ['check_comfort_upsell'],
        },
        {
            'name': 'comfort_queue',
            'number': 'comfort_queue',
            'allowed_clusters': ['s1'],
        },
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
    CALLCENTER_STATS_USER_STATS_SETTINGS_FOR_FETCHING_UPSELL={
        'tariffs': [
            'business',
            'comfortplus',
            'econom',
            'maybach',
            'ultimate',
            'vip',
        ],
        'brands': ['yataxi'],
    },
)
@pytest.mark.parametrize(
    ['comfort_rides_number', 'econom_rides_number', 'expected_queue_number'],
    (
        pytest.param(7, 5, 'GLOBAL/comfort_queue', id='comfort upsell'),
        pytest.param(5, 10, 'GLOBAL/+74999999999', id='not comfort upsell'),
        pytest.param(
            0, 0, 'GLOBAL/comfort_queue', id='comfort upsell (zero orders)',
        ),
    ),
)
@pytest.mark.experiments3(filename='exp3_phone_routing_comfort_upsell.json')
async def test_comfort_upsell(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        comfort_rides_number,
        econom_rides_number,
        expected_queue_number,
):
    @mockserver.json_handler('/user-statistics/v1/recent-orders')
    async def orders_handle(request):
        assert request.json['identities'][0]['type'] == 'phone_id'
        assert request.json['identities'][0]['value'] == '+1234_up_id'
        assert request.json['filters'][0]['name'] == 'brand'
        assert request.json['filters'][0]['values'][0] == 'yataxi'
        assert request.json['filters'][1]['name'] == 'tariff_class'
        assert sorted(request.json['filters'][1]['values']) == [
            'business',
            'comfortplus',
            'econom',
            'maybach',
            'ultimate',
            'vip',
        ]
        assert request.json['timerange']['from'] == '2021-12-14T14:00:00+00:00'

        def make_counter(tariff_class):
            return {
                'properties': [
                    {'name': 'brand', 'value': 'yataxi'},
                    {'name': 'tariff_class', 'value': tariff_class},
                    {'name': 'payment_type', 'value': 'cash'},
                ],
                'value': (
                    econom_rides_number
                    if tariff_class == 'econom'
                    else comfort_rides_number
                ),
                'counted_from': '2021-12-14T14:00:00+00:00',
                'counted_to': '2022-01-14T00:00:00',
            }

        return {
            'data': [
                {
                    'identity': {'type': 'phone_id', 'value': '+1234_up_id'},
                    'counters': [
                        make_counter('econom'),
                        make_counter('business'),
                    ],
                },
            ],
        }

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    assert orders_handle.times_called == 1
    data = response.json()
    queue_number = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['0'][
        'VALUE'
    ]
    assert queue_number == expected_queue_number


@pytest.mark.experiments3(filename='exp3_routing_greetings.json')
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
            'tags': [],
        },
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
async def test_routing_greetings(taxi_callcenter_stats, mock_personal):
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action_value_map = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    assert action_value_map == {
        '0': {'ACTION': 'ANSWER', 'VALUE': 0},
        '1': {
            'ACTION': 'APP',
            'PARAMS': {'CONTENT': 'test_sound', 'PROJECT': 'YANDEX_TAXI'},
            'VALUE': 'APPL_PLAYBACK',
        },
        '2': dial('+74999999999'),
    }


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'queue1',
            'number': '123',
            'allowed_clusters': ['s1'],
            'disabled_clusters': {'disabled_for_routing': []},
            'tags': [],
        },
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
)
@pytest.mark.parametrize(
    ['exp_json_name'],
    (
        pytest.param('exp3_phone_routing_experiment_go_to_epx.json'),
        pytest.param('exp3_phone_routing_config_go_to_epx.json'),
    ),
)
async def test_go_to_experiment_action(
        taxi_callcenter_stats,
        mock_personal,
        exp_json_name,
        load_json,
        experiments3,
):
    exp_json = load_json(exp_json_name)
    experiments3.add_experiments_json(
        load_json('cc_stats_routing_experiment_test.json'),
    )
    experiments3.add_experiments_json(exp_json)
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action_value_map = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    assert action_value_map['0'] == dial()


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {'name': 'disp_test', 'number': '123', 'allowed_clusters': ['s1']},
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
    CALLCENTER_STATS_ROUTING_IGNORE_STATUS_MAP={'123': True},
)
async def test_ignore_status(taxi_callcenter_stats, mock_personal):
    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action_value_map = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    assert action_value_map['0'] == {
        'ACTION': 'DIAL',
        'PARAMS': {
            'IGNORESTATUS': True,
            'ROUTE': 'GLOBAL_ROUTING',
            'TIMEOUT': 300,
        },
        'VALUE': 'GLOBAL/123',
    }


@pytest.mark.experiments3(
    filename='exp3_phone_routing_config_check_zerosuggest.json',
)
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '321',
            'allowed_clusters': ['s1'],
            'disabled_clusters': {'disabled_for_routing': []},
            'tags': ['check_zero_suggest'],
        },
        {
            'name': 'queue1',
            'number': '123',
            'allowed_clusters': ['s1'],
            'disabled_clusters': {'disabled_for_routing': []},
            'tags': [],
        },
        {
            'name': 'queue2',
            'number': '231',
            'allowed_clusters': ['s1'],
            'disabled_clusters': {'disabled_for_routing': []},
            'tags': [],
        },
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
        '+75999999999': {'metaqueue': 'disp_test'},
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
)
@pytest.mark.parametrize(
    ['origin_dn', 'state_mode', 'queue_num'],
    (
        pytest.param('+74999999999', 'robot_call_center', '123'),
        pytest.param('+75999999999', 'robot_call_center_sandbox', '231'),
    ),
)
async def test_zerosuggest(
        mockserver,
        taxi_callcenter_stats,
        origin_dn,
        state_mode,
        queue_num,
        mock_personal,
):
    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _zerosuggest_handle(request):
        assert request.json['state']['current_mode'] == state_mode
        return {
            'results': [
                {
                    'lang': 'ru',
                    'log': '',
                    'method': '',
                    'position': [37, 55],
                    'subtitle': {'hl': [], 'text': 'Петровский бульвар, 21'},
                    'text': 'Москва, Россия',
                    'title': {'hl': [], 'text': 'u1'},
                    'uri': 'test_uri_u1',
                    'userplace_info': {
                        'id': '00000004-AAAA-AAAA-AAAA-000000000001',
                        'name': 'U1',
                        'version': 123,
                    },
                    'tags': ['call_center_ok'],
                },
            ],
        }

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': origin_dn,
                'CALLED_DN': origin_dn,
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()
    action_value_map = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    assert action_value_map['0'] == dial(queue_num)


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp_test',
            'number': '+74999999999',
            'allowed_clusters': ['s1'],
            'tags': ['check_user_tags', 'check_active_order'],
        },
    ],
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
    },
    CALLCENTER_STATS_PASSENGER_TAGS_TO_ATTRIBUTES_MAP={
        'cashrunner': 'antifraud_cashrunner_block_cash',
    },
)
@pytest.mark.parametrize(
    ('ivr_disp_times_called', 'tags_times_called'),
    (
        pytest.param(
            1,
            1,
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES_TAGS_DISABLER={
                    'global_disabled': False,
                    'disabled_tags': [],
                },
            ),
        ),
        pytest.param(
            0,
            0,
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES_TAGS_DISABLER={
                    'global_disabled': True,
                    'disabled_tags': [],
                },
            ),
        ),
        pytest.param(
            1,
            0,
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES_TAGS_DISABLER={
                    'global_disabled': False,
                    'disabled_tags': ['check_user_tags'],
                },
            ),
        ),
    ),
)
@pytest.mark.experiments3(filename='exp3_phone_routing_check_tags.json')
async def test_tags_disabler(
        taxi_callcenter_stats,
        mockserver,
        mock_personal,
        ivr_disp_times_called,
        tags_times_called,
):
    @mockserver.json_handler('/passenger-tags/v3/match_single')
    async def passenger_tags_handler(request):
        return {'tags': {'cashrunner': {}}}

    @mockserver.json_handler('/ivr-dispatcher/has_order_status')
    def has_order_status(request):
        return {'has_order_status': False}

    response = await taxi_callcenter_stats.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'ORIGINAL_DN': '+74999999999',
                'CALLED_DN': '+74999999999',
                'CALLERID': '+1234',
            },
        ),
    )
    assert response.status_code == 200
    assert (
        passenger_tags_handler.times_called,
        has_order_status.times_called,
    ) == (tags_times_called, ivr_disp_times_called)
