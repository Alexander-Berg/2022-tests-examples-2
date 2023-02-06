import datetime
from urllib import parse

import pytest

from tests_callcenter_stats.test_qa_ticket_generation import params
from tests_callcenter_stats.test_qa_ticket_generation import utils

CALL_GEN_TICKET_URL = '/cc/v1/callcenter-stats/v1/call/generate_qa_ticket'


def qa_ticket_gen_settings(
        settings_id='rus',
        manual_gen_enabled=True,
        operators_filter=None,
        calls_filter=None,
):
    return {
        'enabled': False,
        'manual_generation_enabled': manual_gen_enabled,
        'recording_url_format': 'url/{call_link_id}',
        'order_url_format': 'order/{order_id}',
        'min_tickets_per_operator': 3,
        'required_calls_lookup_rules': [],
        'operators_filter': operators_filter or {},
        'calls_filter': calls_filter or {},
        'tracker_queue': 'CALLS' + ('_BEL' if settings_id == 'bel' else ''),
        'tracker_auth_secret_name': 'CALLCENTER_STATS_API_TRACKER_HEADERS' + (
            '_BEL' if settings_id == 'bel' else ''
        ),
        'tracker_summary_format': '{agent_full_name} {call_time} {call_date}',
        'tracker_ticket_fields': params.DEFAULT_QA_TICKET_FIELDS,
    }


