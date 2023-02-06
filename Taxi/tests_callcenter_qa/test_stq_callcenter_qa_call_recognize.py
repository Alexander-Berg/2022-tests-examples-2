import datetime

import pytest


def get_task_data(internal_id, call_id='call-id-01'):
    data = {
        'internalid1': {
            'internal_id': 'internalid1',
            'call_id': call_id,
            'call_guid': '0000000001-0000000001-0000000001-0000000001',
            'talking_duration': 1,
        },
        'internalid2': {
            'internal_id': 'internalid2',
            'call_id': call_id,
            'call_guid': '0000000001-0000000001-1625233862-0000000002',
            'talking_duration': 60,
        },
    }
    return data[internal_id]


def get_row_data(
        call_id='call-id-01',
        in_operation_id=None,
        out_operation_id=None,
        in_text=None,
        out_text=None,
        in_words=None,
        out_words=None,
        duration=60,
):
    return (
        'internalid2',
        call_id,
        '0000000001-0000000001-1625233862-0000000002',
        datetime.timedelta(seconds=duration),
        in_operation_id,
        out_operation_id,
        in_text,
        out_text,
        in_words,
        out_words,
    )


def get_config(config):
    default = {'error_timeout': 900, 'speechkit_model': 'general'}
    default.update(config)
    return default


WORDS_IN = [
    {'startTime': '0.879999999s', 'endTime': '1.159999992s', 'word': 'при'},
    {
        'startTime': '1.219999995s',
        'endTime': '1.539999988s',
        'word': 'написании',
    },
]
WORDS_OUT = [
    {'startTime': '0.879999999s', 'endTime': '1.159999992s', 'word': 'за'},
    {'startTime': '1.219999995s', 'endTime': '1.539999988s', 'word': 'Родину'},
]


