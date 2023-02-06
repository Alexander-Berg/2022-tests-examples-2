from urllib import parse

import pytest

from tests_callcenter_stats.test_qa_ticket_generation import params
from tests_callcenter_stats.test_qa_ticket_generation import utils


def settings(
        launch_time='00:00',
        boundary_time=None,
        metaqueues=None,
        min_tickets_per_operator=3,
        required_calls_lookup_rules=params.DEFAULT_LOOKUP_RULES,
):
    return {
        'enabled': True,
        'launch_time': launch_time,
        'boundary_time': boundary_time,
        'stq_task_creation_delay': 0,
        'settings_map': {
            'cc': {
                'enabled': True,
                'recording_url_format': '{call_guid} {call_link_id}',
                'order_url_format': 'order/{order_id}',
                'min_tickets_per_operator': min_tickets_per_operator,
                'required_calls_lookup_rules': required_calls_lookup_rules,
                'operators_filter': {},
                'calls_filter': (
                    {'metaqueues': metaqueues} if metaqueues else {}
                ),
                'tracker_queue': 'CALLS',
                'tracker_auth_secret_name': (
                    'CALLCENTER_STATS_API_TRACKER_HEADERS'
                ),
                'tracker_summary_format': '{call_time} {call_date}',
                'tracker_ticket_fields': params.DEFAULT_QA_TICKET_FIELDS,
            },
        },
    }


