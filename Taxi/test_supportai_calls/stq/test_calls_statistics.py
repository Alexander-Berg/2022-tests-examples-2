import datetime

from aiohttp import web
import pytest

from supportai_lib.tasks import base_task

from supportai_calls import models as db_models
from test_supportai_calls import common

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-calls', 'dst': 'personal'},
            {'src': 'supportai-calls', 'dst': 'stq-agent'},
            {'src': 'supportai-calls', 'dst': 'supportai-context'},
            {'src': 'supportai-calls', 'dst': 'supportai-tasks'},
        ],
    ),
]


@pytest.mark.project(slug='sample_project')
async def test_sending_calls_statistics_in_stq(
        stq3_context,
        stq_runner,
        mockserver,
        create_task,
        calls_statistics_batches,
        mock_calls_statistics,
):
    calls_init = datetime.datetime.now().astimezone()
    dialog_started = calls_init + datetime.timedelta(seconds=10)

    abonent_hangup_error = 'ABONENT_HANGUP'
    user_busy_error = 'DESTINATION_BUSY'
    no_answer_error = 'DESTINATION_NO_ANSWER'
    unknown_error = 'UNKNOWN_ERROR'

    calls_cases = [
        # chat_id, callcenter_number, attempt_number,
        # error_code, error_index, duration, is_ended, is_forwarded
        ('1', None, 1, None, None, 5, True, False),
        ('2', '4242', 1, None, None, 5, True, False),
        ('3', None, 2, None, None, 5, True, True),
        ('4', None, 1, None, None, 5, False, False),
        ('5', None, 1, abonent_hangup_error, 2, 4, False, False),
        ('6', None, 1, abonent_hangup_error, 2, 4, True, True),
        ('7', None, 3, user_busy_error, 0, None, False, False),
        ('8', None, 1, no_answer_error, 0, None, False, False),
        ('9', None, 2, unknown_error, 0, None, False, False),
        ('10', None, 1, unknown_error, 2, 8, False, True),
    ]
    chat_id_to_data = {
        '1': ('ended', 5, 1),
        '2': ('ended', 5, 1),
        '3': ('forwarded', 5, 2),
        '5': ('hangup', 4, 1),
        '6': ('hangup', 4, 1),
        '7': ('user_busy', None, 3),
        '8': ('no_answer', None, 1),
        '9': ('error', None, 2),
        '10': ('error', 8, 1),
    }

    task = create_task(
        type_='outgoing_calls_init',
        status=base_task.TaskStatus.PROCESSING,
        state=base_task.TaskProcessingState.Working,
    )

    calls = [
        common.get_preset_call(
            project_slug='sample_project',
            task_id=task.id,
            chat_id=chat_id,
            phone=chat_id,
            personal_phone_id=chat_id,
            attempt_number=attempt_number,
            initiated=calls_init,
            status=db_models.CallStatus.INITIATED,
        )
        for chat_id, _, attempt_number, *_ in calls_cases
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _():
        contexts = [
            common.create_context(
                created_at=dialog_started,
                chat_id=chat_id,
                num_records=3,
                error_code=error_code,
                error_code_index=error_index,
                is_forwarded=is_forwarded,
                is_ended=is_ended,
                duration_s=duration_,
                callcenter_number=callcenter_number,
            )
            for (
                chat_id,
                callcenter_number,
                _,
                error_code,
                error_index,
                duration_,
                is_ended,
                is_forwarded,
            ) in calls_cases
        ]
        return web.json_response(
            data={'contexts': contexts, 'total': len(contexts)},
        )

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    assert len(calls_statistics_batches) == 1
    statistics_records = calls_statistics_batches[0]
    assert len(statistics_records) == 9

    for record in statistics_records:
        assert record.pop('call_id', None) is not None
        assert record.pop('direction', None) == 'outgoing'
        assert record.pop('call_service', None) == 'ivr_framework'
        assert record.pop('batch_id', None) == task.id

        chat_id = record.pop('chat_id', None)
        item = chat_id_to_data.pop(chat_id, None)
        assert item is not None
        status, duration, attempt_number = item

        assert record.pop('attempt_number', None) == attempt_number
        initiated_at = record.pop('initiated_at', None)
        assert (
            datetime.datetime.fromisoformat(initiated_at) - calls_init
        ).total_seconds() < 1.0

        assert status == record.pop('status', None)
        if duration is not None:
            assert record.pop('talk_duration', None) == duration
            assert record.pop('total_duration', None) == duration + 10
            assert record.pop('started_at', None) is not None
            assert record.pop('ended_at', None) is not None

        if chat_id in ('7', '8', '9'):
            assert record.pop('call_connected', None) is False
        else:
            assert record.pop('call_connected', None) is True
            assert record.pop('user_was_silent', None) is False

        if status == 'error':
            assert record.pop('error_code', None) == unknown_error
        else:
            assert 'error_code' not in record

        if status == 'forwarded':
            assert record.pop('forwarded_to', None) == 'something'

        assert record.pop('user_phone_number', None) == chat_id
        if chat_id == '2':
            assert record.pop('service_phone_number', None) == '4242'

        assert record.pop('tags', None) == []

        assert not record, chat_id

    assert not chat_id_to_data


@pytest.mark.project(slug='sample_project')
async def test_sending_call_initiation_error_to_statistics(
        stq3_context,
        stq_runner,
        mockserver,
        create_task,
        calls_statistics_batches,
        mock_calls_statistics,
):
    now = datetime.datetime.now().astimezone()
    task = create_task(
        type_='outgoing_calls_init',
        status=base_task.TaskStatus.PROCESSING,
        state=base_task.TaskProcessingState.Working,
    )
    calls = [
        common.get_preset_call(
            project_slug='sample_project',
            chat_id=str(idx),
            phone=str(idx),
            personal_phone_id=str(idx),
            task_id=task.id,
        )
        for idx in range(2)
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    @mockserver.handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(request):
        phone_number = request.json['actions'][0]['originate']['phone_number']
        if phone_number == '0':
            return web.Response(status=500)
        return web.json_response()

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), task.error_message

    assert len(calls_statistics_batches) == 1
    records = calls_statistics_batches[0]
    assert len(records) == 1

    error_record = records[0]
    assert error_record.pop('call_id', None) is not None
    assert error_record.pop('error_code', None) is not None
    assert 'service_phone_number' not in error_record
    initiated_at = error_record.pop('initiated_at', None)
    assert initiated_at is not None
    assert (
        datetime.datetime.fromisoformat(initiated_at) - now
    ).total_seconds() < 1.0
    assert error_record == {
        'chat_id': '0',
        'user_phone_number': '0',
        'direction': 'outgoing',
        'call_service': 'ivr_framework',
        'batch_id': task.id,
        'attempt_number': 1,
        'call_connected': False,
        'status': 'error',
    }


@pytest.mark.project(slug='sample_project')
async def test_sending_error_to_stuck_and_no_context_calls(
        stq3_context,
        stq_runner,
        mockserver,
        create_task,
        calls_statistics_batches,
        mock_calls_statistics,
):
    now = datetime.datetime.now().astimezone()
    delay = datetime.timedelta(minutes=5)

    task = create_task(
        type_='outgoing_calls_init',
        status=base_task.TaskStatus.PROCESSING,
        state=base_task.TaskProcessingState.Working,
    )
    calls = [
        common.get_preset_call(
            project_slug='sample_project',
            task_id=task.id,
            chat_id=str(idx),
            phone=str(idx),
            personal_phone_id=str(idx),
            attempt_number=1,
            initiated=now - delay * 2,
            status=db_models.CallStatus.INITIATED,
        )
        for idx in range(2)
    ]
    async with stq3_context.pg.master_pool.acquire() as conn:
        await db_models.Call.insert_bulk(stq3_context, conn, calls)

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _():
        return {
            'contexts': [
                common.create_context(
                    chat_id='0',
                    created_at=now - delay,
                    duration_s=10,
                    num_records=5,
                    is_ended=False,
                ),
            ],
            'total': 1,
        }

    await stq_runner.supportai_calls_processing.call(
        task_id='out_call_task', args=(), kwargs={'task_id': task.id},
    )
    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message

    assert len(calls_statistics_batches) == 1
    records = calls_statistics_batches[0]
    assert len(records) == 2

    def str_to_dt(dt_string):
        return datetime.datetime.fromisoformat(dt_string)

    for record in records:
        assert record.pop('call_id', None) is not None
        assert record.pop('direction', None) == 'outgoing'
        assert record.pop('call_service', None) == 'ivr_framework'
        assert record.pop('batch_id', None) == task.id
        assert record.pop('status', None) == 'error'
        assert record.pop('error_code', None) == 'UNKNOWN_ERROR'
        assert record.pop('attempt_number', None) == 1

        initiated_at = record.pop('initiated_at', None)
        assert initiated_at is not None
        assert str_to_dt(initiated_at) == now - delay * 2

        chat_id = record.pop('chat_id', None)
        assert record.pop('user_phone_number', None) == chat_id

        if chat_id == '0':
            assert record.pop('talk_duration', None) == 10
            assert record.pop('total_duration', None) == 310
            started_at = record.pop('started_at', None)
            ended_at = record.pop('ended_at', None)
            assert started_at is not None and ended_at is not None
            started_at, ended_at = map(str_to_dt, [started_at, ended_at])
            assert started_at == now - delay
            assert ended_at == now - delay + datetime.timedelta(seconds=10)
            assert record.pop('call_connected') is True
            assert record.pop('tags') == []
            assert record.pop('user_was_silent') is False
        else:
            assert record.pop('call_connected') is False

        assert not record
