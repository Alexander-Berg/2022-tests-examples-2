import urllib.parse

import pytest

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


@pytest.mark.now('2020-07-07T16:30:00.00Z')
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
    ],
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '+74999999999': {'metaqueue': 'disp_test'},
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
    [
        'origin_dn',
        'state_mode',
        'queue_num',
        'expected_testpoint_moment_update',
        'expected_testpoint_average_update',
        'expected_testpoint_cache',
    ],
    (
        pytest.param(
            '+74999999999',
            'robot_call_center',
            '123',
            {
                'QueuesCacheAveragePercent': {},
                'QueuesPercent': {
                    'ru_taxi_test': {'percent_sum': 1000, 'update_count': 1},
                },
            },
            {
                'QueuesCacheAveragePercent': {'ru_taxi_test': 1000},
                'QueuesPercent': {},
            },
            {
                'QueuesCacheAveragePercent': {'ru_taxi_test': 1000},
                'QueuesRecommendedPercent': {'ru_taxi_test': 1000},
            },
        ),
    ),
)
async def test_cache_in_routing(
        mockserver,
        taxi_callcenter_stats,
        origin_dn,
        state_mode,
        queue_num,
        testpoint,
        set_now,
        expected_testpoint_moment_update,
        expected_testpoint_average_update,
        expected_testpoint_cache,
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

    @testpoint('queues-average-percent-calculator-moment-update-finish')
    def moment_update_finish(data):
        pass

    @testpoint('queues-average-percent-calculator-average-update-finish')
    def average_update_finish(data):
        pass

    @testpoint('queues-average-percent-calculator-get-cache')
    def get_cache(data):
        assert data == expected_testpoint_cache

    await taxi_callcenter_stats.enable_testpoints()

    # Run PeriodicTask and wait when it finishes
    async with taxi_callcenter_stats.spawn_task(
            'periodic-task/queue-average-percent-calculator',
    ):
        await set_now('2020-07-07T16:30:11+00:00')
        await moment_update_finish.wait_call()
        await set_now('2020-07-07T16:33:01+00:00')
        await average_update_finish.wait_call()

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
    await get_cache.wait_call()
    assert response.status_code == 200