@pytest.mark.now('2021-07-16T07:00:00.000000+0000')
@pytest.mark.parametrize(
    ['call', 'tp_calls', 'row_data'],
    (
        #
        # Part 0
        #
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 1, 'data': 11},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in',
                out_operation_id='operation_2_out',
            ),
            id='insert call and reschedule, '
            'delay after transcribe = use_sound_duration',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                        {'use_sound_duration': True},
                    ),
                ),
            ],
        ),
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 1, 'data': 3600},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in',
                out_operation_id='operation_2_out',
            ),
            id='insert call and reschedule, delay after transcribe = default',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                        {'use_sound_duration': False},
                    ),
                ),
            ],
        ),
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 1, 'data': 3601},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in',
                out_operation_id='operation_2_out',
            ),
            id='select call and reschedule, delay after transcribe = config',
            marks=[
                pytest.mark.pgsql('callcenter_qa', files=['call_part_0.sql']),
                pytest.mark.config(
                    CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                        {
                            'use_sound_duration': False,
                            'delay_after_transcribe': 3601,
                        },
                    ),
                ),
            ],
        ),
        #
        # Part 1
        #
        pytest.param(
            get_task_data('internalid2', 'not_found'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 1},
            },
            get_row_data(
                call_id='not_found',
                in_text='',
                in_words=[],
                out_text='',
                out_words=[],
            ),
            id='logic error = 404 for IN, OUT',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['call_part_1_logic_error.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'quota-limit'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 1, 'data': 3600},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(call_id='quota-limit'),
            id='transcribe 429 for IN, '
            'delay_after_transcribe_quota_limit = default',
        ),
        pytest.param(
            get_task_data('internalid2', 'quota-limit'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 1, 'data': 429},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(call_id='quota-limit'),
            id='transcribe 429 for IN, '
            'delay_after_transcribe_quota_limit = config',
            marks=pytest.mark.config(
                CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                    {'delay_after_transcribe_quota_limit': 429},
                ),
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'internal-error'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 1, 'data': 600},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(call_id='internal-error'),
            id='transcribe 500 for IN, '
            'delay_after_internal_server_error = default',
        ),
        pytest.param(
            get_task_data('internalid2', 'internal-error'),
            {
                'task-call-insert': {'count': 1},
                'task-reschedule-in-error': {'count': 1, 'data': 500},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(call_id='internal-error'),
            id='transcribe 500 for IN, '
            'delay_after_internal_server_error = config',
            marks=pytest.mark.config(
                CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                    {'delay_after_internal_server_error': 500},
                ),
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'quota-limit'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 1, 'data': 3600},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in', call_id='quota-limit',
            ),
            id='transcribe 429 for OUT',
            marks=pytest.mark.pgsql(
                'callcenter_qa',
                files=['call_part_1_transcribe_out_quota_limit.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'internal-error'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 1, 'data': 600},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in', call_id='internal-error',
            ),
            id='transcribe 500 for OUT',
            marks=pytest.mark.pgsql(
                'callcenter_qa',
                files=['call_part_1_transcribe_out_internal_error.sql'],
            ),
        ),
        #
        # Part 2
        #
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {
                    'count': 1,
                    'data': {
                        'in_operation_id': None,
                        'out_operation_id': 'operation_2_out',
                        'delay': 1,
                    },
                },
                'task-finished': {'count': 0},
            },
            get_row_data(
                out_operation_id='operation_2_out',
                out_text='за Родину',
                out_words=WORDS_OUT,
            ),
            id='404 for operation IN, delay select = 1:0',
            marks=pytest.mark.pgsql(
                'callcenter_qa',
                files=['call_part_2_operation_in_not_found.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {
                    'count': 1,
                    'data': {
                        'in_operation_id': 'operation_1_in',
                        'out_operation_id': None,
                        'delay': 1,
                    },
                },
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in',
                in_text='при написании',
                in_words=WORDS_IN,
            ),
            id='404 for operation OUT, delay select = 0:1',
            marks=pytest.mark.pgsql(
                'callcenter_qa',
                files=['call_part_2_operation_out_not_found.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'quota-limit'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {
                    'count': 1,
                    'data': {
                        'in_operation_id': 'quota-limit',
                        'out_operation_id': 'internal-error',
                        'delay': 600,
                    },
                },
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='quota-limit',
                out_operation_id='internal-error',
            ),
            id='operation 429 for IN, 500 for OUT, delay select = 3600:600, '
            'delay_after_operation_quota_limit = default',
            marks=pytest.mark.pgsql(
                'callcenter_qa',
                files=[
                    'call_part_2_'
                    'operation_in_quota_limit_out_internal_error.sql',
                ],
            ),
        ),
        pytest.param(
            get_task_data('internalid2', 'quota-limit'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {
                    'count': 1,
                    'data': {
                        'in_operation_id': 'internal-error',
                        'out_operation_id': 'quota-limit',
                        'delay': 429,
                    },
                },
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='internal-error',
                out_operation_id='quota-limit',
            ),
            id='operation 500 for IN, 429 for OUT, delay select = 500:429, '
            'delay_after_operation_quota_limit = config',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CALL_RECOGNIZE_SETTINGS=get_config(
                        {
                            'delay_after_internal_server_error': 500,
                            'delay_after_operation_quota_limit': 429,
                        },
                    ),
                ),
                pytest.mark.pgsql(
                    'callcenter_qa',
                    files=[
                        'call_part_2_'
                        'operation_in_internal_error_out_quota_limit.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {
                    'count': 1,
                    'data': {
                        'in_operation_id': 'operation_1_in_not_ready',
                        'out_operation_id': 'operation_2_out_not_ready',
                        'delay': 300,
                    },
                },
                'task-finished': {'count': 0},
            },
            get_row_data(
                in_operation_id='operation_1_in_not_ready',
                out_operation_id='operation_2_out_not_ready',
            ),
            id='operation result for IN, OUT not ready',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['call_part_2_operation_not_ready.sql'],
            ),
        ),
        #
        # Part 3
        #
        pytest.param(
            get_task_data('internalid2'),
            {
                'task-call-insert': {'count': 0},
                'task-reschedule-in-error': {'count': 0},
                'task-reschedule-out-error': {'count': 0},
                'task-reschedule-after-transcribe': {'count': 0},
                'task-reschedule-result-error': {'count': 0},
                'task-finished': {'count': 1},
            },
            get_row_data(
                in_operation_id='operation_1_in',
                out_operation_id='operation_2_out',
                in_text='при написании',
                in_words=WORDS_IN,
                out_text='за Родину',
                out_words=WORDS_OUT,
            ),
            id='operation result for IN, OUT',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['call_part_3.sql'],
            ),
        ),
    ),
)
async def test_stq_qa_call_recognize(
        taxi_callcenter_qa,
        call,
        tp_calls,
        row_data,
        pgsql,
        stq_runner,
        testpoint,
        mockserver,
):
    @testpoint('call_recognize::task-call-insert')
    def handle_call_insert(data):
        assert data == call['internal_id']

    @testpoint('call_recognize::task-reschedule-in-error')
    def handle_reschedule_in_error(data):
        assert data == tp_calls['task-reschedule-in-error']['data']

    @testpoint('call_recognize::task-reschedule-out-error')
    def handle_reschedule_out_error(data):
        assert data == tp_calls['task-reschedule-out-error']['data']

    @testpoint('call_recognize::task-reschedule-after-transcribe')
    def handle_reschedule_transcribe(data):
        assert data == tp_calls['task-reschedule-after-transcribe']['data']

    @testpoint('call_recognize::task-reschedule-result-error')
    def handle_reschedule_result_error(data):
        assert data == tp_calls['task-reschedule-result-error']['data']

    @testpoint('call_recognize::task-finished')
    def handle_finished(data):
        assert data == call

    await stq_runner.callcenter_qa_call_recognize.call(
        task_id='task_id', kwargs=call,
    )

    assert (
        handle_call_insert.times_called
        == tp_calls['task-call-insert']['count']
    )
    assert (
        handle_reschedule_in_error.times_called
        == tp_calls['task-reschedule-in-error']['count']
    )
    assert (
        handle_reschedule_out_error.times_called
        == tp_calls['task-reschedule-out-error']['count']
    )
    assert (
        handle_reschedule_transcribe.times_called
        == tp_calls['task-reschedule-after-transcribe']['count']
    )
    assert (
        handle_reschedule_result_error.times_called
        == tp_calls['task-reschedule-result-error']['count']
    )
    assert handle_finished.times_called == tp_calls['task-finished']['count']

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT'
        ' id, call_id, call_guid, duration,'
        ' in_operation_id, out_operation_id,'
        ' in_text, out_text, in_words, out_words'
        ' FROM callcenter_qa.calls',
    )
    result = cursor.fetchall()
    cursor.close()
    assert result == [row_data]


