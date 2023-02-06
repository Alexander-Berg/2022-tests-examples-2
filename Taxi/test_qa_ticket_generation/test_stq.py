import datetime
from urllib import parse

from aiohttp import web
import pytest

from tests_callcenter_stats.test_qa_ticket_generation import params
from tests_callcenter_stats.test_qa_ticket_generation import utils


def qa_ticket_gen_settings(
        settings_id='rus',
        required_calls_lookup_rules=params.DEFAULT_LOOKUP_RULES,
        tracker_ticket_fields=params.DEFAULT_QA_TICKET_FIELDS.copy(),
        metaqueues=None,
):
    return {
        'enabled': True,
        'recording_url_format': 'url/{call_link_id}',
        'order_url_format': 'order/{order_id}',
        'min_tickets_per_operator': 2 if settings_id == 'bel' else 3,
        'required_calls_lookup_rules': required_calls_lookup_rules,
        'operators_filter': {},
        'calls_filter': {'metaqueues': metaqueues} if metaqueues else None,
        'tracker_queue': 'CALLS' + (
            '_BEL'
            if settings_id == 'bel'
            else ('_INTERNAL' if settings_id == 'internal' else '')
        ),
        'tracker_auth_secret_name': (
            'CALLCENTER_STATS_STARTREK_HEADERS_QA'
            if settings_id == 'internal'
            else (
                'CALLCENTER_STATS_API_TRACKER_HEADERS'
                + ('_BEL' if settings_id == 'bel' else '')
            )
        ),
        'tracker_is_internal': settings_id == 'internal',
        'tracker_summary_format': (
            '{agent_full_name} {call_time} {call_date}'
            if tracker_ticket_fields == params.DEFAULT_QA_TICKET_FIELDS
            else ''
        ),
        'tracker_ticket_fields': tracker_ticket_fields,
    }


def settings(
        tracker_ticket_fields=params.DEFAULT_QA_TICKET_FIELDS.copy(),
        metaqueues=None,
):
    return {
        'enabled': True,
        'launch_time': '00:00',
        'stq_task_creation_delay': 0,
        'settings_map': {
            settings_id: qa_ticket_gen_settings(
                settings_id=settings_id,
                required_calls_lookup_rules=lookup_rules,
                tracker_ticket_fields=tracker_ticket_fields,
                metaqueues=metaqueues,
            )
            for settings_id, lookup_rules in zip(
                ['rus', 'bel', 'internal'],
                [
                    params.DEFAULT_LOOKUP_RULES,
                    params.OTHER_LOOKUP_RULES,
                    params.DEFAULT_LOOKUP_RULES,
                ],
            )
        },
    }


