import pytest


@pytest.mark.now('2020-12-29T21:00:00.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['insert_call_history.sql'])
@pytest.mark.parametrize(
    'expected_block_requests',
    [
        pytest.param(
            [],
            id='no enabled rules',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': False,
                                'time_depth_min': 60,
                                'count': 10,
                                'ban_time_min': 10,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [],
            id='no matching rules',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 60,
                                'count': 10,
                                'ban_time_min': 10,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 600,
                            'queues': ['disp_cc'],
                            'tel_number': '79991111111',
                        },
                        {
                            'expires_in': 600,
                            'queues': ['disp_cc'],
                            'tel_number': '79992222222',
                        },
                        {
                            'expires_in': 600,
                            'queues': ['disp_cc'],
                            'tel_number': '79994444444',
                        },
                    ],
                },
            ],
            id='base filter',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 60,
                                'count': 4,
                                'ban_time_min': 10,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 600,
                            'queues': ['disp_cc'],
                            'tel_number': '79994444444',
                        },
                    ],
                },
            ],
            id='check count',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 60,
                                'count': 8,
                                'ban_time_min': 10,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 600,
                            'queues': ['disp_cc'],
                            'tel_number': '79992222222',
                        },
                    ],
                },
            ],
            id='check called_numbers',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 60,
                                'called_numbers': ['+74958888888'],
                                'count': 4,
                                'ban_time_min': 10,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 60,
                            'queues': ['disp_cc'],
                            'tel_number': '79991111111',
                        },
                        {
                            'expires_in': 60,
                            'queues': ['disp_cc'],
                            'tel_number': '79993333333',
                        },
                    ],
                },
            ],
            id='check time_depth_min',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 120,
                                'called_numbers': ['+74959999999'],
                                'count': 4,
                                'ban_time_min': 1,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 60,
                            'queues': ['disp_cc'],
                            'tel_number': '79994444444',
                        },
                    ],
                },
            ],
            id='check answered_count',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 120,
                                'called_numbers': ['+74957777777'],
                                'count': 6,
                                'answered_count': 6,
                                'ban_time_min': 1,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [],
            id='check bad answered_count',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 120,
                                'called_numbers': ['+74957777777'],
                                'count': 6,
                                'answered_count': 7,
                                'ban_time_min': 1,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'to_block': [
                        {
                            'expires_in': 60,
                            'queues': ['disp_cc'],
                            'tel_number': '79992222222',
                        },
                    ],
                },
                {
                    'to_block': [
                        {
                            'expires_in': 120,
                            'queues': ['disp_cc'],
                            'tel_number': '79994444444',
                        },
                    ],
                },
            ],
            id='check multi-rules',
            marks=[
                pytest.mark.config(
                    CALLCENTER_STATS_NUMBER_BLOCKER_SETTINGS={
                        'period_sec': 60,
                        'block_rules': [
                            {
                                'enabled': True,
                                'time_depth_min': 60,
                                'called_numbers': ['+74958888888'],
                                'count': 4,
                                'ban_time_min': 1,
                            },
                            {
                                'enabled': True,
                                'time_depth_min': 120,
                                'called_numbers': ['+74957777777'],
                                'count': 7,
                                'ban_time_min': 2,
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
async def test(
        taxi_callcenter_stats,
        mock_personal,
        testpoint,
        mockserver,
        expected_block_requests,
):
    @testpoint('block-numbers-finished')
    def number_blocker_finished(data):
        return

    await taxi_callcenter_stats.enable_testpoints()

    @mockserver.json_handler(
        '/callcenter-operators'
        '/cc/v1/callcenter-operators/v1/black_list/add_bulk',
    )
    def black_list_add(request):
        return mockserver.make_response(
            status=200, json={'unhandled_numbers': []},
        )

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_stats.spawn_task('distlock/block-numbers'):
        await number_blocker_finished.wait_call()

    # Check result
    assert black_list_add.times_called == len(expected_block_requests)
    for expected_block_request in expected_block_requests:
        request_json = black_list_add.next_call()['request'].json
        request_json['to_block'] = sorted(
            request_json['to_block'], key=lambda x: x['tel_number'],
        )
        assert request_json == expected_block_request