def select_call_history(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        '   id, call_guid, queue, queued_at, agent_id,'
        '   abonent_phone_id, called_number '
        'FROM callcenter_stats.call_history;',
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def extract_ids(ticket):
    encoded_call_guid, encoded_call_link_id = ticket['RecURL'].split()
    call_guid = parse.unquote(encoded_call_guid)
    call_link_id = parse.unquote(encoded_call_link_id)
    # assert that special characters were shielded in url
    assert call_guid != encoded_call_guid
    assert call_link_id != encoded_call_link_id

    return call_link_id, call_guid


@pytest.mark.parametrize(
    [
        'expected_launch_time_point',
        'expected_boundary_time_point',
        'expected_tickets_count',
    ],
    (
        pytest.param(
            '2020-07-07T21:00:00+00:00',
            '2020-07-07T21:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-07T16:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='00:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-07T21:00:00+00:00',
            '2020-07-07T21:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-06T21:00:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='00:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T00:00:00+00:00',
            '2020-07-08T00:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-07T21:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='03:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T00:00:00+00:00',
            '2020-07-08T00:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-07T21:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='03:00', boundary_time='03:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T02:00:00+00:00',
            '2020-07-08T00:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-07T21:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='05:00', boundary_time='03:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T02:00:00+00:00',
            '2020-07-08T00:00:00+00:00',
            6,
            marks=[
                pytest.mark.now('2020-07-08T00:00:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='05:00', boundary_time='03:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-07T04:00:00+00:00',
            '2020-07-07T04:00:00+00:00',
            4,
            marks=[
                pytest.mark.now('2020-07-07T00:00:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='07:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T21:00:00+00:00',
            '2020-07-08T21:00:00+00:00',
            0,
            marks=[
                pytest.mark.now('2020-07-07T23:00:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='00:00'),
                ),
            ],
        ),
        pytest.param(
            '2020-07-08T00:00:00+00:00',
            '2020-07-08T00:00:00+00:00',
            5,
            marks=[
                pytest.mark.now('2020-07-07T21:30:00.00Z'),
                utils.mark_qa_ticket_gen_settings(
                    settings(launch_time='03:00', metaqueues=['corp_cc']),
                ),
            ],
        ),
    ),
)
@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
async def test_launch_times(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        stq,
        stq_runner,
        testpoint,
        set_now,
        expected_launch_time_point,
        expected_boundary_time_point,
        expected_tickets_count,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    call_history_db = select_call_history(pgsql)

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == expected_launch_time_point
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == (
            2 if expected_tickets_count else 0
        )
        assert (
            result['data']['boundary_time_point']
            == expected_boundary_time_point
        )

    tickets_count = 0
    for _ in range(result['data']['tasks_created']):
        await utils.forward_stq(stq, stq_runner)
        operator_tickets_count = handle_stq_finished.next_call()['data']
        tickets_count += operator_tickets_count
    assert tickets_count == expected_tickets_count

    assert (
        mock_api_tracker.external_issues.times_called == expected_tickets_count
    )
    while mock_api_tracker.external_issues.times_called > 0:
        body = mock_api_tracker.external_issues.next_call()['request'].json
        utils.check_ticket(body, call_history_db, extract_ids)


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.parametrize(
    ['expected_call_link_ids'],
    (
        pytest.param(
            ['id5/hash', 'id6/hash', 'id7/hash'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=3,
                    required_calls_lookup_rules=params.OTHER_LOOKUP_RULES,
                ),
            ),
        ),
        pytest.param(
            ['id1/hash', 'id3/hash', 'id6/hash', 'id4/hash'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=4,
                    required_calls_lookup_rules=[
                        {'talk_duration': {'to': 5}},
                        {'talk_duration': {'from': 10, 'to': 11}},
                        {'talk_duration': {'from': 120, 'to': 240}},
                        {'talk_duration': {'from': 20, 'to': 40}},
                    ],
                ),
            ),
        ),
        pytest.param(
            ['id5/hash', 'id6/hash', 'id7/hash'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=1,
                    required_calls_lookup_rules=params.OTHER_LOOKUP_RULES,
                ),
            ),
        ),
        pytest.param(
            # None == any call_link_id
            ['id5/hash', 'id6/hash', 'id7/hash', None],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=4,
                    required_calls_lookup_rules=params.OTHER_LOOKUP_RULES,
                ),
            ),
        ),
        pytest.param(
            [
                'id1/hash',
                'id2/hash',
                'id3/hash',
                'id4/hash',
                'id5/hash',
                'id6/hash',
                'id7/hash',
            ],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=8,
                    required_calls_lookup_rules=params.OTHER_LOOKUP_RULES,
                ),
            ),
        ),
        pytest.param(
            [],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=0, required_calls_lookup_rules=[],
                ),
            ),
        ),
        pytest.param(
            ['id2/hash', 'id3/hash', 'id4/hash', 'id7/hash'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    min_tickets_per_operator=1,
                    required_calls_lookup_rules=[
                        {'talk_duration': {'from': 4, 'to': 31}, 'count': 3},
                        {
                            'talk_duration': {'from': 239, 'to': 301},
                            'count': 2,
                        },
                    ],
                ),
            ),
        ),
    ),
)
@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_2.sql', 'actions_2.sql'],
)
async def test_lookup_rules(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        stq,
        stq_runner,
        testpoint,
        set_now,
        expected_call_link_ids,
):
    @testpoint('qa-ticket-generation-scheduler::sleep')
    def handle_dist_lock_sleep(data):
        return

    @testpoint('qa-ticket-generation-scheduler::wake-up')
    def handle_dist_lock_wake_up(data):
        return {}

    @testpoint('qa-ticket-generation-scheduler::task-finished')
    def handle_dist_lock_finished(data):
        return

    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    calls_processed = {}
    for call_link_id in expected_call_link_ids:
        calls_processed[call_link_id] = False

    call_history_db = select_call_history(pgsql)

    async with taxi_callcenter_stats.spawn_task(
            'distlock/schedule-qa-ticket-generation',
    ):
        launch_time_point = await handle_dist_lock_sleep.wait_call()
        assert launch_time_point['data'] == '2020-07-07T21:00:00+00:00'
        await set_now(utils.pre_time_point(launch_time_point['data']))
        await handle_dist_lock_wake_up.wait_call()
        await set_now(launch_time_point['data'])
        result = await handle_dist_lock_finished.wait_call()
        assert result['data']['tasks_created'] == 1
        assert (
            result['data']['boundary_time_point']
            == '2020-07-07T21:00:00+00:00'
        )

    await utils.forward_stq(stq, stq_runner)
    tickets_count = handle_stq_finished.next_call()['data']
    assert tickets_count == len(expected_call_link_ids)

    assert mock_api_tracker.external_issues.times_called == len(
        expected_call_link_ids,
    )
    while mock_api_tracker.external_issues.times_called > 0:
        body = mock_api_tracker.external_issues.next_call()['request'].json
        utils.check_ticket(body, call_history_db, extract_ids)

        call_link_id = (
            extract_ids(body)[0]
            if calls_processed.get(extract_ids(body)[0]) is not None
            else None
        )
        assert not calls_processed[call_link_id]
        calls_processed[call_link_id] = True

    assert all(calls_processed.values())