@pytest.mark.parametrize(
    ['call', 'direction', 'expected_text', 'expected_words'],
    (
        pytest.param(
            get_task_data('internalid1'),
            'in',
            'alternatives-empty-text.json',
            'alternatives-empty-words.json',
            id='alternatives for IN (empty)',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['alternatives-empty.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid1'),
            'out',
            'alternatives-empty-text.json',
            'alternatives-empty-words.json',
            id='alternatives for OUT (empty)',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['alternatives-empty.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid1'),
            'in',
            'alternatives-in-text.json',
            'alternatives-in-words.json',
            id='alternatives for IN',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['alternatives-in.sql'],
            ),
        ),
        pytest.param(
            get_task_data('internalid1'),
            'out',
            'alternatives-out-text.json',
            'alternatives-out-words.json',
            id='alternatives for OUT',
            marks=pytest.mark.pgsql(
                'callcenter_qa', files=['alternatives-out.sql'],
            ),
        ),
    ),
)
async def test_alternatives(
        taxi_callcenter_qa,
        call,
        direction,
        expected_text,
        expected_words,
        pgsql,
        stq_runner,
        load_json,
        mockserver,
):
    @mockserver.json_handler(
        '/operation-api-cloud/operations/alternatives-empty',
    )
    def _alternatives_empty(request):
        return mockserver.make_response(
            status=200, json=load_json('alternatives-empty.json'),
        )

    @mockserver.json_handler('/operation-api-cloud/operations/alternatives-in')
    def _alternatives_in(request):
        return mockserver.make_response(
            status=200, json=load_json('alternatives-in.json'),
        )

    @mockserver.json_handler(
        '/operation-api-cloud/operations/alternatives-out',
    )
    def _alternatives_out(request):
        return mockserver.make_response(
            status=200, json=load_json('alternatives-out.json'),
        )

    await stq_runner.callcenter_qa_call_recognize.call(
        task_id='task_id', kwargs=call,
    )

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT'
        f' {direction}_text, {direction}_words'
        ' FROM callcenter_qa.calls',
    )
    result = cursor.fetchall()
    cursor.close()
    assert load_json(expected_text) == {'text': result[0][0]}
    assert load_json(expected_words) == result[0][1]