def select_call_history(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT '
        '   id, queue, queued_at, agent_id, abonent_phone_id,'
        '   called_number '
        'FROM callcenter_stats.call_history;',
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def extract_call_link_id(ticket):
    url_part = ticket['RecURL'][4:]
    call_link_id = parse.unquote(url_part)
    # assert that special characters were shielded in url
    assert call_link_id != url_part
    return (call_link_id,)


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(
        metaqueues=['corp_cc'],
    ),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.parametrize(
    [
        'time_range_from',
        'time_range_to',
        'settings_id',
        'expected_tickets_count',
    ],
    (
        ('2020-07-06T21:00:00+0000', '2020-07-07T21:00:00+0000', 'rus', 3),
        ('2020-07-06T21:00:00+0000', '2020-07-07T15:00:00+0000', 'rus', 3),
        ('2020-07-06T21:00:00+0000', '2020-07-07T15:00:00+0000', 'bel', 2),
        (
            '2020-07-06T21:00:00+0000',
            '2020-07-07T15:00:00+0000',
            'internal',
            3,
        ),
        ('2020-07-06T00:00:00+0000', '2020-07-07T00:00:00+0000', 'rus', 2),
        ('2020-07-07T10:00:00+0000', '2020-07-07T13:00:00+0000', 'rus', 1),
    ),
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
async def test_tickets_create(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        stq_runner,
        testpoint,
        time_range_from,
        time_range_to,
        settings_id,
        expected_tickets_count,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    call_history_db = select_call_history(pgsql)

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'agent_id': '111',
            'time_range_from': time_range_from,
            'time_range_to': time_range_to,
            'settings_id': settings_id,
        },
    )
    tickets_count = handle_stq_finished.next_call()['data']
    assert tickets_count == expected_tickets_count

    assert mock_api_tracker.times_called == expected_tickets_count
    while mock_api_tracker.times_called > 0:
        if mock_api_tracker.external_issues.times_called > 0:
            body = mock_api_tracker.external_issues.next_call()['request'].json
        else:
            body = mock_api_tracker.internal_issues.next_call()['request'].json
        utils.check_ticket(body, call_history_db, extract_call_link_id)


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
async def test_different_calls_and_durations(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    call_history_db = select_call_history(pgsql)
    bad_call_link_ids = [
        'id3/hash',
        'id4/hash',
        'id17/hash',
        'id18/hash',
        'id19/hash',
        'id20/hash',
        'id21/hash',
        'id22/hash',
    ]
    calls = {}

    for agent_id in ['111', '222']:
        # For each operator check all 3 talk duration types
        # types[0]:   1 min <= talk duration < 5 min
        # types[1]:   5 min <= talk duration < 15 min
        # types[2]:   talk duration >= 15 min
        calls[agent_id] = {'ids': [], 'types': [False, False, False]}
        await stq_runner.operator_qa_ticket_generation.call(
            task_id='task_id',
            kwargs={
                'agent_id': agent_id,
                'time_range_from': '2020-07-06T21:00:00+0000',
                'time_range_to': '2020-07-07T21:00:00+0000',
                'settings_id': 'rus',
            },
        )
        tickets_count = handle_stq_finished.next_call()['data']
        assert tickets_count == 3

    assert mock_api_tracker.external_issues.times_called == 6
    while mock_api_tracker.external_issues.times_called > 0:
        body = mock_api_tracker.external_issues.next_call()['request'].json
        utils.check_ticket(body, call_history_db, extract_call_link_id)

        call_link_id = extract_call_link_id(body)[0]
        agent_id = params.OPERATOR_IDS[body['login']]
        assert call_link_id not in bad_call_link_ids
        assert call_link_id not in calls[agent_id]
        calls[agent_id]['ids'].append(call_link_id)

        talk_duration = datetime.time.fromisoformat(body['DialogTime'])
        assert talk_duration >= datetime.time(minute=1)
        idx = int(talk_duration >= datetime.time(minute=5)) + int(
            talk_duration >= datetime.time(minute=15),
        )
        assert not calls[agent_id]['types'][idx]
        calls[agent_id]['types'][idx] = True

    assert all(calls['111']['types'] + calls['222']['types'])
    assert not set(calls['111']['ids']) & set(calls['222']['ids'])


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_2.sql', 'actions_2.sql'],
)
async def test_tracker_fail(
        taxi_callcenter_stats,
        mock_personal,
        pgsql,
        stq_runner,
        testpoint,
        mockserver,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    @mockserver.json_handler('/api-tracker/v2/issues')
    def api_tracker_issues(request):
        if extract_call_link_id(request.json)[0] == 'id6/hash':
            return web.Response(status=500)
        return web.Response(
            status=201, body='{"id": "task_1", "key": "TASK-1"}',
        )

    calls_processed = {'id5/hash': False, 'id6/hash': False, 'id7/hash': False}
    call_history_db = select_call_history(pgsql)

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'agent_id': '111',
            'time_range_from': '2020-07-06T21:00:00+0000',
            'time_range_to': '2020-07-07T21:00:00+0000',
            'settings_id': 'bel',
        },
    )
    tickets_count = handle_stq_finished.next_call()['data']
    assert tickets_count == 2

    assert api_tracker_issues.times_called >= 3
    while api_tracker_issues.times_called > 0:
        body = api_tracker_issues.next_call()['request'].json
        utils.check_ticket(body, call_history_db, extract_call_link_id)
        calls_processed[extract_call_link_id(body)[0]] = True

    assert all(calls_processed.values())


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_2.sql', 'actions_2.sql'],
)
async def test_no_calls_for_agent(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'agent_id': '222',
            'time_range_from': '2020-07-06T21:00:00+0000',
            'time_range_to': '2020-07-07T21:00:00+0000',
            'settings_id': 'rus',
        },
    )
    assert handle_stq_finished.times_called == 0
    assert mock_api_tracker.times_called == 0


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_2.sql', 'actions_2.sql'],
)
async def test_unknown_agent(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'agent_id': 'unknown_id',
            'time_range_from': '2020-07-06T21:00:00+0000',
            'time_range_to': '2020-07-07T21:00:00+0000',
            'settings_id': 'rus',
        },
    )
    assert handle_stq_finished.times_called == 0
    assert mock_api_tracker.times_called == 0


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
# Test that all calls will be processed eventually after several ticket
# generations.
async def test_random_distribution(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    calls_processed = {}
    bad_call_link_ids = [
        'id3/hash',
        'id4/hash',
        'id17/hash',
        'id18/hash',
        'id19/hash',
        'id20/hash',
        'id21/hash',
        'id22/hash',
    ]
    for i in range(1, 23):
        call_link_id = 'id' + str(i) + '/hash'
        if call_link_id in bad_call_link_ids:
            continue
        calls_processed[call_link_id] = False

    call_history_db = select_call_history(pgsql)

    while not all(calls_processed.values()):
        for agent_id in ['111', '222']:
            await stq_runner.operator_qa_ticket_generation.call(
                task_id='task_id',
                kwargs={
                    'agent_id': agent_id,
                    'time_range_from': '2020-07-06T21:00:00+0000',
                    'time_range_to': '2020-07-07T21:00:00+0000',
                    'settings_id': 'rus',
                },
            )
            tickets_count = handle_stq_finished.next_call()['data']
            assert tickets_count == 3

        # For each operator check all 3 talk duration types
        # call_types[0]:   1 min <= talk duration < 5 min
        # call_types[1]:   5 min <= talk duration < 15 min
        # call_types[2]:   talk duration >= 15 min
        call_types = {
            '111': [False, False, False],
            '222': [False, False, False],
        }
        assert mock_api_tracker.external_issues.times_called == 6
        while mock_api_tracker.external_issues.times_called > 0:
            body = mock_api_tracker.external_issues.next_call()['request'].json
            utils.check_ticket(body, call_history_db, extract_call_link_id)

            talk_duration = datetime.time.fromisoformat(body['DialogTime'])
            assert talk_duration >= datetime.time(minute=1)
            idx = int(talk_duration >= datetime.time(minute=5)) + int(
                talk_duration >= datetime.time(minute=15),
            )
            agent_id = params.OPERATOR_IDS[body['login']]
            assert not call_types[agent_id][idx]
            call_types[agent_id][idx] = True

            call_link_id = extract_call_link_id(body)[0]
            assert call_link_id not in bad_call_link_ids
            calls_processed[call_link_id] = True
        assert all(call_types['111'] + call_types['222'])


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.parametrize(
    [],
    (
        pytest.param(
            marks=pytest.mark.config(
                CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(
                    tracker_ticket_fields={},
                ),
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(
                    tracker_ticket_fields=params.EMPTY_QA_TICKET_FIELDS,
                ),
            ),
        ),
    ),
)
@pytest.mark.parametrize(['settings_id'], (('rus',), ('bel',), ('internal',)))
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
async def test_empty_ticket(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        settings_id,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'agent_id': '111',
            'time_range_from': '2020-07-06T21:00:00+0000',
            'time_range_to': '2020-07-07T21:00:00+0000',
            'settings_id': settings_id,
        },
    )
    tickets_count = handle_stq_finished.next_call()['data']
    assert tickets_count == 3

    assert mock_api_tracker.times_called == 3
    while mock_api_tracker.times_called > 0:
        if mock_api_tracker.external_issues.times_called > 0:
            body = mock_api_tracker.external_issues.next_call()['request'].json
        else:
            body = mock_api_tracker.internal_issues.next_call()['request'].json
        assert len(body) == 3
        assert body['queue'] == 'CALLS' + (
            '_BEL'
            if settings_id == 'bel'
            else ('_INTERNAL' if settings_id == 'internal' else '')
        )
        assert not body['summary']
        assert not body['description']


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QA_TICKET_GENERATION_SETTINGS_MAP=settings(),
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP=params.CC_PHONE_INFO_MAP,
)
@pytest.mark.parametrize(
    ['call_link_id', 'ticket_created', 'ml_rating'],
    (
        pytest.param('id17/hash', True, 5.5),
        pytest.param('id7/hash', True, None),
        pytest.param('id3/hash', False, None),
        pytest.param('unknown_id', False, None),
        pytest.param(None, False, None),
    ),
)
@pytest.mark.parametrize(['settings_id'], (('rus',), ('bel',), ('internal',)))
@pytest.mark.pgsql(
    'callcenter_stats', files=['call_history_1.sql', 'actions_1.sql'],
)
async def test_single_call(
        taxi_callcenter_stats,
        mock_personal,
        mock_api_tracker,
        pgsql,
        settings_id,
        call_link_id,
        ticket_created,
        ml_rating,
        stq_runner,
        testpoint,
):
    @testpoint('operator_qa_ticket_generation::task-finished')
    def handle_stq_finished(data):
        return

    call_history_db = select_call_history(pgsql)

    await stq_runner.operator_qa_ticket_generation.call(
        task_id='task_id',
        kwargs={
            'settings_id': settings_id,
            'call_link_id': call_link_id,
            'ml_rating': ml_rating,
        },
    )
    assert handle_stq_finished.times_called == int(ticket_created)

    assert mock_api_tracker.times_called == int(ticket_created)
    while mock_api_tracker.times_called > 0:
        if mock_api_tracker.external_issues.times_called > 0:
            body = mock_api_tracker.external_issues.next_call()['request'].json
        else:
            body = mock_api_tracker.internal_issues.next_call()['request'].json
        utils.check_ticket(
            body, call_history_db, extract_call_link_id, ml_rating,
        )
        result_call_link_id = extract_call_link_id(body)[0]
        assert result_call_link_id == call_link_id
