import pytest


@pytest.mark.config(
    CALLCENTER_STATS_CACHES={
        'subclusters-info-cache': {
            'full-update-interval-ms': 86400000,
            'request-limit': 2,
            'update-interval-ms': 100,
            'update-jitter-ms': 0,
        },
    },
)
@pytest.mark.parametrize(
    ['idx', 'expected_cache_value'],
    [
        pytest.param(
            None,
            {
                'disp': [
                    {
                        'name': 's1',
                        'enabled_for_call_balancing': True,
                        'enabled_for_sip_users_balancing': True,
                        'enabled': True,
                    },
                    {
                        'name': 's2',
                        'enabled_for_call_balancing': False,
                        'enabled_for_sip_users_balancing': False,
                        'enabled': False,
                    },
                ],
                'support': [
                    {
                        'name': 's1',
                        'enabled_for_call_balancing': True,
                        'enabled_for_sip_users_balancing': True,
                        'enabled': False,
                    },
                    {
                        'name': 's3',
                        'enabled_for_call_balancing': True,
                        'enabled_for_sip_users_balancing': True,
                        'enabled': True,
                    },
                ],
            },
            id='only full',
        ),
    ],
)
async def test_subclusters_info_cache(
        taxi_callcenter_stats,
        mockserver,
        testpoint,
        expected_cache_value,
        idx,
):
    @testpoint('queue-list-cache-finish')
    def subclusters_info_cache_finish(data):
        pass

    @mockserver.json_handler('/callcenter-queues/v1/queues/list')
    def _queues_list(request):
        return mockserver.make_response(
            status=200,
            json={
                'subclusters': ['s1', 's2', 's3'],
                'metaqueues': ['disp', 'support'],
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
                                'enabled_for_call_balancing': False,
                                'enabled_for_sip_users_balancing': False,
                                'enabled': False,
                            },
                        ],
                    },
                    {
                        'metaqueue': 'support',
                        'subclusters': [
                            {
                                'name': 's1',
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_users_balancing': True,
                                'enabled': False,
                            },
                            {
                                'name': 's3',
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_users_balancing': True,
                                'enabled': True,
                            },
                        ],
                    },
                ],
            },
        )

    await taxi_callcenter_stats.invalidate_caches()

    value = await subclusters_info_cache_finish.wait_call()
    assert value['data'] == expected_cache_value