def settings(
        stq_task_creation_delay=0,
        settings_ids=('rus',),
        settings_values=(qa_ticket_gen_settings(),),
        default_settings_keys=None,
):
    return {
        'enabled': False,
        'launch_time': '00:00',
        'stq_task_creation_delay': stq_task_creation_delay,
        'default_settings_keys': default_settings_keys,
        'settings_map': {
            key: value for key, value in zip(settings_ids, settings_values)
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


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'corp': {
            'metaqueues': ['corp_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'god': {
            'metaqueues': ['help_cc', 'corp_cc'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.parametrize(
    [
        'call_link_id',
        'project',
        'ml_rating',
        'expected_status',
        'expected_settings_ids',
        'settings_keys',
    ],
    (
        pytest.param('id17/hash', None, 5.5, 200, ['rus'], None),
        pytest.param('id17/hash', None, None, 200, ['rus'], None),
        pytest.param('id17/hash', 'corp', None, 200, ['rus'], None),
        pytest.param('id17/hash', 'god', None, 200, ['rus'], None),
        pytest.param('id17/hash', 'help', None, 404, [], None),
        pytest.param('unknown_id', None, None, 404, [], None),
        pytest.param('id3/hash', None, None, 404, [], None),
        pytest.param(
            'id1/hash',
            None,
            None,
            406,
            [],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_values=(
                        qa_ticket_gen_settings(manual_gen_enabled=False),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id7/hash',
            None,
            None,
            406,
            [],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus', 'bel'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=('rus', 'bel'),
                    settings_values=(
                        qa_ticket_gen_settings(
                            settings_id='rus',
                            operators_filter={
                                'callcenter_ids': [
                                    'volgograd_cc',
                                    'krasnodar_cc',
                                ],
                            },
                        ),
                        qa_ticket_gen_settings(
                            settings_id='bel',
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['bel'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=('rus', 'bel'),
                    settings_values=(
                        qa_ticket_gen_settings(
                            manual_gen_enabled=False,
                            settings_id='rus',
                            operators_filter={
                                'callcenter_ids': [
                                    'volgograd_cc',
                                    'krasnodar_cc',
                                ],
                            },
                        ),
                        qa_ticket_gen_settings(
                            settings_id='bel',
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            406,
            [],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    default_settings_keys=['bel'],
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(manual_gen_enabled=True),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            406,
            [],
            ['bel'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    default_settings_keys=['rus'],
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(manual_gen_enabled=True),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    default_settings_keys=['rus'],
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    default_settings_keys=None,
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            ['rus'],
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    default_settings_keys=['bel'],
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                            calls_filter={'metaqueues': ['corp_cc']},
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            406,
            [],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                            calls_filter={'metaqueues': ['help_cc']},
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['bel'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=('rus', 'bel'),
                    settings_values=(
                        qa_ticket_gen_settings(
                            settings_id='rus',
                            operators_filter={
                                'callcenter_ids': [
                                    'volgograd_cc',
                                    'krasnodar_cc',
                                ],
                            },
                            calls_filter={'metaqueues': ['help_cc']},
                        ),
                        qa_ticket_gen_settings(
                            settings_id='bel',
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                            calls_filter={'metaqueues': ['corp_cc']},
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus', 'bel'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=('rus', 'bel'),
                    settings_values=(
                        qa_ticket_gen_settings(
                            settings_id='rus',
                            operators_filter={
                                'callcenter_ids': [
                                    'volgograd_cc',
                                    'krasnodar_cc',
                                ],
                            },
                            calls_filter={'metaqueues': None},
                        ),
                        qa_ticket_gen_settings(
                            settings_id='bel',
                            operators_filter={
                                'callcenter_ids': ['volgograd_cc'],
                            },
                            calls_filter={'metaqueues': ['corp_cc']},
                        ),
                    ),
                ),
            ),
        ),
        pytest.param(
            'id1/hash',
            None,
            None,
            200,
            ['rus'],
            None,
            marks=utils.mark_qa_ticket_gen_settings(
                settings(
                    settings_ids=['rus'],
                    settings_values=(
                        qa_ticket_gen_settings(
                            calls_filter={'metaqueues': ['corp_cc']},
                        ),
                    ),
                ),
            ),
        ),
    ),
)
@utils.mark_qa_ticket_gen_settings(settings())
async def test_handle(
        taxi_callcenter_stats,
        stq,
        call_link_id,
        project,
        ml_rating,
        expected_status,
        expected_settings_ids,
        settings_keys,
):
    request_body = {'project': project, 'settings_keys': settings_keys}
    if ml_rating:
        request_body['ml'] = {'rating': ml_rating}

    response = await taxi_callcenter_stats.post(
        f'{CALL_GEN_TICKET_URL}?call_link_id={call_link_id}',
        json=request_body,
    )
    assert response.status_code == expected_status

    assert stq.operator_qa_ticket_generation.times_called == len(
        expected_settings_ids,
    )
    for _ in expected_settings_ids:
        stq_call = stq.operator_qa_ticket_generation.next_call()
        assert stq_call['kwargs']['settings_id'] in expected_settings_ids
        assert stq_call['kwargs']['call_link_id'] == call_link_id
        assert stq_call['kwargs'].get('agent_id') is None
        assert stq_call['kwargs'].get('time_range_from') is None
        assert stq_call['kwargs'].get('time_range_to') is None
        if ml_rating:
            assert stq_call['kwargs']['ml_rating'] == ml_rating


@pytest.mark.now('2020-07-07T16:30:00.00Z')
@pytest.mark.parametrize(
    ['expected_etas'],
    (
        pytest.param(
            [
                datetime.datetime(2020, 7, 7, 16, 30, 0),
                datetime.datetime(2020, 7, 7, 16, 30, 0),
            ],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        stq_task_creation_delay=0,
                        settings_ids=('rus', 'bel'),
                        settings_values=(
                            qa_ticket_gen_settings(settings_id='rus'),
                            qa_ticket_gen_settings(settings_id='bel'),
                        ),
                    ),
                ),
            ],
        ),
        pytest.param(
            [
                datetime.datetime(2020, 7, 7, 16, 30, 1, 234000),
                datetime.datetime(2020, 7, 7, 16, 30, 2, 468000),
            ],
            marks=[
                utils.mark_qa_ticket_gen_settings(
                    settings(
                        stq_task_creation_delay=1234,
                        settings_ids=('rus', 'bel'),
                        settings_values=(
                            qa_ticket_gen_settings(settings_id='rus'),
                            qa_ticket_gen_settings(settings_id='bel'),
                        ),
                    ),
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql('callcenter_stats', files=['call_history_1.sql'])
async def test_stq_eta(taxi_callcenter_stats, stq, expected_etas):
    response = await taxi_callcenter_stats.post(
        f'{CALL_GEN_TICKET_URL}?call_link_id=id1/hash', json={},
    )
    assert response.status_code == 200

    assert stq.operator_qa_ticket_generation.times_called == len(expected_etas)
    for expected_eta in expected_etas:
        stq_call = stq.operator_qa_ticket_generation.next_call()
        assert stq_call['eta'] == expected_eta
